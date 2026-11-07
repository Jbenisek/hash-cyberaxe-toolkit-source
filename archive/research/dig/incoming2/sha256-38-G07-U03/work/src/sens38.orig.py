# sens38.py - sensitivity of the derivative's exact ledger (each row: ledger() with one input changed; N_G recomputed),
# and each lever left out (its inputs at the base values).
import sys, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ledger38 import *
from fractions import Fraction as Fr
def row(name, **kw):
    o = ledger(show=False, **kw); print('%-62s %.5f   (attack %.4f, N_G 2^%.4f)' % (name, o['log2_T'], o['attack_units_log2'], o['NG_log2'])); return o
row('claimed configuration (q3_model 2^-101.5, delta 1, A_C 2^70, A_S 2^60, DEV 2^60)')
row('q3_model = measured mean 2^-101.0', q3_log2=-101.0)
row('q3_model = 2^-101.25', q3_log2=-101.25)
row('q3_model = 2^-102 (one bit below the measured bounds)', q3_log2=-102.0)
row('q3_model = 2^-103', q3_log2=-103.0)
row('pair budget delta = 1/2', delta=Fr(1, 2))
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
row('without L0 (tables over all 32 words of G)', ngw=32, p2=dict(p2, P6_COUNT=205, P6_FILL=269))
row('without L2/L5 (W7 path and 3-word entries of the base)', esz=3, costs=dict(cs, P0=96, GROUP4=85, PASS_ENTRY=3, X_E17=58, X_A17int=82, X_SUCC=3211), p2=dict(p2, P5_SETUP=32, P5_BODY_MAX=58, P5_APPEND=28, P6_FILL=255, P6_PREFIX_NONEMPTY=14))
row('without L4 (deep path charged at N1_MAX)', n2=False, costs=dict(cs, EPI=15, X_SUCC=cs['X_SUCC'] - 1))
