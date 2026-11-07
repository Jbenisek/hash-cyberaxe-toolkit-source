#!/usr/bin/env python3
"""The names that the templates of the seventh package use ({{name}} in src/*.md and src/*.json), each computed from
the one data place tools/pkg7_data.py, from the experiment program, from the count (research/pkg7/count) and from
the evidence files that name the SHA-256 of the program. Research helper, not submitted.

    python -B tools/pkg7_text.py        prints the claim line and the figures behind it

Rounding: costs and bounds are rounded up, margins, counts and rooms down. Every rounded bound is checked against
the unrounded value before it is returned. A file of evidence is used only while it names the SHA-256 of the
program as it is now; otherwise the build stops.
"""
import hashlib
import importlib.util
import json
import math
import re
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
sys.path.insert(0, str(TOOLS))
import pkg7_data as D  # noqa: E402

PKG, CAND, PROGRAM = D.PKG, D.CAND, D.PROGRAM
EVID, TEXT = PKG / "work" / "evidence", PKG / "work" / "text"
PASS_BUDGET_LOG2, PASS_OPS_LOG2 = 84, 10
LOOP_X2, LOOP_OUTER, LOOP_SLOW = 1, 8, 16          # bounds of the loop control (6.4), stated in words
E1_RATE_LOG2 = Fraction(3141, 100)                 # measured pass rate of the E1 test, whole class (layout runs)
FILED_BOUND, FILED_CHARGE = Fraction(9752, 100), Fraction(191, 10)
FILED_RA = Fraction(302248762304709, 2097152)      # exact count with rule A of entry c66f230d (144,123,440.89)


def stop(message):
    raise SystemExit("pkg7_text.py: " + message)


def up(x, d):
    q = Fraction(10) ** d
    return Fraction(math.ceil(Fraction(x) * q), q)


def dn(x, d):
    q = Fraction(10) ** d
    return Fraction(math.floor(Fraction(x) * q), q)


def near(x, d):
    q = Fraction(10) ** d
    return Fraction(math.floor(Fraction(x) * q + Fraction(1, 2)), q)


def num(x, d=0):
    """A number with thousands separators and d decimals (the value must already be rounded)."""
    return f"{float(x):,.{d}f}" if d else f"{int(x):,}"


def log2f(x):
    x = Fraction(x)
    return math.log2(x.numerator) - math.log2(x.denominator)


def load_program():
    spec = importlib.util.spec_from_file_location("halfsearch_pkg7_text", PROGRAM)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def class_total():
    text = (D.COUNT / "full_totals.txt").read_text(encoding="ascii")
    if f"eta {D.ETA:08x}" not in text.split("\n")[0] or "extra_mask 00000000" not in text.split("\n")[0]:
        stop("count/full_totals.txt is not the count of the whole class")
    m = re.search(r"^R \(all solutions\) = (\d+)/(\d+) = ", text, re.M)
    return Fraction(int(m.group(1)), int(m.group(2)))


def entry_share(name, sha):
    lines = (EVID / name).read_text(encoding="ascii").split("\n")
    if sha not in lines[0]:
        stop(f"work/evidence/{name} is not for the program as it is now")
    row = next(l for l in lines if l.startswith(f"RULE {D.RULE_CONDITIONS} |"))
    c = [x.strip() for x in row.split("|")]
    ctx = re.findall(r"(\d\.\d+) \(", c[9])
    per_outer = c[10].split()
    return {"trial_log2": c[3], "batches": Fraction(c[5]), "ctx_max": Fraction(ctx[0]), "ctx_min": Fraction(ctx[1]),
            "outer_max": Fraction(per_outer[0]), "outer_min": Fraction(per_outer[1])}


def table(rows):
    return "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)


BATCH_WHAT = {
    "loop": "next list position, end test, branch",
    "X0 to X10": "X0 (1), D0.d1 (1), X10 (1)",
    "C2 to z": "a1 (1), d1 (6), c1 (1), b1 (6), z (3)",
    "rule A": "word y (8), flags and branch (6)",
    "entry count": "next count, budget test, branch",
    "C2, rest": "z again (4), c1 again (1), Y14 (5), Y6 (7)",
    "C1 to Y1": "D0.b1 X5 (13), a1 (2), d1 (6), c1 (1), b1 (6), sum (3)",
    "E1, A and B": "a1 d1 (8), A: c1 b1 a2 c2 (16), B: (16), beta (1)",
    "E1 test": "eps, beta XOR eps (2), n (7), flags and branch (4)",
    "restore": "four kept words loaded again",
}


def build_tokens():
    m = load_program()
    sha = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    rule = D.RULE_CONDITIONS
    if (m.RULE_CONDITIONS, m.FACTOR, m.CLASS_SIZE, m.BATCHES, m.KEPT, m.REGISTERS) != (
            rule, D.FACTOR, D.CLASS_SIZE, D.LIST_WORDS, D.KEPT_WORDS, D.MACHINE_REGISTERS) or rule != 8:
        stop("the program is not the program of pkg7_data.py, or the rule in use is not the one the text is written for")
    t = {"submission_state": D.SUBMISSION_STATE, "program_sha": sha}
    for name in ("s1_s3", "class_q", "residual", "lemma_n", "packed", "count_12", "count_3", "count_4"):
        t["part_" + name] = (PKG / "src" / "parts" / f"{name}.md").read_text(encoding="ascii").rstrip("\n")
    W, MEM, F = D.LIST_WORDS, D.CLASS_SIZE, D.FACTOR
    share = 2 ** (rule - 3)
    nd = -(-(1 << 46) // F)
    if not (nd - 1) << 64 < m.RUN_PAIRS <= nd << 64 or m.STAGE_2_BUDGET != W * m.RUN_PAIRS >> 5:
        stop("the number of values of C0.d1 does not fit RUN_PAIRS of the program")
    N = nd << 81
    if N * F < 1 << 127:
        stop("the trials of a run times the factor are below 2^127")
    t.update(members=num(MEM), members_plain=str(MEM), members_last=num(MEM - 1), members_class=num(1 << 19),
             list_words=num(W), full_words=num(W - 1), last_word=num(W - 1), last_first=num(7 * (W - 1)),
             cube_mask=f"{D.CLASS_MASK:08x}", cube_value=f"{D.CLASS_VALUE:08x}", factor=num(F), nd=num(nd),
             nd_last=num(nd - 1), share_inv=str(share), budget_share=str(float(Fraction(1, share))),
             rule_n_word={8: "eight"}[rule], loop_lanes=num(7 * W))
    if MEM != 7 * (W - 1) + 4:
        stop("the last list word does not hold four members")
    lN = log2f(N)
    t.update(trials_log2=f"{lN:.3f}", trials_log2_6=str(float(up(lN, 6))), rate_log2=f"{128 - math.log2(F):.3f}",
             outer_log2=f"{lN - 49:.3f}", w5_family_log2=f"{math.log2(nd) + 32:.2f}")
    # ---- counts of the program
    tb = {name: rows for name, rows in m.TABLES.items()}
    a, s2 = tb["batch"][:m.STAGE_A_PARTS], tb["batch"][m.STAGE_A_PARTS:]
    A, S2 = (sum(r[1] for r in a), sum(r[2] for r in a)), (sum(r[1] for r in s2), sum(r[2] for r in s2))
    pieces = {name: tuple(sum(r[i] for r in rows) for i in (1, 2, 3)) for name, rows in tb.items() if name != "batch"}
    if (A, S2) != (D.STAGE_A_BY_RULE[rule], D.STAGE_2_BY_RULE[rule]) or pieces != {
            "outer step": D.OUTER_STEP, "table build": D.TABLE_BUILD, "middle step": D.MIDDLE_STEP}:
        stop("TABLES of the program is not PART B of pkg7_data.py")
    rows = [("Part", "What is computed", "Operations", "Loads"), ("---", "---", "---:", "---:")]
    for part in tb["batch"]:
        what = BATCH_WHAT[part[0]]
        listed = [int(x) for x in re.findall(r"\((\d+)\)", what)]
        if listed and sum(listed) != part[1]:
            stop(f"the description of the part {part[0]} does not add up to its {part[1]} operations")
        rows.append((part[0], what, part[1], part[2]))
        if part is a[-1]:
            rows.append(("", "stage A, every batch", A[0], A[1]))
    rows.append(("", "stage 2, only after a pass of stage A", S2[0], S2[1]))
    t["batch_table"] = table(rows)
    rows = [("Piece", "Part", "Operations", "Loads", "Stores"), ("---", "---", "---:", "---:", "---:")]
    for name, label in (("table build", "table build, per list word"), ("middle step", "middle step, per value of X2"),
                        ("outer step", "outer step")):
        rows += [(name, part[0], part[1], part[2], part[3]) for part in tb[name]]
        rows.append(("", label) + pieces[name])
    t["pieces_table"] = table(rows)
    t.update(a_ops=str(A[0]), a_loads=str(A[1]), a_total=str(sum(A)), s2_ops=str(S2[0]), s2_loads=str(S2[1]),
             s2_total=str(sum(S2)), middle_total=str(sum(D.MIDDLE_STEP)), build_total=str(sum(D.TABLE_BUILD)),
             outer_total=str(sum(D.OUTER_STEP)), build_loads=str(D.TABLE_BUILD[1]),
             build_sum="%d + %d + %d = %d" % (D.TABLE_BUILD + (sum(D.TABLE_BUILD),)),
             middle_sum="%d + %d + %d = %d" % (D.MIDDLE_STEP + (sum(D.MIDDLE_STEP),)),
             outer_sum="%d + %d + %d = %d" % (D.OUTER_STEP + (sum(D.OUTER_STEP),)),
             build_per_outer=num(W * sum(D.TABLE_BUILD)))

    # ---- cost
    def per_x2(stage_a, stage_2, middle, shr=share):
        return (W * stage_a + Fraction(W * stage_2, shr) + middle + LOOP_X2
                + Fraction(W * sum(D.TABLE_BUILD) + sum(D.OUTER_STEP) + LOOP_OUTER, 1 << 32) + Fraction(LOOP_SLOW, 1 << 64))

    def charged(p):
        return Fraction(math.ceil(p / MEM * Fraction(104, 100) * 10), 10)

    P = per_x2(sum(A), sum(S2), sum(D.MIDDLE_STEP))
    budgeted, charge = P / MEM, charged(P)
    if float(charge) != D.cost(rule)[2] or abs(float(budgeted) - D.cost(rule)[1]) > 1e-4:
        stop("the cost of this module is not the cost of pkg7_data.py")
    l430, lc = dn(math.log2(430), 6), up(log2f(charge), 6)

    def bound(trials_log2, c=charge):
        """log2 of c * trials * (1 + 2^-7) / 430, rounded up to four decimals."""
        return up(Fraction(trials_log2) + up(log2f(c), 6) - l430 + Fraction(1123, 100000), 4)

    lt = up(lN, 6)
    main = lt + lc - l430
    true_main = lN + log2f(charge) - math.log2(430)
    b4 = bound(lt)
    b2 = up(Fraction(math.log2(2.0 ** float(b4) + 2.0 ** 64)), 2)
    side = (1 << PASS_BUDGET_LOG2 + PASS_OPS_LOG2) + (1 << 60) + (1 << 24) + (1 << 11) + 1 + 430 * (2 + (1 << 63))
    allow = charge * N / 128
    if not (float(main) >= true_main and float(b4) >= true_main + math.log2(1 + 2 ** -7) and side < allow and b2 > b4):
        stop("a rounded bound of the total is below the value it bounds")
    claim = up(b2, 1)
    t.update(charge=str(float(charge)), budgeted=str(float(up(budgeted, 4))), budgeted_up=str(float(up(budgeted, 3))),
             p_x2=num(up(P, 4), 4), charged_x2=num(charge * MEM, 1), charge_log2=str(float(lc)),
             charge_margin=str(float(dn((charge / budgeted - 1) * 100, 1))),
             charge_room=str(float(dn((charge - budgeted) * MEM / W, 2))), main_log2=f"{float(up(main, 6)):.6f}", l430=f"{float(l430):.6f}",
             bound_4dec=str(float(b4)), bound_2dec=str(float(b2)), time_log2=str(float(claim)),
             side_log2=str(float(up(log2f(side), 2))), allow_log2=str(float(dn(log2f(allow * 128) - 7, 3))),
             pass_budget_log2=str(PASS_BUDGET_LOG2), pass_ops_log2=str(PASS_BUDGET_LOG2 + PASS_OPS_LOG2),
             pass_share=str(float(dn(log2f(charge * N) - PASS_BUDGET_LOG2 - PASS_OPS_LOG2, 1))),
             pass_rate_budget=str(float(dn(lN - PASS_BUDGET_LOG2, 2))),
             pass_expected=str(float(near(Fraction(lN) - E1_RATE_LOG2, 2))),
             pass_room=str(float(dn(PASS_BUDGET_LOG2 - (Fraction(lN) - E1_RATE_LOG2), 1))),
             t_a_x2=num(W * sum(A)), t_a_trial=f"{W * sum(A) / MEM:.6f}", t_2_x2=num(Fraction(W * sum(S2), share), 5),
             t_2_trial=f"{W * sum(S2) / share / MEM:.6f}", t_m_trial=f"{sum(D.MIDDLE_STEP) / MEM:.6f}",
             t_b_x2=f"{W * sum(D.TABLE_BUILD) / 2 ** 32:.9f}", t_b_trial=f"{W * sum(D.TABLE_BUILD) / 2 ** 32 / MEM:.3e}",
             t_o_x2=f"{sum(D.OUTER_STEP) / 2 ** 32:.3e}", t_o_trial=f"{sum(D.OUTER_STEP) / 2 ** 32 / MEM:.3e}",
             t_l_x2=f"{LOOP_X2 + LOOP_OUTER / 2 ** 32:.9f}", t_l_trial=f"{(LOOP_X2 + LOOP_OUTER / 2 ** 32) / MEM:.3e}",
             build_per_trial_alone=num(near(Fraction(W * sum(D.TABLE_BUILD), MEM), 4), 4))
    indep = 1 - (1 - Fraction(1, 2 ** rule)) ** 7
    t.update(indep_share=f"{float(indep):.4f}", indep_share_6=f"{float(indep):.6f}",
             expected=str(float(up(per_x2(sum(A), sum(S2), sum(D.MIDDLE_STEP), 1 / indep) / MEM, 4))))
    ub = bound(127)
    t.update(uniform_bound=str(float(up(ub, 3))), uniform_claim=str(float(up(ub, 1))),
             claim_2_25=str(float(up(bound(102), 1))))
    if float(up(ub, 3)) - math.log2(F) >= float(b2):
        stop("the bound for a factor f does not give the bound of the claim at the assumed factor")

    def other(stage_a, stage_2, middle, shr=share):
        c = charged(per_x2(stage_a, stage_2, middle, shr))
        return str(stage_a), str(stage_2), str(float(c)), str(float(up(bound(lt, c), 1)))

    k0 = D.EVERY_READ_A_LOAD[rule]
    t["kept0_a"], t["kept0_2"], t["kept0_charge"], t["kept0_claim"] = other(sum(k0[0]), sum(k0[1]), sum(D.EVERY_READ_MIDDLE_STEP))
    t["addr_a"], t["addr_2"], t["addr_charge"], t["addr_claim"] = other(sum(A) + 3, sum(S2) + 4, sum(D.MIDDLE_STEP))
    for n in (4, 6, 8):
        sa, s_2, c, cl = other(sum(D.STAGE_A_BY_RULE[n]), sum(D.STAGE_2_BY_RULE[n]), sum(D.MIDDLE_STEP), 2 ** (n - 3))
        t[f"r{n}_stages"], t[f"r{n}_charge"], t[f"r{n}_claim"] = f"{sa}, {s_2}", c, cl
    if t["r8_claim"] != t["time_log2"] or t["r8_charge"] != t["charge"]:
        stop("the row of the rule in use is not the claim")
    # ---- the count
    kept, r_sub = D.kept_counts("a15")
    exact, cons = kept[rule]
    r_class = class_total()
    if near(FILED_RA, 2) != Fraction(14412344089, 100):
        stop("FILED_RA is not the exact count with rule A that entry c66f230d prints (144,123,440.89)")
    if not cons <= exact <= r_sub or cons / F < Fraction(7, 2):
        stop("the kept counts are not in order, or the margin is below 3.5")

    def frac(x):
        return f"{x.numerator}/{x.denominator}"

    heavy = (67698688 + 51384320 + 50790400 + 13246464 + 1474560 + 755712, 13328 + 3465, 456 + 1665)
    if (near(r_sub - heavy[0] - heavy[1], 4), near(exact - heavy[0] - heavy[2], 4), near(cons - heavy[0], 4)) != (
            Fraction(102605523, 10000), Fraction(58464676, 10000), Fraction(53094537, 10000)):
        stop("the table of betas in src/proof_evidence.md does not add up to the totals of the count")
    expected_good = Fraction(math.floor(cons) * N, 1 << 128)
    t.update(r_sub=num(near(r_sub, 2), 2), r_sub_int=num(math.floor(r_sub)), r_sub_4=num(near(r_sub, 4), 4), r_sub_frac=frac(r_sub),
             r_sub_log2=f"{log2f(r_sub):.2f}", r_sub_prob=f"{128 - log2f(r_sub):.2f}",
             r_class=num(near(r_class, 2), 2), r_class_int=num(math.floor(r_class)), r_class_frac=frac(r_class),
             sub_gain=str(float(dn(r_sub / r_class, 3))), kept_exact=num(near(exact, 2), 2),
             kept_exact_int=num(math.floor(exact)), kept_exact_4=num(near(exact, 4), 4), kept_exact_frac=frac(exact),
             kept_cons=num(near(cons, 2), 2), kept_cons_int=num(math.floor(cons)), kept_cons_4=num(near(cons, 4), 4),
             kept_cons_frac=frac(cons), kept_diff=num(near(exact - cons, 2), 2), rule_loss=num(near(r_sub - exact, 2), 2),
             margin=str(float(dn(cons / F, 2))), margin_2_25=str(float(dn(cons / 2 ** 25, 2))),
             margin_exact=str(float(dn(exact / F, 2))), margin_all=str(float(dn(r_sub / F, 2))),
             margin_class=str(float(dn(r_class / F, 2))), filed_margin_exact=str(float(dn(FILED_RA / 2 ** 25, 2))),
             filed_margin_all=str(float(dn(r_class / 2 ** 25, 2))),
             f_min=num(math.ceil(-math.log(0.607) * 2 ** 47 / nd)), expected_good=str(float(dn(expected_good, 2))),
             cluster_m=str(float(dn(float(dn(expected_good, 2)) / -math.log(0.607), 2))),
             trial_share=str(float(near(Fraction(W * 2 ** rule, share * MEM), 4))),
             gain_total=str(float(FILED_BOUND - b2)), gain_rate=f"{math.log2(F) - 25:.2f}",
             gain_cost=f"{log2f(FILED_CHARGE / charge):.2f}")
    if abs(float(t["gain_total"]) - float(t["gain_rate"]) - float(t["gain_cost"])) > 0.011:
        stop("the two parts of the gain do not add up")
    # ---- measurements of the entry to stage 2
    e = [entry_share(f, sha) for f in ("entry_share_8192x1_1.txt", "entry_share_512x16_1.txt", "entry_share_8192x1_2.txt")]
    if [x["trial_log2"] for x in e] != ["2^-8.0019", "2^-7.9992", "2^-8.0000"]:
        stop("the shares of the trials in the entry-share files are not those printed in the templates")
    t.update(entry_1=f"{float(e[0]['batches']):.5f}", entry_2=f"{float(e[1]['batches']):.5f}", entry_3=f"{float(e[2]['batches']):.5f}",
             ctx_min=str(float(dn(min(x["ctx_min"] for x in e), 4))), ctx_max=str(float(up(max(x["ctx_max"] for x in e), 4))),
             outer_min=str(float(dn(e[1]["outer_min"], 4))), outer_max=str(float(up(e[1]["outer_max"], 4))),
             entry_room=str(math.floor((Fraction(1, share) / max(x["batches"] for x in e) - 1) * 100)))
    # ---- self-tests
    st = json.loads((TEXT / "selftest_2000_1.json").read_text(encoding="ascii"))
    head, body = (EVID / "selftest_1000000_rule8_61.json").read_text(encoding="ascii").split("\n")[:2]
    lt_ = json.loads(body)
    if sha not in head or (st["seed"], st["cases"], lt_["seed"]) != ("1", 2000, "61"):
        stop("a self-test file is not for this program or not the run that the text names")
    for d in (st, lt_):
        if not (d["lanes_right"] == d["lanes_checked"] == 7 * d["cases"] and d["counts_equal_table"] and d["sums_below_bounds"]
                and d["same_counts_in_every_case"] and d["cases_stored_right"] == d["cases"] and d["zero_test_words"] == 0
                and d["zero_lane_patterns_right"] == 128 and d["rule_a_patterns_right"] == d["rule_a_patterns"] == 65536
                and d["members_in_list"] == MEM and d["registers"] == 16):
            stop("a self-test file does not say what the text says of it")
    order = ("X0 to X10", "C2 to z", "rule A", "C2, rest", "C1 to Y1", "E1, A and B", "E1 test")
    sums = [f"{st['parts'][p]['largest_sum']:.3f}" for p in order]
    bounds = [str(st["parts"][p]["bound"]) for p in order]
    t.update(st_cases=num(st["cases"]), st_lanes=num(st["lanes_right"]), st_rule_lanes=str(st["lanes_passing_rule_a"]),
             st_rule_batches=str(st["batches_entering_stage_2"]), st_patterns=num(st["rule_a_patterns"]),
             st_satisfied=num(st["rule_a_patterns_satisfied"]), st_sums=", ".join(sums[:-1]) + " and " + sums[-1],
             st_bounds=", ".join(bounds[:-1]) + " and " + bounds[-1], reg_batch=str(st["registers"]),
             reg_outer=str(st["outer_step"]["registers"]), reg_build=str(st["table_build"]["registers"]),
             reg_middle=str(st["middle_step"]["registers"]), lt_cases=num(lt_["cases"]), lt_lanes=num(lt_["lanes_right"]),
             lt_rule_lanes=num(lt_["lanes_passing_rule_a"]), lt_rule_batches=num(lt_["batches_entering_stage_2"]),
             lt_largest=str(float(up(Fraction(lt_["largest_lane"], 1 << 32), 3))))
    if (st["registers"], st["outer_step"]["registers"], st["table_build"]["registers"], st["middle_step"]["registers"]) != tuple(
            D.REGISTERS_IN_USE[k] for k in ("batch", "outer step", "table build", "middle step")):
        stop("the registers of the self-test are not those of pkg7_data.py")
    # ---- memory
    words = 7 * W + 512
    t.update(mem_words=num(words), mem_bytes=num(32 * words), search_mem_log2=str(math.ceil(math.log2((1 << 19) + 32 * words))))
    # ---- the displays of Section 4 as printed
    pl = json.loads((TEXT / "proof_lines.json").read_text(encoding="ascii"))
    import proof_lines_pkg7
    if pl["problems"] or pl["display_sha256"] != proof_lines_pkg7.displays()[1] or pl["program_sha256"] != sha:
        stop("work/text/proof_lines.json is not a clean run on the displays and the program as they are now: "
             "run tools/proof_lines_pkg7.py")
    t.update(pl_tuples=num(pl["tuples"]), pl_extreme=num(pl["extreme"]), pl_result="no failure")
    la = (TEXT / "lemma_a_text.txt").read_text(encoding="ascii")
    cases = re.search(r"\(a\) to \(d\): (\d+) cases .*; wrong 0; ", la)
    if sha not in la or not cases:
        stop("work/text/lemma_a_text.txt is not a clean run for the program as it is now: run tools/lemma_a_text_pkg7.py")
    t["la_cases"] = num(int(cases.group(1)))
    # ---- the local run of the organizer harness (own mirror), if there is one for these files
    t.update(validation())
    return t


def validation():
    """Figures of the local harness run, from work/text/validation_log.txt if it exists (own mirror), else from the
    log of the step PROGRAM. The note quotes only a log that names the SHA-256 of the program."""
    sha = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    own, first = TEXT / "validation_log.txt", EVID / "validation_log.txt"
    log = own.read_text(encoding="utf-8", errors="replace") if own.exists() else first.read_text(encoding="utf-8", errors="replace")
    if f"sha256 {sha}  experiments/halfsearch.py" not in log:
        stop("the validation log is not for the program as it is now")
    tries = re.search(r"residual-search: trials=256 successes=256 .* tries mean=([0-9.]+) max=(\d+)", log)
    entered = re.search(r"observation batch_stage_2_entered: 256 rows, values \[0, 1\], sum (\d+)", log)
    out = {"tries_mean": tries.group(1), "entered_local": entered.group(1)}
    lines = [
        "- `python3 experiments/halfsearch.py --selftest 2000 1`: exit status 0; 14,000 of 14,000 lanes right against the "
        "complete digests of their two real messages; the counts of the tables in every case; rule A right on 65,536 of "
        "65,536 packed words of patterns.",
        "- The long self-test, 1,000,000 cases with seed 61: 7,000,000 of 7,000,000 lanes right.",
        "- The displays of Section 4 exactly as printed, run by a tool on 20,000 tuples of eight words: each of the 96 "
        "names equals its value in a forward compression of the real message, and Table C holds cell by cell.",
        "- A second counting machine that shares no code with the program counts the same operations, loads and stores "
        "for all four pieces and refuses the batch with 15 registers.",
        "- The decisions of the program equal those of its first form, which tests the rule as written on h1, on 200,000 "
        "batches.",
        "- The count: my counter against the fractions of GPT Sol 6.1, 0 differences; complete enumeration with 8-bit "
        "words, 6,805,032 integers, none different.",
    ]
    proof_sha = hashlib.sha256((CAND / "proof.md").read_bytes()).hexdigest() if (CAND / "proof.md").exists() else ""
    if own.exists() and f"sha256 {proof_sha}  proof.md" in log:
        tests = re.findall(r"^Ran (\d+) tests", log, re.M)
        if '"status": "mechanically_valid"' in log and "experiment status: passed" in log and len(tests) == 3:
            lines += [
                "- `python3 scripts/local_tracks.py check blake3-r2-exploratory` in a local mirror of the repository: "
                "`mechanically_valid`. The repository's test script: three runs with %s, %s and %s tests, all pass." % tuple(tests),
                "- Organizer intake run locally with the pinned image, with the mirror copy marked ready: both experiments "
                "`passed`, 256 of 256 mask events each, output identical on replay; the toy search tried %s members on "
                "average; its counted batch reported %s operations and %s loads in stage A, %s and %s in stage 2 and 7 right "
                "lanes on every seed, and entered stage 2 on %s of 256 seeds."
                % (tries.group(1), D.STAGE_A_BY_RULE[8][0], D.STAGE_A_BY_RULE[8][1], D.STAGE_2_BY_RULE[8][0],
                   D.STAGE_2_BY_RULE[8][1], entered.group(1)),
            ]
    else:
        lines.append("- The organizer harness has NOT been run on the text of this package as it is now; it was run on the "
                     "program with an earlier text (both experiments passed, 256 of 256 each, replay identical; the toy "
                     "search tried %s members on average)." % tries.group(1))
    out["checks_block"] = "\n".join(lines)
    return out


def main():
    t = build_tokens()
    print(f"state {t['submission_state']}; program {t['program_sha'][:16]}; sub-class {t['members']} members, {t['nd']} values of "
          f"C0.d1, 2^{t['trials_log2']} trials; factor {t['factor']}, kept for H1 {t['kept_cons']}, margin {t['margin']}")
    print(f"stage A {t['a_total']}, stage 2 {t['s2_total']}; per value of X2 {t['p_x2']}, budgeted {t['budgeted']}, charged "
          f"{t['charge']}; bound 2^{t['bound_4dec']} < 2^{t['bound_2dec']}; claim time_log2 {t['time_log2']}")
    print(f"other readings: every read a load {t['kept0_claim']} (charged {t['kept0_charge']}); with address additions "
          f"{t['addr_claim']} ({t['addr_charge']}); rules 4 / 6 / 8: {t['r4_claim']} / {t['r6_claim']} / {t['r8_claim']}; "
          f"uniform rate {t['uniform_claim']}; factor 2^25: {t['claim_2_25']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
