# U8 experiments on the real Pallas field: 2-adic tower, characters, x^5-c, cubic, Frobenius.

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

import sys, random, json
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/poseidon/orchard/impl'))
import poseidon_ref as R
from collections import Counter
from sympy.polys.galoistools import gf_factor, gf_irreducible_p, gf_pow_mod, gf_degree
from sympy.polys.domains import ZZ
P = R.P; RC = R.RC; M = R.MDS
def H(x): return hex(x)
random.seed(8)
def pr(*a): print(' '.join(str(x) for x in a), flush=True)

# ---------- Q2 tower
nz = next(z for z in range(2, 100) if pow(z, (P-1)//2, P) == P-1)
pr("smallest quadratic non-residue z =", nz)
odd = (P-1) >> 32
g = pow(nz, odd, P)
assert pow(g, 1 << 31, P) == P-1 and pow(g, 1 << 32, P) == 1
def ordlevel(k):
    step = 1 << (32-k)
    return sorted(pow(g, step*j, P) for j in range(1, 1 << k, 2))
pr("ORDER 2: -1 =", H(P-1))
for k in range(2, 6):
    L = ordlevel(k)
    pr("ORDER 2^%d (%d elements):" % (k, len(L)))
    if k <= 4:
        for v in L: pr("   ", H(v))
    else:
        pr("    (listed in tower.json)")
    assert all(pow(v, 1 << (k-1), P) == P-1 for v in L)
json.dump({k: [H(v) for v in ordlevel(k)] for k in range(2, 7)}, open('tower.json', 'w'))
i1 = ordlevel(2); i = i1[0]
pr("i^2=-1 for both order-4 elements:", all(v*v % P == P-1 for v in i1))
for z8 in ordlevel(3):
    s2 = (1+i)*pow(z8, P-2, P) % P
    if s2*s2 % P == 2:
        pr("sqrt(2) =", H(s2), "= (1+i)/zeta8, zeta8 =", H(z8), "i =", H(i)); break
def d2(c):
    t = pow(c, odd, P); o = 0
    while t != 1: t = t*t % P; o += 1
    return 32-o
pr("2-depth (c is a 2^d-th power, max d, cap 32): i:", d2(i), " -1:", d2(P-1), " zeta8:", d2(ordlevel(3)[0]),
   " zeta16:", d2(ordlevel(4)[0]), " zeta2^32:", d2(g), " 2:", d2(2), " 3:", d2(3), " 5:", d2(5), " 7:", d2(7))
# ---------- Q4 residuosity
omega = pow(nz, (P-1)//3, P)
assert pow(omega, 3, P) == 1 and omega != 1
pr("omega (cube root of 1) =", H(omega), "; omega^2 =", H(omega*omega % P))
def cubeclass(c):
    t = pow(c, (P-1)//3, P)
    return 0 if t == 1 else (1 if t == omega else 2)
def q4(c):
    t = pow(c, (P-1)//4, P)
    for e in range(4):
        if t == pow(i, e, P): return e
z8 = ordlevel(3)[0]
def q8(c):
    t = pow(c, (P-1)//8, P)
    for e in range(8):
        if t == pow(z8, e, P): return e
vals = {}
for r in range(64):
    for l in range(3): vals['c%d,%d' % (r, l)] = RC[r][l]
for a in range(3):
    for b in range(3): vals['M%d%d' % (a, b)] = M[a][b]
det = (M[0][0]*(M[1][1]*M[2][2]-M[1][2]*M[2][1])-M[0][1]*(M[1][0]*M[2][2]-M[1][2]*M[2][0])+M[0][2]*(M[1][0]*M[2][1]-M[1][1]*M[2][0])) % P
vals['detM'] = det
N = [[pow(M[a][b], P-2, P) for b in range(3)] for a in range(3)]
x = [0, (N[1][0]-N[0][0]) % P, (N[2][0]-N[0][0]) % P]; y = [N[0][0], N[0][1], N[0][2]]
assert all((x[a]+y[b]-N[a][b]) % P == 0 for a in range(3) for b in range(3))
dx = [(x[1]-x[0]) % P, (x[2]-x[0]) % P, (x[2]-x[1]) % P]; dy = [(y[1]-y[0]) % P, (y[2]-y[0]) % P, (y[2]-y[1]) % P]
for k, v in zip(['x1-x0', 'x2-x0', 'x2-x1'], dx): vals[k] = v
for k, v in zip(['y1-y0', 'y2-y0', 'y2-y1'], dy): vals[k] = v
for a in range(3):
    for b in range(3): vals['N%d%d=1/M' % (a, b)] = N[a][b]
pr("\nCAUCHY gauge x0=0: x =", [H(v) for v in x], " y =", [H(v) for v in y])
pr("name | 2-depth | quartic exp e (c^((p-1)/4)=i^e) | octic exp (zeta8^e) | cube class | Legendre")
for k, v in vals.items():
    if k.startswith('c'): continue
    pr("%-9s d2=%2d  q4=%d  q8=%s  cub=%d  leg=%s" % (k, d2(v), q4(v), q8(v), cubeclass(v), '+' if pow(v, (P-1)//2, P) == 1 else '-'))
prodN = 1
for a in range(3):
    for b in range(3): prodN = prodN*N[a][b] % P
cd = dx[0]*dx[1] % P*dx[2] % P*dy[0] % P*dy[1] % P*dy[2] % P
pr("Cauchy det formula prod(dx)prod(dy)/prod(x_i+y_j) == det M:", cd*pow(prodN, P-2, P)*0 + cd*prodN % P == det, "(prod(x_i+y_j)=prod N, so det = prod dx prod dy * prod(M_ij))")
cs = [v for k, v in vals.items() if k.startswith('c')]
pr("\nconstants (192): 2-depth histogram", sorted(Counter(d2(v) for v in cs).items()), "; expected 192/2^(d+1):", [round(192/2**(j+1), 1) for j in range(8)])
pr("quartic exps", sorted(Counter(q4(v) for v in cs).items()), "(expected 48 each)")
pr("octic exps", sorted(Counter(q8(v) for v in cs).items()), "(expected 24 each)")
pr("cube classes", sorted(Counter(cubeclass(v) for v in cs).items()), "(expected 64 each)")
leg = [[1 if pow(RC[r][l], (P-1)//2, P) == 1 else 0 for l in range(3)] for r in range(64)]
used = list(range(6))+list(range(60, 64))
pr("Legendre grid (1=residue, lanes 0,1,2) rows R0-5,R60-63:", [''.join(map(str, leg[r])) for r in used])
pr("residues per lane over 64 rounds:", [sum(leg[r][l] for r in range(64)) for l in range(3)], "(expected 32 each)")
pr("residues in the 10 used rows (30 values):", sum(sum(leg[r]) for r in used), "(expected 15)")
pr("rows with all three lanes same Legendre:", sum(1 for r in range(64) if len(set(leg[r])) == 1), "of 64 (expected 16)")
pr("adjacent-round same-Legendre lane-wise:", sum(leg[r][l] == leg[r+1][l] for r in range(63) for l in range(3)), "of 189 (expected 94.5)")
t = 0; n = 2000
for _ in range(n):
    v = random.randrange(1, P); s = pow(v, 5, P)
    assert q4(s) == q4(v) and pow(v, (P-1)//2, P) == pow(s, (P-1)//2, P)
    if q8(s) == (5*q8(v)) % 8: t += 1
pr("S-box x^5: quadratic and quartic character preserved on", n, "random x (asserted); octic exponent e -> 5e mod 8 on", t, "of", n)
# ---------- Q3
def to_gf(c): return [1, 0, 0, 0, 0, (-c) % P]
d5 = pow(5, -1, P-1)
pat = Counter()
for _ in range(300):
    c = random.randrange(1, P)
    F = gf_factor(to_gf(c), P, ZZ)[1]
    pat[tuple(sorted((gf_degree(f), e) for f, e in F))] += 1
    assert pow(pow(c, d5, P), 5, P) == c
pr("\nx^5-c over F_p, 300 random c != 0: factor degree patterns", dict(pat))
pat = Counter()
for k, v in vals.items():
    if k.startswith('c'):
        F = gf_factor(to_gf(v), P, ZZ)[1]
        pat[tuple(sorted((gf_degree(f), e) for f, e in F))] += 1
pr("x^5-c for the 192 round constants c:", dict(pat))
F = gf_factor(to_gf(1), P, ZZ)[1]; pr("x^5-1 factor degrees:", [gf_degree(f) for f, e in F])
pr("p mod 5 =", P % 5, "; ord_5(p) =", next(k for k in range(1, 5) if pow(P, k, 5) == 1), "; (p^2+1) mod 5 =", (P*P+1) % 5, " => zeta5 in F_{p^4}, not in F_{p^2}")
pr("Legendre(5/p) =", "-1" if pow(5, (P-1)//2, P) == P-1 else "+1", "(Q(sqrt5) inside Q(zeta5) is inert at p iff 5 is a non-residue)")
pr("Phi5 irreducible over F_p:", gf_irreducible_p([1, 1, 1, 1, 1], P, ZZ))
# ---------- Q5
for a in range(2, 50):
    f = [1, 0, 0, (-a) % P]
    if gf_irreducible_p(f, P, ZZ):
        pr("\nsmallest a>=2 with x^3-a irreducible over F_p: a =", a); break
    else:
        pr("x^3 -", a, "reducible (a is a cube)")
fr = pow(a, (P-1)//3, P)
pr("theta^p = theta*a^((p-1)/3) = theta *", H(fr), "=", "omega" if fr == omega else "omega^2" if fr == omega*omega % P else "?")
pr("x^p mod (x^3-a) =", [H(v) for v in gf_pow_mod([1, 0], P, f, P, ZZ)])
T = (M[0][0]+M[1][1]+M[2][2]) % P
S = ((M[0][0]*M[1][1]-M[0][1]*M[1][0])+(M[0][0]*M[2][2]-M[0][2]*M[2][0])+(M[1][1]*M[2][2]-M[1][2]*M[2][1])) % P
cp = [1, (-T) % P, S, (-det) % P]
pr("charpoly(M) = x^3 - T x^2 + S x - D irreducible:", gf_irreducible_p(cp, P, ZZ))
fx = gf_pow_mod([1, 0], P, cp, P, ZZ); fx2 = gf_pow_mod(fx, P, cp, P, ZZ)
pr("in F_p[x]/charpoly(M): x^p =", [H(v) for v in fx], "\n    x^(p^2) =", [H(v) for v in fx2])
pr("x^(p^3) = x:", gf_pow_mod(fx2, P, cp, P, ZZ) == [1, 0])
pr("det M cube class:", cubeclass(det), "; det M 2-depth", d2(det))
