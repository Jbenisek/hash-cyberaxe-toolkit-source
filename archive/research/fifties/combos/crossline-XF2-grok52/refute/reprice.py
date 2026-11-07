"""Independent repricing of crossline-XF2 (Grok 52) on the scored pkgCJ N formula.
Only the constants are imported from the scored code; the new N is rebuilt term by term here.
Run: python -B reprice.py   (from this folder)"""

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

import math
import sys
from fractions import Fraction as Fr

sys.path.insert(0, _hca_public_path_text('__HCA_WORKSPACE__/research/grok/work/job52_xf2_repgate'))
import frontline_full as F  # noqa: E402

K, S = F.RUN_CONTEXTS, F._S
assert F.N == F.TEXT["N"] and F.A_BUDGET == F.TEXT["A_BUDGET"]
mean_filed = -(-246621675 * K >> 15)             # ceil(p* * 16384 K), p* = 246621675 / 2^29
tail = 16384 * S
assert mean_filed + tail == F.A_BUDGET
CL = 16384 * K                                    # clusters per run


def n_new(p_open, guard_units, p_open_is_exact=True):
    """N with the opening budget's mean term at p_open * 16384 K (ceil), same tail, plus guard units per cluster."""
    mean = -(-(p_open * CL).numerator // (p_open * CL).denominator) if isinstance(p_open, Fr) else math.ceil(p_open * CL)
    a_new = mean + tail
    return F.N - F.U_OPEN * (F.A_BUDGET + 1) + F.U_OPEN * (a_new + 1) + guard_units * CL


def lg(n):
    return math.log2(n / 430)


print("K", K, "_S", S, "A_BUDGET", F.A_BUDGET, "mean_filed", mean_filed, "tail", tail)
print("log2 today", lg(F.N))
rows = []
for name, p in [("52/128 exact, p_g=0", Fr(52, 128)),
                ("brief formula at p_g=9/65536", Fr(52, 128) * (1 - Fr(9, 65536)) + Fr(459, 1000) * Fr(9, 65536)),
                ("measured 0.40691 (600k re-check)", Fr(40691, 100000)),
                ("measured 0.40729 (Astra 18 / EBG)", Fr(40729, 100000)),
                ("uniform old gate 0.44823 (no proof)", Fr(940000, 2097152)),
                ("filed p* (no change)", Fr(246621675, 2 ** 29))]:
    for gu in (0, 2, 3, 4):
        rows.append((name, gu, lg(n_new(p, gu))))
for r in rows:
    print("%-40s guard_units %d  log2 %.6f  delta %.4f" % (r[0], r[1], r[2], r[2] - lg(F.N)))
# proof-grade budget from the 64-block lemma (RESULT.md): opens per context <= 6656 + 38 per guard-on block,
# i.e. opened share <= 52/128 + (38/64) p_g, p_g <= 9/65536 (Grok's proved ceiling). Also charge the per-context
# 4-entry Hbad table (4 subtractions, 4 xors, 8 window compares: 20 units per context, a GUESS of the op count).
p_proof = Fr(52, 128) + Fr(38, 64) * Fr(9, 65536)
for gu in (2, 3):
    n = n_new(p_proof, gu) + 20 * K
    print("proof-grade share 52/128+(38/64)(9/65536) guard_units %d +20/context  log2 %.6f  delta %.4f"
          % (gu, lg(n), lg(n) - lg(F.N)))
n = n_new(Fr(52, 128) + Fr(9, 65536), 2) + 20 * K
print("cruder bound 52/128 + 9/65536, 2 guard units +20/context  log2 %.6f" % lg(n))
# break-even opening rate at the 63.55 bar with 2 guard units
lo, hi = Fr(40625, 100000), Fr(1, 2)
for _ in range(60):
    mid = (lo + hi) / 2
    if lg(n_new(mid, 2)) <= 63.55:
        lo = mid
    else:
        hi = mid
print("largest opening rate with 2 guard units and log2 <= 63.55:", float(lo))
# guard units that alone would push 52/128 to the bar
gu = 0
while lg(n_new(Fr(52, 128), gu)) <= 63.55:
    gu += 1
print("guard units per cluster that reach 63.55 at 52/128:", gu, "->", lg(n_new(Fr(52, 128), gu)))
