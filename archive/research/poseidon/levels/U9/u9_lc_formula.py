"""U9 Q1/Q5: leading coefficient of the output along the line nk=a+u t, rho=b+v t equals  c * Phi3(u^5,v^5)^(5^k)  (Phi3 = homogeneous top form of lane 0 after R3 in (A,B)-coordinates,
k = number of rounds after R3, c = constant). Check against the EXACT line polynomial (flint) for r=1, and check the edge values Phi3(1,0), Phi3(0,1) != 0 so no F_p-line can lose degree."""
from u9lib import *
ring = Ring(P); z = ring.x()
f = [z*M[i][0] + M[i][1] for i in range(3)]
for idx in (1, 2, 3):
    g = [ring.pow5(x) for x in f]; f = [ring.lin(M[i], g) for i in range(3)]
phi3 = f[0]; phi3all = f
log('Phi3(z): degree %d (formal 125), constant coefficient nonzero: %s, leading coefficient nonzero: %s, F_p roots: %d' % (phi3.degree(), int(phi3.constant_coefficient()) != 0, int(phi3.leading_coefficient()) != 0, len(phi3.roots())))
def Phi3(U, V):  # homogeneous evaluation
    if V % P == 0: return int(phi3.leading_coefficient()) * pow(U, 125, P) % P
    return int(phi3(U*pow(V, -1, P) % P)) * pow(V, 125, P) % P
r = 1
random.seed(77)
a, b, u, v = [random.randrange(1, P) for _ in range(4)]
# exact line polynomial output
lanes = [ring.mk([a, u]), ring.mk([b, v]), ring.const(CAP)]
for idx in schedule(r):
    lanes = apply_round(ring, lanes, idx, M, RC)
out = lanes[0]
lc_exact = int(out.leading_coefficient())
log('exact line polynomial r=1: degree %d, leading coefficient %s...' % (out.degree(), hex(lc_exact)[:20]))
k = len(schedule(r)) - 4
val = pow(Phi3(pow(u, 5, P), pow(v, 5, P)), 5**k, P)
# c from a second line (ratio test): lc_exact / val should be a constant independent of the line
c1 = lc_exact * pow(val, -1, P) % P
log('lc_exact / Phi3(u^5,v^5)^(5^%d) = %s... (constant c if the formula holds)' % (k, hex(c1)[:20]))
a, b, u2, v2 = [random.randrange(1, P) for _ in range(4)]
lanes = [ring.mk([a, u2]), ring.mk([b, v2]), ring.const(CAP)]
for idx in schedule(r): lanes = apply_round(ring, lanes, idx, M, RC)
lc2 = int(lanes[0].leading_coefficient())
c2 = lc2 * pow(pow(Phi3(pow(u2, 5, P), pow(v2, 5, P)), 5**k, P), -1, P) % P
log('second random line: constant = %s... ; equal to the first: %s' % (hex(c2)[:20], c1 == c2))
