#!/usr/bin/env python3
"""Exact tables of a run of pair_calc_sub (class or cube, rules on h1) and the comparison with GPT Sol 6.1's files.
Research helper of research/pkg7/count, not submitted. Sol's files are read as data to compare with; no figure of
ours is taken from them.

    python3 -B sub_tab.py RUN.out NAME KIND RULENAME,RULENAME,...
KIND a15 | a17 : cube inside the class of pin H8 (gpt_sol_affine_M_A15/A17.csv, gpt_sol_baseline_M_*.txt,
                 gpt_sol_profiles_M_*.csv, gpt_sol_beta_M_A15.csv)
KIND full      : the class itself (gpt_sol_affine_K.csv, gpt_sol_outcomes_E.csv, totals of gpt_sol_answer_E.md)
Writes NAME_totals.txt, NAME_parts.tsv, NAME_outcomes.tsv, NAME_cmp.txt beside this script; prints a few lines.
Per rule:  pass = R of the solutions whose h1 satisfies the rule (exact kept mass);
           kept_whole = R of the outcomes (beta, tau, eps) that have NO violating solution (conservative count);
           tainted = R of the outcomes that have at least one violating solution (R - kept_whole).
A rule of ours and a rule of Sol are matched as affine subspaces (reduced row echelon form over GF(2) of the rows
mask | value), so that two different lists of conditions for the same set of h1 are recognised as the same rule.
"""
import csv
import os
import sys
from fractions import Fraction as F

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import rule_tab as RT

SOL = os.path.join(HERE, "..", "..", "..", "astra-jobs", "server_tasks_2026-10-06")


def canon(rows):
    """rows = [(mask, value)] -> canonical tuple of the affine subspace (reduced row echelon form over GF(2), pivot =
    highest bit of a row, the value in bit 0); None when the conditions contradict each other."""
    basis = []
    for m, b in rows:
        x = (m << 1) | b
        for p in basis:
            if (x >> (p.bit_length() - 1)) & 1:
                x ^= p
        if x == 1:
            return None
        if x == 0:
            continue
        top = x.bit_length() - 1
        basis = [p ^ x if (p >> top) & 1 else p for p in basis]
        basis.append(x)
    return tuple(sorted(basis, reverse=True))


def sol_affine(kind):
    """-> {canonical rule: (label, exact R kept)} from Sol's affine tables."""
    ref = {}
    if kind in ("a15", "a17"):
        tag = kind.upper()
        with open(os.path.join(SOL, "gpt_sol_affine_M_%s.csv" % tag), newline="") as f:
            for row in csv.DictReader(f):
                rows = [(int(m, 16), int(b)) for m, b in zip(row["h_masks"].split(";"), row["rhs_bits"].split(";"))]
                ref[canon(rows)] = ("M %s codim %s" % (tag, row["codimension"]), F(row["R_kept_exact"]))
        base = dict(ln.strip().split("=", 1) for ln in open(os.path.join(SOL, "gpt_sol_baseline_M_%s.txt" % tag)) if "=" in ln)
        old6 = [(0x10000, 0), (0x20000, 0), (1, 0), (2, 1), (0x404, 1), (0x808, 1)]
        ref[canon(old6)] = ("M %s old six (baseline)" % tag, F(base["R_baseline"]))
        return ref, F(base["R_total"])
    with open(os.path.join(SOL, "gpt_sol_affine_K.csv"), newline="") as f:
        for row in csv.DictReader(f):
            rows = [(int(m, 16), int(b)) for m, b in zip(row["h_masks"].split(";"), row["rhs_bits"].split(";"))]
            ref[canon(rows)] = ("K k = %s" % row["k"], F(int(row["best_found_pairs"]), 1 << 83))
    r5 = [(1, 0), (2, 1), (0x10000, 0), (0x20000, 0), (0xc, 1)]
    ref.setdefault(canon(r5), ("E rule 5", F(302248762304709, 2097152)))
    return ref, F(85074516985129, 524288)


def sol_outcomes(kind):
    name = {"a15": "gpt_sol_profiles_M_A15.csv", "a17": "gpt_sol_profiles_M_A17.csv", "full": "gpt_sol_outcomes_E.csv"}[kind]
    d = {}
    with open(os.path.join(SOL, name), newline="") as f:
        for row in csv.DictReader(f):
            d[(row["beta"].strip().lower(), row["t"].strip().lower(), row["s"].strip().lower())] = row
    return name, d


def main():
    path, name, kind, rnames = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4].split(",")
    info, outs = RT.load(path)
    n = info["nrules"]
    assert len(rnames) == n, "rule names"
    den, parts, tot = RT.tables(info, outs)
    rules = []
    for ln in info["rules"]:
        f = ln.split()
        rules.append([(int(x.split(":")[0], 16), int(x.split(":")[1])) for x in f[2:f.index("outside_eta")]])
    bet = info["betas"]
    ran = [d for d in bet.values() if d["state"] == "run"]

    # ---- totals ----
    lines = [info.get("pin", "")] + ["%s  (name %s)" % (ln, rnames[i]) for i, ln in enumerate(info["rules"])]
    lines.append("denominator 2^%d; betas in the list %d, searched %d, with a part %d; outcomes passing the necessary conditions %d, "
                 "listed (side-3 solutions in the cube) %d, with a nonzero product %d"
                 % (96 - info["fixed"], len(bet), len(ran), len(parts), sum(d.get("passing", 0) for d in ran), len(outs), tot["outcomes"]))
    lines.append("counted by n3r_orig %d, by n3r_proj alone %d (of them with a product %d), NOT counted %d, E1 not counted %d"
                 % (sum(o["fn"] == 0 and o["n3st"] == 0 for o in outs), sum(o["fn"] == 1 and o["n3st"] == 0 for o in outs),
                    sum(o["fn"] == 1 and o["n3st"] == 0 and o["e1"] > 0 and o["n3"] > 0 for o in outs),
                    sum(o["n3st"] != 0 for o in outs), sum(o["e1st"] != 0 for o in outs)))
    lines.append("checks inside the run: n3r_orig against n3r_proj on the same outcome: equal %d, different %d; the unchanged n3x "
                 "(where it does not sample) against the integer count: equal %d, different %d; n3x sampled on %d outcomes; "
                 "integer E1 against e1_exact: equal %d, different %d"
                 % (sum(o["both"] == 1 for o in outs), sum(o["both"] == 0 for o in outs), sum(d.get("xequal", 0) for d in ran),
                    sum(d.get("xdiff", 0) for d in ran), sum(d.get("xsampled", 0) for d in ran), sum(d.get("e1equal", 0) for d in ran),
                    sum(d.get("e1diff", 0) for d in ran)))
    lines.append("R (all solutions) = %s = %s" % (RT.fr(tot["R"], den), RT.dec(tot["R"], den, 9)))
    for r in range(n):
        lines.append("rule %-5s (%d conditions): pass %s = %s | kept_whole %s = %s | violate %s | tainted %s | outcomes with a product: all pass %d, none pass %d, split %d"
                     % (rnames[r], len(rules[r]), RT.fr(tot["pass"][r], den), RT.dec(tot["pass"][r], den, 9),
                        RT.fr(tot["R"] - tot["taint"][r], den), RT.dec(tot["R"] - tot["taint"][r], den, 9),
                        RT.dec(tot["R"] - tot["pass"][r], den, 6), RT.dec(tot["taint"][r], den, 6),
                        sum(1 for o in outs if o["e1"] and o["n3"] and o["p"][r] == o["n3"]),
                        sum(1 for o in outs if o["e1"] and o["n3"] and o["p"][r] == 0),
                        sum(1 for o in outs if o["e1"] and o["n3"] and 0 < o["p"][r] < o["n3"])))
    open(os.path.join(HERE, name + "_totals.txt"), "w", encoding="ascii", newline="\n").write("\n".join(lines) + "\n")

    with open(os.path.join(HERE, name + "_parts.tsv"), "w", encoding="ascii", newline="\n") as f:
        f.write("beta\toutcomes\tR\tR_decimal" + "".join("\tpass_%s\tkept_whole_%s" % (r, r) for r in rnames) + "\n")
        for beta, b in sorted(parts.items(), key=lambda kv: -kv[1]["R"]):
            f.write("%s\t%d\t%s\t%s" % (beta, b["outcomes"], RT.fr(b["R"], den), RT.dec(b["R"], den, 6).replace(",", "")))
            for r in range(n):
                f.write("\t%s\t%s" % (RT.fr(b["pass"][r], den), RT.fr(b["R"] - b["taint"][r], den)))
            f.write("\n")
    with open(os.path.join(HERE, name + "_outcomes.tsv"), "w", encoding="ascii", newline="\n") as f:
        f.write("beta\ttau\teps\tE1\tN3\t" + "\t".join("N3_" + r for r in rnames) + "\tR\tfunction\n")
        for o in sorted(outs, key=lambda o: (o["beta"], o["tau"], o["eps"])):
            if o["e1"] and o["n3"]:
                f.write("%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\n" % (o["beta"], o["tau"], o["eps"], o["e1"], o["n3"],
                        "\t".join(str(p) for p in o["p"]), RT.fr(o["e1"] * o["n3"], den), "orig" if o["fn"] == 0 else "proj"))

    # ---- comparison with Sol ----
    out = ["KIND %s: %s" % (kind, info.get("pin", ""))]
    bad = 0
    ref, rtot = sol_affine(kind)
    ours_R = F(tot["R"], den)
    same = ours_R == rtot
    bad += not same
    out.append("total R: ours %s = %s | Sol %s | %s" % (ours_R, RT.dec(ours_R.numerator, ours_R.denominator, 9), rtot,
                                                       "EQUAL" if same else "DIFFERENT by %s" % RT.dec((ours_R - rtot).numerator, (ours_R - rtot).denominator, 9)))
    matched = 0
    for r in range(n):
        key = canon(rules[r])
        mine = F(tot["pass"][r], den)
        if key in ref:
            label, val = ref[key]
            same = mine == val
            bad += not same
            matched += 1
            out.append("rule %-5s pass: ours %s = %s | Sol (%s) %s | %s"
                       % (rnames[r], mine, RT.dec(mine.numerator, mine.denominator, 9), label, val,
                          "EQUAL" if same else "DIFFERENT by %s" % RT.dec((mine - val).numerator, (mine - val).denominator, 9)))
        else:
            out.append("rule %-5s pass: ours %s = %s | Sol: no figure for this rule in this class" % (rnames[r], mine, RT.dec(mine.numerator, mine.denominator, 9)))
    out.append("rules with a figure of Sol: %d of %d; Sol rules of the table not run by us: %d" % (matched, n, len(ref) - len({canon(x) for x in rules} & set(ref))))
    if kind == "full":
        r5 = canon([(1, 0), (2, 1), (0x10000, 0), (0x20000, 0), (0xc, 1)])
        for r in range(n):
            if canon(rules[r]) == r5:
                kw = F(tot["R"] - tot["taint"][r], den)
                same = kw == F(64513843589, 512)
                bad += not same
                out.append("rule %-5s kept_whole: ours %s | Sol (answer E) 64513843589/512 | %s" % (rnames[r], kw, "EQUAL" if same else "DIFFERENT"))
    fname, sol = sol_outcomes(kind)
    ours = {(o["beta"], o["tau"], o["eps"]): o for o in outs if o["e1"] and o["n3"]}
    solpos = {k: v for k, v in sol.items() if int(v["matching_pairs"]) > 0}
    both = sorted(set(ours) & set(solpos))
    only_o, only_s = sorted(set(ours) - set(solpos)), sorted(set(solpos) - set(ours))
    diff, fields = [], 0
    for key in both:
        o, s = ours[key], solpos[key]
        for what, a, b in (("side-1 count", o["e1"], int(s["L"])), ("side-3 count", o["n3"], int(s["J"])),
                           ("pairs", o["e1"] * o["n3"], int(s["matching_pairs"]))):
            fields += 1
            if a != b:
                diff.append("beta %s tau %s eps %s %s: ours %d Sol %d" % (key + (what, a, b)))
    bad += len(diff) + len(only_o) + len(only_s)
    out.append("outcomes with a nonzero product (%s): ours %d, Sol %d (its file has %d rows, %d of them with zero pairs); in both %d; only ours %d; only Sol %d; "
               "integers compared %d, differing %d" % (fname, len(ours), len(solpos), len(sol), len(sol) - len(solpos), len(both), len(only_o), len(only_s), fields, len(diff)))
    out += ["   DIFFERENT " + d for d in diff[:10]]
    out += ["   ONLY OURS beta %s tau %s eps %s" % k for k in only_o[:10]] + ["   ONLY SOL beta %s tau %s eps %s" % k for k in only_s[:10]]
    # per beta: R from Sol's outcome file; for a15 also its own per-beta file
    solb = {}
    for (beta, _, _), v in solpos.items():
        solb[beta] = solb.get(beta, 0) + int(v["matching_pairs"])
    bd = [b for b in sorted(set(parts) | set(solb)) if parts.get(b, {"R": 0})["R"] != solb.get(b, 0)]
    bad += len(bd)
    out.append("betas with a part: ours %d, Sol (sum of its outcome rows) %d; R per beta differing %d" % (len(parts), len(solb), len(bd)))
    out += ["   DIFFERENT beta %s" % b for b in bd[:10]]
    if kind == "a15":
        rows = list(csv.DictReader(open(os.path.join(SOL, "gpt_sol_beta_M_A15.csv"), newline="")))
        d2 = [r["beta"] for r in rows if F(r["R_exact"]) != F(parts.get(r["beta"].strip().lower(), {"R": 0})["R"], den)]
        pos = sum(1 for r in rows if F(r["R_exact"]) > 0)
        bad += len(d2)
        out.append("gpt_sol_beta_M_A15.csv: %d betas, %d positive; R per beta differing from ours %d" % (len(rows), pos, len(d2)))
    notc = sum(o["n3st"] != 0 or o["e1st"] != 0 for o in outs)
    inner = sum(o["both"] == 0 for o in outs) + sum(d.get("xdiff", 0) for d in ran) + sum(d.get("e1diff", 0) for d in ran)
    out.append("outcomes of ours not counted: %d; differences inside our run (two functions, n3x, E1): %d" % (notc, inner))
    bad += notc + inner
    out.append("RESULT: %s" % ("everything equal" if not bad else "%d differences" % bad))
    open(os.path.join(HERE, name + "_cmp.txt"), "w", encoding="ascii", newline="\n").write("\n".join(out) + "\n")
    for ln in lines[-(n + 1):] + out[1:]:
        print(ln[:300])
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
