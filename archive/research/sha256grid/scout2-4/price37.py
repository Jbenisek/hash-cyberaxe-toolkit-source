# price37.py - scout2-4: r37 q3-factor rows on the d3ec5c41 ledger (board best 61.71473).  The ledger function and its
# integers are copied from research/sha256grid/map-r37/ledger_levers.py (score(nscale=1/g): first blocks and data-
# dependent work scale with 1/g, tables and allowances do not).  The factors g are NOT measured at 37 steps: the r37
# Step-3 cells were not available under this scout's file list (see the report).  Rows with the r38 factors are a
# transfer GUESS; the x1.18 / x1.3 / x2 / x4 rows reproduce map-lit/leader_cost_split.txt as a check.
from fractions import Fraction as F
from math import log2
C = 2644
T = F(10005628052435696944197, C)
NFB = 358768880796199274
VMAX = 5884436111293702870939
AC, AS, DEV = 2**60, 2**50, 2**40
fixed = NFB * (1 + F(51, C))
vpart = F(VMAX, C)
rest = T - AC - AS - DEV - fixed - vpart
def score(ac=AC, fb_units=1 + F(51, C), vscale=1, nscale=1):
    n = NFB * nscale
    return log2(ac + AS + DEV + n * fb_units + vpart * nscale * vscale + rest)
b = score()
print("r37 d3ec5c41 ledger rebuilt: %.5f (board 61.71473)" % b)
for g, ref in ((1.18, "61.5530"), (1.3, "61.4625"), (2, "61.0987"), (4, "60.6520")):
    s = score(nscale=F(1) / F(str(g)))
    print("q3 x%-5s: %.4f  delta %+.4f  (leader_cost_split %s)" % (g, s, s - b, ref))
import sys
for g in [float(x) for x in sys.argv[1:]]:
    s = score(nscale=F(1) / F(str(g)))
    print("q3 x%-7.3f (r38 factor transferred, GUESS): %.4f  delta %+.4f" % (g, s, s - b))
