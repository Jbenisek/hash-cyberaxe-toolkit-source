#!/usr/bin/env python3
"""judge7 (hostile-judge lens): the arithmetic of proof.md, claim.json and the note of the pkg7 draft, recomputed
from the printed inputs alone (no module of the package is imported). Prints one line per figure that does NOT
reproduce and a count of those that do. Output also to judge7_numbers.txt."""
import math
from fractions import Fraction as Fr
from pathlib import Path

HERE = Path(__file__).resolve().parent
bad, good = [], 0


def chk(name, got, printed, tol=0.0):
    global good
    if abs(float(got) - float(printed)) <= tol:
        good += 1
    else:
        bad.append(f"DIFF {name}: recomputed {float(got):.10g}, printed {printed}")


def up(x, d):
    return math.ceil(float(x) * 10 ** d - 1e-9) / 10 ** d


def dn(x, d):
    return math.floor(float(x) * 10 ** d + 1e-9) / 10 ** d


F, W, MEM = 49400000, 18725, 131072
nd = -(-(1 << 46) // F)
chk("values of C0.d1", nd, 1424469)
N = nd << 81
lN = math.log2(nd) + 81
chk("trials log2", round(lN, 3), 101.442)
chk("N log2 6 dec up", up(lN, 6), 101.441993)
chk("2^127/F log2", round(127 - math.log2(F), 3), 101.442)
chk("rate log2", round(128 - math.log2(F), 3), 102.442)
chk("F log2", round(math.log2(F), 3), 25.558)
chk("range ratio", dn(nd / 2 ** 19, 2), 2.71, 0.011)      # text: 2.72
chk("outer steps log2", round(lN - 49, 3), 52.442)
# counts
r = Fr(194382080300609, 1048576)
ra = Fr(6219586146887739, 33554432)
rc = Fr(12147454997539, 65536)
rcl = Fr(85074516985129, 524288)
chk("r", round(float(r), 2), 185377197.55)
chk("r_A", round(float(ra), 2), 185358111.47)
chk("kept", round(float(rc), 2), 185355453.45)
chk("class", round(float(rcl), 2), 162266763.66)
chk("class 4dec", round(float(rcl), 4), 162266763.6588)
chk("rule loss", round(float(r - ra), 2), 19086.08)
chk("kept diff", round(float(ra - rc), 2), 2658.01)
chk("gain", dn(r / rcl, 3), 1.142)
chk("margin", dn(rc / F, 2), 3.75)
chk("margin 2^25", dn(rc / 2 ** 25, 2), 5.52)
chk("r log2", dn(math.log2(float(r)), 2), 27.46)
chk("prob log2", dn(128 - math.log2(float(r)), 2), 100.53)
chk("loss one part in", float(r / (r - ra)), 10000, 400)
heavy = [67698688, 51384320, 50790400, 13246464]
chk("heaviest share %", round(100 * heavy[0] / float(r), 1), 36.5)
chk("four heaviest %", round(100 * sum(heavy) / float(r), 1), 98.8)
chk("others part", round(float(r) - sum(heavy) - 1474560 - 755712 - 13328 - 3465, 4), 10260.5523)
chk("others ruleA", round(float(ra) - sum(heavy) - 1474560 - 755712 - 456 - 1665, 4), 5846.4676)
chk("others kept", round(float(rc) - sum(heavy) - 1474560 - 755712, 4), 5309.4537)
chk("rule4-rule8 cost", round(185358154.948508620 - float(ra), 2), 43.48)
chk("expected good", dn(math.floor(rc) * N / 2 ** 128, 2), 1.87)
chk("cluster m", dn(math.floor(rc) * N / 2 ** 128 / -math.log(0.607), 2), 3.75)
chk("f_min", math.ceil(-math.log(0.607) * 2 ** 47 / nd), 49323560)
chk("success", 1 - math.exp(-0.5) - 0.003, 0.3904, 0.0001)
# cost
P = W * 47 + Fr(W * 135, 32) + 134 + 1 + Fr(W * 74 + 260 + 8, 2 ** 32) + Fr(16, 2 ** 64)
chk("stage A per X2", W * 47, 880075)
chk("stage 2 per X2", W * 135 / 32, 78996.09375)
chk("P", round(float(P), 4), 959206.0941)
chk("budgeted", up(P / MEM, 4), 7.3182)
chk("stage A per trial", round(W * 47 / MEM, 6), 6.714439)
chk("stage 2 per trial", round(W * 135 / 32 / MEM, 6), 0.602692)
chk("middle per trial", round(134 / MEM, 6), 0.001022)
chk("build per X2", round(W * 74 / 2 ** 32, 9), 0.000322622)
chk("charge", up(float(P / MEM) * 1.04, 1), 7.7)
chk("charged per X2", round(7.7 * MEM, 1), 1009254.4)
chk("charge margin %", dn((7.7 / float(P / MEM) - 1) * 100, 1), 5.2)
chk("charge room per batch", dn((7.7 - float(P / MEM)) * MEM / W, 1), 2.6)
chk("build per outer", W * 74, 1385650)
chk("build alone per trial", up(W * 74 / MEM, 2), 10.58)
indep = 1 - (1 - 2.0 ** -8) ** 7
chk("indep share", round(indep, 4), 0.0270)
chk("expected cost", up((W * 47 + W * 135 * indep + 135 + (W * 74 + 268) / 2 ** 32) / MEM, 4), 7.2367)
chk("H3 trial share", dn(W * 256 / (32 * MEM), 4), 1.1428)
main = lN + math.log2(7.7) - math.log2(430)
chk("main log2", up(main, 6), 95.638660, 2e-6)
chk("bound", up(main + math.log2(1 + 2 ** -7), 4), 95.6499)
chk("7.7N/128 log2", round(lN + math.log2(7.7) - 7, 3), 97.386, 0.0011)
side = 2 ** 94 + 2 ** 60 + 2 ** 24 + 2 ** 11 + 1 + 430 * (2 + 2 ** 63)
chk("side log2", up(math.log2(side), 2), 94.01)
chk("pass share", dn(lN + math.log2(7.7) - 94, 1), 10.3)
chk("uniform bound", up(127 + math.log2(7.7) - math.log2(430) + math.log2(1 + 2 ** -7), 3), 121.208)
chk("claim 2^25", up(102 + math.log2(7.7) - math.log2(430) + math.log2(1 + 2 ** -7), 1), 96.3)
chk("H2 rate", dn(lN - 84, 2), 17.44)
chk("H2 expected", up(lN - 31.41, 2), 70.04)
chk("H2 room", dn(84 - (lN - 31.41), 1), 13.9)
chk("gain total", round(97.52 - 95.65, 2), 1.87)
chk("gain rate", round(math.log2(F) - 25, 2), 0.56)
chk("gain cost", round(math.log2(19.1 / 7.7), 2), 1.31)


def claim(a, s2, share, middle=134):
    p = W * a + W * s2 / share + middle + 1 + (W * 74 + 268) / 2 ** 32
    c = up(p / MEM * 1.04, 1)
    return c, up(lN + math.log2(c) - math.log2(430) + 0.01123, 1), p / MEM


for name, args, pc, pcl in (("every read a load", (57, 143, 32, 146), 9.2, 96.0), ("address additions", (50, 139, 32), 8.1, 95.8),
                            ("rule 6", (41, 135, 8), 8.6, 95.9), ("rule 4", (37, 128, 2), 15.1, 96.7), ("rule 8", (47, 135, 32), 7.7, 95.7)):
    c, cl, b = claim(*args)
    chk(name + " charge", c, pc)
    chk(name + " claim", cl, pcl)
# memory
chk("mem words", 7 * W + 512, 131587)
chk("mem bytes", 32 * (7 * W + 512), 4210784)
# evidence arithmetic
chk("574 share", round(574 / 18725, 4), 0.0307)
chk("H3 room %", math.floor((1 / 32 / 0.026224 - 1) * 100), 19)
chk("470 z", round((470 - 467.6) / math.sqrt(467.6), 2), 0.11)
chk("56 z", round((56 - 74.8) / math.sqrt(74.8), 2), -2.17)
chk("345 z", round((345 - 335.76) / math.sqrt(335.76), 2), 0.50)
chk("138 z", round((138 - 152.0) / math.sqrt(152.0), 2), -1.14)


def pois(k, m):
    return math.exp(-m + k * math.log(m) - math.lgamma(k + 1))


chk("P(X<=3|14.65)", round(sum(pois(k, 14.65) for k in range(4)), 4), 0.0003)
chk("P(0 in 2 runs|0.25)", round(math.exp(-0.25), 3), 0.779, 1.0)  # placeholder, see text below
# Section 11
chk("item 2/12 share", dn(74899 / 65536, 4), 1.1428)
chk("item 12 5 dec", round(74899 / 65536, 5), 1.14287)
chk("item 5 cost", 74899 * 87 + 74899 * 163 / 4 + 1024, 9569371.25)
chk("item 5 charge", round(19.1 * 524288, 1), 10013900.8)
chk("item 8", round(86 - 70.61, 2), 15.39)
chk("item 9", round(45271 / 32768, 4), 1.3816)
chk("item 10", round(67065401 * 16 / 2 ** 30, 4), 0.9994)
m = 205.97
p_far = sum(pois(k, m) for k in range(0, 205)) + 1 - sum(pois(k, m) for k in range(0, 208))
p204 = pois(204, m)
p_le = sum(pois(k, m) for k in range(0, 2000) if pois(k, m) <= p204 * (1 + 1e-12))
chk("item 11 far", round(p_far, 3), 0.917)
chk("item 11 no more probable", round(p_le, 3), 0.944)
chk("item 13 ratio a", dn(91072901 / 2 ** 25, 2), 2.71)
chk("item 13 ratio b", dn(123244449 / 2 ** 25, 2), 3.67)
chk("item 14", round(9569371.25 / 524288, 4), 18.2521)
chk("item 7 total", round(float(rcl), 4), 162266763.6588)
out = [f"reproduced {good}, not reproduced {len(bad)}"] + bad
out.append(f"info: P(X<=204)+P(X>=208) at mean 205.97 = {p_far:.4f}; sum of P(k) <= P(204) = {p_le:.4f}; "
           f"P(X<=3 | 14.65) = {sum(pois(k, 14.65) for k in range(4)):.6f}; P(X<=2 | 13.0) = {sum(pois(k, 13.0) for k in range(3)):.6f}; "
           f"range ratio {nd / 2 ** 19:.4f}; 2 empty of 2 at 0.25 expected each?: exp(-0.25) = {math.exp(-0.25):.4f}, "
           f"exp(-0.125)^2 = {math.exp(-0.25):.4f}")
(HERE / "judge7_numbers.txt").write_text("\n".join(out) + "\n", encoding="ascii")
print("\n".join(x[:300] for x in out))
