"""w8sel.py (counter_next/knobs; research only): how much is choosing w8 per outer step worth?

v13 solved per outer step (a 2^-13 filter on outer steps) lets w8 be prescribed next to Y4 (knobs_model_out.txt).
w8 enters E3 only in e2 = e1 + f1 + w8 = c + f1 with c = e1 + w8, c' = c + DY3 (DY3 = Y3' - Y3).  First-order
measure: P2(c) = Pr_f1[(c + f1) ^ (c' + (f1 ^ phi)) = eps] with f1 uniform and phi = ROR(dg1_t, 12) the f1
difference of target t.  Exact per c by a 4-state carry DP over the 32 bits of f1; distribution over c sampled.
Reports, per beta* target, E[P2], the best sampled P2 and the mean over the top 2^-k fraction of c.
usage: python -B w8sel.py NC SEED
"""
import sys, random, math
import numpy as np
sys.dont_write_bytecode = True
import e3dfs as D

NC, seed = int(sys.argv[1]), int(sys.argv[2])
DY3 = (D.Y3B - D.Y3) & D.M32
rows, _ = D.load_targets()
bstar = [r for r in rows if r[1] == 0x18b0e098]
rng = np.random.default_rng(seed)
c = rng.integers(0, 2**32, size=NC, dtype=np.uint64)
cp = (c + np.uint64(DY3)) & np.uint64(D.M32)
print(f'DY3 {DY3:08x}; {NC} sampled c = e1 + w8')
out = []
for r in bstar:
    tau, eps = r[2], r[3]
    dg1 = D.outcome_target(tau, eps)[0]
    phi = D.ror(dg1, 12)
    # state counts: v[ca][cb] (number of f1 prefixes), shape (NC, 2, 2)
    v = np.zeros((NC, 2, 2), dtype=np.float64)
    v[:, 0, 0] = 1.0
    for i in range(32):
        cb_ = ((c >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
        cpb = ((cp >> np.uint64(i)) & np.uint64(1)).astype(np.int64)
        pb, eb = (phi >> i) & 1, (eps >> i) & 1
        nv = np.zeros_like(v)
        for ka in (0, 1):
            for kb in (0, 1):
                w = v[:, ka, kb]
                for fb in (0, 1):
                    sa = cb_ + fb + ka
                    sb = cpb + (fb ^ pb) + kb
                    ok = ((sa & 1) ^ (sb & 1)) == eb
                    na, nb = sa >> 1, sb >> 1
                    for a in (0, 1):
                        for b in (0, 1):
                            sel = ok & (na == a) & (nb == b)
                            nv[:, a, b] += np.where(sel, w, 0.0)
        v = nv
    P2 = v.sum(axis=(1, 2)) / 2**32
    m = P2.mean()
    srt = np.sort(P2)[::-1]
    line = f'tau {tau:08x}: phi {phi:08x}; E[P2] = 2^{math.log2(m):.3f}; max sampled 2^{math.log2(srt[0]):.3f} ' \
           f'(x{srt[0] / m:.1f})'
    for k in (4, 8, 12):
        n = max(1, NC >> k)
        line += f'; top 2^-{k}: x{srt[:n].mean() / m:.2f}'
    line += f'; share with P2 = 0: {np.mean(P2 == 0):.3f}'
    out.append(line)
    print(line)
