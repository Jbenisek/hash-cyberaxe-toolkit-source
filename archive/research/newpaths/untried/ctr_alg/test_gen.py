#!/usr/bin/env python3
"""test_gen.py (untried/ctr_alg; research only) - SAT-generated beta* plants per tau (kissat, 120 s cap per call),
retrying with fewer fixed q/w8 bits (24, 16, 8, 0).  UNSAT at 0 fixed bits = no class member y, q, w8, h1 meets that
beta* outcome in E3 at all.  Checks each plant passes the exact outer filter and that both DFS's find the planted h1."""
import os, sys
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e3sat as X  # noqa: E402
os.makedirs(X.CNFDIR, exist_ok=True)
for k in range(7):
    for seed, nfix in ((100 + k, 24), (200 + k, 16), (300 + k, 8), (400 + k, 0)):
        r = X.gen_plant(k, seed, nfix)
        if isinstance(r, str):
            print(f'tau#{k} {X.S.TAUS[k]:08x}: nfix {nfix}: {r}', flush=True); continue
        y, q, w8, h1, sec = r
        g, e, t = X.TARGETS[k]
        ok = X.S.solvable1(q, g) and X.S.solvable2((X.Y3 + y + w8) & X.M, X.ror(g, 12), e)
        d = X.dfs(y, q, w8, X.TARGETS[k])
        print(f'tau#{k} {X.S.TAUS[k]:08x}: nfix {nfix}: y {y:08x} q {q:08x} w8 {w8:08x} h1 {h1:08x} in {sec:.1f} s; '
              f'passes filter {ok}; DFS simple finds it {h1 in d["sols"]}, joint {h1 in d["sols_joint"]}; '
              f'solutions {len(d["sols"])}', flush=True)
        break
