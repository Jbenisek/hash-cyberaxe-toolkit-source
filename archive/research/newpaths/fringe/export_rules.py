"""Write a gdv.py variant in the input format of ../audit/bf.c (plain rules only, no tables):
line 1 'nvars neqs 0', then the variable names, then one line per equation (variable indices).
Usage: python export_rules.py <variant> [len64|len55]   -> rules_<variant>_<length>.txt
"""
import sys

sys.dont_write_bytecode = True
from gdv import build  # noqa: E402

variant = sys.argv[1]
length = sys.argv[2] if len(sys.argv) > 2 else "len64"
eqs, const, vars_, H = build(variant, length)
assert len(vars_) <= 128, len(vars_)
ix = {v: i for i, v in enumerate(vars_)}
with open(f"rules_{variant}_{length}.txt", "w", newline="\n") as fh:
    fh.write(f"{len(vars_)} {len(eqs)} 0\n")
    fh.write(" ".join(vars_) + "\n")
    for _, vs in eqs:
        fh.write(" ".join(str(ix[v]) for v in vs) + "\n")
print(f"rules_{variant}_{length}.txt: {len(vars_)} vars, {len(eqs)} eqs, freedom {len(vars_) - len(eqs)}")
