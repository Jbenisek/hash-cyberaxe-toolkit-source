'''Price check of the E3-fixed design against the score rules (score = log2(ops / 430), success >= 0.39, preprocessing
added, ops counted as executed).  Inputs: P1 at the best pair 2^-44.00 (pairsum.py), T1 in [1, 2^19) (exact uniform
rate), one 2^32 sweep of the cyclic word per E3-held point (k = 1, no T1-before-loop design, no list match: brute.c),
43 ops per candidate (solve.cu, rotation = 1 op).'''
from math import log, log2
p1 = 2 ** -44.00
n = -log(1 - 0.39) / p1                                   # trials for success exactly 0.39
t1 = ((1 << 19) - 1) / 2 ** 32
per_trial_cand = 2 ** 32 / t1
for ops in (43, 1):
    total = n * per_trial_cand * ops
    print('ops/candidate %2d: trials 2^%.3f, candidates per trial 2^%.2f, ops per trial 2^%.2f, score %.2f' %
          (ops, log2(n), log2(per_trial_cand), log2(per_trial_cand * ops), log2(total / 430)))
bar = 63.6027 + log2(430) - log2(n)
print('bar: an E1 trial must cost under 2^%.2f ops; with the T1 filter paid after the solve, a solve under 2^%.2f ops' % (bar, bar - log2(1 / t1)))
print('even with T1 free of charge, one exhaustive 2^32 sweep at 1 op/candidate scores %.2f' % log2(n * 2 ** 32 / 430))
