"""SAT check (exact, word-level GD model): can a SINGLE half-digest word (out0, out2, out5 or out7) be held constant
with 0 checks, i.e. is there a guess set of 15 words (= freedom) whose propagation determines everything?
UNSAT for all four -> c(1) >= 1, hence c(k) >= 1 for every k >= 1 (adding equations never lowers the check count).
Reuses ../gd_sat.encode with gd_order.build filtered to one output equation.  T = number of equations (exact depth).
Usage: python sat_sphere.py <out0|out2|out5|out7> [--tables]   -> writes sph_<word>[T]_k15.cnf
"""

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
import gd_order  # noqa: E402  (read only)
import gd_sat  # noqa: E402  (read only)

word = sys.argv[1]
if "--tables" in sys.argv:
    gd_sat.TABLES = True


def build_one(variant, length):
    eqs, const, _ = gd_order.build("outhalf", length)
    eqs = [e for e in eqs if not (e[0].startswith("out") and e[0] not in word.split(","))]
    vars_ = sorted({v for _, vs in eqs for v in vs} - const)
    return eqs, const, vars_


gd_sat.build = build_one
eqs, const, vars_ = build_one("outhalf", "len64")
F = len(vars_) - len(eqs)
T = len(eqs)
K = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else F
clauses, nv, g, vs = gd_sat.encode("outhalf", "len64", K, T)
fn = f"sph_{word.replace(',', '_')}{'T' if gd_sat.TABLES else ''}_k{K}.cnf"
with open(fn, "w") as fh:
    fh.write(f"p cnf {nv} {len(clauses)}\n")
    for c in clauses:
        fh.write(" ".join(map(str, c)) + " 0\n")
print(fn, "vars", nv, "clauses", len(clauses), "freedom", F, "depth T", T)
