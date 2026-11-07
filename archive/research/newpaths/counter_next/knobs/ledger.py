"""ledger.py (counter_next/knobs; research only): time_log2 of each lever, one formula (counter/adjudicate):
    T = log2(0.5) + 128 - log2(C_eff / margin) + log2(ops_per_unit / 430) + 0.02
C_eff = collision mass per unit of work (a trial, or an outer step covering all 2^32 inner values), margin 2.0
(our convention; the board's 1.4 is shown too).  Inputs are the measured figures named in each line."""
import math

L2 = math.log2


def T(Ceff_log2, ops, margin=2.0):
    return -1 + 128 - (Ceff_log2 - L2(margin)) + L2(ops / 430) + 0.02


rows = []
# baseline: counter cube program (counter/value): C = 2^11 * 67,698,688 per trial, 6.5 ops per trial
Cc = L2(2**11 * 67698688)
base = T(Cc, 6.5)
rows.append(('counter cube program (VALUE.md, reproduced)', base, 'COMPUTED (team)'))
# cube program + outer-step feasibility filters; per outer step: 2^21 trials * 6.5 ops; candidate cost 470 ops
work = 2**21 * 6.5
for name, share_log2, tag in (('cube + Y9 filter (dg1 feasible for some beta* outcome; exact share)', -4.9927, 'COMPUTED'),
                              ('cube + w8 filter (de2 feasible for some beta* outcome)', -4.21, 'COMPUTED'),
                              ('cube + Y9 and w8 filter (same outcome; real outer steps 2^-9.98, uniform 2^-9.92)', -9.95, 'COMPUTED')):
    kept = 2**share_log2
    ops_per_trial = 6.5 * (1 + (1 / kept) * 470 / work)
    rows.append((name, T(Cc - share_log2, ops_per_trial), tag))
# E3 solved per outer step over all 2^32 inner values; targets = 7 heaviest outcomes, C_t = 109,051,904
Ct = L2(109051904) + 32
for name, ops in (('E3 solver, split search, LOW part by table, 15 ops/node (HIGH 42.3 nodes)', 400 + 35 + 42.3 * 15),
                  ('E3 solver, split search, LOW part by table, 20 ops/node', 400 + 35 + 42.3 * 20),
                  ('E3 solver, split search, LOW searched (800 nodes x 8 ops) + HIGH x 20', 400 + 800.4 * 8 + 42.3 * 20),
                  ('E3 solver, plain bit search, 6,329 nodes x 20 ops', 400 + 6328.5 * 20),
                  ('E3 solver floor: outer step alone (400 ops)', 400)):
    rows.append((name, T(Ct, ops), 'COMPUTED nodes; ops/node GUESS'))
# E3 solver with the 20 heaviest outcomes (C 166,723,584): split, table, 20 ops/node, JOIN 245.8 x 30
rows.append(('E3 solver, 20 targets (split, table, 20 ops/node, JOIN 246 x 30 ops)',
             T(L2(166723584) + 32, 400 + 100 + 116.1 * 20 + 245.76 * 30), 'COMPUTED nodes; ops GUESS'))
for name, t, tag in rows:
    print(f'{t:7.2f}  (margin 1.4: {t - L2(2.0) + L2(1.4):6.2f})  {name}  [{tag}]')
