"""route.py - state-word differences (counter low v12, counter high v13, length v14, flags v15) absorbed in round 0,
and where they go in round 1.  Own code (tb3.py, checked against the organizer's _compress).

For each configuration the BASE side is the parent-like or reference compression; the OTHER side copies the
base message except the absorbing words of each column with a d-difference (x = m[2c], y = m[2c+1]).
Per configuration and word width w:
  r0eq     fraction of trials with the whole 16-word state after round 0 equal (must be 1)
  msgdiff  which round-1 calls see a message difference (x / y)
  per round-1 column call C0..C3: fraction with all four outputs different, with the half-A-friendly pattern
           (C0, C2: a and c equal; C1, C3: b and d equal), with the half-B-friendly pattern (the other two)
  hA, hB   fraction of trials with digest words {0,2,5,7} / {1,3,4,6} equal; full = all 8
Configurations (realisable in the organizer's tree unless marked HYP):
  F_root      chunk root (flags 11, len 64)   vs parent root (flags 12): v15 only          [root level, n1 = 1]
  F_root_L55  chunk root (flags 11, len 55)   vs parent root (flags 12): v14 + v15         [root level]
  N_lo        last chunk t < 2^32 even (flags 3) vs parent (flags 4): v12 + v15            [non-root leaf-vs-parent]
  N_hi        last chunk t = k 2^32 (flags 3)  vs parent (flags 4): v13 + v15              [non-root, t >= 2^32]
  N_hi_k1     same, k = 1
  N_lohi      t = k 2^32 + j, j even != 0: v12 + v13 + v15
  N_hi_L55    t = k 2^32, len 55 vs 64: v13 + v14 + v15
  LEN         the 55/63 pair (same position, same counter, flags 11): v14 only, UNPINNED (reference)
  HYP_hi      v13 only (two leaves with different high counter words; never aligned in the tree)
  HYP_lo      v12 only
Run: python -B route.py  (writes to stdout)
"""
import sys
import time

import numpy as np

from tb3 import Toy, absorb

CONFIGS = [
    # name, base(ctr_lo, ctr_hi, blen, flags), other(ctr_lo, ctr_hi, blen, flags), cols
    ('F_root',     (0, 0, 64, 12), (0, 0, 64, 11), (3,)),
    ('F_root_L55', (0, 0, 64, 12), (0, 0, 55, 11), (2, 3)),
    ('N_lo',       (0, 0, 64, 4), ('even', 0, 64, 3), (0, 3)),
    ('N_hi',       (0, 0, 64, 4), (0, 'k', 64, 3), (1, 3)),
    ('N_hi_k1',    (0, 0, 64, 4), (0, 1, 64, 3), (1, 3)),
    ('N_lohi',     (0, 0, 64, 4), ('even', 'k', 64, 3), (0, 1, 3)),
    ('N_hi_L55',   (0, 0, 64, 4), (0, 'k', 55, 3), (1, 2, 3)),
    ('LEN',        (0, 0, 55, 11), (0, 0, 63, 11), (2,)),
    ('HYP_hi',     (0, 0, 64, 3), (0, 'k', 64, 3), (1,)),
    ('HYP_lo',     (0, 0, 64, 3), ('even', 0, 64, 3), (0,)),
]

R1MSG = [(2, 6), (3, 10), (7, 0), (4, 13), (1, 11), (12, 5), (9, 14), (15, 8)]   # round-1 (x, y) per call
CALLW = [(0, 4, 8, 12), (1, 5, 9, 13), (2, 6, 10, 14), (3, 7, 11, 15)]


def param(toy, rng, n, val, w):
    if val == 'even':
        x = (rng.integers(1, 1 << (w - 1), size=n, dtype=np.uint64) * 2) & int(toy.mask)
        x[x == 0] = 2
        return x.astype(np.uint32)
    if val == 'k':
        hi = min(w, 19)
        return rng.integers(1, 1 << hi, size=n, dtype=np.uint64).astype(np.uint32)
    return val


def run(w, n, batches, seed=7):
    toy = Toy(w)
    rng = np.random.default_rng(seed + w)
    res = {}
    for name, base, other, cols in CONFIGS:
        acc = dict(N=0, r0eq=0, hA=0, hB=0, full=0, mx=np.zeros(8), my=np.zeros(8),
                   all4=np.zeros(4), pA=np.zeros(4), pB=np.zeros(4), none=np.zeros(4), dY=np.zeros(16))
        for _ in range(batches):
            m = [rng.integers(0, 1 << w, size=n, dtype=np.uint64).astype(np.uint32) for _ in range(16)]
            vb = toy.init_state(n, ctr_lo=base[0], ctr_hi=base[1], blen=base[2], flags=base[3])
            vo = toy.init_state(n, ctr_lo=param(toy, rng, n, other[0], w), ctr_hi=param(toy, rng, n, other[1], w),
                                blen=other[2], flags=other[3])
            mo = absorb(toy, vb, vo, m, cols)
            rb = toy.compress(vb, m)
            ro = toy.compress(vo, mo)
            eq0 = np.ones(n, bool)
            for i in range(16):
                eq0 &= rb['X'][i] == ro['X'][i]
            acc['r0eq'] += int(eq0.sum())
            # round-1 message differences (permuted schedule)
            for ci, (xi, yi) in enumerate(R1MSG):
                acc['mx'][ci] += int((m[xi] != mo[xi]).sum())
                acc['my'][ci] += int((m[yi] != mo[yi]).sum())
            Yb, Yo = rb['Y'], ro['Y']
            dY = [Yb[i] != Yo[i] for i in range(16)]
            for i in range(16):
                acc['dY'][i] += int(dY[i].sum())
            for ci, (a, b, c, d) in enumerate(CALLW):
                da, db, dc, dd = dY[a], dY[b], dY[c], dY[d]
                acc['all4'][ci] += int((da & db & dc & dd).sum())
                acc['none'][ci] += int((~da & ~db & ~dc & ~dd).sum())
                if ci in (0, 2):
                    A = ~da & ~dc
                    B = ~db & ~dd
                else:
                    A = ~db & ~dd
                    B = ~da & ~dc
                acc['pA'][ci] += int(A.sum())
                acc['pB'][ci] += int(B.sum())
            ob, oo = rb['out'], ro['out']
            hA = (ob[0] == oo[0]) & (ob[2] == oo[2]) & (ob[5] == oo[5]) & (ob[7] == oo[7])
            hB = (ob[1] == oo[1]) & (ob[3] == oo[3]) & (ob[4] == oo[4]) & (ob[6] == oo[6])
            acc['hA'] += int(hA.sum())
            acc['hB'] += int(hB.sum())
            acc['full'] += int((hA & hB).sum())
            acc['N'] += n
        res[name] = acc
    return res


def fmt_rate(k, N):
    if k == 0:
        return '0'
    if k == N:
        return '1'
    return '%d (2^%.1f)' % (k, np.log2(k / N))


def report(w, res):
    print('=' * 110)
    print('w = %d' % w)
    for name, acc in res.items():
        N = acc['N']
        msg = ' '.join('%s%s%s' % (('C%d' % i) if i < 4 else ('E%d' % (i - 4)),
                                     '.x' if acc['mx'][i] else '', '.y' if acc['my'][i] else '')
                       for i in range(8) if acc['mx'][i] or acc['my'][i])
        print('%-11s N=%d r0eq=%s  round-1 message diffs: %s' % (name, N, fmt_rate(acc['r0eq'], N), msg or 'none'))
        dyw = ''.join('x' if acc['dY'][i] == N else ('.' if acc['dY'][i] == 0 else 'p') for i in range(16))
        print('            dY0..15 (x = always differs, p = sometimes, . = never): %s' % dyw)
        for ci in range(4):
            if acc['none'][ci] == N:
                continue
            print('            C%d: all4 differ %s | half-A pattern %s | half-B pattern %s'
                  % (ci, fmt_rate(int(acc['all4'][ci]), N), fmt_rate(int(acc['pA'][ci]), N),
                     fmt_rate(int(acc['pB'][ci]), N)))
        print('            digest half A equal %s | half B equal %s | full %s'
              % (fmt_rate(acc['hA'], N), fmt_rate(acc['hB'], N), fmt_rate(acc['full'], N)))
    sys.stdout.flush()


if __name__ == '__main__':
    plan = [(32, 1 << 18, 4), (8, 1 << 20, 16), (10, 1 << 20, 16), (12, 1 << 20, 16), (16, 1 << 20, 16)]
    for w, n, b in plan:
        t0 = time.time()
        res = run(w, n, b)
        report(w, res)
        print('   (%.0f s)' % (time.time() - t0))
