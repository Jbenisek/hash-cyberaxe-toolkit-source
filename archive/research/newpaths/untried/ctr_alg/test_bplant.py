#!/usr/bin/env python3
"""test_bplant.py (untried/ctr_alg; research only) - (a) closed-form K test vs exact automaton count on random K;
(b) one beta* plant per tau with a 40 s budget each, timed."""
import os, random, sys, time
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e3sat as X  # noqa: E402
rng = random.Random(1)
mism = 0
for _ in range(3000):
    K = rng.getrandbits(32) | 1 if rng.random() < 0.5 else rng.getrandbits(32)
    if rng.random() < 0.5:                      # force some compatible K: build K from a random x with the carries
        x = rng.getrandbits(32)
        K = ((x ^ X.EPS) - x) & X.M            # then x + K == x ^ eps, so x ^ (x + K) == eps
    mism += X.k_ok(K) != (X.count_add_xor(0, K, 0, X.EPS) > 0)
print(f'(a) closed-form K test vs automaton count on 3000 K: mismatches {mism}')
for k in range(7):
    t0 = time.perf_counter()
    r = X.bplant(rng, k, 40.0)
    print(f'(b) tau#{k}: {"none" if r is None else "y %08x q %08x w8 %08x h1 %08x after %d (q,h1), %d y" % r} '
          f'in {time.perf_counter() - t0:.1f} s', flush=True)
