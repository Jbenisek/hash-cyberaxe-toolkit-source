#!/usr/bin/env python3
"""Numerical check of the sixth blake3-r2 package (lengths 55 and 63, pin H8, two-stage batch). Research helper, not submitted.

Part (a) writes the formulas of the family (step S1: the fifty lines of the context; 6.1: the forty-six lines of
the trial) a second time, name by name in the order of research/h8/design/DESIGN.txt, and compares them on random
trials with a plain forward 2-round BLAKE3 compression that is also written here. Nothing of the package's
experiment program is used in part (a). The six constants, the two lengths, eta and the conditions of rule A are
taken from tools/pkg6_data.py, the one place that holds them; everything else is computed here. The length
cancellation, the pinned call, the class, Lemma N and Lemma A are checked on every random trial against the forward
compression.

Part (b) runs pkg6/blake3-r2/experiments/halfsearch.py through its stdin/stdout contract and checks the returned
message pairs with the same forward compression.

Part (c) reads proof.md and looks for the constants that this script computes, in the form in which the proof
prints them, and evaluates the solutions of the seven-word system that Section 10 prints, if it prints any.

    python -B check_pkg6.py [trials, default 20000] [experiment trials, default 256] [--program | --text]

--program leaves part (c) out; --text runs part (c) alone. Exit status 0 only if every check that was run holds.
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
import pkg6_data  # noqa: E402  (PIN, LEN_A, LEN_B, ETA, RULE_A and, for part (b), the stage counts are taken from it)

M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8)
X3, X7, X11, X15, W4, W13 = (pkg6_data.PIN[k] for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
LEN_A, LEN_B = pkg6_data.LEN_A, pkg6_data.LEN_B
LEN_XOR = LEN_A ^ LEN_B
ETA = pkg6_data.ETA
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
    """Plain forward compression. Returns digest words and the states S, X, Y."""
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


# ---------------------------------------------------------------- the formulas of the family, written again
K = (IV[2] + IV[6]) & M32
W4B = ((((K + W4) & M32) ^ LEN_XOR) - K) & M32
DELTA = (W4 - W4B) & M32
Y3, _, Y11, _ = G(X3, X7, X11, X15, W4, W13)
Y3B, _, Y11B, _ = G(X3, X7, X11, X15, W4B, W13)
D3 = (Y3B - Y3) & M32


def g_steps(A, B, C, D, x, y):
    """The eight assignments of one G call, in the order a1, d1, c1, b1, a2, d2, c2, b2."""
    a1 = (A + B + x) & M32; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M32; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
    return a1, d1, c1, b1, a2, d2, c2, b2


CONTEXT_WORDS = ("C0.c1", "C0.d1", "S11", "S4", "X13", "X14", "w0")
# the names that step S1 computes without reading X14 (31), and those that read it (19)
OUTER = ("K0.a1", "X8", "K0.d1", "K0.c1", "K0.b1", "S8", "D2.c1", "D2.d1", "D2.b1", "S7", "X2", "K3.b1", "K3.c1", "K2.a1",
         "K3.d1", "S15", "K2.d1", "S3", "K2.c1", "D3.a1", "K2.b1", "D2.a1", "D3.b1", "S13", "D3.c1", "K3.a1", "w6", "w7",
         "S12", "S0", "w1")
MIDDLE = ("D3.d1", "S9", "K1.c1", "S14", "K1.d1", "S10", "X9", "K1.a1", "X4", "w2", "S6", "C0.b1", "K1.b1", "S2", "S1",
          "S5", "w12", "w3", "w5")


def step_s1(c0c1, c0d1, s11, s4, x13, x14, w0):
    """The fifty lines of the context, in the order of DESIGN.txt section 4. Returns the dict of every name."""
    v = {"C0.c1": c0c1, "C0.d1": c0d1, "S11": s11, "S4": s4, "X13": x13, "X14": x14, "w0": w0,
         "X3": X3, "X7": X7, "X11": X11, "X15": X15, "w4": W4, "w13": W13, "w14": 0, "w15": 0}
    v["K0.a1"] = (IV[0] + IV[4] + v["w0"]) & M32
    v["X8"] = (v["C0.c1"] - v["C0.d1"]) & M32
    v["K0.d1"] = ror(0 ^ v["K0.a1"], 16)
    v["K0.c1"] = (IV[0] + v["K0.d1"]) & M32
    v["K0.b1"] = ror(IV[4] ^ v["K0.c1"], 12)
    v["S8"] = rol(v["S4"], 7) ^ v["K0.b1"]
    v["D2.c1"] = (v["X8"] - v["X13"]) & M32
    v["D2.d1"] = (v["D2.c1"] - v["S8"]) & M32
    v["D2.b1"] = rol(X7, 7) ^ v["X8"]
    v["S7"] = rol(v["D2.b1"], 12) ^ v["D2.c1"]
    v["X2"] = rol(v["X13"], 8) ^ v["D2.d1"]
    v["K3.b1"] = rol(v["S7"], 7) ^ v["S11"]
    v["K3.c1"] = rol(v["K3.b1"], 12) ^ IV[7]
    v["K2.a1"] = (IV[2] + IV[6] + W4) & M32
    v["K3.d1"] = (v["K3.c1"] - IV[3]) & M32
    v["S15"] = (v["S11"] - v["K3.c1"]) & M32
    v["K2.d1"] = ror(LEN_A ^ v["K2.a1"], 16)
    v["S3"] = rol(v["S15"], 8) ^ v["K3.d1"]
    v["K2.c1"] = (IV[2] + v["K2.d1"]) & M32
    v["D3.a1"] = (v["S3"] + v["S4"] + v["w14"]) & M32
    v["K2.b1"] = ror(IV[6] ^ v["K2.c1"], 12)
    v["D2.a1"] = (v["X2"] - v["D2.b1"] - W13) & M32
    v["D3.b1"] = (X3 - v["D3.a1"] - v["w15"]) & M32
    v["D3.d1"] = rol(v["X14"], 8) ^ X3
    v["S13"] = rol(v["D2.d1"], 16) ^ v["D2.a1"]
    v["D3.c1"] = rol(v["D3.b1"], 12) ^ v["S4"]
    v["K3.a1"] = rol(v["K3.d1"], 16) ^ 11
    v["S9"] = (v["D3.c1"] - v["D3.d1"]) & M32
    v["K1.c1"] = (v["S9"] - v["S13"]) & M32
    v["w6"] = (v["K3.a1"] - IV[3] - IV[7]) & M32
    v["S14"] = rol(v["D3.d1"], 16) ^ v["D3.a1"]
    v["K1.d1"] = (v["K1.c1"] - IV[1]) & M32
    v["S10"] = (v["K2.c1"] + v["S14"]) & M32
    v["X9"] = (v["D3.c1"] + v["X14"]) & M32
    v["K1.a1"] = rol(v["K1.d1"], 16) ^ 0
    v["X4"] = ror(v["D3.b1"] ^ v["X9"], 7)
    v["w2"] = (v["K1.a1"] - IV[1] - IV[5]) & M32
    v["S6"] = ror(v["K2.b1"] ^ v["S10"], 7)
    v["C0.b1"] = ror(v["X4"] ^ v["C0.c1"], 12)
    v["w7"] = (v["S3"] - v["K3.a1"] - v["K3.b1"]) & M32
    v["S12"] = (v["S8"] - v["K0.c1"]) & M32
    v["K1.b1"] = ror(IV[5] ^ v["K1.c1"], 12)
    v["S2"] = rol(v["S14"], 8) ^ v["K2.d1"]
    v["S1"] = rol(v["S13"], 8) ^ v["K1.d1"]
    v["S5"] = ror(v["K1.b1"] ^ v["S9"], 7)
    v["w12"] = (v["D2.a1"] - v["S2"] - v["S7"]) & M32
    v["w3"] = (v["S1"] - v["K1.a1"] - v["K1.b1"]) & M32
    v["S0"] = rol(v["S12"], 8) ^ v["K0.d1"]
    v["w1"] = (v["S0"] - v["K0.a1"] - v["K0.b1"]) & M32
    v["w5"] = (v["S2"] - v["K2.a1"] - v["K2.b1"]) & M32
    return v


def trial_6_1(v, y):
    """The forty-six lines of the trial, in the order of DESIGN.txt section 5. Returns a dict of what they define."""
    t = {"Y4": y}
    t["Y8"] = rol(y, 7) ^ v["C0.b1"]
    t["Y12"] = (t["Y8"] - v["C0.c1"]) & M32
    t["Y0"] = rol(t["Y12"], 8) ^ v["C0.d1"]
    t["C0.a1"] = (t["Y0"] - v["C0.b1"] - v["w6"]) & M32
    t["X0"] = (t["C0.a1"] - v["X4"] - v["w2"]) & M32
    t["X12"] = rol(v["C0.d1"], 16) ^ t["C0.a1"]
    t["D0.d1"] = rol(X15, 8) ^ t["X0"]
    t["D1.c1"] = (X11 - t["X12"]) & M32
    t["D0.c1"] = (v["S10"] + t["D0.d1"]) & M32
    t["D1.b1"] = ror(v["S6"] ^ t["D1.c1"], 12)
    t["X10"] = (t["D0.c1"] + X15) & M32
    t["X6"] = ror(t["D1.b1"] ^ X11, 7)
    t["C2.a1"] = (v["X2"] + t["X6"] + v["w7"]) & M32
    t["D1.d1"] = (t["D1.c1"] - v["S11"]) & M32
    t["C2.d1"] = ror(v["X14"] ^ t["C2.a1"], 16)
    t["X1"] = rol(t["X12"], 8) ^ t["D1.d1"]
    t["C2.c1"] = (t["X10"] + t["C2.d1"]) & M32
    t["C2.b1"] = ror(t["X6"] ^ t["C2.c1"], 12)
    t["Y2"] = (t["C2.a1"] + t["C2.b1"] + v["w0"]) & M32
    t["Y14"] = ror(t["C2.d1"] ^ t["Y2"], 8)
    t["E3.h1"] = ror(t["Y14"] ^ ((Y3 + y + v["w15"]) & M32), 16)
    t["D1.a1"] = rol(t["D1.d1"], 16) ^ v["S12"]
    t["D0.b1"] = ror(v["S5"] ^ t["D0.c1"], 12)
    t["w10"] = (t["D1.a1"] - v["S1"] - v["S6"]) & M32
    t["X5"] = ror(t["D0.b1"] ^ t["X10"], 7)
    t["C1.a1"] = (t["X1"] + t["X5"] + v["w3"]) & M32
    t["C1.d1"] = ror(v["X13"] ^ t["C1.a1"], 16)
    t["C1.c1"] = (v["X9"] + t["C1.d1"]) & M32
    t["C1.b1"] = ror(t["X5"] ^ t["C1.c1"], 12)
    t["Y1"] = (t["C1.a1"] + t["C1.b1"] + t["w10"]) & M32
    t["Y13"] = ror(t["C1.d1"] ^ t["Y1"], 8)
    t["Y9"] = (t["C1.c1"] + t["Y13"]) & M32
    t["Y10"] = (t["C2.c1"] + t["Y14"]) & M32
    t["E3.g1"] = (t["Y9"] + t["E3.h1"]) & M32
    t["Y6"] = ror(t["C2.b1"] ^ t["Y10"], 7)
    t["E1.a1"] = (t["Y1"] + t["Y6"] + v["w12"]) & M32
    t["D0.a1"] = rol(t["D0.d1"], 16) ^ v["S15"]
    t["E1.d1"] = ror(t["Y12"] ^ t["E1.a1"], 16)
    t["w8"] = (t["D0.a1"] - v["S0"] - v["S5"]) & M32
    t["w9"] = (t["X0"] - t["D0.a1"] - t["D0.b1"]) & M32
    t["E1.b1"] = ror(t["Y6"] ^ ((Y11 + t["E1.d1"]) & M32), 12)
    t["E3.f1"] = ror(y ^ t["E3.g1"], 12)
    t["w11"] = (t["X1"] - t["D1.a1"] - t["D1.b1"]) & M32
    t["Y5"] = ror(t["C1.b1"] ^ t["Y9"], 7)
    t["E1.a2"] = (t["E1.a1"] + t["E1.b1"] + v["w5"]) & M32
    t["E3.e2"] = (((Y3 + y + v["w15"]) & M32) + t["E3.f1"] + t["w8"]) & M32
    return t


def words_of(v, t):
    """The sixteen message words of a trial: twelve from the context, w8..w11 from the trial."""
    return [t[f"w{i}"] if 8 <= i <= 11 else v[f"w{i}"] for i in range(16)]


def class_of_eta():
    """Lemma Q: mask and value of the fixed bits of e1 = Y3 + Y4."""
    x = rol(ETA, 16)
    v = (D3 + x) & M32
    assert v % 2 == 0 and (v >> 1) & ~x & M32 == 0, "the class is empty"
    mask = x & 0x7FFFFFFF
    return mask, ~(v >> 1) & mask


CMASK, CVALUE = class_of_eta()
CFREE = [i for i in range(32) if not CMASK >> i & 1]
RULE = pkg6_data.RULE_A[ETA]


def rule_on_h1(h1):
    """Rule A as stated on h1: for every condition, the XOR of the named bits of h1 has the stated value."""
    return all(bin(h1 & mask).count("1") & 1 == value for mask, value in RULE)


def rule_on_z():
    """Lemma A (b), (c), derived here: [(bits of z, wanted XOR)], the shifts {distance: mask} and the constants ALL, V."""
    conditions, shifts, everything, v = [], {}, 0, 0
    for mask, value in RULE:
        hbits = [i for i in range(32) if mask >> i & 1]
        for i in hbits:                                # bit i of h1 = bit (i + 24) of z XOR bit (i + 16) of e1
            e = (i + 16) % 32
            assert CMASK >> e & 1, "rule A meets a free bit of e1"
            value ^= CVALUE >> e & 1
        zbits = sorted((i + 24) % 32 for i in hbits)
        conditions.append((zbits, value))
        assert len(zbits) in (1, 2) and not everything >> zbits[0] & 1
        if len(zbits) == 2:
            shifts[zbits[1] - zbits[0]] = shifts.get(zbits[1] - zbits[0], 0) | 1 << zbits[0]
        everything |= 1 << zbits[0]
        v |= value << zbits[0]
    return conditions, shifts, everything, v


Z_CONDITIONS, A_SHIFTS, A_ALL, A_V = rule_on_z()


def zero_word_of_rule(z):
    """The word of Lemma A (c) for one z: zero exactly when the conditions on z hold."""
    y = z
    for distance, mask in A_SHIFTS.items():
        y ^= (z >> distance) & mask
    return (y & A_ALL) ^ A_V


def member(k):
    e1 = CVALUE
    for j, i in enumerate(CFREE):
        e1 |= (k >> j & 1) << i
    return (e1 - Y3) & M32


def eta_of(y4):
    e1 = (Y3 + y4) & M32
    return ror(e1 ^ ((Y3B + y4) & M32), 16)


def to_messages(words):
    other = list(words)
    other[4] = W4B
    other[5] = (words[5] + DELTA) & M32
    return struct.pack("<16I", *words)[:LEN_A], struct.pack("<16I", *other)[:LEN_B]


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
    print(f"(a) formulas of the family against a forward 2-round compression, {trials} random trials")
    print(f"    constants: Y3 {Y3:08x} Y3' {Y3B:08x} Y11 {Y11:08x} Y11' {Y11B:08x} D3 {D3:08x} W4' {W4B:08x} delta {DELTA:08x}")
    print(f"    class eta {ETA:08x}: ROL(eta,16) {rol(ETA, 16):08x}, D3 + ROL(eta,16) {(D3 + rol(ETA, 16)) & M32:08x}, "
          f"mask {CMASK:08x}, value {CVALUE:08x}, {len(CFREE)} free bits, {1 << len(CFREE)} members")
    t = Tally()

    # Lemma Q: membership formula against the definition of eta
    members = [member(k) for k in range(1 << len(CFREE))]
    size = len(members)
    member_set = set(members)
    t.check(f"Lemma Q: all {size} enumerated members are distinct", len(member_set) == size == 1 << len(CFREE))
    t.check(f"Lemma Q: every enumerated member has eta = {ETA_HEX}", all(eta_of(y) == ETA for y in members))
    s = (D3 + rol(ETA, 16)) & M32
    sa, sb = g_steps(X3, X7, X11, X15, W4, W13), g_steps(X3, X7, X11, X15, W4B, W13)
    t.check("the pinned call: the two executions agree in b and d and differ in a and c",
            sa[5] == sb[5] and sa[7] == sb[7] and sa[4] != sb[4] and sa[6] != sb[6])
    t.check("W4' = ((K + W4) XOR (55 XOR 63)) - K, W4 - W4' is plus or minus 8 modulo 2^32, and the top byte of W13 is zero",
            (LEN_A, LEN_B, LEN_XOR) == (55, 63, 8) and DELTA in (LEN_XOR, -LEN_XOR & M32) and W13 >> 24 == 0
            and ((K + W4B) & M32) == ((K + W4) & M32) ^ LEN_XOR)
    t.check("Lemma Q: the fixed bits of D3 + x lie in m, D3 + x is even, bit 31 of e1 is free",
            s % 2 == 0 and (s >> 1) & ~CMASK & M32 == 0 and 31 in CFREE)
    t.check("Lemma A: every bit of e1 that rule A meets is fixed by the class, and no two conditions share a position of z",
            all(CMASK >> ((i + 16) % 32) & 1 for mask, _ in RULE for i in range(32) if mask >> i & 1)
            and len({zb[0] for zb, _ in Z_CONDITIONS}) == len(RULE))
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
    first = None
    rule_passes = 0
    moved = {}
    for n in range(trials):
        seven = [rng.getrandbits(32) for _ in range(7)]
        if n % 16 == 0:                               # extreme words now and then
            seven = [rng.choice((0, M32, x)) for x in seven]
        k = rng.randrange(size)
        y = members[k]
        v = step_s1(*seven)
        tr = trial_6_1(v, y)
        words = words_of(v, tr)
        A, B = to_messages(words)
        da, S_t, X_t, Y_t = hash2(A)
        db, S_tb, X_tb, Y_tb = hash2(B)
        wa = list(struct.unpack("<16I", A + bytes(64 - len(A))))
        wb = list(struct.unpack("<16I", B + bytes(64 - len(B))))
        if first is None:
            first = (seven, k, y, words, da, db)

        t.check("messages: 55 and 63 bytes, B ends in eight zero bytes, w14 = w15 = 0, top byte of w13 zero",
                (len(A), len(B)) == (55, 63) and B[55:] == bytes(8) and words[14] == 0 == words[15] and words[13] >> 24 == 0)
        t.check("messages: the 55 bytes of A hold the sixteen words of the trial; B differs from A only in w4, w5",
                wa == words and [i for i in range(16) if wa[i] != wb[i]] == [4, 5] and wb[4] == W4B
                and wb[5] == (wa[5] + DELTA) & M32)
        # step S1 and the trial, by running round 0 forward on the trial's words with length 55
        t.check("step S1: round 0 of the trial's words gives the sixteen words S of the context",
                S_t == [v[f"S{i}"] for i in range(16)])
        t.check("step S1: X2, X4, X8, X9 are those of the context and X3, X7, X11, X13, X14, X15 the given ones",
                [X_t[i] for i in (2, 4, 8, 9, 3, 7, 11, 13, 14, 15)] == [v[f"X{i}"] for i in (2, 4, 8, 9, 3, 7, 11, 13, 14, 15)])
        t.check("6.1: X0, X1, X5, X6, X10, X12 after round 0 are those of the trial",
                [X_t[i] for i in (0, 1, 5, 6, 10, 12)] == [tr[f"X{i}"] for i in (0, 1, 5, 6, 10, 12)])
        t.check("trial: X3, X7, X11, X15, w4, w13, w14, w15 keep their pinned values",
                (X_t[3], X_t[7], X_t[11], X_t[15], words[4], words[13], words[14], words[15]) == (X3, X7, X11, X15, W4, W13, 0, 0))
        # every call of round 0 with the names of the lines
        t.check("round 0, columns: K0, K1, K2 (length 55), K3 have the first halves and the outputs of step S1",
                g_steps(IV[0], IV[4], IV[0], 0, words[0], words[1])
                == (v["K0.a1"], v["K0.d1"], v["K0.c1"], v["K0.b1"], v["S0"], v["S12"], v["S8"], v["S4"])
                and g_steps(IV[1], IV[5], IV[1], 0, words[2], words[3])
                == (v["K1.a1"], v["K1.d1"], v["K1.c1"], v["K1.b1"], v["S1"], v["S13"], v["S9"], v["S5"])
                and g_steps(IV[2], IV[6], IV[2], LEN_A, words[4], words[5])
                == (v["K2.a1"], v["K2.d1"], v["K2.c1"], v["K2.b1"], v["S2"], v["S14"], v["S10"], v["S6"])
                and g_steps(IV[3], IV[7], IV[3], 11, words[6], words[7])
                == (v["K3.a1"], v["K3.d1"], v["K3.c1"], v["K3.b1"], v["S3"], v["S15"], v["S11"], v["S7"]))
        t.check("round 0, diagonals: D2(S2,S7,S8,S13; w12,w13) = (X2, X7, X8, X13) and D3(S3,S4,S9,S14; 0,0) = (X3, X4, X9, X14), "
                "with the first halves of step S1",
                g_steps(v["S2"], v["S7"], v["S8"], v["S13"], words[12], words[13])
                == (v["D2.a1"], v["D2.d1"], v["D2.c1"], v["D2.b1"], v["X2"], v["X13"], v["X8"], X7)
                and g_steps(v["S3"], v["S4"], v["S9"], v["S14"], 0, 0)
                == (v["D3.a1"], v["D3.d1"], v["D3.c1"], v["D3.b1"], X3, v["X14"], v["X9"], v["X4"]))
        t.check("round 0, diagonals: D0(S0,S5,S10,S15; w8,w9) = (X0, X5, X10, X15) and D1(S1,S6,S11,S12; w10,w11) = "
                "(X1, X6, X11, X12), with the first halves of 6.1",
                g_steps(v["S0"], v["S5"], v["S10"], v["S15"], tr["w8"], tr["w9"])
                == (tr["D0.a1"], tr["D0.d1"], tr["D0.c1"], tr["D0.b1"], tr["X0"], X15, tr["X10"], tr["X5"])
                and g_steps(v["S1"], v["S6"], v["S11"], v["S12"], tr["w10"], tr["w11"])
                == (tr["D1.a1"], tr["D1.d1"], tr["D1.c1"], tr["D1.b1"], tr["X1"], tr["X12"], X11, tr["X6"]))
        # round 1, columns
        c0 = g_steps(tr["X0"], v["X4"], v["X8"], tr["X12"], words[2], words[6])
        t.check("C0(X0,X4,X8,X12; w2,w6): first half (C0.a1, C0.d1, C0.c1, C0.b1) of the context and 6.1, outputs "
                "(Y0, Y4 = y, Y8, Y12)",
                c0 == (tr["C0.a1"], v["C0.d1"], v["C0.c1"], v["C0.b1"], tr["Y0"], tr["Y12"], tr["Y8"], y))
        c1 = g_steps(tr["X1"], tr["X5"], v["X9"], v["X13"], words[3], words[10])
        c2 = g_steps(v["X2"], tr["X6"], tr["X10"], v["X14"], words[7], words[0])
        t.check("C1(X1,X5,X9,X13; w3,w10) and C2(X2,X6,X10,X14; w7,w0): first halves and outputs of 6.1",
                c1 == (tr["C1.a1"], tr["C1.d1"], tr["C1.c1"], tr["C1.b1"], tr["Y1"], tr["Y13"], tr["Y9"], tr["Y5"])
                and c2[:5] == (tr["C2.a1"], tr["C2.d1"], tr["C2.c1"], tr["C2.b1"], tr["Y2"])
                and (c2[5], c2[6], c2[7]) == (tr["Y14"], tr["Y10"], tr["Y6"]))
        t.check("the state Y of A after the columns of round 1 is that of 6.1 (Y0, Y1, Y2, Y4, Y5, Y6, Y8, Y9, Y10, Y12, Y13, Y14)",
                all(Y_t[i] == tr[f"Y{i}"] for i in (0, 1, 2, 4, 5, 6, 8, 9, 10, 12, 13, 14)))
        t.check("length cancellation: A (length 55) and B (length 63) have the same state S and the same state X after round 0",
                S_t == S_tb and X_t == X_tb)
        t.check(f"trial: Y4 of A and of B is the class member, and its eta is {ETA_HEX}",
                Y_t[4] == y == Y_tb[4] and eta_of(Y_t[4]) == ETA)
        t.check("the pinned call in place: Y of A and B differ only in Y3, Y11, with the values of the pin",
                all(Y_t[i] == Y_tb[i] for i in range(16) if i not in (3, 11))
                and (Y_t[3], Y_tb[3], Y_t[11], Y_tb[11]) == (Y3, Y3B, Y11, Y11B))
        t.check("theorem: digest words 0, 2, 5, 7 of A and B are equal", all(da[i] == db[i] for i in (0, 2, 5, 7)))

        # 6.2: the residual from E1 and E3 only, and the identities used by the tests
        w5, w5b, w12, w8 = words[5], (words[5] + DELTA) & M32, words[12], words[8]
        y1, y6, y12, y4, y9, y14 = Y_t[1], Y_t[6], Y_t[12], Y_t[4], Y_t[9], Y_t[14]
        pa, pb = G(y1, y6, Y11, y12, w12, w5), G(y1, y6, Y11B, y12, w12, w5b)
        qa, qb = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
        R = (pa[0] ^ qa[2] ^ pb[0] ^ qb[2], qa[0] ^ pa[2] ^ qb[0] ^ pb[2], qa[1] ^ pa[3] ^ qb[1] ^ pb[3], pa[1] ^ qa[3] ^ pb[1] ^ qb[3])
        t.check("6.2: R from E1 and E3 equals the XOR of digest words 1, 3, 4, 6", R == tuple(da[i] ^ db[i] for i in (1, 3, 4, 6)))
        e1s = g_steps(y1, y6, Y11, y12, w12, w5)
        e3s = g_steps(Y3, y4, y9, y14, 0, w8)
        t.check("6.1, last lines: E1.a1, E1.d1, E1.b1, E1.a2 and E3.h1, E3.g1, E3.f1, E3.e2 are the values of E1 and E3 on A",
                (e1s[0], e1s[1], e1s[3], e1s[4]) == (tr["E1.a1"], tr["E1.d1"], tr["E1.b1"], tr["E1.a2"])
                and (e3s[1], e3s[2], e3s[3], e3s[4]) == (tr["E3.h1"], tr["E3.g1"], tr["E3.f1"], tr["E3.e2"]))
        a1 = (y1 + y6 + w12) & M32; d1 = ror(y12 ^ a1, 16)
        b1, b1b = ror(y6 ^ ((Y11 + d1) & M32), 12), ror(y6 ^ ((Y11B + d1) & M32), 12)
        a2, a2b = (a1 + b1 + w5) & M32, (a1 + b1b + w5b) & M32
        e1, e1b = (Y3 + y4) & M32, (Y3B + y4) & M32
        h1, h1b = ror(y14 ^ e1, 16), ror(y14 ^ e1b, 16)
        g1, g1b = (y9 + h1) & M32, (y9 + h1b) & M32
        f1, f1b = ror(y4 ^ g1, 12), ror(y4 ^ g1b, 12)
        t.check("6.3: h1' = h1 XOR eta and f1 XOR f1' = ROR(g1 XOR g1', 12)",
                h1b == h1 ^ ETA and f1 ^ f1b == ror(g1 ^ g1b, 12) and h1 == tr["E3.h1"])
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
                Y_t[14] == ror(z, 8) == c2s[5] and rol(h1, 24) == z ^ rol(e1, 8))
        on_h1 = rule_on_h1(h1)
        on_z = all((sum(z >> b & 1 for b in zb) & 1) == val for zb, val in Z_CONDITIONS)
        t.check("Lemma A (b), (c): rule A on h1, the conditions on z and the zero word of (c) say the same",
                on_h1 == on_z == (zero_word_of_rule(z) == 0))
        rule_passes += on_h1

        # the trial is the output of step S1 and 6.1 for its own seven words and its own Y4
        seven_t = [c0[2], c0[1], S_t[11], S_t[4], X_t[13], X_t[14], wa[0]]
        v_s = step_s1(*seven_t)
        t.check("remark: step S1 and 6.1 on the trial's own seven words and Y4, read off its forward computation, "
                "return the trial's words", seven_t == seven and words_of(v_s, trial_6_1(v_s, Y_t[4])) == words)

        # the loop structure: what changes with X14 alone, and what changes with the member alone
        if n < 4000:
            other = list(seven); other[5] = rng.getrandbits(32)
            v_o = step_s1(*other)
            t.check("loop structure: a context that differs only in X14 has the same 31 values that step S1 computes "
                    "without X14 (4000 trials)", all(v_o[name] == v[name] for name in OUTER))
            for name in MIDDLE:
                moved[name] = moved.get(name, 0) + (v_o[name] != v[name])
            y_o = members[rng.randrange(size)]
            words_o = words_of(v, trial_6_1(v, y_o))
            t.check("loop structure: two members of one context differ in no message word outside w8..w11 (4000 trials)",
                    all(words_o[i] == words[i] for i in range(16) if not 8 <= i <= 11))

        if ref is not None and n < 2000:
            ra, rb = struct.unpack("<8I", ref(A, 2)), struct.unpack("<8I", ref(B, 2))
            t.check("forward compression of this script equals the organizer reference blake3(m, 2) (first 2000 trials)",
                    list(ra) == da and list(rb) == db)

    t.check("the names OUTER and MIDDLE are the fifty names of step S1", len(OUTER) == 31 and len(MIDDLE) == 19
            and set(OUTER) | set(MIDDLE) | set(CONTEXT_WORDS) | {"X3", "X7", "X11", "X15", "w4", "w13", "w14", "w15"}
            == set(step_s1(*[0] * 7)))
    # distinctness inside one context: all members give different Y4 (C0 forwards) and different messages A
    seven = [rng.getrandbits(32) for _ in range(7)]
    v = step_s1(*seven)
    seen_y, seen_a = set(), set()
    for y in members:
        tr = trial_6_1(v, y)
        words = words_of(v, tr)
        seen_y.add(G(tr["X0"], v["X4"], v["X8"], tr["X12"], words[2], words[6])[1])
        seen_a.add(to_messages(words)[0])
    t.check(f"one context: the {size} members give {size} different Y4 (b output of C0) and {size} different messages A",
            len(seen_y) == size == len(seen_a) and seen_y == member_set)

    ok = t.report()
    print(f"    Y4 values inside the class among the 200000 sampled: {inside}")
    print(f"    trials that satisfy rule A: {rule_passes} of {trials} (a share of 2^-{len(RULE)} is {trials / 2 ** len(RULE):.1f})")
    print(f"    of the 19 values that read X14, changed by a new X14 in 4000 trials: fewest {min(moved.values())} "
          f"({min(moved, key=moved.get)}), most {max(moved.values())}")
    seven, k, y, words, da, db = first
    print("    first trial: seven words", " ".join(f"{x:08x}" for x in seven), f"member {k} Y4 {y:08x}")
    print("      words of A:", " ".join(f"{x:08x}" for x in words))
    print("      digest xor:", " ".join(f"{a ^ b:08x}" for a, b in zip(da, db)))
    print("    organizer reference cross-check:", "used" if ref is not None else "not available")
    return ok


def part_b(count, ref):
    print(f"(b) {PROGRAM.name} of pkg6 through its stdin/stdout contract, {count} seeds per experiment")
    manifest = json.loads(MANIFEST.read_text())
    t = Tally()
    notes = []
    members = {member(k) for k in range(1 << len(CFREE))}
    for entry in manifest["experiments"]:
        name, event = entry["id"], entry["event"]
        request = {"schema_version": 1, "experiment_id": name, "target_profile": "blake3-r2-prefix-v1",
                   "event": event, "max_message_bytes": 4096,
                   "trials": [{"trial": i, "seed": hashlib.sha256(b"pkg6-host-%s-%d" % (name.encode(), i)).hexdigest()}
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
            t.check(f"{name}: lengths 55 and 63, B ends in eight zero bytes, A and B differ only in w4, w5",
                    (len(A), len(B)) == (55, 63) and B[55:] == bytes(8)
                    and [i for i in range(16) if wa[i] != wb[i]] == [4, 5])
            t.check(f"{name}: pinned words and state (w4, w4', w13, w14, w15, X3, X7, X11, X15)",
                    (wa[4], wb[4], wa[13], wa[14], wa[15]) == (W4, W4B, W13, 0, 0)
                    and (X_a[3], X_a[7], X_a[11], X_a[15]) == (X3, X7, X11, X15) and X_a == X_b)
            t.check(f"{name}: digest words 0, 2, 5, 7 equal", all(da[i] == db[i] for i in (0, 2, 5, 7)))
            t.check(f"{name}: Y4 in the class {ETA_HEX}", Y_a[4] in members and eta_of(Y_a[4]) == ETA and Y_a[4] == Y_b[4])
            digest_a = struct.pack("<8I", *da); digest_b = struct.pack("<8I", *db)
            t.check(f"{name}: the organizer's mask event holds",
                    (int.from_bytes(digest_a, "big") ^ int.from_bytes(digest_b, "big")) & mask == expected)
            c0 = g_steps(X_a[0], X_a[4], X_a[8], X_a[12], wa[2], wa[6])
            v_s = step_s1(c0[2], c0[1], S_a[11], S_a[4], X_a[13], X_a[14], wa[0])
            t.check(f"{name}: the pair is the output of step S1 and 6.1 for its own seven words and Y4",
                    list(wa) == words_of(v_s, trial_6_1(v_s, Y_a[4])))
            if ref is not None:
                t.check(f"{name}: digests equal the organizer reference blake3(m, 2)", ref(A, 2) == digest_a and ref(B, 2) == digest_b)
            if name == "residual-search":
                t.check(f"{name}: low byte of digest word 1 agrees", (da[1] ^ db[1]) & 0xFF == 0)
                obs = row["observations"]
                tries.append(obs["tries"])
                t.check(f"{name}: the counted batch reports the stage counts of the data module and 7 right lanes",
                        (obs["batch_stage_a_operations"], obs["batch_stage_a_loads"], obs["batch_stage_2_operations"],
                         obs["batch_stage_2_loads"], obs["batch_lanes_right"]) ==
                        (pkg6_data.STAGE_A_OPS, pkg6_data.STAGE_A_LOADS, pkg6_data.STAGE_2_OPS, pkg6_data.STAGE_2_LOADS, 7))
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


def part_c():
    print("(c) proof.md against what this script computes")
    t = Tally()
    proof = PROOF.read_text(encoding="ascii")
    hx = lambda v: f"{v & M32:08x}"
    s = (D3 + rol(ETA, 16)) & M32
    sa, sb = g_steps(X3, X7, X11, X15, W4, W13), g_steps(X3, X7, X11, X15, W4B, W13)
    size = 1 << len(CFREE)
    shifts = sorted(A_SHIFTS.items())
    constants = ([f"S = {hx(shifts[0][1])}"] if len(shifts) == 1 else [f"S{d} = {hx(m)}" for d, m in shifts]) + [f"ALL = {hx(A_ALL)}"]
    printed = {
        "the six constants": f"X3 = {hx(X3)}   X7 = {hx(X7)}   X11 = {hx(X11)}   X15 = {hx(X15)}\n    W4 = {hx(W4)}   W13 = {hx(W13)}",
        "K + W4 and W4'": f"K + W4 = {hx(K + W4)} and W4' = ((K + W4) XOR {LEN_XOR}) - K = {hx(W4B)}",
        "table of the pinned call, first execution": "a1={} d1={} c1={} b1={}\n               a2={} d2={} c2={} b2={}".format(*(hx(x) for x in sa)),
        "table of the pinned call, second execution": "a1={} d1={} c1={} b1={}\n               a2={} d2={} c2={} b2={}".format(*(hx(x) for x in sb)),
        "the pinned call, statement": f"same d output {hx(sa[5])} and the same b\noutput {hx(sa[7])}. They differ in the a output ({hx(Y3)}, {hx(Y3B)})",
        "W4 - W4'": f"W4 - W4' = {hx(DELTA)}",
        "the two lengths": "a 55-byte message",
        "Lemma Q statement": f"((Y3 + Y4) AND {hx(CMASK)}) = {hx(CVALUE)}.",
        "Lemma Q proof: x and m": f"Put x = ROL(eta,16) = {hx(rol(ETA, 16))} and m = x AND 7fffffff = {hx(CMASK)}.",
        "Lemma Q proof: the sum and its half": f"{hx(s)} >> 1 = {hx(s >> 1)}.",
        "eta": f"Fix eta = {ETA_HEX}.",
        "Lemma A (c): the constants": "Put " + ", ".join(constants) + f" and V = {hx(A_V)}.",
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
    # The solutions of the seven-word system that Section 10 prints, evaluated with the G of this script:
    # E1 = G(Y1, Y6, Y11, Y12; w12, w5) and E3 = G(Y3, Y4, Y9, Y14; 0, w8) for A, and for B with Y11', Y3'
    # and w5 + (W4 - W4'). Digest words 1, 3, 4, 6 are E1.a ^ E3.c, E3.a ^ E1.c, E3.b ^ E1.d, E1.b ^ E3.d.
    found = 0
    for label, pattern in (("inside the class", r"A complete solution of the seven-word system with Y4 in the class, which"),
                           ("that violates rule A", r"A complete solution of the seven-word system with Y4 in the class that violates rule A")):
        sol = re.search(pattern + r".{0,80}?Y1 = ([0-9a-f]{8}), Y6 = ([0-9a-f]{8}), Y12 = ([0-9a-f]{8}), w12 = ([0-9a-f]{8}), "
                        r"w5 = ([0-9a-f]{8}), Y4 = ([0-9a-f]{8}), Y9 = ([0-9a-f]{8}), Y14 = ([0-9a-f]{8}), w15 = 0, w8 = ([0-9a-f]{8})\.", flat)
        if not sol:
            print(f"    (no solution {label} is printed in the form this script looks for)")
            continue
        found += 1
        y1, y6, y12, w12, w5, y4, y9, y14, w8 = (int(x, 16) for x in sol.groups())
        ea, eb = G(y1, y6, Y11, y12, w12, w5), G(y1, y6, Y11B, y12, w12, (w5 + DELTA) & M32)
        fa, fb = G(Y3, y4, y9, y14, 0, w8), G(Y3B, y4, y9, y14, 0, w8)
        t.check(f"the solution {label} printed in Section 10: digest words 1, 3, 4, 6 equal for A and B, Y4 in the class",
                (ea[0] ^ fa[2], fa[0] ^ ea[2], fa[1] ^ ea[3], ea[1] ^ fa[3]) == (eb[0] ^ fb[2], fb[0] ^ eb[2], fb[1] ^ eb[3], eb[1] ^ fb[3])
                and ((Y3 + y4) & M32) & CMASK == CVALUE and eta_of(y4) == ETA)
        h1 = ror(y14 ^ ((Y3 + y4) & M32), 16)
        t.check(f"the solution {label}: its h1 {'violates' if 'violates' in label else 'satisfies'} rule A",
                rule_on_h1(h1) != ("violates" in label))
    ok = t.report()
    print(f"    solutions of the seven-word system found in the text and evaluated: {found}")
    return ok


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    trials = int(args[0]) if len(args) > 0 else 20000
    count = int(args[1]) if len(args) > 1 else 256
    assert trials >= 10000, "at least 10000 trials"
    if "--text" in sys.argv:
        ok_c = part_c()
        print("RESULT (c):", "the proof prints what this script computes" if ok_c else "FAILED: " + "; ".join(FAILS))
        return 0 if ok_c else 1
    rng = random.Random(20261006)
    ref = reference()
    ok_a = part_a(trials, rng, ref)
    ok_b = part_b(count, ref)
    program = "all checks of the program passed" if ok_a and ok_b else "FAILED: " + "; ".join(FAILS)
    print("RESULT (a), (b):", program)
    if "--program" in sys.argv:
        print("RESULT: part (c), the text of proof.md, was left out")
        return 0 if ok_a and ok_b else 1
    del FAILS[:]
    ok_c = part_c()
    print("RESULT (c):", "the proof prints what this script computes" if ok_c else "FAILED: " + "; ".join(FAILS))
    if ok_a and ok_b and ok_c:
        print("RESULT: all checks passed")
        return 0
    print("RESULT: FAILED")
    return 1


if __name__ == "__main__":
    sys.exit(main())
