"""Literal contest-model cost of the HYPOTHETICAL 4-way separable split (4 sides x 2 words, 4 checks, n = 128).
1 unit = one 2-round compression; any other 32-bit word op = 1/430 unit.  Op counts per step are GUESSES (stated).
Step counts per clamp value are the ones measured in kv.py / kmath (COMPUTED at toy size)."""
from math import log2

U = 1 / 430                     # unit per word op
BUILD_OPS = 44                  # GUESS: side element = <= 12 derived words (closure of 2 guesses <= 14, ksplit R1) x 3 ops + 8 for check terms
HASH_OPS = 5                    # GUESS: one table insert or lookup (target subtraction on 2 words + hash/compare)
COMB_OPS = 4                    # GUESS: one join output = group op on 4 words
BDAY_OPS = 8                    # GUESS: insert + compare in the 128-bit birthday table
L = 2.0 ** 64                   # each list = all 2^64 values of a 2-word side (a = n/2 = 64)


def total(members, member_unit, build_unit):
    clamps = max(1.0, members / L)                          # one clamp value (t = 64) yields 2^64 members
    build = 4 * L * build_unit
    leaf_tables = 2 * L * HASH_OPS * U
    per_clamp = L * (2 * HASH_OPS + 2 * COMB_OPS + HASH_OPS + HASH_OPS + COMB_OPS) * U   # look L1,L3; out L12,L34; ins L34; look L12; out
    merge = (2.0 if clamps > 1 else 1.0) * per_clamp       # a started clamp value pays its level-1 lists in full
    mem = members * (member_unit + BDAY_OPS * U)
    return log2(build + leaf_tables + merge + mem), build, merge, mem


rows = [
    ("literal, 2^64.5 members (1 expected collision), member = 1 unit", 2 ** 64.5, 1.0, BUILD_OPS * U),
    ("literal, 2^64 members (0.5 expected collision, 39%)", 2 ** 64, 1.0, BUILD_OPS * U),
    ("literal, 2^64.5 members, member cascade as ~250 word ops", 2 ** 64.5, 250 * U, BUILD_OPS * U),
    ("over-count: every list element = 1 full unit, 2^64.5 members", 2 ** 64.5, 1.0, 1.0),
]
with open("units_results.txt", "w") as f:
    for name, m, mu, bu in rows:
        e, b, g, me = total(m, mu, bu)
        s = f"{name:66s} log2 total = {e:6.2f}   (build {log2(b):5.2f}, merge {log2(g):5.2f}, members {log2(me):5.2f})"
        print(s)
        f.write(s + "\n")
