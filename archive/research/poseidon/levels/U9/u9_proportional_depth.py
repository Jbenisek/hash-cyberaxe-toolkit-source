"""U9 follow-up: how far down are the three lanes proportional? After R4 (AB coords, W=626): lane_i - (M_i0/M_00) lane_0 should have total degree <= 125 (DERIVED). Also after R60 (r=1) not computed (too big)."""
from u9lib import *
ring = Ring(P); W = 626
K = pow((CAP + RC[0][2]) % P, 5, P)
z = ring.x(); zW = ring.xpow(W)
lanes = [z*M[i][0] + zW*M[i][1] + ring.const(M[i][2]*K) for i in range(3)]
for idx in (1, 2, 3, 4): lanes = apply_round(ring, lanes, idx, M, RC)
for i in (1, 2):
    c = M[i][0] * pow(M[0][0], -1, P) % P
    d = lanes[i] - lanes[0]*c
    cs = d.coeffs()
    degs = [ (k % W) + (k // W) for k, x in enumerate(cs) if x != 0]
    log('R4 (AB): lane %d - (M_%d0/M_00)*lane 0: %d monomials, max total degree %d, min total degree %d (DERIVED: <= 125)' % (i, i, len(degs), max(degs), min(degs)))
