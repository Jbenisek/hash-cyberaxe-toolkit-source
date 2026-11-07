#!/usr/bin/env python3
"""Reviewer, lens mathematics and cost: the figures of the count, recomputed from the files (package evidence and
my own runs), and compared with the numbers printed in proof.md Section 10.   python3 -B math_files.py
"""
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EV = PKG / "evidence"
M = 0xFFFFFFFF


def rol(v, n):
    return ((v << n) | (v >> (32 - n))) & M


def ror(v, n):
    return rol(v, 32 - n)


ETA = 0xE7C1815F
# 1. the list
rows = [l.split() for l in (EV / "pinB_e7c1815f.total").read_text(encoding="ascii").splitlines() if l.strip()]
calc2 = [l.split() for l in (EV / "calc2_total_e7c1815f.txt").read_text(encoding="ascii").splitlines() if l.strip()]
noeps = [r for r in rows if len(r) == 2]
ev = [r for r in rows if len(r) == 4]
parity_ok = all(bin(int(r[0], 16) ^ ror(ETA, 1)).count("1") & 1 == 1 for r in noeps) and all(
    bin(int(r[0], 16) ^ ror(ETA, 1)).count("1") & 1 == 0 for r in ev)
ks = [bin(rol(int(r[0], 16), 12) & 0x7FFFFFFF).count("1") for r in rows]
k_ok = all(int(r[1]) == k for r, k in zip(rows, ks))
parts = {r[0]: float(r[3]) for r in ev if float(r[3]) > 0}
print("list: betas %d, no eps %d, evaluated %d, with a part %d, sum %.1f; parity rule explains every beta without a result: %s; "
      "k as defined (weight of ROL(beta,12) below bit 31) in every line: %s, k from %d to %d" % (
          len(rows), len(noeps), len(ev), len(parts), sum(parts.values()), parity_ok, k_ok, min(ks), max(ks)))
c2 = {r[0]: r for r in calc2}
same = sum(1 for r in rows if r[0] in c2 and c2[r[0]][:len(r)] == r)
print("second whole-list count (calc2_total): lines %d, same beta, k, outcomes and part as the list file in %d; lines with a remark %d: %s" % (
    len(calc2), same, sum(1 for r in calc2 if len(r) > 4), " ".join(r[0] + ":" + r[4] for r in calc2 if len(r) > 4)))
# all betas with k <= 14: does the list hold all of them? beta = ROR(c1 XOR (c1 + DY11), 12); count the possible XOR differences
DY11 = 0x4285247F
# all x = c XOR (c + DY11) with weight below bit 31 at most 14: bit by bit, states (carry of c + DY11, x so far)
states = {(0, 0)}
for i in range(32):
    d = DY11 >> i & 1
    new = set()
    for carry, x in states:
        for cbit in (0, 1):
            s = cbit + d + carry
            x2 = x | ((s & 1) ^ cbit) << i
            if bin(x2 & 0x7FFFFFFF).count("1") <= 14:
                new.add((s >> 1, x2))
    states = new
seen = {x for _, x in states}
all_betas = {"%08x" % ror(x, 12) for x in seen}
print("betas with k <= 14 by my own enumeration of c1 XOR (c1 + DY11): %d; the list has %d; same set: %s; a uniform d1 has a beta of the "
      "list with probability %.4f (text 0.469)" % (len(all_betas), len(rows), all_betas == {r[0] for r in rows}, sum(2.0 ** -k for k in ks)))
# 2. my recount of the 39 betas
mine = {}
for l in (HERE / "math_calc2_mass.txt").read_text(encoding="ascii").splitlines():
    m = re.match(r"EXACT-E1 e7c1815f ([0-9a-f]{8}) .*class-rate part ([\d.]+) .*formula fallbacks (\d+)", l)
    if m:
        mine[m.group(1)] = float(m.group(2))
print("my run of the calculator: betas %d, same parts as the list file: %s, sum %.1f" % (
    len(mine), set(mine) == set(parts) and all(abs(mine[b] - parts[b]) < 0.06 for b in parts), sum(mine.values())))
# 3. the products and the dropped part
prod = {}
for l in (EV / "pairs_recount_e7c1815f.txt").read_text(encoding="ascii").splitlines():
    f = l.split()
    if f and f[0] == "OUTX":
        prod[(f[2], f[3], f[4])] = Fraction(int(f[6]) * int(f[8]), 2 ** 80)
viol = {}
for l in (HERE / "math_sat_violate_cadical.txt").read_text(encoding="ascii").splitlines():
    f = l.split()
    viol[(f[1], f[2], f[3])] = f[4]
by_beta = {}
for k, v in prod.items():
    by_beta[k[0]] = by_beta.get(k[0], 0) + v
print("products of %d outcomes add up to the part of their beta within 0.06 for all %d betas: %s" % (
    len(prod), len(by_beta), all(abs(float(by_beta[b]) - parts[b]) < 0.06 for b in parts)))
lost = sum(v for k, v in prod.items() if viol[k] == "SAT")
full = sum(prod.values())
drop_betas = sorted({k[0] for k in prod if viol[k] == "SAT"}, key=lambda b: -sum(v for k, v in prod.items() if k[0] == b and viol[k] == "SAT"))
print("with MY answers: dropped outcomes %d in %d betas carrying %.4f; all %.4f; kept %.4f; printed count 29,977,922 - 12,040 = %d <= kept: %s" % (
    sum(v == "SAT" for v in viol.values()), len(drop_betas), float(lost), float(full), float(full - lost), 29977922 - 12040,
    29977922 - 12040 <= full - lost))
table = {"f8342852": (8, 8448.0), "78346852": (4, 1296.0), "f87c2852": (6, 720.0), "78343852": (4, 648.0), "c81c39b3": (2, 384.0),
         "78345852": (2, 144.0), "787c5852": (1, 128.0), "787c6852": (1, 128.0), "787c3852": (1, 64.0), "58743852": (3, 27.6),
         "d81428d3": (2, 16.0), "d81428b3": (2, 14.0), "d8142873": (2, 12.0), "58fc3852": (2, 10.2)}
okt = set(table) == set(drop_betas) and all(
    sum(1 for k in prod if k[0] == b and viol[k] == "SAT") == n and abs(float(sum(v for k, v in prod.items() if k[0] == b and viol[k] == "SAT")) - p) <= 0.0501
    for b, (n, p) in table.items())                      # one decimal as printed; 10.25 is printed as 10.2
for b, (n, p) in table.items():
    n2 = sum(1 for k in prod if k[0] == b and viol[k] == "SAT")
    p2 = float(sum(v for k, v in prod.items() if k[0] == b and viol[k] == "SAT"))
    if n2 != n or abs(p2 - p) > 0.0501:
        print("   table row %s: text %d outcomes %.1f, mine %d outcomes %.4f (part of the beta %.4f)" % (b, n, p, n2, p2, float(by_beta[b])))
worst = max((k for k in prod if viol[k] == "SAT"), key=lambda k: prod[k])
print("the table of dropped parts in proof.md (typed here) is what my answers give: %s; largest dropped outcome %s %.1f" % (okt, worst, float(prod[worst])))
heavy = sorted(parts, key=lambda b: -parts[b])[:2]
print("heaviest beta %s %.0f%% of the count, two heaviest %.0f%%; four sampled betas %.0f" % (
    heavy[0], 100 * parts[heavy[0]] / sum(parts.values()), 100 * (parts[heavy[0]] + parts[heavy[1]]) / sum(parts.values()),
    sum(parts[b] for b in ("481c6852", "58146852", "481c5852", "58145852"))))
