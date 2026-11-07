#!/usr/bin/env python3
"""Lemma A as the text of proof.md 6.3 states it, (a) to (d), typed here from the text and compared with the
experiment program on a complete enumeration. Research helper, not submitted.

    python -B tools/lemma_a_text_pkg7.py [fills per pattern, default 4]

For every pattern of the 13 bits of z that the rule reads and every pattern of the bits 27, 28, 29 of e1 (2^16
patterns), with the other bits of z, the guard bits of the lane and both neighbouring lanes filled at random, and
with a member of the sub-class that has those three bits:
  rule A on h1 = ROR(ROR(z, 8) XOR e1, 16), as the program's rule_a() has it        (the rule of 6.3)
  = the eight conditions of (b) on z and e1
  = ((y XOR v) AND ALL) == ALL with y from the three steps of (c) on a word of three lanes and v as (c) defines it
  = bit 32 of u + (2^32 - ALL), and that sum is at most 2^32                          (d)
and v is the lane of the program's list V for that member (rule_word). Also (a) for every case, and that the eight
bits of y at the positions of ALL are the combinations that (c) states. Writes work/text/lemma_a_text.txt.
"""
import hashlib
import importlib.util
import random
import sys
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
M32 = 0xFFFFFFFF
ALL = 0x4F010300
READ_Z = (2, 3, 4, 5, 8, 9, 16, 17, 24, 25, 26, 27, 30)


def bit(x, i):
    return x >> i & 1


def main():
    fills = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    spec = importlib.util.spec_from_file_location("halfsearch_lemma_a", PKG / "blake3-r2" / "experiments" / "halfsearch.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = random.Random(20261006)
    free = [i for i in m.CLASS_FREE if i not in (27, 28, 29)]
    cases = wrong = satisfied = 0
    for pattern in range(1 << 13):
        for e3 in range(8):
            for _ in range(fills):
                z = rng.getrandbits(32) & ~sum(1 << i for i in READ_Z)
                z |= sum(bit(pattern, n) << i for n, i in enumerate(READ_Z))
                e1 = m.CLASS_VALUE | sum(rng.getrandbits(1) << i for i in free) | e3 << 27
                y4 = (e1 - m.Y3) & M32
                assert (e1 & m.CLASS_MASK) == m.CLASS_VALUE
                h1 = m.ror(m.ror(z, 8) ^ e1, 16)
                rule = m.rule_a(h1)
                a = m.rol(h1, 24) == z ^ m.rol(e1, 8) and all(bit(h1, i) == bit(z, (i + 24) % 32) ^ bit(e1, (i + 16) % 32) for i in range(32))
                b = (bit(z, 24) == 0 and bit(z, 25) == 1 and bit(z, 8) == 1 and bit(z, 9) == 1
                     and bit(z, 26) ^ bit(z, 2) == 0 and bit(z, 27) ^ bit(z, 3) == bit(e1, 27)
                     and bit(z, 27) ^ bit(z, 4) ^ bit(z, 16) == bit(e1, 28)
                     and bit(z, 30) ^ bit(z, 5) ^ bit(z, 17) == 1 ^ bit(e1, 29))
                # (c) on a packed word of three 36-bit lanes; the middle lane is Z with random guard bits
                word = rng.getrandbits(36) | (z | rng.getrandbits(4) << 32) << 36 | rng.getrandbits(36) << 72
                mask1, mask2 = 0x0003C000 * (1 | 1 << 36 | 1 << 72), 0x40010000 * (1 | 1 << 36 | 1 << 72)
                s = (word << 12) & mask1
                y = word ^ s
                s = s << 12
                y = y ^ s
                s = (y << 13) & mask2
                y = y ^ s
                lane = y >> 36 & (1 << 36) - 1
                bits = (bit(lane, 8) == bit(z, 8) and bit(lane, 9) == bit(z, 9) and bit(lane, 24) == bit(z, 24)
                        and bit(lane, 25) == bit(z, 25) and bit(lane, 26) == bit(z, 26) ^ bit(z, 2)
                        and bit(lane, 27) == bit(z, 27) ^ bit(z, 3) and bit(lane, 16) == bit(z, 16) ^ bit(z, 4) ^ bit(z, 3)
                        and bit(lane, 30) == bit(z, 30) ^ bit(z, 17) ^ bit(z, 5))
                v = (1 << 24 | 1 << 26 | (1 ^ bit(e1, 27)) << 27 | (1 ^ bit(e1, 27) ^ bit(e1, 28)) << 16 | bit(e1, 29) << 30)
                u = (lane ^ v) & ALL
                c = u == ALL
                total = u + (1 << 32) - ALL
                d = total <= 1 << 32 and bit(total, 32) == c
                cases += 1
                satisfied += rule
                wrong += not (a and bits and d and rule == b == c and v == m.rule_word(y4))
    sha = hashlib.sha256((PKG / "blake3-r2" / "experiments" / "halfsearch.py").read_bytes()).hexdigest()
    line = (f"PROGRAM sha256 {sha}; Lemma A as stated in the text, (a) to (d): {cases} cases (2^16 patterns of the 13 bits of z and "
            f"the 3 bits of e1, {fills} fillings each); wrong {wrong}; the rule holds in {satisfied} ({satisfied / cases:.6f}, 2^-8 is "
            f"{2 ** -8:.6f}); the word v of the text equals rule_word() of the program in every case")
    (PKG / "work" / "text" / "lemma_a_text.txt").write_text(line + "\n", encoding="ascii")
    print(line)
    return 1 if wrong else 0


if __name__ == "__main__":
    sys.exit(main())
