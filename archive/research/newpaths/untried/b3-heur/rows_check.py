#!/usr/bin/env python3
"""rows_check.py  (untried/b3-heur; research only; under a second)

Per ROW (not only the sum): over the existing stack cube outputs (read-only), does each tau's normalised mass
L*N/2^(64+free) take one value only?  Prints, per tau, the distinct values and how many cubes show each.
Writes rows_check_out.txt in this folder.
"""
import os, glob
from collections import defaultdict
from rates import parse, S_TAUS

here = os.path.dirname(os.path.abspath(__file__))
stack = os.path.join(here, '..', '..', 'counter_next', 'stack')
per = defaultdict(lambda: defaultdict(int))
n = 0
for fn in sorted(glob.glob(os.path.join(stack, 'cube_*.out'))):
    parts = os.path.basename(fn)[5:-4].split('_')
    if len(parts) != 2:
        continue
    try:
        mask = int(parts[0], 16)
    except ValueError:
        continue
    txt = open(fn).read()
    if 'OUTR' not in txt:
        continue
    n += 1
    _, _, _, _, rows = parse(txt, mask)
    for tau, m in rows.items():
        per[tau][m] += 1
out = [f'cubes parsed: {n}']
for tau in sorted(per, key=lambda t: (t not in S_TAUS, t)):
    vals = per[tau]
    if not any(vals):
        continue
    tag = 'S ' if tau in S_TAUS else '  '
    out.append(f'{tag}tau {tau:08x}: {len(vals)} distinct value(s): ' +
               ', '.join(f'{float(v):,.0f} x{c}' for v, c in sorted(vals.items())))
txt = '\n'.join(out)
print(txt)
open(os.path.join(here, 'rows_check_out.txt'), 'w').write(txt + '\n')
