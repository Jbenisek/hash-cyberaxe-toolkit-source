# verify_sfs.py - scout2-4: independent check of relaxed-SMC successes with the filed package's own reference code
# (vt38.py of pkgR38a base, imported read-only).  For every line of an smc38r sfs file:
#   (a) the two 38-step compressions from CV1 collide (vt38.compress) and the messages differ;
#   (b) the messages are exactly the variant's Step-2 pair from CV1 (vt38.variant + vt38.pair), the variant is valid
#       (vt38.valid) and W7 is in F7;
#   (c) the reference outcome (vt38.outcome): row 16 holds, and the deepest row through which every cell holds.
# A success with deepest row < 37 is a collision of the attack's own pair that the filed program does not report.
# usage: python -B verify_sfs.py file [max_lines]

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
P = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base/experiments/vt38.py')
spec = importlib.util.spec_from_file_location("vt38", P); vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)
fn = sys.argv[1]; mx_lines = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 9
n = ok = 0; deep = collections.Counter(); flagmis = 0; fails = collections.Counter()
for line in open(fn):
    if n >= mx_lines: break
    t = line.split(); n += 1
    cp, ins = int(t[0]), int(t[1]); a0, a1, a2 = (int(x, 16) for x in t[2:5])
    cv = [int(x, 16) for x in t[5:13]]; mx = [int(x, 16) for x in t[13:29]]; my = [int(x, 16) for x in t[29:45]]
    var, c7 = vt.variant(a0, a1, a2)
    if not vt.valid(var): fails['invalid variant'] += 1; continue
    wx, wy = vt.pair(cv, var)
    if wx != mx or wy != my: fails['not the Step-2 pair'] += 1; continue
    if mx == my or vt.compress(cv, mx) != vt.compress(cv, my): fails['no collision'] += 1; continue
    if not vt.inF7(mx[7]): fails['W7 not in F7'] += 1; continue
    r16, w7, d, _ = vt.outcome(cv, a0, a1, a2)
    if not r16: fails['row 16 fails'] += 1; continue
    ok += 1; deep[d] += 1
    flagmis += (d == vt.R - 1) != bool(cp)
print("lines %d  verified %d  failures %s" % (n, ok, dict(fails)))
print("deepest row with every cell holding (37 = full cell path): %s" % dict(sorted(deep.items())))
print("cell-path flag of smc38r disagrees with the reference on %d lines" % flagmis)
