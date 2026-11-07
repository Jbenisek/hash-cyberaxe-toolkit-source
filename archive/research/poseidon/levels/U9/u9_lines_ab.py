"""U9 Q2/Q6: dense-ness of the AB-polynomials along LINES IN THE (A,B) PLANE: A=a0+u t, B=b0+v t (a different family from the (nk,rho)-lines). Starts after R0.M: lanes = M*(A,B,K).
Records degree (expected 5^(rounds after R0)) and zero coefficients inside. usage: python u9_lines_ab.py r seed"""
import sys
from u9lib import *
r, seed = int(sys.argv[1]), int(sys.argv[2]); random.seed(seed)
ring = Ring(P)
K = pow((CAP + RC[0][2]) % P, 5, P)
a0, b0, u, v = [random.randrange(1, P) for _ in range(4)]
# special slices: seed%3==1 -> B fixed (v=0); seed%3==2 -> A fixed (u=0)
if seed % 3 == 1: v = 0
if seed % 3 == 2: u = 0
A = ring.mk([a0, u]); B = ring.mk([b0, v])
lanes = [A*M[i][0] + B*M[i][1] + ring.const(M[i][2]*K) for i in range(3)]
log('r=%d seed=%d AB-line A=a0+u t, B=b0+v t with u!=0:%s v!=0:%s' % (r, seed, u != 0, v != 0))
for n, idx in enumerate(schedule(r)[1:], start=1):
    lanes = apply_round(ring, lanes, idx, M, RC) if idx != 63 else [ring.lin(M[0], [ (lanes[i]+RC[63][i]) if False else ring.pow5(lanes[i]+RC[63][i]) for i in range(3)])]
    out = []
    for l in lanes:
        cs = l.coeffs(); out.append((len(cs)-1, sum(1 for c in cs if c == 0)))
    log('R%-2d deg/zero-coeffs per lane %s  (expected degree 5^%d = %d) (%.0fs)' % (idx, out, n, 5**n, time.time()-T0))

# value check: pull the point (A,B) at a random t back to (nk,rho) and compare the output with the reference hash
t0 = random.randrange(P)
Av = (a0 + u*t0) % P; Bv = (b0 + v*t0) % P
dd = pow(5, -1, P-1)
nk = (pow(Av, dd, P) - RC[0][0]) % P; rho = (pow(Bv, dd, P) - RC[0][1]) % P
log('value check at random t (pull back by 5th roots): %s' % ('MATCH' if int(lanes[0](t0)) == R.hash_reduced(nk, rho, r) else 'MISMATCH'))
