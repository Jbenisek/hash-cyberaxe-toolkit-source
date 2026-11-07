#!/usr/bin/env python3
"""Largest lane value of every SUM of the four counted pieces, per part, for ALL inputs, by interval arithmetic,
and a check that no shifted bit of a neighbouring lane survives.

    python -B work/tools/lane_bound.py [cases for the comparison, default 2000]   writes work/evidence/lane_bound.txt

The self-test of the program reports the largest lane of a sum that occurred in its random cases. This tool runs
the same functions outer_step, table_build, middle_step and packed_batch of halfsearch.py on a second machine, a
subclass of the program's Machine (so it counts, keeps and drops words exactly as that one does) that holds, for
every register, not a value but an upper bound of its lanes, and so gives a bound that holds for every context and
every member (the method of the tool of the same name of research/pkg7_program):

  - a loaded word whose lanes are below 2^32 (a memory cell, a list word, a table word) counts as 2^32 - 1 in every
    lane, whatever its value; the words "bit 32", "not bit 32" and the counters are taken as they are;
  - a sum is bounded by the sum of the bounds of its operands;
  - an XOR is bounded bit by bit: below 2^32 it can be anything, above bit 31 it has at most the bits that one of
    the operands can have;
  - an AND with a fixed cell of the program (a rotation mask, M, "bit 32", the masks of rule A) is bounded by the
    largest lane of that cell, any other AND by the smaller bound of its operands;
  - an OR is bounded by the all-ones word of the longer operand;
  - a store must write a word whose bound is below 2^32 (this is what lets a later load count as 2^32 - 1); the
    stored word is then taken as 2^32 - 1 in every lane.

Because the E1 test and the steps of rule A have shifts that are not followed by an AND with a rotation mask:

  - a shift to the right by r brings the low r bits of the next lane to the positions 36 - r and above. Its result
    is marked, and the only thing allowed with a marked word is an AND with a fixed cell that has no bit at those
    positions (then the mark is gone);
  - a shift to the left by r of a word whose bound, shifted, stays below 2^36 moves no bit out of its lane: the
    result is bounded by the shifted bound and is not marked. Otherwise the bits that leave the lane arrive at the
    low positions of the next lane, up to (bits of the bound) + r - 36: the result is marked, and the only thing
    allowed is an AND with a fixed cell that has no bit below that position;
  - any other use of a marked word is reported as a fault.

And for the end of stage A: the word that is added to "A carry" must be bounded by ALL (then bit 32 of the sum is
set exactly when the word is ALL).

Per rule (4, 6, 8 conditions, the line RULE_CONDITIONS set in memory) it gives, per part, the largest bound of a
sum in units of 2^32 next to the bound of the program's TABLES, the largest bound of a word that enters the flag
computation of stage 2 (it must be below 2^32) and the largest bound of a stored word. It then runs the program's
own machine on random cases and checks that every sum that occurs is at most the bound found here.

Exit status 0 only if every bound is below the bound of TABLES, all are below 2^36, the flag words and the stored
words are below 2^32, no marked word is misused, the counts on the second machine equal TABLES and no observed sum
exceeds its bound. Research helper, not submitted.
"""
import random
import sys

from common import HEAD, RULES, program_with_rule, sha, write

B = 1 << 32
LOW = B - 1


def bound_machine(new, fixed):
    class Bound:
        """A register of the second machine: top bounds every lane; exact is the word if it came from memory;
        need is the mark of a shifted word (kind, position)."""

        __slots__ = ("z", "top", "exact", "born", "last", "need")

        def __init__(self, top, exact=None, need=None):
            self.z, self.top, self.exact, self.born, self.last, self.need = exact or 0, top, exact, 0, 0, need

    class BoundMachine(new.Machine):
        """The machine of the program with bounds in the place of values; k, get, drop, resident, finish and the
        rotation are the program's own, so it counts the same way."""

        def __init__(self):
            super().__init__()
            self.flag_words, self.flag_a, self.stored, self.overflow, self.faults = 0, 0, 0, False, []

        def word(self, constant):
            top = max(new.lanes(constant)) if constant >> 252 == 0 else constant
            return Bound(LOW if top < B else top, constant)

        def value(self, z, *used):                      # only resident() arrives here: a memory word in a register
            return self.word(z)

        def clean(self, *words):
            for x in words:
                if x.need:
                    self.faults.append((self.part, x.need))

        def load(self, constant):
            self.loads[self.part] += 1
            return self.word(constant)

        def store(self, x):
            self.clean(x)
            self.stores[self.part] += 1
            self.stored = max(self.stored, x.top)
            return new.rep(new.MASK)

        def op(self, top, need=None):
            self.ops[self.part] += 1
            return Bound(top, None, need)

        def add(self, x, y):
            self.clean(x, y)
            top = x.top + y.top
            self.sums[self.part] = max(self.sums[self.part], top)
            self.overflow |= top >> new.LANE_BITS != 0
            if self.part == "E1 test" and new.rep(new.MASK) in (x.exact, y.exact):          # word + M of lane_flags
                self.flag_words = max(self.flag_words, y.top if x.exact == new.rep(new.MASK) else x.top)
            if self.part == "rule A" and new.rep(-new.A_ALL) in (x.exact, y.exact):         # u + carry of rule_a_flags
                self.flag_a = max(self.flag_a, y.top if x.exact == new.rep(-new.A_ALL) else x.top)
            return self.op(top)

        def xor(self, x, y):
            self.clean(x, y)
            hx, hy = x.top >> 32, y.top >> 32
            high = hx if hy == 0 else hy if hx == 0 else (1 << max(hx.bit_length(), hy.bit_length())) - 1
            return self.op(high << 32 | LOW)

        def band(self, x, y):
            for v, w in ((x, y), (y, x)):
                if v.need:
                    kind, at = v.need
                    mask = max(new.lanes(w.exact)) if w.exact in fixed and not w.need else None
                    if mask is None or (mask >> at if kind == "high" else mask & ((1 << at) - 1)):
                        self.faults.append((self.part, v.need))
            tops = [max(new.lanes(v.exact)) if v.exact in fixed else v.top for v in (x, y)]
            return self.op(min(tops))

        def bor(self, x, y):
            self.clean(x, y)
            return self.op((1 << max(x.top.bit_length(), y.top.bit_length())) - 1)

        def shr(self, x, r):
            self.clean(x)
            return self.op(new.LANE, ("high", new.LANE_BITS - r))

        def shl(self, x, r):
            self.clean(x)
            if x.top << r <= new.LANE:
                return self.op(x.top << r)
            return self.op(new.LANE, ("low", x.top.bit_length() + r - new.LANE_BITS))

        def advance(self, position):
            self.ops[self.part] += 1
            return Bound(position + 1, position + 1)

        def compare_and_branch(self, x, y):
            self.clean(x, y)
            self.ops[self.part] += 2
            return False

    return BoundMachine


def units(top):
    """A bound written as q * 2^32 - r."""
    q = -(-top // B)
    return f"{q} * 2^32 - {q * B - top}"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    out = [f"{HEAD}PROGRAM sha256 {sha()}; python -B work/tools/lane_bound.py {n}"]
    short, good = [], True
    for rule in RULES:
        new = program_with_rule(rule)
        rng = random.Random(7)
        c = new.memory([rng.getrandbits(32) for _ in range(7)])
        fixed = {new.rep(v) for v in new.FIXED.values()} | {c["bit 32"], c["not bit 32"]}
        BoundMachine = bound_machine(new, fixed)
        bms = {name: BoundMachine() for name in new.TABLES}
        new.outer_step(bms["outer step"], c)
        row = new.table_build(bms["table build"], c, 0)
        new.middle_step(bms["middle step"], c)
        new.packed_batch(bms["batch"], c, row, 0)
        ok = True
        out.append("")
        out.append(f"RULE WITH {rule} CONDITIONS: bounds of the sums for all inputs (units of 2^32)")
        largest, flag_words, flag_a, stored, faults = 0, 0, 0, 0, []
        for name, bm in bms.items():
            table = {row_[0]: row_ for row_ in new.TABLES[name]}
            counts = tuple((part, bm.ops[part], bm.loads[part], bm.stores[part]) for part in bm.ops)
            same_counts = counts == tuple(row_[:4] for row_ in new.TABLES[name])
            ok &= same_counts and not bm.overflow
            for part, top in bm.sums.items():
                quoted = table[part][4]
                if not top:
                    ok &= quoted is None
                    continue
                below = quoted is not None and top < quoted * B
                ok &= below
                out.append(f"  {name:11s} {part:12s} largest bound of a sum {units(top):>15s}   bound of TABLES "
                           f"{quoted} * 2^32   {'below' if below else 'NOT BELOW'}")
            out.append(f"  {name}: operations, loads and stores per part on the second machine equal TABLES: {same_counts}; "
                       f"largest bound of a sum {units(max(bm.sums.values()))}; largest bound of a stored word "
                       f"{bm.stored} (2^32 - 1 = {LOW}); shifted words misused: {len(bm.faults)} {bm.faults[:4]}")
            largest = max(largest, max(bm.sums.values()))
            flag_words, flag_a, stored = max(flag_words, bm.flag_words), max(flag_a, bm.flag_a), max(stored, bm.stored)
            faults += bm.faults
        ok &= 0 < flag_words < B and 0 < flag_a <= new.A_ALL and stored < B and largest < 1 << new.LANE_BITS and not faults
        # the program's machine on random cases: no sum above the bound of its part
        seen, within = 0, True
        for i in range(n):
            seven = [rng.getrandbits(32) for _ in range(7)]
            if i % 4 == 0:                      # extreme words now and then
                seven = [rng.choice((0, new.MASK, v)) for v in seven]
            c = new.memory(seven)
            ms = {name: new.Machine() for name in new.TABLES}
            j = new.BATCHES - 1 if i % 5 == 0 else rng.randrange(new.BATCHES)
            new.outer_step(ms["outer step"], c)
            row = new.table_build(ms["table build"], c, j)
            new.middle_step(ms["middle step"], c)
            new.packed_batch(ms["batch"], c, row, j)
            for name, m in ms.items():
                for part, top in m.sums.items():
                    seen = max(seen, top)
                    within &= top <= bms[name].sums[part]
        ok &= within
        out.append(f"  largest bound of a sum: {units(largest)} = {largest} < 2^{new.LANE_BITS} = {1 << new.LANE_BITS}: "
                   f"{largest < 1 << new.LANE_BITS}; largest bound of a word that enters the flags of stage 2: {flag_words}; "
                   f"of the word added to the carry word of stage A: {flag_a} (ALL = {new.A_ALL}); of a stored word: "
                   f"{stored} (2^32 - 1 = {LOW}); shifted words misused in all pieces: {len(faults)}")
        out.append(f"  {n} random cases on the program's machine: every sum at most the bound of its part: {within}; largest "
                   f"sum seen {seen / B:.3f} * 2^32")
        out.append("  RESULT: " + ("all bounds hold" if ok else "A BOUND DOES NOT HOLD"))
        short.append(f"rule {rule}: largest bound of a sum {units(largest)} (< 2^36: {largest < 1 << new.LANE_BITS}); flag words "
                     f"< 2^32: {flag_words < B}; stage A word <= ALL: {flag_a <= new.A_ALL}; stored < 2^32: {stored < B}; "
                     f"shifted words misused: {len(faults)}; observed within bounds: {within}; "
                     f"{'all bounds hold' if ok else 'A BOUND DOES NOT HOLD'}")
        good &= ok
    write("lane_bound.txt", out)
    print("\n".join(short))
    print("RESULT:", "all bounds hold" if good else "A BOUND DOES NOT HOLD", f" (detail in work/evidence/lane_bound.txt)")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
