# cmp.py : per-pair tail comparison for the note (SUMMARY/SUMMARY2 linear means over the 14 public seeds; per-seed ratio vs 0b2616e3's table)
import json, re
T = '../pkg_r39_combined/work/tail_var/'
mean = {}
for f in ('SUMMARY.txt', 'SUMMARY2.txt'):
    for l in open(T + f):
        m = re.match(r'(\S+) mean_lin (\S+)', l)
        if m: mean[m.group(1)] = float(m.group(2))
dk = open('../pkg_r39_best_work/dkbase/sha256/experiments/r39tail.py').read()
dh = [int(l.split('|')[2]) for l in re.search(r'EXP_S="""\n(.*?)\n"""', dk, re.S).group(1).splitlines()]
SIG = {'s108': 'p_p39chars108_p39s', '7111': '7111e7edc4'}; NAME = {'58fca7a18e': 'our 2b4af365 pair', 'p_p39chars108_p39s': 'the s108 pair of the published characteristic', '7111e7edc4': 'the W9/W11 re-signed pair 7111e7edc4', 'p_p39chars105_p39s': 'the s105 pair of the published characteristic', 'p_p39chars109_p39s': 'the s109 pair of the published characteristic'}
for tag, sig in SIG.items():
    h = [sum(t['observations']['hits'] for t in json.load(open(T + sig + '/out_%02d.json' % i))['trials'][1:21]) for i in range(1, 15)]
    rr = [a / b for a, b in zip(h, dh)]; assert all(a > b for a, b in zip(h, dh))
    oth = {k: v for k, v in mean.items() if k != sig}
    top = sorted(oth.items(), key=lambda kv: -kv[1]); good = [kv for kv in top if kv[1] > -75.0]; rest = [kv for kv in top if kv[1] <= -75.0]
    parts = ['%s %.4f' % (NAME.get(k, 'pair ' + k), v) for k, v in good]
    s = 'in linear mean over the same seeds, this pair %.4f; %s; the other %d pairs %.2f to %.2f' % (mean[sig], ', '.join(parts), len(rest), rest[0][1], rest[-1][1])
    json.dump({'others': s, 'ratio': '%.2f to %.2f' % (min(rr), max(rr)), 'npairs': len(mean)}, open('cmp_%s.json' % tag, 'w'))
    print(tag, s, '| ratio %.2f to %.2f' % (min(rr), max(rr)), '| npairs', len(mean))
