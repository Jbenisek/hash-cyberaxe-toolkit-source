# Single-word A1 count with S's A0, A2, A3 fixed: dense-part cells (E4, E5, W8 + W8 two-bit conditions, W9) and the
# published s0(W9) modular difference.  Comparable to r38's single-word A1 count.

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

import importlib.util
P = _hca_public_path_text('__HCA_WORKSPACE__/research/stuck/r37-1f12a09a/pkg/experiments/a0core.py')
spec = importlib.util.spec_from_file_location("a0core", P); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
M = a.M32
tx = a.trace(a.CV0, a.MX); ty = a.trace(a.CV0, a.MY)
A = [[tx[0][i] for i in range(14)], [ty[0][i] for i in range(14)]]
E = [[tx[1][i] for i in range(14)], [ty[1][i] for i in range(14)]]
pub = (a.s0(a.MX[9]) - a.s0(a.MY[9])) & M
keep16 = {int(l, 16) for l in open('a1_keep16.txt')}
cells_ok, both = 0, 0
for line in open('a1_values.txt'):
    a1 = int(line, 16); w = {}
    for m in (0, 1):
        Am = list(A[m]); Am[1] = a1
        e4 = (Am[4] + Am[0] - a.S0(Am[3]) - a.MAJ(Am[3], Am[2], Am[1])) & M
        e5 = (Am[5] + Am[1] - a.S0(Am[4]) - a.MAJ(Am[4], Am[3], Am[2])) & M
        Em = list(E[m]); Em[4], Em[5] = e4, e5
        w[m] = [(Em[i] - Am[i-4] - Em[i-4] - a.S1(Em[i-1]) - a.CH(Em[i-1], Em[i-2], Em[i-3]) - a.K[i]) & M for i in (8, 9)] + [e4]
    ok = True
    m4, v4, d4, _ = a.CELLS['E'][4]
    if (w[0][2] & m4) != v4 or (w[0][2] ^ w[1][2]) != d4: ok = False
    m8, v8, d8, _ = a.CELLS['W'][8]
    if (w[0][0] & m8) != v8 or (w[0][0] ^ w[1][0]) != d8: ok = False
    b = lambda x, k: (x >> k) & 1; x8 = w[0][0]
    if not (b(x8, 1) != b(x8, 12) and b(x8, 8) != b(x8, 25) and b(x8, 14) == b(x8, 18)): ok = False
    if ok:
        cells_ok += 1
        if ((a.s0(w[0][1]) - a.s0(w[1][1])) & M) == pub: both += 1; assert a1 in keep16
print("A1 single-word (S's A0): cells hold for %d (expect 208); also s0(W9) difference kept: %d" % (cells_ok, both))
