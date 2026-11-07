"""U9 Q2/Q5: the TOP s+1 homogeneous layers (total degree D, D-1, ..., D-s) of the (A,B)-polynomials at every later round.
Constants only enter at degree 0, i.e. at layer k=D > s, and lanes 1,2 of a partial round are lower degree by a factor 5, so for D large:
   output top layers (A,B coords) = kappa * (top layers of lane 0 after R3)^(5^n), n = 5 (r=1) or 6 (r=2)  (S-box layers R4, [R5,] R60..R63).
Series in y (layer index) whose coefficients are dehomogenised polynomials in x=A/B. Truncate y^(s+1).
Step 0 verifies the shortcut against the exact bivariate lanes at R4 (D=625). Then reports zero coefficients per layer of the final output.
usage: python u9_toplayers.py s r"""
import sys
from u9lib import *
s, r = int(sys.argv[1]), int(sys.argv[2])
ring = Ring(P); W = 626
K = pow((CAP + RC[0][2]) % P, 5, P)
z = ring.x(); zW = ring.xpow(W)
lanes = [z*M[i][0] + zW*M[i][1] + ring.const(M[i][2]*K) for i in range(3)]
for idx in (1, 2, 3): lanes = apply_round(ring, lanes, idx, M, RC)
def layers_of(f, D, s):
    cs = f.coeffs(); out = []
    for k in range(s+1):
        d = D - k
        # monomials (i,j), i+j=d : poly in x=i  of degree d
        out.append(ring.mk([int(cs[i + W*(d-i)]) if (i + W*(d-i)) < len(cs) else 0 for i in range(d+1)]))
    return out
def smul(a, b):
    n = len(a); res = []
    for k in range(n):
        acc = None
        for i in range(k+1):
            t = ring.mul(a[i], b[k-i])
            acc = t if acc is None else acc + t
        res.append(acc)
    return res
def spow5(a):
    a2 = smul(a, a); a4 = smul(a2, a2); return smul(a4, a)
S3 = layers_of(lanes[0], 125, s)
# step 0: R4 check
lanes4 = apply_round(ring, lanes, 4, M, RC)
ex = layers_of(lanes4[0], 625, s)
S4 = spow5(S3)
ok = all(ex[k] == S4[k]*M[0][0] for k in range(s+1))
log('step 0: exact R4 lane 0 top %d layers == M_00 * (R3 lane-0 top layers)^5 : %s' % (s+1, ok))
n = 5 if r == 1 else 6
# kappa recursion: lane_i = kappa_i * w^(5^m); start after R4: kappa_i = M_i0, with w = f0^5
kap = [M[i][0] for i in range(3)]
for m in range(n-1):
    kap = [sum(M[i][j]*pow(kap[j], 5, P) for j in range(3)) % P for i in range(3)]
cur = S3
for _ in range(n): cur = spow5(cur)
for k in range(s+1):
    D = 125*5**n - k
    cs = (cur[k]*kap[0]).coeffs()
    zc = sum(1 for c in cs if c == 0)
    log('r=%d output (A,B) layer k=%d (total degree %d): %d coefficients, zero coefficients %d, polynomial degree %d (full layer would have degree %d)' % (r, k, D, D+1, zc + (D+1-len(cs)), len(cs)-1, D))
