#!/usr/bin/env python3
"""Review helper (lens: judge). Reads proof.md only; writes review/judge_misc.txt.

Fact P as displayed, Lemma Q and Lemma A (b), (c) by exhaustion over what they quantify, the two solutions that
Section 10 prints (E1 and E3 for A and B from 6.2, R = 0, beta, tau, eps, h1, rule A), the table of the heaviest
beta (Adds = N1 * N3 / 2^83), and the tables' sums.
"""
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
proof = (HERE.parent / "blake3-r2" / "proof.md").read_text(encoding="utf-8")
M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def G(A, B, C, D, x, y):
    a1 = (A + B + x) & M; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)


X3, X7, X11, X15, W4, W13 = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500, 0x97475638, 0x0007C006
K = (IV[2] + IV[6]) & M
W4B = (((K + W4) ^ 8) - K) & M
a, b = G(X3, X7, X11, X15, W4, W13), G(X3, X7, X11, X15, W4B, W13)
shown = re.findall(r"a1=([0-9a-f]{8}) d1=([0-9a-f]{8}) c1=([0-9a-f]{8}) b1=([0-9a-f]{8})\s+a2=([0-9a-f]{8}) d2=([0-9a-f]{8}) c2=([0-9a-f]{8}) b2=([0-9a-f]{8})", proof)
mine = [tuple(f"{x[k]:08x}" for k in ("a1", "d1", "c1", "b1", "a2", "d2", "c2", "b2")) for x in (a, b)]
say(f"Fact P: K {K:08x} K+W4 {(K + W4) & M:08x} W4' {W4B:08x} W4-W4' {(W4 - W4B) & M:08x}; the two displayed executions equal mine: {shown == mine}; "
    f"same d and b outputs: {a['d2'] == b['d2'] and a['b2'] == b['b2']}; top byte of W13 zero: {W13 >> 24 == 0}")
Y3, Y3B, Y11, Y11B = a["a2"], b["a2"], a["c2"], b["c2"]
DY3, DELTA, ETA = (Y3B - Y3) & M, (W4 - W4B) & M, 0x830303CF
say(f"Y3 {Y3:08x} Y3' {Y3B:08x} DY3 {DY3:08x} Y11 {Y11:08x} Y11' {Y11B:08x} DY11 {(Y11B - Y11) & M:08x} delta {DELTA:08x}")

# Lemma Q by a direct test of the definition on random words and on all members
import random
rnd = random.Random(7)
QM, QV = 0x03CF8303, 0x030C0303
agree = 0
for _ in range(400000):
    y4 = rnd.getrandbits(32)
    e1 = (Y3 + y4) & M
    in_class = ror(e1 ^ ((e1 + DY3) & M), 16) == ETA
    agree += in_class == ((e1 & QM) == QV)
free = [i for i in range(32) if not QM >> i & 1]
members_ok = 0
for k in range(1 << 19):
    e1 = QV
    for j, pos in enumerate(free):
        e1 |= (k >> j & 1) << pos
    members_ok += ror(e1 ^ ((e1 + DY3) & M), 16) == ETA
say(f"Lemma Q: definition and mask test agree on {agree} of 400000 random Y4; all members give eta: {members_ok} of 524288; "
    f"DY3 + x = {(DY3 + rol(ETA, 16)) & M:08x}")

# Lemma A (b), (c): rule A on h1 against the conditions on z and the word of (c), over all 64 values of the six bits of z
# that enter, random other bits, and random members
S_, ALL, V = 0x04000000, 0x07000300, 0x06000300
bad = 0
for t in range(200000):
    z = rnd.getrandbits(32)
    k = rnd.getrandbits(19)
    e1 = QV
    for j, pos in enumerate(free):
        e1 |= (k >> j & 1) << pos
    h1 = ror(ror(z, 8) ^ e1, 16)
    bit = lambda w, i: w >> i & 1
    rule = bit(h1, 0) == 0 and bit(h1, 16) == 0 and bit(h1, 17) == 0 and bit(h1, 1) == 1 and bit(h1, 2) != bit(h1, 3)
    onz = bit(z, 24) == 0 and bit(z, 25) == 1 and bit(z, 8) == 1 and bit(z, 9) == 1 and bit(z, 26) != bit(z, 27)
    wordc = ((z ^ ((z >> 1) & S_)) & ALL) ^ V
    bad += not (rule == onz == (wordc == 0)) or rol(h1, 24) != z ^ rol(e1, 8)
say(f"Lemma A (a), (b), (c): disagreements in 200000 random (z, member): {bad}")


def solution(text):
    v = {k: int(x, 16) for k, x in re.findall(r"\b(Y1|Y6|Y12|w12|w5|Y4|Y9|Y14|w8) =\s+([0-9a-f]{8})", text)}
    want = {k: int(x, 16) for k, x in re.findall(r"\b(beta|tau|eps|h1) =\s+([0-9a-f]{8})", text)}
    A1 = G(v["Y1"], v["Y6"], Y11, v["Y12"], v["w12"], v["w5"])
    B1 = G(v["Y1"], v["Y6"], Y11B, v["Y12"], v["w12"], (v["w5"] + DELTA) & M)
    A3 = G(Y3, v["Y4"], v["Y9"], v["Y14"], 0, v["w8"])
    B3 = G(Y3B, v["Y4"], v["Y9"], v["Y14"], 0, v["w8"])
    R = ((A1["a2"] ^ A3["c2"]) ^ (B1["a2"] ^ B3["c2"]), (A3["a2"] ^ A1["c2"]) ^ (B3["a2"] ^ B1["c2"]),
         (A3["b2"] ^ A1["d2"]) ^ (B3["b2"] ^ B1["d2"]), (A1["b2"] ^ A3["d2"]) ^ (B1["b2"] ^ B3["d2"]))
    h1 = A3["d1"]
    bit = lambda w, i: w >> i & 1
    rule = bit(h1, 0) == 0 and bit(h1, 16) == 0 and bit(h1, 17) == 0 and bit(h1, 1) == 1 and bit(h1, 2) != bit(h1, 3)
    got = dict(beta=A1["b1"] ^ B1["b1"], tau=A1["a2"] ^ B1["a2"], eps=A1["c2"] ^ B1["c2"], h1=h1)
    in_class = ((Y3 + v["Y4"]) & QM) == QV
    return R == (0, 0, 0, 0), got == want, in_class, rule


i = proof.index("*Two solutions, written out.*")
block = proof[i:proof.index("*The other rules and the other factor.*")].replace("\n", " ")
first, second = block.split("A complete solution of the seven-word system with Y4 in the class that violates rule A")
say(f"printed solution 1 (R = 0, printed beta tau eps h1 right, Y4 in the class, satisfies rule A): {solution(first)}")
say(f"printed solution 2 (R = 0, printed beta tau eps h1 right, Y4 in the class, satisfies rule A): {solution(second)}")

# the table of the heaviest beta
rows = re.findall(r"^\| ([0-9a-f]{8}) \| ([0-9a-f]{8}) \| ([0-9* ^]+) \| ([0-9* ^]+) \| ([\d,.]+) \|$", proof, re.M)
val = lambda s: eval(s.replace("^", "**").replace(" ", ""))
okrows = sum(Fraction(val(n1) * val(n3), 2 ** 83) == Fraction(adds.replace(",", "")) for _, _, n1, n3, adds in rows)
say(f"table of the heaviest beta: rows {len(rows)}, Adds = N1 * N3 / 2^83 in {okrows}; sum {float(sum(Fraction(r[4].replace(',', '')) for r in rows)):,.1f}")
kept = re.findall(r"^\| ([0-9a-f]{8}) \| ([0-9a-f]{8}) \| ([0-9a-f]{8}) \| ([\d,.]+) \|$", proof, re.M)
say(f"table of the kept outcomes: rows {len(kept)}, sum of the printed column {sum(float(r[3].replace(',', '')) for r in kept):,.4f}")
(HERE / "judge_misc.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print("\n".join(x[:230] for x in out))
