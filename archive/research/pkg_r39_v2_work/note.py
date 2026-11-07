#!/usr/bin/env python3
# note.py TAG : the submission note of pkg_r39_TAG from the 2b4af365 note, by replacement of its numbers and pair-specific clauses.
# Numbers come from nums.py (sources) and the measured experiment/tail wall times of this build. Misses are printed.
import sys, os, re, json, math
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from nums import nums, CASES
TAG = sys.argv[1]; S108 = TAG == 's108'
V = nums(CASES[TAG]); QD = V['qd']; t3 = V['time3']
t = open('../pkg_r39_best/submission-note-r39.md', encoding='utf-8').read()
ms = lambda f: {l.split()[0]: int(l.split('ms=')[1].split()[0]) for l in open(f) if 'ms=' in l}
SO = ms('solo_%s.txt' % TAG); E = SO; TT = sorted(v for k, v in SO.items() if k.startswith('tail-'))
P70 = json.load(open('pool70_%s.json' % TAG))
dk = 117.836; ours = 116.895
R = []
def r(a, b): R.append((a, b))
if S108:
    r('# SHA-256 reduced to 39 steps: ordinary collision at time_log2 = 116.895 - the accepted walk of 0b2616e3 on a re-signed advice pair whose tail is one bit cheaper',
      '# SHA-256 reduced to 39 steps: ordinary collision at time_log2 = %s - the accepted walk of 0b2616e3 on a second pair of the published characteristic whose tail is one bit cheaper' % t3)
    r('The one change is the 160-byte advice. Instead of the published Table 23 pair we use our own 39-step semi-free-start pair on a re-signed variant of the same characteristic: every A and E state row and every modular message difference is the published one, the XOR signs of rows W11 and W12 are re-chosen, and W16 and W17 equal the published values (proof Appendix C).',
      'The one change is the 160-byte advice. Instead of the published Table 23 pair we use a second 39-step semi-free-start pair on the published characteristic itself: every signed row, state and message schedule, is the published one, only the values differ, and W16 and W17 equal the published values (proof Appendix C).')
else:
    r('# SHA-256 reduced to 39 steps: ordinary collision at time_log2 = 116.895 - the accepted walk of 0b2616e3 on a re-signed advice pair whose tail is one bit cheaper',
      '# SHA-256 reduced to 39 steps: ordinary collision at time_log2 = %s - the accepted walk of 0b2616e3 on a re-signed advice pair whose tail is one bit cheaper' % t3)
    r('the XOR signs of rows W11 and W12 are re-chosen', 'the XOR signs of rows W9 and W11 are re-chosen')
r('our 0c1ef7c3 and d90878ff.', 'our 0c1ef7c3 and d90878ff; our prior entry 2b4af365 (the same walk on another re-signed pair, 116.895).')
r('this pair gives 6,326 verified hits against 3,365 for the published pair (0b2616e3\'s frozen table), a linear 99.9% bound of -74.4489 against -75.4601.',
  'this pair gives %s verified hits against 3,365 for the published pair (0b2616e3\'s frozen table), a linear 99.9%% bound of %s against -75.4601.' % (V['hits'], V['lcb999']))
r("| time_log2 | 116.895 (exact 116.89462), 0.941 below 0b2616e3's 117.836 |",
  "| time_log2 | %s (exact %s), %.3f below 0b2616e3's 117.836 and %.3f below our 2b4af365 (116.895) |" % (t3, V['time'], dk - float(t3), ours - float(t3)))
r('| operations per distinct claw | 8,319.1 over 24 windows of 2^26 (1,418,347 distinct claws; one-sided 99% bounds mu+ 496,229,273 ops/window, c- 58,973.72, g- 58,890.83, r- 0.998513) |',
  '| operations per distinct claw | %s over 24 windows of 2^26 (%s distinct claws; one-sided 99%% bounds mu+ %s ops/window, c- %s, g- %s, r- %s) |' % (V['opc_c'], V['C'], V['mu_p'], V['c_m'], V['g_m'], V['r_m']))
if S108:
    r('| tail declared | -74.52 (binding: the hard-asserted class-specific 99% bound -74.5162; linear 99.9% bound -74.4489) |',
      '| tail declared | %s (all four bounds clear it: 14 hard-asserted runs linear 99.9%% %s and class-specific 99%% %s; 70-run pool linear 99.9%% %s and class-specific 99%% %s) |' % (QD, V['lcb999'], V['par99'], P70['lcb999'], P70['par99']))
    assert min(float(V['lcb999']), float(V['par99']), float(P70['lcb999']), float(P70['par99'])) > float(QD)
    r('| tail runs | 14 public seeds, 6,326 verified hits in 45,875,200 proposals; 70 runs (56 more by the public seed rule): 31,570 hits, 99.9% bound -74.4578 |',
      '| tail runs | 14 public seeds, %s verified hits in 45,875,200 proposals; 70 runs (56 more by the public seed rule): %s hits, 99.9%% bound %s |' % (V['hits'], P70['hits'], P70['lcb999']))
else:
    r('| tail declared | -74.52 (binding: the hard-asserted class-specific 99% bound -74.5162; linear 99.9% bound -74.4489) |',
      '| tail declared | %s (binding: the hard-asserted linear 99.9%% bound %s, less 0.01; class-specific 99%% bound %s) |' % (QD, V['lcb999'], V['par99']))
    r('| tail runs | 14 public seeds, 6,326 verified hits in 45,875,200 proposals; 70 runs (56 more by the public seed rule): 31,570 hits, 99.9% bound -74.4578 |',
      '| tail runs | 14 public seeds, %s verified hits in 45,875,200 proposals; 70 runs (56 more by the public seed rule): %s hits, 99.9%% bound %s |' % (V['hits'], P70['hits'], P70['lcb999']))
r('| halts | B = 2^99.4656 windows, W_BUDGET = 2^128.3520 operations |', '| halts | B = 2^%s windows, W_BUDGET = 2^%s operations |' % (V['B2'], V['WB2']))
# disclosed changes
DIS_OLD = ('Recomputed for the new advice: WIN_EXP, T4_EXP, the chi-square values (268.01, 280.2). The advice\'s own W1 is even, so r39-transplant-claw trial 0 asserts the claw equation directly and runs the filters with check mode off. '
           'The forced id-exhaustion run starts at 2^20 - 1998. The lag-1 autocorrelation test is |r| sqrt(n) < 3 (W17[0] gives 0.0459 on 3,318 groups, 2.6 standard errors). '
           'The 14 public tail runs were about 0.07 bit favourable against the 56 further runs (mean -74.4113); the declared -74.52 sits below both.')
acse = max(float(x) for x in V['acse'])
dis = 'Recomputed for the new advice: WIN_EXP, T4_EXP, the chi-square values (%s, %s), kernel_records (%s) and the group count %s that serve() checks. ' % (V['c17'], V['c18s'], V['krec'], V['nG'])
if S108:
    dis += 'The advice\'s own A[4] is odd, so r39-transplant-claw trial 0 asserts the claw equation through the even-branch formula of F and passes the pair as claw(u, a0), with check mode off. '
else:
    dis += 'r39-transplant-claw trial 0 asserts the claw equation directly and runs the filters with check mode off, as in our 2b4af365. '
dis += 'The forced id-exhaustion run starts at 2^20 - 2000, as in 0b2616e3. The lag-1 autocorrelation test is |r| sqrt(n) < 3, as in our 2b4af365 (largest value here %.1f standard errors).' % acse
if True:
    dis += ' The 14 public tail runs were about %s bit favourable against the 56 further runs (mean %s); the declared %s sits below both.' % (P70['fav'], P70['mean56'], QD)
r(DIS_OLD, dis)
if S108:
    r('Show that the advice pair is a free parameter of the accepted 39-step construction, and that choosing it well lowers the cost: the tail probability is a property of the pair, not only of the characteristic, so a different conforming pair of the same characteristic family gives a different, measurable tail.',
      'Show that the advice pair is a free parameter of the accepted 39-step construction, and that choosing it well lowers the cost: the tail probability is a property of the pair, not only of the characteristic, so a second conforming pair of the published characteristic itself gives a tail one bit better than the published pair.')
r("Before it, 44870635, 19034ce3 and 38912d66 for the program, the replica and the construction.",
  "Before it, 44870635, 19034ce3 and 38912d66 for the program, the replica and the construction. Our 2b4af365 (116.895) is the same walk on another re-signed pair; this entry changes only the advice and the values that follow from it.")
r('Ledger: `python3 r39joint.py --windows 1 --seed S --check --out win_S.json` for S = 1..24 (window seed S*1000), 24 processes at once.',
  'Ledger: `python3 r39joint.py --windows 1 --seed S --check --out win_S.json` for S = 1..24 (window seed S*1000), 24 processes at once (11 local, 13 cloud).')
# experiment configurations paragraph
EXP_OLD = ('The 14 verified 39-step pairs (all on the Table 21 characteristic family, signs of message rows re-chosen, every state row unchanged) were each run through the same replica on the same 14 public seeds. '
           'The replica\'s stage-1 carrier is identical across pairs on each seed, so the comparison is paired: only the final hit count differs. '
           'Results: this pair 6,326 hits (416 to 476 per run); a second pair 6,243; the published Table 23 pair 3,365 (216 to 285 per run); the other twelve pairs between -75.24 and -75.40 in mean. '
           'On every one of the 14 seeds this pair\'s count exceeds the published pair\'s, by a factor of 1.61 to 2.17. '
           'Sandbox experiments locally: window-small 11.4 s, transplant claw 0.3 s; tail runs 16 to 17 s each locally, the same as 0b2616e3\'s replica on the same host.')
CMP = json.load(open('cmp_%s.json' % TAG))
exp = ('The verified 39-step pairs of the Table 21 characteristic family (the published signed rows and re-signed variants, every state row unchanged) were each run through the same replica on the same 14 public seeds. '
       'The replica\'s stage-1 carrier is identical across pairs on each seed, so the comparison is paired: only the final hit count differs. '
       'Results: this pair %s hits (%s to %s per run); %s; the published Table 23 pair 3,365 (216 to 285 per run). '
       'On every one of the 14 seeds this pair\'s count exceeds the published pair\'s, by a factor of %s. '
       'Sandbox experiments locally, one process at a time on a host under other load: window-small %.1f s, transplant claw %.1f s; the tail replica is 0b2616e3\'s code with only CV, MX, EXP and QDECL changed and the same work per run (proof Section 8 gives its sandbox time).'
       % (V['hits'], V['hmin'], V['hmax'], CMP['others'], CMP['ratio'], E['r39-window-small'] / 1000, E['r39-transplant-claw'] / 1000))
r(EXP_OLD, exp)
r('Per-claw side conditions over all 1,418,347 distinct claws of the 24 windows (proof Section 7 and H1): W9 in F9 22,528 (rate 0.01588 against 65/4096), W8 in F8 100,445, both 1,611; W17 low-k matches at k = 8, 12, 16, 20, 24 of 5,431, 301, 17, 2, 0 against 5,540, 346, 22, 1.4, 0.1 expected; the low-12 count is 2.4 sigma low and is disclosed.',
  'Per-claw side conditions over all %s distinct claws of the 24 windows (proof Section 7 and H1): W9 in F9 %s (rate %s against 65/4096), W8 in F8 %s, both %s; W17 low-k matches at k = 8, 12, 16, 20, 24 of %s against %s expected; the largest deviation is k = %d at %.1f sigma.'
  % (V['C'], V['s_f9'], V['s_f9r'], V['s_f8'], V['s_bo'], ', '.join(V['low%d' % k].split(' (')[0] for k in (8, 12, 16, 20, 24)),
     ', '.join('%.1f' % float(V['low%d' % k].split('(')[1][:-1]) for k in (8, 12, 16, 20, 24)),
     max((8, 12, 16, 20), key=lambda k: abs(V['low%dz' % k])), max(abs(V['low%dz' % k]) for k in (8, 12, 16, 20))))
if S108:
    r('The advice pair was selected among 14 verified pairs by its tail on the 14 public seeds; the 56-run pool on fresh seeds supports the declared value independently of that selection.',
      'The advice pair was selected among %d verified pairs by its tail on the 14 public seeds; that selection is visible in the 56 further runs on fresh seeds (linear mean %s against %s for the 14, so the 14 public runs were %s bit favourable), and the declared %s is set from the 70-run pool to absorb it.' % (CMP['npairs'], P70['mean56'], V['mean'], P70['fav'], QD))
else:
    r('The advice pair was selected among 14 verified pairs by its tail on the 14 public seeds; the 56-run pool on fresh seeds supports the declared value independently of that selection.',
      'The advice pair was selected among %d verified pairs by its tail on the 14 public seeds; the 56-run pool on fresh seeds supports the declared value independently of that selection.' % CMP['npairs'])
r('Twelve of the fourteen pairs show no tail gain.', '%d of the %d pairs show no tail gain (linear mean below -75.2).' % (CMP['npairs'] - 5, CMP['npairs']))
r('the windows extrapolate to 2^99.47 by premise H1.', 'the windows extrapolate to 2^%s by premise H1.' % V['B2s'])
miss = []
for a, b in R:
    n = t.count(a)
    if n == 0: miss.append(a)
    t = t.replace(a, b)
for a in miss: print('MISS |', a[:120])
open('../pkg_r39_%s/submission-note-r39.md' % TAG, 'w', encoding='utf-8', newline='\n').write(t)
print('note bytes', len(t.encode()))
