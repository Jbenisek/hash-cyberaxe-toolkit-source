'''Block-counter parametrisation (exact, word level, own b3.py).  The counter word T enters only round 0, as the d input
of column G0 (T0, with m0 m1) or G1 (T1, with m2 m3).  For any new T the column outputs can be kept by re-choosing
(x, y):  a1' = T' ^ rotl(d1, 16), x' = a1' - a - b, y' = a2 - a1' - b1.  This is the whole freedom the counter adds.
Test on random base points: round 0 is then unchanged, but x', y' are message words that round 1 reuses
(m0 -> round-1 column 2 y -> Y14, Y6;  m2 -> round-1 column 0 x -> Y4, Y12;  m3 -> round-1 column 1 x -> Y9, Y1).'''
import random
from b3 import point, W4, W13, M, rotl, E3IN, PINS
HELD = list(PINS) + [E3IN['Y4'], E3IN['Y9'], E3IN['Y14']]
def move(m, T0, T1, col, Tn):
    tr = point(m, T0, T1); g = 'R0C%d' % col
    a1n = Tn ^ rotl(tr[g + '.d1'], 16)
    iv = [0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a, 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19]
    a, b = iv[col], iv[col + 4]
    xi, yi = (0, 1) if col == 0 else (2, 3)
    m2 = list(m); m2[xi] = (a1n - a - b) & M; m2[yi] = (tr[g + '.a2'] - a1n - tr[g + '.b1']) & M
    return tr, (m2, Tn, T1) if col == 0 else (m2, T0, Tn)
rnd = random.Random(5); N = 20000
stats = {0: [0, 0, {}], 1: [0, 0, {}]}
for _ in range(N):
    m = [rnd.getrandbits(32) for _ in range(16)]; m[4], m[13], m[14], m[15] = W4, W13, 0, 0
    T0, T1 = rnd.getrandbits(32), rnd.randrange(1, 1 << 19)
    for col in (0, 1):
        Tn = rnd.getrandbits(32) if col == 0 else rnd.randrange(1, 1 << 19)
        if Tn == (T0 if col == 0 else T1): continue
        tr, (m2, a0, a1) = move(m, T0, T1, col, Tn); tr2 = point(m2, a0, a1)
        r0same = all(tr[k] == tr2[k] for k in tr if k.startswith('R0') and k[3] in 'CD' and k.endswith(('a2', 'b2', 'c2', 'd2')) and k.startswith('R0D'))
        stats[col][0] += r0same
        held_same = all(tr[h] == tr2[h] for h in HELD)
        stats[col][1] += held_same
        for h in HELD:
            if tr[h] != tr2[h]: stats[col][2][h] = stats[col][2].get(h, 0) + 1
names = {v: k for k, v in E3IN.items()}
for col in (0, 1):
    s = stats[col]
    print('counter word T%d moved (%d trials): round-0 output X unchanged in %d; all held words kept in %d; held words broken: %s' %
          (col, N, s[0], s[1], {names.get(k, k): v for k, v in s[2].items()}))
