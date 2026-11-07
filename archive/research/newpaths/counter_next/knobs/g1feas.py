"""g1feas.py (counter_next/knobs; research only): an outer-step filter for the EXISTING cube program.

In the counter arrangement Y9 is fixed per outer step, and a success with outcome j needs
g1 ^ g1' = ROL(tau_j ^ ROR(tau_j, 1), 12) with g1 = Y9 + h1, h1' = h1 ^ eta.  If no h1 at all meets that for any
of the seven beta* outcomes, the outer step cannot succeed and its 2^21-trial cube loop can be skipped.
This measures the share of uniform Y9 for which the condition is feasible for at least one beta* outcome (exact
carry-pair automaton per Y9), and checks the claim 'infeasible => no success' on the exact counts' own terms:
the outcomes' E3 counts N_j are sums over Y9, so their whole mass lies on feasible Y9 (DERIVED).
usage: python -B g1feas.py NY9 SEED
"""
import sys, random
sys.dont_write_bytecode = True
import e3dfs as D

NY, seed = int(sys.argv[1]), int(sys.argv[2])
rows, tot = D.load_targets()
bstar = [r for r in rows if r[1] == 0x18b0e098]
targets = [D.outcome_target(r[2], r[3]) for r in bstar]
print(f'beta* outcomes: {len(bstar)}; taus ' + ' '.join(f'{r[2]:08x}' for r in bstar))
for t, r in zip(targets, bstar):
    print(f'  tau {r[2]:08x}: required dg1 {t[0]:08x} (eta {D.ETA:08x})')
rng = random.Random(seed)
feas_any = 0
feas_each = [0] * len(targets)
for i in range(NY):
    Y9 = rng.getrandbits(32)
    sols, _ = D.search(0, Y9, 0, targets, g1only=True)
    tis = {ti for _, ti in sols}
    feas_any += bool(tis)
    for ti in tis:
        feas_each[ti] += 1
import math
p = feas_any / NY
print(f'uniform Y9 sampled: {NY}; feasible for at least one beta* outcome: {feas_any} = {p:.5f} '
      f'(2^{math.log2(p):.3f})' if feas_any else 'none feasible')
for ti, r in enumerate(bstar):
    q = feas_each[ti] / NY
    print(f'  tau {r[2]:08x}: feasible share {q:.5f}' + (f' (2^{math.log2(q):.3f})' if q else ''))
