import sys
sys.path.insert(0, "..")
from gd_var import build, table_macros, greedy, e_inputs
import gd_order
# consistency with the main model
for v in ("fixed", "outhalf"):
    e1, c1, v1 = gd_order.build(v, "len64")
    e2, c2, v2 = build("02", v, 64)
    print(v, "main:", len(v1), len(e1), "mine:", len(v2), len(e2), "same eqs:", sorted(e1) == sorted(e2), "same const:", c1 == c2)
print("E inputs 02:", e_inputs("02"))
print("E inputs 13:", e_inputs("13"))
for half in ("02", "13"):
    for mode in ("fixed", "outhalf"):
        for L in (64, 55):
            eqs, const, vars_ = build(half, mode, L)
            F = len(vars_) - len(eqs)
            m1 = table_macros(eqs, const, 1)
            print(half, mode, L, "vars", len(vars_), "eqs", len(eqs), "freedom", F, "macros d<=1:", len(m1))
