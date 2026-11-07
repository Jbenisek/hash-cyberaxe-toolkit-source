#!/usr/bin/env python3
"""The figures of the seventh package (a DRAFT) that the step PROGRAM fixed: the sub-class, the rule, the factor, the
counts of the experiment program and the cost arithmetic. ONE place.

    python -B tools/pkg7_data.py             prints the figures and the cost table of the rule in use
    python -B tools/build_pkg7.py --program  compares experiments/halfsearch.py with this file (nothing is written)
    python -B work/tools/cost.py             counts the program again on its machine and writes COST.txt

This file does NOT replace tools/pkg6_data.py, the data module of the TEXT (tokens, paragraphs, readers of the
result files of the filed package). That module is still the one of research/pkg6: its templates describe the old
arrangement (context vc, vd, S11, S4, X13, X14, w0; rule with five conditions; 524,288 members). It is set to
TEXT_PORTED = False and SUBMISSION_STATE = "draft", so tools/build_pkg6.py renders nothing. The step that writes the
text ports it and should take every figure below from here.

PART A  what a person edits: sub-class, rule, factor, margins.
PART B  the counts of the program, typed here once; tools/build_pkg7.py --program and work/tools/cost.py compare
        them with the program's own machine and stop when they differ.
PART C  the kept counts, read from research/pkg7/count (the step COUNT), and the cost arithmetic.
Research helper, not submitted.
"""
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
CAND = PKG / "blake3-r2"
PROGRAM = CAND / "experiments" / "halfsearch.py"
COUNT = PKG / "count"

# =====================================================================================================
# PART A: what a person edits
# =====================================================================================================
SUBMISSION_STATE = "draft"        # stays "draft" until the owner says go for this package
PIN = {"X3": 0x29D4FA98, "X7": 0xBEE3AF28, "X11": 0x44036000, "X15": 0x40C58500, "W4": 0x97475638, "W13": 0x0007C006}
LEN_A, LEN_B = 55, 63
ETA = 0x830303CF                  # the class of Lemma Q: (e1 AND 03cf8303) == 030c0303, 524,288 members
# The sub-class (step COUNT, cube k = 15): the members of the class whose e1 = Y3 + Y4 has the bits of CUBE[0] equal
# to CUBE[1]. Together: (e1 AND 07ef8303) == 030c0303, 131,072 members.
CUBE = (0x04200000, 0x00000000)
CLASS_MASK, CLASS_VALUE, CLASS_SIZE = 0x07EF8303, 0x030C0303, 131072
# Rule A: conditions (mask, value) on h1; three rules, each containing the one before it. The names are those of
# research/pkg7/count/COUNT.md section 2.
RULES = {4: ((0x00000001, 0), (0x00000002, 1), (0x00010000, 0), (0x00020000, 0))}
RULES[6] = RULES[4] + ((0x00000404, 1), (0x00000808, 1))
RULES[8] = RULES[6] + ((0x01001008, 0), (0x02002040, 0))
RULE_NAMES = {4: "p4", 6: "old6", 8: "S8"}
RULE_CONDITIONS = 8
# The factor that H1 assumes for the rate (the line FACTOR of the program; a run has 2^127 / FACTOR trials).
# 92,675,904 = 2^26.4657: half of the cheap-test count 185,351,809, rounded down (margin 2.000068 on rule A).
FACTOR = 92675904
MARGINS = (2.0, 2.4)              # the margins of the cost table: kept count / assumed factor
MACHINE_REGISTERS, KEPT_WORDS = 16, 9      # the lines REGISTERS and KEPT of the program

# =====================================================================================================
# PART B: counts of the program (operations, loads[, stores]); the machine is the judge, not this table
# =====================================================================================================
STAGE_A_BY_RULE = {4: (29, 8), 6: (32, 9), 8: (37, 10)}
STAGE_2_BY_RULE = {4: (101, 27), 6: (105, 30), 8: (105, 30)}       # its entry count (3 + 1) and "restore" included
OUTER_STEP, TABLE_BUILD, MIDDLE_STEP = (148, 91, 21), (43, 26, 5), (85, 40, 9)
REGISTERS_IN_USE = {"batch": 16, "outer step": 11, "table build": 7, "middle step": 13}
LIST_WORDS = 18725                # ceil(131072 / 7); the last word has four members and three spare lanes
# The same program with the line KEPT = 0 (every memory word fetched where it is read): the convention of the text
# of the filed package. Stage A, stage 2, middle step.
EVERY_READ_A_LOAD = {4: ((29, 18), (100, 43)), 6: ((32, 19), (100, 43)), 8: ((37, 20), (100, 43))}
EVERY_READ_MIDDLE_STEP = (85, 52, 9)

# =====================================================================================================
# PART C: kept counts and cost
# =====================================================================================================
BASE, TAIL, UNIT, MARGIN_ON_COST, LANES = 123.339, 0.012, 34, 1.04, 7
X2_VALUES_LOG2 = 32               # values of X2 per outer step: the table of an outer step serves all of them

# =====================================================================================================
# PART C2: the clusters of this package (the filed entry of 2026-10-07 10:35 has none of this)
# =====================================================================================================
# A REPRESENTATIVE is a trial whose bits 14, 30 and 31 of e1 and of X2 are zero; its NEIGHBOURS are the 63 trials
# reached by flipping any non-empty subset of those six bits. Representative and neighbours form a CLUSTER, and the
# clusters partition the trials of the sub-class (Lemma C). Stage A runs on a word of seven representatives; a lane
# that passes rule A goes to stage 2 as before; a lane that passes the GATE, the four conditions
# h0 = 0, h1 = 1, h16 = 0, h17 = 0 that rule A implies, opens its cluster: the neighbour words go through stage A,
# and a neighbour word with a lane that passes rule A goes to stage 2.
# CLUSTERS ON. The filed entry of 2026-10-07 has CLUSTERS = False: every trial goes through stage A. With
# CLUSTERS = True the charge of the claim is cluster_cost() per trial-equivalent in place of the per-trial
# charge of PART C, and the text carries the sections that describe and prove the procedure.
CLUSTERS = True
CLUSTER_SPLIT = True              # the second stage split at the cheap test of Lemma T
CLUSTER_BUDGET = True             # charge the budget of the neighbour path, as the filed entry charges its own
GATE_NAME = "H4"
CLUSTER_FLIPS = ("e1 bit 14", "e1 bit 30", "e1 bit 31", "X2 bit 14", "X2 bit 30", "X2 bit 31")
NEIGHBOURS = 2 ** len(CLUSTER_FLIPS) - 1                           # 63
# Measured on real trials, three times and independently (Section 10): the number of neighbours found to pass
# rule A, per trial whose collision mass rule A keeps, and the two rates of the neighbour path per representative.
YIELD = 40.02                     # the three measurements: 40.018 (se 0.012), 40.032 (se 0.075), 40.027
GATE_SHARE = 1 / 16.0             # a representative passes the gate: 2^-4 exactly (measured 0.0625)
NEIGHBOUR_WORDS_A = 9 / 16.0      # neighbour words through stage A per representative: nine words when the gate opens
NEIGHBOUR_WORDS_2 = 0.1364        # neighbour words that enter stage 2 per representative (measured)
# The priced items of the procedure beyond stage A and stage 2, per representative, with the layout of Section 6.6:
# the gate test and the dispatch of the passing lanes (513 units when the gate opens), the member list and the
# per-group middle cache (1423/16384), and the end of a run (below 2^-20 and dropped).
CLUSTER_WHEN_OPEN, CLUSTER_PER_WORD = 513, 71
CLUSTER_OVERHEAD = 1423 / 16384.0
# The second stage is SPLIT at the cheap test of Lemma T: of its 150 units per entered word (135 and the 15 that
# place its inputs), 81 run before the test, the test costs 12, and the remaining 57 run only for a word that
# passes it. A lane passes with probability 105/16384, a word of seven lanes with 1 - (1 - 105/16384)^7.
SPLIT_PREFIX, SPLIT_TEST, SPLIT_TAIL, SPLIT_PLACE = 81, 12, 57, 15
TEST_PASS_LANE = 105 / 16384.0
# The budget of this package on the neighbour path, as Section 6.4 budgets the entry to stage 2: the gate opens for
# at most BUDGET_FACTOR times its measured share of the representatives of a run, and at most BUDGET_FACTOR times
# the measured share of neighbour words enters stage 2. The filed entry's budget is 1.194 times its measured share.
BUDGET_FACTOR = 1.2


def entered_word(split=True):
    """Units charged for one word that enters stage 2, with the second stage split at the cheap test or whole."""
    if not split:
        return sum(STAGE_2_BY_RULE[RULE_CONDITIONS]) + SPLIT_PLACE
    passes = 1 - (1 - TEST_PASS_LANE) ** LANES
    return SPLIT_PREFIX + SPLIT_TEST + SPLIT_TAIL * passes + SPLIT_PLACE


def cluster_cost(budget=True, split=True):
    """Units charged per trial whose collision mass rule A keeps ("per trial-equivalent"), and the charge.
    A cluster yields 1 + YIELD such trials per representative. With budget=False the measured rates are used."""
    f = BUDGET_FACTOR if budget else 1.0
    gate, words_2 = GATE_SHARE * f, NEIGHBOUR_WORDS_2 * f
    # The representative words of one outer step: LIST_WORDS words for the 131,072 representatives of the sub-class,
    # at CLUSTER_PER_WORD units each (stage A and the gate test).
    per_rep = CLUSTER_PER_WORD * LIST_WORDS / float(2 ** 17)
    per_rep += CLUSTER_WHEN_OPEN * gate
    per_rep += entered_word(split) * (2.0 ** -RULE_CONDITIONS + words_2)
    per_rep += CLUSTER_OVERHEAD
    cost = per_rep / (1 + YIELD)
    return per_rep, cost, math.ceil(cost * MARGIN_ON_COST * 100 - 1e-9) / 100


def kept_counts(name="a15"):
    """{rule: (exact kept count, conservative kept count)} and R, as fractions, from count/<name>_totals.txt.

    Stops unless the file is for the pin, eta and cube of PART A and its rules are the rules of PART A."""
    text = (COUNT / f"{name}_totals.txt").read_text(encoding="ascii")
    head = text.split("\n")[0]
    if (f"eta {ETA:08x}" not in head or f"extra_mask {CUBE[0]:08x} extra_value {CUBE[1]:08x}" not in head):
        raise SystemExit(f"count/{name}_totals.txt is not for the class and cube of pkg7_data.py")
    out = {}
    for n, short in RULE_NAMES.items():
        listed = re.search(rf"^RULE \d+ (.*?)\s+outside_eta \S+\s+\(name {short}\)$", text, re.M)
        want = sorted(f"{mask:08x}:{value}" for mask, value in RULES[n])
        if not listed or sorted(listed.group(1).split()) != want:
            raise SystemExit(f"count/{name}_totals.txt: rule {short} is not the rule with {n} conditions of pkg7_data.py")
        row = re.search(rf"^rule {short}\s+\({n} conditions\): pass (\d+)/(\d+) = \S+ \| kept_whole (\d+)(?:/(\d+))? = ", text, re.M)
        out[n] = (Fraction(int(row.group(1)), int(row.group(2))), Fraction(int(row.group(3)), int(row.group(4) or 1)))
    total = re.search(r"^R \(all solutions\) = (\d+)/(\d+) = ", text, re.M)
    return out, Fraction(int(total.group(1)), int(total.group(2)))


def per_trial(stage_a, stage_2, share, middle=sum(MIDDLE_STEP), members=CLASS_SIZE, words=LIST_WORDS):
    """Operations, loads and stores per trial: every batch of a value of X2 (the last one has spare lanes, so it is
    words * batch / members and not batch / 7), the middle step once per value of X2, the table build (once per
    outer step for every list word) and the outer step over the 2^32 values of X2 of an outer step."""
    batch = sum(stage_a) + share * sum(stage_2)
    once = (sum(TABLE_BUILD) * words + sum(OUTER_STEP)) / 2 ** X2_VALUES_LOG2
    return (words * batch + middle + once) / members


def cost(rule, stage_a=None, stage_2=None, middle=sum(MIDDLE_STEP)):
    """(expected, budgeted, charged) per trial for a rule: expected with the entry share of independent trials,
    1 - (1 - 2^-n)^7; budgeted with the budget of the program, 2^-(n - 3); charged = budgeted * 1.04 rounded up to
    one decimal."""
    stage_a, stage_2 = stage_a or STAGE_A_BY_RULE[rule], stage_2 or STAGE_2_BY_RULE[rule]
    expected = per_trial(stage_a, stage_2, 1 - (1 - 2.0 ** -rule) ** LANES, middle)
    budgeted = per_trial(stage_a, stage_2, 2.0 ** -(rule - 3), middle)
    return expected, budgeted, math.ceil(budgeted * MARGIN_ON_COST * 10 - 1e-9) / 10


def time_log2(factor, charged):
    return BASE - math.log2(factor) + math.log2(charged / UNIT) + TAIL


def main():
    kept, total = kept_counts()
    print(f"state {SUBMISSION_STATE}; sub-class (e1 AND {CLASS_MASK:08x}) == {CLASS_VALUE:08x}, {CLASS_SIZE} members, "
          f"{LIST_WORDS} list words; R of the sub-class {float(total):,.2f}; rule in use: {RULE_CONDITIONS} conditions "
          f"({RULE_NAMES[RULE_CONDITIONS]}); FACTOR {FACTOR} = 2^{math.log2(FACTOR):.4f}")
    for n in RULES:
        exact, conservative = kept[n]
        expected, budgeted, charged = cost(n)
        line = (f"rule {n} ({RULE_NAMES[n]}): stage A {sum(STAGE_A_BY_RULE[n])}, stage 2 {sum(STAGE_2_BY_RULE[n])}; kept exact "
                f"{float(exact):,.2f}, conservative {float(conservative):,.2f}; expected {expected:.4f}, budgeted {budgeted:.4f}, "
                f"charged {charged:.1f}; time_log2")
        for margin in MARGINS:
            line += f" at margin {margin}: {time_log2(float(exact) / margin, charged):.3f};"
        print(line + f" at FACTOR: {time_log2(FACTOR, charged):.3f} (margin {float(exact) / FACTOR:.4f})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
