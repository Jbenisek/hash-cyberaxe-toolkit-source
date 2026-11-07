"""S9: per-representative ledger of pkg10 (proof.md section 8) with the representative path bitsliced.

Inputs: COMPUTED counts from s9_bitslice.py (per 256 representatives) and the filed rows. Score as in proof.md 8:
T = c * N * (1 + 2^-7) / 430 + 2^81, c = total / 41.02 rounded up to 2 decimals, time_log2 rounded up to 2 dec.
"""
import math

N = 759300 * 2 ** 81
TE = 41.02
FILED = 67.585260
REP_A, REP_GATE, REP_S2, DISPATCH = 6.858398, 1.428833, 0.602789, 2.323623
OVERHEAD = 4 + 3 + 2          # loop (3 ops + 1 load), program variant for e27..e29, rule-A test + branch
MASKS_PER_BATCH = 3 * 32 * 4 / 64   # 32 broadcast masks for 3 X2-constants per X2 value, over 64 batches


def score(total):
    c = math.ceil(total / TE * 100 - 1e-9) / 100
    t = c * N * (1 + 2 ** -7) / 430 + 2 ** 81
    return c, math.log2(t), math.ceil(math.log2(t) * 100) / 100


def row(name, stage_a_units, s2, disp_factor, masks=0.0):
    a = (stage_a_units + OVERHEAD + masks) / 256
    total = FILED - REP_A - REP_GATE - REP_S2 + a + s2 + DISPATCH * (disp_factor - 1)
    c, raw, rounded = score(total)
    print("%-58s A/rep %5.2f  total %6.2f  save %5.3f bit  c %.2f  log2T %.4f  claim %.2f"
          % (name, a, total, math.log2(FILED / total), c, raw, rounded))


print("filed:", score(FILED))
# claim's own arithmetic: 3.5 per trial replaces 6.858 only
total = FILED - REP_A + 3.5
print("claim arithmetic (3.5/trial replaces stage A row only): total %.2f save %.3f bit" % (total, math.log2(FILED / total)),
      score(total))
# COMPUTED counts per 256 representatives (s9_bitslice.py count, seeds 0-2; spec counts averaged)
SPEC_OPS, MASK_OPS = 653, 996
cases = [
    ("spec consts, unlimited registers (claim-like)", SPEC_OPS + 64 + 1, 0.0),
    ("spec consts, 14 working registers (Belady)", SPEC_OPS + 268 + 139, 0.0),
    ("mask consts, unlimited registers (traffic lower bound)", MASK_OPS + 223 + 1, MASKS_PER_BATCH),
    ("mask consts, 14 working registers (Belady) = literal", MASK_OPS + 457 + 176, MASKS_PER_BATCH),
]
for name, units, m in cases:
    for s2, d, tag in ((0.40, 1.0, "s2 gathered, dispatch same"), (0.99, 1.2, "s2 repacked, dispatch +20%")):
        row(name + " | " + tag, units, s2, d, m)
