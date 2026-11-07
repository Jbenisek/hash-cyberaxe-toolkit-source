#!/usr/bin/env python3
"""The work per value of X14 before its batches, counted on the program's machine. Research helper, not submitted.

    python -B tools/prep_count.py [contexts]     (default 20000) prints the count, writes evidence/prep_count.txt

The middle loop of the algorithm takes the next value of X14, computes the nineteen lines of the context that
read X14 (the second block of context() in experiments/halfsearch.py) and from them the thirteen constants of a
batch that change with X14 (batch_constants(), group for_x14), and stores the thirteen. The data module charges
PREP_OPS for this, per value of X14. Here the same work is written with calls of the program's Machine only, on
packed words that hold the same 32-bit value in all seven lanes, so that every constant comes out in the
seven-lane form in which a batch loads it, and every operation, every load and every store is counted:

  - an operand that the outer loop left in memory (a word that does not change with X14) is one load every time
    it is used; X14 itself is read from the memory cell of the batch constant "X14" and written back to it;
  - a subtraction x - y is x + (y XOR M) + 1 in every lane (the 1 is merged into a stored operand where one is
    at hand); a rotation is the five operations and two loads of the program's pror; the end test of the middle
    loop is a comparison and a branch, as in the batch;
  - each of the thirteen constants is reduced to 32 bits per lane (AND M) unless it comes out of a rotation or of
    an XOR of reduced words, and is stored: one store each.

For every context drawn (every fifth with extreme words) it checks that the thirteen stored words equal those of
batch_constants() for the context with that X14, that the counts are the same in every case, that no lane of a
sum reaches 2^36 and that at most 16 registers are in use (two of them hold the list position and the stage-2
entry count, as in the batch). It also checks that no other constant of a batch changes with X14 and that each
of the thirteen does. The cost of the outer loop (the lines of the context that do not read X14, once per
context) is not counted here.
"""
import hashlib
import importlib.util
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
PROGRAM = PKG / "blake3-r2" / "experiments" / "halfsearch.py"
sys.path.insert(0, str(TOOLS))
import pkg6_data as data  # noqa: E402

FOR_X14 = ("C0.b1", "-C0.b1-w6", "-X4-w2", "S10+X15", "S6", "X14", "S5", "w3", "X9", "-S1-S6", "w12", "w5", "w5+delta")


def load_program():
    spec = importlib.util.spec_from_file_location("halfsearch_pkg6", PROGRAM)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def outer(hs, c0c, c0d, s11, s4, x13, w0):
    """The words that the outer loop leaves in memory for the middle loop: (per context, fixed), as 32-bit values.

    The lines are those of the first block of context() in the program (they do not read X14); only the values
    that the lines reading X14 or the thirteen constants use are returned.
    """
    IV, M, rol, ror = hs.IV, hs.MASK, hs.rol, hs.ror
    a1_k0 = (IV[0] + IV[4] + w0) & M
    c1_k0 = (IV[0] + ror(a1_k0, 16)) & M
    s8 = rol(s4, 7) ^ ror(IV[4] ^ c1_k0, 12)
    x8 = (c0c - c0d) & M
    c1_d2 = (x8 - x13) & M
    d1_d2 = (c1_d2 - s8) & M
    b1_d2 = rol(hs.X7, 7) ^ x8
    s7 = rol(b1_d2, 12) ^ c1_d2
    x2 = rol(x13, 8) ^ d1_d2
    a1_d2 = (x2 - b1_d2 - hs.W13) & M
    s13 = rol(d1_d2, 16) ^ a1_d2
    c1_k3 = rol(rol(s7, 7) ^ s11, 12) ^ IV[7]
    d1_k3 = (c1_k3 - IV[3]) & M
    s3 = rol((s11 - c1_k3) & M, 8) ^ d1_k3
    w6 = ((rol(d1_k3, 16) ^ 11) - IV[3] - IV[7]) & M
    a1_k2 = (hs.K + hs.W4) & M
    d1_k2 = ror(a1_k2 ^ hs.LEN_A, 16)
    c1_k2 = (IV[2] + d1_k2) & M
    b1_k2 = ror(IV[6] ^ c1_k2, 12)
    a1_d3 = (s3 + s4) & M
    b1_d3 = (hs.X3 - a1_d3) & M
    c1_d3 = rol(b1_d3, 12) ^ s4
    per_context = {"c1_d3+1": c1_d3 + 1, "a1_d3": a1_d3, "c1_d3": c1_d3, "b1_d3": b1_d3, "a1_d2-S7+1": a1_d2 - s7 + 1,
                   "-S13": -s13, "ROL(S13,8)": rol(s13, 8), "C0.c1": c0c, "1-w6": 1 - w6}
    fixed = {"X3": hs.X3, "c1_k2": c1_k2, "b1_k2": b1_k2, "d1_k2": d1_k2, "-a1_k2-b1_k2": -a1_k2 - b1_k2, "-IV1": -IV[1],
             "IV5": IV[5], "-IV1-IV5": -IV[1] - IV[5], "X15": hs.X15, "delta": hs.DELTA5, "M": M, "1": 1}
    return per_context, fixed


def prepare(hs, m, mem, previous, limit):
    """One step of the middle loop on the machine m: returns the thirteen stored words by name."""
    def k(name):
        return m.load(mem[name])

    out = {}
    m.at("next X14")                                                  # next value, end test, branch, store
    x14 = m.band(m.add(m.load(previous), k("1")), k("M"))
    m.compare_and_branch(x14, m.load(limit))
    out["X14"] = m.store(x14)
    m.at("D3 and K2")
    d1_d3 = m.xor(m.prol(x14, 8), k("X3"))
    s9 = m.add(m.xor(d1_d3, k("M")), k("c1_d3+1"))                    # S9 = c1_d3 - d1_d3
    s14 = m.xor(m.prol(d1_d3, 16), k("a1_d3"))
    x9 = m.add(x14, k("c1_d3"))
    out["X9"] = m.store(m.band(x9, k("M")))
    x4 = m.pror(m.xor(x9, k("b1_d3")), 7)
    s10 = m.add(s14, k("c1_k2"))
    out["S10+X15"] = m.store(m.band(m.add(s10, k("X15")), k("M")))
    s6 = m.pror(m.xor(s10, k("b1_k2")), 7)
    out["S6"] = m.store(s6)
    s2 = m.xor(m.prol(s14, 8), k("d1_k2"))
    w5 = m.add(s2, k("-a1_k2-b1_k2"))                                 # w5 = S2 - a1_k2 - b1_k2
    out["w5"] = m.store(m.band(w5, k("M")))
    out["w5+delta"] = m.store(m.band(m.add(w5, k("delta")), k("M")))
    out["w12"] = m.store(m.band(m.add(m.xor(s2, k("M")), k("a1_d2-S7+1")), k("M")))   # w12 = a1_d2 - S2 - S7
    m.at("K1")
    c1_k1 = m.add(s9, k("-S13"))
    d1_k1 = m.add(c1_k1, k("-IV1"))
    a1_k1 = m.prol(d1_k1, 16)
    b1_k1 = m.pror(m.xor(c1_k1, k("IV5")), 12)
    s1 = m.xor(d1_k1, k("ROL(S13,8)"))
    s5 = m.pror(m.xor(b1_k1, s9), 7)
    out["S5"] = m.store(s5)
    out["-S1-S6"] = m.store(m.band(m.add(m.xor(m.add(s1, s6), k("M")), k("1")), k("M")))
    w2 = m.add(a1_k1, k("-IV1-IV5"))                                  # w2 = a1_k1 - IV1 - IV5
    out["-X4-w2"] = m.store(m.band(m.add(m.xor(m.add(x4, w2), k("M")), k("1")), k("M")))
    w3 = m.add(m.add(s1, m.xor(m.add(a1_k1, b1_k1), k("M"))), k("1"))  # w3 = S1 - a1_k1 - b1_k1
    out["w3"] = m.store(m.band(w3, k("M")))
    m.at("C0")
    c0b = m.pror(m.xor(x4, k("C0.c1")), 12)
    out["C0.b1"] = m.store(c0b)
    out["-C0.b1-w6"] = m.store(m.band(m.add(m.xor(c0b, k("M")), k("1-w6")), k("M")))
    return out


def main():
    contexts = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    hs = load_program()

    class Counting(hs.Machine):
        """The program's machine with a store: one more counted kind of step, which ends the life of its operand."""

        def __init__(self):
            super().__init__()
            self.stores = {}

        def at(self, part):
            super().at(part)
            self.stores[part] = 0

        def store(self, x):
            self.stores[self.part] += 1
            self.step += 1
            x.last = self.step
            return x.z

    rng = random.Random(20261006)
    shape, same, equal, registers, largest = None, True, 0, 0, 0
    changed, others = set(), set()
    names = None
    for case in range(contexts):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if case % 5 == 4:                       # extreme words: each context word is 0, 2^32 - 1 or as drawn
            seven = [(0, hs.MASK, v, v)[rng.randrange(4)] for v in seven]
        c0c, c0d, s11, s4, x13, x14, w0 = seven
        per_context, fixed = outer(hs, c0c, c0d, s11, s4, x13, w0)
        mem = {name: hs.rep(value) for group in (per_context, fixed) for name, value in group.items()}
        m = Counting()
        out = prepare(hs, m, mem, hs.rep(x14 - 1), hs.rep(rng.getrandbits(32)))
        X, S, w, c0 = hs.context(seven)
        c, _, for_x14 = hs.batch_constants(X, S, w, c0)
        equal += int(for_x14 == len(FOR_X14) == len(out) and all(out[name] == c[name] for name in FOR_X14))
        found = (tuple((p, m.ops[p], m.loads[p], m.stores[p]) for p in m.ops), len(per_context), len(fixed))
        shape = shape or found
        same = same and found == shape
        registers = max(registers, m.registers())
        largest = max(largest, max(m.sums.values()))
        other = list(seven)
        other[5] = rng.getrandbits(32)
        c2 = hs.batch_constants(*hs.context(other))[0]
        names = names or set(c)
        differ = {name for name in c if c[name] != c2[name]}
        changed |= differ & set(FOR_X14)
        others |= differ - set(FOR_X14)
    table, n_context, n_fixed = shape
    ops, loads, stores = (sum(row[i] for row in table) for i in (1, 2, 3))
    total = ops + loads + stores
    only = not others and changed == set(FOR_X14) and set(FOR_X14) <= names
    good = (equal == contexts and same and registers <= hs.REGISTERS and largest < 1 << hs.LANE_BITS and only
            and total <= data.PREP_OPS)
    sha = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    out = [f"PROGRAM sha256 {sha}; python -B tools/prep_count.py {contexts}",
           "work per value of X14 before its batches, on the program's machine (packed words, the same value in seven lanes):",
           "  " + "; ".join(f"{p}: {o} operations, {l} loads, {s} stores" for p, o, l, s in table),
           f"  total {ops} operations + {loads} loads + {stores} stores = {total}; PREP_OPS of the data module {data.PREP_OPS} "
           f"(covers it: {total <= data.PREP_OPS}); per trial {total} / {hs.CLASS_SIZE} = {total / hs.CLASS_SIZE:.6f}, "
           f"PREP_OPS per trial {data.PREP_OPS / hs.CLASS_SIZE:.6f}",
           f"  registers {registers} of {hs.REGISTERS}; largest lane of a sum {(largest * 1000 >> 32) / 1000} * 2^32 (below 2^36: "
           f"{largest < 1 << hs.LANE_BITS}); words that the outer loop leaves in memory for it: {n_context} per context, {n_fixed} fixed",
           f"  {contexts} contexts (every fifth with extreme words): the thirteen stored words equal batch_constants() in {equal} of "
           f"{contexts}; same counts in every case: {same}; the constants of a batch that change with X14 are these thirteen and "
           f"no other: {only}",
           "RESULT: " + ("the count holds and PREP_OPS covers it" if good else "FAILED"),
           f"exit status {0 if good else 1}"]
    text = "\n".join(out) + "\n"
    (PKG / "evidence" / "prep_count.txt").write_bytes(text.encode("ascii"))
    print(text, end="")
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
