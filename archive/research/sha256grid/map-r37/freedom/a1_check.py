# For every A1 that passes its own dense-part conditions (E5 cell, E5/E6 '+' pair, W9 cell), check that the modular
# differences reaching rows >= 16 through W9 (W9 itself in W16/W25, sigma0(W9) in W24) equal the published ones.

# Publication path adapter: resolve data paths from the extracted source tree.
def _hca_public_path_text(value):
    if "__HCA_WORKSPACE__/" not in value:
        return value
    import os as _hca_os
    from pathlib import Path as _hca_Path
    root = _hca_os.environ.get("HASHCYBERAXE_WORKSPACE")
    if root is None:
        here = _hca_Path(__file__).resolve().parent
        root = next((str(p) for p in (here, *here.parents) if (p / "research").is_dir()), None)
    if root is None:
        raise FileNotFoundError("Extract the research source tree, or set HASHCYBERAXE_WORKSPACE to its archive directory.")
    return value.replace("__HCA_WORKSPACE__/", str(_hca_Path(root).resolve()).replace("\\", "/") + "/")

import importlib.util, numpy as np
P = _hca_public_path_text('__HCA_WORKSPACE__/research/stuck/r37-1f12a09a/pkg/experiments/a0core.py')
spec = importlib.util.spec_from_file_location("a0core", P); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
M = a.M32
tx = a.trace(a.CV0, a.MX); ty = a.trace(a.CV0, a.MY)
Ax = [tx[0][i] for i in range(14)]; Ay = [ty[0][i] for i in range(14)]
Ex = [tx[1][i] for i in range(14)]; Ey = [ty[1][i] for i in range(14)]
m5, v5, d5, p5 = a.CELLS['E'][5]; p6 = a.CELLS['E'][6][3]
mw, vw, dw, _ = a.CELLS['W'][9]
free = [b for b in range(32) if not (m5 >> b) & 1]
idx = np.arange(1 << len(free), dtype=np.uint64)
e5 = np.full(idx.shape, v5, dtype=np.uint64)
for j, b in enumerate(free): e5 |= ((idx >> np.uint64(j)) & np.uint64(1)) << np.uint64(b)
e5 = e5.astype(np.uint32)
q = p5 & p6
ok = ((e5 ^ np.uint32(Ex[6])) & np.uint32(q)) == 0
def rotr(x, n): return ((x >> np.uint32(n)) | (x << np.uint32(32 - n))).astype(np.uint32)
def S1(x): return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)
def s0(x): return rotr(x, 7) ^ rotr(x, 18) ^ (x >> np.uint32(3))
cx = (Ex[9] - Ax[5] - a.S1(Ex[8]) - a.CH(Ex[8], Ex[7], Ex[6]) - a.K[9]) & M
cy = (Ey[9] - Ay[5] - a.S1(Ey[8]) - a.CH(Ey[8], Ey[7], Ey[6]) - a.K[9]) & M
w9x = (np.uint32(cx) - e5).astype(np.uint32); w9y = (np.uint32(cy) - e5).astype(np.uint32)   # E5 equal in both members
ok &= ((w9x & np.uint32(mw)) == np.uint32(vw)) & ((w9x ^ w9y) == np.uint32(dw))
e5ok, w9x, w9y = e5[ok], w9x[ok], w9y[ok]
c5 = (Ax[5] - a.S0(Ax[4]) - a.MAJ(Ax[4], Ax[3], Ax[2])) & M            # E5 = A1 + c5
a1 = (e5ok - np.uint32(c5)).astype(np.uint32)
print("A1 passing own conditions:", len(a1), " published A1 in set:", int(Ax[1]) in set(a1.tolist()))
pub = (a.s0(a.MX[9]) - a.s0(a.MY[9])) & M
d = (s0(w9x) - s0(w9y)).astype(np.uint32)
print("published s0(W9) modular difference %08x; A1 values keeping it: %d of %d" % (pub, int((d == np.uint32(pub)).sum()), len(d)))
print("W9 modular difference constant:", len(set(((w9x - w9y).astype(np.uint32)).tolist())) == 1)
vals, cnt = np.unique(d, return_counts=True)
print("distinct s0(W9) differences:", len(vals), [("%08x" % v, int(c)) for v, c in zip(vals[:6], cnt[:6])])
np.savetxt("a1_values.txt", np.sort(a1), fmt="%08x")
