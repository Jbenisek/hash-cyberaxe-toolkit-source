"""U9 Q4 extension on a toy: (nk,rho)-support at R4 (AB-degree N=625) predicted by the law: 1+10N+25N(N-1)/2 = 4,881,251 monomials per lane. W=3126, q=1000003."""
import sys
from u9lib import Ring, stats2, log
from u9toy import *
q, seed, W = 1000003, int(sys.argv[1]), 3126
Mx, RCx, cap = toy_params(q, seed); ring = Ring(q)
lanes = [ring.x(), ring.xpow(W), ring.const(cap)]
for idx in (0, 1, 2, 3, 4):
    kd = kind(idx)
    lanes = [lanes[i] + RCx[idx][i] for i in range(3)]
    lanes = [ring.pow5(l) if (kd == 'full' or i == 0) else l for i, l in enumerate(lanes)]
    lanes = [ring.lin(Mx[i], lanes) for i in range(3)]
N = 625
ex = {(i, j) for i in range(5*N+1) for j in range(5*N+1) if -(-i//5) + -(-j//5) <= N}
for i, l in enumerate(lanes):
    nzi, ln = ring.nz_index(l); s = stats2(nzi, W)
    got = set(zip(s['i'].tolist(), s['j'].tolist()))
    log('toy q=%d seed=%d (nk,rho) R4 lane %d: monomials %d, law predicts %d, outside law %d, missing from law %d (accidental-zero expectation ~ %.1f), total degree %d degx %d degy %d' % (q, seed, i, len(got), len(ex), len(got-ex), len(ex-got), len(ex)/q, s['deg'], s['degx'], s['degy']))
