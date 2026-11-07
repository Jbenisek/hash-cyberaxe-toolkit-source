#!/usr/bin/env python3
# fresh_summ.py : FRESH_2x128.tsv -> per-block linear mean, 99% Student LB (pkg 7.4b rule), paired ratio p16/base with delta-method se, projected claims.
import re, math, os, collections
H = os.path.dirname(os.path.abspath(__file__)); BASE_CLAIM, BASE_Q = 57.23762, -71.4162
try:
    from scipy.stats import t as T; tq = lambda df: T.ppf(0.99, df)
except Exception:
    tq = lambda df: {127: 2.35585, 255: 2.34100}[df]
E = collections.defaultdict(dict)
for l in open(os.path.join(H, 'FRESH_2x128.tsv')):
    m = re.match(r'(\S+)\t(\d+)\t.*RESULT .* est (\S+)', l)
    if m: E[m.group(1)][int(m.group(2))] = float(m.group(3))
B, P = E['PUB_list170'], E['r37_p16_w4_rx']
def st(v):
    n = len(v); mu = sum(v) / n; sd = math.sqrt(sum((x - mu) ** 2 for x in v) / (n - 1)); lb = mu - tq(n - 1) * sd / math.sqrt(n)
    return n, math.log2(mu), sd / mu, math.log2(lb)
blocks = {'R1': range(930000, 930128), 'R2': range(931000, 931128), 'ALL': list(range(930000, 930128)) + list(range(931000, 931128))}
for tag, d in (('base PUB_list170', B), ('p16_w4_rx', P)):
    lbs = {}
    for b, ss in blocks.items():
        v = [d[s] for s in ss if s in d]; n, lm, rs, lb = st(v); lbs[b] = lb
        print('%-17s %-3s n=%d log2mean=%.5f relsd=%.4f LB99=%.5f zeros=%d' % (tag, b, n, lm, rs, lb, sum(1 for x in v if x == 0)))
    x = math.floor(100 * min(lbs['R1'], lbs['R2'])) / 100
    print('%-17s 7.4b rule x=floor(100 log2 min LB)/100 = %.2f -> claim %.5f' % (tag, x, BASE_CLAIM + (BASE_Q - x)))
ss = sorted(set(B) & set(P)); n = len(ss); mb = sum(B[s] for s in ss) / n; mp = sum(P[s] for s in ss) / n
dq = math.log2(mp / mb); z = [P[s] / mp - B[s] / mb for s in ss]; mz = sum(z) / n
se = math.sqrt(sum((x - mz) ** 2 for x in z) / (n - 1) / n) / math.log(2)
dlb = dq - tq(n - 1) * se
print('paired n=%d dq=log2(mean p16/mean base)=%+.5f se=%.5f  99%% one-sided LB dq=%+.5f' % (n, dq, se, dlb))
qF = -71.41618
print('transfer to block F LB 2^-71.41618: point q3c=%.5f claim %.5f ; with dq LB q3c=%.5f -> floor4 %.4f claim %.5f' % (qF + dq, BASE_CLAIM - dq, qF + dlb, math.floor(1e4 * (qF + dlb)) / 1e4, BASE_CLAIM + (BASE_Q - math.floor(1e4 * (qF + dlb)) / 1e4)))
