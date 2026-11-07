"""lane_check.py - the walk lane's reduced formulas against the full shipped lines (research only).

Checks, on random (context, member, step) of the walk:
  L1  X0 from the listed omega: X0 = ROL((omega - A) XOR S15', 16), and the lane form X0_lo = ((omega>>16) - A_hi - c)
      mod 2^16 XOR S15'_hi with c the carry of the block's low half, X0_hi = the block's
  L2  the 13-line Y9 path from X0 with per-context constants (w3 = X0 + c3, C1.a1 = X0 + c4 + X5) equals Y9, Y1, X10 of
      the 77 lines, and C2.c1 = X10 + C2.d1, C2.b1 = ROR(X6 XOR C2.c1, 12) with C2.d1, X6 fixed per context
  L3  the lists: per live state of test (2)'s automaton after 16 bits, the number of distinct masks among its passing
      high halves (the (state, mask2) lists of the block row)
"""
import random
import sys
import time

import walk_model as W

F = W.F
M = W.M
ror, rol = W.ror, W.rol


def main():
    rng = random.Random(int(sys.argv[1]) if len(sys.argv) > 1 else 7)
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 3000
    t0 = time.time()
    bad1 = bad2 = 0
    for _ in range(n):
        ow = [rng.getrandbits(32) for _ in range(7)]
        e1, y = F.member(rng.getrandbits(19))
        v0 = W.co_walk(ow, y, 0)
        r = rol(v0["K1_d1"], 16)
        r19, hi13 = r & 0x7FFFF, r & ~0x7FFFF & M
        Cc = (v0["C0_a1"] - v0["X4"] + F.IV[1] + F.IV[5]) & M
        xtop = (Cc - hi13) & M
        j0 = ((xtop & 0xFFFF) + 1) & 0xFFFF
        j = j0 + rng.randrange(7 * 65536)
        thi = j ^ r19
        v = W.co_walk(ow, y, thi)
        # per-context constants (from the thi = 0 evaluation only)
        S15p = v0["S15"] ^ ror(F.X15, 8)
        A = (v0["e1"] - v0["S0"] - v0["S5"]) & M
        c3 = (v0["S1"] - v0["K1_b1"] - Cc) & M
        c4 = (v0["X1"] + c3) & M
        # L1
        om = v["omega"]
        x0 = rol(((om - A) & M) ^ S15p, 16)
        xh = ((xtop - j) & M) >> 16
        c = ((A & 0xFFFF) + ((xh ^ S15p) & 0xFFFF)) >> 16
        x0lo = (((om >> 16) - (A >> 16) - c) & 0xFFFF) ^ (S15p >> 16)
        bad1 += x0 != v["X0"] or (xh << 16 | x0lo) != v["X0"]
        # L2
        X0 = x0
        D0d1 = X0 ^ rol(F.X15, 8)
        D0c1 = (v0["S10"] + D0d1) & M
        D0b1 = ror(v0["S5"] ^ D0c1, 12)
        X10 = (D0c1 + F.X15) & M
        X5 = ror(D0b1 ^ X10, 7)
        C1a1 = (X0 + c4 + X5) & M
        C1d1 = ror(v0["X13"] ^ C1a1, 16)
        C1c1 = (v0["X9"] + C1d1) & M
        C1b1 = ror(X5 ^ C1c1, 12)
        Y1 = (C1a1 + C1b1 + v0["w10"]) & M
        Y13 = ror(C1d1 ^ Y1, 8)
        Y9 = (C1c1 + Y13) & M
        C2c1 = (X10 + v0["C2_d1"]) & M
        C2b1 = ror(v0["X6"] ^ C2c1, 12)
        bad2 += (Y9, Y1, X10, C2c1, C2b1, v0["C2_a1"], v0["C2_d1"]) != (v["Y9"], v["Y1"], v["X10"], v["C2_c1"], v["C2_b1"], v["C2_a1"], v["C2_d1"])
    print("L1 X0 from the listed omega (both forms): %d mismatches of %d" % (bad1, n))
    print("L2 13-line Y9 path and the shortcut's C2 words from per-context constants: %d mismatches of %d" % (bad2, n))
    # L3
    f = F.F2
    st16 = {f[f[lo & 255] + (lo >> 8)] for lo in range(1 << 16)}
    for s in sorted(st16):
        masks = {}
        for b2 in range(256):
            s3 = f[s + b2]
            for b3 in range(256):
                m = f[s3 + b3]
                if m:
                    masks[m] = masks.get(m, 0) + 1
        if masks:
            print("L3 state %d: %d passing high halves in %d (state, mask2) lists; partial words per live block <= %d"
                  % (s, sum(masks.values()), len(masks), len(masks)))
    print("seconds %.1f" % (time.time() - t0))


if __name__ == "__main__":
    main()
