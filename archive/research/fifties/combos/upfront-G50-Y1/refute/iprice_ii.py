"""Row (ii) check: openings at 218 units, opened share 0.409 (briefed XF1/XF2 numbers), on the independent rows."""

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

import json, sys
from math import log2
sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/tools/build_pkg/scratch/pkgCJ/work'))
import frontline_full as F
K = F.RUN_CONTEXTS
rows = {s: json.load(open("irows_s%d.json" % s))["rows"] for s in (5501, 6602)}
def mean(x): return sum(x) / len(x)
per = dict(rep=173216, ctx=600 * (K + 1) / K, open=218 * 16384 * 0.409, E=10 * (F.E_BUDGET + 1) / K,
           fill=60 * (F.G_BUDGET + 1) / K, pas=468 * (F.PASS_BUDGET + 1) / K, solver=F.CREDIT / K)
once = F.N - sum(v for k, v in dict(rep=173216 * K, ctx=600 * (K + 1), open=368 * (F.A_BUDGET + 1),
           E=10 * (F.E_BUDGET + 1), fill=60 * (F.G_BUDGET + 1), pas=468 * (F.PASS_BUDGET + 1), solver=F.CREDIT).items())
base = sum(per.values()); N_old = base * K + once
print("row ii per-context %.0f fixed share %.4f score %.4f" % (base, (per["rep"] + per["ctx"] + per["open"]) / base, log2(N_old / 430)))
kept, allr = [], []
for s, rs in rows.items():
    o = sorted(range(len(rs)), key=lambda i: rs[i]["pilot"]); top = set(o[len(rs) - len(rs) // 2:])
    kept += [rs[i] for i in top]; allr += rs
rat = lambda k: mean([r[k] for r in kept]) / mean([r[k] for r in allr])
R = rat("passes_open")
for pu in (11, 25):
    kc = per["rep"] + per["ctx"] + per["open"] * rat("opened") + per["E"] * rat("e_lanes") + per["fill"] * rat("fills") \
        + per["pas"] * R + per["solver"] * rat("calls_open")
    N_new = (kc + (600 + 1024 * pu) / 0.5) / R * K + once + 2 ** 20
    print("row ii keep 1/2 u=%d: R %.4f gain %.4f bit -> %.4f" % (pu, R, log2(N_old / N_new), log2(N_new / 430)))
