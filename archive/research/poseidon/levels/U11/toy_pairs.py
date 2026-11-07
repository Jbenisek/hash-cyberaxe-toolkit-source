"""U11: follow all pairs that agree in lane 0 after a chosen level through the later levels (toy, exhaustive).
Usage: python toy_pairs.py q seed r level_name   e.g. 257 1 1 R3"""
import sys, numpy as np
from collections import Counter
from toy_u11 import make_toy, run, sched

def main(q, seed, r, lvl):
    M, RC = make_toy(q, seed)
    cap = (1 << 65) % q
    nk, rho = np.meshgrid(np.arange(q, dtype=np.int64), np.arange(q, dtype=np.int64), indexing='ij')
    nk = nk.ravel(); rho = rho.ravel()
    lv = run(q, M, RC, r, nk, rho, cap)
    names = [f"R{i}" for i, _ in lv]
    k0 = names.index(lvl)
    inv = np.zeros(q, dtype=np.int64)
    for a in range(1, q): inv[a] = pow(a, -1, q)
    trail = (M[0][2], (-M[0][1]) % q)      # (d1,d2) direction in which (M d)_0 = 0 when d0=0
    L0 = lv[k0][1][0]
    order = np.argsort(L0, kind='stable'); sl = L0[order]
    bounds = np.flatnonzero(np.diff(sl)) + 1
    groups = np.split(order, bounds)
    tot = 0
    agree = Counter(); wt_after = {n: Counter() for n in names[k0:]}
    dircount = Counter(); lane0zero_S_in = Counter()
    trail_pairs = 0; trail_and_agree_next = 0
    S = [lv[k][1] for k in range(len(lv))]
    for g in groups:
        n = len(g)
        if n < 2: continue
        a, b = np.triu_indices(n, 1)
        ia = g[a]; ib = g[b]
        tot += len(ia)
        # direction at level k0
        d1 = (S[k0][1][ia] - S[k0][1][ib]) % q; d2 = (S[k0][2][ia] - S[k0][2][ib]) % q
        # direction id: d2/d1 (d1 != 0) or 'inf'
        dirid = np.where(d1 != 0, d2 * inv[d1] % q, q)
        dc = np.bincount(dirid, minlength=q + 1)
        for i in range(q + 1): dircount[i] += int(dc[i])
        ontrail = (d1 * trail[1] - d2 * trail[0]) % q == 0
        trail_pairs += int(ontrail.sum())
        for k in range(k0, len(lv)):
            d = [(S[k][j][ia] - S[k][j][ib]) % q for j in range(3)]
            w = (d[0] != 0).astype(int) + (d[1] != 0) + (d[2] != 0)
            for wv, cnt in zip(*np.unique(w, return_counts=True)): wt_after[names[k]][(int(wv), bool(d[0][0] == 0) if False else None)] += int(cnt)
            agree[names[k]] += int((d[0] == 0).sum())
            if k == k0 + 1: trail_and_agree_next += int(((d[0] == 0) & ontrail).sum())
    print(f"## q={q} seed={seed} r={r} pairs equal in lane0 after {lvl}: {tot} (expected N(N-1)/2/q = {q*q*(q*q-1)//2/q:.0f})")
    print("pair count with difference (d1,d2) on the trail direction (M d)_0=0:", trail_pairs, " expected tot/(q+1) =", round(tot / (q + 1), 1))
    nxt = names[k0 + 1]
    print(f"agree at next level {nxt}: {agree[nxt]}   ; of those on trail direction: {trail_and_agree_next}  (PROVED equal when the next round is partial)")
    print("direction histogram at", lvl, ": min", min(dircount.values()), "max", max(dircount.values()), "mean", round(tot / (q + 1), 1),
          " d1=0 (inf):", dircount[q], " d2=0 (slope 0):", dircount[0])
    print("level | pairs still equal in lane0 | fraction | 1/q | weight histogram of difference (nonzero lanes)")
    for k in range(k0, len(lv)):
        wh = {w: v for (w, _), v in sorted(wt_after[names[k]].items())}
        print(f"{names[k]:>4} | {agree[names[k]]} | {agree[names[k]]/tot:.5f} | {1/q:.5f} | {wh}")

if __name__ == '__main__':
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])
