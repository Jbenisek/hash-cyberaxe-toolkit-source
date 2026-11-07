"""Translation offsets of the exact rank-2 pairs in the six-bit family (stage6b.json): for each pair of classes
(ca, cb), the set D of z-shifts r with T^r(rep_b) compatible with rep_a. A triangle needs r1, r2 in the right sets with
r2 - r1 in D as well; prints D and the number of closed offset triples (must be 0 if the graph has no triangles)."""
import json
from common import *
S = json.load(open(HERE + 'stage1_stats.json')); words = [tuple(w) for w in S['words']]
E = json.load(open(HERE + 'stage6b.json'))['exact_pairs']
six = [i for i, w in enumerate(words) if len(w) == 6]
tr = lambda bits, t: tuple(sorted(64 * (b // 64) + (b % 64 + t) % 64 for b in bits))
reps = {}; cls = {}; ts = {}
for w in six:
    best = min((tr(words[w], t), t) for t in range(64))
    reps.setdefault(best[0], len(reps)); cls[w] = reps[best[0]]; ts[w] = best[1]
D = {}
for k in E:
    a, b = map(int, k.split(','))
    r = (ts[a] - ts[b]) % 64          # b = T^{-ts_b} rep_b ; in a's frame: T^{r} rep_b
    D.setdefault((cls[a], cls[b]), set()).add(r)
    D.setdefault((cls[b], cls[a]), set()).add((-r) % 64)
for key in sorted(D): print('classes', key, 'offsets', sorted(D[key]))
closed = 0
for ca in range(2):
    for cb in range(2):
        for cc in range(2):
            for r1 in D.get((ca, cb), ()):
                for r2 in D.get((ca, cc), ()):
                    if (r2 - r1) % 64 in D.get((cb, cc), ()): closed += 1
print('closed offset triples (word-level necessary condition for a triangle):', closed)
