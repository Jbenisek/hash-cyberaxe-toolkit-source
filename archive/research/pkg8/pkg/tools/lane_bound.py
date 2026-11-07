#!/usr/bin/env python3
"""Largest lane value of every SUM of the two-stage batch of pkg6, per part, for ALL inputs, by interval arithmetic.

The self-test of the program reports the largest lane of a sum that occurred in its random cases. This tool runs
the same function packed_batch of experiments/halfsearch.py on a second machine that holds, for every register,
not a value but an upper bound of its lanes, and so gives a bound that holds for every context and every member:

  - a loaded word whose lanes are below 2^32 (a constant of the batch, a list word) counts as 2^32 - 1 in every
    lane, whatever its value; the word "bit 32" and the two counters are taken as they are;
  - a sum is bounded by the sum of the bounds of its operands;
  - an XOR is bounded bit by bit: below 2^32 it can be anything, above bit 31 it has at most the bits that one of
    the operands can have;
  - an AND with a loaded constant is bounded by the largest lane of that constant, a shift by 2^36 - 1 (bits of the
    neighbouring lane come in; every shift of the batch is followed by an AND with a loaded mask);
  - an OR is bounded by the all-ones word of the longer operand.

It prints, per part, the largest bound of a sum in units of 2^32 next to the bound of the program's TABLE, the
largest bound of all, and the largest bound of a word that enters the flag computation (it must be below 2^32).
It then runs the program's own machine on random batches and checks that every sum that occurs is at most the
bound found here. Nothing is written.

    python -B tools/lane_bound.py [batches for the comparison, default 2000]

Exit status 0 only if every bound is below the bound of TABLE, all are below 2^36, the flag words are below 2^32
and no observed sum exceeds its bound. Research helper, not submitted.
"""
import importlib.util
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


new = load(PKG / "blake3-r2" / "experiments" / "halfsearch.py", "halfsearch_pkg6")
B = 1 << 32
LOW = B - 1


class Bound:
    """A register of the second machine: top is an upper bound of every lane, exact the loaded constant if it is one."""

    __slots__ = ("z", "top", "exact")

    def __init__(self, top, exact=None):
        self.z, self.top, self.exact = 0, top, exact


class BoundMachine:
    """The machine of the program with bounds in the place of values; it counts operations and loads the same way."""

    def __init__(self):
        self.ops, self.loads, self.sums = {}, {}, {}
        self.part, self.flag_words, self.overflow = None, 0, False

    def at(self, part):
        self.part = part
        self.ops[part] = self.loads[part] = self.sums[part] = 0

    def load(self, constant):
        self.loads[self.part] += 1
        top = max(new.lanes(constant)) if constant >> 252 == 0 else constant
        return Bound(LOW if top < B else top, constant)

    def op(self, top):
        self.ops[self.part] += 1
        return Bound(top)

    def add(self, x, y):
        top = x.top + y.top
        self.sums[self.part] = max(self.sums[self.part], top)
        self.overflow |= top >> new.LANE_BITS != 0
        if new.rep(new.MASK) in (x.exact, y.exact):                # the sum word + M of lane_flags
            self.flag_words = max(self.flag_words, y.top if x.exact == new.rep(new.MASK) else x.top)
        return self.op(top)

    def xor(self, x, y):
        hx, hy = x.top >> 32, y.top >> 32
        high = hx if hy == 0 else hy if hx == 0 else (1 << max(hx.bit_length(), hy.bit_length())) - 1
        return self.op(high << 32 | LOW)

    def band(self, x, y):
        tops = [max(new.lanes(v.exact)) if v.exact is not None else v.top for v in (x, y)]
        return self.op(min(tops))

    def bor(self, x, y):
        return self.op((1 << max(x.top.bit_length(), y.top.bit_length())) - 1)

    def shr(self, x, r):
        return self.op(new.LANE)

    def shl(self, x, r):
        return self.op(new.LANE)

    def pror(self, z, r):
        low = self.band(self.shr(z, r), self.load(new.rep((1 << (32 - r)) - 1)))
        high = self.band(self.shl(z, 32 - r), self.load(new.rep(((1 << r) - 1) << (32 - r))))
        return self.bor(low, high)

    def prol(self, z, r):
        return self.pror(z, 32 - r)

    def advance(self, position):
        return self.op(position + 1)

    def compare_and_branch(self, x, y):
        self.ops[self.part] += 2
        return False


def units(top):
    """A bound written as q * 2^32 - r."""
    q = -(-top // B)
    return f"{q} * 2^32 - {q * B - top}"


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 2000
    rng = random.Random(7)
    X, S, w, c0 = new.context([rng.getrandbits(32) for _ in range(7)])
    bm = BoundMachine()
    new.packed_batch(bm, new.batch_constants(X, S, w, c0)[0], 0)
    table = {row[0]: row for row in new.TABLE}
    ok = not bm.overflow and bm.flag_words < B
    print(f"class eta {new.ETA:08x}, rule A with {len(new.RULE_A)} conditions: bounds of the sums for all inputs (units of 2^32)")
    counts = tuple((part, bm.ops[part], bm.loads[part]) for part in bm.ops)
    same_counts = counts == tuple(row[:3] for row in new.TABLE)
    ok &= same_counts
    for part, top in bm.sums.items():
        quoted = table[part][3]
        if not top:
            ok &= quoted is None
            continue
        below = quoted is not None and top < quoted * B
        ok &= below
        print(f"  {part:16s} largest bound of a sum {units(top):>14s}   bound of TABLE {quoted} * 2^32   "
              f"{'below' if below else 'NOT BELOW'}")
    largest = max(bm.sums.values())
    print(f"largest bound of a sum: {units(largest)} = {largest} < 2^{new.LANE_BITS} = {1 << new.LANE_BITS}: "
          f"{largest < 1 << new.LANE_BITS}; largest bound of a word that enters the flags: {bm.flag_words} (2^32 - 1 = {LOW})")
    print(f"operations and loads per part on the second machine equal TABLE: {same_counts}")
    # the program's machine on random batches: no sum above the bound of its part
    seen, within = {}, True
    for i in range(n):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if i % 4 == 0:                      # extreme words now and then
            seven = [rng.choice((0, new.MASK, v)) for v in seven]
        X, S, w, c0 = new.context(seven)
        m = new.Machine()
        new.packed_batch(m, new.batch_constants(X, S, w, c0)[0], new.BATCHES - 1 if i % 5 == 0 else rng.randrange(new.BATCHES))
        for part, top in m.sums.items():
            seen[part] = max(seen.get(part, 0), top)
            within &= top <= bm.sums[part]
    ok &= within
    print(f"{n} random batches on the program's machine: every sum at most the bound of its part: {within}; largest sum "
          f"seen {max(seen.values()) / B:.3f} * 2^32")
    print("RESULT:", "all bounds hold" if ok else "A BOUND DOES NOT HOLD")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
