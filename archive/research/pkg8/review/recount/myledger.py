"""RECOUNT agent's own charge ledger, from the counts this agent made and the rates measured elsewhere.

    python -B myledger.py
"""
import math
from fractions import Fraction as Fr

# ---- MY COUNTS (all reproduced by mytrace.py, independent of the program's own counter) ----
A_REP = 47          # representative word, first stage
A_NB = 47           # neighbour word, first stage (every one of the nine forms, pure or mixed X2)
S2 = 135            # second stage, representative or neighbour word
GATE_CORE = 9       # gate predicate + branch, core
SEL = 29            # seven-lane dispatch selector
MID = 134           # middle step per X2 value
CACHE = 258         # mixed-middle blend, per canonical-X2 group
TBL = 74            # table build per list word
OUTER = 260         # outer step (taken from the program's part table, NOT re-transcribed here)
ROWS = 133413       # rows per outer tuple in the 8x layout (DERIVED in U.md 4.1, = 131072 + 2341)

# ---- rates, MEASURED elsewhere (MEASURE.md / VERDICT8.md / BIAS.md), used as premises ----
Sp = 40.02                   # yield (H4)
TE = 1.0 + Sp                # 41.02 trial-equivalents per representative
wpr = 2341.0 / 16384.0       # representative stage-A words per representative
P_F7 = 0.02622               # share of representative words with a K8 lane
P_G7 = 0.2416                # share of representative words with a gate lane
pG = 1.0 / 16.0              # share of representatives whose gate opens (structural)
bN1 = 9.0 / 16.0             # neighbour stage-A words per representative (9 per opened cluster)
bN2 = 0.1364                 # neighbour stage-2 words per representative
REPS_GRP = 16384.0

# ---- items I cannot count (named, with the values the ledgers use) ----
ADDR = 5.0                   # cluster address base + 9r, per opened cluster (ESTIMATE)
SPILL = 4.0                  # packet index + cursor spill, per gate word (ESTIMATE)
SETUP = 16.0                 # group advance / list reset, per group (ESTIMATE)
TAIL4 = 4.0                  # last-word spare-lane suppression, per group (ESTIMATE)

KEPT_CLAIM = 185355453.45    # the figure the claim is set against
KEPT_RULE = 185358111.47     # rule A keeps
KEPT_TEST = 185351809.0      # rule A and the cheap test keep
UPLIFT = 1.04                # pkg7's "margin for uncounted operations"


def ledger(gate, s_rep, s_nb, budget=False):
    gate_words = wpr * (P_G7 * (1.2 if budget else 1.0))
    open_share = pG * (1.2 if budget else 1.0)
    it = {
        "rep stage A": A_REP * wpr,
        "gate test": gate * wpr + TAIL4 / REPS_GRP,
        "rep stage 2": s_rep * (wpr / 32.0 if budget else wpr * P_F7),
        "dispatch selector": SEL * gate_words,
        "cluster addressing": ADDR * open_share,
        "metadata spill": SPILL * gate_words,
        "neighbour stage A": A_NB * (9.0 * open_share),
        "neighbour stage 2": s_nb * (bN2 * (1.2 if budget else 1.0)),
        "middle, 8 per group": 8.0 * MID / REPS_GRP,
        "mixed-middle cache": CACHE / REPS_GRP,
        "group setup": SETUP / REPS_GRP,
        "table + outer, amortised": (TBL * ROWS + OUTER) / 2.0 ** 43,
    }
    return it


def tlog2(kept, charge, margin):
    return 123.339 - math.log2(kept / margin) + math.log2(charge / 34.0) + 0.012


P_LANE = Fr(105, 16384)
P_WORD = float(1 - (1 - P_LANE) ** 7)
SPLIT_WORD = 81 + 12 + 57 * P_WORD          # my prefix 81, test 12 (not recounted), tail 54 + 3

print("P(word of seven lanes passes the cheap test) = %.10f" % P_WORD)
print("my split of the second stage: prefix 81 + test 12 + tail 57 -> %.4f per entered word" % SPLIT_WORD)
print("(Grok's hand figure adds one unit: 96.5084; count_split.py derives 95.5084 and labels it 96.5084)")
print()
hdr = "%-46s %9s %9s %9s %9s" % ("ledger", "per rep", "K", "t(3.75)", "t(2.4)")
print(hdr)
print("-" * len(hdr))
rows = []
for label, gate, s2r, s2n, budget, kept in [
        ("whole stage 2, expected rates, gate 9", 9, S2, S2, False, KEPT_RULE),
        ("whole stage 2, expected rates, gate 10 (Grok)", 10, S2, S2, False, KEPT_RULE),
        ("whole stage 2, expected rates, gate 12 (U 4.3)", 12, S2, S2, False, KEPT_RULE),
        ("whole stage 2, 1.2x budget (Sec 8), gate 12", 12, S2, S2, True, KEPT_RULE),
        ("split stage 2, expected rates, gate 12", 12, SPLIT_WORD, SPLIT_WORD, False, KEPT_TEST),
        ("split stage 2, 1.2x budget, gate 12", 12, SPLIT_WORD, SPLIT_WORD, True, KEPT_TEST)]:
    it = ledger(gate, s2r, s2n, budget)
    per_rep = sum(it.values())
    K = per_rep / TE
    print("%-46s %9.4f %9.4f %9.3f %9.3f"
          % (label, per_rep, K, tlog2(kept, K, 3.75), tlog2(kept, K, 2.4)))
    rows.append((label, it, per_rep, K))

print()
print("with the package's 1.04 uplift and its own rounding:")
for label, it, per_rep, K in rows:
    c = K * UPLIFT
    print("  %-46s charge %6.4f -> %6.3f  t(3.75) %7.3f  t(2.4) %7.3f"
          % (label, K, c, tlog2(KEPT_CLAIM, c, 3.75), tlog2(KEPT_CLAIM, c, 2.4)))

print()
print("the package's own figures, recomputed with the same formula:")
for c in (1.6389, 1.71, 7.7):
    print("  charge %6.4f  t(3.75) %7.4f  t(2.4) %7.4f" % (c, tlog2(KEPT_CLAIM, c, 3.75), tlog2(KEPT_CLAIM, c, 2.4)))
print("  the package's per-representative total 67.225 -> K %.4f" % (67.225 / TE))
print()
print("itemised, the row the package's charge should be compared with (1.2x budget, gate 12):")
for k, v in rows[3][1].items():
    print("    %-28s %9.4f   (/TE %.5f)" % (k, v, v / TE))
