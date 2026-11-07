
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

import sys, random
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgR38M3/pkg/sha256-r38/experiments'))
import a0lean38 as L
rng = random.Random(99); m = L.Mach(lambda: rng.getrandbits(256)); st = L.Stats()
bad = 0; diffs = {}; n = 0
while n < 1500:
    o0 = m.ops; cv, hits, M0 = L.process_fb(m, st, False, False); tot = m.ops - o0
    if hits: continue
    n += 1
    s = 0
    for c in L.CLASSES:
        mm = L.Mach(); L.w7test(mm, c[0], cv[0]); s += mm.ops + 4
    d = tot - s; diffs[d] = diffs.get(d, 0) + 1
print('no-hit fb: metered total minus (sum of w7 tests + 4/class):', diffs, '(ledger fixed = 35 incl. br)')
