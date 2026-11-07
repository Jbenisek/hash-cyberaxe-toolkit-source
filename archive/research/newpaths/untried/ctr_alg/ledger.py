#!/usr/bin/env python3
"""ledger.py (untried/ctr_alg; research only) - every work measure per passing step on the record steps (rec7 = the
150 steps of e3solve_out.txt, rec11 = the 120 steps of e3solve2.py's run, pooled = 270), and its value on the X2
ledger: stack_calc.py V4, T = log2(S * c / 430) + 0.02, c = 400 + 35 + 2^-9.8132 * SOLVE, S = 2^69.987 (R_SUB).
Inputs: systems.json (e3sat.py), time_split.json + time_split_cms.json (e3sat_time.py), cms_inproc.json."""
import json, os
from math import log2
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, f)))
systems = J('systems.json')
split = {r['name']: r for r in J('time_split.json')['rows']}
for r in J('time_split_cms.json')['rows']:
    split[r['name']]['cms'] = r['cms']
inproc = J('cms_inproc.json')
assert inproc['names'] == [s['name'] for s in systems]
CLK_NS = 4.7
R_SUB, P_SUB = 67_698_688, 2 ** -9.8132


def T(solve):
    m = 2 ** 32 * R_SUB * 2 ** -128
    return log2(0.5 / (m / 2.0) * (435 + P_SUB * solve) / 430) + 0.02


BASE = T(2 ** 18.51)
CFGS = ('kissat', 'kissat-nc', 'cadical', 'cms')
measures = {
    'DFS simple (e3solve.py weights)': lambda i, s: s['dfs']['ops_simple'],
    'DFS joint (e3solve2.py weights)': lambda i, s: s['dfs']['ops_joint'],
}
for c in CFGS:
    measures[f'{c}: LB = literals + propagations'] = (lambda c: lambda i, s: s['sat'][c]['lb'])(c)
for c in CFGS:
    measures[f'{c}: process CPU - start-up (cycles)'] = (lambda c: lambda i, s: s['sat'][c]['time_ops'])(c)
for c in CFGS:
    measures[f'{c}: solve phase F - F_bot (cycles)'] = (lambda c: lambda i, s: split[s['name']][c]['solve_cyc'])(c)
measures['cms in-process, fresh solver (cycles)'] = lambda i, s: inproc['fresh_ns'][i] * CLK_NS
measures['cms in-process, incremental template (cycles)'] = lambda i, s: inproc['incr_ns'][i] * CLK_NS
measures['oracle min(DFS simple, cms incremental)'] = \
    lambda i, s: min(s['dfs']['ops_simple'], inproc['incr_ns'][i] * CLK_NS)
print(f'X2 ledger: SOLVE 2^18.51 -> T {BASE:.3f}; SOLVE 0 -> T {T(0):.3f} (ceiling {BASE - T(0):.3f} bit)\n')
for tags in (('rec7',), ('rec11',), ('rec7', 'rec11')):
    steps = {}
    for i, s in enumerate(systems):
        if s['set'] in tags:
            steps.setdefault((s['set'], s['step']), []).append((i, s))
    print(f'{"+".join(tags)}: {len(steps)} passing steps, {sum(len(v) for v in steps.values())} systems')
    print(f'  {"measure (per passing step)":48s} {"mean":>8s} {"median":>8s}   T on X2   change vs 70.990')
    for name, f in measures.items():
        v = sorted(sum(f(i, s) for i, s in st) for st in steps.values())    # unclipped: F - F_bot noise averages out
        mean = sum(v) / len(v)
        print(f'  {name:48s} 2^{log2(mean):5.2f}  2^{log2(max(v[len(v) // 2], 1)):5.2f}   {T(mean):7.3f}   '
              f'{BASE - T(mean):+.3f}')
    print()


def T4p(solve):                                    # stack_calc V4p/V4s: outer step packed, c = 65 + 16 + ...
    m = 2 ** 32 * R_SUB * 2 ** -128
    return log2(0.5 / (m / 2.0) * (81 + P_SUB * solve) / 430) + 0.02


pooled = {}
for i, s in enumerate(systems):
    if s['set'] in ('rec7', 'rec11'):
        pooled.setdefault((s['set'], s['step']), 0.0)
        pooled[(s['set'], s['step'])] += inproc['incr_ns'][i] * CLK_NS
best = sum(pooled.values()) / len(pooled)
print(f'packed-outer variant (stack_calc V4p, c = 81 + 2^-9.8132 * SOLVE): DFS simple 2^18.51 -> T {T4p(2 ** 18.51):.3f}'
      f' (V4p 70.213); V4s GUESS solver 2^15 -> T {T4p(2 ** 15):.3f} (V4s 68.135); measured best off-the-shelf '
      f'(cms in-process incremental, pooled 2^{log2(best):.2f}) -> T {T4p(best):.3f}')
