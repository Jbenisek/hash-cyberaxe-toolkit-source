"""Block-1 partial preimage model (variant e, two-level): full 2-round compression, 16 free message words,
chaining-value words o_i = v_i ^ v_{i+8}; the listed targets are constants: 'o4' (single CV word) or 's0' (o0 + o4,
the K0:a1 key form v0 + v4).   usage: python export_b1.py <out> <targets comma list>"""
import sys
from gd_two import compress
from export_model import export
from gd_var import closure
out, targets = sys.argv[1], sys.argv[2].split(",")
eqs, const = [], set()
init = [f"iv{i}" for i in range(16)]; const.update(init)
st, _ = compress("", init, [f"m{i}" for i in range(16)], eqs)
for i in range(8):
    eqs.append((f"o{i}", (f"o{i}", st[i], st[i + 8])))
for t in targets:
    if t.startswith("s"):
        j = int(t[1:]); eqs.append((f"s{j}", (f"s{j}", f"o{j}", f"o{j+4}")))
    const.add(t)
const = closure(eqs, const)
eqs = [(n, vs) for n, vs in eqs if any(v not in const for v in vs)]
vars_ = sorted({v for _, vs in eqs for v in vs} - const)
nr = export(eqs, const, vars_, [], out)
print(out, "vars", len(vars_), "eqs", len(eqs), "freedom", len(vars_) - len(eqs), "reps", nr)
