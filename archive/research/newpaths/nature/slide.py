"""'Ribosome slippage' (slide) check at full width: the unique message m* whose round 0 maps the initial state to itself.

Round 0 is a bijection message -> state for a fixed initial state (Sol W, section 3.3; Aumasson et al. FSE 2010).
So for target X = v_init there is exactly one m*.  Then 2-round(m*) = 1-round(PERM(m*)) (same length and flags).
This script inverts round 0 with Sol's formulas (3)-(5), verifies the fixed point, and verifies the slide identity.
"""
M = 0xFFFFFFFF
IV = [0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19]
PERM = [2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8]


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M


def rol(x, r):
    return ((x << r) | (x >> (32 - r))) & M


def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


COLS = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]
DIAG = [(0, 5, 10, 15), (1, 6, 11, 12), (2, 7, 8, 13), (3, 4, 9, 14)]


def rnd(v, m):
    v = list(v)
    for i, (a, b, c, d) in enumerate(COLS):
        v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], m[2 * i], m[2 * i + 1])
    for i, (a, b, c, d) in enumerate(DIAG):
        v[a], v[b], v[c], v[d] = G(v[a], v[b], v[c], v[d], m[8 + 2 * i], m[9 + 2 * i])
    return v


def comp(m, rounds, blen=64, flags=11):
    v = IV[:] + IV[:4] + [0, 0, blen, flags]
    for _ in range(rounds):
        v = rnd(v, m)
        m = [m[PERM[i]] for i in range(16)]
    return [v[i] ^ v[i + 8] for i in range(8)]


def inv_round(v0, X):
    """message m with rnd(v0, m) == X (Sol W formulas (3)-(5))."""
    S = [None] * 16
    saved = {}
    for i, (ia, ib, ic, idd) in enumerate(DIAG):           # (4): old b,c of each diagonal
        A, B, C, D = X[ia], X[ib], X[ic], X[idd]
        s = rol(B, 7) ^ C; r = (C - D) & M; q = rol(D, 8) ^ A
        S[ib] = rol(s, 12) ^ r; S[ic] = (r - q) & M
        saved[i] = (s, q, A)
    m = [0] * 16
    for i, (ia, ib, ic, idd) in enumerate(COLS):           # (3): columns with known final b,c
        a, b, c, d = v0[ia], v0[ib], v0[ic], v0[idd]
        B, C = S[ib], S[ic]
        s = rol(B, 7) ^ C; r = rol(s, 12) ^ b; q = (r - c) & M; D = (C - r) & M
        p = rol(q, 16) ^ d; A = rol(D, 8) ^ q
        m[2 * i] = (p - a - b) & M; m[2 * i + 1] = (A - p - s) & M
        S[ia], S[idd] = A, D
    for i, (ia, ib, ic, idd) in enumerate(DIAG):           # (5): diagonal messages
        s, q, A = saved[i]
        a, b, d = S[ia], S[ib], S[idd]
        p = rol(q, 16) ^ d
        m[8 + 2 * i] = (p - a - b) & M; m[9 + 2 * i] = (A - p - s) & M
    return m


if __name__ == "__main__":
    for blen in (64, 55, 0):
        v0 = IV[:] + IV[:4] + [0, 0, blen, 11]
        ms = inv_round(v0, v0)
        fixed = rnd(v0, ms) == v0
        pm = [ms[PERM[i]] for i in range(16)]
        slide = comp(ms, 2, blen) == comp(pm, 1, blen)
        print(f"blen={blen}: m* = {' '.join('%08x' % x for x in ms)}")
        print(f"   round0(v_init, m*) == v_init: {fixed};  2-round(m*) == 1-round(PERM(m*)): {slide}")
        print(f"   digest {' '.join('%08x' % x for x in comp(ms, 2, blen))}")
