"""Does the chaining value change how often the outer-word cube can be realized?

u = Y12 = (ROL(y, 7) XOR b) - c with b = C0.b1 = ROR(X4 XOR Cc1, 12), c = Cc1 (twoblock.build, Step Y).
The cube {22, 23} (24..26 follow) is usable in an outer step only if those bits of u are constant over ALL
2^17 sub-class members y.  The CV enters b only through X4 (via S14 <- K2.b1 <- cv6).  This script draws random
outer steps (Cc1, Cd1, D3d1, S15, S9, w5), computes (b, c) with the real construction for a given CV, and checks
constancy of u bits 22, 23 over all 2^17 members by brute force.  Reference rate (cloud REPORT.md section 6):
0.590 % (2^24 outer pairs, C15).
usage: python cube_realize.py OUTER_STEPS SEED
"""
import struct
import sys

import numpy as np

import twoblock as tb
from verifier.blake3 import _compress

M = 0xFFFFFFFF


def outer_bc(cv, flags, rng):
    Cc1, Cd1, D3d1, S15, S9, w5 = (int(rng.integers(0, 1 << 32)) for _ in range(6))
    K = (cv[2] + cv[6]) & M
    X3 = (tb.T - tb.X7 + K) & M
    k2d1 = tb.ror(55 ^ tb.Q, 16); k2c1 = (tb.IV[2] + k2d1) & M; k2b1 = tb.ror(cv[6] ^ k2c1, 12)
    S2 = (tb.Q + k2b1 + w5) & M; S14 = tb.ror(k2d1 ^ S2, 8)
    D3a1 = tb.rol(D3d1, 16) ^ S14; D3c1 = (S9 + D3d1) & M
    D3b1 = (X3 - D3a1) & M
    X14 = tb.ror(D3d1 ^ X3, 8); X9 = (D3c1 + X14) & M; X4 = tb.ror(D3b1 ^ X9, 7)
    b = tb.ror(X4 ^ Cc1, 12)
    return b, Cc1


def all_members():
    free = [i for i in range(32) if not tb.SUB_AND >> i & 1]
    k = np.arange(1 << 17, dtype=np.uint64)
    e1 = np.full(1 << 17, tb.CLASS_VAL, dtype=np.uint64)
    for j, p in enumerate(free):
        e1 |= ((k >> np.uint64(j)) & np.uint64(1)) << np.uint64(p)
    y = ((e1 - np.uint64(tb.Y3A)) & np.uint64(M)).astype(np.uint32)
    return ((y << np.uint32(7)) | (y >> np.uint32(25))).astype(np.uint32)


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    seed = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    rly = all_members()
    mask = np.uint32((1 << 22) | (1 << 23))
    rng0 = np.random.default_rng(seed + 99)
    b0 = bytes(int(x) for x in rng0.integers(0, 256, size=64))
    cvs = [("IV/11", tb.IV, 11), ("chained/10", _compress(tb.IV, struct.unpack("<16I", b0), 0, 64, 1, 2)[:8], 10)]
    for name, cv, flags in cvs:
        rng = np.random.default_rng(seed)
        hits = 0
        hits_all5 = 0
        for _ in range(n):
            b, c = outer_bc(cv, flags, rng)
            u = (rly ^ np.uint32(b)) - np.uint32(c)
            v = u & mask
            if np.all(v == v[0]):
                hits += 1
                m5 = np.uint32(0x1f << 22)
                w = u & m5
                hits_all5 += int(np.all(w == w[0]))
        p = hits / n
        print(f"{name}: {n} outer steps, bits 22,23 constant over all 2^17 members: {hits} = {100 * p:.3f} % "
              f"(+- {100 * (p * (1 - p) / n) ** 0.5:.3f} %); of those with 22..26 all constant: {hits_all5}",
              flush=True)


if __name__ == "__main__":
    main()
