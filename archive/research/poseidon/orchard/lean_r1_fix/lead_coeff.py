"""Leading coefficient f_D of the digest polynomial F_j(W) (r=1, D = 5^7) for the three lines, by propagating leading
coefficients through the rounds, and a check of degree-by-structure; also cross-checks F_j against the reference hash."""
import sys, os, random
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import poseidon_ref as ref
P, MDS, RC, CAP = ref.P, ref.MDS, ref.RC, 1 << 65
E5 = (4 * (P - 1) + 1) // 5
def solve2(a, b, c, d, e, f):
    inv = pow((a * d - b * c) % P, -1, P); return ((e * d - b * f) * inv) % P, ((a * f - e * c) * inv) % P
def line(j):
    K = pow((CAP + RC[0][2]) % P, 5, P); I = [k for k in range(3) if k != j]
    base = [(MDS[k][2] * K + RC[1][k]) % P for k in range(3)]; i1, i2 = I
    UQ, VQ = solve2(MDS[i1][0], MDS[i1][1], MDS[i2][0], MDS[i2][1], -base[i1] % P, -base[i2] % P)
    a, b = MDS[j][1], (-MDS[j][0]) % P
    d = [(MDS[k][0] * a + MDS[k][1] * b) % P for k in range(3)]
    kappa = (MDS[j][0] * UQ + MDS[j][1] * VQ + base[j]) % P
    v0 = [pow(kappa, 5, P) if k == j else 0 for k in range(3)]; v1 = [pow(d[k], 5, P) if k != j else 0 for k in range(3)]
    A = [sum(MDS[k][i] * v0[i] for i in range(3)) % P for k in range(3)]; B = [sum(MDS[k][i] * v1[i] for i in range(3)) % P for k in range(3)]
    return dict(UQ=UQ, VQ=VQ, a=a, b=b, alpha=[(A[k] + RC[2][k]) % P for k in range(3)], beta=B)
def F(L, W, r=1):
    x = [(L['alpha'][k] + L['beta'][k] * W) % P for k in range(3)]
    s = x
    for idx in [2, 3] + list(range(4, 4 + r)) + [60, 61, 62, 63]:
        if idx != 2: s = [(s[k] + RC[idx][k]) % P for k in range(3)]
        full = idx < 4 or idx >= 60
        s = [pow(v, 5, P) if (full or k == 0) else v for k, v in enumerate(s)]
        if idx != 63: s = [sum(MDS[i][k] * s[k] for k in range(3)) % P for i in range(3)]
        else: s = [sum(MDS[0][k] * s[k] for k in range(3)) % P]
    return s[0]
def lead(L):
    l = list(L['beta'])
    for idx in [2, 3, 4, 60, 61, 62, 63]:
        full = idx != 4
        l = [pow(v, 5, P) if (full or k == 0) else 0 for k, v in enumerate(l)]   # partial round: other coordinates have lower degree
        if idx != 63: l = [sum(MDS[i][k] * l[k] for k in range(3)) % P for i in range(3)]
        else: l = [sum(MDS[0][k] * l[k] for k in range(3)) % P]
    return l[0]
random.seed(1)
for j in range(3):
    L = line(j)
    # check F_j(tau^5) = reference hash of the inputs built from tau
    ok = True
    for _ in range(5):
        tau = random.randrange(1, P)
        U, V = (L['UQ'] + tau * L['a']) % P, (L['VQ'] + tau * L['b']) % P
        nk, rho = (pow(U, E5, P) - RC[0][0]) % P, (pow(V, E5, P) - RC[0][1]) % P
        ok &= ref.hash_reduced(nk, rho, 1) == F(L, pow(tau, 5, P))
    print('j=%d  F_j(tau^5) == reference hash on 5 random tau: %s ; leading coefficient f_D = 0x%064x (nonzero: %s)' % (j, ok, lead(L), lead(L) != 0))
