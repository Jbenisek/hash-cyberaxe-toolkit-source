#!/usr/bin/env python3
"""summarize.py: found against predicted, work per collision and measured gain for the toy runs (research only).

Reads out/<tag>_set<i>_r<first>.txt (finished parts only), mass_set<i>.txt (exact counts) and sets_w8.txt.
Predictions (exact model counts, W = 8):
  filed  : P = sumper / (n * 2^48) per trial
  ctrH   : P = mass_D / (n * |D| * 2^40) per counted trial (t = 0 trials are skipped and not counted as trials,
           but are added to the work), D = d1 values of the heaviest beta
  ctrAll : the counter arrangement with all 256 d1 values (control): P = sumper / (n * 2^48)
"""
import glob, math, os, re, sys
from collections import defaultdict

W = 8
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)

info = {}
for f in glob.glob('mass_set*.txt'):
    t = open(f).read()
    m = re.search(r'^MASS W \d+ set (\d+) eta \w+ n (\d+) sumper (\d+)', t, re.M)
    h = re.search(r'^HEAVIEST beta (\w+) nd1 (\d+) mass (\d+)', t, re.M)
    s = int(m.group(1))
    info[s] = dict(n=int(m.group(2)), sumper=int(m.group(3)), beta=h.group(1), nd=int(h.group(2)), md=int(h.group(3)))

rows = defaultdict(lambda: dict(runs=0, trials=0, tzero=0, coll=0, bad=0, bogus=0, pred=0.0, with_=0, pwith=0.0,
                                sq=0.0, secs=0.0, hits=0, cl=defaultdict(int)))
for f in sorted(glob.glob('out/*.txt')):
    base = os.path.basename(f)
    if base == 'progress.txt':
        continue
    txt = open(f).read()
    if '\nEND' not in txt:
        continue
    tag = base.split('_')[0].replace('', '').replace('\r', '')   # jobs.txt had CRLF: WSL put U+F00D in the names
    for line in txt.splitlines():
        p = line.split()
        if line.startswith('RUN '):
            kv = dict(re.findall(r'\b(set|trials|tzero|coll|bad|bogus) (\d+)', line))
            s = int(kv['set'])
            I = info[s]
            tr, tz, c = int(kv['trials']), int(kv['tzero']), int(kv['coll'])
            if tag == 'ctrH':
                P = I['md'] / (I['n'] * I['nd'] * 2.0 ** (5 * W))
            else:
                P = I['sumper'] / (I['n'] * 2.0 ** (6 * W))
            L = tr * P
            for key in (tag, (tag, s)):
                r = rows[key]
                r['runs'] += 1; r['trials'] += tr; r['tzero'] += tz; r['coll'] += c
                r['bad'] += int(kv['bad']); r['bogus'] += int(kv['bogus']); r['pred'] += L
                r['with_'] += c > 0; r['pwith'] += 1 - math.exp(-L); r['sq'] += (c - L) ** 2
        elif line.startswith('HIT '):
            kv = dict(zip(p[1:21:2], p[2:21:2]))
            s = int(kv['set'])
            cell = (kv['run'], kv['outer'], kv['x2'], kv['member'])
            for key in (tag, (tag, s)):
                rows[key]['hits'] += 1
                rows[key]['cl'][cell] += 1
        elif line.startswith('PART '):
            kv = dict(zip(p[1::2], p[2::2]))
            for key in (tag, (tag, int(kv['set']))):
                rows[key]['secs'] += float(kv['seconds'])


def z(o, e):
    return (o - e) / math.sqrt(e) if e > 0 else float('nan')


def ci(k):  # rough 95% interval for a Poisson count (Wilson-like, enough here)
    if k == 0:
        return 0.0, 3.69
    return max(0.0, k - 1.96 * math.sqrt(k) + 0.96), k + 1.96 * math.sqrt(k) + 1.96


out = []
P = out.append
P('Toy end-to-end (W = 8), sets 0..7: collisions found against the exact prediction, work per collision')
P('arrangement  set  runs        trials     t=0  found  pred     z     runs>=1 exp    disp   bad bogus hits  multi  trials/coll(found)  trials/coll(pred)  cpu s/coll')
for tag in ('filed', 'ctrAll', 'ctrH'):
    keys = sorted(k[1] for k in rows if isinstance(k, tuple) and k[0] == tag)
    for s in keys + ['all']:
        r = rows[(tag, s)] if s != 'all' else rows[tag]
        if r['runs'] == 0:
            continue
        multi = sum(v - 1 for v in r['cl'].values() if v > 1)
        tpc = (r['trials'] + r['tzero']) / r['coll'] if r['coll'] else float('inf')
        tpp = (r['trials'] + r['tzero']) / r['pred'] if r['pred'] else float('inf')
        cps = r['secs'] / r['coll'] if r['coll'] else float('inf')
        disp = r['sq'] / r['pred'] if r['pred'] else float('nan')
        P(f"{tag:<12} {str(s):>4} {r['runs']:5d} {r['trials']:14d} {r['tzero']:7d} {r['coll']:6d} {r['pred']:7.1f} {z(r['coll'], r['pred']):6.2f}   "
          f"{r['with_']:4d} {r['pwith']:6.1f}  {disp:5.2f}  {r['bad']:4d} {r['bogus']:4d} {r['hits']:5d} {multi:5d}  {tpc:17.4g}  {tpp:17.4g}  {cps:9.2f}")
    P('')

P('Measured gain per set: (found/trial in ctrH) / (found/trial in filed), against the predicted gain mean(mass_D/|D|)/(sumper/256)')
P('set  beta |D|  predicted gain   measured gain  (95% range from the Poisson counts)   ctrH found/pred   filed found/pred')
lg_pred = []; tot = dict(cf=0, tf=0, cc=0, tc=0, pf=0.0, pc=0.0)
for s in sorted(k[1] for k in rows if isinstance(k, tuple) and k[0] == 'ctrH'):
    I = info[s]
    g = (I['md'] / I['nd']) / (I['sumper'] / 2 ** W)
    f, c = rows[('filed', s)], rows[('ctrH', s)]
    if f['runs'] == 0 or c['runs'] == 0:
        continue
    tf, tc = f['trials'], c['trials'] + c['tzero']
    if f['coll'] > 0 and c['coll'] > 0:
        meas = (c['coll'] / tc) / (f['coll'] / tf)
        lo_c, hi_c = ci(c['coll']); lo_f, hi_f = ci(f['coll'])
        lo = (lo_c / tc) / (hi_f / tf); hi = (hi_c / tc) / (max(lo_f, 0.5) / tf)
        P(f"{s:3d}  {I['beta']:>4} {I['nd']:3d}  {g:14.3f}   {meas:12.3f}   ({lo:.2f} .. {hi:.2f})          {c['coll']:4d}/{c['pred']:6.1f}       {f['coll']:4d}/{f['pred']:6.1f}")
    else:
        P(f"{s:3d}  {I['beta']:>4} {I['nd']:3d}  {g:14.3f}   (no collision in one arrangement yet)   {c['coll']}/{c['pred']:.1f}  {f['coll']}/{f['pred']:.1f}")
    tot['cf'] += f['coll']; tot['tf'] += tf; tot['cc'] += c['coll']; tot['tc'] += tc; tot['pf'] += f['pred']; tot['pc'] += c['pred']
P('')
if tot['cf'] and tot['cc']:
    # pooled: ratio of (found/pred) between the arrangements, and the trial-weighted predicted gain
    rf, rc = tot['cf'] / tot['pf'], tot['cc'] / tot['pc']
    P(f"pooled sets: filed found/pred = {tot['cf']}/{tot['pf']:.1f} = {rf:.3f}; ctrH found/pred = {tot['cc']}/{tot['pc']:.1f} = {rc:.3f}; "
      f"ratio ctrH/filed of (found/pred) = {rc / rf:.3f} (1 = the predicted gain is realised)")
    P(f"pooled trials per collision: filed {tot['tf'] / tot['cf']:.4g}, ctrH {tot['tc'] / tot['cc']:.4g}, ratio {(tot['tf'] / tot['cf']) / (tot['tc'] / tot['cc']):.2f} "
      f"(log2 {math.log2((tot['tf'] / tot['cf']) / (tot['tc'] / tot['cc'])):.2f}); predicted ratio {(tot['tf'] / tot['pf']) / (tot['tc'] / tot['pc']):.2f}")
text = '\n'.join(out)
print(text)
open('summary.txt', 'w').write(text + '\n')
