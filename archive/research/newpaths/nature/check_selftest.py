"""Cross-check nature.c's toy compression against Grok's job28.py (read-only import)."""

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

import sys
sys.dont_write_bytecode = True
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job28_newpaths'))
import job28  # noqa: E402

ok = bad = 0
for line in open(_hca_public_path_text('__HCA_WORKSPACE__/research/newpaths/nature/selftest.txt')):
    left, right = line.split("|")
    m = [int(x, 16) for x in left.split()[1:]]
    o = [int(x, 16) for x in right.split()[1:]]
    w = max(8, max(x.bit_length() for x in m))
    w = 8 if w <= 8 else (16 if w <= 16 else 32)
    py = job28.compress(m, w, job28.primary_rots(w))
    if py == o:
        ok += 1
    else:
        bad += 1
        print("MISMATCH", w, m, o, py)
print("selftest vs job28.compress: ok", ok, "bad", bad)
