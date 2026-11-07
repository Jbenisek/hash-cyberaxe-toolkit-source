"""e3split.py (counter_next/knobs; research only): a cheaper exact E3 search by splitting h1 at bit 12.

The bits of h1 below 12 reach the rest of E3 only through (i) the carry pair into bit 12 of g1 = Y9 + h1 and
g1' = Y9 + h1', (ii) g1 bits 0..11 (-> f1 bits 20..31 -> e2 bits 20..31), (iii) h1 bits 8..11 (-> h2 bits 0..3)
and (iv) g1 bits 0..11 in g2 = g1 + h2.  e2 bits 0..19 depend only on f1 bits 0..19 = (y ^ g1) bits 12..31 and
start with carry 0.  So, per target:
  LOW : all h1 bits 0..11 meeting dg1 bits 0..11, grouped by the carry pair into bit 12 (bit-serial search);
  HIGH: for each carry pair present, all h1 bits 12..31 meeting dg1 bits 12..31 and de2 bits 0..19 (bit-serial);
  JOIN: every (low, high) pair with the same carry pair -> full check of the four E3 differences.
Cost = nodes of LOW + nodes of HIGH + number of JOIN pairs (each a full E3 evaluation, about 30 operations).
Checked against e3dfs.search (plain search, itself checked against the 2^32 brute force) on planted and random
outer steps.
usage: python -B e3split.py check NU SEED   |   python -B e3split.py cost NU SEED NT
"""
import sys, random, math
import numpy as np
sys.dont_write_bytecode = True
import e3dfs as D

U = np.uint64
ETA = D.ETA


def low_part(Y9, tg1):
    cand = np.array([0], dtype=np.uint64)
    nodes = 0
    Y9u, eta = U(Y9), U(ETA)
    for k in range(1, 13):
        cand = np.concatenate([cand, cand | U(1 << (k - 1))])
        nodes += len(cand)
        mk = U((1 << k) - 1)
        dg1 = ((Y9u + cand) & mk) ^ ((Y9u + (cand ^ eta)) & mk)
        cand = cand[dg1 == (U(tg1) & mk)]
        if not len(cand):
            break
    groups = {}
    if len(cand):
        m12 = U(0xfff)
        ca = (((Y9u & m12) + cand) >> U(12)) & U(1)
        cb = (((Y9u & m12) + ((cand ^ eta) & m12)) >> U(12)) & U(1)
        for p in set(zip(ca.tolist(), cb.tolist())):
            sel = (ca == U(p[0])) & (cb == U(p[1]))
            groups[p] = cand[sel]
    return groups, nodes


def high_part(y, Y9, w8, tg1, te2, ca, cb):
    """x = h1 >> 12 (20 bits).  Returns (array of x, nodes)."""
    e1, e1b = U((D.Y3 + y) & D.M32), U((D.Y3B + y) & D.M32)
    Yh, eh, yh, w8u = U(Y9 >> 12), U(ETA >> 12), U(y >> 12), U(w8)
    cand = np.array([0], dtype=np.uint64)
    nodes = 0
    for k in range(1, 21):           # k bits of x known (h1 bits 12 .. 12+k-1)
        cand = np.concatenate([cand, cand | U(1 << (k - 1))])
        nodes += len(cand)
        mk = U((1 << k) - 1)
        g1 = (Yh + cand + U(ca)) & mk
        g1b = (Yh + (cand ^ eh) + U(cb)) & mk
        c = ((g1 ^ g1b) == (U(tg1 >> 12) & mk))
        f1 = (yh ^ g1) & mk
        f1b = (yh ^ g1b) & mk
        e2 = (e1 + f1 + w8u) & mk
        e2b = (e1b + f1b + w8u) & mk
        c &= ((e2 ^ e2b) == (U(te2) & mk))
        cand = cand[c]
        if not len(cand):
            break
    return cand, nodes


def split_search(y, Y9, w8, targets):
    sols, cost = [], dict(low=0, high=0, join=0)
    for ti, t in enumerate(targets):
        groups, n = low_part(Y9, t[0])
        cost['low'] += n
        for (ca, cb), lows in groups.items():
            highs, n = high_part(y, Y9, w8, t[0], t[1], ca, cb)
            cost['high'] += n
            cost['join'] += len(lows) * len(highs)
            for lo in lows.tolist():
                for hi in highs.tolist():
                    h = lo | (hi << 12)
                    if D.e3_full(y, h, Y9, w8) == t:
                        sols.append((h, ti))
    return sols, cost


def main():
    mode = sys.argv[1]
    if mode == 'check':
        NU, seed = int(sys.argv[2]), int(sys.argv[3])
        rng = random.Random(seed)
        rows, _ = D.load_targets(7)
        listed = [D.outcome_target(r[2], r[3]) for r in rows]
        same = 0
        for u in range(NU):
            y, Y9, w8, h = D.rand_member(rng), rng.getrandbits(32), rng.getrandbits(32), rng.getrandbits(32)
            tg = [D.e3_full(y, h, Y9, w8)] + listed
            a, _ = D.search(y, Y9, w8, tg)
            b, _ = split_search(y, Y9, w8, tg)
            same += sorted(a) == sorted(b) and (h, 0) in b
        print(f'split search vs plain search (planted target + 7 listed targets): identical and planted found '
              f'in {same}/{NU} outer steps')
    elif mode == 'cost':
        NU, seed, nt = int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4])
        rows, tot = D.load_targets(nt)
        targets = [D.outcome_target(r[2], r[3]) for r in rows]
        C = sum(r[0] for r in rows) / 2**81
        rng = random.Random(seed)
        tl = th = tj = 0
        plain = 0
        per = []
        for u in range(NU):
            y, Y9, w8 = D.rand_member(rng), rng.getrandbits(32), rng.getrandbits(32)
            _, c = split_search(y, Y9, w8, targets)
            tl += c['low']; th += c['high']; tj += c['join']
            per.append(c['low'] + c['high'] + c['join'])
        a = np.array(per, dtype=float)
        print(f'targets {nt} (C {C:.0f}); outer steps {NU}: mean nodes LOW {tl / NU:.1f}, HIGH {th / NU:.1f}, '
              f'JOIN pairs {tj / NU:.2f}; total mean {a.mean():.1f}, median {np.median(a):.0f}, max {a.max():.0f}')


if __name__ == '__main__':
    main()
