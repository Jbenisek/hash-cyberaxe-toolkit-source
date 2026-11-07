"""Run the exact linear-consistency filter on every message pattern with truncated model-B cost <= 5.
python -B exact_all_low.py <results.bin> [budget] [node_cap]"""
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from exact_routes import Search  # noqa: E402

res = np.fromfile(sys.argv[1], dtype=np.uint8).reshape(65536, 10).astype(int)
budget = int(sys.argv[2]) if len(sys.argv) > 2 else 5
cap = int(sys.argv[3]) if len(sys.argv) > 3 else 300_000
pats = [M for M in range(1, 65536) if res[M, 1] <= budget]
pats.sort(key=lambda M: (res[M, 1], M))
t0 = time.time()
for M in pats:
    S = Search(M, budget, cap)
    S.run()
    words = [j for j in range(16) if (M >> j) & 1]
    if S.found:
        S.found.sort(key=lambda r: (r[0], r[1]))
        best = S.found[0]
        txt = f"consistent routes {len(S.found)}; best refined round-1 {best[0]} (truncated {best[1]}), round-0 value conditions {best[2]}"
    else:
        txt = "no linearly consistent route"
    print(f"M={M:5d} m{words} truncB={res[M, 1]} nodes={S.nodes} capped={S.capped}: {txt}")
print(f"{len(pats)} patterns, {time.time() - t0:.1f}s")
