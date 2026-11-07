#!/usr/bin/env python3
"""Review helper (lens: judge). Reads only; writes review/judge_counts.txt.

Recomputes, from the files in evidence/ and with exact fractions, the figures of the count that the text prints:
the count of all solutions, its parts per beta, the conservative count per rule (an outcome is kept only if all
three solver files say that no solution violates the rule, and its beta holds no estimate), the comparison with
the recount of the other model beta by beta, and it evaluates every model that the solver files print in plain
arithmetic (E3 for A and B from the definitions of proof 6.2). Also the arithmetic of Sections 7 and 8 and the
figures of the long self-test.
"""
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
PKG = HERE.parent
EV = PKG / "evidence"
M = 0xFFFFFFFF
Y3, Y3B, ETA = 0x8127C181, 0x7EDF3E7E, 0x830303CF
QMASK, QVALUE = 0x03CF8303, 0x030C0303
out = []


def say(*a):
    out.append(" ".join(str(x) for x in a))


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M


def e3(a, y4, y9, h1, w8):
    """E3 = G(a, Y4, Y9, Y14; 0, w8) with its second value h1 given: returns (e1, f1, e2, h2, g2, f2)."""
    e1 = (a + y4) & M
    g1 = (y9 + h1) & M
    f1 = ror(y4 ^ g1, 12)
    e2 = (e1 + f1 + w8) & M
    h2 = ror(h1 ^ e2, 8)
    g2 = (g1 + h2) & M
    f2 = ror(f1 ^ g2, 7)
    return e1, f1, e2, h2, g2, f2


def rule(h1, n):
    b = lambda i: h1 >> i & 1
    ok = b(0) == 0 and b(1) == 1 and b(16) == 0 and b(17) == 0
    if n >= 5:
        ok = ok and (b(2) ^ b(3)) == 1
    if n >= 6:
        ok = ok and (b(7) ^ b(8)) == 1
    return ok


def is_solution(tau, eps, y4, h1, y9, w8):
    """The E3 system of an outcome: Y4 in the class, and the differences psi, eps, tau (and eta, by the class)."""
    if ((Y3 + y4) & QMASK) != QVALUE:
        return False
    A = e3(Y3, y4, y9, h1, w8)
    h1b = h1 ^ ror(((Y3 + y4) & M) ^ ((Y3B + y4) & M), 16)          # h1' = ROR(Y14 XOR e1', 16), the same Y14
    B = e3(Y3B, y4, y9, h1b, w8)
    psi = tau ^ ror(tau, 1)
    return (h1 ^ h1b) == ETA and (A[1] ^ B[1]) == psi and (A[2] ^ B[2]) == eps and (A[4] ^ B[4]) == tau \
        and (A[3] ^ B[3]) == ror(ETA ^ eps, 8) and (A[5] ^ B[5]) == ror(psi ^ tau, 7)


# ---- the outcomes
outcomes, sampled, order = {}, {}, []
for line in (EV / "pairs_recount_830303cf.txt").read_text().splitlines():
    f = line.split()
    if not f:
        continue
    if f[0] == "PAIR":
        sampled[f[2]] = int(f[f.index("sampled") + 1])
        order.append(f[2])
    elif f[0] == "OUTX":
        outcomes[(f[2], f[3], f[4])] = Fraction(int(f[6]) * int(f[8]), 2 ** 83)
betas = sorted({k[0] for k in outcomes})
est = sorted(b for b in betas if sampled.get(b, 0) > 0)
total = sum(outcomes.values())
full = sum(v for k, v in outcomes.items() if k[0] not in est)
say(f"outcomes {len(outcomes)} in {len(betas)} betas; sum {float(total):,.4f}; betas with sampled outcomes {len(est)} "
    f"({sum(1 for k in outcomes if k[0] in est)} outcomes, {float(total - full):.6f}); in full {float(full):,.4f}; "
    f"log2 {math.log2(total):.4f}")
part = {b: sum(v for k, v in outcomes.items() if k[0] == b) for b in betas}
top = sorted(part.items(), key=lambda kv: -kv[1])
say("shares: heaviest %.4f, two %.4f, four %.4f; sixteen largest outcomes %.4f" % (
    top[0][1] / total, (top[0][1] + top[1][1]) / total, sum(v for _, v in top[:4]) / total,
    sum(sorted(outcomes.values(), reverse=True)[:16]) / total))
k15 = [b for b in betas if bin(((int(b, 16) << 12 | int(b, 16) >> 20) & 0x7FFFFFFF)).count("1") >= 15]
say(f"betas with k >= 15: {len(k15)}, outcomes {sum(1 for k in outcomes if k[0] in k15)}, sum {float(sum(part[b] for b in k15)):.4f}; "
    f"k <= 14: {len(betas) - len(k15)} betas, {sum(1 for k in outcomes if k[0] not in k15)} outcomes, "
    f"{float(sum(part[b] for b in betas if b not in k15)):,.4f}")

# ---- the solver files
for n in (4, 5, 6):
    files = {"kissat": EV / f"rule_a_sat_830303cf_rule{n}.txt", "cadical": EV / f"rule_a_sat2_cadical_830303cf_rule{n}.txt",
             "cryptominisat5": EV / f"rule_a_sat2_cryptominisat5_830303cf_rule{n}.txt"}
    ans, base, bad_models, models = {}, {}, 0, 0
    for name, p in files.items():
        ans[name], base[name] = {}, {}
        for line in p.read_text().splitlines():
            f = line.split()
            if f and f[0] in ("ALL", "BASE", "VIOLATE") and len(f) >= 5:
                key = (f[1], f[2], f[3])
                (ans if f[0] == "VIOLATE" else base)[name][key] = f[4]
                if "Y4" in f and "w8" in f and f[4] == "SAT":
                    v = {f[i]: int(f[i + 1], 16) for i in range(5, len(f) - 1) if f[i] in ("Y4", "h1", "Y9", "w8")}
                    models += 1
                    ok = is_solution(int(f[2], 16), int(f[3], 16), v["Y4"], v["h1"], v["Y9"], v["w8"])
                    if f[0] == "VIOLATE":
                        ok = ok and not rule(v["h1"], n)
                    bad_models += not ok
    keys = set(outcomes)
    line = [f"RULE {n}:"]
    for name in files:
        line.append(f"{name}: answers {len(ans[name])} (all outcomes covered: {set(ans[name]) == keys}), base SAT "
                    f"{sum(1 for v in base[name].values() if v == 'SAT')} of {len(base[name])}, violate UNSAT "
                    f"{sum(1 for v in ans[name].values() if v == 'UNSAT')}, SAT {sum(1 for v in ans[name].values() if v == 'SAT')}, "
                    f"other {sum(1 for v in ans[name].values() if v not in ('SAT', 'UNSAT'))};")
    agree = all(ans["kissat"].get(k) == ans["cadical"].get(k) == ans["cryptominisat5"].get(k) for k in keys)
    kept = [k for k in keys if all(ans[s].get(k) == "UNSAT" for s in files) and k[0] not in est]
    kept_est = [k for k in keys if all(ans[s].get(k) == "UNSAT" for s in files) and k[0] in est]
    cons = sum(outcomes[k] for k in kept)
    line.append(f"three solvers agree on every outcome: {agree}; kept {len(kept)} (in betas with estimates and unviolable: "
                f"{len(kept_est)}); conservative count {float(cons):,.4f} = {cons.numerator} / {cons.denominator}; "
                f"/ 2^25 = {float(cons) / 2 ** 25:.4f}; / 2^26 = {float(cons) / 2 ** 26:.4f}; share {float(cons / total):.6f}; "
                f"kissat models evaluated here {models}, not a solution or not violating {bad_models}")
    say(" ".join(line))
    if n == 5:
        perb = {}
        for k in kept:
            perb.setdefault(k[0], []).append(outcomes[k])
        say("   rule 5, kept per beta: " + "; ".join(f"{b} {len(v)} {float(sum(v)):,.4f}" for b, v in sorted(perb.items(), key=lambda kv: -sum(kv[1]))))
        dropped = sorted(((outcomes[k], k) for k in keys if k not in kept), reverse=True)[:3]
        say("   rule 5, largest outcomes left out: " + "; ".join(f"{k[0]} {k[1]} {k[2]} {float(v):,.1f}" for v, k in dropped))

# ---- the recount of the other model
for label, name in (("as received", "as_received_parts_A.csv"), ("rerun here", "gpt_sol_parts_A.csv")):
    rows = (EV / "gpt_recount" / name).read_text().splitlines()
    head = rows[0].split(",")
    g = {}
    for r in rows[1:]:
        f = dict(zip(head, r.split(",")))
        g[f["beta"]] = g.get(f["beta"], 0) + Fraction(int(f["R_numerator"]), int(f["R_denominator"]))
    gt = sum(g.values())
    same_full = sum(1 for b in betas if b not in est and g.get(b) == part[b])
    say(f"recount ({label}): betas {len(g)}, the same set as the count: {set(g) == set(betas)}; total {gt.numerator} / {gt.denominator} = "
        f"{float(gt):,.4f}; parts equal as fractions for {same_full} of {len(betas) - len(est)} betas counted in full; "
        f"the {len(est)} betas with estimates: recount {float(sum(g.get(b, 0) for b in est)):.6f}, count {float(sum(part[b] for b in est)):.6f}; "
        f"recount minus count {float(gt - total):.6f}")
    diff = [(b, float(g.get(b, 0)), float(part[b])) for b in betas if b not in est and g.get(b) != part[b]]
    if diff:
        say("   betas in full that differ: " + "; ".join(f"{b} {x:.10f} {y:.10f}" for b, x, y in diff[:6]))
a = (EV / "gpt_recount" / "as_received_parts_A.csv").read_bytes().replace(b"\r\n", b"\n")
b_ = (EV / "gpt_recount" / "gpt_sol_parts_A.csv").read_bytes().replace(b"\r\n", b"\n")
say(f"   the two files of parts are the same text: {a == b_}; 85074516985129 / 524288 = {85074516985129 / 524288:,.4f}")

# ---- arithmetic of Sections 7 and 8
LW, MEM = 74899, 524288
for n, (ops, loads) in ((4, (52, 31)), (5, (55, 32)), (6, (58, 33))):
    bud = Fraction(LW * (ops + loads)) + Fraction(LW * 163, 2 ** (n - 3)) + 1024
    say(f"rule {n}: budgeted per X14 {float(bud):,.2f}, per trial {float(bud / MEM):.5f}; with the margin 19.1 / 18.2521: "
        f"{float(bud / MEM) * 19.1 / (float((Fraction(LW * 87) + Fraction(LW * 163, 4) + 1024) / MEM)):.3f}")
bud5 = float((Fraction(LW * 87) + Fraction(LW * 163, 4) + 1024) / MEM)
for charge, T in ((19.1, 102), (18.8, 102), (19.0, 102), (24.6, 102), (16.7, 102), (19.1, 101), (19.1, 127), (19.1, 103)):
    rest = 2.0 ** (T - 16 + 10) + 2.0 ** (T - 51 + 11) + 2.0 ** 60 + 2.0 ** 25 + 2.0 ** 11 + 1
    tot = math.log2((charge * 2.0 ** T + rest) / 430 + 2 + 2.0 ** 63)
    say(f"charge {charge}, 2^{T} trials: main 2^{T + math.log2(charge) - math.log2(430):.5f}, total 2^{tot:.5f}, one decimal up {math.ceil(tot * 10) / 10:.1f}")
say(f"margin of the charge {19.1 / bud5 - 1:.4f}; expected cost {float((LW * 87 + LW * 163 * 7 / 32 + 1024) / MEM):.4f}; "
    f"budget share of trials {LW / 2 ** 21:.6f} = 2^{math.log2(LW / 2 ** 21):.4f} = {LW / 2 ** 21 * 32:.4f} * 2^-5")
say(f"f_min = {math.ceil(2 ** 26 * -math.log(0.607))}; 1 - exp(-1/2) = {1 - math.exp(-0.5):.6f}; 126003600 / 2^26 = {126003600 / 2 ** 26:.4f}; "
    f"largest cluster size {126003600 / 2 ** 26 / -math.log(0.607):.3f}; 126003600 / 2^24 = {126003600 / 2 ** 24:.3f}")

# ---- the long self-tests
for n in (4, 5, 6):
    p = EV / f"selftest_1000000_rule{n}_61.json"
    j = json.loads(p.read_text().strip().splitlines()[-1])
    keys = [k for k in j if not isinstance(j[k], (dict, list))]
    say(f"selftest rule {n}: " + ", ".join(f"{k}={j[k]}" for k in keys)[:900])

(HERE / "judge_counts.txt").write_text("\n".join(out) + "\n", encoding="utf-8")
print(f"{len(out)} lines -> judge_counts.txt")
