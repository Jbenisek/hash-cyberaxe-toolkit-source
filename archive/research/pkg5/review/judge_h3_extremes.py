#!/usr/bin/env python3
"""Hostile-judge lens: the sets of seed words with the most extreme shares in a judge_h3 output file, and how
extreme they are for a maximum over that many sets. Read-only.  python judge_h3_extremes.py <out file>"""
import math
import sys
from pathlib import Path

path = Path(sys.argv[1])
rows = []
for line in path.read_text().split("\n"):
    f = line.split()
    if f and f[0] == "SEED":
        rows.append((int(f[1]), int(f[3]), int(f[5]), int(f[7]), int(f[9])))
p = 1 / 64
z = sorted(((r[3] - r[2] * p) / math.sqrt(r[2] * p * (1 - p)), r[0], r[3] / r[2] * 64, r[4] / r[1]) for r in rows)
tail = lambda x: 0.5 * math.erfc(x / math.sqrt(2))  # noqa: E731
print("sets", len(rows))
print("highest three (sd, seed number, lane share / 2^-6, batch share):", [tuple(round(v, 4) for v in t) for t in z[-3:]])
print("lowest three:", [tuple(round(v, 4) for v in t) for t in z[:3]])
print("chance that the largest of %d normal values is at least %.2f sd: %.3f; that the smallest is at most %.2f: %.3f" % (
    len(rows), z[-1][0], 1 - (1 - tail(z[-1][0])) ** len(rows), z[0][0], 1 - (1 - tail(-z[0][0])) ** len(rows)))
print("sets beyond 3 sd: %d high, %d low (expected %.1f each)" % (sum(t[0] >= 3 for t in z), sum(t[0] <= -3 for t in z), len(rows) * tail(3)))
print("sets beyond 2 sd: %d high, %d low (expected %.1f each)" % (sum(t[0] >= 2 for t in z), sum(t[0] <= -2 for t in z), len(rows) * tail(2)))
