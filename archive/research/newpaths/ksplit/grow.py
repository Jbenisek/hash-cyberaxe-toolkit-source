"""Heuristic: grow proper closed regions keeping delta <= D (lower bound on the largest such region).
Usage: python grow.py <fixed|outhalf> <plain|tables> <D> <trials> <seed>"""
import random, sys
from kmodel import Sys

v, m, D, trials, seed = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
S = Sys(v, m)
pc = lambda x: bin(x).count("1")
rng = random.Random(seed)
delta = lambda X: pc(X) - S.ein(X)
best = (0, 0)
for t in range(trials):
    R = 0
    while True:
        cands = [w for w in range(S.N) if not (R >> w) & 1]
        rng.shuffle(cands)
        grown = False
        for w in cands:
            R2 = S.closure(R | (1 << w))
            if R2 != S.ALL and delta(R2) <= D:
                R = R2
                grown = True
                break
        if not grown:
            break
    if pc(R) > best[0]:
        best = (pc(R), R)
        print("trial", t, "size", pc(R), "delta", delta(R), flush=True)
print("BEST size", best[0], "delta", delta(best[1]))
print("region:", " ".join(S.nm(best[1])))
