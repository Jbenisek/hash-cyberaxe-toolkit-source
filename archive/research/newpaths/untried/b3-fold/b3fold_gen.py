"""Pinned 55/63-byte pair generator for 2-round BLAKE3 (last-chunk compression, counter t, flags 3).

Builds REAL message pairs (A: 55 bytes, B: 63 bytes) whose round-0 state X is identical (Lemma L)
and whose round-0 outputs hit the front-line pins X3, X7, X11, X15 with w4 = W4, w13 = W13
(BLAKE3_2ROUND_MAP.md Section 2.1-2.2). Construction is deterministic from 9 free words:
  X2, X8, X13, w12  -> invert D2 (pin X7 = D2.b)        -> S2, S7, S8, S13
  w5 solved so K2.a = S2; w7 solved so K3.b = S7 (w6 free); w1 solved so K0.c = S8 (t_lo, w0 free)
  S9 forced by pin X3 = D3.a; w2, w3 solved so K1.c = S9 and K1.d = S13 (t_hi = 0)
  w9 solved so D0.d = X15 (w8 free); w11 solved so D1.c = X11 (w10 free)
Pure-Python builder (checked against the organizer reference) and a numpy builder (bulk).
"""

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import sys
import numpy as np

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash/verifier'))
import blake3 as ref  # organizer reference, reduced rounds

M = 0xFFFFFFFF
IV = ref.IV
PERM = ref.PERMUTATION

X3P, X7P, X11P, X15P = 0x29D4FA98, 0xBEE3AF28, 0x44036000, 0x40C58500
W4, W13 = 0x97475638, 0x0007C006
KK = (IV[2] + IV[6]) & M
W4B = ((((KK + W4) & M) ^ 8) - KK) & M
DW5 = (W4 - W4B) & M  # w5' = w5 + w4 - w4'
LEN_A, LEN_B, FLAGS = 55, 63, 3  # CHUNK_START | CHUNK_END, last chunk of F||A


def ror(x, n):
    return ((x >> n) | (x << (32 - n))) & M


def rol(x, n):
    return ((x << n) | (x >> (32 - n))) & M


def G(a, b, c, d, x, y):
    a1 = (a + b + x) & M; d1 = ror(d ^ a1, 16); c1 = (c + d1) & M; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return a2, b2, c2, d2


def Ginv(a2, b2, c2, d2, x, y):
    b1 = rol(b2, 7) ^ c2; c1 = (c2 - d2) & M; d1 = rol(d2, 8) ^ a2; a1 = (a2 - b1 - y) & M
    b = rol(b1, 12) ^ c1; c = (c1 - d1) & M; d = rol(d1, 16) ^ a1; a = (a1 - b - x) & M
    return a, b, c, d


def build_pair(free, t_hi=0):
    """free = (X2, X8, X13, w12, w6, t_lo, w0, w8, w10). Returns (words_A, words_B, counter)."""
    X2, X8, X13, w12, w6, t_lo, w0, w8, w10 = free
    S2, S7, S8, S13 = Ginv(X2, X7P, X8, X13, w12, W13)
    # K2 = G(IV2, IV6, IV2, 55; W4, w5): a-output S2 via w5
    a1 = (IV[2] + IV[6] + W4) & M; d1 = ror(LEN_A ^ a1, 16); c1 = (IV[2] + d1) & M; b1 = ror(IV[6] ^ c1, 12)
    w5 = (S2 - a1 - b1) & M
    _, S6, S10, S14 = G(IV[2], IV[6], IV[2], LEN_A, W4, w5)
    # K3 = G(IV3, IV7, IV3, 3; w6, w7): b-output S7 via w7
    a1 = (IV[3] + IV[7] + w6) & M; d1 = ror(FLAGS ^ a1, 16); c1 = (IV[3] + d1) & M; b1 = ror(IV[7] ^ c1, 12)
    c2 = rol(S7, 7) ^ b1; d2 = (c2 - c1) & M; a2 = rol(d2, 8) ^ d1; w7 = (a2 - a1 - b1) & M
    S3, S11, S15 = a2, c2, d2
    # K0 = G(IV0, IV4, IV0, t_lo; w0, w1): c-output S8 via w1
    a1 = (IV[0] + IV[4] + w0) & M; d1 = ror(t_lo ^ a1, 16); c1 = (IV[0] + d1) & M; b1 = ror(IV[4] ^ c1, 12)
    d2 = (S8 - c1) & M; a2 = rol(d2, 8) ^ d1; w1 = (a2 - a1 - b1) & M
    S0, S4, S12 = a2, ror(b1 ^ S8, 7), d2
    # pin X3 = D3.a with D3 = G(S3, S4, S9, S14; 0, 0) forces S9
    a1 = (S3 + S4) & M; d1 = ror(S14 ^ a1, 16); b1 = (X3P - a1) & M; c1 = rol(b1, 12) ^ S4
    S9 = (c1 - d1) & M
    # K1 = G(IV1, IV5, IV1, t_hi; w2, w3): c-output S9 and d-output S13 via w2, w3
    c1 = (S9 - S13) & M; d1 = (c1 - IV[1]) & M; a1 = rol(d1, 16) ^ t_hi; w2 = (a1 - IV[1] - IV[5]) & M
    b1 = ror(IV[5] ^ c1, 12); a2 = rol(S13, 8) ^ d1; w3 = (a2 - a1 - b1) & M
    S1, S5 = a2, ror(b1 ^ S9, 7)
    # D0 = G(S0, S5, S10, S15; w8, w9): d-output X15 via w9
    a1 = (S0 + S5 + w8) & M; d1 = ror(S15 ^ a1, 16); c1 = (S10 + d1) & M; b1 = ror(S5 ^ c1, 12)
    a2 = rol(X15P, 8) ^ d1; w9 = (a2 - a1 - b1) & M
    # D1 = G(S1, S6, S11, S12; w10, w11): c-output X11 via w11
    a1 = (S1 + S6 + w10) & M; d1 = ror(S12 ^ a1, 16); c1 = (S11 + d1) & M; b1 = ror(S6 ^ c1, 12)
    d2 = (X11P - c1) & M; a2 = rol(d2, 8) ^ d1; w11 = (a2 - a1 - b1) & M
    wa = [w0, w1, w2, w3, W4, w5, w6, w7, w8, w9, w10, w11, w12, W13, 0, 0]
    wb = list(wa); wb[4] = W4B; wb[5] = (w5 + DW5) & M
    return wa, wb, (t_lo | (t_hi << 32))


def ref_state(words, counter, block_len):
    """Final 16-word state from the organizer reference (unfold its 16 output words; cv = IV)."""
    out = ref._compress(IV, words, counter, block_len, FLAGS, 2)
    hi = [out[8 + i] ^ IV[i] for i in range(8)]
    lo = [out[i] ^ hi[i] for i in range(8)]
    return lo + hi, out


def round0_state(words, counter, block_len):
    v = list(IV) + list(IV[:4]) + [counter & M, counter >> 32, block_len, FLAGS]
    m = words
    for (a, b, c, d), (x, y) in zip(
            [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
             (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)],
            [(0, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11), (12, 13), (14, 15)]):
        v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], m[x], m[y])
    return v


# ---------------------------------------------------------------- numpy bulk version
U = np.uint32


def rv(x, n):
    return (x >> n) | (x << (32 - n))


def lv(x, n):
    return (x << n) | (x >> (32 - n))


def Gv(a, b, c, d, x, y):
    a1 = a + b + x; d1 = rv(d ^ a1, 16); c1 = c + d1; b1 = rv(b ^ c1, 12)
    a2 = a1 + b1 + y; d2 = rv(d1 ^ a2, 8); c2 = c1 + d2; b2 = rv(b1 ^ c2, 7)
    return a2, b2, c2, d2


def Ginv_v(a2, b2, c2, d2, x, y):
    b1 = lv(b2, 7) ^ c2; c1 = c2 - d2; d1 = lv(d2, 8) ^ a2; a1 = a2 - b1 - y
    b = lv(b1, 12) ^ c1; c = c1 - d1; d = lv(d1, 16) ^ a1; a = a1 - b - x
    return a, b, c, d


def build_pairs_v(F):
    """F: array (9, N) uint32 of free words, same order as build_pair. Returns (WA list of 16 arrays,
    WB list, t_lo array). t_hi = 0."""
    X2, X8, X13, w12, w6, t_lo, w0, w8, w10 = [F[i] for i in range(9)]
    N = X2.shape[0]
    full = lambda val: np.full(N, val, dtype=U)
    iv = [full(x) for x in IV]
    S2, S7, S8, S13 = Ginv_v(X2, full(X7P), X8, X13, w12, full(W13))
    a1 = iv[2] + iv[6] + U(W4); d1 = rv(full(LEN_A) ^ a1, 16); c1 = iv[2] + d1; b1 = rv(iv[6] ^ c1, 12)
    w5 = S2 - a1 - b1
    _, S6, S10, S14 = Gv(iv[2], iv[6], iv[2], full(LEN_A), full(W4), w5)
    a1 = iv[3] + iv[7] + w6; d1 = rv(full(FLAGS) ^ a1, 16); c1 = iv[3] + d1; b1 = rv(iv[7] ^ c1, 12)
    c2 = lv(S7, 7) ^ b1; d2 = c2 - c1; a2 = lv(d2, 8) ^ d1; w7 = a2 - a1 - b1
    S3, S11, S15 = a2, c2, d2
    a1 = iv[0] + iv[4] + w0; d1 = rv(t_lo ^ a1, 16); c1 = iv[0] + d1; b1 = rv(iv[4] ^ c1, 12)
    d2 = S8 - c1; a2 = lv(d2, 8) ^ d1; w1 = a2 - a1 - b1
    S0, S4, S12 = a2, rv(b1 ^ S8, 7), d2
    a1 = S3 + S4; d1 = rv(S14 ^ a1, 16); b1 = full(X3P) - a1; c1 = lv(b1, 12) ^ S4
    S9 = c1 - d1
    c1 = S9 - S13; d1 = c1 - iv[1]; a1 = lv(d1, 16)  # t_hi = 0
    w2 = a1 - iv[1] - iv[5]
    b1 = rv(iv[5] ^ c1, 12); a2 = lv(S13, 8) ^ d1; w3 = a2 - a1 - b1
    S1 = a2; S5 = rv(b1 ^ S9, 7)
    a1 = S0 + S5 + w8; d1 = rv(S15 ^ a1, 16); c1 = S10 + d1; b1 = rv(S5 ^ c1, 12)
    a2 = lv(full(X15P), 8) ^ d1; w9 = a2 - a1 - b1
    a1 = S1 + S6 + w10; d1 = rv(S12 ^ a1, 16); c1 = S11 + d1; b1 = rv(S6 ^ c1, 12)
    d2 = full(X11P) - c1; a2 = lv(d2, 8) ^ d1; w11 = a2 - a1 - b1
    z = full(0)
    WA = [w0, w1, w2, w3, full(W4), w5, w6, w7, w8, w9, w10, w11, w12, full(W13), z, z]
    WB = list(WA); WB[4] = full(W4B); WB[5] = w5 + U(DW5)
    return WA, WB, t_lo


CALLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15),
         (0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def compress2_v(W, t_lo, block_len, keep_round0=False):
    """2-round compression on arrays; returns final 16-word state (list of arrays) [and round-0 state]."""
    N = t_lo.shape[0]
    full = lambda val: np.full(N, val, dtype=U)
    v = [full(x) for x in IV] + [full(x) for x in IV[:4]] + [t_lo.copy(), full(0), full(block_len), full(FLAGS)]
    m = list(W)
    x0 = None
    for r in range(2):
        for j, (a, b, c, d) in enumerate(CALLS):
            v[a], v[b], v[c], v[d] = Gv(v[a], v[b], v[c], v[d], m[2 * j], m[2 * j + 1])
        if r == 0 and keep_round0:
            x0 = list(v)
        m = [m[i] for i in PERM]
    return (v, x0) if keep_round0 else v
