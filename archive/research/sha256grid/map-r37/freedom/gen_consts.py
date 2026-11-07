# Builds C constants for the r37 dense-part single-word freedom count.
# Data source (read only, public package of submission 1f12a09a): characteristic cells, two-bit conditions, SFS pair.

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
P = _hca_public_path_text('__HCA_WORKSPACE__/research/stuck/r37-1f12a09a/pkg/experiments/a0core.py')
spec = importlib.util.spec_from_file_location("a0core", P); a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
tx = a.trace(a.CV0, a.MX); ty = a.trace(a.CV0, a.MY)
SAx = [tx[0][i] for i in range(14)]; SAy = [ty[0][i] for i in range(14)]
SEx = [tx[1][i] for i in range(14)]; SEy = [ty[1][i] for i in range(14)]
Wx = [tx[2][i] for i in range(14)];  Wy = [ty[2][i] for i in range(14)]
# self-check: recompute E_i, W_i (i>=4 / i>=8) from A rows only, as the C code will
def E_of(A, i): return (A[i] + A[i-4] - a.S0(A[i-1]) - a.MAJ(A[i-1], A[i-2], A[i-3])) & a.M32
def W_of(A, E, i): return (E[i] - A[i-4] - E[i-4] - a.S1(E[i-1]) - a.CH(E[i-1], E[i-2], E[i-3]) - a.K[i]) & a.M32
for SA, SE, W in ((SAx, SEx, Wx), (SAy, SEy, Wy)):
    for i in range(4, 14): assert E_of(SA, i) == SE[i]
    for i in range(8, 14): assert W_of(SA, SE, i) == W[i]
out = []
def arr(n, v): out.append("static const uint32_t %s[%d] = {%s};" % (n, len(v), ",".join("0x%08xu" % x for x in v)))
arr("SAX", SAx); arr("SAY", SAy); arr("KK", a.K[:14])
for k in ('E', 'W'):
    for j, nm in enumerate(('M', 'V', 'D', 'P')):
        arr("%s%s" % (k, nm), [a.CELLS[k][i][j] for i in range(14)])
# A rows 0..13: confirm rows 0..5 carry no A condition or difference (so A0..A3 are free words, same in both members)
for i in range(0, 6): assert a.CELLS['A'][i][:3] == (0, 0, 0), i
# two-bit conditions closing at rows <= 13 that are NOT the Step-2 words W6/W7 (those are tested per chaining value)
x2 = [c for c in a.X2 if max(c[1], c[5]) <= 13 and not (c[0] == 'W' and c[1] in (6, 7))]
print("x2 conditions used:", x2, file=sys.stderr)
assert all(c[0] == 'W' and c[1] == 8 and c[5] == 8 for c in x2)
out.append("#define NX2 %d" % len(x2))
out.append("static const int X2B1[%d] = {%s};" % (len(x2), ",".join(str(c[2]) for c in x2)))
out.append("static const int X2B2[%d] = {%s};" % (len(x2), ",".join(str(c[6]) for c in x2)))
out.append("static const int X2EQ[%d] = {%s};" % (len(x2), ",".join('1' if c[3] == '=' else '0' for c in x2)))
open("consts.h", "w").write("#include <stdint.h>\n" + "\n".join(out) + "\n")
print("A0..A3 (x):", ["%08x" % v for v in SAx[:4]], file=sys.stderr)
print("E rows 4..13 cell bit counts:", [bin(a.CELLS['E'][i][0]).count('1') for i in range(4, 14)], file=sys.stderr)
print("W rows 8..13 diff/value bits:", [(bin(a.CELLS['W'][i][0]).count('1'), bin(a.CELLS['W'][i][2]).count('1')) for i in range(8, 14)], file=sys.stderr)
