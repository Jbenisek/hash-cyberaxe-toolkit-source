#!/usr/bin/env python3
"""value_calc.py  (counter/value; research only) - the time_log2 ledger, filed path against the counter arrangement.
Conventions of the filed package research/pkg10 (64c075ac, 92.53): margin 2.0 on the counted rate (H1 factor =
count / 2), success floor 0.39 (lambda = 0.5 expected successes), cost = trials x charge / 430 units, +0.02 for the
one-time items (92.508 -> 92.53 in the filed text).  Inputs are named with their source."""
from math import log2

LAMBDA = 0.5
OPS_PER_UNIT = 430
ONE_TIME = 0.02            # pkg10: 100.534 + log2(1.65/430) = 92.508, claimed 92.53

def t_log2(factor, charge):
    return log2(LAMBDA) + 128 - log2(factor) + log2(charge / OPS_PER_UNIT) + ONE_TIME

# --- filed (pkg10 proof.md table 'beta / Part of r / Kept for H1'; note: F = 92,675,904; charges 1.65 / 7.7) ---
R_SUB = 185377197.5523            # rate of the sub-class (exact, both counters)
KEPT_H1 = 185355453.4537          # kept for H1 (rule A, outcomes without violating solutions)
F_FILED = 92675904                # H1 factor (margin 2.00 on KEPT_H1)
rows = []
rows.append(('filed 64c075ac: clusters, charge 1.65 per trial-equivalent (H1-H6)', F_FILED, 1.65))
rows.append(('filed arrangement without clusters, charge 7.7 per trial (H1-H3)', F_FILED, 7.7))

# --- counter arrangement: c1 forced into the cube of beta* = 18b0e098 (k = 11 fixed bits of c1) ---
PART_BSTAR_SUB = 67698688         # pkg10 proof.md: part of 18b0e098 in r, with rule A, and kept for H1 (all equal)
PART_BSTAR_ALL = 71698432         # whole class (h8_deep_expected.txt / BLOCK_REPORT)
K = 11
F_CTR = PART_BSTAR_SUB * 2 ** K / 2.0
# machine count (count_ctr.py, same machine as halfsearch.py): stage A 41 units per 7-lane word, stage 2 72 per
# entered word, entry budget 1/32 per word as filed; filed: 47 and 135 -> budgeted 7.318, charged 7.7.
LANES = 7
filed_budgeted = (47 + 135 / 32) / LANES + 0.0011     # +0.0011: middle step, table, outer step amortised (pkg7)
ctr_budgeted = (41 + 72 / 32) / LANES + 0.0010        # outer step ~300 units per 2^21/7 words: 0.001
allow = 7.7 / filed_budgeted                           # the filed allowance and rounding, applied alike
ctr_charge_same_allowance = ctr_budgeted * allow
ctr_charge_rounded = round(ctr_budgeted * 1.04 + 0.0499, 1)
rows.append(('counter, no clusters, charge = filed charge 7.7 (cost not improved)', F_CTR, 7.7))
rows.append((f'counter, no clusters, charge {ctr_charge_rounded} (machine count x 1.04, rounded up to 0.1)', F_CTR, ctr_charge_rounded))
rows.append((f'counter, no clusters, charge {ctr_charge_same_allowance:.3f} (same allowance factor as filed)', F_CTR, ctr_charge_same_allowance))
rows.append(('counter, whole class (beta* part 71,698,432; rule A not recounted there), charge as above', PART_BSTAR_ALL * 2 ** K / 2, ctr_charge_rounded))

print(f'rate factor of a counter trial over a filed trial: {PART_BSTAR_SUB * 2 ** K / R_SUB:.2f} = 2^{log2(PART_BSTAR_SUB * 2 ** K / R_SUB):.3f}'
      f' (sub-class);  whole class {PART_BSTAR_ALL * 2 ** K / 162266763.6588:.2f} = 2^{log2(PART_BSTAR_ALL * 2 ** K / 162266763.6588):.3f}')
print(f'H1 factors: filed {F_FILED} = 2^{log2(F_FILED):.4f}; counter {F_CTR:.0f} = 2^{log2(F_CTR):.4f}')
print(f'trials: filed 2^{log2(LAMBDA) + 128 - log2(F_FILED):.3f} (trial-equivalents), counter 2^{log2(LAMBDA) + 128 - log2(F_CTR):.3f}')
print(f'per-trial budgeted cost: filed {filed_budgeted:.4f}, counter {ctr_budgeted:.4f} (ratio {ctr_budgeted / filed_budgeted:.4f} = 2^{log2(ctr_budgeted / filed_budgeted):.3f})')
base = t_log2(F_FILED, 1.65)
for name, F, ch in rows:
    t = t_log2(F, ch)
    print(f'{t:7.3f}  ({t - base:+.3f} vs filed claim)  {name}')
# board convention (leaders: margin 1.4 instead of 2.0): -log2(2/1.4)
print(f'board convention margin 1.4: subtract {log2(2 / 1.4):.3f} from every row')
