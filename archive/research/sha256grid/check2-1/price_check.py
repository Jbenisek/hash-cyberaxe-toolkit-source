#!/usr/bin/env python3
"""check2-1: independent re-derivation of the A_S price and the CPU-second -> unit conversions (research only).
Ledger integers are those of map-r38/levers_r38.py (c99df2dc ledger); the formula is proof.md line 625:
T = A_C + A_S + DEV + (pre + init + online + fin_ops)/C + N_G + fin_units."""
from fractions import Fraction as F
import math
from decimal import Decimal, getcontext
getcontext().prec = 50
C = 2728
PRE = 466_412_701_031_896_270_852_028
INIT = 1024
ONLINE = 11_938_977_653_196_641_712_347_327
NG = 398_563_284_869_814_990_705
FIN_OPS = 1024
FIN_UNITS = 6

def lg(x):
    x = F(x)
    return float((Decimal(x.numerator).ln() - Decimal(x.denominator).ln()) / Decimal(2).ln())

def T(A_C, A_S, DEV, pad=F(1)):
    return A_C + A_S + DEV + F(PRE + INIT + FIN_OPS, C) + F(ONLINE, C) * pad + NG * pad + FIN_UNITS

base = lg(T(2**70, 2**70, 2**64))
a50 = lg(T(2**70, 2**50, 2**64))
a50p = lg(T(2**70, 2**50, 2**64, F(50, 51)))
print('base (A_S 2^70)            %.6f  (package proof.md line 4: 2^72.633442)' % base)
print('A_S 2^50                   %.6f  ceil5 %.5f  vs base %+.4f  vs board 72.64 %+.4f  vs ours 72.61489 %+.4f'
      % (a50, math.ceil(a50 * 1e5) / 1e5, a50 - base, a50 - 72.64, a50 - 72.61489))
print('A_S 2^50, N_G pad 50/51    %.6f  ceil5 %.5f  vs board %+.4f  vs ours %+.4f'
      % (a50p, math.ceil(a50p * 1e5) / 1e5, a50p - 72.64, a50p - 72.61489))
print('share of A_S=2^70 in the base total: %.4f' % (2**70 / float(T(2**70, 2**70, 2**64))))
u = math.log2(1e10 / C)
print('units per CPU-second at 10^10 word ops / C: 2^%.4f' % u)
for s in (21.66, 331.67, 51.25, 570.72, 658.08, 3520):
    print('  %8.2f CPU-s -> 2^%.3f units; 2^50 is 2^%.2f above' % (s, math.log2(s) + u, 50 - math.log2(s) - u))
print('paper 2^38.3 units -> %.0f CPU-s at this rate' % (2 ** (38.3 - u)))
