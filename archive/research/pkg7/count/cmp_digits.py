#!/usr/bin/env python3
"""The decimals that GPT Sol's answers K and M (and the task text) print, against ours rounded to the same number
of places (half up). The printed strings are copied here as data.   python3 -B cmp_digits.py"""
import os, sys
from fractions import Fraction as F
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rule_tab as RT
NAMES = {"a15": ["F5", "old6", "S6", "S7", "S8", "S9", "p5", "p4"], "a17": ["F5", "old6", "S6", "S7", "S8", "S9", "p5", "p4"],
         "full": ["F5", "old6", "K7", "K8", "S6", "S7", "S8", "p5"]}
PRINTED = [  # (run, rule or R, printed string, where)
    ("a15", "R", "185377197.55", "task text"), ("a15", "S8", "185358111.47", "task text"), ("a15", "S6", "185367007.60", "task text"),
    ("a15", "S7", "185366948.10", "task text"), ("full", "R", "162266763.66", "task text"), ("full", "old6", "162243592.98", "task text"),
    ("a15", "S6", "185367007.603330314", "M, kept R_6"), ("a15", "S7", "185366948.099803299", "M, kept R_7"), ("a15", "S8", "185358111.467592090", "M, kept R_8"),
    ("a17", "S6", "186151462.104162633", "M, kept R_6"), ("a17", "S7", "186151422.058318824", "M, kept R_7"), ("a17", "S8", "186142708.926058024", "M, kept R_8"),
    ("full", "R", "162266763.658769608", "K, R_total"), ("full", "F5", "162255060.247764766", "K, k = 5"), ("full", "old6", "162243592.984480470", "K, k = 6"),
    ("full", "K7", "144123440.887789249", "K, k = 7"), ("full", "K8", "125953518.490220308", "K, k = 8"),
]
vals = {}
for run, names in NAMES.items():
    info, outs = RT.load(os.path.join(HERE, run + ".out"))
    den, parts, tot = RT.tables(info, outs)
    vals[(run, "R")] = F(tot["R"], den)
    for r, nm in enumerate(names):
        vals[(run, nm)] = F(tot["pass"][r], den)
bad = 0
out = []
for run, nm, s, where in PRINTED:
    places = len(s.split(".")[1])
    mine = RT.dec(vals[(run, nm)].numerator, vals[(run, nm)].denominator, places).replace(",", "")
    ok = mine == s
    bad += not ok
    out.append("%-4s %-4s %-24s printed %s | ours %s | %s" % (run, nm, where, s, mine, "same to the last digit" if ok else "DIFFERENT"))
out.append("RESULT: %d printed decimals compared, %d different" % (len(PRINTED), bad))
open(os.path.join(HERE, "cmp_digits.txt"), "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
print(out[-1])
