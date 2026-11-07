#!/usr/bin/env python3
"""verdicts.py (untried/ctr_alg; research only) - one line per main-sample and planted system: solutions, DFS work
(simple, joint; op weights of the stack code), SAT lower bound (best config), best CLI solve phase (F - F_bot), CMS
in-process (fresh; incremental), and the verdict of the most favourable MEASURED solver cost against the cheaper DFS.
Note: the incremental CMS times of the first systems in file order include the template's start-up (cold solver)."""
import json, os
from math import log2
HERE = os.path.dirname(os.path.abspath(__file__))
J = lambda f: json.load(open(os.path.join(HERE, f)))
systems = J('systems.json')
split = {r['name']: r for r in J('time_split.json')['rows']}
for r in J('time_split_cms.json')['rows']:
    split[r['name']]['cms'] = r['cms']
inproc = J('cms_inproc.json')
L = lambda x: log2(x) if x > 0 else float('-inf')
for i, s in enumerate(systems):
    if not s['main']:
        continue
    d = s['dfs']; dmin = min(d['ops_simple'], d['ops_joint'])
    lb = min(v['lb'] for v in s['sat'].values())
    raw = [split[s['name']][c]['solve_cyc'] for c in ('kissat', 'kissat-nc', 'cadical', 'cms')]
    noisy = sum(v <= 0 for v in raw)            # F - F_bot below timing noise: not used for this line
    cli = min(v for v in raw if v > 0)
    fr, inc = inproc['fresh_ns'][i] * 4.7, inproc['incr_ns'][i] * 4.7
    meas = min(cli, fr, inc)
    agree = all(v['sols'] == d['sols'] == d['sols_joint'] for v in s['sat'].values())
    found = '' if s['plant'] is None else (' planted h1 found by all' if all(
        s['plant'] in v['sols'] for v in s['sat'].values()) and s['plant'] in d['sols'] else ' PLANT MISSED')
    verdict = 'SAT dearer' if meas > dmin else 'SAT cheaper'
    print(f"{s['name']:15s} {len(d['sols'])} sol{'' if agree else ' DISAGREE'}{found} | DFS simple 2^{L(d['ops_simple']):.1f}"
          f" joint 2^{L(d['ops_joint']):.1f} | SAT LB 2^{L(lb):.1f}, CLI solve 2^{L(cli):.1f}"
          f"{f' ({noisy} CLI split(s) below noise, dropped)' if noisy else ''}, CMS in-proc fresh "
          f"2^{L(fr):.1f} incr 2^{L(inc):.1f} | {verdict} by 2^{abs(L(meas) - L(dmin)):.1f} (best measured vs cheaper DFS)")
