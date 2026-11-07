# chkverify.py - check2-4: verify chk38 success dumps with the filed package's own reference code and counted program
# (vt38.py of pkgR38a base, imported read-only, bytecode writing off).  For every line:
#   (a) the A0 / A2 indices give the line's A0 / A2, the variant is valid, the messages are its Step-2 pair from CV1;
#   (b) the two 38-step compressions from CV1 collide, the messages differ, W7 is in F7, row 16 holds (vt38.outcome);
#   (c) the deepest row through which every cell holds (37 = the filed success event) agrees with the dump's flag;
#   (d) the filed first row-17 test (E17^x against GREC's mask) agrees with the dump's flag.
# For the first NPROG lines the counted online program itself (vt38.program, virtual registers, interpreter Machine)
# is run with the line's CV1 forced and a bucket holding the true entry: it must count one W7 pass (NW), count a
# first-test pass (N1) exactly when (d) holds, and output the pair (succ) exactly when every cell holds.
# usage: python3 -B chkverify.py file NPROG

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
E = vt.emb(); vt.tables()
fn = sys.argv[1]; NPROG = int(sys.argv[2]) if len(sys.argv) > 2 else 0
n = ok = 0; fails = collections.Counter(); deep = collections.Counter(); prog = collections.Counter()
flag_cp = flag_ft = 0; nft = ncp = 0
for line in open(fn):
    t = line.split()
    if len(t) != 48: fails["malformed"] += 1; continue
    n += 1
    cp, ft, j, k = int(t[1]), int(t[2]), int(t[3]), int(t[4])
    a0, a1, a2 = (int(x, 16) for x in t[5:8])
    cv = [int(x, 16) for x in t[8:16]]; mx = [int(x, 16) for x in t[16:32]]; my = [int(x, 16) for x in t[32:48]]
    if E["A0"][j] != a0 or E["A2"][k] != a2: fails["index mismatch"] += 1; continue
    var, c7 = vt.variant(a0, a1, a2)
    if not vt.valid(var): fails["invalid variant"] += 1; continue
    wx, wy = vt.pair(cv, var)
    if wx != mx or wy != my: fails["not the Step-2 pair"] += 1; continue
    if mx == my or vt.compress(cv, mx) != vt.compress(cv, my): fails["no collision"] += 1; continue
    if not vt.inF7(mx[7]): fails["W7 not in F7"] += 1; continue
    r16, w7, d, (tx, ty, _, _) = vt.outcome(cv, a0, a1, a2)
    if not r16 or not w7: fails["row 16 or W7"] += 1; continue
    ok += 1; deep[d] += 1
    gi = vt.G.index(tx[2][16]); g = vt.GREC[gi]
    ftr = (tx[1][17] & g[1]) == g[2] and (tx[1][17] - tx[2][17]) & vt.M == g[0]
    flag_cp += (d == vt.R - 1) != bool(cp); flag_ft += ftr != bool(ft); nft += ftr; ncp += d == vt.R - 1
    if n <= NPROG:
        true = vt.entry(cv, j, a1, k)
        mach = vt.Machine([1, 2], lambda jj, Y, Z0: [true], cvforce=cv); mach.run(vt.program([j], alloc=False))
        nw, n1 = mach.r.get("NW", 0), mach.r.get("N1", 0)
        prog["runs"] += 1
        prog["NW==1"] += nw == 1
        prog["N1 == first test"] += n1 == int(ftr)
        prog["N1==1"] += n1 == 1
        prog["succ == full cell path"] += (mach.succ == (j, true)) == (d == vt.R - 1)
        prog["succ"] += mach.succ == (j, true)
print("%s: lines %d  verified %d  failures %s" % (fn.split("/")[-1], n, ok, dict(fails)))
print("  deepest row with every cell holding (37 = filed success event): %s" % dict(sorted(deep.items())))
print("  full cell path %d of %d; filed first row-17 test passes %d of %d" % (ncp, ok, nft, ok))
print("  dump flags disagreeing with the reference: cell path %d, first test %d" % (flag_cp, flag_ft))
if prog: print("  counted program (vt38.Machine) on the first %d lines: %s" % (prog["runs"], dict(prog)))
