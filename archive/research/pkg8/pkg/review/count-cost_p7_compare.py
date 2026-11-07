#!/usr/bin/env python3
"""Reviewer (count and cost): the own 32-bit recount (count-cost_p7_own32.tsv, made by count-cost_p7_cnt.c)
against count/a15_outcomes.tsv, the fractions printed in proof.md and the outside model's CSV. Exact fractions."""
import csv
import pathlib
from fractions import Fraction as F

HERE = pathlib.Path(__file__).resolve().parent
PKG = HERE.parent
SOL = PKG.parent.parent / "astra-jobs" / "server_tasks_2026-10-06"
own = {}
for line in (HERE / "count-cost_p7_own32.tsv").read_text().splitlines():
    f = line.split("\t")
    own[(f[0], f[1], f[2])] = (int(f[3]), int(f[4]), int(f[5]), int(f[6]), int(f[7]), int(f[8]))
rows = list(csv.DictReader((PKG / "count" / "a15_outcomes.tsv").open(), delimiter="\t"))
print("outcomes in the package table %d, recounted %d" % (len(rows), len(own)))
dif = {"E1": 0, "N3": 0, "N3_S8": 0, "N3_old6": 0, "N3_p4": 0, "R": 0, "eta relation": 0}
D = 1 << 81
tot = {k: F(0) for k in ("all", "S8", "old6", "p4", "kept S8", "kept old6", "kept p4")}
split = {"S8": [0, 0, 0], "old6": [0, 0, 0], "p4": [0, 0, 0]}
beta = {}
for r in rows:
    key = (r["beta"], r["tau"], r["eps"])
    ok, n1, n3, s8, o6, p4 = own[key]
    dif["eta relation"] += ok != 1
    dif["E1"] += n1 != int(r["E1"])
    dif["N3"] += n3 != int(r["N3"])
    dif["N3_S8"] += s8 != int(r["N3_S8"])
    dif["N3_old6"] += o6 != int(r["N3_old6"])
    dif["N3_p4"] += p4 != int(r["N3_p4"])
    dif["R"] += F(n1 * n3, D) != F(r["R"])
    tot["all"] += F(n1 * n3, D)
    b = beta.setdefault(r["beta"], [0, F(0), F(0), F(0)])
    b[0] += 1; b[1] += F(n1 * n3, D); b[2] += F(n1 * s8, D)
    for name, x in (("S8", s8), ("old6", o6), ("p4", p4)):
        tot[name] += F(n1 * x, D)
        if x == n3:
            tot["kept " + name] += F(n1 * n3, D)
            split[name][0] += 1
            if name == "S8":
                b[3] += F(n1 * n3, D)
        elif x == 0:
            split[name][1] += 1
        else:
            split[name][2] += 1
print("different from the package table:", dif)
TEXT = {"all": F(194382080300609, 1048576), "S8": F(6219586146887739, 33554432), "kept S8": F(12147454997539, 65536),
        "old6": F(3109793308378027, 16777216), "kept old6": F(12147455783971, 65536),
        "p4": F(1554896901466299, 8388608), "kept p4": F(48589823135925, 262144)}
for k, v in tot.items():
    print("  %-9s own %s = %.4f; text/COUNT.md %s: %s" % (k, v, float(v), TEXT[k], "EQUAL" if v == TEXT[k] else "DIFFERENT"))
print("  outcomes all pass / none / split: S8 %s (text 99 / 76 / 142), old6 %s, p4 %s" % (split["S8"], split["old6"], split["p4"]))
# the outside model's file: kept pairs per number of conditions
for row in csv.DictReader((SOL / "gpt_sol_affine_M_A15.csv").open()):
    if row["codimension"] == "8":
        print("  outside model, 8 conditions: kept_pairs %s; own sum of N1*N3_S8 %d: %s; masks %s rhs %s" % (
            row["kept_pairs"], tot["S8"] * D, "EQUAL" if int(row["kept_pairs"]) == tot["S8"] * D else "DIFFERENT",
            row["h_masks"], row["rhs_bits"]))
# the table of proof.md Section 10 (beta, outcomes, part of r, with rule A, kept for H1)
PROOF = {"18b0e098": (7, 67698688, 67698688, 67698688), "18b1a098": (16, 51384320, 51384320, 51384320),
         "18d0e098": (12, 50790400, 50790400, 50790400), "18d1a098": (12, 13246464, 13246464, 13246464),
         "18b3e098": (4, 1474560, 1474560, 1474560), "18d3e098": (6, 755712, 755712, 755712),
         "18d16398": (6, 13328, 456, 0), "18f1e098": (8, 3465, 1665, 0)}
bad = sum(1 for b, want in PROOF.items() if (beta[b][0], beta[b][1], beta[b][2], beta[b][3]) != want)
rest = [sum(v[t] for b, v in beta.items() if b not in PROOF) for t in range(4)]
print("  proof table: 8 named betas different %d; betas %d; others: %d outcomes, %.4f, %.4f, %.4f (text 45 others: 246, 10,260.5523, 5,846.4676, 5,309.4537)"
      % (bad, len(beta), rest[0], float(rest[1]), float(rest[2]), float(rest[3])))
print("  margin: kept S8 / 49,400,000 = %.5f; exact r_A / 49,400,000 = %.5f; kept/3.75 = %.0f" % (
    float(tot["kept S8"]) / 49400000, float(tot["S8"]) / 49400000, float(tot["kept S8"]) / 3.75))
