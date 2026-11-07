"""not shipped: leading coefficient f_D of F(W) (line j = 0) by propagating (degree, leading coefficient) through the rounds; checked against the r1/r2 values."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import poseidon_ref as ref
P, M = ref.P, ref.MDS
def lc_F(r, j=0):
    d = [(M[k][0] * M[j][1] + M[k][1] * (-M[j][0])) % P for k in range(3)]
    beta = [sum(M[k][i] * pow(d[i], 5, P) for i in range(3) if i != j) % P for k in range(3)]
    deg, lc = 1, beta[:]                      # round-2 S-box input alpha + beta W
    def full(deg, lc):
        lc5 = [pow(x, 5, P) for x in lc]; return deg * 5, [sum(M[i][k] * lc5[k] for k in range(3)) % P for i in range(3)]
    deg, lc = full(deg, lc)                   # round 2
    deg, lc = full(deg, lc)                   # round 3
    for _ in range(r):                        # partial: lane 0 only; after M every lane has degree 5 deg with lc M[i][0] lc0^5
        t = pow(lc[0], 5, P); deg, lc = deg * 5, [M[i][0] * t % P for i in range(3)]
    for _ in range(4): deg, lc = full(deg, lc)   # rounds 60..63, digest = row 0 of the last MDS
    return deg, lc[0]
known = {1: 0x1c66a426cd2d5ec686ea41cae3a27d49c8724fffa0bc4f305029be8b2cce93c3, 2: 0x13f08536819885e275e9b4b9c9c3aaaf453220a766fbe69710da897c392caa6f}
for r in (1, 2, 3, 4):
    deg, c = lc_F(r)
    print('r=%d deg=%d (5^%d) f_D=0x%064x nonzero=%s %s' % (r, deg, 6 + r, c, c != 0, ('matches packaged value' if known.get(r) == c else 'MISMATCH with packaged') if r in known else ''))
