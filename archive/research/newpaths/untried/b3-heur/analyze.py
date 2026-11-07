#!/usr/bin/env python3
"""analyze.py evals_s1.tsv  (untried/b3-heur; research only; under a second)

Post-processing of the annealing log: per phase counts, the S and total values seen on members of the front-line
class, whether total is a function of e1 bits (2, 21, 26) alone on the sampled members, and the classes (eta) visited
off the front-line class with their exact rates.  Writes analyze_out.txt in this folder.
"""
import sys, os
from collections import Counter, defaultdict

CM, CV = 0x03CF8303, 0x030C0303
BEST_TOTAL, CLASS_S = 76161024, 67633152
here = os.path.dirname(os.path.abspath(__file__))
fn = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, 'evals_s1.tsv')
rows = []
for line in open(fn):
    f = line.rstrip('\n').split('\t')
    if f[0] == 'phase':
        continue
    rows.append(dict(phase=f[0], n=int(f[1]), e1=int(f[2], 16), eta=int(f[3], 16), fixed=int(f[4]), S=int(f[5]),
                     r7=int(f[6]), tot=int(f[7]), nrows=int(f[8]), rc=f[9], sec=float(f[10])))
out = []
p = out.append
p(f'log {os.path.basename(fn)}: {len(rows)} evaluations (distinct points, cache hits are not re-run)')
for ph, c in sorted(Counter(r['phase'] for r in rows).items()):
    secs = sum(r['sec'] for r in rows if r['phase'] == ph)
    p(f'  phase {ph}: {c} evaluations, binary seconds {secs:.1f}')
p(f'  return codes: {dict(Counter(r["rc"] for r in rows))}')
inc = [r for r in rows if r['e1'] & CM == CV]
p(f'\nmembers of the front-line class (eta 830303cf) evaluated: {len(inc)} of 2^19 = 524,288')
p(f'  S values: {dict(Counter(r["S"] for r in inc))}')
p(f'  r7 values: {dict(Counter(r["r7"] for r in inc))}')
p(f'  total values: {dict(sorted(Counter(r["tot"] for r in inc).items()))}')
p(f'  members with S > {CLASS_S:,}: {sum(r["S"] > CLASS_S for r in inc)}; with total > {BEST_TOTAL:,}: '
  f'{sum(r["tot"] > BEST_TOTAL for r in inc)}; with total = {BEST_TOTAL:,}: {sum(r["tot"] == BEST_TOTAL for r in inc)}')
grp = defaultdict(set)
for r in inc:
    key = (r['e1'] >> 2 & 1, r['e1'] >> 21 & 1, r['e1'] >> 26 & 1)
    grp[key].add(r['tot'])
p('  total grouped by e1 bits (2, 21, 26):')
for k in sorted(grp):
    p(f'    {k}: {sorted(grp[k])}  ({sum(1 for r in inc if (r["e1"]>>2&1, r["e1"]>>21&1, r["e1"]>>26&1) == k)} members)')
p(f'  total a function of bits (2, 21, 26) alone on the sample: {all(len(v) == 1 for v in grp.values())}')
off = [r for r in rows if r['e1'] & CM != CV]
etas = defaultdict(list)
for r in off:
    etas[r['eta']].append(r)
nz = {k: v for k, v in etas.items() if any(x['tot'] for x in v)}
p(f'\noff-class points evaluated: {len(off)}, distinct classes (eta) {len(etas)}, classes with any nonzero rate: {len(nz)}')
fx = Counter(v[0]['fixed'] for v in etas.values())
p(f'  class fixed-bit counts visited (class size 2^(32-fixed)): {dict(sorted(fx.items()))}')
for k, v in sorted(nz.items(), key=lambda kv: -max(x['tot'] for x in kv[1]))[:20]:
    b = max(v, key=lambda x: x['tot'])
    p(f'    eta {k:08x} fixed {b["fixed"]}: {len(v)} members, best {b["e1"]:08x} total {b["tot"]:,} S {b["S"]:,} rows {b["nrows"]}')
txt = '\n'.join(out)
print(txt)
open(os.path.join(here, 'analyze_out.txt'), 'w').write(txt + '\n')
