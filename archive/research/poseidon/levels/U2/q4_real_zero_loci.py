"""Q4 on the real field. Zero loci Z_{k,i} = {(nk,rho): S-box input of lane i in round k is 0}, k=1,2,3.
   In (A,B) coordinates: Z_{1,i} is a LINE (pre-S R1 lane is affine in (A,B)); Z_{2,i} a quintic curve; Z_{3,i} a degree-25 curve.
   Pairwise intersections over F_p are found exactly (line substitution / resultant + root finding) and every point found is re-checked with the
   reference implementation; for every point we list ALL (round,lane) in {1,2,3}x{0,1,2} whose S-box input is zero there."""
import time, sys, itertools
from u2lib import *
random.seed(3)
t0 = time.time()
D5 = pow(5, -1, P - 1)
def inv(x): return pow(x, P - 2, P)
def AB_to_nk_rho(A, B): return (pow(A, D5, P) - a0) % P, (pow(B, D5, P) - b0) % P
def pre_s_inputs(nk, rho):
    """dict (k,i)-> S-box input of lane i in round k (k=0..3) using the reference round functions"""
    s = [nk, rho, CAP]; out = {}
    for k in range(4):
        for i in range(3): out[(k, i)] = (s[i] + RC[k][i]) % P
        s = pr.round_full(s, k)
    return out
# curves as (A,B) polynomial arrays: pre-S input of round k lane i
curves = {}
for k in (1, 2, 3):
    L, D = lanes_after(k - 1)
    for i in range(3):
        curves[(k, i)] = badd_const(L[i][:D+1, :D+1], RC[k][i])
degC = {1: 1, 2: 5, 3: 25}
def uni_in_A(C, B0):
    D = C.shape[0] - 1
    pw = [1]
    for _ in range(D): pw.append(pw[-1] * B0 % P)
    co = [sum(int(C[i, j]) * pw[j] for j in range(D + 1 - i)) % P for i in range(D + 1)]
    return pnorm(co)
def uni_in_B(C, A0):
    D = C.shape[0] - 1
    pw = [1]
    for _ in range(D): pw.append(pw[-1] * A0 % P)
    co = [sum(int(C[i, j]) * pw[i] for i in range(D + 1 - j)) % P for j in range(D + 1)]
    return pnorm(co)
def resultant(f, g):
    """resultant of two univariate polys over F_p (Euclid)"""
    f, g = pnorm(f[:]), pnorm(g[:])
    if not f or not g: return 0
    res = 1
    while True:
        df, dg = len(f) - 1, len(g) - 1
        if dg == 0: return res * pow(g[0], df, P) % P
        r = pmod(f, g)
        if not r: return 0
        dr = len(r) - 1
        if (df * dg) % 2: res = -res % P
        res = res * pow(g[-1], df - dr, P) % P
        f, g = g, r
def interpolate(xs, ys):
    n = len(xs); poly = []
    full = [1]
    for x in xs: full = pmul(full, [(-x) % P, 1])
    for i in range(n):
        num, _ = pdivmod(full, [(-xs[i]) % P, 1])
        den = peval(num, xs[i])
        coef = ys[i] * inv(den) % P
        poly = padd(poly, [c * coef % P for c in num])
    return poly
def intersect(c1, c2):
    """all F_p points (A,B) common to two curves given as (A,B) polys. returns (list of points, degree of resultant poly)"""
    d1, d2 = c1.shape[0] - 1, c2.shape[0] - 1
    n = d1 * d2 + 4
    xs = list(range(1, n + 1)); ys = [resultant(uni_in_A(c1, x), uni_in_A(c2, x)) for x in xs]
    R = interpolate(xs[:n - 2], ys[:n - 2])
    # check on two extra points that the degree bound d1*d2 was right
    assert all(peval(R, xs[j]) == ys[j] for j in (n - 2, n - 1)), "resultant degree bound violated"
    if not R: return None, -1
    pts = []
    for B0 in roots_Fp(R):
        g = pgcd(uni_in_A(c1, B0), uni_in_A(c2, B0))
        if len(g) > 1:
            for A0 in roots_Fp(g): pts.append((A0, B0))
    return pts, len(R) - 1
def check_point(A, B, want, tag):
    nk, rho = AB_to_nk_rho(A, B)
    zi = sorted(kv for kv, val in pre_s_inputs(nk, rho).items() if val == 0 and kv[0] >= 1)
    ok = all(w in zi for w in want)
    print(f"      {tag}: (nk,rho) recovered; S-box inputs zero at (round,lane) = {zi} ; requested pair zero: {ok}", flush=True)
    return zi

print("== R1 lines: concurrency criterion (M^-1 c1)_2 == -K ==")
# M^-1 via adjugate
def inv3(Mx):
    a = Mx; det = (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1]) - a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0]) + a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0])) % P
    di = inv(det)
    cof = [[0]*3 for _ in range(3)]
    for i in range(3):
        for j in range(3):
            m = [[a[r][c] for c in range(3) if c != j] for r in range(3) if r != i]
            cof[i][j] = ((-1)**(i+j)) * (m[0][0]*m[1][1]-m[0][1]*m[1][0]) % P
    return [[cof[j][i] * di % P for j in range(3)] for i in range(3)]
Mi = inv3(MDS)
v2 = sum(Mi[2][j] * RC[1][j] for j in range(3)) % P
print(f"  (M^-1 c1)_2 = {hex(v2)} ; -K = {hex((-K) % P)} ; equal: {v2 == (-K) % P}  => the three R1 zero lines are concurrent iff equal (OBSERVED: not concurrent)")
names = sorted(curves)
print("== pairwise intersections over F_p (exact), all pairs except R3 x R3 ==")
found_pts = []
for (n1, n2) in itertools.combinations(names, 2):
    if n1[0] == n2[0] and n1[0] == 3: continue
    if n1[0] == n2[0] == 1:
        # two lines: solve
        c1, c2 = curves[n1], curves[n2]
        a1, b1, e1 = int(c1[1, 0]), int(c1[0, 1]), int(c1[0, 0]); a2, b2, e2 = int(c2[1, 0]), int(c2[0, 1]), int(c2[0, 0])
        det = (a1 * b2 - a2 * b1) % P
        A = (-(e1 * b2 - e2 * b1)) * inv(det) % P; B = (-(a1 * e2 - a2 * e1)) * inv(det) % P
        pts = [(A, B)]; dres = 'line x line'
    else:
        pts, dres = intersect(curves[n1], curves[n2])
    print(f"  Z_R{n1[0]},lane{n1[1]} x Z_R{n2[0]},lane{n2[1]}: {len(pts)} F_p points (resultant degree {dres}; Bezout max {degC[n1[0]]*degC[n2[0]]}) t={time.time()-t0:.1f}s", flush=True)
    for (A, B) in pts:
        zi = check_point(A, B, [n1, n2], 'point')
        found_pts.append((n1, n2, (A, B), zi))
print("== points where >=3 of the 9 curves vanish together ==")
tri = [(n1, n2, zi) for (n1, n2, pt, zi) in found_pts if len(zi) >= 3]
print(f"  {len(tri)} of {len(found_pts)} pairwise intersection points lie on a third curve" + (": " + str(tri) if tri else ""))
print(f"done t={time.time()-t0:.1f}s")
