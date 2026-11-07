#!/usr/bin/env python3
# Ledger of the counter search (proof.md 9.1 and Section 11): integers only, standard library.  Run: python3 ledger.py
from fractions import Fraction
from math import isqrt, log2
cd = lambda a, b: -(-a // b)                                            # ceiling division
FACTOR = 10 * 138512695296 // 11
RC = cd(cd(24797 << 128, 50000 * FACTOR * ((1 << 21) - 1)), 1 << 19)   # RUN_CONTEXTS
STEPS = RC << 19                                                        # RUN_STEPS
s = isqrt(10 * RC - 1) + 1                                              # ceil(sqrt(10 RUN_CONTEXTS))
E_B = cd(1000026 * STEPS * 233715456, 10**6 << 32) + (s << 19)          # E lanes
P_B = cd(1000176 * STEPS * 18289159183466496, 10**6 << 64) + (s << 19)  # passing lanes
A_B = cd(852139 * RC, 128) + 16384 * s                                  # opened clusters
G_B = 7164 * RC + 84261 * s                                             # fills, F budget of H_G_cluster
F_B = cd(9 * RC, 4) + 128 * s                                           # straddling clusters
MC = cd(101 * STEPS * 335060079487497, 100 << 48)                       # m_C = 1.01 RUN_STEPS u_U, rounded up
LC = 15012 << 19
CREDIT = MC + isqrt(40 * LC * MC - 1) + 1 + 14 * LC + 15012
C_B = cd(MC, 4272) + (s << 19)                                          # calls, each with U >= 4,272
OPEN = 5 + 3 + 6 + 2 + 4 + 70 + 11 + 13                                 # opened cluster
U = dict(open=OPEN, E=6, fill=56, pas=1 + 27 + 7, call=6, strad=5 + 21 + 4 * 45 + 29 + 2 - OPEN)
REP, TAIL = 2 + 17 + 6 + 4 * 7, 2 + 17 + 6 + 4 * 4                      # representative batch, last batch
CTX = 509 + 160 + 48896 + 17 * 2341 + 16                                # context
WB = (U['open'] * A_B + U['E'] * E_B + U['fill'] * G_B + U['pas'] * P_B + U['call'] * C_B + U['strad'] * F_B)
WCTX = (U['open'] * 16384 + U['E'] * 2**19 + U['fill'] * 84261 + (U['pas'] + U['call']) * 2**19 + U['strad'] * 128)
ONCE = sum([2**38, 2**26, 2**20, 2**20, 4 * 2**26, 2**50, 40, 12 * 2**20, 2**27, 2**34, 3 * 2**20, 14 * 2**20, 2**36,
            2 * 2**22, 2**38, 2**41, 2**34, 2**28, 2**20, 2**40, 2**38, 2**36, 2**37, 3 * 2**35, 30 * 2**32, 2**32])
ROWS = [('context', CTX * (RC + 1)), ('representative batches', (REP * 2340 + TAIL) * RC),
        ('opened clusters', U['open'] * (A_B + 16384)), ('E lanes', U['E'] * (E_B + 2**19)),
        ('fills', U['fill'] * (G_B + 84261)), ('passing lanes', U['pas'] * (P_B + 2**19)),
        ('calls', U['call'] * (C_B + 2**19)), ('straddling clusters', U['strad'] * (F_B + 128)),
        ('credit', CREDIT), ('one-time work', ONCE)]
S_OLD = 116 * 5 * 2**53 + 116 * (2**51 + 2**10) + 2**50
N = sum(v for _, v in ROWS) + S_OLD + 430 * 2**38                       # 430 T
assert WB + WCTX == sum(v for k, v in ROWS if k in ('opened clusters', 'E lanes', 'fills', 'passing lanes', 'calls',
                                                    'straddling clusters'))
print('RUN_CONTEXTS', RC, 's', s)
for name, v in (('E_BUDGET', E_B), ('PASS_BUDGET', P_B), ('A_BUDGET', A_B), ('G_BUDGET', G_B), ('FB_BUDGET', F_B),
                ('m_C', MC), ('CREDIT', CREDIT), ('CALL_BUDGET', C_B), ('WB', WB), ('W_CTX', WCTX)):
    print(name, v)
print('units', U, 'representative', REP, TAIL, 'context', CTX)
for k, v in ROWS:
    print('%-24s %d  log2 %.3f' % (k, v, log2(v)))
print('S_old', S_OLD)
print('N =', N)
PW = 100000
a = (N**PW // 430**PW).bit_length() - 1
while (1 << (a + 1)) * 430**PW <= N**PW: a += 1
while (1 << a) * 430**PW > N**PW: a -= 1
claim = Fraction(-(-(a + 1) * 10**5 // PW), 10**5)
print('certificate: 2^%d * 430^%d <= N^%d < 2^%d * 430^%d' % (a, PW, PW, a + 1, PW))
print('log2(N/430) = %.10f' % (log2(N) - log2(430)))
print('time_log2 = %.5f' % float(claim))
