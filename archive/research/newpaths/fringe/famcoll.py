"""Partial-output birthday with structured families (toy w=8, output 8 words = 64 bits).
Family = all values of a few message words (others fixed at random).  Counts colliding pairs in out_A (out0,2,5,7),
out_B (out1,3,4,6) and the full output, and compares with the uniform expectation C(N,2)/2^bits.
A family whose count is far above expectation has a low-entropy output (Renyi-2) and would shorten a birthday.
Usage: python famcoll.py [nwords=2] [nfam=120] [w=8] [seed]
"""
import itertools
import random
import sys

import numpy as np

sys.dont_write_bytecode = True
from quicktests import vtrace  # noqa: E402


def pairs_equal(keys):
    """number of unordered pairs with equal key"""
    _, cnt = np.unique(keys, return_counts=True)
    return int((cnt * (cnt - 1) // 2).sum())


def main():
    k = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    nfam = int(sys.argv[2]) if len(sys.argv) > 2 else 120
    w = int(sys.argv[3]) if len(sys.argv) > 3 else 8
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 1
    rng = random.Random(seed)
    combos = list(itertools.combinations(range(16), k))
    if len(combos) > nfam:
        combos = rng.sample(combos, nfam)
    N = 1 << (w * k)
    exp_half = N * (N - 1) / 2 / 2.0 ** (4 * w)
    exp_full = N * (N - 1) / 2 / 2.0 ** (8 * w)
    tot = [0, 0, 0]
    worst = []
    for words in combos:
        base = [rng.getrandbits(w) for _ in range(16)]
        M = np.tile(np.array(base, dtype=np.uint64), (N, 1))
        idx = np.arange(N, dtype=np.uint64)
        for t, wd in enumerate(words):
            M[:, wd] = (idx >> np.uint64(w * t)) & np.uint64((1 << w) - 1)
        _, Z = vtrace(M, w)
        o = [Z[i] ^ Z[i + 8] for i in range(8)]
        sh = np.uint64(w)
        kA = ((o[0] << sh | o[2]) << sh | o[5]) << sh | o[7]
        kB = ((o[1] << sh | o[3]) << sh | o[4]) << sh | o[6]
        cA, cB = pairs_equal(kA), pairs_equal(kB)
        cF = pairs_equal(np.stack([kA, kB], axis=1).view([("a", np.uint64), ("b", np.uint64)]).ravel())
        tot[0] += cA
        tot[1] += cB
        tot[2] += cF
        worst.append((max(cA, cB) / exp_half, words, cA, cB, cF))
    worst.sort(reverse=True)
    n = len(combos)
    print(f"w={w}, families of {k} free words (N=2^{w * k} each), {n} families:")
    print(f"  out_A colliding pairs: {tot[0]} (uniform expectation {n * exp_half:.1f})")
    print(f"  out_B colliding pairs: {tot[1]} (uniform expectation {n * exp_half:.1f})")
    print(f"  full collisions: {tot[2]} (uniform expectation {n * exp_full:.3g})")
    print("  top 5 families by half-collision ratio (ratio, words, cA, cB, full):")
    for r in worst[:5]:
        print(f"    {r[0]:.2f} {r[1]} {r[2]} {r[3]} {r[4]}")


if __name__ == "__main__":
    main()
