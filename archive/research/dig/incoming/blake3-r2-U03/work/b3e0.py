# b3e0.py - our own 2-round BLAKE3 tracer + E0 relaxation experiments (blake3-r2-U03). Standard library + numpy.
import random, sys, json, time
M = 0xffffffff
def ror(x, n): return ((x >> n) | (x << (32 - n))) & M
def rol(x, n): return ror(x, 32 - n)
IV = [0x6a09e667,0xbb67ae85,0x3c6ef372,0xa54ff53a,0x510e527f,0x9b05688c,0x1f83d9ab,0x5be0cd19]
P = [2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8]
CALLS = [(0,4,8,12),(1,5,9,13),(2,6,10,14),(3,7,11,15),(0,5,10,15),(1,6,11,12),(2,7,8,13),(3,4,9,14)]
NAMES = ['K0','K1','K2','K3','D0','D1','D2','D3','C0','C1','C2','C3','E0','E1','E2','E3']
def G(A, B, C, D, x, y):
    a1 = (A + B + x) & M; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)
def Ginv(a2, b2, c2, d2, x, y):
    b1 = rol(b2, 7) ^ c2; c1 = (c2 - d2) & M; d1 = rol(d2, 8) ^ a2
    B = rol(b1, 12) ^ c1; C = (c1 - d1) & M; rd = rol(d1, 16)  # a1 = rd xor D
    return dict(b1=b1, c1=c1, d1=d1, B=B, C=C, rd=rd)
def round_from(v, m, trace=None, rnd=0):
    v = list(v)
    for j, (a, b, c, d) in enumerate(CALLS):
        # call index within the round: columns 0-3, diagonals 4-7
        x, y = m[2 * j], m[2 * j + 1]
        r = G(v[a], v[b], v[c], v[d], x, y)
        if trace is not None:
            trace[rnd * 8 + j] = (v[a], v[b], v[c], v[d], x, y)
        v[a], v[b], v[c], v[d] = r['a2'], r['b2'], r['c2'], r['d2']
    return v
def compress(h, m, tlo, thi, n, flags, rounds, trace=None):
    v = list(h) + IV[:4] + [tlo, thi, n, flags]
    m = list(m)
    for r in range(rounds):
        v = round_from(v, m, trace, r)
        m = [m[i] for i in P]
    out = [v[i] ^ v[i + 8] for i in range(8)] + [v[i + 8] ^ h[i] for i in range(8)]
    return v, out
# ---------------- validation on known answers ----------------
def validate():
    ok = {}
    # 1. BLAKE3("") 7 rounds
    v, out = compress(IV, [0] * 16, 0, 0, 0, 1 | 2 | 8, 7)
    dig = b''.join(w.to_bytes(4, 'little') for w in out[:8]).hex()
    ok['blake3_empty_7rounds'] = dig == 'af1349b9f5f9a1a6a0404dea36dcc9499bcb25c9adc112b7cc9a93cae41f3262'
    # 2. package Fact P (C3 with W4 / W4')
    X3, X7, X11, X15, W4, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006
    r = G(X3, X7, X11, X15, W4, W13)
    ok['factP_w4'] = (r['a1'], r['d1'], r['c1'], r['b1'], r['a2'], r['d2'], r['c2'], r['b2']) == (0x7ffffff8, 0x7af83f3a, 0xbefb9f3a, 0x01200183, 0x8127c181, 0xbbfbdffe, 0x7af77f38, 0x76f7aefd)
    W4p = (((0x5bf2cd1d + W4) ^ 8) - 0x5bf2cd1d) & M
    r2 = G(X3, X7, X11, X15, W4p, W13)
    ok['factP_w4p'] = (r2['a2'], r2['d2'], r2['c2'], r2['b2']) == (0x7edf3e7e, 0xbbfbdffe, 0x850000c3, 0x76f7aefd)
    # 3. Lemma L: K2 length 55 vs 63 leaves same four state words
    rng = random.Random(1); good = True
    for _ in range(2000):
        w4, w5 = rng.getrandbits(32), rng.getrandbits(32)
        w4p = (((0x5bf2cd1d + w4) ^ 8) - 0x5bf2cd1d) & M; w5p = (w5 + w4 - w4p) & M
        a = G(IV[2], IV[6], IV[2], 55, w4, w5); b = G(IV[2], IV[6], IV[2], 63, w4p, w5p)
        good &= (a['a2'], a['b2'], a['c2'], a['d2']) == (b['a2'], b['b2'], b['c2'], b['d2'])
    ok['lemmaL_2000'] = good
    # 4. Ginv round trip
    good = True
    for _ in range(2000):
        A, B, C, D, x, y = [rng.getrandbits(32) for _ in range(6)]
        r = G(A, B, C, D, x, y); iv = Ginv(r['a2'], r['b2'], r['c2'], r['d2'], x, y)
        good &= iv['B'] == B and iv['C'] == C and (iv['rd'] ^ D) == r['a1'] and (r['a2'] - r['a1'] - iv['b1']) & M == y
    ok['Ginv_roundtrip'] = good
    return ok
# ---------------- clean reachable round-1 states ----------------
X3, X7, X11, X15, W4, W13 = 0x29d4fa98, 0xbee3af28, 0x44036000, 0x40c58500, 0x97475638, 0x0007c006
K = 0x5bf2cd1d
W4P = (((K + W4) ^ 8) - K) & M
def clean_base(rng):
    X = [rng.getrandbits(32) for _ in range(16)]
    X[3], X[7], X[11], X[15] = X3, X7, X11, X15
    w = [rng.getrandbits(32) for _ in range(16)]
    w[4], w[13], w[14], w[15] = W4, W13, 0, 0
    w5p = (w[5] + W4 - W4P) & M
    wp = list(w); wp[4] = W4P; wp[5] = w5p
    m1 = [w[i] for i in P]; m1p = [wp[i] for i in P]
    tr, trp = {}, {}
    Y = round_from(X, m1, tr, 0)  # note: "round" here is round 1 (second); trace index 0..7 = C0..C3,E0..E3 offset
    return X, w, wp, m1, m1p
