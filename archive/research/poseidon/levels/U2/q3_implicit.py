"""Q3: least total degree d of a nonzero (reduced) polynomial in 3 variables vanishing on the whole image of the state set after R_k.M (k=0,1,2),
   toy field F_q, all q^2 points.  Method: evaluation matrix on a row subset; rank == #columns on the subset PROVES no such polynomial of degree <= d;
   nullity > 0 gives a candidate kernel vector that is then verified on ALL q^2 points."""
import sys, time
import numpy as np
from toylib import *
q = int(sys.argv[1]); seed = int(sys.argv[2]); kmax = int(sys.argv[3]); dmax = int(sys.argv[4]); dstart = int(sys.argv[5]) if len(sys.argv) > 5 else 1; kmin = int(sys.argv[6]) if len(sys.argv) > 6 else 0
T = Toy(q, seed)
steps = dict(T.steps(4))
rng = np.random.default_rng(1)
N = q * q
t0 = time.time()
for k in range(kmin, kmax + 1):
    pts = steps[f'R{k}.M']
    found = None
    for d in range(dstart, dmax + 1):
        mons = monomials(d, q)
        m = len(mons)
        nrows = min(N, m + 60)
        rows = rng.choice(N, size=nrows, replace=False) if nrows < N else np.arange(N)
        Mx = eval_monomials(pts, mons, q, rows)
        rk = rank_mod(Mx, q)
        if rk == m:
            print(f"q={q} seed={seed} R{k}: degree <= {d}: {m} monomials, rank {rk} on {nrows} sampled points -> NO vanishing polynomial (PROVED for this point set) t={time.time()-t0:.1f}s", flush=True)
            continue
        ker = kernel_mod(Mx, q)
        ok = False
        allrows = np.arange(N)
        for v in ker[:5]:
            # verify on all points in chunks
            good = True
            for s in range(0, N, 20000):
                rr = allrows[s:s + 20000]
                vals = eval_monomials(pts, mons, q, rr).dot(v) % q
                if vals.any(): good = False; break
            if good: ok = True; break
        print(f"q={q} seed={seed} R{k}: degree <= {d}: {m} monomials, rank {rk} on {nrows} sampled points, nullity {m-rk}; verified vanishing on all {N} points: {ok} t={time.time()-t0:.1f}s", flush=True)
        if ok:
            found = d; break
        # else: sampled rows were not enough; use more rows
        rows = np.arange(N) if N <= 4 * m else rng.choice(N, size=4 * m, replace=False)
        Mx = eval_monomials(pts, mons, q, rows); rk = rank_mod(Mx, q)
        print(f"   retry with {len(rows)} rows: rank {rk} of {m}", flush=True)
        if rk < m:
            found = d; print(f"   -> least degree is {d} (kernel persists on {len(rows)} rows)"); break
    print(f"q={q} seed={seed} R{k}: LEAST DEGREE of a vanishing polynomial = {found} (searched up to {dmax}); #points {N}; counting bound: first d with C(d+3,3) > {N} is {next(d for d in range(1,400) if (d+1)*(d+2)*(d+3)//6 > N)}", flush=True)
