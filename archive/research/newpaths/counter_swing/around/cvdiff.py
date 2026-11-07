"""cvdiff.py - chaining-value differences as the difference source (the multi-block / two-block "swing").
A non-first block of a chunk starts from a chained CV h. Two messages whose chunks differ in an earlier block
reach the last block with h != h'. Lemma G1 (b and c inputs of a G call are functions of its output) forces
h4..h7 = h'4..h'7; a difference in h0..h3 (the a inputs) is absorbed by the column's x word alone.
Also the CHUNK_START case: a multi-block last block (flags 2, cv = chained h) vs a one-block last chunk
(flags 3, cv = IV) at the same position; it needs h4..h7 = IV4..IV7 (planted here, costs 2^128 for real).
Prints round-0 equality, the round-1 message differences and the dY pattern at w = 32, and pattern rates at w = 8.
Run: python -B cvdiff.py
"""
import numpy as np

from tb3 import Toy

R1MSG = [(2, 6), (3, 10), (7, 0), (4, 13), (1, 11), (12, 5), (9, 14), (15, 8)]
CALLW = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]


def absorb_a_d(toy, vb, vo, m, cols):
    """columns may differ in a (v[c]) and/or d (v[c+12]); b, c must be equal."""
    mk = toy.mask
    mo = [x.copy() for x in m]
    for c in cols:
        a, ao, b = vb[c], vo[c], vb[c + 4]
        a1 = (a + b + m[2 * c]) & mk
        a1o = a1 ^ vb[c + 12] ^ vo[c + 12]
        mo[2 * c] = (a1o - ao - b) & mk
        mo[2 * c + 1] = (m[2 * c + 1] + a1 - a1o) & mk
    return mo


def run(w, n, batches, cfg, rng):
    toy = Toy(w)
    name, words, flags_pair = cfg
    tot = dict(N=0, r0=0, hA=0, hB=0)
    mx = np.zeros(8)
    my = np.zeros(8)
    dYc = np.zeros(16)
    pA = np.zeros(4)
    pB = np.zeros(4)
    for _ in range(batches):
        m = [rng.integers(0, 1 << w, size=n, dtype=np.uint64).astype(np.uint32) for _ in range(16)]
        h = [rng.integers(0, 1 << w, size=n, dtype=np.uint64).astype(np.uint32) for _ in range(8)]
        if words == 'iv':
            ho = [np.full(n, np.uint32(x)) for x in toy.iv]
            for i in range(4, 8):
                h[i] = ho[i].copy()                      # planted h4..h7 = IV4..IV7
        else:
            ho = [x.copy() for x in h]
            for c in words:                              # a nonzero XOR difference in word c
                ho[c] = h[c] ^ rng.integers(1, 1 << w, size=n, dtype=np.uint64).astype(np.uint32)
        vb = toy.init_state(n, cv=h, blen=64, flags=flags_pair[0])
        vo = toy.init_state(n, cv=ho, blen=64, flags=flags_pair[1])
        cols = [c for c in range(4) if (words == 'iv') or (c in words) or flags_pair[0] != flags_pair[1] and c == 3]
        mo = absorb_a_d(toy, vb, vo, m, sorted(set(cols)))
        rb, ro = toy.compress(vb, m), toy.compress(vo, mo)
        eq = np.ones(n, bool)
        for i in range(16):
            eq &= rb['X'][i] == ro['X'][i]
        tot['r0'] += int(eq.sum())
        for ci, (xi, yi) in enumerate(R1MSG):
            mx[ci] += int((m[xi] != mo[xi]).sum())
            my[ci] += int((m[yi] != mo[yi]).sum())
        dY = [rb['Y'][i] != ro['Y'][i] for i in range(16)]
        for i in range(16):
            dYc[i] += int(dY[i].sum())
        for ci, (a, b, c, d) in enumerate(CALLW):
            if ci in (0, 2):
                A, B = ~dY[a] & ~dY[c], ~dY[b] & ~dY[d]
            else:
                A, B = ~dY[b] & ~dY[d], ~dY[a] & ~dY[c]
            pA[ci] += int(A.sum())
            pB[ci] += int(B.sum())
        ob_, oo = rb['out'], ro['out']
        tot['hA'] += int(((ob_[0] == oo[0]) & (ob_[2] == oo[2]) & (ob_[5] == oo[5]) & (ob_[7] == oo[7])).sum())
        tot['hB'] += int(((ob_[1] == oo[1]) & (ob_[3] == oo[3]) & (ob_[4] == oo[4]) & (ob_[6] == oo[6])).sum())
        tot['N'] += n
    N = tot['N']
    msg = ' '.join('%s%s%s' % (('C%d' % i) if i < 4 else ('E%d' % (i - 4)), '.x' if mx[i] else '',
                               '.y' if my[i] else '') for i in range(8) if mx[i] or my[i])
    dyw = ''.join('x' if dYc[i] == N else ('.' if dYc[i] == 0 else 'p') for i in range(16))
    act = [ci for ci in range(4) if any(dYc[j] for j in CALLW[ci])]
    pat = ' '.join('C%d A=%d B=%d' % (ci, pA[ci], pB[ci]) for ci in act)
    print('w=%2d %-26s N=%d r0eq=%d  msg: %-22s dY: %s | %s | hA=%d hB=%d'
          % (w, name, N, tot['r0'], msg, dyw, pat, tot['hA'], tot['hB']))


CFGS = [
    ('dh0 (word 0)', (0,), (2, 2)),
    ('dh1', (1,), (2, 2)),
    ('dh2', (2,), (2, 2)),
    ('dh3', (3,), (2, 2)),
    ('dh1+dh3', (1, 3), (2, 2)),
    ('dh1+dh2', (1, 2), (2, 2)),
    ('dh1+dh2+dh3', (1, 2, 3), (2, 2)),
    ('CHUNK_START h4..7=IV planted', 'iv', (2, 3)),
]

if __name__ == '__main__':
    rng = np.random.default_rng(55)
    for cfg in CFGS:
        run(32, 1 << 17, 2, cfg, rng)
    for cfg in CFGS:
        run(8, 1 << 20, 8, cfg, rng)
