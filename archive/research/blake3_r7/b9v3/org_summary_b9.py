import json
from math import sqrt, pi, exp
d = json.load(open('organizer_report_b9.json'))
E = {e['id']: e for e in d['execution']['experiments']}
e = E['bsrho-n18']; t = e['checked_trials']; n = len(t)
ob = [x['untrusted_participant_observations'] for x in t]
tt = sum(x['success'] for x in t); ii = sum(o['ideal_ok'] for o in ob)
ts = [o['t1_steps'] for o in ob]
th = sum(o['target_halt'] for o in ob); ih = sum(o['ideal_halt'] for o in ob)
l1 = "bsrho-n18 (organizer run, public seed): %d of %d trials returned a pair that the organizer verified; ideal-function control (program's own) %d of %d; family-law runs at n = 12 (program's own): mean first repeat %.2f; halts target %d, ideal %d." % (tt, n, ii, n, sum(ts) / n, th, ih)
e = E['proj-k0-w256']; t = e['checked_trials']; n = len(t)
ob = [x['untrusted_participant_observations'] for x in t]
lam = 2048 * 2047 / 2 / (1 << 21)
hit = sum(x['success'] for x in t)
names = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")
src = []
for s, nm in enumerate(("uniform", "counter", "iterates")):
    idx = [i for i, o in enumerate(ob) if o['source'] == s]
    h = sum(1 for i in idx if t[i]['success'])
    src.append("%s %d of %d" % (nm, h, len(idx)))
tot = {k: sum(o['dup_' + k] for o in ob) for k in names}
l2 = "proj-k0-w256 (organizer run): %d of %d trials returned a verified pair; by source: %s; equal pairs in the seven projections (program's own), total over %d trials: %s." % (hit, n, "; ".join(src), n, ", ".join("%s %d" % (k, tot[k]) for k in names))
open('organizer_summary.txt', 'w', newline='\n').write(l1 + "\n" + l2 + "\n")
print(l1); print(l2); print(d['execution']['status'], [ (k,len(v['checked_trials'])) for k,v in E.items()])
