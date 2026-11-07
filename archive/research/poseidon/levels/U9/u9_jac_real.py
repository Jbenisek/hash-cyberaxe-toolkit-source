"""U9 Q7 on the real field: F_p-rational points where TWO S-box inputs vanish at round k (rank of the state Jacobian drops to 1 there, and stays <=1 afterwards).
(A,B) coordinates (bijective with (nk,rho)). Common zeros of lane polys P_i, P_j (+constants of round k) via Res_B interpolated in A, then gcd in B.
Then verify with forward-mode Jacobian (exact, mod p) through ALL later rounds, and map back to (nk,rho) by the 5th root x^d and compare with the reference hash value."""
import sys
from u9lib import *
ring = Ring(P)
W = 626
d5 = pow(5, -1, P-1)
K = pow((CAP + RC[0][2]) % P, 5, P)
z = ring.x(); zW = ring.xpow(W)
lanes = [z*M[i][0] + zW*M[i][1] + ring.const(M[i][2]*K) for i in range(3)]
def coeff2d(f, D):
    cs = f.coeffs(); cs = [int(c) for c in cs]
    cs += [0]*(W*(D+1) - len(cs))
    return [[cs[i + W*j] for i in range(D+1)] for j in range(D+1)]   # c[j][i]: coefficient of A^i B^j
def lagrange(xs, ys):
    # Newton interpolation mod P -> list of coefficients
    n = len(xs); c = list(ys)
    for j in range(1, n):
        for i in range(n-1, j-1, -1):
            c[i] = (c[i]-c[i-1]) * pow(xs[i]-xs[i-j], -1, P) % P
    poly = ring.mk([c[n-1]])
    for i in range(n-2, -1, -1):
        poly = poly * ring.mk([-xs[i] % P, 1]) + c[i]
    return poly
def common_zeros(Pi, Pj, D):
    ci, cj = coeff2d(Pi, D), coeff2d(Pj, D)
    n = D*D + 1
    xs = list(range(n)); ys = []
    for al in xs:
        def col(c): return ring.mk([sum(c[j][i]*pow(al, i, P) for i in range(D+1)) % P for j in range(D+1)])
        ys.append(int(col(ci).resultant(col(cj))))
    Rz = lagrange(xs, ys)
    pts = []
    if Rz.degree() < 0: return None
    for al, mult in Rz.roots():
        al = int(al)
        def col(c): return ring.mk([sum(c[j][i]*pow(al, i, P) for i in range(D+1)) % P for j in range(D+1)])
        g = col(ci).gcd(col(cj))
        for be, m2 in g.roots(): pts.append((al, int(be)))
    return pts, Rz.degree()
def fwd(A, B, r):
    """forward-mode state and Jacobian wrt (A,B) from just after R0.M; returns list of (round, rank)"""
    s = [(M[i][0]*A + M[i][1]*B + M[i][2]*K) % P for i in range(3)]
    J = [[M[i][0], M[i][1]] for i in range(3)]
    ranks = []
    for idx in schedule(r)[1:]:
        s = [(s[i] + RC[idx][i]) % P for i in range(3)]
        d = []; S = []
        for i in range(3):
            if kind(idx) == 'full' or i == 0: S.append(pow(s[i], 5, P)); d.append(5*pow(s[i], 4, P) % P)
            else: S.append(s[i]); d.append(1)
        Jd = [[d[i]*J[i][j] % P for j in range(2)] for i in range(3)]
        s = [sum(M[i][j]*S[j] for j in range(3)) % P for i in range(3)]
        J = [[sum(M[i][l]*Jd[l][j] for l in range(3)) % P for j in range(2)] for i in range(3)]
        minors = [(J[a][0]*J[b][1]-J[a][1]*J[b][0]) % P for a, b in ((0,1),(0,2),(1,2))]
        rk = 2 if any(minors) else (1 if any(x for row in J for x in row) else 0)
        ranks.append((idx, rk))
    return ranks, s, J
for k_idx, (round_idx, D) in enumerate(((1, 1), (2, 5), (3, 25))):
    # S-box inputs of round `round_idx` = lanes after previous round + constants
    if round_idx > 1: lanes = apply_round(ring, lanes, round_idx-1, M, RC)
    inp = [lanes[i] + RC[round_idx][i] for i in range(3)]
    tot = 0
    for (i, j) in ((0,1),(0,2),(1,2)):
        res = common_zeros(inp[i], inp[j], D)
        pts, rd = res
        tot += len(pts)
        log('round R%d: lanes (%d,%d) S-box inputs both zero: resultant degree %d, F_p-rational common zeros (A,B): %d' % (round_idx, i, j, rd, len(pts)))
        for (A, B) in pts:
            for r in (1, 2):
                ranks, s_end, J_end = fwd(A, B, r)
                rk = dict(ranks)
                nk = (pow(A, d5, P) - RC[0][0]) % P; rho = (pow(B, d5, P) - RC[0][1]) % P
                y = R.hash_reduced(nk, rho, r)
                log('   point A=%s.. B=%s..  r=%d: rank after each round %s ; output (via AB pipeline) matches hash_reduced(nk,rho): %s' % (hex(A)[:10], hex(B)[:10], r, [rk_ for _, rk_ in ranks], s_end[0] == y))
    log('round R%d total F_p-rational double-zero points: %d' % (round_idx, tot))
