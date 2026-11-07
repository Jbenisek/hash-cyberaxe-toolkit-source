#!/usr/bin/env python3
"""analyze.py  (counter/value; research only) - rates of the counter arrangement's real trials against the exact
seven-word model (research/h8/gpu/out/h8_deep_expected.txt, whole eta class) and against the GPU model runs."""
import glob, os, re, sys
from math import log2, sqrt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'out')
# exact per-trial probabilities, whole class (h8_deep_expected.txt), conditioned on beta* where marked
P_BETA = 2.0 ** -11
EXACT = {
    'listed tau': 2.9429793357849121e-07 / P_BETA,            # given beta* (c1 in the cube)
    'listed E1 outcome': 1.4122036873231991e-13 / P_BETA,     # given beta*
    'rule A (8)': 2.0 ** -8,
    'gate H4': 2.0 ** -4,
}
EXACT_ALL_E3 = {'listed partial E3': 2.0287926894013708e-10, 'listed partial E3 eps 6e21be55': 5.2295945351943374e-11}
EXACT_FREE = {'listed beta': 0.0040283203125, 'beta=18b0e098': P_BETA, 'listed tau': 2.0724255591630936e-06}


def parse(path):
    d, cop, head = {}, [], ''
    for ln in open(path):
        if ln.startswith('RUN'): head = ln.strip()
        m = re.match(r'CNT (.+?)\s+(\d+)$', ln.rstrip())
        if m: d[m.group(1)] = int(m.group(2))
        m = re.match(r'COP bit\s+(\d+) gate (\d+) rule (\d+)', ln)
        if m: cop.append(tuple(int(x) for x in m.groups()))
        m = re.match(r'(TAUI|E3G) (\d+) (\d+)', ln)
        if m: d[f'{m.group(1)}{m.group(2)}'] = int(m.group(3))
        m = re.match(r'SQ rule_per_outer (\S+) tau_per_outer (\S+) outer (\d+) inner (\d+)', ln)
        if m: d['SQ'] = (float(m.group(1)), float(m.group(2)), int(m.group(3)), int(m.group(4)))
    return head, d, cop


def z(obs, exp):
    return (obs - exp) / sqrt(exp) if exp > 0 else float('nan')


def line(name, obs, n, exp_p):
    exp = exp_p * n
    lg = log2(obs / n) if obs else float('-inf')
    return f'  {name:40s} {obs:>14d}  2^{lg:8.3f}   expected {exp:14.2f} (2^{log2(exp_p):.3f})  z {z(obs, exp):+6.2f}'


runs = sys.argv[1:] or sorted(glob.glob(os.path.join(OUT, '*.txt')))
tot = {}
for p in runs:
    if os.path.basename(p) in ('gpu_runs.log',) or not open(p).read().strip():
        continue
    head, d, cop = parse(p)
    if 'trials' not in d:
        continue
    n = d['trials']
    print(f'== {os.path.basename(p)}: {head}  (trials 2^{log2(n):.2f})')
    free = 'cube=0' in head
    sub = 'sub=1' in head
    exp = dict(EXACT_FREE) if free else dict(EXACT)
    if not sub and not free:
        exp.update(EXACT_ALL_E3)
    if free:
        exp.update({'rule A (8)': 2.0 ** -8, 'gate H4': 2.0 ** -4})
        exp.update(EXACT_ALL_E3)
    for k in d:
        if k in exp:
            print(line(k, d[k], n, exp[k]))
    if 'SQ' in d:   # per-outer-step overdispersion: z with the empirical variance of the per-outer counts
        sqr, sqt, no, ni = d['SQ']
        for k, sq, pe in (('rule A (8)', sqr, exp.get('rule A (8)')), ('listed tau', sqt, exp.get('listed tau'))):
            if pe and k in d:
                mean = d[k] / no
                var = sq / no - mean * mean
                zz = (d[k] - pe * n) / sqrt(var * no) if var > 0 else float('nan')
                print(f'  {k:40s} variance/mean per outer step {var / mean:10.1f}; z with that variance {zz:+6.2f}')
    for k in ('listed tau & rule A', 'listed outcome & rule A'):   # E1 side against the E3-side rule on h1
        if k in d:
            a, b = k.split(' & ')
            a = {'listed outcome': 'listed E1 outcome', 'listed partial E3': 'listed partial E3'}.get(a, a)
            b = {'rule A': 'rule A (8)', 'early': 'early word 0'}.get(b, b)
            if a in exp and b in exp:
                print(line(k + ' (vs product of exact rates)', d[k], n, exp[a] * exp[b]))
            elif a in d and b in d and d[a] and d[b]:
                print(line(k + ' (vs product of margins)', d[k], n, d[a] / n * d[b] / n))
    for k in ('listed partial E3', 'listed partial E3 eps 6e21be55', 'early word 0', 'eta condition', 'residual word 0 zero',
              'residual word 1 zero', 'residual word 2 zero', 'residual word 3 zero', 'listed outcome & listed partial E3',
              'beta != 18b0e098 (must be 0)', 'beta=18b0e098', 'listed beta'):
        if k in d and k not in exp:
            o = d[k]
            print(f'  {k:40s} {o:>14d}  2^{(log2(o / n) if o else float("-inf")):8.3f}')
    if 'TAUI0' in d and d.get('listed E1 outcome'):
        # exact E1 weights of the 14 listed outcomes of beta* (H8_recount_k14.txt OUTX lines, units of 2^46), in the
        # order of TAUS in ctr_gpu.cu; expected count of outcome i = n * W_i * 2^46 * 2^-96 * 2^11
        W = [8, 4, 32, 16, 8, 4, 32, 16, 16, 8, 2, 1, 8, 4]
        chi = 0.0
        cells = []
        for i, w in enumerate(W):
            e = n * w * 2.0 ** (46 - 96 + 11)
            o = d[f'TAUI{i}']
            chi += (o - e) ** 2 / e
            cells.append(f'{o}/{e:.1f}')
        print(f'  listed E1 outcomes per tau (observed/exact): {" ".join(cells)}; chi-square {chi:.1f} on 14 cells')
    if cop:
        nr = d.get('rule-A trials with flips', 0)
        print(f'  d1-direction co-pass of rule-A trials (n = {nr}): bit: P(gate H4 | rule A) / P(rule A | rule A)')
        print('   ' + '  '.join(f'{b}:{g / nr:.3f}/{r / nr:.3f}' for b, g, r in cop))
    key = ('free' if free else 'cube') + ('_sub' if sub else '_all') + ('_gpu' if os.path.basename(p).startswith('g_') else '_cpu') + ('_model' if ' model ' in head or head.startswith('RUN model') else '')
    t = tot.setdefault(key, {})
    for k, v in d.items():
        if isinstance(v, int):
            t[k] = t.get(k, 0) + v
print('\n== GPU real (counter arrangement) against GPU model (seven-word model, beta* forced), rates per trial')
KEYS = ('listed tau', 'listed E1 outcome', 'rule A (8)', 'gate H4', 'listed partial E3', 'listed partial E3 eps 6e21be55',
        'early word 0', 'eta condition', 'listed outcome & rule A', 'listed tau & rule A', 'listed partial E3 & rule A',
        'residual word 0 zero', 'residual word 1 zero', 'residual word 2 zero', 'residual word 3 zero')
for sub in ('sub', 'all'):
    r, m = tot.get(f'cube_{sub}_gpu'), tot.get(f'cube_{sub}_gpu_model')
    if not r or not m:
        continue
    print(f'-- {sub}: real 2^{log2(r["trials"]):.2f} trials, model 2^{log2(m["trials"]):.2f} trials')
    for k in KEYS:
        if k in r and k in m and m[k] and r[k]:
            pr, pm = r[k] / r['trials'], m[k] / m['trials']
            sd = sqrt(1 / r[k] + 1 / m[k])            # Poisson, relative
            print(f'  {k:36s} real {r[k]:>13d} (2^{log2(pr):8.3f})  model {m[k]:>13d} (2^{log2(pm):8.3f})  '
                  f'ratio {pr / pm:.4f} +- {sd * pr / pm:.4f} (Poisson only)')
print('\n== pooled by kind')
for key, d in sorted(tot.items()):
    n = d['trials']
    print(f'{key}: trials 2^{log2(n):.3f}; ' + '; '.join(f'{k} {d[k]} (2^{log2(d[k] / n):.3f})' for k in
          ('listed tau', 'listed E1 outcome', 'listed partial E3', 'listed partial E3 eps 6e21be55', 'rule A (8)',
           'early word 0', 'eta condition') if k in d and d[k]))
