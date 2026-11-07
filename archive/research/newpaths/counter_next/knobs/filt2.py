"""filt2.py (counter_next/knobs; research only): the share of outer steps of the EXISTING cube program that can
succeed at all, from two exact necessary conditions per beta* outcome t:
  A_t(Y9): some h1 gives g1 ^ g1' = dg1_t                     (exact automaton, as g1exact.py)
  B_t(c) : some f1 gives (c + f1) ^ (c' + (f1 ^ phi_t)) = eps  (c = e1 + w8, c' = c + DY3; exact DP, as w8sel.py)
A success with outcome t needs both, so outer steps with no t meeting both can be skipped.  Y9 and c are sampled
uniformly and independently (outer-step words); kept share = Pr[exists t: A_t and B_t].
usage: python -B filt2.py NY NC SEED
"""
import sys, random, math
from collections import Counter
import numpy as np
sys.dont_write_bytecode = True
import e3dfs as D

NY, NC, seed = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
DY3 = (D.Y3B - D.Y3) & D.M32
rows, _ = D.load_targets()
bstar = [r for r in rows if r[1] == 0x18b0e098]
T = [D.outcome_target(r[2], r[3]) for r in bstar]
W = [r[0] for r in bstar]
rng = random.Random(seed)
pa = Counter()
for _ in range(NY):
    sols, _ = D.search(0, rng.getrandbits(32), 0, T, g1only=True)
    m = 0
    for _, ti in sols:
        m |= 1 << ti
    pa[m] += 1
nrng = np.random.default_rng(seed)
c = nrng.integers(0, 2**32, size=NC, dtype=np.uint64)
cp = (c + np.uint64(DY3)) & np.uint64(D.M32)
pbm = np.zeros(NC, dtype=np.int64)
for ti, t in enumerate(T):
    phi, eps = D.ror(t[0], 12), t[1]
    v = np.zeros((NC, 2, 2), dtype=bool)
    v[:, 0, 0] = True
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
                    for a in (0, 1):
                        for b in (0, 1):
                            nv[:, a, b] |= w & ok & ((sa >> 1) == a) & ((sb >> 1) == b)
        v = nv
    pbm |= v.any(axis=(1, 2)).astype(np.int64) << ti
pb = Counter(pbm.tolist())
kept = sum(fa * fb for ma, fa in pa.items() for mb, fb in pb.items() if ma & mb) / (NY * NC)
ka = sum(f for m, f in pa.items() if m) / NY
kb = sum(f for m, f in pb.items() if m) / NC
print(f'beta* outcomes {len(T)}; Y9 sampled {NY}, c sampled {NC}')
print(f'  Y9 feasible for some t: {ka:.5f} (2^{math.log2(ka):.3f});  c feasible for some t: {kb:.5f} (2^{math.log2(kb):.3f})')
print(f'  outer step feasible for some t on BOTH (kept share): {kept:.6f} = 2^{math.log2(kept):.3f}')
print(f'  gain for the cube program (success mass / kept share): 2^{-math.log2(kept):.3f}')
for ti, r in enumerate(bstar):
    a = sum(f for m, f in pa.items() if m >> ti & 1) / NY
    b = sum(f for m, f in pb.items() if m >> ti & 1) / NC
    print(f'  tau {r[2]:08x}: A {a:.5f}, B {b:.5f}, both {a * b:.2e}')
