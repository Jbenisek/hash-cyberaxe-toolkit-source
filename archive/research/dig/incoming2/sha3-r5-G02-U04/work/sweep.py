# sweep.py (SHA-256 d7a5884dc8bba53e...)
"""Arithmetic count of the multi-pass E block (mirrors e_blk's counted ops) for (LB, EP, NRES); spill rule:
a step needs x, a load temporary and one address register per B-dependent level: spills = max(0, 2 + dy - (64 - resident))."""
import math, itertools, sys
from collections import Counter
CN = [[math.comb(n, k) for k in range(5)] for n in range(30)]
def pos(i):
    b = []
    while len(b) < 4 and i:
        b.append((i & -i).bit_length() - 1); i &= i - 1
    return b
def cands(LB):
    fr = Counter()
    for r in range(1, 1 << LB):
        b = pos((1 << LB) * 0b1111 + r)
        for w in range(1, len(b) + 1):
            s = b[:w]
            if max(s) < LB and w < 4:
                rk = sum(CN[s[v]][v + 1] for v in range(w))
                top = (w == len(b))
                fr[(w, rk)] += 0 if top else 2   # lower level: saves load+store; top: saves load but store at pass end
                if top: fr[(w, rk)] += 1
    return [k for k, _ in fr.most_common()]
def block(LB, EP, NRES, spill=2):
    C = cands(LB); RES = set(C[:NRES])
    sizes = [24 * (p + 1) // EP - 24 * p // EP for p in range(EP)]
    tot = 0
    for p, m in enumerate(sizes):
        nres = m * (1 + NRES)
        if nres > 62: return None
        tot += nres
        for r in range(1 << LB):
            b = pos((1 << LB) * 0b1111 + r)
            d, dy = len(b), sum(q >= LB for q in b)
            rk = [sum(CN[b[v]][v + 1] for v in range(w + 1)) for w in range(d)]
            tot += dy + 2 * max(0, spill + dy - (64 - nres))
            per = 0
            for w in range(d, 0, -1):
                res = (w, rk[w - 1]) in RES
                per += (0 if res else 1) if w == d else (1 if res else 3)
            tot += m * (per + 1) + (m - 1) + (2 if p else 0) + (1 if p < EP - 1 else 2)
        tot += m + m * sum(1 for (w, q) in RES if w < 4)
    return tot, sorted(RES, key=C.index)
if __name__ == '__main__':
    for LB in map(int, sys.argv[1:]):
        best = None
        for EP in (4, 5, 6, 7, 8, 9, 10, 11, 12):
            for NRES in range(0, 30):
                out = block(LB, EP, NRES)
                if out is None: break
                t = out[0]
                if best is None or t < best[0]: best = (t, EP, NRES)
                if NRES == int(62 / (24 // EP)) - 1 or EP in (6, 8) and NRES in (14, 18, 19):
                    print(LB, EP, NRES, t, round(t / (1 << LB), 2), flush=True)
        print('best', LB, best, round(best[0] / (1 << LB), 3))
