#!/usr/bin/env python3
"""Markdown tables for COUNT.md from the three runs (exact fractions and decimals). Research helper, not submitted.
    python3 -B mk_tables.py        writes COUNT_tables.md beside this script
"""
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rule_tab as RT

RUNS = [("a15", "cube k = 15, mask 07ef8303 value 030c0303, 131,072 members", ["F5", "old6", "S6", "S7", "S8", "S9", "p5", "p4"]),
        ("a17", "cube k = 17, mask 07ef831b value 030c031b, 32,768 members", ["F5", "old6", "S6", "S7", "S8", "S9", "p5", "p4"]),
        ("full", "full class, mask 03cf8303 value 030c0303, 524,288 members", ["F5", "old6", "K7", "K8", "S6", "S7", "S8", "p5"])]
SHOW = {"a15": ["old6", "S6", "S7", "S8"], "a17": ["old6", "S6", "S7", "S8"], "full": ["old6", "S6", "S7", "S8"]}


def d(q, n=6):
    return RT.dec(q.numerator, q.denominator, n)


def main():
    out = []
    for run, label, names in RUNS:
        path = os.path.join(HERE, run + ".out")
        if not os.path.exists(path):
            out.append("## %s: %s.out missing\n" % (label, run))
            continue
        info, outs = RT.load(path)
        den, parts, tot = RT.tables(info, outs)
        R = F(tot["R"], den)
        out.append("### %s (run `%s.out`, denominator 2^%d)\n" % (label, run, 96 - info["fixed"]))
        out.append("R = %s = %s; betas with a part %d; outcomes with a nonzero product %d.\n" % (R, d(R, 9), len(parts), tot["outcomes"]))
        out.append("| rule | conditions | exact passing mass | decimal | conservative (whole outcomes without a violating solution) | decimal | outcomes: all pass / none / split |")
        out.append("|---|---|---|---|---|---|---|")
        pos = [o for o in outs if o["e1"] and o["n3"]]
        for r, nm in enumerate(names):
            p = F(tot["pass"][r], den)
            k = F(tot["R"] - tot["taint"][r], den)
            nc = len(info["rules"][r].split()[2:info["rules"][r].split().index("outside_eta")])
            a = sum(1 for o in pos if o["p"][r] == o["n3"])
            z = sum(1 for o in pos if o["p"][r] == 0)
            out.append("| %s | %d | %s | %s | %s | %s | %d / %d / %d |" % (nm, nc, p, d(p, 9), k, d(k, 9), a, z, len(pos) - a - z))
        out.append("")
        show = SHOW[run]
        idx = [names.index(s) for s in show]
        out.append("Heaviest betas (R, then exact / conservative per rule; all betas in `%s_parts.tsv`):\n" % run)
        out.append("| beta | outcomes | R | " + " | ".join("%s exact | %s conservative" % (s, s) for s in show) + " |")
        out.append("|---|---|---|" + "---|---|" * len(show))
        for beta, b in sorted(parts.items(), key=lambda kv: -kv[1]["R"])[:8]:
            row = "| %s | %d | %s |" % (beta, b["outcomes"], d(F(b["R"], den), 4))
            for r in idx:
                row += " %s | %s |" % (d(F(b["pass"][r], den), 4), d(F(b["R"] - b["taint"][r], den), 4))
            out.append(row)
        rest = sorted(parts.items(), key=lambda kv: -kv[1]["R"])[8:]
        row = "| the other %d | %d | %s |" % (len(rest), sum(b["outcomes"] for _, b in rest), d(F(sum(b["R"] for _, b in rest), den), 4))
        for r in idx:
            row += " %s | %s |" % (d(F(sum(b["pass"][r] for _, b in rest), den), 4), d(F(sum(b["R"] - b["taint"][r] for _, b in rest), den), 4))
        out.append(row)
        out.append("")
    open(os.path.join(HERE, "COUNT_tables.md"), "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
    print("COUNT_tables.md written, %d lines" % len(out))


if __name__ == "__main__":
    main()
