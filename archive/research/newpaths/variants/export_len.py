"""Shorter single-block messages: message words m_i with 4*i >= L are zero constants (the boundary word with
L % 4 != 0 is treated as free; its zero top bytes are an extra bit-level condition, not modelled).
usage: python export_len.py <half> <L> <tables> <out>"""
import sys
from gd_var import build, closure, table_macros
from export_model import export, main_rules
half, L, t, out = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
eqs, const, vars_ = build(half, "fixed", 64)
zeros = {f"m{i}" for i in range(16) if 4 * i >= L}
const = closure(eqs, set(const) | zeros)
eqs = [(n, vs) for n, vs in eqs if any(v not in const for v in vs)]
vars_ = sorted({v for _, vs in eqs for v in vs} - const)
macros = []
if t:
    macros = table_macros(eqs, const, t) + (main_rules(eqs, const) if t == 1 else [])
nr = export(eqs, const, vars_, macros, out)
open(out + ".vars", "w").write("\n".join(vars_) + "\n")
print(out, "zero words", sorted(zeros, key=lambda s: int(s[1:])), "vars", len(vars_), "eqs", len(eqs),
      "freedom", len(vars_) - len(eqs), "reps", nr)
