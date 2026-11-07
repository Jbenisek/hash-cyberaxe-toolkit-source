#!/usr/bin/env python3
"""skip_curve.py - the same as skip_mass.py on a finer grid of kept shares s (best net bit per score)."""
import json, math, os
from skip_mass import load, kept, HERE
pc, rs = load("scores_pc.txt"), load("scores_rootsteps.txt")
out = {}
for ci, name in ((0, "hot14"), (1, "S6"), (2, "T_rows")):
    sp, cap, sr = [r[ci] for r in pc], [r[3] for r in pc], [r[ci] for r in rs]
    rows = []
    for s in (0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95):
        t, f, s_cap = kept(sp, cap, s)
        m = (sum(1 for x in sr if x > t) + f * sum(1 for x in sr if x == t)) / len(sr)
        be = 0.758 + 0.2415 * s_cap
        rows.append(dict(s=s, s_cap=round(s_cap, 4), m=round(m, 4), se=round(math.sqrt(m * (1 - m) / len(sr)), 4),
                         breakeven=round(be, 4), dbit=round(math.log2(be / m), 4)))
    out[name] = rows
json.dump(out, open(os.path.join(HERE, "skip_curve.json"), "w"), indent=1)
for k, v in out.items():
    print(k, " ".join("s%.2f:m%.4f/be%.4f/%+.4f" % (r["s"], r["m"], r["breakeven"], r["dbit"]) for r in v))
