"""List message patterns by model-B cost (and their model-A cost) from a results file.
python -B list_low.py <results.bin> <maxB> [init]"""
import sys

import numpy as np

res = np.fromfile(sys.argv[1], dtype=np.uint8).reshape(65536, 10).astype(int)
maxb = int(sys.argv[2])
init = int(sys.argv[3]) if len(sys.argv) > 3 else -1
rows = []
for M in range(1 if init < 0 else 0, 65536):
    if res[M, 1] <= maxb:
        rows.append((res[M, 1], res[M, 0], bin(M).count("1"), M))
rows.sort()
for b, a, w, M in rows:
    words = [j for j in range(16) if (M >> j) & 1]
    print(f"B={b} A={a} |M|={w} M={M} words m{words}")
print(f"{len(rows)} patterns with model-B cost <= {maxb}")
