"""b3-r1c scout: pair model of the 55/63 counter construction (2-round BLAKE3).

Reconstructs the front-line parameterisation from BLAKE3_2ROUND_MAP.md Section 2:
outer words (C0.d1, D2.a1, D2.b1, S11, S4, X9, w6), member y = Y4, and the trial
word w0 (t solved in K0).  Every assignment is one inversion step.  Checked against
the organizer reference hash-smash/verifier/blake3.py (_compress, rounds=2).
"""
import os, random, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VER = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "hash-smash", "verifier"))
sys.path.insert(0, VER)
import blake3 as ref  # organizer reference (reduced rounds)

M = 0xFFFFFFFF
IV = ref.IV
PERM = ref.PERMUTATION


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & M


def g_trace(a, b, c, d, x, y):
    a1 = (a + b + x) & M
    d1 = ror(d ^ a1, 16)
    c1 = (c + d1) & M
    b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M
    d2 = ror(d1 ^ a2, 8)
    c2 = (c1 + d2) & M
    b2 = ror(b1 ^ c2, 7)
    return (a1, b1, c1, d1), (a2, b2, c2, d2)


CALLS = [  # name, state indices, schedule slots (round r uses permuted schedule)
    ("K0", (0, 4, 8, 12), (0, 1)), ("K1", (1, 5, 9, 13), (2, 3)),
    ("K2", (2, 6, 10, 14), (4, 5)), ("K3", (3, 7, 11, 15), (6, 7)),
    ("D0", (0, 5, 10, 15), (8, 9)), ("D1", (1, 6, 11, 12), (10, 11)),
    ("D2", (2, 7, 8, 13), (12, 13)), ("D3", (3, 4, 9, 14), (14, 15)),
]
R1NAMES = ["C0", "C1", "C2", "C3", "E0", "E1", "E2", "E3"]


def trace(words, t, blen, flags=3):
    """Full 2-round trace. Returns dict of named words (S, X, Y, Z, mids)."""
    v = list(IV) + list(IV[:4]) + [t & M, t >> 32, blen, flags]
    m = list(words)
    out = {}
    for r in range(2):
        for k, (nm, idx, sl) in enumerate(CALLS):
            name = nm if r == 0 else R1NAMES[k]
            a, b, c, d = (v[i] for i in idx)
            mid, o = g_trace(a, b, c, d, m[sl[0]], m[sl[1]])
            for lab, val in zip(("a1", "b1", "c1", "d1"), mid):
                out[name + "." + lab] = val
            for i, val in zip(idx, o):
                v[i] = val
            if k == 3:
                for i in range(16):
                    out[("S" if r == 0 else "Y") + str(i)] = v[i]
        for i in range(16):
            out[("X" if r == 0 else "Z") + str(i)] = v[i]
        m = [m[i] for i in PERM]
    return out


# constants from BLAKE3_2ROUND_MAP.md Section 2.2
PIN = {3: 0x29D4FA98, 7: 0xBEE3AF28, 11: 0x44036000, 15: 0x40C58500}
W4, W13 = 0x97475638, 0x0007C006
KLEN = (IV[2] + IV[6]) & M
W4B = (((KLEN + W4) ^ 8) - KLEN) & M


def build(p):
    """p: dict with C0d1, D2a1, D2b1, S11, S4, X9, w6, y, w0 -> (words_A, t, words_B)."""
    w = [0] * 16
    w[4], w[13] = W4, W13
    X3, X7, X11, X15 = PIN[3], PIN[7], PIN[11], PIN[15]
    w6 = p["w6"]; w[6] = w6
    # K3 from (w6, S11)
    a1 = (IV[3] + IV[7] + w6) & M; d1 = ror(3 ^ a1, 16); c1 = (IV[3] + d1) & M; b1 = ror(IV[7] ^ c1, 12)
    S11 = p["S11"]; d2 = (S11 - c1) & M; a2 = rol(d2, 8) ^ d1
    w[7] = (a2 - a1 - b1) & M; S3, S15, S7 = a2, d2, ror(b1 ^ S11, 7)
    # D2 from (D2.a1, D2.b1) and pin X7
    Da1, Db1 = p["D2a1"], p["D2b1"]
    Dc1 = rol(Db1, 12) ^ S7; X2 = (Da1 + Db1 + W13) & M
    X8 = rol(X7, 7) ^ Db1; X13 = (X8 - Dc1) & M; Dd1 = rol(X13, 8) ^ X2
    S13 = rol(Dd1, 16) ^ Da1; S8 = (Dc1 - Dd1) & M
    # D3 from (S3, S4, X9) and pin X3
    S4, X9 = p["S4"], p["X9"]
    e_a1 = (S3 + S4) & M; e_b1 = (X3 - e_a1) & M; e_c1 = rol(e_b1, 12) ^ S4
    X14 = (X9 - e_c1) & M; e_d1 = rol(X14, 8) ^ X3
    S14 = rol(e_d1, 16) ^ e_a1; S9 = (e_c1 - e_d1) & M; X4 = ror(e_b1 ^ X9, 7)
    # K2: S14 -> w5
    a1 = (IV[2] + IV[6] + W4) & M; d1 = ror(55 ^ a1, 16); c1 = (IV[2] + d1) & M; b1 = ror(IV[6] ^ c1, 12)
    a2 = rol(S14, 8) ^ d1; w[5] = (a2 - a1 - b1) & M; S2 = a2; S10 = (c1 + S14) & M; S6 = ror(b1 ^ S10, 7)
    w[12] = (Da1 - S2 - S7) & M
    # K1 from (S9, S13)
    c1 = (S9 - S13) & M; d1 = (c1 - IV[1]) & M; a1 = rol(d1, 16)
    w[2] = (a1 - IV[1] - IV[5]) & M; b1 = ror(IV[5] ^ c1, 12)
    S1 = rol(S13, 8) ^ d1; w[3] = (S1 - a1 - b1) & M; S5 = ror(b1 ^ S9, 7)
    # K0 from (S4, S8); w0 free, t solved
    kb1 = rol(S4, 7) ^ S8; kc1 = rol(kb1, 12) ^ IV[4]; kd1 = (kc1 - IV[0]) & M
    S12 = (S8 - kc1) & M; S0 = rol(S12, 8) ^ kd1
    w0 = p["w0"]; w[0] = w0; ka1 = (IV[0] + IV[4] + w0) & M
    w[1] = (S0 - ka1 - kb1) & M; t = rol(kd1, 16) ^ ka1
    # C0 from (C0.d1, y)
    Cd1 = p["C0d1"]; Cc1 = (X8 + Cd1) & M; Cb1 = ror(X4 ^ Cc1, 12)
    y = p["y"]; Cc2 = rol(y, 7) ^ Cb1; Y12 = (Cc2 - Cc1) & M; Y0 = rol(Y12, 8) ^ Cd1
    Ca1 = (Y0 - Cb1 - w6) & M; X12 = rol(Cd1, 16) ^ Ca1; X0 = (Ca1 - X4 - w[2]) & M
    # D0 from X0 and pin X15
    Fd1 = rol(X15, 8) ^ X0; Fa1 = rol(Fd1, 16) ^ S15; w[8] = (Fa1 - S0 - S5) & M
    Fc1 = (S10 + Fd1) & M; Fb1 = ror(S5 ^ Fc1, 12); w[9] = (X0 - Fa1 - Fb1) & M
    # D1 from X12 and pin X11
    Hc1 = (X11 - X12) & M; Hd1 = (Hc1 - S11) & M; Ha1 = rol(Hd1, 16) ^ S12
    w[10] = (Ha1 - S1 - S6) & M; Hb1 = ror(S6 ^ Hc1, 12); X1 = rol(X12, 8) ^ Hd1
    w[11] = (X1 - Ha1 - Hb1) & M
    wB = list(w); wB[4] = W4B; wB[5] = (w[5] + W4 - W4B) & M
    return w, t, wB


def rand_params(rng):
    return {k: rng.getrandbits(32) for k in ("C0d1", "D2a1", "D2b1", "S11", "S4", "X9", "w6", "y", "w0")}


def residual(wA, t, wB):
    a = ref._compress(IV, wA, t, 55, 3, 2)[:8]
    b = ref._compress(IV, wB, t, 63, 3, 2)[:8]
    return [x ^ y for x, y in zip(a, b)]


if __name__ == "__main__":
    rng = random.Random(20261010)
    n, ok_half, ok_trace, ok_key = 2000, 0, 0, 0
    for _ in range(n):
        p = rand_params(rng)
        wA, t, wB = build(p)
        r = residual(wA, t, wB)
        ok_half += (r[0] | r[2] | r[5] | r[7]) == 0
        TA, TB = trace(wA, t, 55), trace(wB, t, 63)
        same = all(TA["X%d" % i] == TB["X%d" % i] for i in range(16))
        pins = all(TA["X%d" % i] == PIN[i] for i in PIN)
        yok = TA["Y4"] == p["y"]
        ok_trace += same and pins and yok
        # residual = E1 key xor E3 key (word map 1:Z1^Z9, 3:Z3^Z11, 4:Z4^Z12, 6:Z6^Z14)
        dz = {i: TA["Z%d" % i] ^ TB["Z%d" % i] for i in range(16)}
        ok_key += (r[1] == dz[1] ^ dz[9] and r[3] == dz[3] ^ dz[11]
                   and r[4] == dz[4] ^ dz[12] and r[6] == dz[6] ^ dz[14])
    T = trace(*build(rand_params(rng))[:2], 55)
    print("C3 outputs A: Y3=%08x Y7=%08x Y11=%08x Y15=%08x" % (T["Y3"], T["Y7"], T["Y11"], T["Y15"]))
    wA, t, wB = build(rand_params(rng)); TB = trace(wB, t, 63)
    print("C3 outputs B: Y3=%08x Y7=%08x Y11=%08x Y15=%08x" % (TB["Y3"], TB["Y7"], TB["Y11"], TB["Y15"]))
    print("pairs=%d  half-collision(words 0,2,5,7)=%d  X equal+pins+Y4=y: %d  residual=E1key^E3key: %d"
          % (n, ok_half, ok_trace, ok_key))
