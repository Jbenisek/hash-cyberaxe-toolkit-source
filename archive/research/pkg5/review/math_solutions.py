#!/usr/bin/env python3
"""Reviewer, lens mathematics and cost: the two complete solutions printed in proof.md Section 10, evaluated with
G alone from the values typed from the text.   python3 -B math_solutions.py
"""
M = 0xFFFFFFFF


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def steps(A, B, C, D, x, y):
    a1 = (A + B + x) & M; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)


Y3, Y3B, Y11, Y11B, DELTA, ETA = 0x3F52EDA0, 0xC0AC125F, 0x5EBF5BC0, 0xA144803F, 0xFFFFFFFE, 0xE7C1815F


def rule_a(h1):
    b = lambda i: h1 >> i & 1  # noqa: E731
    return [b(16) == 1, b(0) == b(1), b(1) == b(2), b(2) == b(3), b(3) != b(4), b(23) != b(24)]


for name, (Y1, Y6, Y12, w12, w5, Y4, Y9, Y14, w8), want in (
        ("violating", (0x052CE267, 0xFAD31D99, 0x69DA227B, 0, 0x57D7DFEF, 0xC0D07BF1, 0xFCDE77B6, 0xA48CB1EE, 0x5141CE8C),
         (0xF8342852, 0x17D4E830, 0xF298B0A9, 0xD87FA4AF)),
        ("satisfying", (0x00000000, 0x7E1401E5, 0x5A538AB4, 0, 0x234E3245, 0x0AD073E5, 0x61E4852D, 0xDDCC82F4, 0xA2EE086C),
         (0x481C6852, 0x481C2830, 0x2D5730A9, 0xE37197EF))):
    ea, eb = steps(Y1, Y6, Y11, Y12, w12, w5), steps(Y1, Y6, Y11B, Y12, w12, (w5 + DELTA) & M)
    fa, fb = steps(Y3, Y4, Y9, Y14, 0, w8), steps(Y3B, Y4, Y9, Y14, 0, w8)
    R = (ea["a2"] ^ fa["c2"] ^ eb["a2"] ^ fb["c2"], fa["a2"] ^ ea["c2"] ^ fb["a2"] ^ eb["c2"],
         fa["b2"] ^ ea["d2"] ^ fb["b2"] ^ eb["d2"], ea["b2"] ^ fa["d2"] ^ eb["b2"] ^ fb["d2"])
    got = (ea["b1"] ^ eb["b1"], ea["a2"] ^ eb["a2"], ea["c2"] ^ eb["c2"], fa["d1"])
    print("%s: R zero %s; beta, tau, eps, h1 as printed %s; eta %s; class %s; rule A conditions %s" % (
        name, R == (0, 0, 0, 0), got == want, fa["d1"] ^ fb["d1"] == ETA, ((Y3 + Y4) & 0x015FE7C1) == 0x00036181,
        "".join("1" if c else "0" for c in rule_a(fa["d1"]))))
