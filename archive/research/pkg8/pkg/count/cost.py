#!/usr/bin/env python3
"""time_log2 of every counted (class, rule) at margin 3.75. Research helper of research/pkg7/count, not submitted.

    python3 -B cost.py            writes COST_COUNT.txt beside this script and prints its ranking lines

Kept counts: our own runs (a15.out, a17.out, full.out, read with rule_tab.py), exact fractions.
Program counts: read from research/pkg7_program/COST.txt (two-level program, every read of a memory word a load) and
from research/pkg7_prep/opt/COST_OPT.txt (strict tier, 9 words kept in registers; confirmed by opt_verify/VERDICT.md).
Cost model, the one of research/pkg7_program/work/tools/cost.py:
    budget share of the batches that enter stage 2 = 2^-(n-3) for a rule of n conditions
    budgeted per trial = (stage A + share * stage 2) / 7 + middle step / members + table build and outer step (tiny)
    charged = budgeted * 1.04 rounded up to 0.1
    time_log2 = 123.339 - log2(f) + log2(charged / 34) + 0.012,   f = kept count / 3.75
STAGE A OF THE NEW RULES IS NOT COUNTED BY ANY MACHINE. Two columns:
    "as given"  the stage-A count of the program's own rule with the nearest number of conditions (rule 4, 5 or 6;
                rule 6 for 6 and more conditions): what "COST.txt scaled for the entry budget" means literally;
    "estimate"  the program's rule-4 count plus an increment per kind of condition, taken from what the program's
                rules 5 and 6 cost over rule 4 (COST.txt: rule 5 = +1 operation +1 load for a pair of adjacent bits
                by an addition; rule 6 = a further +3 operations +1 load for a pair of distant bits by shift, AND,
                XOR): adjacent pair +2, group of distant pairs with one shift distance +4, each further shift
                group of a three-bit parity +4. These increments are an ESTIMATE of this helper.
"""
import math
import os
import re
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rule_tab as RT

RES = os.path.join(HERE, "..", "..")
MARGIN = 3.75
# run -> (file, rule names in the order of the run, members of the class or cube, label)
RUNS = {
    "full": ("full.out", ["F5", "old6", "K7", "K8", "S6", "S7", "S8", "p5"], 524288, "class 03cf8303/030c0303 (2^19)"),
    "a15": ("a15.out", ["F5", "old6", "S6", "S7", "S8", "S9", "p5", "p4"], 131072, "cube 07ef8303/030c0303 (2^17)"),
    "a17": ("a17.out", ["F5", "old6", "S6", "S7", "S8", "S9", "p5", "p4"], 32768, "cube 07ef831b/030c031b (2^15)"),
}
# rule -> (conditions n, program rule whose stage A is taken "as given", estimated increment over rule 4, wording)
RULES = {
    "p4": (4, 4, 0, "h0=0, h1=1, h16=0, h17=0 (rule 4 of the program)"),
    "p5": (5, 5, 2, "p4 and h2^h3=1 (rule 5, the filed one)"),
    "F5": (5, 5, 6, "h0=0, h1=1, h16^h17=0, h2^h10=1, h3^h11=1"),
    "old6": (6, 6, 4, "p4 and h2^h10=1, h3^h11=1"),
    "K7": (7, 6, 6, "old6 and h10^h11=1 (same set as old6 and h2^h3=1)"),
    "K8": (8, 6, 14, "old6 and h2^h3=1, h24^h29^h30=1"),
    "S6": (6, 6, 14, "F5 and P: h3^h12^h24=0"),
    "S7": (7, 6, 18, "F5 and P and Q: h6^h13^h25=0"),
    "S8": (8, 6, 16, "old6 and P and Q"),
    "S9": (9, 6, 18, "S8 and h2^h3=1"),
}


def program_counts():
    """-> {tier: {"A": {4, 5, 6}, "S2": .., "mid": .., "table": 74, "outer": 260}} read from the two cost files."""
    t = open(os.path.join(RES, "pkg7_program", "COST.txt"), encoding="utf-8", errors="replace").read()
    a = {int(m.group(1)): (int(m.group(2)), int(m.group(3))) for m in
         re.finditer(r"rule (\d): batch stage A \d+ \+ \d+ = (\d+), stage 2 \d+ \+ \d+ = (\d+)", t)}
    mid = int(re.search(r"middle step\s+\d+ operations \+ \d+ loads \+\s*\d+ stores =\s*(\d+)", t).group(1))
    tab = int(re.search(r"table build\s+\d+ operations \+ \d+ loads \+\s*\d+ stores =\s*(\d+)", t).group(1))
    outer = int(re.search(r"outer step\s+\d+ operations \+ \d+ loads \+\s*\d+ stores =\s*(\d+)", t).group(1))
    assert set(a) == {4, 5, 6} and len({v[1] for v in a.values()}) == 1
    tiers = {"program": {"A": {n: a[n][0] for n in a}, "S2": a[4][1], "mid": mid, "table": tab, "outer": outer}}
    t2 = open(os.path.join(RES, "pkg7_prep", "opt", "COST_OPT.txt"), encoding="utf-8", errors="replace").read()
    b = {int(m.group(1)): (int(m.group(2)), int(m.group(3)), int(m.group(4))) for m in
         re.finditer(r"rule (\d), recoded, 9 words kept in registers \(strict/halfsearch.py as it is\): stage A \d+ \+ \d+ = (\d+), "
                     r"stage 2 \d+ \+ \d+ = (\d+);.*?middle step \d+ \+ \d+ \+ \d+ = (\d+)", t2)}
    assert set(b) == {4, 5, 6} and len({v[1] for v in b.values()}) == 1 and len({v[2] for v in b.values()}) == 1
    tiers["tightened"] = {"A": {n: b[n][0] for n in b}, "S2": b[4][1], "mid": b[4][2], "table": tab, "outer": outer}
    return tiers


def ceil_to(x, s):
    return math.ceil(x / s - 1e-9) * s


def charged(A, S2, n, members, tier):
    share = 2.0 ** -(n - 3)
    words = -(-members // 7)
    amort = tier["mid"] / members + tier["table"] * words / (2.0 ** 32 * members) + tier["outer"] / (2.0 ** 32 * members)
    budgeted = (A + share * S2) / 7.0 + amort
    return share, budgeted, ceil_to(budgeted * 1.04, 0.1)


def tl(kept, ch):
    return 123.339 - math.log2(float(kept) / MARGIN) + math.log2(ch / 34.0) + 0.012


def main():
    tiers = program_counts()
    out = ["COST_COUNT.txt: time_log2 at margin %.2f for every counted (class, rule). Research table, not a claim of a package." % MARGIN,
           "python3 -B cost.py (research/pkg7/count). Kept counts: our runs a15.out, a17.out, full.out. Stage A of the new rules is NOT counted; see the head of cost.py.",
           "program counts read: " + "; ".join("%s: stage A rule 4/5/6 = %d/%d/%d, stage 2 = %d, middle step %d" % (
               k, v["A"][4], v["A"][5], v["A"][6], v["S2"], v["mid"]) for k, v in tiers.items()),
           "tier 'program' = research/pkg7_program/COST.txt (every read of a memory word a load); tier 'tightened' = research/pkg7_prep/opt strict (9 words kept in registers, 16 registers)",
           ""]
    rows = []
    for run, (fname, names, members, label) in RUNS.items():
        path = os.path.join(HERE, fname)
        if not os.path.exists(path):
            out.append("run %s: %s is missing" % (run, fname))
            continue
        info, outs = RT.load(path)
        den, parts, tot = RT.tables(info, outs)
        assert info["nrules"] == len(names)
        for r, nm in enumerate(names):
            n, given_rule, inc, words = RULES[nm]
            exact = F(tot["pass"][r], den)
            cons = F(tot["R"] - tot["taint"][r], den)
            for tname, tier in tiers.items():
                for how in ("as given", "estimate"):
                    A = tier["A"][given_rule] if (how == "as given" or nm in ("p4", "p5")) else tier["A"][4] + inc   # p4, p5 are counted
                    share, bud, ch = charged(A, tier["S2"], n, members, tier)
                    rows.append((tl(exact, ch), run, label, nm, n, words, exact, cons, tname, how, A, share, bud, ch,
                                 tl(cons, ch) if cons > 0 else float("nan")))
    for tname in tiers:
        for how in ("as given", "estimate"):
            out.append("TIER %s, stage A %s%s" % (tname, how, "" if how == "as given" else " (ESTIMATE: rule-4 count + increment)"))
            out.append("  time_log2 (exact) | class or cube | rule (n) | kept exact | kept conservative | stage A, stage 2 | budget | budgeted | charged | log2 f (exact) | time_log2 with the conservative count")
            for row in sorted(r for r in rows if r[8] == tname and r[9] == how):
                t, run, label, nm, n, words, exact, cons, _, _, A, share, bud, ch, tc = row
                out.append("  %.3f | %s | %s (%d) | %s | %s | %d, %d | %.5f | %.4f | %.1f | %.4f | %.3f"
                           % (t, label, nm, n, RT.dec(exact.numerator, exact.denominator, 2), RT.dec(cons.numerator, cons.denominator, 2),
                              A, tiers[tname]["S2"], share, bud, ch, math.log2(float(exact) / MARGIN), tc))
            out.append("")
    out.append("RULES: " + "; ".join("%s = %s" % (k, v[3]) for k, v in RULES.items()))
    out.append("P = h3^h12^h24, Q = h6^h13^h25 (gpt_sol_answer_M.md). Increment over rule 4 in the column 'estimate': "
               + ", ".join("%s +%d" % (k, v[2]) for k, v in RULES.items()))
    ref = 123.339 - 25 + math.log2(19.1 / 34.0) + 0.012
    out.append("reference, the filed pkg6: kept 126,003,600 (conservative, rule p5, full class), f = 2^25, charged 19.1: time_log2 %.3f" % ref)
    open(os.path.join(HERE, "COST_COUNT.txt"), "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
    for tname in tiers:
        for how in ("as given", "estimate"):
            best = sorted(r for r in rows if r[8] == tname and r[9] == how)[:3]
            print("%s, stage A %s: " % (tname, how) + " | ".join("%s %s %.3f (charged %.1f, A %d)" % (b[1], b[3], b[0], b[13], b[10]) for b in best))


if __name__ == "__main__":
    main()
