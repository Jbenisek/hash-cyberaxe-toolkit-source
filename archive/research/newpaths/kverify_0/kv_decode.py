"""kverify_0: decode a kissat model of r1_*/r2_* and re-check closedness, properness, delta and size in plain Python."""

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
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/newpaths'))
from gd_order import build

eqs, const, vars_ = build("fixed", "len64")
WORDS = sorted(vars_)
EQ = [tuple(v for v in vs if v not in const) for _, vs in eqs]


def check(A, name):
    closed = all(not (sum(u not in A for u in U) == 1) for U in EQ)
    d = len(A) - sum(1 for U in EQ if all(u in A for u in U))
    print(f"{name}: |A|={len(A)} closed={closed} proper={len(A) < len(WORDS)} delta={d}")


fn = sys.argv[1]
true = set()
for line in open(fn):
    if line.startswith("v "):
        true.update(int(x) for x in line[2:].split() if int(x) > 0)
A = {w for i, w in enumerate(WORDS) if i + 1 in true}
check(A, "A")
if fn.startswith("r2"):
    # second region's x variables start after A's block (A x, then A's closure/proper adds no vars) -> recompute offset
    off = len(WORDS)
    B = {w for i, w in enumerate(WORDS) if off + i + 1 in true}
    check(B, "B")
    check(A | B, "AuB")
