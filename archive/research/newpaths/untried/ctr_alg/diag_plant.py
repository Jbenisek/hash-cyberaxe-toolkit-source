#!/usr/bin/env python3
"""diag_plant.py (untried/ctr_alg; research only) - why bplant() found no beta* plant in 60 s.
For tau#0: over random (q, h1) with (1), the count n3 of h2 with (3) given g1 (exact automaton count); over member y,
the count n2 of e2 with (2) given (y, g1) (exact count); the expected number of plants per (q, h1, y) = sum n2*n3/2^32.
"""
import os, random, sys, time
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e3sat as X  # noqa: E402
S, M, ETA, DY3 = X.S, X.M, X.ETA, X.DY3
rng = random.Random(3)
g, eps, tau = X.TARGETS[0]
t0 = time.perf_counter()
n3s, pairs = [], []
while len(n3s) < 300:
    q, h1 = rng.getrandbits(32), rng.getrandbits(32)
    if ((q + h1) & M) ^ ((q + (h1 ^ ETA)) & M) != g:
        continue
    g1 = (q + h1) & M
    n3 = X.count_add_xor(g1, g1 ^ g, X.DH2, tau)
    n3s.append(n3); pairs.append((q, h1, g1, n3))
nz = [n for n in n3s if n]
print(f'(q,h1) with (1): 300 in {time.perf_counter() - t0:.1f} s; n3 = 0 for {300 - len(nz)}; nonzero n3: '
      f'min {min(nz) if nz else 0}, median {sorted(nz)[len(nz) // 2] if nz else 0}, max {max(nz) if nz else 0}, '
      f'mean over all {sum(n3s) / 300:.1f} (LM 2^32 * 2^-22 = 1024)')
exp_total, ys = 0.0, 0
n2s = []
for q, h1, g1, n3 in [p for p in pairs if p[3]][:20]:
    for _ in range(50):
        y = S.member(rng); ys += 1
        f1 = X.ror(y ^ g1, 12); f1b = X.ror(y ^ (g1 ^ g), 12)
        K = (DY3 + f1b - f1) & M
        n2 = X.count_add_xor(0, K, 0, eps)
        n2s.append(n2)
        exp_total += n2 * n3 / 2 ** 32
nz2 = [n for n in n2s if n]
print(f'y samples {ys} on 20 (q,h1) with n3 > 0: n2 = 0 for {ys - len(nz2)}; nonzero n2 median '
      f'{sorted(nz2)[len(nz2) // 2] if nz2 else 0}, max {max(nz2) if nz2 else 0}; expected plants per (q,h1,y) '
      f'{exp_total / ys:.2e} (if (2) and (3) were independent)')
