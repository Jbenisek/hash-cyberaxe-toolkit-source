"""U11 real field: difference structure (weights, line degrees, dead parts). Light, single process."""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys, time, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as H
from flint import fmpz_mod_ctx, fmpz_mod_poly_ctx
P = H.P; RC = H.RC; M = H.MDS
ctx = fmpz_mod_ctx(P); pctx = fmpz_mod_poly_ctx(ctx); X = pctx.gen()
random.seed(1012)
D5 = pow(5, -1, P - 1)


def inv3(a):
    det = (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1]) - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0]) + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])) % P
    di = pow(det, -1, P)
    c = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            i1, i2 = [x for x in range(3) if x != i]
            j1, j2 = [x for x in range(3) if x != j]
            c[i][j] = ((-1)**(i+j) * (a[i1][j1]*a[i2][j2]-a[i1][j2]*a[i2][j1])) % P
    return [[c[j][i]*di % P for j in range(3)] for i in range(3)]


MI = inv3(M)


def mv(Mx, v):
    return [sum(Mx[i][j]*v[j] for j in range(3)) % P for i in range(3)]


assert mv(M, mv(MI, [1, 2, 3])) == [1, 2, 3]

print("## 1. S-box and C preserve the zero pattern of a difference (PROVED); M obeys wt(d)+wt(Md)>=4")
for sup in [(1, 2), (0, 2), (0, 1)]:
    i, j = sup
    for outlane in range(3):
        dj = (-M[outlane][i]*pow(M[outlane][j], -1, P)) % P
        d = [0, 0, 0]
        d[i] = 1
        d[j] = dj
        o = mv(M, d)
        print(f"  support {sup}, (Md)_{outlane}=0: d_{i}=1, d_{j}={hex(dj)}; zero lanes of Md = {[k for k in range(3) if o[k]==0]}")
for outlane in range(3):
    e = [0, 0, 0]
    e[outlane] = 1
    d = mv(MI, e)
    print(f"  Md = e_{outlane}: nonzero lanes of d = {[k for k in range(3) if d[k] != 0]} (M^-1 has no zero entry)")


def levels(nk, rho, r):
    s = [nk, rho, H.CAPACITY]
    out = [("init", list(s))]
    for idx in H.schedule(r):
        s = H.round_full(s, idx) if (idx < 4 or idx >= 60) else H.round_partial(s, idx)
        out.append((f"R{idx}", list(s)))
    return out


for r in (1, 2):
    wts = {}
    for _ in range(300):
        n1, r1, n2, r2 = [random.randrange(P) for _ in range(4)]
        a = levels(n1, r1, r)
        b = levels(n2, r2, r)
        for (nm, s), (_, t) in zip(a, b):
            w = sum(1 for i in range(3) if (s[i]-t[i]) % P)
            wts.setdefault(nm, {}).setdefault(w, 0)
            wts[nm][w] += 1
    print(f"r={r} 300 random input pairs, weight histogram of the state difference per level: {wts}")
n1, r1 = random.randrange(P), random.randrange(P)
n2 = random.randrange(P)
a = levels(n1, r1, 1)
b = levels(n2, r1, 1)
print("r=1 pair differing only in nk: weights per level:", [(nm, sum(1 for i in range(3) if (s[i]-t[i]) % P)) for (nm, s), (_, t) in zip(a, b)])
b = levels(n1, random.randrange(P), 1)
print("r=1 pair differing only in rho: weights per level:", [(nm, sum(1 for i in range(3) if (s[i]-t[i]) % P)) for (nm, s), (_, t) in zip(a, b)])

print("\n## 2. line degrees: Phi(s + t d) as polynomials in t, from the state entering R4.C (after R3.M)")


def poly_round(st, idx):
    full = idx < 4 or idx >= 60
    st = [st[i] + RC[idx][i] for i in range(3)]
    for i in (range(3) if full else range(1)):
        st[i] = st[i] ** 5
    return [st[0]*M[i][0] + st[1]*M[i][1] + st[2]*M[i][2] for i in range(3)]


def line_degrees(s, d, r):
    st = [X * d[i] + s[i] for i in range(3)]
    res = []
    for idx in list(range(4, 4+r)) + list(range(60, 64)):
        st = poly_round(st, idx)
        res.append((f"R{idx}", [x.degree() for x in st]))
    return res


s = [random.randrange(P) for _ in range(3)]
trail = [0, M[0][2], (-M[0][1]) % P]
assert mv(M, trail)[0] == 0
d_gen0 = [0, random.randrange(P), random.randrange(P)]
d_gen = [random.randrange(P) for _ in range(3)]
for r in (1, 2):
    for nm, d in [("generic d (all lanes)", d_gen), ("d0=0 generic", d_gen0), ("d0=0 on trail (Md)_0=0", trail)]:
        print(f"r={r} {nm}: lane degrees in t by round: {line_degrees(s, d, r)}")

print("\n## 3. a real pair with equal lane 0 after R3.M (found by root finding) followed through the tail")
K = pow((H.CAPACITY + RC[0][2]) % P, 5, P)


def lane_polys_R3(Ap):
    st = [X * M[i][1] + (M[i][0]*Ap + M[i][2]*K) % P for i in range(3)]
    for idx in (1, 2, 3):
        st = poly_round(st, idx)
    return st


def find_pair():
    while True:
        nk = random.randrange(P)
        rho = random.randrange(P)
        lv = levels(nk, rho, 1)
        tgt = [s for nm, s in lv if nm == "R3"][0][0]
        Ap = random.randrange(P)
        f = lane_polys_R3(Ap)[0] - tgt
        g = (X.pow_mod(P, f) - X).gcd(f)
        if g.degree() > 0:
            Bp = int(g.roots()[0][0])
            return (nk, rho), ((pow(Ap, D5, P) - RC[0][0]) % P, (pow(Bp, D5, P) - RC[0][1]) % P)


p1, p2 = find_pair()
for r in (1, 2):
    a = levels(*p1, r)
    b = levels(*p2, r)
    print(f"r={r}: pair #1 = ({hex(p1[0])[:14]}.., {hex(p1[1])[:14]}..)  #2 = ({hex(p2[0])[:14]}.., {hex(p2[1])[:14]}..)")
    for (nm, s), (_, t) in zip(a, b):
        d = [(s[i]-t[i]) % P for i in range(3)]
        print(f"   {nm:>5}: zero lanes of difference {[i for i in range(3) if d[i] == 0]}")
    s3 = [s for nm, s in a if nm == "R3"][0]
    t3 = [s for nm, s in b if nm == "R3"][0]
    dd = [(t3[i]-s3[i]) % P for i in range(3)]
    print("   line s3 + t*(t3-s3), lane degrees:", line_degrees(s3, dd, r))
    print("   final lane0 differs:", a[-1][1][0] != b[-1][1][0])

print("\n## 4. structural reductions, 200 random inputs each")
bad = 0
for _ in range(200):
    nk, rho = random.randrange(P), random.randrange(P)
    ref = H.hash_reduced(nk, rho, 1)
    A = pow((nk+RC[0][0]) % P, 5, P)
    B = pow((rho+RC[0][1]) % P, 5, P)
    s = mv(M, [A, B, K])
    for idx in [1, 2, 3, 4, 60, 61, 62, 63]:
        s = H.round_full(s, idx) if idx != 4 else H.round_partial(s, idx)
    if s[0] != ref:
        bad += 1
print("X2 (start from M*(A,B,K), skip R0) mismatches:", bad)
bad = 0
for _ in range(200):
    nk, rho = random.randrange(P), random.randrange(P)
    s = [nk, rho, H.CAPACITY]
    for idx in [0, 1, 2, 3, 4, 60, 61, 62]:
        s = H.round_full(s, idx) if idx != 4 else H.round_partial(s, idx)
    t = [pow((s[i]+RC[63][i]) % P, 5, P) for i in range(3)]
    y = sum(M[0][j]*t[j] for j in range(3)) % P
    if y != H.hash_reduced(nk, rho, 1):
        bad += 1
print("X7 (only row 0 of M in R63) mismatches:", bad)
bad = 0
Cc = mv(M, [0, RC[4][1], RC[4][2]])
for _ in range(200):
    nk, rho = random.randrange(P), random.randrange(P)
    s = [nk, rho, H.CAPACITY]
    for idx in [0, 1, 2, 3]:
        s = H.round_full(s, idx)
    w = pow((s[0]+RC[4][0]) % P, 5, P)
    s2 = mv(M, [w, s[1], s[2]])
    c60 = [(RC[60][i] + Cc[i]) % P for i in range(3)]
    s3 = [pow((s2[i]+c60[i]) % P, 5, P) for i in range(3)]
    s3 = mv(M, s3)
    t = H.round_full(H.round_partial(s, 4), 60)
    if s3 != t:
        bad += 1
print("X5 (lane 1,2 constants of R4 carried into R60) mismatches:", bad)
print("effective R60 constants for r=1:", [hex((RC[60][i] + Cc[i]) % P) for i in range(3)])
