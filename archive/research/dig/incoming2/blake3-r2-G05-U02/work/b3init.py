"""G05-U02: INIT.v4..v7 (h[4..7]) scan. Own code. Parametrised round-0 inverse (after research/r2_half.py derive,
rewritten with the chaining value h, counter t, flags as parameters), vectorised with numpy.
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

import sys, struct, random
import numpy as np
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/hash-smash'))
from verifier import blake3 as VB
M = 0xFFFFFFFF
IV = VB.IV
U = np.uint32
def ror(v, n): return (v >> U(n)) | (v << U(32 - n))
def rol(v, n): return (v << U(n)) | (v >> U(32 - n))
def c(x): return U(x & M)

def pyror(v, n): return ((v >> n) | (v << (32 - n))) & M
def pyg(v, a, b, cc, d, x, y):
    v[a] = (v[a] + v[b] + x) & M; v[d] = pyror(v[d] ^ v[a], 16); v[cc] = (v[cc] + v[d]) & M; v[b] = pyror(v[b] ^ v[cc], 12)
    v[a] = (v[a] + v[b] + y) & M; v[d] = pyror(v[d] ^ v[a], 8); v[cc] = (v[cc] + v[d]) & M; v[b] = pyror(v[b] ^ v[cc], 7)
PERM = VB.PERMUTATION
def my_compress(h, m, t, blen, flags, rounds):
    """own reference compress (python ints); returns state after rounds (16 words) and output cv (8)"""
    v = list(h) + list(IV[:4]) + [t & M, t >> 32, blen, flags]
    m = list(m)
    for _ in range(rounds):
        pyg(v, 0, 4, 8, 12, m[0], m[1]); pyg(v, 1, 5, 9, 13, m[2], m[3]); pyg(v, 2, 6, 10, 14, m[4], m[5]); pyg(v, 3, 7, 11, 15, m[6], m[7])
        pyg(v, 0, 5, 10, 15, m[8], m[9]); pyg(v, 1, 6, 11, 12, m[10], m[11]); pyg(v, 2, 7, 8, 13, m[12], m[13]); pyg(v, 3, 4, 9, 14, m[14], m[15])
        m = [m[i] for i in PERM]
    return v, tuple(v[i] ^ v[i + 8] for i in range(8))

def g(a, b, cc, d, x, y):
    a = a + b + x; d = ror(d ^ a, 16); cc = cc + d; b = ror(b ^ cc, 12)
    a = a + b + y; d = ror(d ^ a, 8); cc = cc + d; b = ror(b ^ cc, 7)
    return a, b, cc, d

FREE = (1, 2, 5, 6, 9, 10, 12, 13, 14)
def derive(h, pin, free, t=0, flags=3, w15=0):
    """free: dict idx-> uint32 array. h: list of 8 python ints (chaining value).
    returns w, wb (lists of arrays), X, S"""
    la, lb = pin['len_a'], pin['len_b']
    x3, x7, x11, x15 = [c(x) for x in pin['inputs']]
    w4 = c(pin['w4']); w13 = c(pin['w13'])
    n = free[1].shape[0]
    Z = np.zeros(n, dtype=U)
    X = [Z.copy() for _ in range(16)]; S = [Z.copy() for _ in range(16)]; w = [Z.copy() for _ in range(16)]
    for i in FREE: X[i] = free[i]
    X[3] = Z + x3; X[7] = Z + x7; X[11] = Z + x11; X[15] = Z + x15
    w4 = Z + w4
    w[4] = w4; w[13] = Z + w13; w[15] = Z + c(w15)
    K = (IV[2] + h[6]) & M
    a1_c2 = w4 + c(K)
    d1_c2 = ror(a1_c2 ^ c(la), 16)
    c1_c2 = d1_c2 + c(IV[2])
    b1_c2 = ror(c1_c2 ^ c(h[6]), 12)
    b1_d1 = rol(X[6], 7) ^ X[11]
    c1_d1 = X[11] - X[12]
    d1_d1 = rol(X[12], 8) ^ X[1]
    S[6] = rol(b1_d1, 12) ^ c1_d1
    S[11] = c1_d1 - d1_d1
    S[10] = b1_c2 ^ rol(S[6], 7)
    b1_d0 = rol(X[5], 7) ^ X[10]
    c1_d0 = X[10] - X[15]
    S[5] = rol(b1_d0, 12) ^ c1_d0
    d1_d0 = c1_d0 - S[10]
    X[0] = d1_d0 ^ rol(X[15], 8)
    S[14] = S[10] - c1_c2
    S[2] = rol(S[14], 8) ^ d1_c2
    w[5] = S[2] - a1_c2 - b1_c2
    d1_d3 = rol(X[14], 8) ^ X[3]
    a1_d3 = rol(d1_d3, 16) ^ S[14]
    b1_d3 = X[3] - a1_d3 - w[15]
    X[4] = ror(b1_d3 ^ X[9], 7)
    c1_d3 = X[9] - X[14]
    S[4] = rol(b1_d3, 12) ^ c1_d3
    S[9] = c1_d3 - d1_d3
    dcol = {0: t & M, 1: t >> 32, 3: flags}
    def column(j, sb, sc):
        a0, b0, c0 = c(h[j]), c(h[4 + j]), c(IV[j])
        b1 = rol(sb, 7) ^ sc
        c1 = rol(b1, 12) ^ b0
        sd = sc - c1
        d1 = c1 - c0
        a1 = rol(d1, 16) ^ c(dcol[j])
        wx = a1 - a0 - b0
        sa = rol(sd, 8) ^ d1
        wy = sa - a1 - b1
        return sa, sd, wx, wy
    S[1], S[13], w[2], w[3] = column(1, S[5], S[9])
    d1_d2 = rol(X[13], 8) ^ X[2]
    a1_d2 = rol(d1_d2, 16) ^ S[13]
    b1_d2 = X[2] - a1_d2 - w[13]
    X[8] = b1_d2 ^ rol(X[7], 7)
    c1_d2 = X[8] - X[13]
    S[7] = rol(b1_d2, 12) ^ c1_d2
    S[8] = c1_d2 - d1_d2
    w[12] = a1_d2 - S[2] - S[7]
    S[0], S[12], w[0], w[1] = column(0, S[4], S[8])
    S[3], S[15], w[6], w[7] = column(3, S[7], S[11])
    a1_d0 = rol(d1_d0, 16) ^ S[15]
    w[8] = a1_d0 - S[0] - S[5]
    w[9] = X[0] - a1_d0 - b1_d0
    a1_d1 = rol(d1_d1, 16) ^ S[12]
    w[10] = a1_d1 - S[1] - S[6]
    w[11] = X[1] - a1_d1 - b1_d1
    w[14] = a1_d3 - S[3] - S[4]
    w4b = (a1_c2 ^ c(la) ^ c(lb)) - c(K)
    wb = list(w); wb[4] = w4b; wb[5] = w[5] + w4 - w4b
    return w, wb, X, S

def tail(h, pin, X, w, wb):
    """round 1 part: residual words (digest 1,3,4,6) as XOR of A and B differences"""
    x3, x7, x11, x15 = [c(x) for x in pin['inputs']]
    w4 = wb[4] * U(0) + c(pin['w4']); w4b = wb[4]
    y0 = g(X[0], X[4], X[8], X[12], w[2], w[6])
    y1 = g(X[1], X[5], X[9], X[13], w[3], w[10])
    y2 = g(X[2], X[6], X[10], X[14], w[7], w[0])
    c3a = g(x3, x7, x11, x15, w4, w[13]); c3b = g(x3, x7, x11, x15, w4b, w[13])
    e1a = g(y1[0], y2[1], c3a[2], y0[3], w[12], w[5]); e1b = g(y1[0], y2[1], c3b[2], y0[3], w[12], wb[5])
    e3a = g(c3a[0], y0[1], y1[2], y2[3], w[15], w[8]); e3b = g(c3b[0], y0[1], y1[2], y2[3], w[15], w[8])
    res = (e1a[0] ^ e3a[2] ^ e1b[0] ^ e3b[2], e3a[0] ^ e1a[2] ^ e3b[0] ^ e1b[2],
           e3a[1] ^ e1a[3] ^ e3b[1] ^ e1b[3], e1a[1] ^ e3a[3] ^ e1b[1] ^ e3b[3])
    return res

def rand_free(rng, n):
    return {i: rng.integers(0, 1 << 32, size=n, dtype=np.uint64).astype(U) for i in FREE}

PIN = dict(len_a=55, len_b=63, inputs=(0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500), w4=0x97475638, w13=0x0007c006)
