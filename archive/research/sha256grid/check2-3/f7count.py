"""check2-3: exact |F7| = #{w in 2^32 : s0(w + D7) - s0(w) = T7} by exhaustive numpy count (D7, T7 from vt38.py);
the q3 tail weight 2^(32-f)/|F7| and p2 = |F7|/2^32 of the ledger depend on it."""

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

import sys, importlib.util, math
sys.dont_write_bytecode = True
import numpy as np
BASE = _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38a/base')
spec = importlib.util.spec_from_file_location('vt38', BASE + r'\experiments\vt38.py')
vt = importlib.util.module_from_spec(spec); spec.loader.exec_module(vt)
U = np.uint32
def ror(x, n): return (x >> U(n)) | (x << U(32 - n))
def s0(x): return ror(x, 7) ^ ror(x, 18) ^ (x >> U(3))
D7, T7 = U(vt.D7), U(vt.T7); CH = 1 << 26; tot = 0
with np.errstate(over='ignore'):
    for c in range(1 << 6):
        w = np.arange(c * CH, (c + 1) * CH, dtype=np.uint64).astype(U)
        tot += int(np.count_nonzero((s0(w + D7) - s0(w)) == T7))
# spot check of the definition against vt38.inF7 on a few values
import random
rng = random.Random(1); xs = [rng.getrandbits(32) for _ in range(200000)]
with np.errstate(over='ignore'):
    xa = np.array(xs, dtype=U); mine = ((s0(xa + D7) - s0(xa)) == T7)
dis = sum(1 for x, m in zip(xs, mine.tolist()) if bool(vt.inF7(x)) != m)
print('definition vs vt38.inF7 on 200,000 random words: %d disagreements (%d in F7)' % (dis, int(mine.sum())))
print('D7 0x%08x T7 0x%08x  |F7| = %d  (proof.md / q3gpu F7N 287309824: %s)  p2 = |F7|/2^32 = 2^%.6f' % (vt.D7, vt.T7, tot, tot == 287309824, math.log2(tot / 2 ** 32)))
