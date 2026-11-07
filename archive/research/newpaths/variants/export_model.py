"""Write a model file for gdx.c.
usage: python export_model.py <half 02|13> <mode fixed|outhalf|partial> <length 64|55> <tables 0|1|2> <out> [held,comma,list]
tables 0: plain propagation; 1: one-free-word sub-systems (2^32 tables) plus the main model's K (y,a2)->x rule;
2: up to two free words (2^64 tables, preprocessing 2^64 - allowed: preprocessing up to ~2^88 is negligible)."""
import sys

from gd_var import build, closure, table_macros


def main_rules(eqs, const):
    """The main model's extra rule: round-0 column with constant inputs a,b,c,d and free x,y: (y, a2) -> x."""
    calls = {}
    for name, vs in eqs:
        if ":" in name:
            calls.setdefault(name.split(":")[0], {})[name.split(":")[1]] = vs
    out = []
    for call, e in calls.items():
        a, b, x = e["a1"][1], e["a1"][2], e["a1"][3]
        d, c, y = e["d1"][1], e["c1"][1], e["a2"][3]
        if all(u in const for u in (a, b, c, d)) and y not in const and x not in const:
            out.append(((y, e["a2"][0]), x))
    return out


def model(half, mode, length, tables, held=None, cvvar=False):
    eqs, const, vars_ = build(half, mode, length, held, cvvar)
    macros = []
    if tables >= 1:
        macros = table_macros(eqs, const, tables)
        if tables == 1:
            macros += main_rules(eqs, const)
    return eqs, const, vars_, macros


def export(eqs, const, vars_, macros, fn):
    ix = {v: i for i, v in enumerate(vars_)}
    rules = []
    for _, vs in eqs:
        nv = [ix[v] for v in vs if v not in const]
        if nv:
            rules.append((0, nv))
    for trig, tgt in macros:
        rules.append((1, [ix[t] for t in trig if t not in const] + [ix[tgt]]))
    # equivalence classes: same closure from a single guess
    base = closure(eqs, const, macros)
    seen = {}
    reps = []
    for v in vars_:
        if v in base:
            continue
        key = frozenset(closure(eqs, set(const) | {v}, macros))
        if key not in seen:
            seen[key] = v
            reps.append(ix[v])
    with open(fn, "w") as fh:
        fh.write(f"{len(vars_)} {len(rules)}\n")
        for t, nv in rules:
            fh.write(f"{t} {len(nv)} {' '.join(map(str, nv))}\n")
        fh.write(f"reps {len(reps)} {' '.join(map(str, reps))}\n")
    return len(reps)


if __name__ == "__main__":
    half, mode, length, tables, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
    held = sys.argv[6].split(",") if len(sys.argv) > 6 else None
    eqs, const, vars_, macros = model(half, mode, length, tables, held)
    nreps = export(eqs, const, vars_, macros, out)
    with open(out + ".vars", "w") as fh:
        fh.write("\n".join(vars_) + "\n")
    print(f"{out}: vars {len(vars_)} eqs {len(eqs)} freedom {len(vars_) - len(eqs)} macros {len(macros)} reps {nreps}")
