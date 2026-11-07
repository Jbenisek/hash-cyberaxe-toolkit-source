import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from fractions import Fraction
from math import log2
import bsrho as b
st = b.step256()
def run(tail, lam_milli, kappa=11, R=1024):
    b.TAIL_AGES = tail
    b.INFLIGHT = b.inflight_m(eps=tail)
    b.LAMBDA = Fraction(lam_milli, 1000)
    p = b.plan(256, kappa, None, R)
    if p is None: return None
    lg = b.ledger(p, st, R)
    ls = b.loss(p)
    return log2(lg["total"] / b.UNIT), ls["P_lower"], p["Tp"], p["tmax"], b.INFLIGHT
best = {}
for tail in (1e-6, 1e-5, 1e-4, 1e-3, 3e-3, 1e-2, 3e-2):
    for lam in range(497, 520):
        for kappa in (9, 10, 11, 12, 13):
            r = run(tail, lam, kappa)
            if r and r[1] >= 0.39 + 1e-4:
                k = (tail,)
                if k not in best or r[0] < best[k][0][0]:
                    best[k] = (r, lam, kappa)
                break
for k, v in sorted(best.items()):
    print("tail %g -> lam %d kappa %d: time_log2 %.5f P_lower %.5f Tp %d tmax %d M %d" % (k[0], v[1], v[2], v[0][0], v[0][1], v[0][2], v[0][3], v[0][4]))
