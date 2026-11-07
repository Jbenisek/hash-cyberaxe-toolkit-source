
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

import sys, hashlib, importlib.util, time
sys.dont_write_bytecode = True
P=_hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgB3W/pkg/blake3-r2/experiments/frontline.py')
sp = importlib.util.spec_from_file_location("F", P); F = importlib.util.module_from_spec(sp); sp.loader.exec_module(F)
lo, hi, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
with open(out, "w") as f:
    for i in range(lo, hi):
        t=time.time()
        o = F.walk_thi(hashlib.sha256(b"scanonce-g07u04/" + b"%d" % i).digest(), words_cap=None, full_every=64)[3]
        f.write("%d %d %d %d %d %d %.2f\n" % (i, o["words"], o["pf_words"], o["listed"], o["mismatches"], o["halted"], time.time()-t)); f.flush()
