#!/usr/bin/env python3
"""Reviewer (lens: count and cost) recomputation of the claim arithmetic of research/pkg7 (DRAFT).
Own code; reads nothing from the package tools. Every figure is typed from blake3-r2/proof.md Sections 6 to 9
and from COST.txt and recomputed with exact fractions or mpmath-free high precision (decimal / fractions)."""
import math
from fractions import Fraction as F
from decimal import Decimal, getcontext

getcontext().prec = 60
out = []


def log2(x):
    x = F(x)
    return float(Decimal(x.numerator).ln() / Decimal(2).ln() - Decimal(x.denominator).ln() / Decimal(2).ln())


def chk(name, got, want, tol=0.0, mode="eq"):
    if mode == "eq":
        ok = abs(got - want) <= tol
    elif mode == "le":      # stated figure must be an upper bound of the value
        ok = got <= want + 1e-15
    elif mode == "ge":      # stated figure must be a lower bound
        ok = got >= want - 1e-15
    out.append(("ok  " if ok else "BAD ") + f"{name}: computed {got!r}, text {want!r} ({mode})")
    return ok


FACTOR = 49400000
MEMBERS, W = 131072, 18725
vd = -(-(1 << 46) // FACTOR)
chk("values of C0.d1 = ceil(2^46/f)", vd, 1424469)
N = vd << 81
chk("N >= 2^127/f", int(N * FACTOR >= 1 << 127), 1)
chk("log2 N", log2(N), 101.441993, 5e-7)
chk("log2 N printed 101.442 (upper)", log2(N), 101.442, mode="le")
chk("log2 f", log2(FACTOR), 25.558, 5e-4)
chk("f*2^-128 = 2^-102.442", log2(F(FACTOR, 1 << 128)), -102.442, 5e-4)
chk("list words", -(-MEMBERS // 7), W)
chk("131072 = 18724*7+4", 18724 * 7 + 4, MEMBERS)
# P of Section 8
A, S2, MID, BUILD, OUTER = 47, 135, 134, 74, 260
P = F(W * A) + F(W * S2, 32) + MID + 1 + F(W * BUILD + OUTER + 8, 1 << 32) + F(16, 1 << 64)
chk("P", float(P), 959206.0941, 5e-5)
chk("P upper", float(P), 959206.0941, mode="le")
chk("stage A per X2", W * A, 880075)
chk("stage A per trial", W * A / MEMBERS, 6.714439, 5e-7)
chk("stage 2 per X2", W * S2 / 32, 78996.09375)
chk("stage 2 per trial", W * S2 / 32 / MEMBERS, 0.602692, 5e-7)
chk("middle per trial", MID / MEMBERS, 0.001022, 5e-7)
chk("build per X2", W * BUILD / 2 ** 32, 0.000322622, 5e-10)
chk("build per trial", W * BUILD / 2 ** 32 / MEMBERS, 2.461e-09, 5e-13)
chk("outer per X2", OUTER / 2 ** 32, 6.054e-08, 5e-12)
chk("outer per trial", OUTER / 2 ** 32 / MEMBERS, 4.619e-13, 5e-17)
chk("loop control per X2", 1 + 8 / 2 ** 32 + 16 / 2 ** 64, 1.000000002, 5e-10)
chk("loop control per trial", (1 + 8 / 2 ** 32) / MEMBERS, 7.629e-06, 5e-10)
bud = P / MEMBERS
chk("budgeted per trial", float(bud), 7.3182, 5e-5)
chk("budgeted < 7.319", float(bud), 7.319, mode="le")
chk("charged*members", 7.7 * MEMBERS, 1009254.4, 1e-6)
chk("charge over budget, percent", (7.7 / float(bud) - 1) * 100, 5.2, 0.05)
chk("margin per batch of 7", (7.7 - float(bud)) * 7, 2.6, 0.1)
chk("1.04*budgeted rounded up to .1", math.ceil(float(bud) * 1.04 * 10) / 10, 7.7)
share = 1 - (1 - 2.0 ** -8) ** 7
chk("independent share", share, 0.0270, 5e-5)
exp = (W * (A + share * S2) + MID + 1 + (W * BUILD + OUTER + 8) / 2 ** 32) / MEMBERS
chk("expected per trial (with loop control)", exp, 7.2367, 5e-5)
exp0 = (W * (A + share * S2) + MID + (W * BUILD + OUTER) / 2 ** 32) / MEMBERS
chk("expected per trial (COST.txt, no loop control)", exp0, 7.2367, 5e-5)
chk("build per trial if per X2", W * BUILD / MEMBERS, 10.58, mode="le")
# total
main = F(77, 10) * N
rest = (1 << 94) + (1 << 60) + (1 << 24) + (1 << 11) + 1
T = (main + rest) / 430 + 2 + (1 << 63)
chk("log2(7.7N/430)", log2(main / 430), 95.638660, 5e-7)
chk("log2 7.7 (text rounds up)", log2(F(77, 10)), 2.944859, mode="le")
chk("log2 430 (text rounds down)", log2(430), 8.748192, mode="ge")
chk("log2 rest+units*430 < 94.01", log2(rest + 430 * (2 + (1 << 63))), 94.01, mode="le")
chk("7.7N*2^-7 = 2^97.386", log2(main / 128), 97.386, 5e-4)
chk("log2(1+2^-7) < 0.01123", log2(F(129, 128)), 0.01123, mode="le")
chk("log2 T < 95.6499", log2(T), 95.6499, mode="le")
chk("log2 T < 95.65", log2(T), 95.65, mode="le")
chk("claim 95.7 = total rounded up to 0.1", math.ceil(log2(T) * 10) / 10, 95.7)
chk("selection 2^90 instead of 2^60 still < 95.65", log2((main + rest - (1 << 60) + (1 << 90)) / 430 + 2 + (1 << 63)), 95.65, mode="le")
chk("2^94 share of main loop < 2^-10.3", log2(F(1 << 94) / main), -10.3, mode="le")
chk("preprocessing 2^71 ops in units < 63", log2(F(1 << 71, 430)), 63, mode="le")
# formula of the task: 123.339 - log2 f + log2(charged/34) + 0.012
chk("formula time_log2", 123.339 - math.log2(FACTOR) + math.log2(7.7 / 34) + 0.012, 95.650, 1.5e-3)
# Section 7
x = F(FACTOR * vd, 1 << 47)
chk("f*N/2^128", float(x), 0.5, 1e-6)
p = 1 - math.exp(-float(x)) - 0.003
chk("success >= 0.3904", p, 0.3904, mode="ge")
fmin = math.ceil(-math.log(1 - 0.393) * 2 ** 47 / vd)
chk("least f for 0.39", fmin, 49323560, 1)
chk("margin 185,355,453/f", 185355453 / FACTOR, 3.75, 5e-3)
chk("margin exact", 185358111.47 / FACTOR, 3.7522, 5e-5)
chk("expected good trials 1.87", 185355453 * vd / 2 ** 47, 1.87, 0.01)
chk("121.208 constant", log2(F(77, 10) * (1 << 127) / 430) + 0.01123, 121.208, mode="le")
chk("at f=1 submit 121.3", math.ceil((log2(F(77, 10) * (1 << 127) / 430) + 0.01123) * 10) / 10, 121.3)
chk("at f=2^25 submit 96.3", math.ceil((log2(F(77, 10) * (1 << 102) / 430) + 0.01123) * 10) / 10, 96.3)
chk("count / 2^25", 185355453 / 2 ** 25, 5.52, 5e-3)
chk("H2 budget rate 2^-17.44", 84 - log2(N), -17.44, 5e-3)
chk("H2 passes 2^70.04", log2(N) - 31.41, 70.04, 1e-2)
chk("H3 share 1.1428*2^-8", W / 32 / MEMBERS * 256, 1.1428, 1e-4)
chk("H3 room 19 percent", (0.03125 / 0.02622 - 1) * 100, 19, 0.5)
chk("outer steps 2^52.442", log2(vd << 32), 52.442, 5e-4)
chk("range 2.72 times 2^19", vd / 2 ** 19, 2.72, 5e-3)
chk("trials per outer step 2^49", MEMBERS << 32, 1 << 49)
# other readings
def reading(a, s2, mid=134, share=1 / 32):
    b = (W * (a + s2 * share) + mid + 1 + (W * BUILD + OUTER + 8) / 2 ** 32) / MEMBERS
    c = math.ceil(b * 1.04 * 10 - 1e-9) / 10
    t = log2(F(str(c)) * N / 430) + 0.01123
    return b, c, t, math.ceil(t * 10 - 1e-9) / 10
for name, a, s2, mid, sh, wc, wt in (("every read a load", 57, 143, 146, 1 / 32, 9.2, 96.0),
                                      ("address additions", 50, 139, 134, 1 / 32, 8.1, 95.8),
                                      ("rule 6", 41, 135, 134, 1 / 8, 8.6, 95.9),
                                      ("rule 4", 37, 128, 134, 1 / 2, 15.1, 96.7)):
    b, c, t, r = reading(a, s2, mid, sh)
    chk(name + " charged", c, wc)
    chk(name + " scalar", r, wt)
    out.append(f"     {name}: budgeted {b:.4f}, charged {c}, bound {t:.4f}")
# memory
chk("data words", 7 * W + 512, 131587)
chk("data bytes", (7 * W + 512) * 32, 4210784)
chk("memory < 2^23", int(2 ** 19 + 4210784 < 2 ** 23), 1)
chk("lists 2^24", 2 * MEMBERS * 64, 1 << 24)
# counts quoted (fractions)
r = F(194382080300609, 1048576); ra = F(6219586146887739, 33554432); rk = F(12147454997539, 65536)
chk("r", float(r), 185377197.55, 5e-3)
chk("r_A", float(ra), 185358111.47, 5e-3)
chk("kept", float(rk), 185355453.45, 5e-3)
chk("loss r - r_A", float(r - ra), 19086.08, 5e-3)
chk("r_A - kept", float(ra - rk), 2658.01, 6e-3)
chk("r / r_class", float(r / F(85074516985129, 524288)), 1.142, 5e-4)
chk("log2 r", log2(r), 27.46, 5e-3)
chk("heaviest beta share", 67698688 / float(r) * 100, 36.5, 0.05)
chk("four heaviest share", (67698688 + 51384320 + 50790400 + 13246464) / float(r) * 100, 98.8, 0.05)
chk("beta table sum r", 67698688 + 51384320 + 50790400 + 13246464 + 1474560 + 755712 + 13328 + 3465 + 10260.5523, 185377197.5523, 1e-3)
chk("beta table sum r_A", 67698688 + 51384320 + 50790400 + 13246464 + 1474560 + 755712 + 456 + 1665 + 5846.4676, 185358111.4676, 1e-3)
chk("beta table sum kept", 67698688 + 51384320 + 50790400 + 13246464 + 1474560 + 755712 + 5309.4537, 185355453.4537, 1e-3)
chk("rule 4 to 8 loss 43.48", 185358154.948508620 - 185358111.467592090, 43.48, 5e-3)
bad = [l for l in out if l.startswith("BAD")]
print("\n".join(out))
print(f"checks {sum(1 for l in out if l[:3] in ('ok ', 'BAD'))}, BAD {len(bad)}")
