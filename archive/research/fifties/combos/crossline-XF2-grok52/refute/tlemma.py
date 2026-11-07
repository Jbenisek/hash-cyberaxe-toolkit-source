"""Exhaustive check of the algebra in RESULT.md section 2: for every choice of the seven 7-bit constants
(sampled 200000 times at random, plus 0/127 corners), with z = y[1..7] over the 64 odd values and
omega = 3 + 4u + P(z), P(z) = ((((z ^ b) - c - br8) ^ d) - A - br16) ^ L) - SS  (mod 128), u = (z - 1) / 2 mod 32,
the 64 values of omega mod 128 are one full parity class, so exactly 26 lie in S7 (13 odd + 13 even per interval)."""
import random
S7 = set(range(0x25, 0x3F)) | set(range(0x45, 0x5F))
assert len(S7) == 52 and sum(w & 1 for w in S7) == 26
rng = random.Random(7)
bad = 0
cases = [tuple(rng.randrange(128) for _ in range(6)) + (rng.randrange(2), rng.randrange(2)) for _ in range(200000)]
cases += [(0,) * 6 + (0, 0), (127,) * 6 + (1, 1)]
for b, c, d, A, L, SS, br8, br16 in cases:
    oms = []
    for v in (0, 1):                  # e1 bit 7
        for u in range(32):           # e1 bits 2..6
            e1 = 3 + 4 * u + 128 * v
            y = (e1 - 0x81) & 255     # low byte of Y3 = 0x81
            z = y >> 1 & 127          # y[1..7]
            P = ((((((z ^ b) - c - br8) & 127) ^ d) - A - br16 & 127) ^ L) - SS & 127
            oms.append((e1 + P) & 127)
    s = set(oms)
    bad += len(s) != 64 or len({w & 1 for w in s}) != 1 or len(s & S7) != 26
print("cases", len(cases), "bad", bad)
