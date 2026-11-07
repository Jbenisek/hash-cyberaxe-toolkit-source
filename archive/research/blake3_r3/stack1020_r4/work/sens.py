import sys, importlib.util
from math import log2
sys.dont_write_bytecode = True
spec = importlib.util.spec_from_file_location("b", "../pkg/blake3/experiments/bsrho.py"); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
base = log2(b.ledger()["total"] / b.UNIT)
print("base %.5f" % base, {k: "%.3e" % v for k, v in b.loss(b.plan(256)).items() if isinstance(v, float)})
for eps in (0.01, 0.05, 0.10, 0.25):
    b._lossq.__defaults__ = (1 - eps, 20000, 2000); b._B.clear()
    p = b.plan(256); t = log2(b.ledger(p)["total"] / b.UNIT)
    print("eps %.2f Tp %d time %.5f extra %.4f" % (eps, p["Tp"], t, t - base))
