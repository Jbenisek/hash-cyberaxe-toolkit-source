"""'Affinity maturation' test: is there a gradient on the residual of the filed 55/63 family?

For random trials (eight basis words of fam55.build, y in the sub-class), flip one bit of one basis word (for y:
one of the 17 free sub-class bits of e1, so y stays in the sub-class), rebuild the pair, and measure the Hamming
distance between the old and the new 128-bit residual R = halfB(A) xor halfB(B).  A hill climb (or any local
search) needs moves with small distance.  Random-function baseline: Binomial(128, 1/2), mean 64, sd 5.7.
"""
import random
import sys

import fam55 as F

NAMES = ["C0.c1", "C0.d1", "D3.d1", "S15", "S9", "w5", "X2", "y"]


def resid(args):
    dA, dB = F.residual(F.build(*args))
    r = 0
    for i in (1, 3, 4, 6):
        r = (r << 32) | (dA[i] ^ dB[i])
    return r


def main(ntr=40, seed=1):
    rng = random.Random(seed)
    stats = {}
    allhd = []
    for t in range(ntr):
        base = [rng.randrange(1 << 32) for _ in range(7)]
        k = rng.randrange(1 << 17)
        r0 = resid(base + [F.class_member_sub(k)])
        for wi in range(8):
            for j in range(32 if wi < 7 else 17):
                if wi < 7:
                    a = list(base); a[wi] ^= 1 << j
                    a = a + [F.class_member_sub(k)]
                else:
                    a = base + [F.class_member_sub(k ^ (1 << j))]
                hd = bin(r0 ^ resid(a)).count("1")
                stats.setdefault((NAMES[wi], j), []).append(hd)
                allhd.append(hd)
    allhd.sort()
    n = len(allhd)
    print(f"trials {ntr}, single-bit flips {n}: residual Hamming distance mean {sum(allhd) / n:.2f}, "
          f"min {allhd[0]}, 1st percentile {allhd[n // 100]}, 10th {allhd[n // 10]}, median {allhd[n // 2]}")
    rows = sorted(((sum(v) / len(v), min(v), k) for k, v in stats.items()))
    print("lowest mean distance per (word, bit)  [y bits are indices of the 17 free sub-class bits]:")
    for m, mn, k in rows[:12]:
        print(f"  {k[0]:6s} bit {k[1]:2d}: mean {m:6.2f}  min {mn}")
    print(f"flips with distance <= 16: {sum(1 for h in allhd if h <= 16)} of {n}; "
          f"<= 32: {sum(1 for h in allhd if h <= 32)}")


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else 40)
