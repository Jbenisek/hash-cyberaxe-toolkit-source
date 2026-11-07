"""p3prep.py: input for feat8's P mode: the exact model's P(coll | member, E1.d1, w8) for every W=8 hit and every
N0 trial in a cell of nonzero mass; plus a self-check (sum over w8 must equal mass[k][d1])."""
import os
import numpy as np
from load import feats, col, HERE

F = feats(8)
lines, seen = [], set()
for kind in ('h', 'n0'):
    idx, a = F[kind]
    for row in a:
        mode, s, k, d1, w8, m = (int(col(row[None], c)[0]) for c in ('mode', 'set', 'k', 'd1', 'w8', 'mass'))
        if m <= 0:
            continue
        key = (s, k, d1, w8)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f'P c{s}_{k}_{d1}_{w8} {mode} {s} {k} {d1} {w8}')
# self-check cells: first hit's cell, all 256 w8
idx, a = F['h']
for j in (0, 1):
    s, k, d1 = (int(col(a[j:j + 1], c)[0]) for c in ('set', 'k', 'd1'))
    for w8 in range(256):
        lines.append(f'P chk{j}_{s}_{k}_{d1}_{w8} 0 {s} {k} {d1} {w8}')
open(os.path.join(HERE, 'p3_in.txt'), 'w').write('\n'.join(lines) + '\n')
print(len(lines), 'P lines')
