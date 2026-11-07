"""Joint lens, step 3: what the per-(context, member) GF(2) relations of R are made of (ctx set, 256 groups of 1024 rows;
grouphull.c shows that 1024 cube points already give the full-cube hull in 64 of 64 groups).
For every relation a.R = const of a group: is a.K1 constant on the group? is a.K3 constant? (R = K1 ^ K3.)
Also: rank of K3 per group, and the hull test with the 2 global relations removed.
Run: python explore3_grouprel.py > explore3_grouprel_out.txt"""
import sys
sys.dont_write_bytecode = True
import numpy as np
from explore0_rank import load, affine_basis, null_space

res = load("ctx", "res.u32", 4)
keys = load("ctx", "keys.u32", 8)


def dots(a, X):
    """a . row for every row of X (n x 4 u32), a = 128-bit python int."""
    acc = np.zeros(len(X), dtype=np.uint32)
    for w in range(4):
        m = np.uint32((a >> (32 * w)) & 0xffffffff)
        acc ^= X[:, w] & m
    acc ^= acc >> 16; acc ^= acc >> 8; acc ^= acc >> 4; acc ^= acc >> 2; acc ^= acc >> 1
    return acc & 1


tot = {"rel": 0, "k1const": 0, "k3const": 0, "both": 0, "neither": 0, "bad_const": 0, "bad_k1side_k3side": 0}
per_group = []
for g in range(256):
    sl = slice(g * 1024, (g + 1) * 1024)
    rk, base, piv = affine_basis(res[sl])
    rel = null_space(piv, base)
    K1, K3 = keys[sl, :4], keys[sl, 4:]
    nb = 0
    for a, c in rel:
        d1, d3 = dots(a, K1), dots(a, K3)
        c1 = d1.min() == d1.max()
        c3 = d3.min() == d3.max()
        tot["rel"] += 1
        tot["k1const"] += c1
        tot["k3const"] += c3
        tot["both"] += c1 and c3
        tot["neither"] += (not c1) and (not c3)
        if c:
            tot["bad_const"] += 1
            nb += 1
            if c1 and c3:
                tot["bad_k1side_k3side"] += 1
    per_group.append((rk, len(rel), nb, affine_basis(K3)[0]))
print("ctx groups: 256 x 1024 rows")
print("relations of R over all groups: %d" % tot["rel"])
print("  a.K1 constant on the group: %d ; a.K3 constant: %d ; both constant (relation splits into an E1 part and an E3 part): %d ; neither: %d" % (
    tot["k1const"], tot["k3const"], tot["both"], tot["neither"]))
print("  relations with constant 1 (they exclude R = 0): %d ; of these, split ones: %d" % (tot["bad_const"], tot["bad_k1side_k3side"]))
arr = np.array(per_group)
print("groups with 0 in the hull: %d of 256" % int((arr[:, 2] == 0).sum()))
print("number of constant-1 relations per group: histogram", dict(zip(*[x.tolist() for x in np.unique(arr[:, 2], return_counts=True)])))
print("rank of K3 per group vs rank of R: corr %.3f ; mean K3 rank %.2f" % (np.corrcoef(arr[:, 0], arr[:, 3])[0, 1], arr[:, 3].mean()))
# per context: are the member groups' verdicts correlated (context-level effect)?
ok = (arr[:, 2] == 0).reshape(16, 16)
print("groups with 0 in hull per context (16 members each):", ok.sum(1).tolist())
