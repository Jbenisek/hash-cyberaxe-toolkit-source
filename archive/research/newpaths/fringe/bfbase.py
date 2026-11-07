"""Brute-force baseline for the SAT test: random messages at w=6 until out0,2,5,7 equal the target of
cnfgen.py outhalfA seed 1 (the instance kissat could not solve in 300 s).  Expected one hit per 2^(4w) = 2^24.
Usage: python bfbase.py [log2 tries=26]
"""
import sys
import time

import numpy as np

sys.dont_write_bytecode = True
import random  # noqa: E402
import toyb3 as T  # noqa: E402
from quicktests import vtrace  # noqa: E402

w = 6
rng = random.Random(1)
m0 = [rng.getrandbits(w) for _ in range(16)]       # same draw as cnfgen.generate(seed=1)
tgt = T.trace(m0, w)["out"]
n = int(sys.argv[1]) if len(sys.argv) > 1 else 26
gen = np.random.default_rng(11)
hits, t0 = 0, time.time()
chunk = 1 << 20
for _ in range((1 << n) // chunk):
    M = gen.integers(0, 1 << w, (chunk, 16), dtype=np.uint64)
    _, Z = vtrace(M, w)
    ok = np.ones(chunk, dtype=bool)
    for i in (0, 2, 5, 7):
        ok &= (Z[i] ^ Z[i + 8]) == np.uint64(tgt[i])
    for row in M[ok]:
        msg = [int(x) for x in row]
        assert all(T.compress(msg, w)[i] == tgt[i] for i in (0, 2, 5, 7))
        hits += 1
print(f"w=6 outhalfA seed 1: {hits} verified solutions in 2^{n} random messages "
      f"(expected {2 ** (n - 4 * w):.1f}), {time.time() - t0:.1f} s numpy  [COMPUTED]")
