"""U9 Q2 (deep rounds): are the LOWEST s total-degree layers of the (A,B) polynomials full at every round, up to the last one?
Low layers of f^5 depend only on low layers of f, so we can run the whole pipeline in the truncated ring F_p[A,B]/(total degree > s) at any depth (here to R63, r=1,2).
Bivariate poly = f(z, z^W) with W=2s+1; after each multiplication drop monomials with i+j > s. Also reports the missing monomials, if any.
usage: python u9_lowlayers.py s"""
import sys
from u9lib import *
s = int(sys.argv[1]); W = 2*s + 1
ring = Ring(P)
mask_idx = None
def trunc(f):
    cs = f.coeffs()
    keep = [0]*((s+1)*W)
    for k, c in enumerate(cs):
        if k >= (s+1)*W: break
        i = k % W; j = k // W
        if i + j <= s: keep[k] = c
    return ring.mk(keep)
def tpow5(f):
    f2 = trunc(f*f); f4 = trunc(f2*f2); return trunc(f4*f)
def support(f):
    cs = f.coeffs(); return {(k % W, k // W) for k, c in enumerate(cs) if c != 0}
tri = {(i, j) for i in range(s+1) for j in range(s+1-i)}
K = pow((CAP + RC[0][2]) % P, 5, P)
for r in (1, 2):
    z = ring.x(); zW = ring.xpow(W)
    lanes = [z*M[i][0] + zW*M[i][1] + ring.const(M[i][2]*K) for i in range(3)]
    for idx in schedule(r)[1:]:
        kd = kind(idx)
        lanes = [lanes[i] + RC[idx][i] for i in range(3)]
        lanes = [tpow5(l) if (kd == 'full' or i == 0) else l for i, l in enumerate(lanes)]
        if idx == 63: lanes = [trunc(ring.lin(M[0], lanes))]
        else: lanes = [trunc(ring.lin(M[i], lanes)) for i in range(3)]
        miss = [len(tri - support(l)) for l in lanes]
        log('s=%d r=%d after R%-2d: lowest %d layers (%d monomials): missing monomials per lane %s' % (s, r, idx, s+1, len(tri), miss))
