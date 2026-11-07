import json, time
import cnt, r5_copy as r
from sweep import cands
out = {}
t0 = time.time()
for LB in (8, 9, 10, 11, 12):
    C = cands(LB)
    best = {}
    for EP in (1, 2, 3, 4, 6, 8, 12, 24):
        m = 24 // EP
        top = 62 // m - 1
        for NRES in sorted(set([0] + list(range(max(0, top - 6), top + 1)))):
            if m * (1 + NRES) > 62: continue
            res = C[:NRES]
            c = cnt.count(LB, EP, res)
            k = (EP, NRES)
            if EP not in best or c < best[EP][0]:
                best[EP] = (c, NRES)
    out[LB] = best
    print(LB, {ep: v for ep, v in best.items()}, round(time.time()-t0), flush=True)
json.dump({str(k): {str(a): b for a, b in v.items()} for k, v in out.items()}, open("sweepbuf.json", "w"))
