#!/usr/bin/env python3
"""The conservative count of each first-stage rule over ALL betas with a part. Research helper, not submitted.

    python -B tools/conservative_h8.py

Reads evidence/pairs_recount_<eta>.txt (every outcome with its two factors; tools/outcomes_h8.py) and, for every
rule of pkg6_data.RULES, evidence/rule_a_sat_<eta>_rule<n>.txt (tools/rule_a_sat.py) and, where they exist, the
files of the second formula evidence/rule_a_sat2_<solver>_<eta>_rule<n>.txt (tools/rule_a_sat2.py).

The conservative count of a rule is the sum of E1 * N3 / 2^83 over the outcomes for which the solver answered that
no solution violates the rule, taken only from the betas that the calculator counted in full (a beta in which an
outcome went through the random-subset branch of the E3 count is left out with all its outcomes). Every outcome
with a violating solution is left out in full. The sums are exact fractions of the printed factors.

Writes evidence/conservative_h8.txt and prints its summary lines. The groundwork's figures
(research/h8/batch/H8_conservative.txt, eight betas of an earlier list) are recomputed on its own list and compared.
"""
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import pkg6_data as data  # noqa: E402

EVID, ETA = data.EVID, data.ETA
SCALE = 2 ** 83
GROUNDWORK = data.RESEARCH / "h8" / "batch"
SOLVERS2 = ("cadical", "cryptominisat5")


def read_outcomes():
    """({(beta, tau, eps): Fraction}, {beta: sampled outcomes}) from the outcome file of the package."""
    prod, sampled = {}, {}
    for line in (EVID / f"pairs_recount_{ETA:08x}.txt").read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) > 2 and f[0] == "PAIR":
            sampled[f[2]] = int(f[f.index("sampled") + 1])
        elif len(f) > 8 and f[0] == "OUTX":
            prod[(f[2], f[3], f[4])] = Fraction(int(f[6]) * int(f[8]), SCALE)
    return prod, sampled


def read_sat(path, first="ALL"):
    """{(beta, tau, eps): {question: answer}} of a result file; question names in upper case."""
    out = {}
    if not path.exists():
        return None
    for line in path.read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) >= 5 and f[0] in (first, "VIOLATE"):
            out.setdefault((f[1], f[2], f[3]), {})["VIOLATE" if f[0] == "VIOLATE" else "ALL"] = (f[4], line)
    return out


def main():
    prod, sampled = read_outcomes()
    estimated = {b for b, n in sampled.items() if n}
    exact = {k: v for k, v in prod.items() if k[0] not in estimated}
    total, total_exact = sum(prod.values()), sum(exact.values())
    lines = [f"CONSERVATIVE COUNT PER RULE, class eta {ETA:08x} (pin H8); tools/conservative_h8.py; unit 2^-128 per trial",
             f"outcomes {len(prod)} in {len({k[0] for k in prod})} betas, sum {float(total):,.6f}; betas with estimates "
             f"{len(estimated)} ({sum(1 for k in prod if k[0] in estimated)} outcomes, {float(total - total_exact):.6f}), left out of "
             f"every figure below; outcomes of the betas counted in full {len(exact)}, sum {float(total_exact):,.6f}"]
    ground = {}
    for m in re.finditer(r"^rule A(\d): (\d+) outcomes can violate it; they carry ([\d.]+) in all .*?rate without them ([\d.]+)$",
                         (GROUNDWORK / "H8_conservative.txt").read_text(encoding="ascii"), re.M):
        ground[int(m.group(1))] = (int(m.group(2)), float(m.group(4)))
    ground_keys, ground_bad = set(), {}
    for line in (GROUNDWORK / "H8_sat.txt").read_text(encoding="ascii").split("\n"):
        f = line.split()                               # rule tau eps beta answer ..
        if len(f) > 4 and re.fullmatch(r"A\d", f[0]) and f[4] == "SAT":
            ground_bad.setdefault(int(f[0][1]), set()).add((f[3], f[1], f[2]))
    for line in (GROUNDWORK / "H8_outcomes.txt").read_text(encoding="ascii").split("\n"):
        f = line.split()
        if len(f) > 5 and f[0] == "OUT" and float(f[5]) > -900:
            ground_keys.add((f[1], f[2], f[3]))
    problems = []
    for n in sorted(data.RULES):
        sat = read_sat(EVID / f"rule_a_sat_{ETA:08x}_rule{n}.txt")
        if sat is None:
            lines.append(f"RULE {n}: no result file of tools/rule_a_sat.py")
            continue
        if set(sat) != set(prod):
            problems.append(f"rule {n}: the answers are not for the outcomes of the count")
            continue
        bad_answers = [k for k, v in sat.items() if v["ALL"][0] != "SAT" or " solution 1" not in v["ALL"][1]
                       or v["VIOLATE"][0] not in ("SAT", "UNSAT")
                       or (v["VIOLATE"][0] == "SAT" and " solution 1 rule_A 0" not in v["VIOLATE"][1])]
        if bad_answers:
            problems.append(f"rule {n}: {len(bad_answers)} answers are missing or have a model that fails its check")
        violable = {k for k, v in sat.items() if v["VIOLATE"][0] == "SAT"}
        kept = sum(v for k, v in exact.items() if k not in violable)
        lost = total_exact - kept
        clean = sorted({k[0] for k in exact} - {k[0] for k in violable})
        second = []
        for solver in SOLVERS2:
            other = read_sat(EVID / f"rule_a_sat2_{solver}_{ETA:08x}_rule{n}.txt", first="BASE")
            if other is None:
                second.append(f"{solver}: not run")
                continue
            same = sum(other.get(k, {}).get("VIOLATE", ("?",))[0] == v["VIOLATE"][0] for k, v in sat.items())
            # a base answer counts only with its model checked in plain arithmetic, as in pkg6_data.read_sat
            base = sum(v.get("ALL", ("?", ""))[0] == "SAT" and " solution 1" in v["ALL"][1] for v in other.values())
            second.append(f"{solver}: base satisfiable {base} of {len(other)}, answers to the second question equal {same} of {len(sat)}")
            if same != len(sat) or set(other) != set(sat):
                problems.append(f"rule {n}: {solver} with the second formula does not give the same answers")
            if base != len(sat):
                problems.append(f"rule {n}: {solver} with the second formula has a base answer for {base} of {len(sat)} outcomes "
                                f"(a missing answer is a problem: run tools/rule_a_sat2.py {n} {solver} again)")
        g_keys = {k for k in prod if k in ground_keys}
        g_kept = sum(prod[k] for k in g_keys if k not in violable)
        g_bad = sum(1 for k in g_keys if k in violable)
        lines += [
            f"RULE {n} | outcomes {len(sat)} | no violating solution {len(sat) - len(violable)} | violating solution {len(violable)} "
            f"(in the betas counted in full: {sum(1 for k in exact if k in violable)} of {len(exact)}) | conservative count "
            f"{kept.numerator} / {kept.denominator} = {float(kept):,.4f} | left out {float(lost):,.4f} ({100 * float(lost / total_exact):.4f}%) | "
            f"betas without a violable outcome {len(clean)}",
            f"RULE {n} margins: count / 2^24 = {float(kept) / 2 ** 24:.4f}; / 2^25 = {float(kept) / 2 ** 25:.4f}; / 2^26 = "
            f"{float(kept) / 2 ** 26:.4f}",
            f"RULE {n} second formula: " + "; ".join(second),
            f"RULE {n} on the groundwork's list ({len(g_keys)} outcomes of its {len({k[0] for k in g_keys})} betas): violable {g_bad}, "
            f"kept {float(g_kept):,.1f}; H8_conservative.txt has {ground.get(n, ('-', 0))[0]} and {ground.get(n, ('-', 0.0))[1]:,.1f} "
            f"(its script takes the products from logarithms printed with two decimals and rescales them per beta); the same "
            f"violable outcomes as research/h8/batch/H8_sat.txt: {ground_bad.get(n, set()) == {k for k in g_keys if k in violable}}"]
        if n in ground and (g_bad != ground[n][0] or abs(float(g_kept) - ground[n][1]) > 1e-3 * ground[n][1]
                            or ground_bad.get(n, set()) != {k for k in g_keys if k in violable}):
            problems.append(f"rule {n}: the groundwork's answers on its own list are not reproduced")
        heavy = sorted(((float(prod[k]), k) for k in violable if k in exact), reverse=True)[:3]
        lines.append(f"RULE {n} heaviest outcomes left out: " + "; ".join(f"{k[0]} {k[1]} {k[2]} {v:,.1f}" for v, k in heavy))
    lines.append("RESULT: " + ("all comparisons hold" if not problems else "PROBLEMS: " + "; ".join(problems)))
    (EVID / "conservative_h8.txt").write_text("\n".join(lines) + "\n", encoding="ascii", newline="\n")
    for line in lines:
        if line.startswith(("RULE", "RESULT")) and ("| outcomes" in line or "margins" in line or line.startswith("RESULT")):
            print(line[:260])
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
