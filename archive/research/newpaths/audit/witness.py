"""Sanity: the k=8 CNF (gd_sat.py, unmodified) plus unit clauses fixing the guess variables to the greedy best set
(gd_best_fixed_len64.txt) must be SAT; with the same set minus one guess (k=8 CNF, 7 guesses fixed) it must be UNSAT."""
import os
import sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "orig"))
from gd_order import build  # noqa: E402
eqs, const, vars_ = build("fixed", "len64")
greedy = [l.split()[-1] for l in open(os.path.join(HERE, "..", "gd_best_fixed_len64.txt")) if l.startswith("guess")]
g = {v: i + 1 for i, v in enumerate(vars_)}     # gd_sat numbers the guess variables first, in vars_ order
src = open(os.path.join(HERE, "gd_fixed_len64_k8_T100.cnf")).read().split("\n", 1)
nv, nc = map(int, src[0].split()[2:])
for tag, S in (("greedy8", greedy), ("greedy7", greedy[:-1])):
    units = [f"{g[v] if v in S else -g[v]} 0" for v in vars_]
    with open(os.path.join(HERE, f"witness_{tag}.cnf"), "w") as fh:
        fh.write(f"p cnf {nv} {nc + len(units)}\n" + src[1] + "\n".join(units) + "\n")
    print(tag, S)
