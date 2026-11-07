"""One-time editing helper (step PROGRAM of pkg7): replaces the rule section of the program. Not submitted."""
import sys
from pathlib import Path

p = Path(sys.argv[1])
t = p.read_text(encoding="ascii")
a = t.index("def rule_a_constants():")
b = t.index("def class_member(k):")
new = r'''def rule_a_constants():
    """Lemma A: rule A as a test on z, the XOR of the fifth and the second value of C2, for this sub-class.

    Bit i of h1 is bit (i + 24) mod 32 of z XOR bit (i + 16) mod 32 of e1. So a condition of the rule, "the XOR of
    the bits of h1 in mask is value", reads: the XOR of the bits of z in ROL(mask, 24) is value XOR the XOR of the
    bits of e1 in ROL(mask, 16). The right side is known for every member: e1 = Y3 + Y4. The steps A_STEPS make a
    word y from z by shifts, ANDs with fixed masks and XORs alone, so every bit of y is the XOR of a set of bits of
    z of the same lane or of a neighbouring lane. This function follows the steps on five lanes of names of bits
    and stops unless, for every position t of A_ALL, the set at t has only bits 0 to 31 of the lane itself and is
    the XOR of the sets of some of the conditions (the conditions of t), and unless there are as many positions as
    conditions and the positions are independent as combinations of the conditions. Then "for every t, bit t of y
    is the XOR, over the conditions of t, of their right sides" holds exactly when every condition holds. Returns
    the masks of the steps and, for every t, (t, c, m): the wanted bit at t is c XOR the XOR of the bits of e1 in
    m. rule_word() puts a 1 at t where the wanted bit is 0; with that word v, a trial satisfies rule A exactly
    when ((y XOR v) AND ALL) == ALL.
    """
    rule = [(rol(mask, 24), rol(mask, 16), value) for mask, value in RULE_A]
    width, mid = 5 * LANE_BITS, 2 * LANE_BITS
    y, s, reach = [1 << p for p in range(width)], None, 0

    def shifted(x, d):
        return [x[p - d] if 0 <= p - d < width else 0 for p in range(width)]

    for step in A_STEPS:
        if isinstance(step, tuple):
            s = [v if step[1] >> p % LANE_BITS & 1 else 0 for p, v in enumerate(shifted(y, step[0]))]
        else:
            s = shifted(s, step)
        reach += abs(step[0] if isinstance(step, tuple) else step)
        y = [a ^ b for a, b in zip(y, s)]

    def reduced(bits, combination, basis):
        for b, c in basis:
            if bits ^ b < bits:
                bits, combination = bits ^ b, combination ^ c
        return bits, combination

    basis, independent, flip = [], [], []
    for i, (bits, _, _) in enumerate(rule):
        basis.append(reduced(bits, 1 << i, basis))
        if not basis[-1][0]:
            raise ValueError("rule A: a condition follows from the others")
    for t in range(LANE_BITS):
        if A_ALL >> t & 1:
            if reach > mid or y[mid + t] & (1 << mid) - 1 or y[mid + t] >> mid + 32:
                raise ValueError("rule A: a read position holds a bit of another lane or a bit above 31")
            bits, combination = reduced(y[mid + t] >> mid, 0, basis)
            independent.append(reduced(combination, 0, independent))
            if bits or not independent[-1][0]:
                raise ValueError("rule A: a read position does not hold a new combination of the conditions")
            chosen = [r for i, r in enumerate(rule) if combination >> i & 1]
            flip.append((t, sum(r[2] for r in chosen) & 1, sum(1 << i for i in range(32)
                                                              if sum(r[1] >> i & 1 for r in chosen) & 1)))
    if A_ALL >> 32 or len(flip) != len(rule):
        raise ValueError("rule A: the read positions are not the rule")
    return tuple(step[1] for step in A_STEPS if isinstance(step, tuple)), tuple(flip)


A_MASKS, A_FLIP = rule_a_constants()
# The bits of e1 that the wanted bits depend on and that the sub-class leaves free.
A_FREE = tuple(i for i in CLASS_FREE if any(m >> i & 1 for _, _, m in A_FLIP))


def rule_word(y4):
    """The lane of the list V for class member y4 (Lemma A): a 1 at every read position whose wanted bit is 0."""
    e1 = (Y3 + y4) & MASK
    return sum((1 ^ c ^ bin(e1 & m).count("1") & 1) << t for t, c, m in A_FLIP)


# The memory words that a batch reads, the table words and the word of the list V apart: masks, fixed words, the
# two bounds of the loop, and the words that the outer step and the middle step have stored. With KEPT a number,
# the first KEPT of them are RESIDENT: the class loop entry loads each into a register, and it stays there for all
# batches of the value of X2. They are the masks of the rotations by 16 and by 12, the masks of the steps of rule
# A and the words that stage A must find in a register so that five registers are enough for its values. Stage 2
# gives up the registers of the words EVICT and loads these words again at its end. With RC_AGAIN stage A does not
# keep the third value of C2 and stage 2 forms it again; with Z_AGAIN the first step of rule A takes the register
# of z, and stage 2 forms z again.
BATCH_WORDS = (["A16", "B16", "A12", "B12"] + ["A mask %d" % (n + 1) for n in range(len(A_MASKS))]
               + ["A all", "A carry", "not bit 32", "X2+w7", "w0",
                  "end of list", "-w2", "ROL(X15,8)", "S10+X15", "X14", "stage-2 budget", "A8", "B8", "A7", "B7",
                  "-X15", "S5", "w3", "X13", "X9", "S12", "w12-S1-S6", "Y11", "Y11'", "w5", "w5+delta", "A31",
                  "eta", "M", "bit 32"])
RESIDENT = tuple(BATCH_WORDS if KEPT is None else BATCH_WORDS[:KEPT])
EVICT = () if KEPT is None else RESIDENT[5:]
RC_AGAIN = bool(KEPT)
Z_AGAIN = bool(KEPT and A_STEPS)
# (part, operations, loads, stores, bound) of the four counted pieces: the tables of proof.md Section 6.5 and, in
# units of 2^32, the bound that Section 6.5 gives for the sums of the part. The outer step is run once for the six
# words of an outer step. The table build is run once per outer step for every word of the list, and stores one
# word of each of the five lists of the table. The middle step is run once per value of X2; its last part loads
# the words RESIDENT into registers. The batch is run once per value of X2 for every word of the list, that is for
# seven trials. Its first STAGE_A_PARTS parts are stage A, which every batch runs; the others are stage 2, which a
# batch runs only when one of its lanes passes rule A. The part "rule A" has three operations for every step of
# A_STEPS with a mask, two for every other step and six more, and one load, the word of the list V. The masks of
# the steps take the places of X2 + w7 and w0 among the nine words RESIDENT; stage A then loads these where it
# reads them. Forming z again costs stage 2 four operations and three loads.
A_OPS = sum(3 if isinstance(step, tuple) else 2 for step in A_STEPS)
TABLES = {
    "outer step": (("next w5", 6, 6, 2, 2), ("K2 and D3", 67, 39, 9, 4), ("K3", 43, 25, 4, 7),
                   ("C0 and D2", 32, 21, 6, 5)),
    "table build": (("build loop", 3, 1, 0, None), ("build C0", 13, 11, 2, 3), ("build D1", 27, 14, 3, 4)),
    "middle step": (("next X2", 6, 7, 2, 2), ("D2 and K1", 47, 15, 4, 8), ("K0", 32, 9, 3, 6),
                    ("class loop entry", 0, len(RESIDENT), 0, None)),
    "batch": (("loop", 3, 1, 0, None), ("X0 to X10", 3, 4, 0, 3), ("C2 to z", 17, 2 + len(A_MASKS), 0, 4),
              ("rule A", 6 + A_OPS, 1, 0, 2), ("entry count", 3, 1, 0, None),
              ("C2, rest", 13 + 4 * Z_AGAIN, 4 + 3 * Z_AGAIN, 0, 5), ("C1 to Y1", 31, 8, 0, 5),
              ("E1, A and B", 41, 6, 0, 9), ("E1 test", 13, 4, 0, 2), ("restore", 0, len(EVICT), 0, None)),
}
STAGE_A_PARTS = 4
# The budget of proof.md 6.4 step 4 on the batches that enter stage 2: a share 2^-STAGE_2_LOG2_SHARE of the batches
# of a run, one half, one eighth or one part in 32 for the rule with four, six or eight conditions. A run has
# 2^127 / FACTOR trials, FACTOR being the factor that proof.md Section 7 assumes for the rate: that is RUN_PAIRS
# pairs of an outer step and a value of X2, with BATCHES batches each.
FACTOR = 49400000
RUN_PAIRS = -(-(1 << 127) // (FACTOR * CLASS_SIZE))
STAGE_2_LOG2_SHARE = len(RULE_A) - 3
STAGE_2_BUDGET = BATCHES * RUN_PAIRS >> STAGE_2_LOG2_SHARE


'''
t = t[:a] + new + t[b:]
p.write_bytes(t.encode("ascii"))
print(len(t.encode("ascii")))
