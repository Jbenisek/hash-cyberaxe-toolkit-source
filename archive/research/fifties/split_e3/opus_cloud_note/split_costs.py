"""Side-1 (E1) / side-3 (E3) split costs from the exact 453-pair table (C15 weights).

Pr[Z] = sum_(t,s) P1(t,s) * P3(t,s). The current search pays this product per trial.
If E1 and E3 can be driven by separate free words, the cost becomes a sum (one-sided split)
or a balanced meet-in-the-middle on the concentrated (t,s) key.
Run: python3 notes/split_costs.py
"""
from fractions import Fraction as F
import math

rows = []
for line in open("results/pairs_453_weights.txt"):
    t, s, w15, w13, p1 = line.split()
    rows.append((F(w15), F(p1)))
lg = math.log2
P3 = sum(r[0] for r in rows); P1 = sum(r[1] for r in rows)
Z = sum(a * b for a, b in rows)
print("side 3 (E3) total P3 = 2^%.2f, side 1 (E1) total P1 = 2^%.2f, Pr[Z] = 2^%.2f" % (lg(P3), lg(P1), lg(Z)))
rows = [r for r in rows if r[0] > 0 and r[1] > 0]
# one-sided: fresh configs until E3 lands on an accepted pair, then search E1 with E3 fixed
rows.sort(key=lambda r: -r[1])
best = None; a3 = F(0); aw = F(0)
for k, (p3, p1) in enumerate(rows, 1):
    a3 += p3; aw += p3 / p1
    tot = 1 / a3 + aw / a3
    if best is None or tot < best[0]:
        best = (tot, k, 1 / a3, aw / a3)
print("one-sided split: 2^%.2f E3 configs + 2^%.2f E1 trials (%d pairs accepted)" % (lg(best[2]), lg(best[3]), best[1]))
print("balanced MITM on (t,s): 2 x 2^%.2f trials; memory = on-support hits only" % (lg(1 / Z) / 2))
for c in (30, 74, 524):
    print("  at %3d ops per trial: one-sided ~ %.1f, MITM ~ %.1f (score units, 430 ops)" %
          (c, lg(float(best[2]) * c / 430), lg(2 * float(1 / Z) ** 0.5 * c / 430)))
