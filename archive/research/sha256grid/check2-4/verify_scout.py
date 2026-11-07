# verify_scout.py - check2-4: verify the scout's own success dumps (scout2-4/sfs_cut16.txt, sfs_cut22.txt; format of
# smc38r.c: cp instream a0 a1 a2 cv[8] mx[16] my[16]) with the filed vt38.py, read-only: valid variant of the
# embedded A0 / A2 lists, Step-2 pair, collision, W7 in F7, row 16; the full-cell-path flag; the filed first row-17
# test.  usage: python3 -B verify_scout.py file

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

import importlib.util, sys, collections
sys.dont_write_bytecode = True
P = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base/experiments/vt38.py')
spec = importlib.util.spec_from_file_location("vt38", P); vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)
E = vt.emb(); vt.tables(); A0I = {a: j for j, a in enumerate(E["A0"])}; A2I = {a: k for k, a in enumerate(E["A2"])}
n = ok = ncp = nft = flag = 0; fails = collections.Counter(); deep = collections.Counter(); ftw = collections.Counter()
for line in open(sys.argv[1]):
    t = line.split(); n += 1
    cp, ins = int(t[0]), int(t[1]); a0, a1, a2 = (int(x, 16) for x in t[2:5])
    cv = [int(x, 16) for x in t[5:13]]; mx = [int(x, 16) for x in t[13:29]]; my = [int(x, 16) for x in t[29:45]]
    if a0 not in A0I or a2 not in A2I: fails["A0/A2 not in the lists"] += 1; continue
    var, c7 = vt.variant(a0, a1, a2)
    if not vt.valid(var): fails["invalid variant"] += 1; continue
    if vt.pair(cv, var) != (mx, my): fails["not the Step-2 pair"] += 1; continue
    if mx == my or vt.compress(cv, mx) != vt.compress(cv, my): fails["no collision"] += 1; continue
    if not vt.inF7(mx[7]): fails["W7"] += 1; continue
    r16, w7, d, (tx, ty, _, _) = vt.outcome(cv, a0, a1, a2)
    if not r16: fails["row 16"] += 1; continue
    ok += 1; deep[d] += 1; ncp += d == vt.R - 1; flag += (d == vt.R - 1) != bool(cp)
    g = vt.GREC[vt.G.index(tx[2][16])]; f = (tx[1][17] & g[1]) == g[2]; nft += f; ftw[(ins, f)] += 1
print("%s: lines %d verified %d failures %s" % (sys.argv[1].split("/")[-1], n, ok, dict(fails)))
print("  deepest cell row: %s" % dict(sorted(deep.items())))
print("  full cell path %d; cell-path flag disagreements %d; filed first row-17 test passes %d of %d; (instream, first test) counts %s"
      % (ncp, flag, nft, ok, dict(ftw)))
