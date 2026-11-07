"""Q6: exact polynomial relations among lanes of different steps, toy F_q, all q^2 points (provable lower bounds via row subsets).
   Part A: affine dimension (rank of [1, lanes]) of each step and of unions of steps.
   Part B: least total degree of a polynomial relation among the 6 variables (R1.M lanes, R2.M lanes)."""
import sys, itertools, time
import numpy as np
from toylib import *
q = int(sys.argv[1]); seed = int(sys.argv[2])
T = Toy(q, seed); st = dict(T.steps(4)); N = q * q
rng = np.random.default_rng(5)
rows_aff = rng.choice(N, size=min(N, 400), replace=False)
def affdim(names):
    cols = [np.ones(N, dtype=np.int64)]
    for n in names: cols += [st[n][i] for i in range(3)]
    Mx = np.stack([c[rows_aff] for c in cols], axis=1)
    return rank_mod(Mx, q) - 1, len(cols) - 1
print(f"== Part A: q={q} seed={seed}: affine dimension of lane sets (dimension of affine span of the point set; number of variables)")
inits = ['init']
for n in ['init', 'R0.C', 'R0.S', 'R0.M', 'R1.C', 'R1.S', 'R1.M', 'R2.C', 'R2.S', 'R2.M', 'R3.C', 'R3.S', 'R3.M']:
    print(f"  {n:6s}: affine dim {affdim([n])[0]} of 3")
print("  pairs of steps (union of 6 lanes; affine dim of 6 would mean NO affine relation among them):")
names = ['R0.S', 'R0.M', 'R1.S', 'R1.M', 'R2.S', 'R2.M', 'R3.M']
for a, b in itertools.combinations(names, 2):
    d, n = affdim([a, b])
    print(f"  {a:5s} + {b:5s}: affine dim {d} of {n}  -> {n-d} independent affine relations")
# Part B
def mons_nv(nv, d):
    out = []
    for dd in range(d + 1):
        for c in itertools.combinations_with_replacement(range(nv), dd): out.append(c)
    return out
def eval_mons(vars_, mons, rows):
    X = [v[rows] % q for v in vars_]
    cache = {(): np.ones(len(rows), dtype=np.int64)}
    out = np.empty((len(rows), len(mons)), dtype=np.int64)
    for j, c in enumerate(mons):
        if c not in cache:
            cache[c] = cache[c[:-1]] * X[c[-1]] % q
        out[:, j] = cache[c]
    return out
vars6 = [st['R1.M'][i] for i in range(3)] + [st['R2.M'][i] for i in range(3)]
print(f"== Part B: q={q}: least degree of a nonzero polynomial relation among (R1.M lanes, R2.M lanes) [6 variables]")
for d in range(1, 6):
    mons = mons_nv(6, d); m = len(mons)
    # reduced monomials only: exponent < q holds automatically (d<=5<q)
    nrows = min(N, m + 80)
    rows = rng.choice(N, size=nrows, replace=False)
    Mx = eval_mons(vars6, mons, rows); t0 = time.time()
    rk = rank_mod(Mx, q)
    msg = f"  degree <= {d}: {m} monomials, rank {rk} on {nrows} points"
    if rk == m: msg += " -> no relation (PROVED)"
    else:
        ker = kernel_mod(Mx, q); good = 0
        for v in ker:
            ok = True
            for s in range(0, N, 20000):
                if (eval_mons(vars6, mons, np.arange(s, min(N, s + 20000))).dot(v) % q).any(): ok = False; break
            good += ok
        msg += f", nullity {m-rk}, of which vanish on all {N} points: {good} (kernel basis vectors checked)"
    print(msg + f" t={time.time()-t0:.1f}s", flush=True)
    if rk < m and good: break
