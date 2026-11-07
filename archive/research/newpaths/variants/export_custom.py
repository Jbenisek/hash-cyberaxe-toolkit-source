"""Other exact holdings for the same target (out words of one half constant), modelled on top of 'outhalf':
extra constants given by name (Y<i>, m<i>, E<j>.a2/b2/c2/d2).  Equations whose words all become constant are dropped.
usage: python export_custom.py <half> <length> <out> <comma list of held names>"""
import sys
from gd_var import build
from export_model import export
half, L, out, held = sys.argv[1], int(sys.argv[2]), sys.argv[3], sys.argv[4].split(",")
eqs, const, vars_ = build(half, "outhalf", L)
# resolve Y names: Y<i> = state after round-1 columns, i.e. the input words of the E calls
import gd_var
eqs_tmp, _, _ = build(half, "outhalf", L)
ymap = {}
from gd_var import DIAG, HALF
for name, vs in eqs:
    pass
# E<j> inputs a,b,c,d appear in E<j>:a1 (a,b), E<j>:d1 (d), E<j>:c1 (c)
for j in HALF[half]:
    e = {n.split(":")[1]: vs for n, vs in eqs if n.startswith(f"E{j}:")}
    a, b, x = e["a1"][1], e["a1"][2], e["a1"][3]
    d, c = e["d1"][1], e["c1"][1]
    for pos, w in zip(DIAG[j], (a, b, c, d)):
        ymap[f"Y{pos}"] = w
const = set(const) | {ymap.get(h, h) for h in held}
from gd_var import closure
const = closure(eqs, const)          # words fixed by the constants alone count as constants
eqs = [(n, vs) for n, vs in eqs if any(v not in const for v in vs)]
vars_ = sorted({v for _, vs in eqs for v in vs} - const)
nr = export(eqs, const, vars_, [], out)
open(out + ".vars", "w").write("\n".join(vars_) + "\n")
print(out, "vars", len(vars_), "eqs", len(eqs), "freedom", len(vars_) - len(eqs), "reps", nr)
