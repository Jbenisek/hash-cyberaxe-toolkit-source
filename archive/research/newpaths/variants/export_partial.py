"""Export partial-held models: drop f of the 12 E-input words from the held set (f = 1, 2)."""
import itertools, sys
from gd_var import build, e_inputs
from export_model import export, table_macros
t = int(sys.argv[1]) if len(sys.argv) > 1 else 0
for half in ("02", "13"):
    ins = e_inputs(half)
    for f in (1, 2):
        for drop in itertools.combinations(ins, f):
            held = [w for w in ins if w not in drop]
            eqs, const, vars_ = build(half, "partial", 64, held)
            macros = table_macros(eqs, const, t) if t else []
            fn = f"models/part_{half}_t{t}_" + "-".join(drop) + ".mdl"
            nr = export(eqs, const, vars_, macros, fn)
            open(fn + ".vars", "w").write("\n".join(vars_) + "\n")
            print(fn, len(vars_), len(eqs), len(vars_) - len(eqs), nr)
