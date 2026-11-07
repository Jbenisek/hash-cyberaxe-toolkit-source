"""exp_tail.py - sample the unreduced lane sums of the add chains in the 'no internal masks' circuit (policy none).
Counts, per big add site, how often the unreduced value reaches T units (T*2^32); lane limit is 16 units (2^36)."""
import sys, os, json, time
import numpy as np
sys.path.insert(0, os.path.dirname(__file__))
from b3scan import *

class Col(list):
    def __init__(self, n): super().__init__(); self.n = n
    def append(self, item):
        tag, v = item
        super().append((tag, v.nv, v.cs, v.bound))
        if v.bound >= 6 * (1 << 32):
            idx = len(self) - 1
            st = STAT.setdefault(idx, {"tag": tag, "nv": v.nv, "cs": v.cs, "bound": v.bound / 2.0**32, "cnt": {t: 0 for t in TS}, "max": 0, "sum": 0.0, "sumsq": 0.0})
            r = v.real
            for t in TS:
                st["cnt"][t] += int(np.count_nonzero(r >= np.uint64(t << 32)))
            st["max"] = max(st["max"], int(r.max()))
            u = r.astype(np.float64) / 2.0**32
            st["sum"] += float(u.sum()); st["sumsq"] += float((u*u).sum())
TS = list(range(6, 17))
STAT = {}
chunks = int(sys.argv[1]); N = 1 << 20; t0 = time.time()
bad = 0
for c in range(chunks):
    inputs = rand_inputs(N, 1000 + c)
    tr = Tracer(36, 7, "none"); 
    # rebuild through build() with custom tracer hook: patch Tracer.adds creation
    import b3scan
    orig = b3scan.Tracer.__init__
    def init(self, *a, **k):
        orig(self, *a, **k); self.adds = Col(N)
    b3scan.Tracer.__init__ = init
    tr = b3scan.build(policy="none", inputs=inputs)
    b3scan.Tracer.__init__ = orig
    if c == 0:
        bad = check_vs_scalar(tr, inputs, N, nchk=300)
    if time.time() - t0 > 270: 
        chunks = c + 1; break
out = {"samples": chunks * N, "mismatch_of_300_chunk0": bad, "sites": {}}
for idx, st in STAT.items():
    st = dict(st); st["tag"] = list(st["tag"]); st["mean_units"] = st["sum"] / (chunks * N); st["var_units"] = st["sumsq"] / (chunks * N) - st["mean_units"]**2
    out["sites"][str(idx)] = st
json.dump(out, open(os.path.join(os.path.dirname(__file__), "tail_out.json"), "w"), indent=1)
print("done", chunks, time.time() - t0)
