import sys
sys.dont_write_bytecode = True
sys.path.insert(0, sys.argv[1])
from fractions import Fraction
from math import log2
import bsrho as b
st = b.step256()
def t(R=1024, kappa=11, tail=1e-6, lam=497, entry=26):
    b.ENTRY = entry
    b.TAIL_AGES = tail; b.INFLIGHT = b.inflight_m(eps=tail); b.LAMBDA = Fraction(lam, 1000)
    p = b.plan(256, kappa, None, R)
    if p is None: return None
    lg = b.ledger(p, st, R); ls = b.loss(p)
    return round(log2(lg["total"] / b.UNIT), 5), round(ls["P_lower"], 5), p["tmax"], p["Tp"]
print("baseline", t())
print("R=800", t(R=800))
print("R=800 kappa10", t(R=800, kappa=10))
print("kappa10", t(kappa=10))
print("entry 10 B (no stored length; recovery cost not re-priced)", t(entry=10))
print("entry 18 B", t(entry=18))
print("tail 3e-3 lam 503", t(tail=3e-3, lam=503))
