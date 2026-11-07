"""Fill the Section 8 total from the two numbers the agents supply, and print every figure that moves.
    fill_total.py CHARGE P        (CHARGE: the new upper-bound charge per trial-equivalent; P: preprocessing_log2)"""

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
from math import log2
charge, P = float(sys.argv[1]), float(sys.argv[2])
N = 759300 * 2**81
lc = log2(charge)
main0 = log2(N) + lc - log2(430)
rest = (2**94 + 2**28 + 2**11 + 1) / 430 + 2
T = charge * N / 430 + rest + 2**P
closed = charge * N * (1 + 2**-7) / 430 + 2**(P + 1)
time = int(log2(closed) * 100 + 1) / 100            # rounded up to two decimals
f = lambda x: f"{x:.6f}"
vals = {"[CHARGE]": f"{charge:.2f}", "[P]": f"{P:g}", "[P1]": f"{P + 1:g}", "[LOG2C]": f(lc), "[MAIN0]": f(main0),
        "[MAIN]": f"{log2(charge * N * (1 + 2**-7) / 430):.4f}", "[SLACK]": f"{log2(charge * N) - 7 - 0.0005:.3f}",
        "[TIME]": f"{time:.2f}"}
assert 2**94.01 < charge * N * 2**-7, "the 2^-7 slack no longer covers the small terms"
t = open(_hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/sec8_total_template.md'), encoding="utf-8").read()
for k, v in vals.items():
    t = t.replace(k, v)
open(_hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/sec8_total_filled.md'), "w", encoding="utf-8", newline="\n").write(t)
pt = open(_hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/sec8_preproc_template.md'), encoding="utf-8").read()
open(_hca_public_path_text('__HCA_WORKSPACE__/research/pkg10/sec8_preproc_filled.md'), "w", encoding="utf-8",
     newline="\n").write(pt.replace("[P]", f"{P:g}"))
print("direct log2 T =", f(log2(T)), " closed form =", f(log2(closed)), " claim =", vals["[TIME]"])
for k, v in vals.items():
    print(f"  {k:<9} {v}")
