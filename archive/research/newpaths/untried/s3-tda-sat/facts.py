"""Exact chi / linear-layer / degrees-of-freedom facts for the TDA and connector ledger (COMPUTED).
Writes facts.txt.  Pure enumeration, runs in seconds."""
import itertools
import math
import kk

out = []


def P(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    out.append(s)


# ---- all linear subspaces of F2^5 ----
def span(vecs):
    sp = {0}
    for v in vecs:
        sp |= {u ^ v for u in sp}
    return frozenset(sp)


subs = set()
for k in range(6):
    for combo in itertools.combinations(range(1, 32), k):
        subs.add(span(combo))
subs = sorted(subs, key=len)
P("linear subspaces of F2^5:", len(subs))

# ---- 1. chi restriction weights and DDT shape ----
P("\n[1] chi row: restriction weight w(a) by Hamming weight of a")
for hw in range(1, 6):
    ws = sorted({kk.W[a] for a in range(32) if bin(a).count('1') == hw})
    P(f"  |a|={hw}: w(a) in {ws}")
ok_aff = True
for a in range(1, 32):
    sp = kk.out_space(a)
    b0 = sp[0]
    lin = {b ^ b0 for b in sp}
    if lin != span(list(lin)) or len(sp) != 2 ** kk.W[a]:
        ok_aff = False
P("  output-difference sets are affine of dim w(a):", ok_aff)
P("  single-bit a=e_i -> b=e_i needs 2 conditions (x_{i-1}=1, x_{i+1}=0); w(e_i) =", kk.W[1])

# ---- 2. linearization: largest affine subspace on which chi is affine ----
def chi_affine_on(U):
    U = list(U)
    for u, v, w in itertools.product(U, U, U):
        if kk.CHI[u] ^ kk.CHI[v] ^ kk.CHI[w] ^ kk.CHI[u ^ v ^ w]:
            return False
    return True


best = {}
for V in subs:
    d = int(math.log2(len(V)))
    for t in range(32):
        U = frozenset(t ^ v for v in V)
        if chi_affine_on(U):
            best[d] = best.get(d, 0) + 1
maxd = max(best)
P("\n[2] chi full linearization")
P("  affine subspaces (dim:count, cosets counted with multiplicity) on which chi is affine:", dict(sorted(best.items())))
P(f"  max dim = {maxd} -> fully linearizing one chi row costs {5 - maxd} linear conditions")
P(f"  fully linearizing all 320 chi1 rows costs {320 * (5 - maxd)} of 1080 message DF")

# ---- 3. TDA difference phase: affine sets of input differences compatible with an output b ----
P("\n[3] TDA difference phase (input differences compatible with a fixed output difference b)")
rows3 = []
for b in range(1, 32):
    C = {a for a in range(1, 32) if kk.DDT[a][b]}
    dmax, wmin_at_dmax = 0, None
    for V in subs:
        d = int(math.log2(len(V)))
        if d < dmax:
            continue
        for t in range(32):
            U = {t ^ v for v in V}
            if U <= C:
                wm = max(kk.W[a] for a in U)
                if d > dmax or wmin_at_dmax is None or wm < wmin_at_dmax:
                    dmax, wmin_at_dmax = d, wm
    wmin = min(kk.W[a] for a in C)
    rows3.append((b, len(C), dmax, wmin, wmin_at_dmax))
hist = {}
for b, nC, dmax, wmin, wd in rows3:
    hist.setdefault((bin(b).count('1'), nC, dmax, wmin, wd), 0)
    hist[(bin(b).count('1'), nC, dmax, wmin, wd)] += 1
P("  (|b|, #compatible a, max affine dim D(b), min w(a), worst w inside a max-dim affine set): count")
for k in sorted(hist):
    P("   ", k, ":", hist[k])
Dmax = max(r[2] for r in rows3)
P(f"  max D(b) over all b = {Dmax}")
P(f"  the 520 zero-difference bits (512 capacity + 8 pad) need >= ceil(520/{Dmax}) = {math.ceil(520 / Dmax)} active chi1 rows")
P("  for a generic (non-kernel) TDA target; each active row costs >= 2 value conditions")

# ---- 4. digest round (chi6, plane y=0, output lanes x=0..3 must not differ) ----
P("\n[4] digest round: chi6 rows in plane y=0, zero difference required on output bits x=0..3")
feas = [(a, kk.PD[a]) for a in range(1, 32) if kk.PD[a]]
P("  nonzero input differences that can give a digest collision in their row:",
  [(format(a, '05b')[::-1], f"{-math.log2(p / 32):.0f} cond") for a, p in feas])
P("  (bit string printed x=0..4 left to right)")
single_bad = [x for x in range(5) if kk.PD[1 << x] == 0]
P("  single-bit row inputs that make a digest collision impossible: x in", single_bad)
P("  plane-0 chi6 inputs come from theta6-output lanes (x,x):",
  sorted({kk.xyz(kk.RHOPI_INV[kk.idx(x, 0, 0)])[:2] for x in range(5)}))

# ---- 5. message space and CP kernel ----
P("\n[5] message space (135-byte block, byte 135 = 0x86, capacity 512 = 0)")
P("  free bits:", len(kk.FREE), " zero-difference bits:", 1600 - len(kk.FREE))
cols = {}
for i in kk.FREE:
    x, y, z = kk.xyz(i)
    cols.setdefault((x, z), 0)
    cols[(x, z)] += 1
P("  columns:", len(cols), " min free bits per column:", min(cols.values()), " -> parity map rank 320, CP-kernel dim",
  len(kk.FREE) - 320)

# ---- 6. 2-round connector fan-in: one chi2 input bit as a function of chi1 outputs ----
P("\n[6] fan-in of one chi2 input bit from chi1 output bits (theta2 then rho, pi)")
fan = set()
for p in range(1600):
    src = kk.RHOPI_INV[p]
    x, y, z = kk.xyz(src)
    bits = {src} | {kk.idx((x - 1) % 5, yy, z) for yy in range(5)} | {kk.idx((x + 1) % 5, yy, (z - 1) % 64) for yy in range(5)}
    rws = {(kk.xyz(i)[1], kk.xyz(i)[2]) for i in bits}
    fan.add((len(bits), len(rws)))
P("  (chi1 output bits, distinct chi1 rows) over all 1600 chi2 input bits:", sorted(fan))
P("  making one chi1 output bit linear costs 1 condition (fix x_{i+1}, x_{i+2} or their sum);")
P("  the two bits a chi2 input bit needs from one chi1 row are adjacent (x, x-1) and share one condition,")
P("  so linearizing an isolated chi2 condition bit costs <= 10 conditions, and all of chi1 costs",
  320 * (5 - maxd))

with open("facts.txt", "w") as f:
    f.write("\n".join(out) + "\n")
