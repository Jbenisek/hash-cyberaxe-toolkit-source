import sys
sys.dont_write_bytecode = True
sys.path.insert(0, 'pkg/blake3/experiments')
import bsrho as b
from math import log2
for K in (12, 13, 14):
    b.KAPPA_256 = K
    b.CFG[256]["kappa"] = K
    b._B.clear()
    p = b.plan(256)
    lg = b.ledger(p)
    ls = b.loss(p)
    print("kappa", K, "Tp", p["Tp"], "B", p["B"], "tmax", p["tmax"], "time_log2 %.5f" % log2(lg["total"] / b.UNIT), "P %.6f" % ls["P_lower"], flush=True)
