"""Sampling rates for the xor/additive compatibility events in the {m2,m3,m4,m6} local collision.

compat(delta, D): there is a z with z ^ (z + delta) = D  (mod 2^32).  Exact word test:
  carry vector c = D ^ delta; need c_0 = 0 and, at every bit i < 31 with delta_i == c_i,
  c_{i+1} == delta_i (the carry is forced there; elsewhere z_i sets it freely).
Checked against brute force on 8-bit words first.

Rates printed (COMPUTED, numpy, seeded):
  R1  random delta, random D                                 (reference)
  R2  D3 second condition: D = ROR(ROR(a^(a-d),24) ^ (u^(u+d)), 16) against delta = d
  R3  C0 condition: D = xor-difference of a random word pair  against a random delta
python -B compat_rates.py [n]
"""
import sys

import numpy as np

M32 = np.uint64(0xFFFFFFFF)


def compat(delta, D, bits=32):
    mask = (1 << bits) - 1
    c = (D ^ delta) & mask
    ok0 = (c & 1) == 0
    eq = ~(delta ^ c) & mask
    bad = (((c >> 1) ^ delta) & eq) & ((1 << (bits - 1)) - 1)
    return ok0 & (bad == 0)


def brute_check():
    bits = 8
    mask = 255
    agree = 0
    for delta in range(256):
        reach = set(((z ^ ((z + delta) & mask)) for z in range(256)))
        for D in range(256):
            if (D in reach) == bool(compat(delta, D, bits)):
                agree += 1
    return agree


def ror(x, n):
    return ((x >> np.uint64(n)) | (x << np.uint64(32 - n))) & M32


def main():
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 4_000_000
    print(f"8-bit brute-force agreement: {brute_check()}/65536")
    rng = np.random.default_rng(20261010)
    r = lambda: rng.integers(0, 1 << 32, size=n, dtype=np.uint64)
    delta = r()
    delta[delta == 0] = 1
    D = r()
    p1 = compat(delta, D).mean()
    a, u = r(), r()
    neg = (np.uint64(1 << 32) - delta) & M32
    ds14 = ror(a ^ ((a + neg) & M32), 24)
    q = u ^ ((u + delta) & M32)
    D3 = ror(ds14 ^ q, 16)
    p2 = compat(delta, D3).mean()
    x, xp = r(), r()
    p3 = compat(delta, x ^ xp).mean()
    for name, p in (("R1 random", p1), ("R2 D3 second condition", p2), ("R3 C0 condition", p3)):
        print(f"{name:26s} rate {p:.3e} = 2^{np.log2(p):.2f}  (n = {n})")


if __name__ == "__main__":
    main()
