"""xplus1 lens library: the ring GF(2)[x]/(x^32+1) = GF(2)[x]/((x+1)^32).

A u32 word w is the polynomial sum w_i x^i.  Rotation left by r = multiplication by x^r (a unit),
XOR = ring addition.  Write w = sum_j c_j (x+1)^j.  By Lucas, C(i,j) is odd iff j is a bit-subset of i,
so c_j = XOR of w_i over all i that are bit-supersets of j.  `digits(w)` returns the word whose bit j is c_j
(a superset-sum Moebius transform on the 5-bit index; it is an involution).

valuation v(w) = min{ j : c_j = 1 } (32 for w = 0).  Ideal I_k = ((x+1)^k) = { v >= k }, dimension 32-k.
I_{32-2^s} = words of period 2^s (I_28 = period-4 words).  w mod (x+1)^(2^s) = XOR-fold of w to 2^s bits.
"""
import numpy as np

U32 = np.uint32
U64 = np.uint64
_MASKS = ((1, 0x55555555), (2, 0x33333333), (4, 0x0F0F0F0F), (8, 0x00FF00FF), (16, 0x0000FFFF))


def ror(x, r):
    x = np.asarray(x, dtype=U32)
    r %= 32
    if r == 0:
        return x.copy()
    return (x >> U32(r)) | (x << U32(32 - r))


def digits(w):
    c = np.array(w, dtype=U32, copy=True)
    for s, m in _MASKS:
        c ^= (c >> U32(s)) & U32(m)
    return c


def ctz32(c):
    c = np.asarray(c, dtype=U32)
    v = np.full(c.shape, 32, np.int64)
    nz = c != 0
    low = (c & (~c + U32(1)))[nz]
    v[nz] = np.round(np.log2(low.astype(np.float64))).astype(np.int64)
    return v


def val(w):
    return ctz32(digits(w))


def low_digits(w, m):
    """w mod (x+1)^m, as the m low digits (bit j = c_j, j < m)."""
    if m >= 32:
        return digits(w)
    return digits(w) & U32((1 << m) - 1)


def parity(x):
    return (np.bitwise_count(np.asarray(x, dtype=U32)) & 1).astype(np.uint8)


# ---------- pure-python references for the self-test ----------
def val_ref(w):
    """valuation by repeated exact division of the polynomial by (x+1)."""
    if w == 0:
        return 32
    v = 0
    while True:
        if bin(w).count('1') & 1:
            return v
        q = acc = 0
        for i in range(32):
            acc ^= (w >> i) & 1
            q |= acc << i
        w = q
        v += 1


def xp1_pow_bits():
    """bit patterns of (x+1)^j, j = 0..31."""
    p, out = 1, []
    for _ in range(32):
        out.append(p)
        p = p ^ (p << 1)
    return out


def selftest(rng, n=20000):
    pw = xp1_pow_bits()
    ws = [int(x) for x in rng.integers(0, 2**32, size=n, dtype=np.uint64)]
    # add structured words: zero, all ones, period-4, period-2, powers of (x+1), sparse words
    ws += [0, 0xFFFFFFFF, 0x11111111, 0x55555555, 0x33333333, 0x0F0F0F0F, 0xAAAAAAAA, 1, 3, 0x80000000]
    ws += pw
    ws += [int(a) & int(b) for a, b in zip(rng.integers(0, 2**32, 2000, dtype=np.uint64),
                                            rng.integers(0, 2**32, 2000, dtype=np.uint64))]
    arr = np.array(ws, dtype=U32)
    c = digits(arr)
    fails = 0
    # 1: reconstruction w = sum c_j (x+1)^j
    for w, cj in zip(ws, c.tolist()):
        acc = 0
        for j in range(32):
            if (cj >> j) & 1:
                acc ^= pw[j]
        if acc != w:
            fails += 1
    # 2: valuation vs exact division
    v = val(arr)
    for w, vv in zip(ws, v.tolist()):
        if val_ref(w) != vv:
            fails += 1
    # 3: involution, rotation invariance, ultrametric inequality, period words
    if not np.array_equal(digits(c), arr):
        fails += 1
    for r in (1, 7, 8, 12, 16, 31):
        if not np.array_equal(val(ror(arr, r)), v):
            fails += 1
    b = arr[::-1].copy()
    if np.any(val(arr ^ b) < np.minimum(v, val(b))):
        fails += 1
    p4 = np.array([sum(((n4 >> (i % 4)) & 1) << i for i in range(32)) for n4 in range(16)], dtype=U32)
    if np.any(val(p4) < 28):
        fails += 1
    if [val_ref(p) for p in pw] != list(range(32)):
        fails += 1
    return len(ws), fails
