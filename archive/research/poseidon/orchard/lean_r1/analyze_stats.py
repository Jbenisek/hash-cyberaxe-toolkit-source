"""Summary of the single-centre campaign (data/stats.json by collect.py) against the Poisson(1/2) root-count model."""
import json, math, os
HERE = os.path.dirname(os.path.abspath(__file__))
s = json.load(open(os.path.join(HERE, 'data', 'stats.json')))
n, k = s['centres'], s['successes']
hist = {int(a): b for a, b in s['degG_histogram'].items()}
lam = 0.5
pk = lambda j: math.exp(-lam) * lam ** j / math.factorial(j)
print('centres %d successes %d rate %.4f wilson95 [%.3f, %.3f]; model 1-exp(-1/2) = %.4f; expected successes %.1f +- %.1f' % (
    n, k, k / n, s['wilson95'][0], s['wilson95'][1], 1 - math.exp(-lam), n * (1 - math.exp(-lam)), math.sqrt(n * 0.3935 * 0.6065)))
cells = [(j, hist.get(j, 0), n * pk(j)) for j in range(4)] + [('>=4', sum(v for a, v in hist.items() if a >= 4), n * (1 - sum(pk(j) for j in range(4))))]
chi = sum((o - e) ** 2 / e for _, o, e in cells if e > 0)
print('root-count histogram (observed / expected under Poisson(1/2)):', ', '.join('%s: %d / %.1f' % c for c in cells), '; chi-square %.2f (4 dof, 5%% critical 9.49)' % chi)
print('by line j (successes / centres):', s['by_j'])
print('all collisions verified by the big-int reference and the organizer verifier:', s['all_verified'], '(%d collisions)' % s['n_collisions'])
