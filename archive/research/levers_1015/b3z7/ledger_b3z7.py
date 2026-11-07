"""ledger_b3z7.py - the memory term of the B3Z6 ledger with the solver, context and routine counted from the emitted program.
Integers only.  Run: python3 ledger_b3z7.py N_EMITTED"""
import sys
from fractions import Fraction
from math import log2
N_EMIT = int(sys.argv[1])
TAB_W, MISC_W = 4895744, 499530
LANE = 28 * 2**9 + 2**17 + 2**7 + 10 * 2**9          # 150,656: lane sites, the one copy of an opened cluster, the last batch (bounds, unchanged)
REST = 2**20                                          # allowance for the code not emitted (outer filter, loops of the walk, builders), unchanged bound
OLD_CODE = 3300000
def l5(B):                                            # log2 rounded up at 5 decimals, by integer power
    n = (B ** 100000).bit_length()
    if B ** 100000 == 1 << (n - 1):
        n -= 1
    return Fraction(n, 10**5)
SEL = 2**28 + 2**20
OUT_PHASE = 136256
rows = []
for name, code in (("B3Z6 (bounds)", OLD_CODE), ("B3Z7 emitted", LANE + N_EMIT + REST)):
    B = 32 * (TAB_W + MISC_W + code)
    peak = max(B, SEL, OUT_PHASE)
    rows.append((name, code, B, l5(B), peak, l5(peak)))
T = Fraction(6267324, 10**5)
for name, code, B, lb, peak, lp in rows:
    print("%-14s code %9d  search %12d (2^%s)  peak %12d  memory_log2 %s  score %s" % (name, code, B, float(lb), peak, float(lp), float(T + lp - 20)))
old, new = rows[0], rows[1]
print("gain in memory_log2 (SEL cap 2^28+2^20 as is):", float(old[5] - new[5]))
print("search-phase gain alone (no SEL floor):", float(old[3] - new[3]))
print("SEL floor %d = 2^%s" % (SEL, float(l5(SEL))))
for cap in (2**28, 240 * 10**6, 230 * 10**6, 220 * 10**6, 211561792 - 2**20, 2**27):
    peak = max(new[2], cap + 2**20)
    print("SEL cap %11d -> peak %12d memory_log2 %.5f score %.5f gain vs filed %.5f" % (cap, peak, float(l5(peak)), float(T + l5(peak) - 20), float(old[5] - l5(peak))))
