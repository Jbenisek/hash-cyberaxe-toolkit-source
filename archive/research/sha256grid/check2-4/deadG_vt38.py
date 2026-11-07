# deadG_vt38.py - check2-4 side note: confirm with the filed vt38.rowok (read-only) that a G word has no E17^x with
# every row-17 cell.  For G index gi: rows 12..15 of the published pair, row 16 from G[gi], then every E17^x in the
# first-test mask set (2^22 values; any E17 with all row-17 cells lies in it) -> W17^x, W17^y = W17^x (dW17 = 0),
# both members stepped, vt38.rowok(.., 17) counted.  usage: python3 -B deadG_vt38.py gi [gi ...]

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

import importlib.util, sys
sys.dont_write_bytecode = True
P = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base/experiments/vt38.py')
spec = importlib.util.spec_from_file_location("vt38", P); vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)
vt.tables(); M = vt.M
for gi in (int(x) for x in sys.argv[1:]):
    g = vt.G[gi]; mE, vE = vt.GREC[gi][1], vt.GREC[gi][2]
    tr = []
    for m, (A_, E_, W_) in enumerate((vt.TX, vt.TY)):
        A = {i: A_[i] for i in range(12, 16)}; E = {i: E_[i] for i in range(12, 16)}; W = {i: W_[i] for i in range(0, 16)}
        W[16] = g if m == 0 else (g - vt.DW16) & M
        vt._step(A, E, W, 16)
        tr.append((A, E, W))
    (Ax, Ex, Wx), (Ay, Ey, Wy) = tr
    assert vt.rowok((Ax, Ex, Wx), (Ay, Ey, Wy), 16)
    dw17 = (vt.s1(Wx[15]) - vt.s1(Wy[15]) + Wx[10] - Wy[10]) & M
    c17x = (Ax[13] + Ex[13] + vt.S1(Ex[16]) + vt.CH(Ex[16], Ex[15], Ex[14]) + vt.K[17]) & M
    free = ~mE & M; s = 0; n = cnt = 0
    while True:
        e = s | vE; n += 1
        Wx[17] = (e - c17x) & M; Wy[17] = (Wx[17] - dw17) & M
        vt._step(Ax, Ex, Wx, 17); vt._step(Ay, Ey, Wy, 17)
        cnt += vt.rowok((Ax, Ex, Wx), (Ay, Ey, Wy), 17)
        s = (s - free) & free
        if s == 0: break
    print("G index %2d (%08x): masked E17 values %d, with every row-17 cell (vt38.rowok) %d, dW17 %08x" % (gi, g, n, cnt, dw17))
