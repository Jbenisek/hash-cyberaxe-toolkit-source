#!/usr/bin/env python3
"""Hostile-judge lens: figures of proof.md / claim.json of pkg5 recomputed from the evidence files (read-only).
Output: review/judge_numbers.out"""
import hashlib
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
PKG = Path(__file__).resolve().parent.parent
EV = PKG / "evidence"
M = 0xFFFFFFFF
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def rol(v, n):
    return ror(v, 32 - n)


def g(a, b, c, d, x, y):
    a1 = (a + b + x) & M; d1 = ror(d ^ a1, 16); c1 = (c + d1) & M; b1 = ror(b ^ c1, 12)
    a2 = (a1 + b1 + y) & M; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)


def rule_a(h):
    b = lambda i: h >> i & 1
    return b(16) == 1 and b(0) == b(1) and b(1) == b(2) and b(2) == b(3) and b(3) != b(4) and b(23) != b(24)


ETA = 0xE7C1815F
Y3, Y3B, Y11, Y11B, DELTA = 0x3F52EDA0, 0xC0AC125F, 0x5EBF5BC0, 0xA144803F, 0xFFFFFFFE
# Fact P from the six constants
X3, X7, X11, X15, W4, W13 = 0xD5D881CA, 0xAA277E35, 0x1F208000, 0x123F2142, 0x7FFFFFFF, 0xFFFD6E01
K = (0x3C6EF372 + 0x1F83D9AB) & M
W4B = ((((K + W4) & M) ^ 2) - K) & M
pa, pb = g(X3, X7, X11, X15, W4, W13), g(X3, X7, X11, X15, W4B, W13)
say("FactP", pa["a2"] == Y3, pb["a2"] == Y3B, pa["c2"] == Y11, pb["c2"] == Y11B, pa["b2"] == pb["b2"], pa["d2"] == pb["d2"],
    "delta", hex((W4 - W4B) & M))


def seven(sol, name):
    ea = g(sol["Y1"], sol["Y6"], Y11, sol["Y12"], sol["w12"], sol["w5"])
    eb = g(sol["Y1"], sol["Y6"], Y11B, sol["Y12"], sol["w12"], (sol["w5"] + DELTA) & M)
    fa = g(Y3, sol["Y4"], sol["Y9"], sol["Y14"], 0, sol["w8"])
    fb = g(Y3B, sol["Y4"], sol["Y9"], sol["Y14"], 0, sol["w8"])
    R = (ea["a2"] ^ fa["c2"] ^ eb["a2"] ^ fb["c2"], fa["a2"] ^ ea["c2"] ^ fb["a2"] ^ eb["c2"],
         fa["b2"] ^ ea["d2"] ^ fb["b2"] ^ eb["d2"], ea["b2"] ^ fa["d2"] ^ eb["b2"] ^ fb["d2"])
    e1 = (Y3 + sol["Y4"]) & M
    say(name, "R", ["%08x" % r for r in R], "h1 %08x" % fa["d1"], "ruleA", rule_a(fa["d1"]),
        "eta %08x" % (fa["d1"] ^ fb["d1"]), "class", (e1 & 0x015FE7C1) == 0x00036181,
        "beta %08x tau %08x eps %08x" % (ea["b1"] ^ eb["b1"], ea["a2"] ^ eb["a2"], ea["c2"] ^ eb["c2"]),
        "bits23,24", fa["d1"] >> 23 & 1, fa["d1"] >> 24 & 1)


seven(dict(Y1=0x052CE267, Y6=0xFAD31D99, Y12=0x69DA227B, w12=0, w5=0x57D7DFEF, Y4=0xC0D07BF1, Y9=0xFCDE77B6,
           Y14=0xA48CB1EE, w8=0x5141CE8C), "violating solution:")
seven(dict(Y1=0, Y6=0x7E1401E5, Y12=0x5A538AB4, w12=0, w5=0x234E3245, Y4=0x0AD073E5, Y9=0x61E4852D, Y14=0xDDCC82F4,
           w8=0xA2EE086C), "solution in class:")

# the count from the recount with both factors
outx, part_by_beta = {}, {}
for line in (EV / "pairs_recount_e7c1815f.txt").read_text().split("\n"):
    f = line.split()
    if f and f[0] == "OUTX":
        beta, tau, eps, n1, n3 = f[2], f[3], f[4], int(f[6]), int(f[8])
        outx[(beta, tau, eps)] = Fraction(n1 * n3, 2 ** 80)
    m = re.match(r"EXACT-E1 e7c1815f ([0-9a-f]{8}) .*class-rate part ([\d.]+)", line)
    if m:
        part_by_beta[m.group(1)] = float(m.group(2))
say("OUTX outcomes", len(outx), "betas", len({k[0] for k in outx}), "sum of N1*N3/2^80", float(sum(outx.values())),
    "sum of EXACT-E1 parts", sum(part_by_beta.values()))
worst = max(abs(float(sum(v for k, v in outx.items() if k[0] == b)) - p) for b, p in part_by_beta.items())
say("largest |sum of outcomes of a beta - printed part|", worst)

sat = {}
for line in (EV / "rule_a_sat_e7c1815f.txt").read_text().split("\n"):
    f = line.split()
    if f and f[0] in ("ALL", "VIOLATE"):
        sat[(f[0], f[1], f[2], f[3])] = f[4]
say("SAT lines: ALL", sum(k[0] == "ALL" for k in sat), "VIOLATE", sum(k[0] == "VIOLATE" for k in sat),
    "same keys as OUTX", {k[1:] for k in sat if k[0] == "VIOLATE"} == set(outx), {k[1:] for k in sat if k[0] == "ALL"} == set(outx))
viol = [k for k in outx if sat.get(("VIOLATE",) + k) == "SAT"]
unsat = [k for k in outx if sat.get(("VIOLATE",) + k) == "UNSAT"]
dropped = sum(outx[k] for k in viol)
total = sum(outx.values())
say("violate SAT", len(viol), "in betas", len({k[0] for k in viol}), "UNSAT", len(unsat), "dropped", float(dropped),
    "kept", float(total - dropped), "kept/total", float((total - dropped) / total), "dropped share %", 100 * float(dropped / total))
say("kept / 2^23", float((total - dropped) / 2 ** 23), "total / 2^23", float(total / 2 ** 23), "kept/8375631", float((total - dropped) / 8375631),
    "kept/2^24", float((total - dropped) / 2 ** 24))
big = max(viol, key=lambda k: outx[k])
say("largest dropped outcome", big, float(outx[big]))
heavy = [k for k in outx if k[0] == "481c6852"]
say("heaviest beta: outcomes", len(heavy), "all UNSAT", all(sat[("VIOLATE",) + k] == "UNSAT" for k in heavy), "sum", float(sum(outx[k] for k in heavy)))
top2 = sorted(part_by_beta.values(), reverse=True)[:2]
say("share heaviest", top2[0] / float(total), "top two", sum(top2) / float(total))
# share of the count that sits in betas none of whose outcomes is dropped
clean = {b for b in part_by_beta} - {k[0] for k in viol}
say("betas with no dropped outcome", len(clean), "their share", sum(part_by_beta[b] for b in clean) / float(total))
by_beta = {}
for k in viol:
    by_beta.setdefault(k[0], []).append(float(outx[k]))
say("dropped per beta", sorted(((b, len(v), round(sum(v), 1)) for b, v in by_beta.items()), key=lambda t: -t[2]))

# whole-list totals
for name in ("calc2_total_e7c1815f.txt", "pinB_e7c1815f.total"):
    rows = [l.split() for l in (EV / name).read_text().split("\n") if l.strip()]
    say(name, "betas", len(rows), "no eps", sum(len(r) == 2 for r in rows), "counted", sum(len(r) == 4 for r in rows),
        "with a part", sum(len(r) == 4 and float(r[3]) > 0 for r in rows), "sum", sum(float(r[3]) for r in rows if len(r) == 4),
        "k range", min(int(r[1]) for r in rows), max(int(r[1]) for r in rows))

# cost arithmetic
L, A, S2 = 9363, 100, 138
bud = Fraction(L * A) + Fraction(L * S2, 8) + 256
exp = Fraction(L * A) + Fraction(L * S2 * 7, 64) + 256
say("budgeted per alpha", float(bud), "per trial", float(bud / 65536), "expected per trial", float(exp / 65536),
    "margin %", 100 * (17.4 * 65536 / float(bud) - 1))
say("main exp", 104 + math.log2(17.4) - math.log2(430), "total exp",
    math.log2((17.4 * 2.0 ** 104 + 2.0 ** 98 + 2.0 ** 67 + 2.0 ** 60 + 2.0 ** 22 + 2.0 ** 11 + 1) / 430 + 2 + 2.0 ** 63))
say("stage-2 budget as share of trials: log2", math.log2(L) + 85 - 104, "budget / (2^-6 share)", L * 2.0 ** 85 / 2.0 ** 98,
    "0.125/0.109375", 0.125 / 0.109375)
say("success", 1 - math.exp(-0.5) - 0.003, "f_min", math.ceil(2.0 ** 24 * -math.log(0.607)))
say("E1 pass 1521/2^40 log2", math.log2(1521) - 40, "layout mean log2", math.log2(11812 / 8) - 40, "1390/2^40", math.log2(1390) - 40)
say("log2(34/17.4)", math.log2(34 / 17.4), "rule A share 4 runs log2", math.log2(17179784810) - 40,
    "max rel dev", max(abs(x / 2 ** 32 - 1) for x in (4294916967, 4294925479, 4295022265, 4294920099)),
    "sd units", [round((x - 2 ** 32) / math.sqrt(2 ** 38 / 64 * 63 / 64), 2) for x in (4294916967, 4294925479, 4295022265, 4294920099)])
say("selftest long: lanes", 131196 + 130602, "share log2", math.log2((131196 + 130602) / 16800000), "batches", 102933 + 102397,
    (102933 + 102397) / 2400000)
for name in ("blake3-r2/proof.md", "blake3-r2/claim.json", "blake3-r2/experiments/halfsearch.py", "submission-note-r2.md"):
    say("sha256", name, hashlib.sha256((PKG / name).read_bytes()).hexdigest())
(PKG / "review" / "judge_numbers.out").write_text("\n".join(out) + "\n", encoding="ascii")
print(len(out), "lines written")
