#!/usr/bin/env python3
"""Reviewer check, lens MATHEMATICS AND COST, parts (d) and (e): the cost arithmetic and the probability bound,
recomputed with exact fractions and 60-digit decimals from the figures of proof.md 6.5, 7 and 8 (typed here).
Nothing of the package is imported.   python3 -B math_cost.py   -> review/math_cost.txt
"""
import sys
from decimal import Decimal, getcontext
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
getcontext().prec = 60
LN2 = Decimal(2).ln()


def log2(x):
    x = Decimal(x.numerator) / Decimal(x.denominator) if isinstance(x, Fraction) else Decimal(x)
    return x.ln() / LN2


out, bad = [], []


def say(name, value, claimed=None, ok=None):
    line = "%-58s %s" % (name, value)
    if claimed is not None:
        line += "   | text: %s   %s" % (claimed, "ok" if ok else "DIFFERS")
        if not ok:
            bad.append(name)
    out.append(line)


C = 430
A_OPS, A_LOADS, B_OPS, B_LOADS = 64, 36, 96, 42
members, lanes = 65536, 7
batches = -(-members // lanes)
say("batches per alpha", batches, "9,363", batches == 9363)
say("full batches, members in the last", divmod(members, lanes), "9,362 and 2", divmod(members, lanes) == (9362, 2))
stage_a, stage_2 = A_OPS + A_LOADS, B_OPS + B_LOADS
say("stage A, stage 2", (stage_a, stage_2), "100, 138", (stage_a, stage_2) == (100, 138))
budget_share = Fraction(1, 8)
alpha = batches * stage_a + batches * stage_2 * budget_share + 256
say("operations per alpha, budgeted", float(alpha), "1,098,067.75", alpha == Fraction("1098067.75"))
per_trial = alpha / members
say("per trial, budgeted", "%.6f" % per_trial, "< 16.756", per_trial < Fraction("16.756") and per_trial > Fraction("16.755"))
charge = Fraction("17.4")
say("charged per alpha", float(charge * members), "1,140,326.4", charge * members == Fraction("1140326.4"))
margin = charge * members / alpha - 1
say("margin of the charge over the budgeted cost", "%.4f%%" % (100 * margin), "3.8%", Fraction("0.038") <= margin < Fraction("0.039"))
expected = (batches * stage_a + batches * stage_2 * Fraction(7, 64) + 256) / members
say("per trial, expected with 7 * 2^-6 of the batches", "%.6f" % expected, "<= 16.448", Fraction("16.447") < expected <= Fraction("16.448"))
exact_enter = 1 - Fraction(63, 64) ** 7
say("  (independent lanes: 1 - (63/64)^7 of the batches)", "%.6f -> %.4f per trial" % (
    exact_enter, (batches * stage_a + batches * stage_2 * exact_enter + 256) / members))
T = 104
main = charge * 2 ** T
rest = 2 ** 98 + 2 ** 67 + 2 ** 60 + 2 ** 22 + 2 ** 11 + 1
say("log2 17.4, log2 430", "%.6f %.6f" % (log2(charge), log2(C)), "4.12102, 8.74819",
    abs(log2(charge) - Decimal("4.12102")) < Decimal("0.000005") and abs(log2(C) - Decimal("8.74819")) < Decimal("0.000005"))
say("log2 of 17.4 * 2^104 / 430", "%.6f" % log2(main / C), "99.37282", abs(log2(main / C) - Decimal("99.37282")) < Decimal("0.00001"))
say("log2 of the terms after the first", "%.6f" % log2(Fraction(rest)), "< 98.01", log2(Fraction(rest)) < Decimal("98.01"))
say("  they are below 17.4 * 2^104 * 2^-7 = 2^", "%.4f" % log2(main / 128), "101.121", rest < main / 128 and abs(log2(main / 128) - Decimal("101.121")) < Decimal("0.001"))
total = (main + rest) / C + 2 + 2 ** 63
say("log2 of the total as written (line 1 of the display)", "%.6f" % log2(total), "< 99.3841 < 99.39", log2(total) < Decimal("99.3841"))
upper = main * (1 + Fraction(1, 128)) / C + 2 ** 64
say("log2 of the second line of the display", "%.6f" % log2(upper), "< 2^99.3841 + 2^64", total < upper)
say("log2(1 + 2^-7)", "%.6f" % log2(1 + Fraction(1, 128)), "< 0.01123", log2(1 + Fraction(1, 128)) < Decimal("0.01123"))
tenths = int((log2(upper) * 10).to_integral_value(rounding="ROUND_CEILING"))   # Decimal's // truncates, so not used here
say("time_log2 rounded up to one decimal", "%.1f" % (tenths / 10), "99.4", tenths == 994)
say("  the same from the total as written (not the bound)", "%.1f" % (int((log2(total) * 10).to_integral_value(rounding="ROUND_CEILING")) / 10))
say("passes: 2^88 * 2^10 as a share of the main loop, log2", "%.4f" % log2(Fraction(2 ** 98) / main), "below 2^-10.12", log2(Fraction(2 ** 98) / main) < Decimal("-10.12"))
say("stage-2 budget as a share of the trials, log2", "%.4f" % log2(Fraction(batches * 2 ** 85, 2 ** T)), "2^-5.81",
    abs(log2(Fraction(batches * 2 ** 85, 2 ** T)) + Decimal("5.81")) < Decimal("0.005"))
say("budget over seven times 2^-6", "%.6f" % (budget_share / Fraction(7, 64)), "1.142", Fraction("1.142") <= budget_share / Fraction(7, 64) < Fraction("1.143"))
say("uniform rate: log2(17.4 * 2^127 / 430)", "%.5f" % log2(charge * 2 ** 127 / C), "122.37282 -> 122.4", abs(log2(charge * 2 ** 127 / C) - Decimal("122.37282")) < Decimal("0.00001"))
say("one stage, 34 per trial: log2(34 / 17.4)", "%.4f" % log2(Fraction(34) / charge), "0.96 / 0.97 bits", Decimal("0.96") <= log2(Fraction(34) / charge) < Decimal("0.97"))
# probability
e = (Decimal(-1) / 2).exp()
p = 1 - e - Decimal("0.002") - Decimal("0.0005") - Decimal("0.0005")
say("1 - exp(-1/2) - 0.002 - 0.0005 - 0.0005", "%.6f" % p, ">= 0.39 (0.3904)", p >= Decimal("0.39"))
fmin = -(Decimal(2) ** 24) * Decimal("0.607").ln()
say("smallest factor f with 1 - exp(-f / 2^24) - 0.003 >= 0.39", "%.2f" % fmin, "8,375,631", int(fmin.to_integral_value(rounding="ROUND_CEILING")) == 8375631)
full, used, factor = Fraction("29977922"), Fraction("29965882"), 2 ** 23
say("count used / 2^23, count of all / 2^23", "%.4f %.4f" % (used / factor, full / factor), "3.57, 3.57", int(used / factor * 100) == 357 == int(full / factor * 100))
say("expected good trials per run under M", "%.4f" % (used / 2 ** 24), "1.78", int(used / 2 ** 24 * 100) == 178)
say("cluster size that keeps 0.39", "%.4f" % (float(used) / float(fmin)), "3.57", int(float(used) / float(fmin) * 100) == 357)
say("count used / count of all", "%.6f" % (used / full), "0.999598", abs(used / full - Fraction("0.999598")) < Fraction("0.0000005"))
say("dropped share, percent (12,039.8 of the count)", "%.4f%%" % (100 * 12039.8 / float(full)), "0.041%", abs(100 * 12039.8 / float(full) - 0.041) < 0.0005)
say("count used / 2^22", "%.2f" % (used / 2 ** 22), "7.1", int(used / 2 ** 22 * 10) == 71)
# H2 / H3 figures
say("E1-test pass rate, 1,521 in 2^40: log2", "%.4f" % (log2(1521) - 40), "2^-29.42", abs(log2(1521) - 40 + Decimal("29.42")) < Decimal("0.01"))
runs = (4294916967, 4294925479, 4295022265, 4294920099)
mean = 2 ** 38 // 64
sd = (Decimal(2 ** 38) * Decimal(63) / Decimal(4096)).sqrt()
say("rule A: four runs, sum", sum(runs), "17,179,784,810", sum(runs) == 17179784810)
say("  deviations in binomial sd", " ".join("%+.2f" % ((r - mean) / sd) for r in runs), "-0.8 -0.6 +0.8 -0.7", True)
say("  largest relative deviation", "%.2e" % max(abs(r - mean) / mean for r in runs), "1.3e-05", max(abs(r - mean) / mean for r in runs) < 1.3e-5)
say("  share of all four, log2", "%.6f" % (log2(sum(runs)) - 40), "2^-6.0000", abs(log2(sum(runs)) - 40 + 6) < Decimal("0.00005"))
say("self-test: 261,798 of 16,800,000 lanes, log2", "%.4f" % (log2(261798) - log2(16800000)), "2^-6.004", abs(log2(261798) - log2(16800000) + Decimal("6.004")) < Decimal("0.0005"))
say("self-test: 205,330 of 2,400,000 batches", "%.4f" % (205330 / 2400000), "0.0856", abs(205330 / 2400000 - 0.0856) < 0.00005)
exp_share = Fraction(3, 4) * exact_enter + Fraction(1, 4) * (1 - Fraction(63, 64) ** 2)
say("  expected for that mix (3/4 full, 1/4 last batch)", "%.4f" % exp_share)
Path(__file__).with_name("math_cost.txt").write_text("\n".join(out) + "\n", encoding="ascii", newline="\n")
print("lines %d, differing from the text: %d %s" % (len(out), len(bad), bad))
