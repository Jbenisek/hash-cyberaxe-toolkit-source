# sens38.py - sensitivity of the derivative's exact ledger (each row: ledger() with one input changed; N_G recomputed),
# and each lever left out (its inputs at the base values).
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger38 import *
from fractions import Fraction as Fr
def row(name, **kw):
    o = ledger(show=False, **kw); print('%-62s %.5f   (attack %.4f, N_G 2^%.4f)' % (name, o['log2_T'], o['attack_units_log2'], o['NG_log2'])); return o
row('claimed configuration (q3_model 2^-101.5, delta 0.564, A_C 2^70, A_S 2^60, DEV 2^60)')
row('q3_model = measured mean 2^-101.0', q3_log2=-101.0)
row('q3_model = 2^-101.25', q3_log2=-101.25)
row('q3_model = 2^-102 (one bit below the measured bounds)', q3_log2=-102.0)
row('q3_model = 2^-103', q3_log2=-103.0)
row('pair budget delta = 0.56 (the limits rounded down)', delta=Fr(56, 100))
row('pair budget delta = 1/2', delta=Fr(1, 2))
row('pair budget delta = 1 (the budget of aa0496d3)', delta=Fr(1))
row('pair budget delta = 1.5', delta=Fr(3, 2))
row('A_C = 2^72', ac=72); row('A_C = 2^74', ac=74); row('A_C = 2^76', ac=76); row('A_C = 2^78', ac=78); row('A_C = 2^66', ac=66)
row('A_S = 2^50, DEV = 2^50 (the allowances of the r37 filings)', as_=50, dev=50)
row('A_S = 2^50 alone', as_=50)
row('A_S = 2^70, DEV = 2^64 (the allowances of 0ae69bcb)', as_=70, dev=64)
row('A_S = 2^64, DEV = 2^64', as_=64, dev=64)
row('cap margin eps = 2^-8 (0.39%)', eps=Fr(1, 256), eps2=Fr(1)); row('cap margin eps = 2^-6', eps=Fr(1, 64), eps2=Fr(1)); row('cap margin eps = 2^-4 (uniform)', eps=Fr(1, 16), eps2=Fr(1)); row('cap margin eps = 2^-3', eps=Fr(1, 8), eps2=Fr(1))
row('success bound 0.396 instead of 0.39', succ=Fr(396, 1000))
row('no allowances (the attack and preprocessing alone)', ac=-1000, as_=-1000, dev=-1000)
cs = json.load(open(os.path.join(RUNS, 'costs.json'))); p1 = json.load(open(os.path.join(RUNS, 'pre1.json'))); p2 = json.load(open(os.path.join(RUNS, 'pre2.json')))
# the pass iterations scale with the words listed: 6 (count) and 10 (fill) operations per word of G
row('without L0 (tables over all 32 words of G)', ngw=32, p2=dict(p2, P6_COUNT_IT=p2['P6_COUNT_IT'] + 6 * 10, P6_FILL_IT=p2['P6_FILL_IT'] + 10 * 10))
row('without L2/L5 (W7 path and 3-word entries of the base)', esz=3, costs=dict(cs, P0=96, GROUP4=85, PASS_ENTRY=3, X_E17=58, X_A17int=82, X_SUCC=3211), p2=dict(p2, P5_SETUP=32, P5_BODY_MAX=58, P5_APPEND=28, P6_FILL_IT=p2['P6_FILL_IT'] + 22, P6_PREFIX_NONEMPTY=14))
row('without L4 (deep path charged at N1_MAX)', n2=False, costs=dict(cs, EPI=15, X_SUCC=cs['X_SUCC'] - 1))

# the four changes of this derivative (Appendix D.3), one after the other: log2 T of the exact ledger (6 decimals) and the change against the row before
p2_aa = {"P5_SETUP": 35, "P5_BODY_MAX": 56, "P5_APPEND": 43, "P5_LOOP": 3, "P6_COUNT": 145, "P6_FILL": 189, "P6_PREFIX_EMPTY": 6, "P6_PREFIX_NONEMPTY": 11}   # pre2.json of aa0496d3
printed = dict(p2_aa, P5_SETUP=p2['P5_SETUP'], P5_BODY_MAX=p2['P5_BODY_MAX'], P5_APPEND=p2['P5_APPEND'], P6_FILL=233)                                   # the bodies as they execute
loop_old = dict(p2, P6_ZERO16=64, P6_COUNT_IT=145 + 3, P6_COUNT_VAR=16, P6_FILL_IT=233 + 3, P6_FILL_VAR=16)                                              # 4 per header, loop control +3, 16 per variant
steps = [('aa0496d3 as filed (its pre2.json, pair budget 1)', dict(p2=p2_aa, delta=Fr(1))),
         ('(1) the counts the printed bodies execute (P6 fill 233, P5 setup 37, append 46, body 57)', dict(p2=printed, delta=Fr(1))),
         ('(2) + P6 zero unrolled 16 times (34 per 16 headers)', dict(p2=dict(loop_old, P6_ZERO16=p2['P6_ZERO16']), delta=Fr(1))),
         ('(3) + Y loop of the count and fill passes on u (144 / 232 per iteration, 16 / 17 per variant)', dict(p2=p2, delta=Fr(1))),
         ('(4) + pair budget delta = 0.564 instead of 1  [this derivative]', dict(p2=p2, delta=Fr(141, 250)))]
prev = None
for name, kw in steps:
    o = ledger(show=False, p1=json.load(open(os.path.join(RUNS, 'pre1.json'))), **kw)
    print('%-92s %.6f  %s  (claim %.5f)' % (name, o['log2_T'], '          ' if prev is None else '%+.6f' % (o['log2_T'] - prev), o['time_log2'])); prev = o['log2_T']
