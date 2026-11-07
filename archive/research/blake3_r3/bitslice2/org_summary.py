import json
from math import sqrt, pi, exp
d = json.load(open('organizer_report.json'))
E = {e['id']: e for e in d['execution']['experiments']}
e = E['bsrho-n18']; t = e['checked_trials']; n = len(t)
ob = [x['untrusted_participant_observations'] for x in t]
tt = sum(x['success'] for x in t); ii = sum(o['ideal_ok'] for o in ob)
pt, pi_ = tt / n, ii / n; pp = (tt + ii) / (2 * n)
z = (pt - pi_) / sqrt(pp * (1 - pp) * 2 / n)
ts = [o['t1_steps'] for o in ob]; N1 = 1 << 12
mean = sum(ts) / n; ratio = mean / sqrt(pi * N1 / 2); sd = sqrt((4 - pi) / 2 * N1) / sqrt(n)
e2 = sum(v * v for v in ts) / n / (2 * N1)
th = sum(o['target_halt'] for o in ob); ih = sum(o['ideal_halt'] for o in ob)
l1 = "bsrho-n18 (organizer run, public seed): %d of %d trials returned a pair that the organizer verified (%.3f); ideal-function control %d of %d; two-proportion z %.2f; family-law runs at n = 12: mean first repeat %.2f, ratio to sqrt(pi N/2) %.4f (z %.2f), E[T^2]/2N %.3f; halts target %d, ideal %d." % (tt, n, pt, ii, n, z, mean, ratio, (mean - sqrt(pi * N1 / 2)) / sd, e2, th, ih)
e = E['proj-k0-w256']; t = e['checked_trials']; n = len(t)
ob = [x['untrusted_participant_observations'] for x in t]
lam = 2048 * 2047 / 2 / (1 << 21)
hit = sum(x['success'] for x in t)
names = ("w0", "w3", "w7", "xor8", "sum8", "p01", "p23")
src = []
for s, nm in enumerate(("uniform", "counter", "iterates")):
    idx = [i for i, o in enumerate(ob) if o['source'] == s]
    h = sum(1 for i in idx if t[i]['success'])
    src.append("%s %d of %d (expected %.1f)" % (nm, h, len(idx), (1 - exp(-lam)) * len(idx)))
tot = {k: sum(o['dup_' + k] for o in ob) for k in names}
zs = ", ".join("%.2f" % ((tot[k] - lam * n) / sqrt(lam * n)) for k in names)
l2 = "proj-k0-w256 (organizer run): %d of %d trials returned a verified pair (expected %.1f); by source: %s; equal pairs in the seven projections, total over %d trials against %.1f expected: %s; z %s." % (hit, n, (1 - exp(-lam)) * n, "; ".join(src), n, lam * n, ", ".join("%s %d" % (k, tot[k]) for k in names), zs)
open('organizer_summary.txt', 'w', newline='\n').write(l1 + "\n" + l2 + "\n")
print(l1); print(l2)
