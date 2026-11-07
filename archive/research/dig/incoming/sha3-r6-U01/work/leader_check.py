"""Does the leader's explicit prefix construction (4867f093 note: L3,L4,L6,L7 from L0,L1,L2,L5) satisfy our 128 conditions? Plain (uncomplemented) lanes."""
import random, itertools, json
from sha3lab import *
import q12
F, dirs, conds = q12.setup('F64')
rng = random.Random(5)
rotr = lambda v, r: rotl(v, 64 - r)
def mk(L0, L1, L2, L5, c3, c4, c6, c7, k3):
    X = L0 ^ L5
    L3 = (0x06 if k3 else 0) ^ c3 ^ rotl(X, 1)
    L4 = c4
    L6 = c6
    L7 = L2 ^ rotr(X, 1) ^ c7
    lanes = [L0, L1, L2, L3, L4, L5, L6, L7]
    return sum(l << (64 * i) for i, l in enumerate(lanes))
res = {}
for c3, c4, c6, c7, k3 in itertools.product((0, M64), (0, M64), (0, M64), (0, M64), (0, 1)):
    ok = 0; tot = 0
    for _ in range(20):
        m = mk(rng.getrandbits(64), rng.getrandbits(64), rng.getrandbits(64), rng.getrandbits(64), c3, c4, c6, c7, k3)
        for c in conds:
            r, v = q12.eq_of(F, c)
            tot += 1; ok += (parity(r & m) == v)
    res[(c3 != 0, c4 != 0, c6 != 0, c7 != 0, k3)] = ok / tot
best = sorted(res.items(), key=lambda t: -t[1])[:6]
print(best)
