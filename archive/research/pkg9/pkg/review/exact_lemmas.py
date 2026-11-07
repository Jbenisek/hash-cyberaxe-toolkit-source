#!/usr/bin/env python3
"""exact lens, pkg7 (draft): Fact P, Lemma L, Lemmas Q and Q2 over all 2^32 values of Y4, Lemma A enumerated.

    python -B exact_lemmas.py          everything (about three minutes, one process)
Typed from the text of Sections 2, 3, 6.1 and 6.3; nothing of the package's code is used.
"""
import os
import random
import sys

import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exact_blake3 as B3  # noqa: E402
from exact_check import (ALL, CLASS_MASK, CLASS_VAL, DELTA, ETA, FREE, IV, LB, M, NL, RULE, SUB_MASK, W4, W4P, W13,  # noqa: E402
                         WORD, X3, X7, X11, X15, Y3, Y3P, Y11, Y11P, bit, lemma_a_word, member, note, pack, lanes,
                         rep, rol, ror, rule_a, rule_on_z, v_word, FAIL)

U32 = np.uint32


def nror(x, r):
    return (x >> U32(r)) | (x << U32(32 - r))


def part_p():
    K = (IV[2] + IV[6]) & M
    note(K == 0x5BF2CD1D and (K + W4) & M == 0xF33A2355 and (((K + W4) & M) ^ 8) - K & M == W4P == 0x97475640
         and (W4 - W4P) & M == DELTA == 0xFFFFFFF8, "3.2: K, K + W4, W4', W4 - W4'")
    a = B3.g_values(X3, X7, X11, X15, W4, W13)
    b = B3.g_values(X3, X7, X11, X15, W4P, W13)
    want_a = (0x7FFFFFF8, 0x7AF83F3A, 0xBEFB9F3A, 0x01200183, 0x8127C181, 0xBBFBDFFE, 0x7AF77F38, 0x76F7AEFD)
    want_b = (0x80000000, 0x8500C0C5, 0xC90420C5, 0xFED77E78, 0x7EDF3E7E, 0xBBFBDFFE, 0x850000C3, 0x76F7AEFD)
    note(a == want_a and b == want_b, "Fact P: the two displayed executions of C3, all sixteen values")
    note((a[4], b[4], a[6], b[6]) == (Y3, Y3P, Y11, Y11P) and a[5] == b[5] and a[7] == b[7] and W13 >> 24 == 0,
         "Fact P: same d and b outputs; Y3, Y3', Y11, Y11'; top byte of W13 zero")
    rnd = random.Random(20261006)
    bad = 0
    for t in range(200000):
        w4, w5 = (rnd.getrandbits(32), rnd.getrandbits(32)) if t > 40 else ((0, M, W4, 8, M - 7)[t % 5], (0, M, 7)[t % 3])
        w4p = ((((K + w4) & M) ^ 8) - K) & M
        w5p = (w5 + w4 - w4p) & M
        bad += B3.g_values(IV[2], IV[6], IV[2], 55, w4, w5)[4:] != B3.g_values(IV[2], IV[6], IV[2], 63, w4p, w5p)[4:]
    note(bad == 0, "Lemma L: K2 with length 55 and (w4, w5) = K2 with length 63 and (w4', w5'), 200,000 pairs, wrong %d"
         % bad)


def part_q():
    dy3 = (Y3P - Y3) & M
    x = rol(ETA, 16)
    note(dy3 == 0xFDB77CFD and x == 0x03CF8303 and (dy3 + x) & M == 0x01870000 and 0x01870000 >> 1 == 0x00C38000
         and (~0x00C38000) & x == 0x030C0303 and 0x00C38000 & ~x == 0,
         "Lemma Q, the words of its proof: DY3, ROL(eta,16), DY3 + x, its half, the value on the mask")
    note(SUB_MASK == CLASS_MASK | 0x04200000 and CLASS_MASK & 0x04200000 == 0 and CLASS_VAL & 0x04200000 == 0
         and FREE == [2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 20, 27, 28, 29, 30, 31],
         "Lemma Q2: 07ef8303 = 03cf8303 OR 04200000 (bits 21 and 26); free positions 2-7, 10-14, 20, 27-31")
    n_class = n_sub = wrong_q = wrong_q2 = sub_outside = 0
    sub_members = []
    step = 1 << 24
    for lo in range(0, 1 << 32, step):
        y4 = np.arange(lo, lo + step, dtype=np.uint64).astype(U32)
        e1 = y4 + U32(Y3)
        e1p = y4 + U32(Y3P)
        eta = nror(e1 ^ e1p, 16)
        in_class = eta == U32(ETA)
        by_mask = (e1 & U32(CLASS_MASK)) == U32(CLASS_VAL)
        in_sub = (e1 & U32(SUB_MASK)) == U32(CLASS_VAL)
        by_bits = in_class & ((e1 & U32(0x04200000)) == 0)
        n_class += int(in_class.sum())
        n_sub += int(in_sub.sum())
        wrong_q += int((in_class != by_mask).sum())
        wrong_q2 += int((in_sub != by_bits).sum())
        sub_outside += int((in_sub & ~in_class).sum())
        sub_members.append(y4[in_sub].copy())
    note(wrong_q == 0 and n_class == 524288, "Lemma Q over all 2^32 values of Y4: eta = 830303cf exactly when the "
         "mask condition holds (wrong %d); members %d" % (wrong_q, n_class))
    note(wrong_q2 == 0 and n_sub == 131072 and sub_outside == 0, "Lemma Q2 over all 2^32 values: the sub-class is the "
         "class with bits 21 and 26 of e1 zero (wrong %d); members %d; outside the class %d" % (
             wrong_q2, n_sub, sub_outside))
    allsub = np.sort(np.concatenate(sub_members))
    mine = np.array([member(k) for k in range(131072)], dtype=U32)
    note(len(set(mine.tolist())) == 131072 and np.array_equal(np.sort(mine), allsub),
         "member number k, k = 0..131,071: 131,072 different words, the same set as the sub-class of the scan")
    return mine


def part_a(mine):
    # the eight conditions are independent
    hb = sorted({i for m, _ in RULE for i in range(32) if m >> i & 1})
    cnt = 0
    for p in range(1 << len(hb)):
        h = sum((p >> t & 1) << i for t, i in enumerate(hb))
        cnt += rule_a(h)
    note(len(hb) == 13 and cnt == 32, "rule A reads %d bits of h1 (%s); %d of the 2^13 patterns satisfy it: share 2^-8"
         % (len(hb), " ".join(map(str, hb)), cnt))
    zb = [2, 3, 4, 5, 8, 9, 16, 17, 24, 25, 26, 27, 30]
    rnd = random.Random(7)
    # (b), (c), (d) for EVERY member and every pattern of the 13 bits of z (other bits and guard bits random)
    e1 = (mine + U32(Y3)).astype(np.uint64)
    v = np.array([v_word(int(y)) for y in mine], dtype=np.uint64)
    rule_masks = [(np.uint64(m), val) for m, val in RULE]
    wrong_b = wrong_c = wrong_d = total = sat = 0
    for p in range(1 << 13):
        z = rnd.getrandbits(32)
        for t, i in enumerate(zb):
            z = z & ~(1 << i) | (p >> t & 1) << i
        guard = rnd.getrandbits(4)
        # rule A as written on h1 = ROR(ROR(z, 8) XOR e1, 16)   (Lemma A (a), checked on real messages elsewhere)
        h1 = (np.uint64(ror(z, 8)) ^ e1)
        h1 = ((h1 >> np.uint64(16)) | (h1 << np.uint64(16))) & np.uint64(M)
        ok = np.ones(len(e1), dtype=bool)
        for m, val in rule_masks:
            par = h1 & m
            par ^= par >> np.uint64(16)
            par ^= par >> np.uint64(8)
            par ^= par >> np.uint64(4)
            par ^= par >> np.uint64(2)
            par ^= par >> np.uint64(1)
            ok &= (par & np.uint64(1)) == np.uint64(val)
        # (b): the conditions on z, with e27, e28, e29 of the member
        e27, e28, e29 = (e1 >> np.uint64(27)) & np.uint64(1), (e1 >> np.uint64(28)) & np.uint64(1), (
            e1 >> np.uint64(29)) & np.uint64(1)
        zc = (bit(z, 24) == 0 and bit(z, 25) == 1 and bit(z, 8) == 1 and bit(z, 9) == 1 and bit(z, 26) ^ bit(z, 2) == 0)
        cb = np.full(len(e1), zc) & (np.uint64(bit(z, 27) ^ bit(z, 3)) == e27) & (
            np.uint64(bit(z, 27) ^ bit(z, 4) ^ bit(z, 16)) == e28) & (
            np.uint64(bit(z, 30) ^ bit(z, 5) ^ bit(z, 17)) == (np.uint64(1) ^ e29))
        # (c): the word y from one lane with filled guard bits, then (y XOR v) AND ALL = ALL
        Z = z | guard << 32
        s = (Z << 12) & 0x0003C000
        y = Z ^ s
        s = (s << 12) & ((1 << 36) - 1)
        y ^= s
        s = (y << 13) & 0x40010000
        y ^= s
        u = (np.uint64(y & M) ^ v) & np.uint64(ALL)
        cc = u == np.uint64(ALL)
        # (d): bit 32 of u + (2^32 - ALL), and the sum at most 2^32
        sm = u + np.uint64((1 << 32) - ALL)
        cd = ((sm >> np.uint64(32)) & np.uint64(1)) == np.uint64(1)
        wrong_b += int((ok != cb).sum())
        wrong_c += int((ok != cc).sum())
        wrong_d += int((ok != cd).sum()) + int((sm > np.uint64(1 << 32)).sum())
        total += len(e1)
        sat += int(ok.sum())
    note(wrong_b == 0, "Lemma A (b): all 131,072 members x all 8,192 patterns of the 13 bits of z = %d cases, wrong %d"
         % (total, wrong_b))
    note(wrong_c == 0, "Lemma A (c): (y XOR v) AND ALL = ALL exactly when rule A holds, the same cases, wrong %d"
         % wrong_c)
    note(wrong_d == 0, "Lemma A (d): bit 32 of u + (2^32 - ALL), sum at most 2^32, the same cases, wrong %d" % wrong_d)
    print("     cases in which rule A holds: %d of %d = 2^-8 times %.6f" % (sat, total, sat * 256 / total))
    # (c) in the packed word: every pattern of the 13 bits and of e27..e29 in every lane, neighbours and guards filled
    reps = {}
    for y4 in map(int, mine):
        reps.setdefault(((Y3 + y4) & M) >> 27 & 7, y4)
    wrong = cases = 0
    for p in range(1 << 16):
        zs, ys = [], []
        for lane in range(NL):
            q = (p + 9973 * lane) % (1 << 16) if lane else p
            z = rnd.getrandbits(36)
            for t, i in enumerate(zb):
                z = z & ~(1 << i) | (q >> t & 1) << i
            zs.append(z)
            ys.append(reps[q >> 13])
        Zw = pack(zs)
        yw = lemma_a_word(Zw)
        u = (yw ^ pack(v_word(y) for y in ys)) & rep(ALL)
        sm = u + rep((1 << 32) - ALL)
        for lane, w in enumerate(lanes(sm)):
            h1 = ror(ror(zs[lane] & M, 8) ^ ((Y3 + ys[lane]) & M), 16)
            wrong += (w >> 32 & 1) != rule_a(h1) or w > 1 << 32
            cases += 1
    note(wrong == 0, "Lemma A (c), (d) in the packed word, 36-bit lanes with filled guard bits and neighbours: "
         "%d lanes (2^16 patterns in each of 7 lanes), wrong %d" % (cases, wrong))
    # the bits of e1 that (b) uses as constants
    fixed = {i: bit(CLASS_VAL, i) for i in (0, 1, 8, 9, 16, 17, 18, 19, 22, 26)}
    note(all(SUB_MASK >> i & 1 for i in fixed) and fixed == {0: 1, 1: 1, 8: 1, 9: 1, 18: 1, 19: 1, 16: 0, 17: 0, 22: 0,
                                                             26: 0} and not CLASS_MASK >> 26 & 1,
         "Lemma A (b), proof: bits 0 1 8 9 18 19 of e1 are 1 and 16 17 22 26 are 0 in the sub-class; bit 26 is free in "
         "the class")


if __name__ == "__main__":
    part_p()
    members = part_q()
    part_a(members)
    print("FAILED: %d" % len(FAIL) if FAIL else "all checks of this part hold")
    sys.exit(1 if FAIL else 0)
