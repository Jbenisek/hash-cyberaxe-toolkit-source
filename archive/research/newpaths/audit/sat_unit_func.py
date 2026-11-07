"""Same random-system test as sat_unit.py for gd_sat_audit.encode with and without --func (plain rules)."""
import os, random, subprocess, sys
sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "orig"))
import gd_sat_audit
from gd_order import propagate
from rules import nc_eqs
from sat_unit import rand_system, kmin_bf, solve

rng = random.Random(4)
bad = 0
lines = []
for trial in range(20):
    n, m = rng.randint(9, 14), rng.randint(4, 9)
    eqs, const, vars_ = rand_system(rng, n, m)
    gd_sat_audit.get = lambda variant, length, rset, s=(eqs, const, vars_): (s[0], s[1], s[2], nc_eqs(s[0], s[1]), [])
    km = kmin_bf(eqs, const, vars_)
    out = []
    for func in (False, True):
        gd_sat_audit.FUNC = func
        for k in (km - 1, km):
            if k < 0:
                out.append("-")
                continue
            clauses, nv, g, vs, _, _ = gd_sat_audit.encode("x", "plain", k, len(vars_))
            txt = f"p cnf {nv} {len(clauses)}\n" + "".join(" ".join(map(str, c)) + " 0\n" for c in clauses)
            rc, true = solve(txt, f"f{trial}_{int(func)}_k{k}")
            if rc == 10:
                known = set(const) | {v for v in vs if g[v] in true}
                propagate(eqs, known, [])
                rc = 10 if len(known) == len(const) + len(vars_) else -10
            out.append(rc)
    ok = out[0] in ("-", 20) and out[1] == 10 and out[2] in ("-", 20) and out[3] == 10
    bad += not ok
    lines.append(f"trial {trial}: vars={len(vars_)} kmin={km} plain enc (k-1,k)={out[:2]} func enc (k-1,k)={out[2:]} {'OK' if ok else 'BAD'}")
lines.append(f"failures: {bad} of 20")
print("\n".join(lines))
open(os.path.join(HERE, "sat_unit_func.log"), "w").write("\n".join(lines) + "\n")
