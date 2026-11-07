"""Multi-sibling test (idea 'alternative splicing'): one base message, several block lengths L >= 55.

K2 trick (Lemma L generalised, fringe angle 3): with a1_L = a1_55 ^ 55 ^ L every length L gives the same round-0
state; the siblings differ only in w4 (C3's x) and w5 (E1's y).  Half A (digest words 0,2,5,7) agrees between
two siblings iff C3 gives the same b and d outputs (Y7, Y15) for their two w4 values.

Test 1: the filed pin H8 - which lengths 55..63 share C3's (b, d) with L = 55?
Test 2: how many x values in a +-2^k window around a pinned x share (b, d)?  (random-function baseline: 2^-64)
"""
M = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)


def ror(x, r):
    return ((x >> r) | (x << (32 - r))) & M


def G(a, b, c, d, x, y):
    a = (a + b + x) & M; d = ror(d ^ a, 16); c = (c + d) & M; b = ror(b ^ c, 12)
    a = (a + b + y) & M; d = ror(d ^ a, 8); c = (c + d) & M; b = ror(b ^ c, 7)
    return a, b, c, d


X3, X7, X11, X15, W4, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006
K = (IV[2] + IV[6]) & M
a1_55 = (K + W4) & M
rows = []
ref = None
for L in range(55, 64):
    a1L = a1_55 ^ 55 ^ L
    w4 = (a1L - K) & M
    out = G(X3, X7, X11, X15, w4, W13)
    if ref is None:
        ref = out
    rows.append((L, w4, out, out[1] == ref[1], out[3] == ref[3]))
    print(f"L={L} w4={w4:08x} C3 out a={out[0]:08x} b={out[1]:08x} c={out[2]:08x} d={out[3]:08x} "
          f"b_same={out[1] == ref[1]} d_same={out[3] == ref[3]}")
# K2 check: d1 constant across L
for L in range(55, 64):
    a1L = a1_55 ^ 55 ^ L
    assert ror(L ^ a1L, 16) == ror(55 ^ a1_55, 16)
print("K2 d1 constant across L = 55..63: True")
