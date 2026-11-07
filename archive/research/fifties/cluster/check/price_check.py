#!/usr/bin/env python3
"""Independent check of CLUSTER.md items (2) and (3): unit counts and the price, exact integers.
Constants: RUN_CONTEXTS, RUN_BATCHES as printed in research/frontline/ca/CA.md line 66 (pkgF);
S_old and the batch rows as printed in CLUSTER.md lines 67-71."""
from fractions import Fraction as F
from decimal import Decimal, getcontext
getcontext().prec = 60

RC = 1553906557396539                     # CA.md l.66
RB = 116386047242443374561                # CA.md l.66
S_OLD = 15136396605699096622327           # CLUSTER.md l.71
OLD_ROW_PRINTED = 7797818548046984199417  # CLUSTER.md l.67
NEW_REP_PRINTED = 345581048832203290905
NEW_PART_PRINTED = 3417649651085488704599
NEW_ROW_PRINTED = 3763230699917691995504
S_NEW_PRINTED = 11101808757569804418414


def log2(x):
    x = F(x)
    n = x.numerator.bit_length() - x.denominator.bit_length()
    return Decimal(n) + (Decimal(x.numerator) / Decimal(x.denominator) / (Decimal(2) ** n)).ln() / Decimal(2).ln()


# ---- item 2: unit counts by hand from the listing ----
batch67 = 4 + 19 + sum(6 if i else 5 for i in range(7)) + 3
rep = batch67 + 7 * 4
last3 = 4 + 19 + sum(6 if i else 5 for i in range(3)) + 3
partner = 4 * batch67 + last3
lanes = [7, 7, 7, 7, 3]
reps_per_ctx = -(-(1 << 14) // 7)
alive_per_ctx = F(13, 32) * (1 << 14)
per_member = F(rep * reps_per_ctx + partner * alive_per_ctx, 1 << 19)
now = F(67 * RB - 30 * RC, (1 << 19) * RC)
print("item2: batch67", batch67, "rep", rep, "last3", last3, "partner", partner, "lanes", sum(lanes),
      "reps/ctx", reps_per_ctx, "alive/ctx", alive_per_ctx)
print("item2: numerator", rep * reps_per_ctx + partner * alive_per_ctx, "per member", float(per_member),
      "now", float(now), "ratio", float(per_member / now))
print("item2: budgeted", rep * reps_per_ctx + partner * 7072, float(F(rep * reps_per_ctx + partner * 7072, 1 << 19)))
print("item2: RB vs ceil(2^19 RC/7):", RB, -(-((1 << 19) * RC) // 7), "RC*74899 =", RC * 74899)

# ---- item 3: price ----
alive_budget = F(17, 16) * F(13, 32) * (1 << 14) * RC
assert alive_budget.denominator == 1
alive_budget = int(alive_budget)
old_row = 67 * RB - 30 * RC
new_rep = 95 * 2341 * RC
new_part = 311 * (alive_budget + 1)
new_row = new_rep + new_part
s_new = S_OLD - old_row + new_row
print("item3: ALIVE_BUDGET == 7072*RC:", alive_budget == 7072 * RC)
print("item3: old row", old_row, old_row == OLD_ROW_PRINTED, "share", float(F(old_row, S_OLD)))
print("item3: new rep", new_rep, new_rep == NEW_REP_PRINTED, "new part", new_part, new_part == NEW_PART_PRINTED)
print("item3: new row", new_row, new_row == NEW_ROW_PRINTED, "S_new", s_new, s_new == S_NEW_PRINTED)
T_old = F(S_OLD + (1 << 70), 430) + (1 << 38)
T_new = F(s_new + (1 << 70), 430) + (1 << 38)
lo, ln = log2(T_old), log2(T_new)
print("item3: log2 T_old %.8f  log2 T_new %.8f  delta %.6f" % (lo, ln, ln - lo))
# variant with rep batch 81 (LEVERS +2/lane)
s_l = S_OLD - old_row + 81 * 2341 * RC + new_part
print("item3: variant rep 81: log2 T %.8f delta %.6f" % (log2(F(s_l + (1 << 70), 430) + (1 << 38)),
                                                         log2(F(s_l + (1 << 70), 430) + (1 << 38)) - lo))
