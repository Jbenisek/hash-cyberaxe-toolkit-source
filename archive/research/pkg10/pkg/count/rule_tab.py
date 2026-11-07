#!/usr/bin/env python3
"""Exact tables from the output of pair_calc_rule (lines PIN, RULE, OUTR, BETA). Research helper, not submitted.

    python3 -B rule_tab.py RUN.out NAME RULENAME[,RULENAME...]
writes NAME_outcomes.tsv, NAME_parts.tsv, NAME_totals.txt beside this script and prints NAME_totals.txt.

Every figure is a sum of integer products E1 * N3 (or E1 * N3_rule) divided by 2^(96 - fixed bits of the class),
made with Python fractions: no rounding anywhere. Per rule:
    pass       R of the solutions whose h1 satisfies the rule
    violate    R of the others (pass + violate = R)
    tainted    whole R of the outcomes that have at least one violating solution
    kept_whole R - tainted (what is left when such outcomes are dropped completely)
"""
import os
import sys
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))


def load(path):
    """-> (info, outcomes); an outcome is a dict with exact integers."""
    info = {"rules": [], "betas": {}}
    outs = []
    for line in open(path, encoding="ascii", errors="replace"):
        f = line.split()
        if not f:
            continue
        if f[0] == "PIN":
            info["fixed"] = int(f[f.index("fixed_bits") + 1])
            info["nrules"] = int(f[f.index("rules") + 1])
            info["pin"] = line.strip()
            info["rules"] = []                 # a file joined from several slices repeats the head lines
        elif f[0] == "RULE":
            info["rules"].append(line.strip())
        elif f[0] == "OUTR":
            n = info["nrules"]
            i, j, k = f.index("P"), f.index("S"), f.index("X")
            z = f.index("Z")
            outs.append({"eta": f[1], "beta": f[2], "tau": f[3], "eps": f[4], "e1": int(f[6]), "n3": int(f[8]),
                         "p": [int(x) for x in f[i + 1:i + 1 + n]], "n3st": int(f[j + 1]), "e1st": int(f[j + 2]),
                         "fn": int(f[f.index("M") + 1]), "xn": float(f[k + 1]), "xs": int(f[k + 2]),
                         "both": int(f[f.index("B") + 1]), "sizes": f[z + 1:z + 6]})
        elif f[0] == "BETA":
            d = {"line": line.strip(), "k": int(f[3]) if len(f) > 3 and f[2] == "k" else -1}
            for name in ("passing", "notcounted", "proj", "e1fallback", "xsampled", "xequal", "xdiff", "bothequal",
                         "bothdiff", "e1equal", "e1diff"):
                if name in f:
                    d[name] = int(f[f.index(name) + 1])
            d["state"] = "infeasible" if "infeasible" in f else "noeps" if "noeps" in f else "run"
            info["betas"][f[1]] = d
    return info, outs


def tables(info, outs):
    """-> (den, per-outcome rows, per-beta dict, totals dict), all exact."""
    n = info["nrules"]
    den = 1 << (96 - info["fixed"])
    parts = {}
    for o in outs:
        if o["e1"] == 0 or o["n3"] == 0:
            continue
        b = parts.setdefault(o["beta"], {"outcomes": 0, "R": 0, "pass": [0] * n, "taint": [0] * n})
        b["outcomes"] += 1
        b["R"] += o["e1"] * o["n3"]
        for r in range(n):
            b["pass"][r] += o["e1"] * o["p"][r]
            if o["n3"] - o["p"][r] > 0:
                b["taint"][r] += o["e1"] * o["n3"]
    tot = {"outcomes": sum(b["outcomes"] for b in parts.values()), "R": sum(b["R"] for b in parts.values()),
           "pass": [sum(b["pass"][r] for b in parts.values()) for r in range(n)],
           "taint": [sum(b["taint"][r] for b in parts.values()) for r in range(n)]}
    return den, parts, tot


def fr(num, den):
    q = Fraction(num, den)
    return str(q.numerator) if q.denominator == 1 else "%d/%d" % (q.numerator, q.denominator)


def dec(num, den, digits=6):
    q = Fraction(num, den)
    s = "-" if q < 0 else ""
    q = abs(q)
    scaled = (q.numerator * 10 ** digits * 2 + q.denominator) // (2 * q.denominator)      # rounded half up
    return "%s%s.%0*d" % (s, format(scaled // 10 ** digits, ","), digits, scaled % 10 ** digits)


def main():
    path, name, rnames = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
    info, outs = load(path)
    n = info["nrules"]
    assert len(rnames) == n, "rule names"
    den, parts, tot = tables(info, outs)
    with open(os.path.join(HERE, name + "_outcomes.tsv"), "w", encoding="ascii", newline="\n") as f:
        f.write("beta\ttau\teps\tE1\tN3\t" + "\t".join("N3_" + r for r in rnames) + "\tR\tfunction\told_n3x_sampled\n")
        for o in sorted(outs, key=lambda o: (o["beta"], o["tau"], o["eps"])):
            if o["e1"] and o["n3"]:
                f.write("%s\t%s\t%s\t%d\t%d\t%s\t%s\t%s\t%d\n" % (o["beta"], o["tau"], o["eps"], o["e1"], o["n3"],
                        "\t".join(str(p) for p in o["p"]), fr(o["e1"] * o["n3"], den), "orig" if o["fn"] == 0 else "proj", o["xs"]))
    with open(os.path.join(HERE, name + "_parts.tsv"), "w", encoding="ascii", newline="\n") as f:
        f.write("beta\toutcomes\tR" + "".join("\tpass_%s\tviolate_%s\ttainted_%s\tkept_whole_%s" % (r, r, r, r) for r in rnames) + "\n")
        for beta, b in sorted(parts.items(), key=lambda kv: -kv[1]["R"]):
            f.write("%s\t%d\t%s" % (beta, b["outcomes"], fr(b["R"], den)))
            for r in range(n):
                f.write("\t%s\t%s\t%s\t%s" % (fr(b["pass"][r], den), fr(b["R"] - b["pass"][r], den), fr(b["taint"][r], den),
                                              fr(b["R"] - b["taint"][r], den)))
            f.write("\n")
    bet = info["betas"]
    ran = [d for d in bet.values() if d["state"] == "run"]
    lines = [info.get("pin", ""), *info["rules"],
             "betas in the list %d: impossible for D11 %d, no eps %d, searched %d; with a part %d; outcomes with a nonzero product %d"
             % (len(bet), sum(d["state"] == "infeasible" for d in bet.values()), sum(d["state"] == "noeps" for d in bet.values()),
                len(ran), len(parts), tot["outcomes"]),
             "outcomes passing the necessary conditions %d; listed (side-3 solutions) %d; counted by n3r_orig %d, by n3r_proj %d; NOT counted %d; E1 not counted %d"
             % (sum(d.get("passing", 0) for d in ran), len(outs), sum(o["fn"] == 0 and o["n3st"] == 0 for o in outs),
                sum(o["fn"] == 1 and o["n3st"] == 0 for o in outs), sum(o["n3st"] != 0 for o in outs), sum(o["e1st"] != 0 for o in outs)),
             "checks inside the run: n3r_orig against n3r_proj on the same outcome: equal %d, different %d; old n3x (no sampling) against the integer count: equal %d, different %d; "
             "old n3x sampled: %d outcomes; integer E1 against e1_exact: equal %d, different %d"
             % (sum(o["both"] == 1 for o in outs), sum(o["both"] == 0 for o in outs), sum(d.get("xequal", 0) for d in ran),
                sum(d.get("xdiff", 0) for d in ran), sum(d.get("xsampled", 0) for d in ran), sum(d.get("e1equal", 0) for d in ran),
                sum(d.get("e1diff", 0) for d in ran)),
             "R (all solutions) = %s = %s" % (fr(tot["R"], den), dec(tot["R"], den, 10))]
    for r in range(n):
        lines.append("rule %s: pass %s = %s | violate %s = %s | tainted %s = %s | kept_whole %s = %s"
                     % (rnames[r], fr(tot["pass"][r], den), dec(tot["pass"][r], den), fr(tot["R"] - tot["pass"][r], den),
                        dec(tot["R"] - tot["pass"][r], den), fr(tot["taint"][r], den), dec(tot["taint"][r], den),
                        fr(tot["R"] - tot["taint"][r], den), dec(tot["R"] - tot["taint"][r], den)))
    # the outcomes that the old count estimated (random-subset branch of n3x)
    est = [o for o in outs if o["xs"] > 0 and o["e1"] and o["n3"] and o["n3st"] == 0]
    if est or any(o["xs"] > 0 for o in outs):
        exact = sum(o["e1"] * o["n3"] for o in est)
        old = sum(Fraction(o["e1"]) * Fraction(o["xn"]) for o in outs if o["xs"] > 0)
        zero_old = sum(1 for o in est if o["xn"] == 0.0)
        lines.append("outcomes that the unchanged n3x estimates (random-subset branch): %d listed, %d with a nonzero product in %d betas; their exact R %s = %s; "
                     "with the estimate of n3x %s; outcomes among them that n3x put at zero %d"
                     % (sum(o["xs"] > 0 for o in outs), len(est), len({o["beta"] for o in est}), fr(exact, den), dec(exact, den, 10),
                        dec(old.numerator, old.denominator * den, 10), zero_old))
    text = "\n".join(lines) + "\n"
    open(os.path.join(HERE, name + "_totals.txt"), "w", encoding="ascii", newline="\n").write(text)
    for ln in lines:
        print(ln[:420])


if __name__ == "__main__":
    main()
