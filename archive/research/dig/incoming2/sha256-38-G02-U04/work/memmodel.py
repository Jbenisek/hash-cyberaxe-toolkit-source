# scan-once-wave2 sha256-38-G02-U04: price memory objects CTAB, CODE7, CODEO with the r38 ledger (a0lean38.py, copy of pkgR38M3 experiment source)
import sys, math, json
from fractions import Fraction
from decimal import Decimal, getcontext
import a0lean38 as L
getcontext().prec = 80
CAL = L.calibrate()
K = len(L.CLASSES); C = 2728
p7 = Fraction(287309824, 2**32)

def run(dFB=0, dVisit=0, dW7=0, label=''):
    """Ledger with extra ops: dFB per first block (always), dVisit per class visit (p7-weighted, K classes), dW7 per class per W7 test (all K classes)."""
    cal = CAL
    rows, info = L.ledger(cal, show=False)   # baseline pieces
    g = info['g']; vbar0 = info['vbar']; pany = info['pany']
    khit = K * p7
    vbar = vbar0 + dFB + khit * dVisit + K * dW7
    class_max = max(7 + 15 * (cal['prog'][h] + 6) + 3840 * (cal['lane_max'][c[2]] + cal['step3b']) for c, h in zip(L.CLASSES, L.GRP)) + dVisit
    vmax_f = K * (44 + 2 + 4 + class_max) + cal['fb_scalars'] + cal['planes'] + dFB + K * dW7
    F = cal['fixed']
    q3 = Decimal(2) ** Decimal('-97.7838'); h3 = 1 - Decimal(2) ** Decimal('-9.5'); eps = Fraction(1, 2**16); two = Decimal(2); succ = Decimal('0.39')
    N = 1
    for _ in range(6):
        vb = Decimal(vbar.numerator) / Decimal(vbar.denominator) if isinstance(vbar, Fraction) else Decimal(vbar)
        pcap = Decimal(vmax_f) / (Decimal(eps.denominator) ** 2 * Decimal(N) * vb) if N > 1 else Decimal(0)
        x = -(Decimal(1) - succ - two ** -60 - pcap).ln()
        N = int((x / (Decimal(g.numerator) / Decimal(g.denominator) * q3 * h3)).to_integral_value(rounding='ROUND_CEILING'))
    VMAX = -((-N * Fraction(vbar) * (1 + eps)).__floor__())
    tot = 0
    for (nm, v) in rows:
        if nm.startswith('data-dependent'): tot += VMAX
        elif nm.startswith('overshoot'): tot += class_max + 1000
        else: tot += int(v)
    T = math.log2(tot) - math.log2(C)
    return T, tot, N

def S(T, B): return T + max(0.0, math.log2(B) - 20)
if __name__ == '__main__':
    parts, B0 = L.memory(CAL)
    T0, tot0, N0 = run()
    print('BASE time_log2(exact)=%.10f B=%d log2B=%.6f S=%.10f' % (T0, B0, math.log2(B0), S(T0, B0)))
    for p in parts: print('  ', p[1], p[0])
    print('prog lengths', CAL['prog'], 'classes_of', CAL['classes_of'])
    print('w7 avg per class', float(sum(c * p for (c, ok), p in CAL['w7'].items())), 'N0', N0)
