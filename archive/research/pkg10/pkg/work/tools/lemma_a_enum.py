#!/usr/bin/env python3
"""Lemma A of the program of research/pkg7, stated here a second time by hand and checked by complete enumeration.

    python -B work/tools/lemma_a_enum.py [fills per pattern, default 16]     writes work/evidence/lemma_a_enum.txt

Nothing in this file is taken from the program except, at the very end, a comparison of the constants typed here
with the program's. The statement, for the sub-class (e1 AND 07ef8303) == 030c0303 and h1 = ROR(ROR(z, 8) XOR e1, 16),
so that bit i of h1 is bit (i + 24) mod 32 of z XOR bit (i + 16) mod 32 of e1:

  RULE with eight conditions on h1 (research/pkg7/count/COUNT.md, rule S8):
      h0 = 0, h1 = 1, h16 = 0, h17 = 0, h2 ^ h10 = 1, h3 ^ h11 = 1, h3 ^ h12 ^ h24 = 0, h6 ^ h13 ^ h25 = 0
  TEST with eight conditions, on one lane of 36 bits (z may have bits 32 to 35):
      s = (z << 12) AND 0003c000;  y = z XOR s;  s = s << 12;  y = y XOR s;  s = (y << 13) AND 40010000;  y = y XOR s
      passes when at the positions 8, 9, 16, 24, 25, 26, 27, 30 the bits of y are
      y8 = e0, y9 = e1, y24 = e16, y25 = 1 ^ e17, y26 = 1 ^ e18 ^ e26, y27 = 1 ^ e19 ^ e27,
      y16 = 1 ^ e8 ^ e27 ^ e28, y30 = e9 ^ e22 ^ e29          (e_i is bit i of e1)
  RULE with six conditions: the first six of the eight.  TEST: s = (z << 24) AND 0c000000; y = z XOR s; positions
      8, 9, 24, 25, 26, 27 with the wanted bits of the list above.
  RULE with four conditions: the first four.  TEST: y = z; positions 8, 9, 24, 25.

CLAIM: for every z below 2^36 and every e1 of the sub-class, TEST passes exactly when RULE holds.

Why an enumeration is complete. RULE reads the bits 2, 3, 4, 5, 8, 9, 16, 17, 24, 25, 26, 27, 30 of z (13 bits; 8 for
six conditions, 4 for four) and the bits 0, 1, 8, 9, 16, 17, 18, 19, 22, 26, 27, 28, 29 of e1. TEST is made of shifts,
ANDs with fixed masks and XORs, so each of its eight bits is an XOR of bits of z and e1; which ones, the tool finds
by trying: it flips every one of the 36 bits of z and every one of the 32 bits of e1 in turn, on random words, and
records every bit that ever changes the outcome of TEST or of RULE (SUPPORT below). All 2^13 patterns of the z bits
are then run with all patterns of the bits of e1 in the support that the sub-class leaves free, each with several
random fills of all other bits (other bits of z including 32 to 35, other free bits of e1). Since both sides
depend on nothing outside the support, agreement on every pattern is agreement on every input.

The tool also runs the test inside a 256-bit word of seven lanes with random neighbours (a shift moves bits of the
next lane in): the lane's outcome must not change. Research helper, not submitted.
"""
import random
import sys

from common import program_with_rule, sha, write

M32, LANE_BITS, LANES = 0xFFFFFFFF, 36, 7
CLASS_MASK, CLASS_VALUE = 0x07EF8303, 0x030C0303
RULE = {4: ((0, 0), (1, 1), (16, 0), (17, 0))}                     # (bits of h1 XORed, value)
RULE[6] = RULE[4] + (((2, 10), 1), ((3, 11), 1))
RULE[8] = RULE[6] + (((3, 12, 24), 0), ((6, 13, 25), 0))
STEPS = {4: (), 6: ((24, 0x0C000000),), 8: ((12, 0x0003C000), 12, (13, 0x40010000))}
WANTED = {8: (0, (0,)), 9: (0, (1,)), 24: (0, (16,)), 25: (1, (17,)), 26: (1, (18, 26)), 27: (1, (19, 27)),
          16: (1, (8, 27, 28)), 30: (0, (9, 22, 29))}             # position of y: (constant, bits of e1 XORed)
POSITIONS = {4: (8, 9, 24, 25), 6: (8, 9, 24, 25, 26, 27), 8: (8, 9, 16, 24, 25, 26, 27, 30)}


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M32


def bit(v, i):
    return v >> i & 1


def rule(n, z, e1):
    h1 = ror(ror(z & M32, 8) ^ e1, 16)
    for bits, value in RULE[n]:
        bits = (bits,) if isinstance(bits, int) else bits
        if sum(bit(h1, i) for i in bits) & 1 != value:
            return False
    return True


def test_word(n, z, width):
    """y of the test for a word of the given width (36: one lane; 252: seven lanes, the masks in every lane)."""
    full = (1 << width) - 1
    y, s = z, None
    for step in STEPS[n]:
        if isinstance(step, tuple):
            s = (y << step[0]) & full & sum(step[1] << LANE_BITS * i for i in range(width // LANE_BITS))
        else:
            s = (s << step) & full
        y ^= s
    return y


def test(n, z, e1):
    y = test_word(n, z, LANE_BITS)
    return all(bit(y, t) == WANTED[t][0] ^ (sum(bit(e1, i) for i in WANTED[t][1]) & 1) for t in POSITIONS[n])


def main():
    fills = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    rng = random.Random(8)
    free = [i for i in range(32) if not CLASS_MASK >> i & 1]
    out = [f"PROGRAM sha256 {sha()} (used only for the last comparison); python -B work/tools/lemma_a_enum.py {fills}"]
    good = True

    def member():
        e1 = CLASS_VALUE
        for i in free:
            e1 |= rng.getrandbits(1) << i
        return e1

    for n in (4, 6, 8):
        # SUPPORT: the bits of z and the free bits of e1 that can change TEST or RULE
        zs, es = set(), set()
        for _ in range(20000):
            z, e1 = rng.getrandbits(LANE_BITS), member()
            base = (test(n, z, e1), rule(n, z, e1))
            for i in range(LANE_BITS):
                if (test(n, z ^ 1 << i, e1), rule(n, z ^ 1 << i, e1)) != base:
                    zs.add(i)
            for i in free:
                if (test(n, z, e1 ^ 1 << i), rule(n, z, e1 ^ 1 << i)) != base:
                    es.add(i)
        zs, es = sorted(zs), sorted(es)
        expected_z = sorted({(i + 24) % 32 for bits, _ in RULE[n] for i in ((bits,) if isinstance(bits, int) else bits)})
        expected_e = sorted({(i + 16) % 32 for bits, _ in RULE[n] for i in ((bits,) if isinstance(bits, int) else bits)} & set(free))
        support_ok = zs == expected_z and es == expected_e
        # complete enumeration over the support, several fills of everything else
        total = agree = passing = 0
        for pattern in range(1 << len(zs) + len(es)):
            for _ in range(fills):
                z, e1 = rng.getrandbits(LANE_BITS), member()
                for k, i in enumerate(zs):
                    z = z & ~(1 << i) | (pattern >> k & 1) << i
                for k, i in enumerate(es):
                    e1 = e1 & ~(1 << i) | (pattern >> len(zs) + k & 1) << i
                a, b = test(n, z, e1), rule(n, z, e1)
                total, agree, passing = total + 1, agree + (a == b), passing + b
        # seven lanes: the neighbours do not change a lane's outcome
        lanes_same = lanes_total = 0
        for _ in range(20000):
            word = rng.getrandbits(LANE_BITS * LANES)
            y = test_word(n, word, LANE_BITS * LANES)
            for lane in range(LANES):
                alone = test_word(n, word >> LANE_BITS * lane & (1 << LANE_BITS) - 1, LANE_BITS)
                lanes_total += 1
                lanes_same += all(bit(y >> LANE_BITS * lane, t) == bit(alone, t) for t in POSITIONS[n])
        ok = support_ok and agree == total and lanes_same == lanes_total and passing * (1 << n) == total
        good &= ok
        out.append(f"RULE WITH {n} CONDITIONS: support found by flipping bits: z {zs}, free bits of e1 {es} "
                   f"(expected {expected_z}, {expected_e}: {support_ok}); patterns {1 << len(zs) + len(es)} * {fills} fills = "
                   f"{total} inputs, TEST = RULE in {agree}; RULE holds in {passing} (a share 2^-{n}: "
                   f"{passing * (1 << n) == total}); a lane inside a word of seven lanes with random neighbours gives the same "
                   f"eight bits as alone in {lanes_same} of {lanes_total}; {'ok' if ok else 'FAIL'}")
        hs = program_with_rule(n)
        typed = (tuple(STEPS[n]), tuple(sorted((t, WANTED[t][0], sum(1 << i for i in WANTED[t][1])) for t in POSITIONS[n])),
                 tuple((sum(1 << i for i in ((b,) if isinstance(b, int) else b)), v) for b, v in RULE[n]),
                 (CLASS_MASK, CLASS_VALUE))
        theirs = (tuple(hs.A_STEPS), tuple(sorted(hs.A_FLIP)), tuple(hs.RULE_A), (hs.CLASS_MASK, hs.CLASS_VALUE))
        same = typed == theirs and hs.A_ALL == sum(1 << t for t in POSITIONS[n])
        good &= same
        out.append(f"   the steps, the read positions, the wanted bits, the rule and the sub-class typed here are those of the "
                   f"program: {same}")
    out.append("RESULT: " + ("TEST = RULE on every pattern, for the three rules" if good else "FAILED"))
    write("lemma_a_enum.txt", out)
    print("\n".join(line[:300] for line in out[1:]))
    return 0 if good else 1


if __name__ == "__main__":
    sys.exit(main())
