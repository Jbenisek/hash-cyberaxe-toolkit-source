#!/usr/bin/env python3
"""The outcomes of the count of class 830303cf (pin H8), assembled for the package. Research helper, not submitted.

    python -B tools/outcomes_h8.py

Reads (and copies nothing out of place: the sources stay in research/h8/counts, their SHA-256 is written down):
  research/h8/counts/H8_allb_positive.txt   every beta with a part that the batch count finished (PAIR, EXACT-E1, OUTS, OUTX)
  research/h8/counts/H8_satc.txt            the betas that the solver found satisfiable and the batch count had not reached
  research/h8/counts/H8_recount_k14.txt     the own count of all betas with k <= 14 (compared outcome by outcome)
  research/h8/counts/H8_count.txt           the table of the count (its totals are compared)
  evidence/gpt_recount/gpt_sol_parts_A.csv  the parts of the independent recount (GPT Sol 6.1, own program), as written by
                                            the program rebuilt and rerun here; as_received_parts_A.csv is the file as received
Writes:
  evidence/pairs_recount_830303cf.txt       one block per beta with a part: its PAIR, EXACT-E1 and OUTS lines and one line
                                            OUTX per outcome with a nonzero product (tau, eps, E1, N3), heaviest beta first
  evidence/count_h8.txt                     the count beta by beta, in exact fractions of the printed factors, which betas
                                            hold estimates, and the comparison with the independent recount
Exit status 0 only if every comparison holds.
"""
import hashlib
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
COUNTS = PKG.parent / "h8" / "counts"
EVID = PKG / "evidence"
ETA = "830303cf"
SCALE = 2 ** 83                     # part = E1 * N3 / 2^83 (H8_count.txt, head)
SOURCES = ("H8_allb_positive.txt", "H8_satc.txt")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def k_of(beta):
    v = int(beta, 16)
    return bin(((v << 12) | (v >> 20)) & 0x7FFFFFFF).count("1")


def blocks(path):
    """{beta: dict(pair, exact, outs, outx=[(tau, eps, E1, N3)], sampled, fallbacks)} of one calculator output."""
    out = {}
    for line in path.read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) < 3 or f[1] != ETA:
            continue
        b = out.setdefault(f[2], dict(pair=None, exact=None, outs=None, outx=[], sampled=0, fallbacks=0))
        if f[0] == "PAIR":
            b["pair"], b["sampled"] = line, (int(f[f.index("sampled") + 1]) if "sampled" in f else 0)
        elif f[0] == "EXACT-E1":
            b["exact"], b["fallbacks"] = line, int(f[-1])
        elif f[0] == "OUTS":
            b["outs"] = line
        elif f[0] == "OUTX":
            b["outx"].append((f[3], f[4], int(f[6]), int(f[8])))
    return out


def decimal(v, digits=4):
    return f"{float(v):,.{digits}f}"


def main():
    problems = []
    found = {}
    for name in SOURCES:
        for beta, b in blocks(COUNTS / name).items():
            if not b["outx"]:
                continue
            if beta in found:
                problems.append(f"beta {beta} has outcomes in two source files")
            found[beta] = dict(b, source=name)
    part = {beta: sum(Fraction(e * n, SCALE) for _, _, e, n in b["outx"]) for beta, b in found.items()}
    order = sorted(found, key=lambda beta: (-part[beta], beta))
    total = sum(part.values())
    outcomes = sum(len(b["outx"]) for b in found.values())
    flagged = [beta for beta in order if found[beta]["sampled"] or found[beta]["fallbacks"]]
    exact_betas = [beta for beta in order if beta not in flagged]
    exact_total = sum(part[b] for b in exact_betas)

    # the own count of the betas with k <= 14, outcome by outcome
    k14 = {beta: b for beta, b in blocks(COUNTS / "H8_recount_k14.txt").items() if b["outx"]}
    same14 = sum(sorted(found[b]["outx"]) == sorted(k14[b]["outx"]) for b in k14 if b in found)
    if set(k14) - set(found) or same14 != len(k14):
        problems.append("the outcomes of the betas with k <= 14 are not those of H8_recount_k14.txt")
    light = [b for b in order if k_of(b) <= 14]
    if set(light) != set(k14):
        problems.append("the betas with a part and k <= 14 are not those of H8_recount_k14.txt")

    # the table of the count
    table = (COUNTS / "H8_count.txt").read_text(encoding="ascii")
    m = re.search(r"all betas finished by the calculator: with a part (\d+), sum ([\d,.]+); of it from k >= 15: ([\d,.]+)", table)
    m2 = re.search(r"\((\d+) betas with a part, (\d+) outcomes with a nonzero product\)", table)
    m3 = re.search(r"sampled outcomes (\d+), formula fallbacks (\d+)\), lightest k (\d+); their parts \(estimates\) add up to ([\d.]+)", table)
    if not (m and m2 and m3):
        problems.append("H8_count.txt does not have the lines that are compared")
    else:
        t_betas, t_sum, t_heavy = int(m.group(1)), float(m.group(2).replace(",", "")), float(m.group(3).replace(",", ""))
        if (t_betas, int(m2.group(1)), int(m2.group(2))) != (len(found), len(found), outcomes) or abs(t_sum - float(total)) > 5e-4:
            problems.append("betas, outcomes or sum differ from H8_count.txt")
        if abs(float(sum(part[b] for b in order if k_of(b) >= 15)) - t_heavy) > 5e-4:
            problems.append("the part of the betas with k >= 15 differs from H8_count.txt")
        if abs(float(sum(part[b] for b in flagged)) - float(m3.group(4))) > 5e-6 or int(m3.group(2)) != 0:
            problems.append("the estimated parts differ from H8_count.txt")

    # the independent recount, beta by beta
    lines_gpt = []
    rerun, received = EVID / "gpt_recount" / "gpt_sol_parts_A.csv", EVID / "gpt_recount" / "as_received_parts_A.csv"
    gpt, gpt_outcomes = {}, {}
    if rerun.exists():
        for row in rerun.read_text(encoding="ascii").strip().split("\n")[1:]:
            f = row.split(",")
            gpt[f[0]] = gpt.get(f[0], 0) + Fraction(int(f[7]), int(f[8]))
            gpt_outcomes[f[0]] = gpt_outcomes.get(f[0], 0) + int(f[5])
        same_file = received.exists() and received.read_bytes().replace(b"\r\n", b"\n") == rerun.read_bytes().replace(b"\r\n", b"\n")
        g_total = sum(gpt.values())
        equal = [b for b in exact_betas if b in gpt and abs(gpt[b] - part[b]) <= Fraction(1, 10 ** 9) * max(part[b], 1)]
        identical = [b for b in exact_betas if gpt.get(b) == part[b]]
        differ = [b for b in exact_betas if b not in equal]
        same_outcomes = [b for b in exact_betas if gpt_outcomes.get(b) == len(found[b]["outx"])]
        lines_gpt = [
            f"INDEPENDENT RECOUNT (GPT Sol 6.1, OpenAI; its own program gpt_sol_independent_a.rs, sha256 "
            f"{sha(EVID / 'gpt_recount' / 'gpt_sol_independent_a.rs')[:16]}, rebuilt here with rustc -O and rerun with the argument all32):",
            f"  the parts file of the rerun {'equals' if same_file else 'DIFFERS FROM'} the file as received; betas with a part "
            f"{len(gpt)}; total {g_total.numerator} / {g_total.denominator} = {decimal(g_total, 10)}",
            f"  same set of betas with a part as the count: {set(gpt) == set(found)}; total minus the count {float(g_total - total):+.6f}",
            f"  the {len(exact_betas)} betas that the count has in full: part equal to within 10^-9 of its value in {len(equal)}, "
            f"identical as a fraction of the printed factors in {len(identical)}, different {len(differ)} {' '.join(differ)}; "
            f"same number of outcomes with a nonzero product in {len(same_outcomes)}",
            f"  sum over these {len(exact_betas)} betas: count {decimal(exact_total, 6)}, recount {decimal(sum(gpt.get(b, 0) for b in exact_betas), 6)}",
            f"  the {len(flagged)} betas in which the count holds estimates: count {decimal(sum(part[b] for b in flagged), 6)}, "
            f"recount {decimal(sum(gpt.get(b, 0) for b in flagged), 6)}; outcomes with a nonzero product: count "
            f"{sum(len(found[b]['outx']) for b in flagged)}, recount {sum(gpt_outcomes.get(b, 0) for b in flagged)}",
        ]
        if set(gpt) != set(found) or differ or not same_file:
            problems.append("the independent recount does not agree beta by beta, or its rerun differs from the file received")
    else:
        lines_gpt = ["INDEPENDENT RECOUNT: evidence/gpt_recount/gpt_sol_parts_A.csv is not there (the rerun has not ended); not compared"]
        problems.append("the rerun of the independent recount is missing")

    head = [f"# tools/outcomes_h8.py: class eta {ETA}, pin H8; every beta with a part and every outcome (tau, eps) with a nonzero "
            f"product, from the calculator outputs in research/h8/counts",
            f"# sources: " + "; ".join(f"{name} sha256 {sha(COUNTS / name)[:16]}" for name in SOURCES + ("H8_recount_k14.txt",)),
            f"# OUTX eta beta tau eps E1 <triples (c1, b1, a2)> N3 <quadruples (Y4, h1, Y9, w8)>; what an outcome adds is E1 * N3 / 2^83",
            f"# betas {len(found)}, outcomes {outcomes}; a beta whose PAIR line has sampled > 0 holds estimates of N3 "
            f"({len(flagged)} betas)"]
    body = []
    for beta in order:
        b = found[beta]
        body += [b["pair"], b["exact"], b["outs"]] + [f"OUTX {ETA} {beta} {tau} {eps} E1 {e} N3 {n}" for tau, eps, e, n in b["outx"]]
    (EVID / f"pairs_recount_{ETA}.txt").write_text("\n".join(head + body) + "\n", encoding="ascii", newline="\n")

    report = [
        f"COUNT OF CLASS {ETA} (pin H8), from the outcomes with their two factors (tools/outcomes_h8.py); unit 2^-128 per trial",
        f"sources: " + "; ".join(f"research/h8/counts/{name} sha256 {sha(COUNTS / name)[:16]}" for name in SOURCES),
        f"betas with a part {len(found)}; outcomes with a nonzero product {outcomes}; sum {total.numerator} / {total.denominator} "
        f"= {decimal(total, 6)}",
        f"betas with k <= 14: {len(light)}, outcomes {sum(len(found[b]['outx']) for b in light)}, sum "
        f"{decimal(sum(part[b] for b in light), 6)}; the same outcomes with the same factors as H8_recount_k14.txt in {same14} of {len(k14)} betas",
        f"betas with k >= 15: {len(order) - len(light)}, sum {decimal(sum(part[b] for b in order if k_of(b) >= 15), 6)}",
        f"betas in which an outcome went through the random-subset branch of the E3 count (estimates): {len(flagged)}, outcomes "
        f"with a nonzero product {sum(len(found[b]['outx']) for b in flagged)}, sum {decimal(sum(part[b] for b in flagged), 6)}; "
        f"E1 formula fallbacks {sum(found[b]['fallbacks'] for b in order)}",
        f"betas counted in full: {len(exact_betas)}, outcomes {sum(len(found[b]['outx']) for b in exact_betas)}, sum "
        f"{exact_total.numerator} / {exact_total.denominator} = {decimal(exact_total, 6)}",
    ] + lines_gpt + ["beta | k | outcomes | part | estimates (sampled outcomes of the beta) | part in the independent recount | source"]
    for beta in order:
        b = found[beta]
        report.append(f"BETA {beta} | {k_of(beta)} | {len(b['outx'])} | {decimal(part[beta], 8)} | {b['sampled']} | "
                      f"{decimal(gpt[beta], 8) if beta in gpt else '-'} | {b['source']}")
    report.append("RESULT: " + ("all comparisons hold" if not problems else "PROBLEMS: " + "; ".join(problems)))
    (EVID / "count_h8.txt").write_text("\n".join(report) + "\n", encoding="ascii", newline="\n")
    for line in report[2:7] + lines_gpt[:1] + [report[-1]]:
        print(line[:200])
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
