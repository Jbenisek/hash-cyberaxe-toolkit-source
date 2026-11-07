#!/usr/bin/env python3
"""Numerical check of the fifth blake3-r2 package (new constants, new class, two-stage batch). Research helper, not submitted.

Part (a) writes the formulas of pkg5 proof.md (step S1, Section 6.1) a second time, straight from the
text, and compares them on random trials with a plain forward 2-round BLAKE3 compression that is also
written here. Nothing of the package's experiment program is used in part (a). The six constants and eta
are taken from tools/pkg5_data.py, the one place that holds them, and so are the conditions of rule A; everything
else is computed here, and the constants that the rendered proof prints (Fact P, Lemma Q, Lemma A) are read back from
proof.md and compared. Lemma N and Lemma A are checked on every random trial against the forward compression, and
the solution that violates rule A, which Section 10 prints, is evaluated with the G of this script.

Part (b) runs pkg5/blake3-r2/experiments/halfsearch.py through its stdin/stdout contract and checks
the returned message pairs with the same forward compression.

    python -B check_pkg5.py [trials, default 20000] [experiment trials, default 256]

Exit status 0 only if every check holds.
"""
import hashlib
import json
import random
import re
import struct
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PROGRAM = HERE / "blake3-r2" / "experiments" / "halfsearch.py"
MANIFEST = HERE / "blake3-r2" / "experiments" / "manifest.json"
PROOF = HERE / "blake3-r2" / "proof.md"
sys.path.insert(0, str(HERE / "tools"))
import pkg5_data  # noqa: E402  (only PIN, ETA, LOG2_X12, RULE_A and, for part (b), the stage counts are taken from it)

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
X3, X7, X11, X15, W4, W13 = (pkg5_data.PIN[k] for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
ETA = pkg5_data.ETA
ETA_HEX = f"{ETA:08x}"
FAILS = []


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M32


def rol(v, n):
    return ror(v, 32 - n)


def G(A, B, C, D, x, y):
    A = (A + B + x) & M32; D = ror(D ^ A, 16); C = (C + D) & M32; B = ror(B ^ C, 12)
    A = (A + B + y) & M32; D = ror(D ^ A, 8); C = (C + D) & M32; B = ror(B ^ C, 7)
    return A, B, C, D


# ---------------------------------------------------------------- forward 2-round BLAKE3, one block
def compress2(words, n):
    """Plain forward compression (proof.md Section 1). Returns digest words and the states S, X, Y."""
    v = list(IV) + list(IV[:4]) + [0, 0, n, 11]
    s = list(words)
    snap = []
    for _ in range(2):
        for j in range(4):
            idx = (j, 4 + j, 8 + j, 12 + j)
            out = G(*(v[i] for i in idx), s[2 * j], s[2 * j + 1])
            for i, o in zip(idx, out):
                v[i] = o
        snap.append(list(v))
        for j, idx in enumerate(((0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14))):
            out = G(*(v[i] for i in idx), s[8 + 2 * j], s[9 + 2 * j])
            for i, o in zip(idx, out):
                v[i] = o
        snap.append(list(v))
        s = [s[p] for p in PERM]
    S, X, Y, Z = snap
    return [Z[i] ^ Z[i + 8] for i in range(8)], S, X, Y


def hash2(message):
    """Complete 2-round BLAKE3-256 of a message of at most 64 bytes, as eight digest words."""
    assert len(message) <= 64
    words = struct.unpack("<16I", message + bytes(64 - len(message)))
    return compress2(words, len(message))


# ---------------------------------------------------------------- the proof's formulas, written again
K = (IV[2] + IV[6]) & M32
W4B = ((((K + W4) & M32) ^ 2) - K) & M32
DELTA = (W4 - W4B) & M32
Y3, _, Y11, _ = G(X3, X7, X11, X15, W4, W13)
Y3B, _, Y11B, _ = G(X3, X7, X11, X15, W4B, W13)
D3 = (Y3B - Y3) & M32


def g_steps(A, B, C, D, x, y):
    """The eight assignments of one G call, in the order a1, d1, c1, b1, a2, d2, c2, b2 (proof.md Section 2)."""
    a1 = (A + B + x) & M32; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M32; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


def qa_steps(a, b, c, d, y):
    """The second value (first-half d) of a G call with first word 0: used for h1 of E3."""
    return g_steps(a, b, c, d, 0, y)[1]


def col(j, sb, sc, d0):
    b1 = rol(sb, 7) ^ sc; c1 = rol(b1, 12) ^ IV[4 + j]; sd = (sc - c1) & M32
    d1 = (c1 - IV[j]) & M32; a1 = rol(d1, 16) ^ d0
    x = (a1 - IV[j] - IV[4 + j]) & M32; sa = rol(sd, 8) ^ d1; y = (sa - a1 - b1) & M32
    return sa, sd, x, y


def step_s1(X1, X2, X5, X6, X9, X10, X12, X13, X14):
    """Step S1 of proof.md Section 4. Returns (X, S, w, keep) with keep = (bD1, aD3)."""
    X = [None] * 16; S = [None] * 16; w = [None] * 16
    X[1], X[2], X[5], X[6], X[9], X[10], X[12], X[13], X[14] = X1, X2, X5, X6, X9, X10, X12, X13, X14
    X[3], X[7], X[11], X[15] = X3, X7, X11, X15
    w[4], w[13], w[15] = W4, W13, 0
    p = (K + W4) & M32; q = ror(p ^ 60, 16); r = (q + IV[2]) & M32; u = ror(r ^ IV[6], 12)
    b = rol(X6, 7) ^ X11; c = (X11 - X12) & M32; d = rol(X12, 8) ^ X1
    S[6] = rol(b, 12) ^ c; S[11] = (c - d) & M32; bD1, dD1 = b, d
    S[10] = u ^ rol(S[6], 7)
    b = rol(X5, 7) ^ X10; c = (X10 - X15) & M32; S[5] = rol(b, 12) ^ c
    d = (c - S[10]) & M32; X[0] = d ^ rol(X15, 8); bD0, dD0 = b, d
    S[14] = (S[10] - r) & M32; S[2] = rol(S[14], 8) ^ q; w[5] = (S[2] - p - u) & M32
    d = rol(X14, 8) ^ X3; a = rol(d, 16) ^ S[14]; b = (X3 - a - w[15]) & M32
    X[4] = ror(b ^ X9, 7); c = (X9 - X14) & M32
    S[4] = rol(b, 12) ^ c; S[9] = (c - d) & M32; aD3 = a
    S[1], S[13], w[2], w[3] = col(1, S[5], S[9], 0)
    d = rol(X13, 8) ^ X2; a = rol(d, 16) ^ S[13]; b = (X2 - a - W13) & M32
    X[8] = b ^ rol(X7, 7); c = (X[8] - X13) & M32
    S[7] = rol(b, 12) ^ c; S[8] = (c - d) & M32; w[12] = (a - S[2] - S[7]) & M32
    S[0], S[12], w[0], w[1] = col(0, S[4], S[8], 0)
    S[3], S[15], w[6], w[7] = col(3, S[7], S[11], 11)
    a = rol(dD0, 16) ^ S[15]; w[8] = (a - S[0] - S[5]) & M32; w[9] = (X[0] - a - bD0) & M32
    a = rol(dD1, 16) ^ S[12]; w[10] = (a - S[1] - S[6]) & M32; w[11] = (X1 - a - bD1) & M32
    w[14] = (aD3 - S[3] - S[4]) & M32
    return X, S, w, (bD1, aD3)


def class_of_eta():
    """Lemma Q: mask and value of the fixed bits of e1 = Y3 + Y4."""
    x = rol(ETA, 16)
    v = (D3 + x) & M32
    assert v % 2 == 0 and (v >> 1) & ~x & M32 == 0, "the class is empty"
    mask = x & 0x7FFFFFFF
    return mask, ~(v >> 1) & mask


CMASK, CVALUE = class_of_eta()
CFREE = [i for i in range(32) if not CMASK >> i & 1]
RULE = pkg5_data.RULE_A[ETA]


def rule_on_h1(h1):
    """Rule A as proof.md 6.3 states it: for every condition, the XOR of the named bits of h1 has the stated value."""
    return all(bin(h1 & mask).count("1") & 1 == value for mask, value in RULE)


def rule_on_z():
    """Lemma A (b), (c), derived here: [(bits of z, wanted XOR)] and the constants S, ALL, V."""
    conditions, s, everything, v = [], 0, 0, 0
    for mask, value in RULE:
        hbits = [i for i in range(32) if mask >> i & 1]
        for i in hbits:                                # bit i of h1 = bit (i + 24) of z XOR bit (i + 16) of e1
            e = (i + 16) % 32
            assert CMASK >> e & 1, "rule A meets a free bit of e1"
            value ^= CVALUE >> e & 1
        zbits = sorted((i + 24) % 32 for i in hbits)
        conditions.append((zbits, value))
        assert len(zbits) == 1 or (len(zbits) == 2 and zbits[1] == zbits[0] + 1)
        if len(zbits) == 2:
            s |= 1 << zbits[0]
        everything |= 1 << zbits[0]
        v |= value << zbits[0]
    return conditions, s, everything, v


Z_CONDITIONS, A_S, A_ALL, A_V = rule_on_z()
# the ranges of the algorithm (6.4): 2^(127 - F) trials = contexts * 2^32 alphas * members; X12 and X14 as stated
X13_BITS = 127 - pkg5_data.LOG2_FACTOR - 32 - len(CFREE) - pkg5_data.LOG2_X12 - 32


def member(k):
    e1 = CVALUE
    for j, i in enumerate(CFREE):
        e1 |= (k >> j & 1) << i
    return (e1 - Y3) & M32


def eta_of(y4):
    e1 = (Y3 + y4) & M32
    return ror(e1 ^ ((Y3B + y4) & M32), 16)


def trial_6_1(X, S, w, keep, alpha, y):
    """The formulas of proof.md 6.1 in the order of the text. Returns a dict of everything they define."""
    bD1, aD3 = keep
    t = {}
    # D0 family
    c = (alpha - X15) & M32; d = (c - S[10]) & M32; t["X0"] = rol(X15, 8) ^ d
    b = ror(S[5] ^ c, 12); t["X5"] = ror(b ^ alpha, 7); t["X10"] = alpha
    dD0, bD0 = d, b
    # C0 backwards
    a1 = (t["X0"] + X[4] + w[2]) & M32; d1 = ror(X[12] ^ a1, 16); c1 = (X[8] + d1) & M32
    b1 = ror(X[4] ^ c1, 12)
    c2 = rol(y, 7) ^ b1; t["Y12"] = (c2 - c1) & M32; a2 = rol(t["Y12"], 8) ^ d1
    t["w6"] = (a2 - a1 - b1) & M32
    # K3 with S7 kept
    ka = (IV[3] + IV[7] + t["w6"]) & M32; kd = ror(11 ^ ka, 16); kc = (IV[3] + kd) & M32
    kb = ror(IV[7] ^ kc, 12)
    t["S11"] = rol(S[7], 7) ^ kb; t["S15"] = (t["S11"] - kc) & M32; t["S3"] = rol(t["S15"], 8) ^ kd
    t["w7"] = (t["S3"] - ka - kb) & M32
    # D1 with the new S11
    d = (X11 - X[12] - t["S11"]) & M32; t["X1"] = rol(X[12], 8) ^ d
    a = rol(d, 16) ^ S[12]; t["w10"] = (a - S[1] - S[6]) & M32; t["w11"] = (t["X1"] - a - bD1) & M32
    # D0 with the new S15
    a = rol(dD0, 16) ^ t["S15"]; t["w8"] = (a - S[0] - S[5]) & M32; t["w9"] = (t["X0"] - a - bD0) & M32
    # D3 with the new S3
    t["w14"] = (aD3 - t["S3"] - S[4]) & M32
    return t


def d0_family_plain(X, S, alpha):
    """The D0 family alone (context's S15): X0, X5, w8, w9."""
    c = (alpha - X15) & M32; d = (c - S[10]) & M32; x0 = rol(X15, 8) ^ d
    b = ror(S[5] ^ c, 12); x5 = ror(b ^ alpha, 7)
    a = rol(d, 16) ^ S[15]
    return x0, x5, (a - S[0] - S[5]) & M32, (x0 - a - b) & M32


def to_messages(words):
    other = list(words)
    other[4] = W4B
    other[5] = (words[5] + DELTA) & M32
    return struct.pack("<16I", *words)[:60], struct.pack("<16I", *other)[:62]


# ---------------------------------------------------------------- bookkeeping
class Tally:
    def __init__(self):
        self.count = {}
        self.order = []

    def check(self, name, ok):
        if name not in self.count:
            self.count[name] = [0, 0]
            self.order.append(name)
        self.count[name][0] += 1
        if ok:
            self.count[name][1] += 1
        elif len(FAILS) < 10:
            FAILS.append(name)
        return ok

    def report(self):
        for name in self.order:
            n, good = self.count[name]
            print(f"  [{'ok' if n == good else 'FAIL'}] {good} of {n}  {name}")
        return all(n == good for n, good in self.count.values())


def reference():
    """The organizer's reference BLAKE3, if the repository is next to this folder (optional cross-check)."""
    root = HERE.parent.parent / "hash-smash"
    if not (root / "verifier" / "blake3.py").exists():
        return None
    sys.path.insert(0, str(root))
    try:
        from verifier.blake3 import blake3 as ref
    except Exception:
        return None
    return ref


def part_a(trials, rng, ref):
    print(f"(a) proof formulas against a forward 2-round compression, {trials} random trials")
    print(f"    constants: Y3 {Y3:08x} Y3' {Y3B:08x} Y11 {Y11:08x} Y11' {Y11B:08x} D3 {D3:08x} W4' {W4B:08x} delta {DELTA:08x}")
    print(f"    class eta {ETA:08x}: ROL(eta,16) {rol(ETA, 16):08x}, D3 + ROL(eta,16) {(D3 + rol(ETA, 16)) & M32:08x}, "
          f"mask {CMASK:08x}, value {CVALUE:08x}, {len(CFREE)} free bits, {1 << len(CFREE)} members")
    t = Tally()

    # Lemma Q: membership formula against the definition of eta
    members = [member(k) for k in range(1 << len(CFREE))]
    size = len(members)
    t.check(f"Lemma Q: all {size} enumerated members are distinct", len(set(members)) == size == 1 << len(CFREE))
    t.check(f"Lemma Q: every enumerated member has eta = {ETA_HEX}", all(eta_of(y) == ETA for y in members))
    # what the rendered proof prints, read back from proof.md
    proof = PROOF.read_text(encoding="ascii")
    hx = lambda v: f"{v & M32:08x}"
    s = (D3 + rol(ETA, 16)) & M32
    sa, sb = g_steps(X3, X7, X11, X15, W4, W13), g_steps(X3, X7, X11, X15, W4B, W13)
    printed = {
        "the six constants": f"X3 = {hx(X3)}   X7 = {hx(X7)}   X11 = {hx(X11)}   X15 = {hx(X15)}\n    W4 = {hx(W4)}   W13 = {hx(W13)}",
        "K + W4 and W4'": f"K + W4 = {hx(K + W4)} and W4' = ((K + W4) XOR 2) - K = {hx(W4B)}",
        "Fact P table, first execution": "a1={} d1={} c1={} b1={}\n               a2={} d2={} c2={} b2={}".format(*(hx(v) for v in sa)),
        "Fact P table, second execution": "a1={} d1={} c1={} b1={}\n               a2={} d2={} c2={} b2={}".format(*(hx(v) for v in sb)),
        "Fact P statement": f"same d output {hx(sa[5])} and the same b\noutput {hx(sa[7])}. They differ in the a output ({hx(Y3)}, {hx(Y3B)})",
        "Lemma Q statement": f"((Y3 + Y4) AND {hx(CMASK)}) = {hx(CVALUE)}.",
        "Lemma Q proof: x and m": f"Put x = ROL(eta,16) = {hx(rol(ETA, 16))} and m = x AND 7fffffff = {hx(CMASK)}.",
        "Lemma Q proof: the sum and its half": f"{hx(s)} >> 1 = {hx(s >> 1)}.",
        "eta": f"Fix eta = {ETA_HEX}.",
        "Lemma A (c): the constants S, ALL and V": f"Put S = {hx(A_S)}, ALL = {hx(A_ALL)} and V = {hx(A_V)}.",
        "Lemma A (b): the conditions on z": " ".join(
            (f"bit {zb[0]} of z is {v}" if len(zb) == 1 else f"bits {zb[0]} and {zb[1]} of z {'differ' if v else 'are equal'}")
            + (";" if n + 1 < len(Z_CONDITIONS) else ".") for n, (zb, v) in enumerate(Z_CONDITIONS)),
        "rule A as stated on h1": " ".join(
            (f"bit {hb[0]} of h1 is {v}" if len(hb) == 1 else f"bits {hb[0]} and {hb[1]} of h1 {'differ' if v else 'are equal'}")
            + (";" if n + 1 < len(RULE) else ".")
            for n, (hb, v) in enumerate(sorted((([i for i in range(32) if m >> i & 1], v) for m, v in RULE),
                                               key=lambda c: (len(c[0]) != 1, c[1], c[0])))),
        "the member count": f"It has {size:,} members: the {len(CFREE)} bits",
    }
    flat = re.sub(r"\s+", " ", proof)
    for name, text in printed.items():
        t.check(f"proof.md prints what this script computes: {name}", re.sub(r"\s+", " ", text) in flat)
    # The solution of the seven-word system that Section 10 prints inside the class, evaluated with the G of this
    # script: E1 = G(Y1, Y6, Y11, Y12; w12, w5) and E3 = G(Y3, Y4, Y9, Y14; 0, w8) for A, and for B with Y11', Y3'
    # and w5 + (W4 - W4'). Digest words 1, 3, 4, 6 are E1.a ^ E3.c, E3.a ^ E1.c, E3.b ^ E1.d, E1.b ^ E3.d.
    sol = re.search(r"A complete solution of the seven-word system with Y4 in the class, which.{0,80}?Y1 = ([0-9a-f]{8}), Y6 = "
                    r"([0-9a-f]{8}), Y12 = ([0-9a-f]{8}), w12 = ([0-9a-f]{8}), w5 = ([0-9a-f]{8}), Y4 = ([0-9a-f]{8}), Y9 = "
                    r"([0-9a-f]{8}), Y14 = ([0-9a-f]{8}), w15 = 0, w8 = ([0-9a-f]{8})\. .{0,200}?beta = ([0-9a-f]{8}), and the XOR "
                    r"differences of its a and c outputs are tau = ([0-9a-f]{8}) and eps = ([0-9a-f]{8})", flat)
    if sol:
        y1, y6, y12, w12, w5, y4, y9, y14, w8, beta_p, tau_p, eps_p = (int(v, 16) for v in sol.groups())
        ea, eb = G(y1, y6, Y11, y12, w12, w5), G(y1, y6, Y11B, y12, w12, (w5 + DELTA) & M32)
        fa, fb = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
        words_a = (ea[0] ^ fa[2], fa[0] ^ ea[2], fa[1] ^ ea[3], ea[1] ^ fa[3])
        words_b = (eb[0] ^ fb[2], fb[0] ^ eb[2], fb[1] ^ eb[3], eb[1] ^ fb[3])
        t.check("the solution of the seven-word system printed in Section 10: digest words 1, 3, 4, 6 equal for A and B",
                words_a == words_b)
        t.check("the printed solution has Y4 in the class", ((Y3 + y4) & M32) & CMASK == CVALUE and eta_of(y4) == ETA)
        b1a = ror(y6 ^ ((Y11 + ror(y12 ^ ((y1 + y6 + w12) & M32), 16)) & M32), 12)
        b1b = ror(y6 ^ ((Y11B + ror(y12 ^ ((y1 + y6 + w12) & M32), 16)) & M32), 12)
        t.check("the printed solution has the beta, tau and eps that the proof states for it",
                (b1a ^ b1b, ea[0] ^ eb[0], ea[2] ^ eb[2]) == (beta_p, tau_p, eps_p))
        row = re.search(rf"\| {tau_p:08x} \| {eps_p:08x} \| ", proof)
        t.check("the outcome of the printed solution is a row of the table of outcomes", row is not None)
    else:
        print("    (no solution inside the class is printed in Section 10)")
    # The solution that violates rule A, printed in Section 10, evaluated with the G of this script.
    bad = re.search(r"A complete solution of the seven-word system with Y4 in the class that violates rule A.{0,80}?Y1 = "
                    r"([0-9a-f]{8}), Y6 = ([0-9a-f]{8}), Y12 = ([0-9a-f]{8}), w12 = ([0-9a-f]{8}), w5 = ([0-9a-f]{8}), Y4 = "
                    r"([0-9a-f]{8}), Y9 = ([0-9a-f]{8}), Y14 = ([0-9a-f]{8}), w15 = 0, w8 = ([0-9a-f]{8})\. .{0,120}?h1 = ([0-9a-f]{8}) "
                    r"does not satisfy rule A.{0,200}?Its outcome is tau = ([0-9a-f]{8}), eps = ([0-9a-f]{8}) with beta = ([0-9a-f]{8})", flat)
    if bad:
        y1, y6, y12, w12, w5, y4, y9, y14, w8, h1_p, tau_p, eps_p, beta_p = (int(v, 16) for v in bad.groups())
        ea, eb = G(y1, y6, Y11, y12, w12, w5), G(y1, y6, Y11B, y12, w12, (w5 + DELTA) & M32)
        fa, fb = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
        t.check("the solution that violates rule A, printed in Section 10: digest words 1, 3, 4, 6 equal for A and B",
                (ea[0] ^ fa[2], fa[0] ^ ea[2], fa[1] ^ ea[3], ea[1] ^ fa[3]) == (eb[0] ^ fb[2], fb[0] ^ eb[2], fb[1] ^ eb[3], eb[1] ^ fb[3]))
        h1 = ror(y14 ^ ((Y3 + y4) & M32), 16)
        t.check("that solution has Y4 in the class, the h1 that the proof prints, and h1 violates rule A",
                ((Y3 + y4) & M32) & CMASK == CVALUE and eta_of(y4) == ETA and h1 == h1_p and not rule_on_h1(h1))
        b1a = ror(y6 ^ ((Y11 + ror(y12 ^ ((y1 + y6 + w12) & M32), 16)) & M32), 12)
        b1b = ror(y6 ^ ((Y11B + ror(y12 ^ ((y1 + y6 + w12) & M32), 16)) & M32), 12)
        t.check("that solution has the beta, tau and eps that the proof states for it",
                (b1a ^ b1b, ea[0] ^ eb[0], ea[2] ^ eb[2]) == (beta_p, tau_p, eps_p))
    else:
        print("    (no solution that violates rule A is printed in Section 10)")
    t.check("Fact P: the two executions agree in b and d and differ in a and c",
            sa[5] == sb[5] and sa[7] == sb[7] and sa[4] != sb[4] and sa[6] != sb[6])
    t.check("W4 - W4' is +2 or -2 modulo 2^32, and DELTA is the word the proof prints",
            DELTA in (2, M32 - 1) and f"W4 - W4' = {hx(DELTA)}" in flat)
    t.check("Lemma Q: the fixed bits of DY3 + x lie in m, DY3 + x is even, bit 31 of e1 is free",
            s % 2 == 0 and (s >> 1) & ~CMASK & M32 == 0 and 31 in CFREE)
    member_set = set(members)
    inside = 0
    for _ in range(200000):
        y = rng.getrandbits(32)
        if rng.random() < 0.5:                       # half of the samples near the class: a member with bits flipped
            y = members[rng.randrange(size)]
            for _ in range(rng.randrange(0, 3)):
                y ^= 1 << rng.randrange(32)
        by_formula = ((Y3 + y) & M32) & CMASK == CVALUE
        inside += by_formula
        t.check(f"Lemma Q: (e1 AND mask) = value  <=>  eta(Y4) = {ETA_HEX}  (200000 values of Y4, half near the class)",
                by_formula == (eta_of(y) == ETA) == (y in member_set))
    changed_all = 0
    changed_sets = {}
    first = None
    rule_passes = 0
    for n in range(trials):
        nine = [rng.getrandbits(32) for _ in range(9)]
        if n % 16 == 0:                               # a context of the algorithm: X1 = X10 = 0, X12 and X13 in their ranges
            nine[0] = nine[5] = 0
            nine[6] = rng.randrange(1 << pkg5_data.LOG2_X12)
            nine[7] = rng.randrange(1 << X13_BITS)
        alpha = rng.getrandbits(32)
        k = rng.randrange(size)
        y = members[k]
        X, S, w, keep = step_s1(*nine)

        # Lemma S for the context, by running round 0 forward
        _, S_f, X_f, _ = compress2(w, 60)
        t.check("Lemma S: round 0 of the context's words gives the S and X of step S1", S_f == S and X_f == X)

        # Lemma F alone (alpha, context's S15)
        x0, x5, w8a, w9a = d0_family_plain(X, S, alpha)
        t.check("Lemma F: D0(S0,S5,S10,S15; w8,w9) = (X0, X5, alpha, X15)",
                G(S[0], S[5], S[10], S[15], w8a, w9a) == (x0, x5, alpha, X15))
        base_w = list(w); base_w[8], base_w[9] = w8a, w9a
        base_X = list(X); base_X[0], base_X[5], base_X[10] = x0, x5, alpha
        _, S_b, X_b, _ = compress2(base_w, 60)
        t.check("Lemma F: the context with the D0 family applied is a valid round 0 (same S, X0 X5 X10 moved)",
                S_b == S and X_b == base_X)

        tr = trial_6_1(X, S, w, keep, alpha, y)
        t.check("6.1: the trial's X0, X5 equal those of the D0 family", (tr["X0"], tr["X5"]) == (x0, x5))
        # Lemma Y
        c0 = G(tr["X0"], X[4], X[8], X[12], w[2], tr["w6"])
        t.check("Lemma Y: C0(X0,X4,X8,X12; w2,w6) has b output y and d output Y12", c0[1] == y and c0[3] == tr["Y12"])
        # Lemma K
        t.check("Lemma K: K3(IV3,IV7,IV3,11; w6,w7) = (S3', S7, S11', S15')",
                G(IV[3], IV[7], IV[3], 11, tr["w6"], tr["w7"]) == (tr["S3"], S[7], tr["S11"], tr["S15"]))
        # Lemma F, the three diagonal calls with the new inputs
        t.check("Lemma F: D1(S1,S6,S11',S12; w10,w11) = (X1', X6, X11, X12)",
                G(S[1], S[6], tr["S11"], S[12], tr["w10"], tr["w11"]) == (tr["X1"], X[6], X11, X[12]))
        t.check("Lemma F: D0(S0,S5,S10,S15'; w8,w9) = (X0, X5, alpha, X15)",
                G(S[0], S[5], S[10], tr["S15"], tr["w8"], tr["w9"]) == (tr["X0"], tr["X5"], alpha, X15))
        t.check("Lemma F: D3(S3',S4,S9,S14; w14,0) = (X3, X4, X9, X14)",
                G(tr["S3"], S[4], S[9], S[14], tr["w14"], 0) == (X3, X[4], X[9], X[14]))

        # the whole trial, forward
        words = list(w)
        for i in (6, 7, 8, 9, 10, 11, 14):
            words[i] = tr[f"w{i}"]
        A, B = to_messages(words)
        da, S_t, X_t, Y_t = hash2(A)
        db, S_tb, X_tb, Y_tb = hash2(B)
        if first is None:
            first = (nine, alpha, k, y, words, da, db)
        t.check("messages: 60 and 62 bytes, B ends in two zero bytes, word 15 zero",
                (len(A), len(B)) == (60, 62) and B[60:] == b"\0\0" and words[15] == 0)
        t.check("Lemma L: A and B have the same state S and the same state X after round 0", S_t == S_tb and X_t == X_tb)
        t.check("trial: S7 unchanged", S_t[7] == S[7])
        t.check("trial: S differs from the context only in S3, S11, S15",
                all(S_t[i] == S[i] for i in range(16) if i not in (3, 11, 15))
                and (S_t[3], S_t[11], S_t[15]) == (tr["S3"], tr["S11"], tr["S15"]))
        t.check("trial: every X word except X1 equals the context with the D0 family applied",
                all(X_t[i] == base_X[i] for i in range(16) if i != 1) and X_t[1] == tr["X1"])
        t.check("trial: X3, X7, X11, X15, w4, w13, w15 keep their pinned values",
                (X_t[3], X_t[7], X_t[11], X_t[15], words[4], words[13], words[15]) == (X3, X7, X11, X15, W4, W13, 0))
        diff_ctx = frozenset(i for i in range(16) if words[i] != w[i])
        diff_base = frozenset(i for i in range(16) if words[i] != base_w[i])
        t.check("trial: no message word outside w6..w11, w14 differs from the context", diff_ctx <= {6, 7, 8, 9, 10, 11, 14})
        t.check("trial: no message word outside w6..w11, w14 differs from the context with the D0 family applied",
                diff_base <= {6, 7, 8, 9, 10, 11, 14})
        changed_all += diff_base == {6, 7, 8, 9, 10, 11, 14}
        changed_sets[diff_base] = changed_sets.get(diff_base, 0) + 1
        t.check(f"trial: Y4 of A and of B is the class member, and its eta is {ETA_HEX}",
                Y_t[4] == y == Y_tb[4] and eta_of(Y_t[4]) == ETA)
        t.check("trial: Y12 of A is the Y12 of 6.1", Y_t[12] == tr["Y12"])
        t.check("Fact P in place: Y of A and B differ only in Y3, Y11, with the values of 3.2",
                all(Y_t[i] == Y_tb[i] for i in range(16) if i not in (3, 11))
                and (Y_t[3], Y_tb[3], Y_t[11], Y_tb[11]) == (Y3, Y3B, Y11, Y11B))
        t.check("theorem: digest words 0, 2, 5, 7 of A and B are equal", all(da[i] == db[i] for i in (0, 2, 5, 7)))

        # 6.2: the residual from E1 and E3 only, and the identities used by the early test
        w5, w5b, w12, w8 = words[5], (words[5] + DELTA) & M32, words[12], words[8]
        y1, y6, y12, y4, y9, y14 = Y_t[1], Y_t[6], Y_t[12], Y_t[4], Y_t[9], Y_t[14]
        pa, pb = G(y1, y6, Y11, y12, w12, w5), G(y1, y6, Y11B, y12, w12, w5b)
        qa, qb = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
        R = (pa[0] ^ qa[2] ^ pb[0] ^ qb[2], qa[0] ^ pa[2] ^ qb[0] ^ pb[2], qa[1] ^ pa[3] ^ qb[1] ^ pb[3], pa[1] ^ qa[3] ^ pb[1] ^ qb[3])
        t.check("6.2: R from E1 and E3 equals the XOR of digest words 1, 3, 4, 6", R == tuple(da[i] ^ db[i] for i in (1, 3, 4, 6)))
        a1 = (y1 + y6 + w12) & M32; d1 = ror(y12 ^ a1, 16)
        b1, b1b = ror(y6 ^ ((Y11 + d1) & M32), 12), ror(y6 ^ ((Y11B + d1) & M32), 12)
        a2, a2b = (a1 + b1 + w5) & M32, (a1 + b1b + w5b) & M32
        e1, e1b = (Y3 + y4) & M32, (Y3B + y4) & M32
        h1, h1b = ror(y14 ^ e1, 16), ror(y14 ^ e1b, 16)
        g1, g1b = (y9 + h1) & M32, (y9 + h1b) & M32
        f1, f1b = ror(y4 ^ g1, 12), ror(y4 ^ g1b, 12)
        t.check("6.3: h1' = h1 XOR eta and f1 XOR f1' = ROR(g1 XOR g1', 12)",
                h1b == h1 ^ ETA and f1 ^ f1b == ror(g1 ^ g1b, 12))
        tt = a2 ^ a2b
        t.check("Lemma E, the two identities of its proof: d2 XOR d2' = ROR(t,8) in E1, f2 XOR f2' = ROR(f1 XOR f1' XOR g2 XOR g2', 7) in E3",
                (a2, a2b) == (pa[0], pb[0]) and pa[3] ^ pb[3] == ror(tt, 8)
                and qa[1] ^ qb[1] == ror(f1 ^ f1b ^ qa[2] ^ qb[2], 7))
        early = f1 ^ f1b ^ tt ^ ror(tt, 1)
        t.check("Lemma E: residual words 1 and 3 both zero implies a zero early-test word (vacuous unless that occurs)",
                not (R[0] == 0 and R[2] == 0) or early == 0)
        # Lemma N: n = eps XOR ROL(beta XOR eps, 1) XOR eta from E1 alone equals D3 XOR ROL(D6, 8) of the two digests
        beta, eps = b1 ^ b1b, pa[2] ^ pb[2]
        word_n = eps ^ rol(beta ^ eps, 1) ^ ETA
        t.check("Lemma N: n from E1 alone equals D3 XOR ROL(D6, 8) of the two complete digests",
                word_n == (da[3] ^ db[3]) ^ rol(da[6] ^ db[6], 8) == R[1] ^ rol(R[3], 8))
        # Lemma A: z = a2 XOR d1 of C2 = G(X2, X6, X10, X14; w7, w0), evaluated forwards on the trial's state and words
        c2s = g_steps(X_t[2], X_t[6], X_t[10], X_t[14], words[7], words[0])
        z = c2s[4] ^ c2s[1]
        t.check("Lemma A (a): Y14 = ROR(z, 8) and ROL(h1, 24) = z XOR ROL(e1, 8)",
                Y_t[14] == ror(z, 8) == c2s[5] and rol(h1, 24) == z ^ rol(e1, 8) and h1 == qa_steps(Y3, y4, y9, y14, w8))
        on_h1 = rule_on_h1(h1)
        on_z = all((sum(z >> b & 1 for b in zb) & 1) == v for zb, v in Z_CONDITIONS)
        t.check("Lemma A (b), (c): rule A on h1, the conditions on z and the zero word of (c) say the same",
                on_h1 == on_z == ((((z ^ ((z >> 1) & A_S)) & A_ALL) ^ A_V) == 0))
        rule_passes += on_h1

        # the trial is the output of step S1 for its own nine words
        nine_t = [X_t[i] for i in (1, 2, 5, 6, 9, 10, 12, 13, 14)]
        X_s, S_s, w_s, _ = step_s1(*nine_t)
        t.check("remark: step S1 on the trial's nine state words returns the trial's words, S and X",
                w_s == words and S_s == S_t and X_s == X_t)

        # 6.4 step 1: the context's X1 does not matter, and its X5, X10 matter only through S5
        if n < 4000:
            other = list(nine); other[0] = rng.getrandbits(32)
            X_o, S_o, w_o, keep_o = step_s1(*other)
            tr_o = trial_6_1(X_o, S_o, w_o, keep_o, alpha, y)
            words_o = list(w_o)
            for i in (6, 7, 8, 9, 10, 11, 14):
                words_o[i] = tr_o[f"w{i}"]
            t.check("6.4: a context that differs only in X1 gives the same trial words (4000 trials)", words_o == words)
            x10 = rng.getrandbits(32)                 # another (X5, X10) with the same S5
            c = (x10 - X15) & M32
            other = list(nine); other[5] = x10; other[2] = ror(ror(S[5] ^ c, 12) ^ x10, 7)
            X_o, S_o, w_o, keep_o = step_s1(*other)
            tr_o = trial_6_1(X_o, S_o, w_o, keep_o, alpha, y)
            words_o = list(w_o)
            for i in (6, 7, 8, 9, 10, 11, 14):
                words_o[i] = tr_o[f"w{i}"]
            t.check("6.4: a context with another (X5, X10) and the same S5 gives the same trial words (4000 trials)",
                    S_o[5] == S[5] and words_o == words)

        if ref is not None and n < 2000:
            ra, rb = struct.unpack("<8I", ref(A, 2)), struct.unpack("<8I", ref(B, 2))
            t.check("forward compression of this script equals the organizer reference blake3(m, 2) (first 2000 trials)",
                    list(ra) == da and list(rb) == db)

    # distinctness inside one (context, alpha): all members give different Y4 and different messages
    nine = [rng.getrandbits(32) for _ in range(9)]
    alpha = rng.getrandbits(32)
    X, S, w, keep = step_s1(*nine)
    seen_y, seen_a = set(), set()
    for y in members:
        tr = trial_6_1(X, S, w, keep, alpha, y)
        words = list(w)
        for i in (6, 7, 8, 9, 10, 11, 14):
            words[i] = tr[f"w{i}"]
        A, _ = to_messages(words)
        _, _, _, Y_t = hash2(A)
        seen_y.add(Y_t[4]); seen_a.add(A)
    t.check(f"one context and alpha: the {size} members give {size} different Y4 and {size} different messages A",
            len(seen_y) == size == len(seen_a) and seen_y == member_set)

    ok = t.report()
    print(f"    Y4 values inside the class among the 200000 sampled: {inside}")
    print(f"    trials that satisfy rule A: {rule_passes} of {trials} (a share of 2^-{len(RULE)} is {trials / 2 ** len(RULE):.1f})")
    print(f"    trials in which all of w6..w11, w14 differ from the context with the D0 family applied: {changed_all} of {trials}")
    for s, c in sorted(changed_sets.items(), key=lambda kv: -kv[1])[:4]:
        print(f"      changed words {sorted(s)}: {c} trials")
    nine, alpha, k, y, words, da, db = first
    print("    first trial: nine words", " ".join(f"{v:08x}" for v in nine), f"alpha {alpha:08x} member {k} Y4 {y:08x}")
    print("      words of A:", " ".join(f"{v:08x}" for v in words))
    print("      digest xor:", " ".join(f"{a ^ b:08x}" for a, b in zip(da, db)))
    print("    organizer reference cross-check:", "used" if ref is not None else "not available")
    return ok


def part_b(count, ref):
    print(f"(b) {PROGRAM.name} of pkg5 through its stdin/stdout contract, {count} seeds per experiment")
    manifest = json.loads(MANIFEST.read_text())
    t = Tally()
    notes = []
    members = {member(k) for k in range(1 << len(CFREE))}
    for entry in manifest["experiments"]:
        name, event = entry["id"], entry["event"]
        request = {"schema_version": 1, "experiment_id": name, "target_profile": "blake3-r2-prefix-v1",
                   "event": event, "max_message_bytes": 4096,
                   "trials": [{"trial": i, "seed": hashlib.sha256(b"pkg5-host-%s-%d" % (name.encode(), i)).hexdigest()}
                              for i in range(count)]}
        payload = json.dumps(request, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        outs = [subprocess.run([sys.executable, "-B", "-s", str(PROGRAM)], input=payload, capture_output=True, check=True).stdout
                for _ in range(2)]
        t.check(f"{name}: output byte-identical on a second run", outs[0] == outs[1])
        result = json.loads(outs[0])
        mask, expected = int(event["mask_hex"], 16), int(event["expected_hex"], 16)
        tries, missing, full, seen, entered = [], 0, 0, set(), 0
        t.check(f"{name}: one row per requested trial, in order", [r["trial"] for r in result["trials"]] == list(range(count)))
        for row in result["trials"]:
            if row["message_a_hex"] is None:
                missing += 1
                continue
            A, B = bytes.fromhex(row["message_a_hex"]), bytes.fromhex(row["message_b_hex"])
            wa = struct.unpack("<16I", A + bytes(64 - len(A)))
            wb = struct.unpack("<16I", B + bytes(64 - len(B)))
            da, S_a, X_a, Y_a = hash2(A)
            db, S_b, X_b, Y_b = hash2(B)
            t.check(f"{name}: lengths 60 and 62, B ends in two zero bytes, A and B differ only in w4, w5",
                    (len(A), len(B)) == (60, 62) and B[60:] == b"\0\0"
                    and [i for i in range(16) if wa[i] != wb[i]] == [4, 5])
            t.check(f"{name}: pinned words and state (w4, w4', w13, w15, X3, X7, X11, X15)",
                    (wa[4], wb[4], wa[13], wa[15]) == (W4, W4B, W13, 0)
                    and (X_a[3], X_a[7], X_a[11], X_a[15]) == (X3, X7, X11, X15) and X_a == X_b)
            t.check(f"{name}: digest words 0, 2, 5, 7 equal", all(da[i] == db[i] for i in (0, 2, 5, 7)))
            t.check(f"{name}: Y4 in the class {ETA_HEX}", Y_a[4] in members and eta_of(Y_a[4]) == ETA and Y_a[4] == Y_b[4])
            digest_a = struct.pack("<8I", *da); digest_b = struct.pack("<8I", *db)
            t.check(f"{name}: the organizer's mask event holds",
                    (int.from_bytes(digest_a, "big") ^ int.from_bytes(digest_b, "big")) & mask == expected)
            X_s, S_s, w_s, _ = step_s1(*[X_a[i] for i in (1, 2, 5, 6, 9, 10, 12, 13, 14)])
            t.check(f"{name}: the pair is the output of steps S1 to S3 for its own nine state words", list(wa) == w_s)
            if ref is not None:
                t.check(f"{name}: digests equal the organizer reference blake3(m, 2)", ref(A, 2) == digest_a and ref(B, 2) == digest_b)
            if name == "residual-search":
                t.check(f"{name}: low byte of digest word 1 agrees", (da[1] ^ db[1]) & 0xFF == 0)
                obs = row["observations"]
                tries.append(obs["tries"])
                t.check(f"{name}: the counted batch reports the stage counts of the data module and 7 right lanes",
                        (obs["batch_stage_a_operations"], obs["batch_stage_a_loads"], obs["batch_stage_2_operations"],
                         obs["batch_stage_2_loads"], obs["batch_lanes_right"]) ==
                        (pkg5_data.STAGE_A_OPS, pkg5_data.STAGE_A_LOADS, pkg5_data.STAGE_2_OPS, pkg5_data.STAGE_2_LOADS, 7))
                entered += obs["batch_stage_2_entered"]
            full += da == db
            seen.add(A)
        t.check(f"{name}: every seed returned a pair", missing == 0)
        t.check(f"{name}: all returned messages A are different", len(seen) == count - missing)
        line = f"    {name}: pairs {count - missing} of {count}, full collisions {full}, {len(outs[0])} bytes of output"
        if tries:
            line += (f", members tried: mean {sum(tries) / len(tries):.1f}, max {max(tries)}; counted batches in which a lane "
                     f"satisfies rule A: {entered} of {len(tries)}")
        notes.append(line)
    ok = t.report()
    for line in notes:
        print(line)
    return ok


def main():
    trials = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 256
    assert trials >= 10000, "at least 10000 trials"
    rng = random.Random(20261005)
    ref = reference()
    ok_a = part_a(trials, rng, ref)
    ok_b = part_b(count, ref)
    if ok_a and ok_b:
        print("RESULT: all checks passed")
        return 0
    print("RESULT: FAILED:", "; ".join(FAILS))
    return 1


if __name__ == "__main__":
    sys.exit(main())
