# deadG_price.py - check2-4 side note (not part of the scout's claim): price dropping the G words that can never
# succeed.  exact17.out (COMPUTED, exhaustive over the 2^22 masked E17 values): 10 of the 32 G words have no E17^x with
# every row-17 cell and no E17^x with the M-event row-17 predicate, so neither the filed program nor the M program can
# succeed on them.  Tables built for the other 22 words keep every success (S unchanged) and cut entries, W7 passes and
# first-test passes by 10/32.  Online part exact given the counted per-item costs; the P6 build costs per (Y, variant)
# with 22 instead of 32 targets are a GUESS (count pass 6 ops and fill pass 8 ops per target removed).
import math
from fractions import Fraction as F
exec(open("ledger_chk.py").read().split("b = ledger()")[0])   # R, C, LOG, ledger (my transcription of cert.py)
def ledger_g(nG=32, q3_log2=-102.0, deep_mult=1, p6=True):
    m = len(R); SR = sum(R)
    p2 = F(287309824, 2 ** 32); p16 = F(nG, 2 ** 32)
    q3 = F(math.floor(2.0 ** q3_log2 * 2 ** 140), 2 ** 140)
    S = SR * p2 * q3; qlb = S / 2
    cexp = F(math.ceil(-math.log(1 - 0.396) * 10 ** 6), 10 ** 6); NG = -(-cexp // qlb)
    BMAX = 14 * nG * 768; muE = SR * p16; muW = muE * p2; mu1 = muW / 2 ** 10; rng = m * BMAX
    def cap(mu, t): return -(-(NG * mu * (1 + t)) // 1), float(2 * (t * mu) ** 2 * NG / rng ** 2)
    NE_MAX, eE = cap(muE, F(1, 64)); NW_MAX, eW = cap(muW, F(1, 32)); N1_MAX, e1 = cap(mu1, F(3))
    c17b = 3158 * deep_mult
    online = NG * (64 + m * 30 + 15) + NE_MAX * 10 + NW_MAX * 66 + N1_MAX * c17b + rng * (10 + 66 + c17b)
    cnt, fil = (211 - 6 * (32 - nG), 275 - 8 * (32 - nG)) if p6 else (211, 275)
    pre = (2 ** 32 * 152 + 768 * 64 + 32 * 128 + m * 768 * (2 ** 29 * 67 + 50) + SR * 25
           + 2 ** 32 * SR * (cnt + fil) + m * 2 ** 64 * 14 + m * 2 ** 32 * 20)
    T = F(2) ** 70 * 2 + F(2) ** 64 + F(pre + 2048 + online, C) + NG + 6
    succ = 1 - math.exp(-float(NG * qlb)) - math.exp(-eE) - math.exp(-eW) - math.exp(-e1)
    return LOG(T), succ
print("filed (32 words): %.5f" % ledger_g()[0])
for g, lab, dm in ((1.0, "filed program", 1), (10.692, "M program, scout g, deep x2", 2), (10.928, "M program, my g, deep x2", 2)):
    q = -102.0 + math.log2(g)
    a = ledger_g(32, q, dm)[0]; b, s = ledger_g(22, q, dm); c = ledger_g(22, q, dm, p6=False)[0]
    print("%-30s 32 words %.5f  -> 22 words %.5f (P6 cut GUESS)  %.5f (P6 unchanged)  success %.7f" % (lab, a, b, c, s))
