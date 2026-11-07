"""check2-3: own exact re-implementation of the proof.md Section 7 ledger (cert.py form, N_G and the caps recomputed
from the success bound with ceilings), independent of levers_r38.py's linear N_G scaling.
  S = SR p2 q3_model, q_lb = S (1 - delta/2), N_G = ceil(L / q_lb), L = 0.504182 (= -ln(1-0.396) rounded up),
  NE_MAX = ceil(N_G SR 2^-27 (1 + 2^-6)), NW_MAX = ceil(N_G SR 2^-27 p2 (1 + 2^-5)), N1_MAX = ceil(N_G SR 2^-27 p2 2^-10 * 4),
  online = N_G (64 + 256*30 + 15) + 10 NE_MAX + 66 NW_MAX + 3158 N1_MAX + 256*344064*3234,
  T = A_C + A_S + DEV + (pre + init + online + fin_ops)/C + N_G + 6."""
import sys
sys.dont_write_bytecode = True
from fractions import Fraction
import mpmath as mp
mp.mp.dps = 80
SR = 191_773_672_732; F7N = 287_309_824; C = 2728
PRE = 466_412_701_031_896_270_852_028; INIT = 1024; FIN_OPS = 1024; FIN_U = 6
AC = AS = 1 << 70; DEV = 1 << 64

def ceil_mp(x): return int(mp.ceil(x))
def ledger(q3, delta=mp.mpf(1), L=mp.mpf('0.504182'), ac=AC, as_=AS, dev=DEV):
    p2 = mp.mpf(F7N) / 2 ** 32
    S = SR * p2 * q3; qlb = S * (1 - delta / 2)
    NG = ceil_mp(L / qlb)
    ENE = mp.mpf(SR) / 2 ** 27; ENW = ENE * p2; EN1 = ENW / 2 ** 10
    NE = ceil_mp(NG * ENE * (1 + mp.mpf(2) ** -6)); NW = ceil_mp(NG * ENW * (1 + mp.mpf(2) ** -5)); N1 = ceil_mp(NG * EN1 * 4)
    online = NG * (64 + 256 * 30 + 15) + NE * 10 + NW * 66 + N1 * (26 + 3132) + 256 * 344064 * (10 + 66 + 3158)
    T = Fraction(ac + as_ + dev + NG + FIN_U) + Fraction(PRE + INIT + online + FIN_OPS, C)
    lg = mp.log(mp.mpf(T.numerator) / T.denominator, 2)
    return lg, NG, NE, NW, N1, online, mp.log(S, 2)

lg, NG, NE, NW, N1, on, lS = ledger(mp.mpf(2) ** -102)
print('q3_model 2^-102 (filed): log2 S %.5f  N_G %d  NE_MAX %d  NW_MAX %d  N1_MAX %d  online %d  T 2^%.6f' % (lS, NG, NE, NW, N1, on, lg))
print('  matches proof.md 7 (N_G 398563284869814990705, NE_MAX 578375349533157559511618, NW_MAX 39285380938092027141708, '
      'N1_MAX 148808261129136466446, online 11938977653196641712347327):',
      (NG, NE, NW, N1, on) == (398563284869814990705, 578375349533157559511618, 39285380938092027141708, 148808261129136466446, 11938977653196641712347327))
dstruct = mp.mpf(767) / 2 ** 18 + mp.mpf(SR) / 2 ** 55
Lnp = mp.ceil(-mp.log(1 - mp.mpf('0.39')) * 10 ** 6) / 10 ** 6
print('no-pad L = -ln(0.61) rounded up = %s; structural pair delta = %.6f' % (mp.nstr(Lnp, 7), float(dstruct)))
print('success-bound-only row (L 0.39, q3 2^-102): T 2^%.6f  (proof.md 7: 72.61489)' % ledger(mp.mpf(2) ** -102, L=Lnp)[0])
for lab, e in (('2^-101.0101 (leader R1 bound = go line)', '-101.0101'), ('2^-101.0002 (G2 bound, rounded)', '-101.0002'),
               ('2^-101.00017 (G2 bound, unrounded)', '-101.00017'), ('2^-101.00030 (checker fresh replicate bound)', '-101.00030')):
    q = mp.mpf(2) ** mp.mpf(e)
    a = ledger(q)[0]; b = ledger(q, L=Lnp)[0]; c = ledger(q, delta=dstruct)[0]; d = ledger(q, delta=dstruct, L=Lnp)[0]
    print('q3_model %-45s T 2^%.6f (vs 72.64 %+.4f) | no pad %.6f | pair 0.002931 %.6f | pair + no pad %.6f' % (lab, a, a - 72.64, b, c, d))
