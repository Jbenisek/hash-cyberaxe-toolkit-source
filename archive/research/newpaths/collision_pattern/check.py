"""check.py: the recovered parameters reproduce every found pair (words from the runs' own code = the saved
message A), every hit is a collision with no construction failure, null trials are valid and almost never collide."""
import numpy as np
from load import hits, feats, col

H = hits()
for W in (8, 10):
    F = feats(W)
    idx, a = F['h']
    bad = 0
    for i, row in zip(idx, a):
        h = H[i]
        A = [int(c) for c in h['A']]
        nb = W // 2
        LEN_A = 7 * W - 1
        wa = [sum(A[j * nb + q] << (2 * q) for q in range(nb) if j * nb + q < LEN_A) for j in range(16)]
        ws = [int(row[9 + j]) for j in range(16)]
        mask = [((1 << (2 * max(0, min(nb, LEN_A - j * nb)))) - 1) for j in range(16)]
        same = all((ws[j] & mask[j]) == wa[j] for j in range(16))
        bad += (not same) or row[7] != 0 or row[8] != 1 or int(h['member']) != row[3] or \
            (int(h['d1']) >= 0 and int(h['d1']) != row[5]) or int(h['t']) != row[6]
    print(f'W={W}: hits {len(a)}: parameters reproduce the saved pair, fail 0, collide: {len(a) - bad} of {len(a)}')
    for k in ('n0', 'n1'):
        if k in F:
            b = F[k][1]
            print(f'  null {k}: {len(b)} trials, construction failures {int((col(b, "fail") != 0).sum())}, '
                  f'collisions among them {int(col(b, "coll").sum())}, t=0 among ctr nulls '
                  f'{int(((col(b, "mode") == 1) & (col(b, "t") == 0)).sum())}')
