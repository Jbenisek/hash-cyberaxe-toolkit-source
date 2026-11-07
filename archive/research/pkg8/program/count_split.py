"""The second stage SPLIT at the cheap test on x = c1 xor c1', checked against the program's own part table.

Main session, 2026-10-07. Research only; nothing is filed.

The cheap test ((c1 xor c1') AND cbfffff9) == 0a098189 passes with 105/16384 per lane and keeps 185,351,809 of the
eight-condition rule's mass in C15 (exact, gpt_sol_answer_O.md O4). Both c1 and c1' are already computed inside the
second stage's part "E1, A and B", so the test needs no new stage: the second stage is SPLIT at it.

Grok's job24 priced the split by hand as 81 prefix + 12 test + 57 tail per entered word. This script derives the
same split from the program's OWN part table (halfsearch_cluster.TABLES["batch"]) and from the lines of the part
"E1, A and B", so the figure rests on the program's counter rather than on a hand replay.

  python -B count_split.py
"""
import sys
from fractions import Fraction as Fr
import math

sys.dont_write_bytecode = True
import halfsearch_cluster as H

B = dict((name, (ops, loads)) for name, ops, loads, _, _ in H.TABLES["batch"])
unit = lambda name: sum(B[name])
STAGE_A = [n for n, *_ in H.TABLES["batch"]][:H.STAGE_A_PARTS]
STAGE_2 = [n for n, *_ in H.TABLES["batch"]][H.STAGE_A_PARTS:]

# The lines of "E1, A and B" up to and including c1 and c1', read from the source (packed_batch):
#   a1  = add(add(y1, y6), k("w12-S1-S6"))        2 operations, 1 load
#   d1  = pror(xor(a1, load(row["Y12"])), 16)     1 load, 1 xor and a 5-operation lane rotation
#   c1  = add(d1, k("Y11"))                       1 operation, 1 load
#   c1b = add(d1, k("Y11'"))                      1 operation, 1 load
PREFIX_E1_OPS, PREFIX_E1_LOADS = 2 + 1 + 5 + 1 + 1, 1 + 1 + 1 + 1
TEST = 12          # 7 operations + 5 loads, measured in research\others\tests\RESULTS.md
TAIL_EXTRA = 3     # restoring the values the branch leaves live (Grok's "+3")

prefix = sum(unit(n) for n in STAGE_2 if n not in ("E1, A and B", "E1 test", "restore")) \
         + PREFIX_E1_OPS + PREFIX_E1_LOADS
tail = (unit("E1, A and B") - PREFIX_E1_OPS - PREFIX_E1_LOADS) + unit("E1 test") + unit("restore") + TAIL_EXTRA
stage2 = sum(unit(n) for n in STAGE_2)

P_LANE = Fr(105, 16384)
P_WORD = 1 - (1 - P_LANE) ** 7

print("stage A %d, stage 2 %d (the program's own parts)" % (sum(unit(n) for n in STAGE_A), stage2))
print("split: prefix %d + test %d + tail %d = %d if the tail always ran" % (prefix, TEST, tail, prefix + TEST + tail))
print("P(a word of seven lanes passes the test) = %s = %.10f" % (P_WORD, float(P_WORD)))
print("per entered word: %.4f  (Grok's hand figure 96.5084)" % float(prefix + TEST + tail * P_WORD))

# The same ledger as gpt_sol_answer_U2.md section 9.1, with this word price in place of the wrapped 150
bA, pG, rho, b2, m_eq, g = Fr(2341, 16384), Fr(1, 16), Fr(1, 256), Fr(341, 2500), Fr(2051, 50), Fr(1423, 16384)
tiny = Fr(11473881, 2 ** 43)
WRAPPER = 150 - stage2                      # Sol's wrapper around a second-stage word
for label, price, kept in (("second stage whole (Sol's row)", Fr(150), Fr(6219586146887739, 33554432)),
                           ("split at the cheap test", prefix + TEST + tail * P_WORD + WRAPPER, Fr(185351809))):
    C = 71 * bA + Fr(513, 16) + price * (rho + b2) + g + tiny
    Q = C / m_eq
    for margin in (Fr(15, 4), Fr(12, 5)):
        t = 123.339 - math.log2(float(kept / margin)) + math.log2(float(Q) / 34) + 0.012
        print("%-32s margin %-4s charge/rep %7.3f  Q %7.4f  time_log2 %7.3f"
              % (label, float(margin), float(C), float(Q), t))
