#!/usr/bin/env python3
"""construction_impl.py -- independent reviewer, lens "construction" (pkg6 draft).

Steps S1, T, S2, S3, the compression of Section 1, Fact P, Lemmas L, Q, T, E, N, A are typed here from the TEXT of
blake3-r2/proof.md (Sections 1 to 6) alone. The organizer's reference hash (hash-smash/verifier/blake3.py) supplies
every digest and, through its own _g, the state after round 0. The package's program is imported only in the last
part, for a word-by-word comparison with what the text gives.

Usage: python -B construction_impl.py [contexts=4000] [members=25] [seed=20261006]
Writes review/construction_impl_out.txt; prints a short summary.
"""
import os
import random
import struct
import sys
import time

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
WORKSPACE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(WORKSPACE, "hash-smash"))
from verifier.blake3 import blake3 as org_blake3, _g as org_g, IV as ORG_IV  # noqa: E402

M = 0xFFFFFFFF
IV = (0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
CALLS = ((0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))
NAMES = (("K0", "K1", "K2", "K3", "D0", "D1", "D2", "D3"), ("C0", "C1", "C2", "C3", "E0", "E1", "E2", "E3"))
# Section 3.2
X3, X7, X11, X15, W4, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006
K = (IV[2] + IV[6]) & M
W4P = ((((K + W4) & M) ^ 8) - K) & M
# Section 6.1
ETA, CMASK, CVALUE = 0x830303cf, 0x03cf8303, 0x030c0303
Y3, Y3P, Y11, Y11P = 0x8127c181, 0x7edf3e7e, 0x7af77f38, 0x850000c3
DY3 = (Y3P - Y3) & M
FREE = [i for i in range(32) if not CMASK >> i & 1]

OUT = []
RES = {}


def chk(name, ok):
    r = RES.setdefault(name, [0, 0])
    r[1] += 1
    if ok:
        r[0] += 1
    return ok


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & M


def g8(A, B, C, D, x, y):
    """The eight assignments of Section 2, in the order a1, d1, c1, b1, a2, d2, c2, b2."""
    a1 = (A + B + x) & M
    d1 = ror(D ^ a1, 16)
    c1 = (C + d1) & M
    b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M
    d2 = ror(d1 ^ a2, 8)
    c2 = (c1 + d2) & M
    b2 = ror(b1 ^ c2, 7)
    return (a1, d1, c1, b1, a2, d2, c2, b2)


def trace(w, n):
    """Section 1, with every call's inputs, words and eight values, and the states S, X, Y, Z."""
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    s = list(w)
    calls, st = {}, {}
    for r in range(2):
        for i, (a, b, c, d) in enumerate(CALLS):
            inp = (v[a], v[b], v[c], v[d])
            vals = g8(v[a], v[b], v[c], v[d], s[2 * i], s[2 * i + 1])
            v[a], v[d], v[c], v[b] = vals[4], vals[5], vals[6], vals[7]
            calls[NAMES[r][i]] = (inp, (s[2 * i], s[2 * i + 1]), vals)
            if i == 3:
                st["S" if r == 0 else "Y"] = tuple(v)
        if r == 0:
            st["X"] = tuple(v)
        s = [s[PERM[i]] for i in range(16)]
    st["Z"] = tuple(v)
    o = [v[i] ^ v[i + 8] for i in range(8)]
    return o, st, calls


def org_round0(words, n):
    v = list(ORG_IV) + list(ORG_IV[:4]) + [0, 0, n, 11]
    for i, (a, b, c, d) in enumerate(CALLS):
        org_g(v, a, b, c, d, words[2 * i], words[2 * i + 1])
    return tuple(v)


class NS(dict):
    __getattr__ = dict.__getitem__


def step_S1(vc, vd, S11, S4, X13, X14, w0):
    # K0, forwards from w0 and backwards from S4
    ka = (IV[0] + IV[4] + w0) & M; kd = ror(ka, 16); kc = (IV[0] + kd) & M
    kb = ror(IV[4] ^ kc, 12)
    S8 = rol(S4, 7) ^ kb; S12 = (S8 - kc) & M; S0 = rol(S12, 8) ^ kd
    w1 = (S0 - ka - kb) & M
    # D2, backwards from its outputs X7, X8, X13
    X8 = (vc - vd) & M; tc = (X8 - X13) & M; td = (tc - S8) & M; tb = rol(X7, 7) ^ X8
    S7 = rol(tb, 12) ^ tc; X2 = rol(X13, 8) ^ td
    ta = (X2 - tb - W13) & M; S13 = rol(td, 16) ^ ta
    # K3, backwards from its outputs S7, S11
    mb = rol(S7, 7) ^ S11; mc = rol(mb, 12) ^ IV[7]; md = (mc - IV[3]) & M
    S15 = (S11 - mc) & M; S3 = rol(S15, 8) ^ md; ma = rol(md, 16) ^ 11
    w6 = (ma - IV[3] - IV[7]) & M; w7 = (S3 - ma - mb) & M
    # K2, its first four values
    p = (K + W4) & M; q = ror(p ^ 55, 16); r = (IV[2] + q) & M
    u = ror(IV[6] ^ r, 12)
    # D3 with w14 = w15 = 0, the lines that do not read X14
    ea = (S3 + S4) & M; eb = (X3 - ea) & M; ec = rol(eb, 12) ^ S4
    # D3, the lines that read X14
    ed = rol(X14, 8) ^ X3; S9 = (ec - ed) & M; S14 = rol(ed, 16) ^ ea
    X9 = (ec + X14) & M; X4 = ror(eb ^ X9, 7)
    # K2, rest
    S10 = (r + S14) & M; S6 = ror(u ^ S10, 7); S2 = rol(S14, 8) ^ q
    w5 = (S2 - p - u) & M
    # D2, its first word
    w12 = (ta - S2 - S7) & M
    # K1, backwards from its outputs S9, S13
    nc = (S9 - S13) & M; nd = (nc - IV[1]) & M; na = rol(nd, 16)
    nb = ror(IV[5] ^ nc, 12); S1 = rol(S13, 8) ^ nd
    S5 = ror(nb ^ S9, 7); w2 = (na - IV[1] - IV[5]) & M; w3 = (S1 - na - nb) & M
    # C0, its fourth value
    vb = ror(X4 ^ vc, 12)
    return NS(locals())


def step_T(c, y):
    vb, vc, vd, w6, w2, X4 = c.vb, c.vc, c.vd, c.w6, c.w2, c.X4
    S0, S1, S5, S6, S10, S11, S12, S15 = c.S0, c.S1, c.S5, c.S6, c.S10, c.S11, c.S12, c.S15
    # C0, backwards from its b output y
    Y8 = rol(y, 7) ^ vb; Y12 = (Y8 - vc) & M; Y0 = rol(Y12, 8) ^ vd
    va = (Y0 - vb - w6) & M; X0 = (va - X4 - w2) & M; X12 = rol(vd, 16) ^ va
    # D0, backwards from its outputs X0, X15
    fd = rol(X15, 8) ^ X0; fc = (S10 + fd) & M; X10 = (fc + X15) & M
    fb = ror(S5 ^ fc, 12); X5 = ror(fb ^ X10, 7)
    fa = rol(fd, 16) ^ S15; w8 = (fa - S0 - S5) & M; w9 = (X0 - fa - fb) & M
    # D1, backwards from its outputs X11, X12
    gc = (X11 - X12) & M; gb = ror(S6 ^ gc, 12); X6 = ror(gb ^ X11, 7)
    gd = (gc - S11) & M; X1 = rol(X12, 8) ^ gd
    ga = rol(gd, 16) ^ S12; w10 = (ga - S1 - S6) & M; w11 = (X1 - ga - gb) & M
    return NS(locals())


def member(k):
    """Member number k (text after Lemma Q): the bits of k at the free positions of e1, increasing position."""
    e1 = CVALUE
    for j, pos in enumerate(FREE):
        e1 |= (k >> j & 1) << pos
    return (e1 - Y3) & M


def in_class_def(y4):
    e1 = (Y3 + y4) & M
    return ror(e1 ^ ((e1 + DY3) & M), 16) == ETA


def in_class_q(y4):
    return ((Y3 + y4) & CMASK) == CVALUE


def rule_a_h1(h1):
    return (h1 & 1) == 0 and (h1 >> 16 & 1) == 0 and (h1 >> 17 & 1) == 0 and (h1 >> 1 & 1) == 1 \
        and (h1 >> 2 & 1) != (h1 >> 3 & 1)


def rule_a_z(z):
    return (z >> 24 & 1) == 0 and (z >> 25 & 1) == 1 and (z >> 8 & 1) == 1 and (z >> 9 & 1) == 1 \
        and (z >> 26 & 1) != (z >> 27 & 1)


def rule_a_word(z):
    S, ALL, V = 0x04000000, 0x07000300, 0x06000300
    return ((z ^ ((z >> 1) & S)) & ALL) ^ V


STATS = {"class trials": 0, "rule A passes": 0, "n zero": 0, "early zero": 0, "first failure": None}


def check_trial(c, ctx, y):
    t = step_T(c, y)
    w = [ctx[6], c.w1, c.w2, c.w3, W4, c.w5, c.w6, c.w7, t.w8, t.w9, t.w10, t.w11, c.w12, W13, 0, 0]
    wb = list(w)
    wb[4] = W4P
    wb[5] = (w[5] + W4 - W4P) & M                      # step S2
    A = struct.pack("<16I", *w)[:55]                    # step S3
    B = struct.pack("<16I", *wb)[:63]
    ok = True
    blkA = struct.unpack("<16I", A + bytes(64 - len(A)))
    blkB = struct.unpack("<16I", B + bytes(64 - len(B)))
    ok &= chk("lengths 55 and 63; B ends in eight zero bytes", len(A) == 55 and len(B) == 63 and B[55:] == bytes(8))
    ok &= chk("zero-filled block of A is the 16 words of S1+T; of B the same with w4', w5'",
              list(blkA) == w and list(blkB) == wb)
    ok &= chk("w14 = w15 = 0 and top byte of w13 zero in both blocks",
              blkA[14] == blkA[15] == blkB[14] == blkB[15] == 0 and blkA[13] >> 24 == 0 and blkB[13] >> 24 == 0)
    ok &= chk("A and B share every word except w4, w5 (and those two differ)",
              all((blkA[i] == blkB[i]) == (i not in (4, 5)) for i in range(16)))
    ok &= chk("w4 = W4, w4' = W4', w5' = w5 - 8, w13 = W13",
              blkA[4] == W4 and blkB[4] == 0x97475640 and blkB[5] == (blkA[5] - 8) & M and blkA[13] == W13)
    # round 0 with the organizer's _g
    xa, xb = org_round0(blkA, 55), org_round0(blkB, 63)
    ok &= chk("states after round 0 equal for A (n=55) and B (n=63), organizer _g", xa == xb)
    ok &= chk("pin in place: X3, X7, X11, X15", (xa[3], xa[7], xa[11], xa[15]) == (X3, X7, X11, X15))
    oa, sa, ca = trace(blkA, 55)
    ob, sb, cb = trace(blkB, 63)
    da, db = org_blake3(A, 2), org_blake3(B, 2)
    ok &= chk("own compression (Section 1) = organizer blake3(.,2) for A and B",
              struct.pack("<8I", *oa) == da and struct.pack("<8I", *ob) == db and sa["X"] == xa and sb["X"] == xb)
    wa_, wb_ = struct.unpack("<8I", da), struct.unpack("<8I", db)
    dd = [p ^ q_ for p, q_ in zip(wa_, wb_)]
    ok &= chk("organizer digests agree on words 0, 2, 5, 7", dd[0] == dd[2] == dd[5] == dd[7] == 0)
    # Lemma S, F, Y: every call with its inputs and its eight values
    S = (c.S0, c.S1, c.S2, c.S3, c.S4, c.S5, c.S6, c.S7, c.S8, c.S9, c.S10, c.S11, c.S12, c.S13, c.S14, c.S15)
    X = (t.X0, t.X1, c.X2, X3, c.X4, t.X5, t.X6, X7, c.X8, c.X9, t.X10, X11, t.X12, ctx[4], ctx[5], X15)
    ok &= chk("state after the column step = S0..S15 of step S1", sa["S"] == S)
    ok &= chk("state after round 0 = X0..X15 of steps S1 and T", sa["X"] == X)
    exp = {
        "K0": ((IV[0], IV[4], IV[0], 0), (w[0], w[1]), (c.ka, c.kd, c.kc, c.kb, c.S0, c.S12, c.S8, c.S4)),
        "K1": ((IV[1], IV[5], IV[1], 0), (w[2], w[3]), (c.na, c.nd, c.nc, c.nb, c.S1, c.S13, c.S9, c.S5)),
        "K2": ((IV[2], IV[6], IV[2], 55), (W4, w[5]), (c.p, c.q, c.r, c.u, c.S2, c.S14, c.S10, c.S6)),
        "K3": ((IV[3], IV[7], IV[3], 11), (w[6], w[7]), (c.ma, c.md, c.mc, c.mb, c.S3, c.S15, c.S11, c.S7)),
        "D2": ((c.S2, c.S7, c.S8, c.S13), (w[12], W13), (c.ta, c.td, c.tc, c.tb, c.X2, ctx[4], c.X8, X7)),
        "D3": ((c.S3, c.S4, c.S9, c.S14), (0, 0), (c.ea, c.ed, c.ec, c.eb, X3, ctx[5], c.X9, c.X4)),
    }
    ok &= chk("Lemma S: K0, K1, K2, K3, D2, D3 (inputs, words, eight values each)",
              all(ca[k_] == v_ for k_, v_ in exp.items()))
    expf = {
        "D0": ((c.S0, c.S5, c.S10, c.S15), (w[8], w[9]), (t.fa, t.fd, t.fc, t.fb, t.X0, X15, t.X10, t.X5)),
        "D1": ((c.S1, c.S6, c.S11, c.S12), (w[10], w[11]), (t.ga, t.gd, t.gc, t.gb, t.X1, t.X12, X11, t.X6)),
    }
    ok &= chk("Lemma F: D0, D1 (inputs, words, eight values each)", all(ca[k_] == v_ for k_, v_ in expf.items()))
    expy = ((t.X0, c.X4, c.X8, t.X12), (w[2], w[6]), (t.va, c.vd, c.vc, c.vb, t.Y0, t.Y12, t.Y8, y))
    ok &= chk("Lemma Y: C0 in A and in B (inputs, words, eight values)", ca["C0"] == expy and cb["C0"] == expy)
    ya, yb = sa["Y"], sb["Y"]
    ok &= chk("Y4 = y in A and in B", ya[4] == y and yb[4] == y)
    ok &= chk("Fact P in the trial: Y3, Y3', Y11, Y11', and Y equal elsewhere",
              (ya[3], yb[3], ya[11], yb[11]) == (Y3, Y3P, Y11, Y11P)
              and all(ya[i] == yb[i] for i in range(16) if i not in (3, 11))
              and ya[7] == 0x76f7aefd and ya[15] == 0xbbfbdffe)
    # 6.2: the calls E1 and E3
    e1A, e1B, e3A, e3B = ca["E1"], cb["E1"], ca["E3"], cb["E3"]
    ok &= chk("6.2: inputs and words of E1 and E3 on A and B as displayed",
              e1A[0] == (ya[1], ya[6], Y11, t.Y12) and e1B[0] == (ya[1], ya[6], Y11P, t.Y12)
              and e1A[1] == (w[12], w[5]) and e1B[1] == (w[12], (w[5] + 0xfffffff8) & M)
              and e3A[0] == (Y3, y, ya[9], ya[14]) and e3B[0] == (Y3P, y, ya[9], ya[14])
              and e3A[1] == (0, w[8]) and e3B[1] == (0, w[8]))
    h1, h1p = e3A[2][1], e3B[2][1]
    cls_d, cls_q = in_class_def(y), in_class_q(y)
    ok &= chk("Lemma Q on this y: definition and mask form agree, and (h1 xor h1' = eta) exactly for members",
              cls_d == cls_q and ((h1 ^ h1p) == ETA) == cls_q)
    # Lemma E, as an identity: early word = ROL(D4,7) xor D1 (so R = 0 implies it is zero)
    tt = e1A[2][4] ^ e1B[2][4]
    early = (e3A[2][3] ^ e3B[2][3]) ^ tt ^ ror(tt, 1)
    ok &= chk("Lemma E as an identity: early word = ROL(D4,7) xor D1 of the organizer digests",
              early == rol(dd[4], 7) ^ dd[1])
    beta, eps = e1A[2][3] ^ e1B[2][3], e1A[2][6] ^ e1B[2][6]
    n = eps ^ rol(beta ^ eps, 1) ^ ETA
    # Lemma A
    c2v = ca["C2"][2]
    z = c2v[4] ^ c2v[1]
    e1 = (Y3 + y) & M
    ok &= chk("Lemma A (a): ROL(h1,24) = z xor ROL(e1,8); Y14 = ROR(z,8)",
              rol(h1, 24) == z ^ rol(e1, 8) and ya[14] == ror(z, 8))
    if cls_q:
        STATS["class trials"] += 1
        ok &= chk("Lemma T: eta = 830303cf for a class member", (h1 ^ h1p) == ETA)
        ok &= chk("Lemma N: n = D3 xor ROL(D6,8) of the organizer digests (class members)",
                  n == dd[3] ^ rol(dd[6], 8))
        ra = rule_a_h1(h1)
        ok &= chk("Lemma A (b), (c): rule A on h1 = conditions on z = zero word (class members)",
                  ra == rule_a_z(z) and ra == (rule_a_word(z) == 0))
        STATS["rule A passes"] += ra
        STATS["n zero"] += n == 0
        STATS["early zero"] += early == 0
    if not ok and STATS["first failure"] is None:
        STATS["first failure"] = (ctx, y)
    return w, A, B


def fact_p():
    txt = {W4: (0x7ffffff8, 0x7af83f3a, 0xbefb9f3a, 0x01200183, 0x8127c181, 0xbbfbdffe, 0x7af77f38, 0x76f7aefd),
           W4P: (0x80000000, 0x8500c0c5, 0xc90420c5, 0xfed77e78, 0x7edf3e7e, 0xbbfbdffe, 0x850000c3, 0x76f7aefd)}
    chk("3.1/3.2 constants: K = 5bf2cd1d, K + W4 = f33a2355, W4' = 97475640, W4 - W4' = fffffff8, top byte W13 0",
        K == 0x5bf2cd1d and (K + W4) & M == 0xf33a2355 and W4P == 0x97475640 and (W4 - W4P) & M == 0xfffffff8
        and W13 >> 24 == 0)
    for w4, want in txt.items():
        got = g8(X3, X7, X11, X15, w4, W13)
        v = [X3, X7, X11, X15]
        org_g(v, 0, 1, 2, 3, w4, W13)
        chk("Fact P: the eight displayed values of each execution, own G and organizer _g",
            got == want and (v[0], v[1], v[2], v[3]) == (want[4], want[7], want[6], want[5]))
    a, b = g8(X3, X7, X11, X15, W4, W13), g8(X3, X7, X11, X15, W4P, W13)
    chk("Fact P: d and b outputs equal, a and c outputs differ", a[5] == b[5] and a[7] == b[7]
        and a[4] != b[4] and a[6] != b[6])
    chk("Lemma Q arithmetic: DY3 = fdb77cfd, ROL(eta,16) = 03cf8303, DY3 + x = 01870000, value 030c0303, 19 free",
        DY3 == 0xfdb77cfd and rol(ETA, 16) == CMASK and (DY3 + CMASK) & M == 0x01870000
        and (~0x00c38000 & CMASK) & M == CVALUE and len(FREE) == 19 and 31 in FREE and bin(CMASK).count("1") == 13)


def lemma_l(rng, count):
    edge = [0, 1, 7, 8, M, (-K) & M, (8 - K) & M, (0x80000000 - K) & M, (0x7ffffff8 - K) & M]
    for i in range(count):
        w4 = edge[i % len(edge)] if i < 4 * len(edge) else rng.getrandbits(32)
        w5 = rng.getrandbits(32) if i % 3 else edge[(i // 3) % len(edge)]
        w4p = ((((K + w4) & M) ^ 8) - K) & M
        w5p = (w5 + w4 - w4p) & M
        va, vb = [IV[2], IV[6], IV[2], 55], [IV[2], IV[6], IV[2], 63]
        org_g(va, 0, 1, 2, 3, w4, w5)
        org_g(vb, 0, 1, 2, 3, w4p, w5p)
        chk("Lemma L: K2 with (55; w4, w5) and (63; w4', w5') leaves the same four words (organizer _g)", va == vb)


def lemma_q_exhaustive():
    import numpy as np
    y3, dy3 = np.uint32(Y3), np.uint32(DY3)
    members = mismatch = 0
    step = 1 << 24
    for base in range(0, 1 << 32, step):
        y = np.arange(base, base + step, dtype=np.uint64).astype(np.uint32)
        e1 = y + y3
        x = e1 ^ (e1 + dy3)
        eta = (x >> np.uint32(16)) | (x << np.uint32(16))
        d = eta == np.uint32(ETA)
        q = (e1 & np.uint32(CMASK)) == np.uint32(CVALUE)
        mismatch += int(np.count_nonzero(d != q))
        members += int(np.count_nonzero(d))
    chk("Lemma Q, all 2^32 values of Y4: definition = mask form, and 524,288 members",
        mismatch == 0 and members == 524288)
    k = np.arange(1 << 19, dtype=np.uint32)
    e1 = np.full(1 << 19, CVALUE, dtype=np.uint32)
    for j, pos in enumerate(FREE):
        e1 |= ((k >> np.uint32(j)) & np.uint32(1)) << np.uint32(pos)
    y4 = e1 - y3
    x = e1 ^ (e1 + dy3)
    eta = (x >> np.uint32(16)) | (x << np.uint32(16))
    chk("numbering: the 2^19 numbers give 2^19 distinct members, all in the class, e1 increasing with k",
        int(np.count_nonzero(eta == np.uint32(ETA))) == 1 << 19 and len(np.unique(y4)) == 1 << 19
        and bool(np.all(np.diff(e1.astype(np.int64)) > 0)))
    return members, mismatch


def program_compare(rng, samples):
    sys.path.insert(0, os.path.join(HERE, "..", "blake3-r2", "experiments"))
    import halfsearch as hs
    chk("program constants = text: W4', delta, Y3, Y3', Y11, Y11', class mask/value/size, rule constants, lengths",
        hs.W4B == W4P and hs.DELTA5 == 0xfffffff8 and (hs.Y3, hs.Y3B, hs.Y11, hs.Y11B) == (Y3, Y3P, Y11, Y11P)
        and hs.CLASS_MASK == CMASK and hs.CLASS_VALUE == CVALUE and hs.CLASS_SIZE == 524288
        and hs.A_SHIFTS == ((1, 0x04000000),) and hs.A_ALL == 0x07000300 and hs.A_VALUE == 0x06000300
        and (hs.LEN_A, hs.LEN_B) == (55, 63) and hs.BATCHES == 74899 and hs.RULE_CONDITIONS == 5
        and hs.STAGE_2_BUDGET == 74899 << 81)
    chk("program class_member(k) = text numbering for all 2^19 numbers",
        all(hs.class_member(k) == member(k) for k in range(1 << 19)))
    u, mem = hs.list_words(74898)
    chk("program list: last word holds members 524286, 524287 and repeats the last; lanes hold ROL(y,7)",
        mem == [member(524286)] + [member(524287)] * 6
        and [(u >> (36 * i)) & 0xFFFFFFFFF for i in range(7)] == [rol(y, 7) for y in mem])
    for i in range(samples):
        ctx = tuple(rng.getrandbits(32) for _ in range(7))
        y = member(rng.getrandbits(19)) if i % 4 else rng.getrandbits(32)
        c = step_S1(*ctx)
        t = step_T(c, y)
        w = [ctx[6], c.w1, c.w2, c.w3, W4, c.w5, c.w6, c.w7, t.w8, t.w9, t.w10, t.w11, c.w12, W13, 0, 0]
        Xp, Sp, wp, c0 = hs.context(ctx)
        words, st = hs.trial(Xp, Sp, wp, c0, y)
        wb = list(w)
        wb[4], wb[5] = W4P, (w[5] + W4 - W4P) & M
        chk("program context()/trial()/messages() = steps S1, T, S2, S3 of the text (words and both messages)",
            words == w and hs.messages(words) == (struct.pack("<16I", *w)[:55], struct.pack("<16I", *wb)[:63])
            and c0 == (c.vb, c.vc, c.vd) and st == (t.X0, t.X1, t.X5, t.X6, t.X10, t.X12, t.Y12))
        h = rng.getrandbits(32)
        chk("program rule_a(h1) = rule A as written in 6.3", hs.rule_a(h) == rule_a_h1(h))


def main():
    n_ctx = int(sys.argv[1]) if len(sys.argv) > 1 else 4000
    n_mem = int(sys.argv[2]) if len(sys.argv) > 2 else 25
    seed = int(sys.argv[3]) if len(sys.argv) > 3 else 20261006
    rng = random.Random(seed)
    t0 = time.time()
    fact_p()
    lemma_l(rng, 200000)
    trials = 0
    seen = set()
    # (1) random contexts, random members of the class
    for _ in range(n_ctx):
        ctx = tuple(rng.getrandbits(32) for _ in range(7))
        c = step_S1(*ctx)
        for _ in range(n_mem):
            w, A, B = check_trial(c, ctx, member(rng.getrandbits(19)))
            trials += 1
            seen.add(A)
    # (2) contexts as the algorithm lays them out: vd < 2^19, seed words held, X14 consecutive
    seeds = tuple(rng.getrandbits(32) for _ in range(4))
    for i in range(n_ctx // 8):
        ctx = (rng.getrandbits(32), rng.getrandbits(19), seeds[0], seeds[1], seeds[2], (0xfffffff0 + i) & M, seeds[3])
        c = step_S1(*ctx)
        for j in range(20):
            k = (i * 20 + j) % 524288 if j < 10 else 524287 - j
            w, A, B = check_trial(c, ctx, member(k))
            trials += 1
            seen.add(A)
    # (3) extreme contexts
    ext = (0, M, 0x80000000, 1)
    for i in range(n_ctx // 20):
        ctx = tuple(ext[rng.getrandbits(2)] if rng.getrandbits(2) else rng.getrandbits(32) for _ in range(7))
        c = step_S1(*ctx)
        for j in range(20):
            y = member((0, 524287, 1, 524286)[j]) if j < 4 else (ext[j % 4] if j < 8 else member(rng.getrandbits(19)))
            check_trial(c, ctx, y)
            trials += 1
    # (4) the theorem for any y (not only members)
    for _ in range(n_ctx // 4):
        ctx = tuple(rng.getrandbits(32) for _ in range(7))
        c = step_S1(*ctx)
        for _ in range(6):
            check_trial(c, ctx, rng.getrandbits(32))
            trials += 1
    t1 = time.time()
    members, mismatch = lemma_q_exhaustive()
    t2 = time.time()
    program_compare(rng, 3000)
    t3 = time.time()
    bad = [k for k, (a, b) in RES.items() if a != b]
    OUT.append("construction_impl.py: text-only implementation of proof.md Sections 1-6 against the organizer's "
               "verifier/blake3.py; seed %d" % seed)
    OUT.append("trials (two real messages each, hashed by the organizer's blake3 with rounds=2): %d; class members "
               "among them %d; distinct messages A in parts 1-2: %d" % (trials, STATS["class trials"], len(seen)))
    for k, (a, b) in RES.items():
        OUT.append("%-8s %9d of %9d  %s" % ("ok" if a == b else "FAIL", a, b, k))
    OUT.append("class trials that satisfy rule A: %d (share %.5f; 2^-5 = 0.03125); with n = 0: %d; early word 0: %d"
               % (STATS["rule A passes"], STATS["rule A passes"] / max(1, STATS["class trials"]), STATS["n zero"],
                  STATS["early zero"]))
    OUT.append("Lemma Q exhaustive: members %d, mismatches %d" % (members, mismatch))
    OUT.append("first failing trial: %r" % (STATS["first failure"],))
    OUT.append("seconds: trials %.0f, Lemma Q %.0f, program %.0f" % (t1 - t0, t2 - t1, t3 - t2))
    OUT.append("RESULT: %s" % ("all checks hold" if not bad else "FAILED: " + "; ".join(bad)))
    with open(os.path.join(HERE, "construction_impl_out.txt"), "w", encoding="ascii", newline="\n") as f:
        f.write("\n".join(OUT) + "\n")
    print(OUT[1])
    print("checks: %d kinds, failing kinds: %d" % (len(RES), len(bad)))
    print(OUT[-5])
    print(OUT[-4])
    print(OUT[-2])
    print(OUT[-1])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
