#!/usr/bin/env python3
"""U02 Q2: necessity of the C3 pin.  (1) digest-level test: with the Fact P pin, E0/E2 inputs agree, so digest words 0,2,5,7 agree
for A and B for ANY other Y words and messages; (2) single-coordinate ablations of the pin (a1,d1 -> q1; c1,b1 -> q2; W13 -> q3/q4)
and what they break."""
import random, json
from factp import *
def G(s, a, b, c, d, mx, my):
    s[a] = (s[a] + s[b] + mx) & M; s[d] = ror(s[d] ^ s[a], 16); s[c] = (s[c] + s[d]) & M; s[b] = ror(s[b] ^ s[c], 12)
    s[a] = (s[a] + s[b] + my) & M; s[d] = ror(s[d] ^ s[a], 8); s[c] = (s[c] + s[d]) & M; s[b] = ror(s[b] ^ s[c], 7)
def digest_words(Y3, Y7, Y11, Y15, rest, m):
    s = list(rest); s[3], s[7], s[11], s[15] = Y3, Y7, Y11, Y15
    G(s, 0, 5, 10, 15, m[1], m[11]); G(s, 1, 6, 11, 12, m[12], m[5]); G(s, 2, 7, 8, 13, m[9], m[14]); G(s, 3, 4, 9, 14, m[15], m[8])
    return [s[i] ^ s[i + 8] for i in range(8)]
def pins_from(a1, b1, c1, d1):
    X7 = rol(b1, 12) ^ c1; return (a1 - X7 - W4) & M, X7, (c1 - d1) & M, rol(d1, 16) ^ a1
rnd = random.Random(20261012)
rec = c3(PIN['X3'], PIN['X7'], PIN['X11'], PIN['X15'], W4, W13)
base = dict(a1=rec['a1'], b1=rec['b1'], c1=rec['c1'], d1=rec['d1'], w13=W13)
def trial(co, ntr=8):
    X3, X7, X11, X15 = pins_from(co['a1'], co['b1'], co['c1'], co['d1'])
    A = c3(X3, X7, X11, X15, W4, co['w13']); B = c3(X3, X7, X11, X15, W4B, co['w13'])
    deq, beq = A['d2'] == B['d2'], A['b2'] == B['b2']
    same = [0] * 8
    for _ in range(ntr):
        rest = [rnd.getrandbits(32) for _ in range(16)]; m = [rnd.getrandbits(32) for _ in range(16)]
        mB = list(m); mB[5] = (m[5] + W4 - W4B) & M          # w5' = w5 + w4 - w4'
        dA = digest_words(A['a2'], A['b2'], A['c2'], A['d2'], rest, m); dB = digest_words(B['a2'], B['b2'], B['c2'], B['d2'], rest, mB)
        for i in range(8): same[i] += dA[i] == dB[i]
    return deq, beq, [i for i in range(8) if same[i] == ntr], [i for i in range(8) if same[i] == 0]
res = {}
d, b, eq, ne = trial(base, 64)
res['record'] = dict(d2_equal=d, b2_equal=b, digest_words_always_equal=eq, digest_words_never_equal=ne)
print('record pin:', res['record'])
assert d and b and set(eq) == {0, 2, 5, 7}, 'validation: record pin must give equal words 0,2,5,7'
axes = {'a1': 'q1', 'd1': 'q1', 'c1': 'q2', 'b1': 'q2', 'w13': 'q3'}
abl = {}
for ax, q in axes.items():
    bit_rows = []
    for bt in range(32):
        co = dict(base); co[ax] ^= 1 << bt
        d, b, eq, ne = trial(co, 4)
        bit_rows.append((bt, d, b, eq))
    nd = sum(r[1] for r in bit_rows); nb = sum(r[2] for r in bit_rows)
    both = sum(1 for r in bit_rows if r[1] and r[2])
    kept = sum(1 for r in bit_rows if set(r[3]) >= {0, 2, 5, 7})
    # random replacement of the coordinate (20 draws)
    rr = 0
    for _ in range(2000):
        co = dict(base); co[ax] = rnd.getrandbits(32)
        d, b, eq, ne = trial(co, 1) if False else (None, None, None, None)
        X3, X7, X11, X15 = pins_from(co['a1'], co['b1'], co['c1'], co['d1'])
        A = c3(X3, X7, X11, X15, W4, co['w13']); B = c3(X3, X7, X11, X15, W4B, co['w13'])
        rr += A['d2'] == B['d2'] and A['b2'] == B['b2']
    abl[ax] = dict(quarter=q, single_bit_flips_keeping_d2_equal=nd, keeping_b2_equal=nb, keeping_both=both, keeping_digest_0257=kept, random_replacements_keeping_both_of_2000=rr)
    print(ax, abl[ax])
res['ablation'] = abl
json.dump(res, open('necessity.json', 'w'), indent=1)
