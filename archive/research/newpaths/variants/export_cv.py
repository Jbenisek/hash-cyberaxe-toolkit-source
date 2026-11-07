"""Export two-block CV-list models for gdcv (CV words init0..init7 unknown).
usage: python export_cv.py <half> <mode fixed|partial|outhalf> <length> <tables 0|1|2> <out> [held]"""
import sys
from gd_var import build, closure, table_macros
half, mode, L, t, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
held = sys.argv[6].split(",") if len(sys.argv) > 6 else None
eqs, const, vars_ = build(half, mode, L, held, cvvar=True)
cv = [f"init{i}" for i in range(8)]
macros = table_macros(eqs, const, t) if t else []
ix = {v: i for i, v in enumerate(vars_)}
p1eqs = [e for e in eqs if not any(v in cv for v in e[1])]
p1mac = [m for m in macros if not any(v in cv for v in m[0] + (m[1],))]
rules = [(0, [ix[v] for v in vs if v not in const]) for _, vs in eqs]
rules = [r for r in rules if r[1]] + [(1, [ix[x] for x in trig if x not in const] + [ix[tgt]]) for trig, tgt in macros]
base = closure(p1eqs, const, p1mac)
seen, reps = {}, []
for v in vars_:
    if v in base or v in cv:
        continue
    key = frozenset(closure(p1eqs, set(const) | {v}, p1mac))
    if key not in seen:
        seen[key] = v
        reps.append(ix[v])
with open(out, "w") as fh:
    fh.write(f"{len(vars_)} {len(rules)}\n")
    for tt, nv in rules:
        fh.write(f"{tt} {len(nv)} {' '.join(map(str, nv))}\n")
    fh.write(f"reps {len(reps)} {' '.join(map(str, reps))}\n")
    fh.write(f"cv 8 {' '.join(str(ix[c]) for c in cv)}\n")
open(out + ".vars", "w").write("\n".join(vars_) + "\n")
print(out, "vars", len(vars_), "eqs", len(eqs), "Ffixed", len(vars_) - 8 - len(eqs), "reps", len(reps), "macros", len(macros))
