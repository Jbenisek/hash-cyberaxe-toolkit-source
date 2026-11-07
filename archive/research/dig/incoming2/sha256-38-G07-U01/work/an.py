import math, re, sys
from fractions import Fraction
src = open('a0lean38.py', encoding='utf-8').read()
# parametrised copy: P7S scales the class-pass probability p7 everywhere in ledger (g, classes, lanes, hits); drop the g assertion
src = src.replace("def ledger(cal=None,", "def ledger(P7S=Fraction(1), cal=None,",1)
src = src.replace("p7 = Fraction(287309824, 2**32); K = len(CLASSES); g = K * 3840 * p7; assert g == Fraction(92475, 4)",
                  "p7 = Fraction(287309824, 2**32) * P7S; K = len(CLASSES); g = K * 3840 * p7")
assert 'P7S' in src
ns = {'__name__': 'a0'}
exec(compile(src, 'a0p', 'exec'), ns)
L = ns; cal = L['calibrate']()
def T(**kw):
    rows, info = L['ledger'](cal=dict(cal), show=False, **kw); N = sum(int(v) for _, v in rows)
    return math.log2(N) - math.log2(2728), N, info, rows
base, N0, i0, rows0 = T()
print('known answer: log2 T = %.5f (claim 87.90374)' % base)
print('A_C=2^84 -> %.5f (claim 87.99563)' % T(A_C=2**84)[0])
print('--- H4 R2/R3')
for k, v in [('A_C', 2**78), ('A_S', 2**74), ('DEV', 2**64)]:
    print(k, 'share of N = %.6g' % (v * 2728 / N0))
print('N_FB*C share %.4f; data-dep V_MAX share %.4f' % (i0['N_FB'] * 2728 / N0, i0['VMAX'] / N0))
for lab, kw in [('A_C=2^78 (filed)', {}), ('A_C=2^79', dict(A_C=2**79)), ('A_C=2^80', dict(A_C=2**80)), ('A_C=2^82', dict(A_C=2**82)), ('A_C=2^84', dict(A_C=2**84)), ('A_C=2^90', dict(A_C=2**90)),
                ('A_C=2^77', dict(A_C=2**77)), ('A_C=2^76', dict(A_C=2**76)), ('A_C=2^70', dict(A_C=2**70)), ('A_C=0', dict(A_C=0)),
                ('A_S=2^80', dict(A_S=2**80)), ('A_S=2^70', dict(A_S=2**70)), ('A_S=0', dict(A_S=0)), ('A_S=2^78', dict(A_S=2**78)),
                ('DEV=2^70', dict(DEV=2**70)), ('DEV=2^74', dict(DEV=2**74)), ('DEV=0', dict(DEV=0)), ('all three 0', dict(A_C=0, A_S=0, DEV=0))]:
    t = T(**kw)[0]; print('%-20s %.5f  delta %+.5f' % (lab, t, t - base))
# thresholds: A_C that costs 0.01 / 0.1 bit
for d in (0.01, 0.1):
    lo, hi = 78.0, 100.0
    for _ in range(40):
        m = (lo + hi) / 2
        t = T(A_C=int(2**m))[0] if m < 62 else T(A_C=int(2**(m - 40)) << 40)[0]
        if t - base < d: lo = m
        else: hi = m
    print('A_C where cost = %.2f bit: 2^%.3f' % (d, lo))
# CPU-year recount of A_C at the accepted price 2^21.427 units/CPU-s (proof price unit), and the factor vs the re-run
price = 2**21.427
for k, v in [('A_C', 2**78), ('A_S', 2**74), ('DEV', 2**64)]:
    cs = v / price; print('%s = %.4g CPU-s = %.4g CPU-years at 2^21.427 units/s' % (k, cs, cs / 31557600))
print('A_C / (593858 CPU-s re-run at that price) = %.4g = 2^%.3f' % (2**78 / (593858 * price), math.log2(2**78 / (593858 * price))))
print('A_S 2^74 / paper 2^38.3 = 2^%.2f ; paper A_S 2^41.3-style 37-case: n/a' % (74 - 38.3))
print('wrong-unit negative control: 2^78/(593858*2644) = %.4g (2^%.2f) vs proof "2^37" factor %.4g' % (2**78 / (593858 * 2644), math.log2(2**78 / (593858 * 2644)), 2.0**37))
print('--- H1 R4')
for e in (0.01, 0.05, 0.10):
    # whole-rate error: q3 scaled by 1/(1+e) (rate lower than modelled)
    t1 = T(q3_log2=str(Decimal := -97.7838 - math.log2(1 + e)))[0] if False else None
from decimal import Decimal
for e in (0.001, 0.01, 0.05, 0.1):
    q = Decimal('-97.7838') - Decimal(math.log2(1 + e))
    t_q3 = T(q3_log2=str(q))[0] - base
    s = Fraction(1) / Fraction(1 + e).limit_denominator(10**6)
    t_p7 = T(P7S=s)[0] - base
    s2 = Fraction(1 + e).limit_denominator(10**6)
    t_p7up = T(P7S=s2)[0] - base
    print('rate error %.3f: q3/(1+e) -> %+.5f bit ; p7/(1+e) (class pass rate low, classes+lanes+hit costs scale too) -> %+.5f ; p7*(1+e) -> %+.5f' % (e, t_q3, t_p7, t_p7up))
# measured ratios
pc = [(17972582, 17956864), (35894449, 35913728), (71766725, 71827456)]
gp = [(69014714880, 1.0009), (137834684160, 0.9995), (275584224000, 0.9992)]
r16 = [(468, 513.75), (1062, 1027.5), (2031, 2055.0)]
o = sum(a for a, b in pc); e = sum(b for a, b in pc)
print('passing classes pooled obs/exp = %.6f (obs %d exp %d), rel sd(poisson) %.2e => log2 %.6f' % (o / e, o, e, 1 / math.sqrt(o), math.log2(o / e)))
o = sum(a for a, b in r16); e = sum(b for a, b in r16)
print('row16 passes pooled obs/exp = %.5f (obs %d exp %.2f) rel sd %.4f => log2 %.5f, z=%.2f' % (o / e, o, e, 1 / math.sqrt(o), math.log2(o / e), (o - e) / math.sqrt(e)))
sd = 1 / math.sqrt(o)
print('row16 rate error 1 sd (%.4f) as q3-type error: %.5f bit; ledger(p7) effect of passing-class 1-sd: %.6f' % (sd, math.log2(1 + sd) , 0))
