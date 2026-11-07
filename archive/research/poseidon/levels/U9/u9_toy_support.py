"""U9 Q2/Q4 on toy fields: bivariate supports (Kronecker, nmod_poly) with RANDOM Cauchy MDS and random constants.
usage: python u9_toy_support.py q seed r lastround W
Reports for AB coords R1.. : monomials, triangle size, missing coefficients (zeros inside triangle) vs expectation tri/q ; for nk coords R1..R3 (if last>=3): law check.
A coefficient that is zero 'by accident' occurs at rate ~1/q; structural zeros would show as many more."""
import sys
import time
from u9lib import Ring, stats2, log
from u9toy import *
q, seed, r, last, W = [int(x) for x in sys.argv[1:6]]
Mx, RCx, cap = toy_params(q, seed)
ring = Ring(q)
def apply(lanes, idx):
    kd = kind(idx)
    lanes = [lanes[i] + RCx[idx][i] for i in range(3)]
    lanes = [ring.pow5(l) if (kd == 'full' or i == 0) else l for i, l in enumerate(lanes)]
    return [ring.lin(Mx[i], lanes) for i in range(3)]
def law_set(N):
    return {(i, j) for i in range(5*N+1) for j in range(5*N+1) if -(-i//5) + -(-j//5) <= N}
z = ring.x(); zW = ring.xpow(W)
log('toy q=%d seed=%d r=%d' % (q, seed, r))
# AB coordinates
K = pow((cap + RCx[0][2]) % q, 5, q)
lanes = [z*Mx[i][0] + zW*Mx[i][1] + ring.const(Mx[i][2]*K) for i in range(3)]
for idx in sched(r)[1:]:
    if idx > last and idx < 60: break
    lanes = apply(lanes, idx)
    if idx >= 60 and idx > last: break
    res = []
    for l in lanes:
        nzi, ln = ring.nz_index(l); s = stats2(nzi, W); res.append(s)
    log('AB R%-2d: ' % idx + '; '.join('lane%d n=%d tri=%d missing=%d' % (i, s['n'], s['tri'], s['tri']-s['n']) for i, s in enumerate(res)) + '  expected missing per lane ~ tri/q = %.2f' % (res[0]['tri']/q))
# nk coordinates
if last >= 3:
    lanes = [z, zW, ring.const(cap)]
    for idx in sched(r)[:4]:
        lanes = apply(lanes, idx)
        if idx == 0: continue
        N = 5**idx
        ex = law_set(N)
        out = []
        for l in lanes:
            nzi, ln = ring.nz_index(l); s = stats2(nzi, W)
            got = set(zip(s['i'].tolist(), s['j'].tolist()))
            out.append((len(got), len(ex), len(got - ex), len(ex - got)))
        log('nk R%d: law N=%d predicted %d; per lane (actual, predicted, outside-law, missing-from-law)=%s ; expected missing ~ %.2f' % (idx, N, len(ex), out, len(ex)/q))
log('done %.1fs' % (time.time()-T0)) if False else None
