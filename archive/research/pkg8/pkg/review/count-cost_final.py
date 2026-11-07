#!/usr/bin/env python3
"""count-cost reviewer: the count against my reruns, and the arithmetic of the cost, the trials and the claim.

    python -B count-cost_final.py        (pure Python; reads only; writes review/count-cost_final.out)

1. review/count-cost_calc2.out (night_pair_calc2 executed by me on the eight heaviest betas) against
   evidence/pairs_recount_830303cf.txt: part of each beta, the set of outcomes with a nonzero product, both logarithms.
2. review/count-cost_gpt/gpt_sol_parts_A.csv (the other model's Rust program, compiled and run by me) against the file
   as received and against the count, beta by beta, as exact fractions.
3. The totals and shares that the text prints.
4. Cost per trial, charge, total, time_log2 for the three rules and two factors; success probability; budgets;
   memory. Every figure is recomputed from the stage counts and compared with the sentence of proof.md that prints it.
"""
import hashlib
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EVID = PKG / "evidence"
OUT, BAD = [], []


def say(text, ok=True):
    OUT.append(("ok   " if ok else "BAD  ") + text)
    if not ok:
        BAD.append(text)


def main():
    prod, sampled = {}, {}
    for line in (EVID / "pairs_recount_830303cf.txt").read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) > 2 and f[0] == "PAIR":
            sampled[f[2]] = int(f[f.index("sampled") + 1])
        elif len(f) > 8 and f[0] == "OUTX":
            prod[(f[2], f[3], f[4])] = (int(f[6]), int(f[8]))
    part = {}
    for (beta, _, _), (e, n) in prod.items():
        part[beta] = part.get(beta, 0) + Fraction(e * n, 2 ** 83)
    estimated = {b for b, n in sampled.items() if n}
    total = sum(part.values())
    exact = sum(v for b, v in part.items() if b not in estimated)

    # 1. the calculator, executed by me
    cpart, cout = {}, {}
    for line in (HERE / "count-cost_calc2.out").read_text(encoding="ascii").split("\n"):
        f = line.split()
        if f and f[0] == "EXACT-E1":
            cpart[f[2]] = float(f[f.index("part") + 1])
        elif f and f[0] == "OUT":
            p1, n3 = float(f[f.index("log2P1") + 1]), float(f[f.index("log2N3") + 1])
            if p1 > -900 and n3 > -900:
                cout[(f[1], f[2], f[3])] = (p1, n3)
    same_part = [b for b in cpart if abs(cpart[b] - float(part.get(b, -1))) < 0.06]
    mine = {k for k in cout}
    theirs = {k for k in prod if k[0] in cpart}
    def k_of(beta):                 # the number of bits that beta fixes in c1; E1 is P1 * 2^(96 - k)
        v = int(beta, 16)
        return bin(((v << 12) | (v >> 20)) & 0x7FFFFFFF).count("1")

    logs = sum(abs(cout[k][0] - (math.log2(prod[k][0]) - (96 - k_of(k[0])))) < 0.006 and abs(cout[k][1] - math.log2(prod[k][1])) < 0.006
               for k in mine & theirs)
    say(f"calculator rerun: {len(cpart)} betas, part equal to the count's in {len(same_part)}; outcomes with a nonzero product {len(mine)} "
        f"against {len(theirs)} in the count, the same set: {mine == theirs}; both logarithms equal to two decimals in {logs}; "
        f"sum of the eight parts {sum(cpart.values()):,.1f} = {100 * sum(cpart.values()) / float(total):.4f}% of the count",
        len(same_part) == len(cpart) == 8 and mine == theirs and logs == len(mine))

    # 2. the other model's program, compiled and run by me
    def norm(path):
        return path.read_bytes().replace(b"\r\n", b"\n")

    my_csv, received, theirs_csv = HERE / "count-cost_gpt" / "gpt_sol_parts_A.csv", EVID / "gpt_recount" / "as_received_parts_A.csv", EVID / "gpt_recount" / "gpt_sol_parts_A.csv"
    gpt, rows = {}, 0
    for row in my_csv.read_text(encoding="ascii").strip().split("\n")[1:]:
        f = row.split(",")
        gpt[f[0]] = gpt.get(f[0], 0) + Fraction(int(f[7]), int(f[8]))
        rows += 1
    g_total = sum(gpt.values())
    full = [b for b in part if b not in estimated]
    identical = [b for b in full if gpt.get(b) == part[b]]
    near = [b for b in full if b in gpt and abs(gpt[b] - part[b]) <= Fraction(1, 10 ** 9) * part[b]]
    off = sorted(((float(gpt[b] / part[b] - 1), b, float(part[b])) for b in full if b in gpt and gpt[b] != part[b]), key=lambda t: -abs(t[0]))
    src = hashlib.sha256((EVID / "gpt_recount" / "gpt_sol_independent_a.rs").read_bytes()).hexdigest()
    say(f"other model's program (source sha256 {src[:16]}) compiled and run by me: csv rows {rows}, equal to the file as received "
        f"{norm(my_csv) == norm(received)}, equal to the package's rerun {norm(my_csv) == norm(theirs_csv)}; total {g_total.numerator} / "
        f"{g_total.denominator} = {float(g_total):,.6f}; betas {len(gpt)}, the same set as the count: {set(gpt) == set(part)}",
        norm(my_csv) == norm(received) == norm(theirs_csv) and set(gpt) == set(part) and g_total == Fraction(85074516985129, 524288))
    say(f"beta by beta, the {len(full)} betas counted in full: identical fractions {len(identical)}, within 10^-9 {len(near)}; not identical: "
        + ("; ".join(f"{b} relative {d:+.2e} of {v:.6f}" for d, b, v in off) or "none")
        + f"; the {len(estimated)} betas with estimates: count {float(sum(part[b] for b in estimated)):.6f}, recount "
        f"{float(sum(gpt.get(b, 0) for b in estimated)):.6f}; recount minus count {float(g_total - total):+.6f}",
        len(near) == len(full) == 53)

    # 3. totals and shares
    order = sorted(part, key=lambda b: -part[b])
    outs = sorted((Fraction(e * n, 2 ** 83) for e, n in prod.values()), reverse=True)
    shares = [float(sum(part[b] for b in order[:i]) / total) for i in (1, 2, 4)]
    say(f"count: {total.numerator} / {total.denominator} = {float(total):,.4f} from {len(part)} betas, {len(prod)} outcomes; in full "
        f"{float(exact):,.4f} from {len(full)} betas, {sum(k[0] not in estimated for k in prod)} outcomes; log2 {math.log2(total):.4f}; "
        f"heaviest beta {shares[0]:.4f}, two {shares[1]:.4f}, four {shares[2]:.4f}; sixteen heaviest outcomes {float(sum(outs[:16]) / total):.4f}",
        f"{float(total):,.4f}" == "162,266,763.6579" and f"{float(exact):,.4f}" == "162,266,763.3758" and len(part) == 60 and len(prod) == 453)

    # 4. arithmetic
    proof = (PKG / "blake3-r2" / "proof.md").read_text(encoding="ascii")
    flat = re.sub(r"\s+", " ", proof)
    claim = json.loads((PKG / "blake3-r2" / "claim.json").read_text(encoding="ascii"))
    words, members = 74899, 524288
    say(f"list: 524288 = 74898 * 7 + 2: {members == 74898 * 7 + 2}; contexts 2^83, batches 74,899 * 2^83, trials 2^51 * 2^32 * 2^19 = 2^{51 + 32 + 19}",
        members == 74898 * 7 + 2 and 51 + 32 + 19 == 102)
    stage_a = {4: 52 + 31, 5: 55 + 32, 6: 58 + 33}
    counts = {4: Fraction(174205287047626759, 2 ** 30), 5: Fraction(135295336110358535, 2 ** 30), 6: Fraction(182145803, 2)}
    charges = {4: 24.6, 5: 19.1, 6: 16.7}
    rows = []
    for n in (4, 5, 6):
        per_x14 = words * stage_a[n] + Fraction(words * 163, 2 ** (n - 3)) + 1024
        budget = per_x14 / members
        row = [n, int(counts[n]), float(counts[n]) / 2 ** 25, float(counts[n]) / 2 ** 26, float(budget), charges[n], charges[n] / float(budget) - 1]
        for factor in (25, 26):
            t = 127 - factor
            rest = 2.0 ** (t - 16 + 10) + 2.0 ** (t - 51 + 11) + 2.0 ** 60 + 2.0 ** 25 + 2.0 ** 11 + 1
            true_total = math.log2((charges[n] * 2.0 ** t + rest) / 430 + 2 + 2.0 ** 63)
            row.append(true_total)
        rows.append(row)
    table_ok = True
    for n, count, m25, m26, budget, charge, margin, t25, t26 in rows:
        cell = (f"| {n} | {count:,} | {math.floor(m25 * 100) / 100:.2f} | {math.floor(m26 * 100) / 100:.2f} | {stage_a[n] - (31 + n - 4)} + {31 + n - 4} | "
                f"{math.ceil(budget * 1000) / 1000:.3f} ({charge}) | {math.ceil(t25 * 10) / 10:.1f} | {math.ceil(t26 * 10) / 10:.1f} |")
        found = cell in proof
        table_ok = table_ok and found
        say(f"rule {n}: count {count:,}, / 2^25 = {m25:.4f}, / 2^26 = {m26:.4f}; budgeted {budget:.4f}, charge {charge} (margin {100 * margin:.2f}%); "
            f"total 2^{t25:.5f} at 2^25 and 2^{t26:.5f} at 2^26; the row of the proof's table is exactly this: {found}", found)
    n, count, m25, m26, budget, charge, margin, t25, t26 = rows[1]
    per_x14 = words * 87 + Fraction(words * 163, 4) + 1024
    main_exp = 102 + math.log2(19.1) - math.log2(430)
    checks = [
        ("9,569,371.25 operations" in flat and float(per_x14) == 9569371.25, f"per X14 {float(per_x14):,.2f}"),
        ("less than 18.253 per trial" in flat and budget < 18.253, f"per trial {budget:.5f} < 18.253"),
        ("19.1 * 524288 = 10,013,900.8" in flat and abs(19.1 * members - 10013900.8) < 1e-6, "charged per X14 10,013,900.8"),
        ("4.6% of the bound" in flat and 0.0455 < margin < 0.0465, f"margin {100 * margin:.3f}%"),
        ("2^(102 + 4.255501 - 8.748193) = 2^97.50731" in flat and abs(math.log2(19.1) - 4.255501) < 5e-7 and abs(math.log2(430) - 8.748193) < 5e-7
         and abs(main_exp - 97.50731) < 5e-6, f"main loop 2^{main_exp:.6f}"),
        ("< 2^97.5186 + 2^64" in flat and main_exp + math.log2(1 + 2 ** -7) < 97.5186 and t25 < 97.5186, f"total 2^{t25:.6f} < 2^97.5186 < 2^97.52"),
        (claim["claim"]["time_log2"] == 97.6 and 97.52 <= 97.6, "claim time_log2 97.6"),
        ("at most 17.525 operations on average" in flat
         and (words * 87 + words * 163 * Fraction(7, 32) + 1024) / members < 17.525, f"expected cost {float((words * 87 + words * 163 * Fraction(7, 32) + 1024) / members):.4f}"),
        ("only for f >= 33,502,523" in flat and math.ceil(2 ** 26 * -math.log(0.607)) == 33502523, f"least factor {math.ceil(2 ** 26 * -math.log(0.607)):,}"),
        (1 - math.exp(-0.5) - 0.003 >= 0.39 and claim["claim"]["success_probability"] == 0.39, f"success {1 - math.exp(-0.5) - 0.003:.5f} >= 0.39"),
        ("1.142 times 2^-5" in flat and "2^-4.81" in flat and abs(words / 2 ** 16 - 1.1429) < 1e-4 and abs(math.log2(words / 2 ** 21) + 4.8073) < 1e-4,
         f"stage-2 budget = {words / 2 ** 16:.4f} * 2^-5 of the trials = 2^{math.log2(words / 2 ** 21):.4f}"),
        ("would give 2^70.6 passes" in flat and abs((102 - 31.39) - 70.61) < 1e-9, "E1 passes 2^70.61 against the budget 2^86 (2^15.39)"),
        ("19.1 * 2^127 / 430 = 2^122.50731" in flat and abs(127 + math.log2(19.1) - math.log2(430) - 122.50731) < 5e-6, "uniform rate 2^122.50731 -> 122.6"),
        ("fewer than 75,776 words, that is 2,424,832 bytes" in flat and 75776 * 32 == 2424832 and words + 256 <= 75776 and 2 ** 19 + 2424832 < 2 ** 22,
         "memory of the search below 2^22 bytes"),
        ("1.87 expected good trials" in flat and "up to 3.76" in flat and abs(float(counts[5]) / 2 ** 26 - 1.8776) < 1e-4
         and abs(float(counts[5]) / 2 ** 26 / -math.log(0.607) - 3.761) < 1e-3, "clustering remark 1.8776 and 3.761"),
        ("It is 77.65% of the count of all solutions" in flat and abs(float(counts[5] / total) - 0.7765) < 1e-4, f"share kept {100 * float(counts[5] / total):.3f}%"),
    ]
    for ok, text in checks:
        say("arithmetic and sentence: " + text, bool(ok))
    lost = total - counts[5]
    say(f"given up in all: exact {float(lost):,.4f} (36,263,162.6160 + 0.2820); the introduction prints 36,263,164 "
        f"(the difference of the two rounded figures 162,266,764 and 126,003,600): {'36,263,164 in all' in flat}; Section 10 prints 36,263,162.6160: "
        f"{'36,263,162.6160' in flat}", abs(float(lost) - 36263164) < 0.5)
    sha = {name: hashlib.sha256((PKG / "blake3-r2" / name).read_bytes()).hexdigest() for name in ("proof.md", "claim.json", "experiments/halfsearch.py")}
    say(f"files as reviewed: proof.md {sha['proof.md'][:16]} ({proof.count(chr(10))} lines), claim.json {sha['claim.json'][:16]}, program "
        f"{sha['experiments/halfsearch.py'][:16]}; state {claim['submission_state']}",
        sha["proof.md"].startswith("76a0c35b7a42624b") and sha["claim.json"].startswith("86804b4e80fc7327") and claim["submission_state"] == "draft")
    (HERE / "count-cost_final.out").write_text("\n".join(OUT) + "\n", encoding="ascii", newline="\n")
    print(f"{len(OUT)} checks, {len(BAD)} bad; details in review/count-cost_final.out")
    for text in BAD[:8]:
        print("BAD " + text[:300])
    return 1 if BAD else 0


if __name__ == "__main__":
    sys.exit(main())
