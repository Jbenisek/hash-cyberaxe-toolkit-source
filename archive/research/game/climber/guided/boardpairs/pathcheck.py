#!/usr/bin/env python3
"""pathcheck.py : per verified pair, C1 cond (t>=16) and rows whose signed difference differs from the seed's."""
import os, re, glob, json, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, '..', 'kit')))
import char_pair_profile as cpp
SEEDS = {'r38': ('r38_s102.json', 38), 'r37': ('r37_tab17.json', 37)}

def prof(cv, m1, m2, n):
    return cpp.profile([int(x, 16) for x in cv], [int(x, 16) for x in m1], [int(x, 16) for x in m2], n)

for b, (sw, n) in SEEDS.items():
    s = json.load(open(os.path.join(HERE, 'wit', sw))); ps = prof(s['cv'], s['M1'], s['M2'], n)
    print('%s seed cond=%d' % (b, ps['total']['cond']))
    seen = set()
    for f in sorted(glob.glob(os.path.join(HERE, 'out', b + '_*.chk'))):
        t = open(f).read()
        if 'INDEP VERIFIED' not in t: continue
        m1 = re.search(r'^M1: W=([0-9a-f ]+)$', t, re.M).group(1).split(); m2 = re.search(r'^M2: W=([0-9a-f ]+)$', t, re.M).group(1).split()
        cv = re.search(r'^M1: W=.*\n\s*chain=([0-9a-f ]+)$', t, re.M).group(1).split()
        if tuple(m1 + cv) in seen: continue
        seen.add(tuple(m1 + cv)); p = prof(cv, m1, m2, n)
        dif = [k + str(r) for k in 'AEW' for r in (range(-4, n) if k != 'W' else range(n)) if p['rows'][k][r] != ps['rows'][k][r]]
        print('%s\t%s\tcond=%d\tdelta=%+d\tpath_rows_changed=%s' % (b, os.path.basename(f)[:-4], p['total']['cond'], p['total']['cond'] - ps['total']['cond'], ','.join(dif) or '-'))
