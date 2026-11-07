"""Joint lens, step 1: where the rank deficits come from.
- affine rank of K1 and K3 separately (rand, all rows)
- in ctx groups (context, member): which E3/E1 inputs vary with j, rank of K1, K3 and R per group,
  and whether R = 0 satisfies every per-group relation (0 in the group's affine hull)
Run: python explore1_groups.py > explore1_groups_out.txt"""
import sys
sys.dont_write_bytecode = True
import os
import numpy as np
from explore0_rank import load, affine_basis, null_space, fmt_mask

res = load("rand", "res.u32", 4)
keys = load("rand", "keys.u32", 8)
for lab, arr in (("K1", keys[:, :4]), ("K3", keys[:, 4:])):
    rk, base, piv = affine_basis(arr)
    rel = null_space(piv, base)
    print("[rand] affine rank of %s: %d (%d relations)" % (lab, rk, len(rel)))
    for a, c in rel[:50]:
        print("    %s = %d" % (fmt_mask(a), c))

res = load("ctx", "res.u32", 4)
keys = load("ctx", "keys.u32", 8)
ein = load("ctx", "einputs.u32", 9)
names = ("Y1", "Y6", "Y12", "w12", "w5", "Y4", "Y9", "Y14", "w8")
var = {nm: 0 for nm in names}
stats = []
zero_in_hull = 0
k3const = 0
for g in range(256):
    sl = slice(g * 1024, (g + 1) * 1024)
    for i, nm in enumerate(names):
        if len(np.unique(ein[sl, i])) > 1:
            var[nm] += 1
    rR, bR, pR = affine_basis(res[sl])
    r1 = affine_basis(keys[sl, :4])[0]
    r3 = affine_basis(keys[sl, 4:])[0]
    n3 = len(np.unique(np.ascontiguousarray(keys[sl, 4:]).view(np.dtype((np.void, 16)))))
    rel = null_space(pR, bR)
    ok = all(c == 0 for a, c in rel)
    zero_in_hull += ok
    stats.append((rR, r1, r3, n3, len(rel), sum(c for a, c in rel)))
print("[ctx] groups (context, member) where each E input varies with j:", var)
arr = np.array(stats)
print("[ctx] per group: rank R min/median/max %d/%d/%d; rank K1 %d/%d/%d; rank K3 %d/%d/%d; distinct K3 min/median/max %d/%d/%d" % (
    arr[:, 0].min(), np.median(arr[:, 0]), arr[:, 0].max(), arr[:, 1].min(), np.median(arr[:, 1]), arr[:, 1].max(),
    arr[:, 2].min(), np.median(arr[:, 2]), arr[:, 2].max(), arr[:, 3].min(), np.median(arr[:, 3]), arr[:, 3].max()))
print("[ctx] groups whose affine hull of R contains 0 (every relation has constant 0): %d of 256" % zero_in_hull)
print("[ctx] mean number of relations with constant 1 per group: %.2f" % arr[:, 5].mean())
# K1 rank over a whole context (16 members)
for c in range(2):
    sl = slice(c * 16384, (c + 1) * 16384)
    print("[ctx] context %d: rank R %d, rank K1 %d, rank K3 %d" % (c, affine_basis(res[sl])[0], affine_basis(keys[sl, :4])[0], affine_basis(keys[sl, 4:])[0]))
