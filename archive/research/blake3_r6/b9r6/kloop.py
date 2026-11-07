import sys
sys.path.insert(0, "pkg/blake3/experiments")
import bsrho as b
from math import log2
for k in (12, 13, 14):
    b.KAPPA_256 = k
    b._B.clear()
    p = b.plan(256, kappa=k)
    lg = b.ledger(p)
    tot = lg["total"]
    print(k, p["Tp"], p["B"], float(tot) / b.UNIT if False else tot, log2(tot / b.UNIT) if True else 0, flush=True)
