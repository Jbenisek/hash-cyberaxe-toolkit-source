#!/usr/bin/env python3
"""Reviewer, lens mathematics and cost: the per-beta answers of math_seven.py against the package's per-outcome file.

For every beta: is "a solution that violates rule A exists" (my whole-system answer) the same as "the package drops
an outcome of this beta"? Is the outcome (tau, eps) of each of my violating models one of the outcomes that the
package drops? And "other": does the seven-word system of a beta have a solution whose outcome is not in the
calculator's list?   python3 -B math_seven_cross.py
"""
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
dropped, kept = {}, {}
for l in (PKG / "evidence" / "rule_a_sat_e7c1815f.txt").read_text(encoding="ascii").splitlines():
    f = l.split()
    if f and f[0] == "VIOLATE":
        (dropped if f[4] == "SAT" else kept).setdefault(f[1], set()).add((f[2], f[3]))
betas = set(dropped) | set(kept)
for solver in ("cadical", "kissat"):
    p = HERE / ("math_seven_violate_%s.txt" % solver)
    if not p.exists():
        continue
    same = model_in_dropped = model_in_kept = model_unlisted = sat = 0
    for l in p.read_text(encoding="ascii").splitlines():
        f = l.split()
        beta, ans = f[1], f[2]
        if beta not in betas:
            continue
        same += int((ans == "SAT") == (beta in dropped))
        if ans == "SAT":
            sat += 1
            key = (f[10], f[12])
            model_in_dropped += int(key in dropped.get(beta, ()))
            model_in_kept += int(key in kept.get(beta, ()))
            model_unlisted += int(key not in dropped.get(beta, ()) and key not in kept.get(beta, ()))
    print("%s violate: betas with a part %d, same answer as 'the package drops an outcome of it' %d; my %d violating models: outcome "
          "among the package's dropped %d, among its kept %d, not in the list %d" % (solver, len(betas), same, sat, model_in_dropped,
                                                                                     model_in_kept, model_unlisted))
for solver in ("cadical", "kissat"):
    p = HERE / ("math_seven_other_%s.txt" % solver)
    if p.exists():
        rows = [l.split() for l in p.read_text(encoding="ascii").splitlines()]
        rows = [r for r in rows if r[1] in betas]
        print("%s other (a solution with an outcome that the calculator does not list): betas %d, UNSAT %d, SAT %d, undecided %d" % (
            solver, len(rows), sum(r[2] == "UNSAT" for r in rows), sum(r[2] == "SAT" for r in rows), sum(r[2] == "?" for r in rows)))
        for r in rows:
            if r[2] == "SAT":
                print("   ", " ".join(r[:14]))
