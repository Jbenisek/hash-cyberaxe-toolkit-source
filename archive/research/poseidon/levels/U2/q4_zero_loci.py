"""Q4: zero-sensitivity loci Z_{k,i} = {(nk,rho): S-box input of lane i in round k is 0}, k=1,2,3, i=0,1,2 on toys (exhaustive).
   S-box input of round k lane i = (state after R_{k-1}.M)_i + c_{k,i}  (= step 'Rk.C')."""
import sys, itertools
import numpy as np
from toylib import *
def run(q, seed):
    T = Toy(q, seed); st = dict(T.steps(4))
    Z = {}
    for k in (1, 2, 3):
        for i in range(3):
            Z[(k, i)] = (st[f'R{k}.C'][i] == 0)
    names = sorted(Z)
    sizes = {n: int(Z[n].sum()) for n in names}
    pair = {(a, b): int((Z[a] & Z[b]).sum()) for a, b in itertools.combinations(names, 2)}
    trip_same = {k: int((Z[(k, 0)] & Z[(k, 1)] & Z[(k, 2)]).sum()) for k in (1, 2, 3)}
    trip_all = sum(1 for a, b, c in itertools.combinations(names, 3) if (Z[a] & Z[b] & Z[c]).any())
    # concurrency criterion for R1 : (M^-1 c1)_2 == -K  (K = (cap + c02)^5)
    Mi = None
    return sizes, pair, trip_same, trip_all
if __name__ == '__main__':
    qs = [int(x) for x in sys.argv[1].split(',')]; seeds = int(sys.argv[2])
    for q in qs:
        tot_sz = {}; pair_counts = []; pairs_by_type = {}; trips = {1: [], 2: [], 3: []}; tall = 0
        for s in range(1, seeds + 1):
            sizes, pair, ts, ta = run(q, s)
            for n, v in sizes.items(): tot_sz.setdefault(n, []).append(v)
            for (a, b), v in pair.items():
                typ = (a[0], b[0])
                pairs_by_type.setdefault(typ, []).append(v)
            for k in (1, 2, 3): trips[k].append(ts[k])
            tall += ta
        print(f"=== q={q}, {seeds} seeds ===")
        for n in sorted(tot_sz):
            v = tot_sz[n]; print(f"  |Z_R{n[0]},lane{n[1]}|: min {min(v)} mean {sum(v)/len(v):.2f} max {max(v)}   (q = {q})")
        for typ, v in sorted(pairs_by_type.items()):
            print(f"  pair intersections round{typ[0]} x round{typ[1]}: n={len(v)} min {min(v)} mean {sum(v)/len(v):.3f} max {max(v)} ; histogram {dict(sorted({x: v.count(x) for x in set(v)}.items()))}")
        for k in (1, 2, 3):
            v = trips[k]; print(f"  triple (all 3 lanes of round {k} zero at once): number of seeds with >=1 point: {sum(1 for x in v if x)}/{len(v)} ; mean points {sum(v)/len(v):.4f}")
        print(f"  triples among all 9 curves with a common point: {tall} (over {seeds} seeds, 84 triples each)")
