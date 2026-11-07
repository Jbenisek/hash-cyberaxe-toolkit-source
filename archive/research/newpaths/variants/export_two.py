"""usage: python export_two.py <half> <mode> <length2> <out> [held]   (no tables: block-2 K tables would depend on the CV)"""
import sys
from gd_two import build_two
from export_model import export
half, mode, L2, out = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
held = sys.argv[5].split(",") if len(sys.argv) > 5 else None
eqs, const, vars_ = build_two(half, mode, L2, held)
nr = export(eqs, const, vars_, [], out)
open(out + ".vars", "w").write("\n".join(vars_) + "\n")
print(out, "vars", len(vars_), "eqs", len(eqs), "freedom", len(vars_) - len(eqs), "reps", nr)
