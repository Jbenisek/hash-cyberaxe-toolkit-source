"""2-round connector ledger at rate 1088 / capacity 512 for the DDS middle placement (COMPUTED + DERIVED).

The connector must output b2 = S (6-bit double-kernel pattern) after chi2.  chi2 input a2 is any chi-compatible
input of S's rows; chi1 output must then be exactly b1 = L^-1(a2) = theta^-1(rhopi^-1(a2)).
Computes, per class: whether some a2 makes rhopi^-1(a2) a CP-kernel vector (b1 sparse), else |b1|, active chi1 rows,
and sum over active rows of the minimum restriction weight of a compatible input (a floor on chi1 value conditions).
Writes conn.txt."""
import itertools
import kk
import dds2 as D

PI, PIINV = kk.RHOPI, kk.RHOPI_INV
out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s, flush=True)
    out.append(s)


# theta on the 320-bit parity plane: p(theta(u)) = (I + E) p(u), E(p)[x,z] = p[x-1,z] ^ p[x+1,z-1]
def cidx(x, z):
    return x + 5 * z


cols = []
for z in range(64):
    for x in range(5):
        v = 1 << cidx(x, z)
        v |= 1 << cidx((x - 1) % 5, z)
        v |= 1 << cidx((x + 1) % 5, (z - 1) % 64)
        cols.append(v)      # row (x,z) of I+E as a bitmask over input parities
# invert I+E by Gauss-Jordan on rows
n = 320
A = [cols[i] | (1 << (n + i)) for i in range(n)]
for c in range(n):
    r = next(r for r in range(c, n) if (A[r] >> c) & 1)
    A[c], A[r] = A[r], A[c]
    for r2 in range(n):
        if r2 != c and (A[r2] >> c) & 1:
            A[r2] ^= A[c]
INV = [A[i] >> n for i in range(n)]   # row i of (I+E)^-1


def theta_inv(v):
    pv = 0
    for i in v:
        x, y, z = kk.xyz(i)
        pv ^= 1 << cidx(x, z)
    pu = 0
    for i in range(n):
        if bin(INV[i] & pv).count("1") & 1:
            pu |= 1 << i
    # E(pu) column effect
    u = set(v)
    for z in range(64):
        for x in range(5):
            e = ((pu >> cidx((x - 1) % 5, z)) & 1) ^ ((pu >> cidx((x + 1) % 5, (z - 1) % 64)) & 1)
            if e:
                for y in range(5):
                    u ^= {kk.idx(x, y, z)}
    return u


# self-check
import random
rnd = random.Random(3)
for _ in range(5):
    s = {rnd.randrange(1600) for _ in range(rnd.randrange(1, 30))}
    assert kk.theta_set(theta_inv(s)) == s
P("theta inverse check ok")
minw = {}
for b in range(1, 32):
    minw[b] = min(kk.W[a] for a in range(1, 32) if kk.DDT[a][b])

for ci, c in enumerate(D.classes):
    S = set(c)
    rwS = kk.rows(S)
    keys = list(rwS)
    opts = [[a for a in range(1, 32) if kk.DDT[a][rwS[k]]] for k in keys]
    # backward kernel test over all compatible a2 (exact, meet in the middle on parities)
    def par(a_rowset):
        m = 0
        for i in a_rowset:
            x, y, z = kk.xyz(PIINV[i])
            m ^= 1 << cidx(x, z)
        return m
    h = len(keys) // 2
    L = {}
    for combo in itertools.product(*opts[:h]):
        L.setdefault(par(kk.unrows(dict(zip(keys[:h], combo)))), combo)
    kern = False
    for combo in itertools.product(*opts[h:]):
        if par(kk.unrows(dict(zip(keys[h:], combo)))) in L:
            kern = True
            break
    a2 = S  # identity choice (w = 12)
    b1 = theta_inv({PIINV[i] for i in a2})
    rw1 = kk.rows(b1)
    floor = sum(minw[v] for v in rw1.values())
    P(f"class {ci}: some compatible a2 has a CP-kernel pre-image: {kern};  identity a2: |b1| = {len(b1)} bits, "
      f"{len(rw1)} active chi1 rows, chi1 value-condition floor sum(min w) = {floor}")
P("ledger (DERIVED): DF after chi1 <= 1080 - max(520 counting bound, floor); chi2 adds w(a2)=12 conditions and")
P("the linearization of the 12 chi2 condition bits adds <= 10 each (<= 120).")
with open("conn.txt", "w") as f:
    f.write("\n".join(out) + "\n")
