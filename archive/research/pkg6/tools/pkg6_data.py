#!/usr/bin/env python3
"""Every figure of the sixth package (a DRAFT) that depends on the pinned call, the class, the rule or the rate. ONE place.

The package is for the family with message lengths 55 and 63 (pin H8, class 830303cf). The readers of result files,
the tokens and the paragraphs of this file are those of that family; nothing of the fifth package (pin B, lengths
60 and 62) is read except its filed claim, for the sentences that compare the two.

To swap the rule or the factor, edit PART A below and nothing else (FILE_STEPS.md says what must be run again), then

    python -B tools/build_pkg6.py            (renders src/* into the package files and the note)
    python -B tools/fmt_pkg6.py              (format checks, ranges, field lengths, drift)

PART A  the pin, the class, the rule, the assumed factor, the charge.
PART B  everything that follows by arithmetic: Fact P, Lemma Q, Lemma A, the list, the cost, the claim.
PART C  readers of the result files in evidence/ (the figures are read from those files, not typed here).
PART D  the tokens {{name}} that the templates in src/ use, and the paragraphs and tables written from the result
        files (so that a missing file gives a true sentence or stops the build, not a gap).

    python -B tools/pkg6_data.py             prints every token
Research helper, not submitted.
"""
import hashlib
import json
import math
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
RESEARCH = PKG.parent
EVID = PKG / "evidence"
H8 = EVID / "h8"                  # copies of the groundwork's result files (tools/fetch_h8.py; SOURCES.txt names them)
CAND = PKG / "blake3-r2"
PROGRAM = CAND / "experiments" / "halfsearch.py"

# =====================================================================================================
# PART A: what a person edits
# =====================================================================================================
TEXT_PORTED = True                # the templates in src/ and the readers below are those of this family
# Pin H8 (research/h8/design/DESIGN.txt section 0). The top byte of W13 is zero.
PIN = {"X3": 0x29D4FA98, "X7": 0xBEE3AF28, "X11": 0x44036000, "X15": 0x40C58500, "W4": 0x97475638, "W13": 0x0007C006}
PIN_NAME = "pinH8"
LEN_A, LEN_B = 55, 63             # message lengths; W4' = ((K + W4) XOR (LEN_A XOR LEN_B)) - K
ETA = 0x830303CF                  # the class of the package

# RULE A of the two-stage batch (proof 6.3, Lemma A): conditions on h1, the first-half d value of E3 on message A.
# Each entry (mask, value) says: the XOR of the bits of h1 in mask equals value. Three rules are written out, with
# four, five and six conditions, each containing the one before it (research/h8/batch/H8_rules.txt). They were read
# off the E3 counts of the class and are NOT consequences of R = 0. RULE_CONDITIONS says which of them the package
# uses; the build writes it into the line RULE_CONDITIONS of the program, which has the same three rules.
# THE CHOICE (2026-10-06): the rule with the fewest operations per trial whose conservative count, over all betas
# with a part, is at least 3.5 times the assumed factor 2^25. evidence/conservative_h8.txt: four conditions 4.8352,
# five 3.7552, six 2.7142. So five. derive() stops if the count of the rule in use is below 3.5 times the factor.
RULES = {4: ((0x00000001, 0), (0x00000002, 1), (0x00010000, 0), (0x00020000, 0))}
RULES[5] = RULES[4] + ((0x0000000C, 1),)
RULES[6] = RULES[5] + ((0x00000180, 1),)
RULE_CONDITIONS = 5
RULE_A = {ETA: RULES[RULE_CONDITIONS]}
LOG2_FACTOR = 25                  # H1 assumes a rate of 2^LOG2_FACTOR times the uniform one
MIN_MARGIN = 3.5                  # least ratio of the conservative count to the assumed factor (earlier packages: 3.4 to 3.6)
ALT_FACTORS = (25, 26)            # the factors of the table "the other rules and the other factor"
# "draft" until the owner says go for this package; then "ready" (see FILE_STEPS.md). It goes into claim.json.
SUBMISSION_STATE = "ready"
# Primitive operations charged per trial: the budgeted cost of derive() plus a margin. 19.1 is 4.6% above the
# budgeted cost of the rule with five conditions (18.2521 with PREP_OPS below); the filed package has 3.7%.
# evidence/rule_figures.txt has the table of the program agent: 18.8 (margin 3.0%) would print time_log2 97.5 at
# factor 2^25, 19.0 and 19.1 print 97.6. The larger margin is kept because the cost per pair (vc, vd) is bounded in
# words only. The owner decides.
CHARGE = 19.1
# Operations per value of X14 before its batches (the 19 lines of step S1 that read X14 and the 13 constants of a
# batch that change with X14, in seven lanes). A BOUND that is charged: tools/prep_count.py writes that work out on
# the program's machine and counts 91 operations + 59 loads + 13 stores = 163 (evidence/prep_count.txt).
PREP_OPS = 1024
PASS_SHIFT = 16                   # budget on passes of the E1 test (Lemma N): trials * 2^-PASS_SHIFT
RULE_SHARE_H8_RUN = (2048, "1")   # the run of tools/rule_share_h8.py that is quoted: contexts, seed text
RULE_SHARE_H8_LAYOUT = (8, 4, 64, "1")        # its run in the ranges of the algorithm: quadruples, pairs, values of X14, seed text
RULE_SHARE_H8_SECOND = (2048, "2")            # a second run with another seed text, quoted beside the first
STAGE_2_LOG2_SHARE = RULE_CONDITIONS - 3      # stage-2 budget: a share 2^-this of the batches (the program computes the same)
PASS_OPS_LOG2 = 10                # a passing trial is recomputed in below 2^10 operations
MEMORY_LOG2 = 35                  # declared: preprocessing (host below 2^34 bytes, graphics card below 10 GB) and search
PREPROCESSING_LOG2 = 63
ADVICE_LOG2 = 6
SELECTION_OPS_LOG2 = 60           # bound stated for all preprocessing computations (participant estimate)
SELFTEST = ("2000", "1")          # cases and seed of the self-test quoted in the text
BIG_SELFTEST_SEED = "61"          # evidence/selftest_1000000_rule<n>_<seed>.json
SUBMISSIONS = (("17bba2ae", "123.5"), ("5ceb1802", "121.5"), ("04638ed8", "112.4"), ("c47c1a80", "99.4"))
FILED_CLAIM = RESEARCH / "pkg5" / "blake3-r2" / "claim.json"      # the filed package c47c1a80, read for comparisons
FILED_MEMBERS = 65536
# What has been reviewed of THIS text. Change the sentences when the state of the reviews changes.
# State on 2026-10-06, evening: three reviewing helper agents (construction and exact part; count and cost; figures
# and public text) reviewed the text of 17:10; a fourth applied their findings. review/construction_impl_out.txt is
# the file behind "120,000 trials". If a further check of the applied changes is made, say so here.
EXACT_REVIEW = ("These proofs were written by one helper agent of the participant, an instance of the same AI model. "
                "Two further helper agents, whose task was to review this text, checked them. One read the two steps "
                "line by line against the eight assignments of each call and tested them with an implementation of "
                "its own, typed from this text: on 120,000 trials, hashed with the organizer's reference hash, each of "
                "the nine calls of Lemmas S, F and Y has the inputs, the words and the eight values that the lemmas "
                "state. The other read the proofs of the three lemmas and tested the construction from this text on "
                "1,200 real trials in the same way. Neither reported an error in the lemmas or their proofs. No "
                "person has read them.")
REVIEW_CLAIM = ("were written by helper agents of the participant and were reviewed once, by three further helper agents "
                "of the same AI model and by no person")
VERSION_REVIEW = ("This version of the text was reviewed once by three further helper agents, each with a task of its "
                  "own (the construction and the exact part; the count and the cost; the figures and the public text). "
                  "Helper agents applied their findings; the changes they made have not been reviewed in turn. No "
                  "person has reviewed the text. The reviews named in the note of the filed package were of that "
                  "package.")

# =====================================================================================================
# PART B: arithmetic
# =====================================================================================================
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
C_UNIT = 430
# Stage A of a batch, by the number of conditions of the rule (operations, loads), and stage 2, the count of its own
# entry (3 operations, 1 load) included. The build compares them with the table of the program; the self-test of
# the program counts them on its machine (evidence/selftest_1000000_rule<n>_<seed>.json).
STAGE_A_BY_RULE = {4: (52, 31), 5: (55, 32), 6: (58, 33)}
STAGE_A_OPS, STAGE_A_LOADS = STAGE_A_BY_RULE[RULE_CONDITIONS]
STAGE_2_OPS, STAGE_2_LOADS = 115, 48
RULE_A_PROBES = tuple((0x9E3779B9 * (i + 1) ^ (i << 13)) & 0xFFFFFFFF for i in range(4096))
WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve",
         "thirteen", "fourteen", "fifteen", "sixteen")
WORDS_SHARE = {1: "one half", 2: "one quarter", 3: "one eighth", 4: "one sixteenth"}       # 2^-n in words


def rule_a(h1, eta=None):
    """Rule A on the word h1 (PART A)."""
    return all(bin(h1 & mask).count("1") & 1 == value for mask, value in RULE_A[ETA if eta is None else eta])


def rule_on_z(rule, qmask, qvalue):
    """Lemma A (b), (c) for a rule: its conditions on z for the class, and the constants of the stage-A word.

    Returns (conditions, SHIFTS, ALL, V); a condition is (lower bit of z, upper bit of z or None, wanted XOR, the
    bits of h1 it comes from, the bits of e1 that were inserted). A condition on two bits p < q of z is kept at
    position p with the distance q - p; SHIFTS is a tuple of pairs (distance, mask of the positions p with that
    distance), as in the program: the rule holds exactly when ((z XOR y) AND ALL) == V, y the XOR over SHIFTS of
    ((z >> distance) AND mask)."""
    conditions, shifts, everything, wanted = [], {}, 0, 0
    for mask, value in rule:
        hbits = [i for i in range(32) if mask >> i & 1]
        ebits = [(i + 16) % 32 for i in hbits]
        if any(not qmask >> e & 1 for e in ebits):
            raise SystemExit("rule A reads a bit of h1 that meets a free bit of e1: the batch would need a second list")
        for e in ebits:
            value ^= qvalue >> e & 1
        low = sorted((i + 24) % 32 for i in hbits)
        if len(low) not in (1, 2) or everything >> low[0] & 1:
            raise SystemExit("rule A: a condition is neither one bit nor the XOR of two bits of z, or two share a position")
        if len(low) == 2:
            shifts[low[1] - low[0]] = shifts.get(low[1] - low[0], 0) | 1 << low[0]
        everything |= 1 << low[0]
        wanted |= value << low[0]
        conditions.append((low[0], low[1] if len(low) == 2 else None, value, tuple(hbits), tuple(ebits)))
    return conditions, tuple(sorted(shifts.items())), everything, wanted


def ror(v, n):
    return ((v >> n) | (v << (32 - n))) & M32


def rol(v, n):
    return ror(v, 32 - n)


def hx(v):
    return f"{v & M32:08x}"


def num(v):
    return f"{int(round(v)):,}"


def g_steps(A, B, C, D, x, y):
    a1 = (A + B + x) & M32; d1 = ror(D ^ a1, 16); c1 = (C + d1) & M32; b1 = ror(B ^ c1, 12)
    a2 = (a1 + b1 + y) & M32; d2 = ror(d1 ^ a2, 8); c2 = (c1 + d2) & M32; b2 = ror(b1 ^ c2, 7)
    return dict(a1=a1, d1=d1, c1=c1, b1=b1, a2=a2, d2=d2, c2=c2, b2=b2)


def up(x, digits):
    """x rounded up to the given number of decimals (a bound that is stated must not be below the value)."""
    q = 10 ** digits
    return math.ceil(x * q - 1e-9) / q


def down(x, digits):
    q = 10 ** digits
    return math.floor(x * q + 1e-9) / q


def total_exponents(charge, T, free):
    """The chain of Section 8 for a charge and 2^T trials: (main exponent, exponent of the terms after the first,
    stated total exponent, bound with two decimals, time_log2, the total as written)."""
    l_charge, l_unit = math.log2(charge), math.log2(C_UNIT)
    main = T + l_charge - l_unit
    ctx = T - 32 - free
    rest = 2.0 ** (T - PASS_SHIFT + PASS_OPS_LOG2) + 2.0 ** (ctx + 11) + 2.0 ** SELECTION_OPS_LOG2 + 2.0 ** (free + 6) + 2.0 ** 11 + 1
    if not math.log2(rest) < T + l_charge - 7:
        raise SystemExit("the terms after the first are not below a share 2^-7 of the main loop")
    total_exp = math.floor((up(main, 5) + 0.01123) * 1e4 + 1) / 1e4
    bound = up(total_exp, 2)
    time_log2 = up(bound, 1)
    true_total = math.log2((charge * 2.0 ** T + rest) / C_UNIT + 2 + 2.0 ** 63)
    if not true_total < total_exp < bound <= time_log2:
        raise SystemExit("cost arithmetic does not chain")
    return main, math.log2(rest), total_exp, bound, time_log2, true_total


def budget(n, list_words):
    """Operations per value of X14 for the rule with n conditions, budgeted: stage A of every batch, stage 2 of the
    budgeted share 2^-(n - 3) of the batches, and the work before the batches. An exact fraction."""
    a_ops, a_loads = STAGE_A_BY_RULE[n]
    return list_words * (a_ops + a_loads) + Fraction(list_words * (STAGE_2_OPS + STAGE_2_LOADS), 2 ** (n - 3)) + PREP_OPS


def derive():
    d = {}
    p = PIN
    K = (IV[2] + IV[6]) & M32
    w4b = ((((K + p["W4"]) & M32) ^ LEN_A ^ LEN_B) - K) & M32
    a = g_steps(p["X3"], p["X7"], p["X11"], p["X15"], p["W4"], p["W13"])
    b = g_steps(p["X3"], p["X7"], p["X11"], p["X15"], w4b, p["W13"])
    if a["d2"] != b["d2"] or a["b2"] != b["b2"] or a == b:
        raise SystemExit("PIN does not have the property of Fact P")
    if p["W13"] >> 24:
        raise SystemExit("the top byte of W13 is not zero")
    d.update(K=K, KW4=(K + p["W4"]) & M32, W4B=w4b, delta=(p["W4"] - w4b) & M32, A=a, B=b,
             Y3=a["a2"], Y3B=b["a2"], Y11=a["c2"], Y11B=b["c2"])
    if d["delta"] not in (LEN_A ^ LEN_B, -(LEN_A ^ LEN_B) & M32):
        raise SystemExit("W4 - W4' is neither plus nor minus the XOR of the two lengths")
    d["DY3"], d["DY11"] = (d["Y3B"] - d["Y3"]) & M32, (d["Y11B"] - d["Y11"]) & M32
    x = rol(ETA, 16)
    s = (d["DY3"] + x) & M32
    if s & 1 or (s >> 1) & ~x & M32:
        raise SystemExit("no Y4 gives this eta for this pin")
    mask = x & 0x7FFFFFFF
    d.update(x=x, qsum=s, qhalf=s >> 1, qmask=mask, qvalue=~(s >> 1) & mask & M32,
             fixed=bin(mask).count("1"), free=32 - bin(mask).count("1"))
    d["members"] = 1 << d["free"]
    d["list_words"] = -(-d["members"] // 7)
    d["full_batches"], d["rest"] = divmod(d["members"], 7)
    d["spare"] = 7 - d["rest"] if d["rest"] else 0
    # the claim
    T = 127 - LOG2_FACTOR
    d["T"] = T
    d["ctx"] = T - 32 - d["free"]                                # pairs (vc, vd): 2^ctx, vc any word, vd below 2^d_bits
    d["d_bits"] = d["ctx"] - 32
    if not 0 <= d["d_bits"] <= 32:
        raise SystemExit("the pairs (vc, vd) do not fit two words")
    d["pass_budget"] = T - PASS_SHIFT
    d["alphas_exp"] = d["ctx"] + 32                              # contexts: pairs (vc, vd) times values of X14
    d["stage2_shift"] = d["alphas_exp"] - STAGE_2_LOG2_SHARE     # stage-2 budget: list_words * 2^stage2_shift batches
    d["z_conditions"], d["a_shifts"], d["a_all"], d["a_value"] = rule_on_z(RULE_A[ETA], d["qmask"], d["qvalue"])
    d["rule_conditions"] = len(RULE_A[ETA])
    if d["rule_conditions"] != RULE_CONDITIONS or any(mask << distance >> 32 for distance, mask in d["a_shifts"]):
        raise SystemExit("rule A: the number of conditions is not RULE_CONDITIONS, or a shifted bit lies above bit 31 of z")
    d["advice_rule_words"] = 2 + len(d["a_shifts"])
    d["advice_bytes"] = 28 + 4 * d["advice_rule_words"]
    if d["advice_bytes"] > 2 ** ADVICE_LOG2:
        raise SystemExit("the stored constants do not fit the declared advice")
    d["pass_ops"] = d["pass_budget"] + PASS_OPS_LOG2
    d["ctx_ops"] = d["ctx"] + 11
    d["lists_ops"] = d["free"] + 6
    l_charge, l_unit = math.log2(CHARGE), math.log2(C_UNIT)
    d["main_exp"], d["rest_exp"], d["total_exp"], d["total_bound"], d["time_log2"], d["true_total"] = total_exponents(CHARGE, T, d["free"])
    d["seventh"] = T + l_charge - 7
    d["slack"] = 2 ** (d["time_log2"] - d["total_exp"])
    d["pass_share"] = T + l_charge - d["pass_ops"]
    d["f_min"] = math.ceil(2.0 ** (LOG2_FACTOR + 1) * -math.log(0.607))
    if not d["f_min"] <= 2 ** LOG2_FACTOR:
        raise SystemExit("the assumed factor does not give 0.39")
    d["uniform_exp"] = 127 + l_charge - l_unit
    # The total of Section 8 for a factor f between 1 and 2^LOG2_FACTOR (2^127 / f trials): the terms after the first
    # stay below a share 2^-7 of the main loop, so the same chain gives a total below 2^(uniform_total - log2 f).
    d["uniform_total"] = total_exponents(CHARGE, 127, d["free"])[3]
    if abs(d["uniform_total"] - LOG2_FACTOR - d["total_bound"]) > 1e-9:
        raise SystemExit("the total for a general factor is not the stated bound minus log2 f at both ends")
    # the two logarithms as the text prints them (six decimals) must give the main exponent as it prints it (five)
    if f"{T + round(l_charge, 6) - round(l_unit, 6):.5f}" != f"{d['main_exp']:.5f}":
        raise SystemExit("the printed logarithms of the charge and of 430 do not add up to the printed main exponent")
    # per value of X14 (the names say "alpha", as in the fifth package, whose inner parameter was alpha)
    d["stage_a"], d["stage_2"] = STAGE_A_OPS + STAGE_A_LOADS, STAGE_2_OPS + STAGE_2_LOADS
    d["alpha_stage_a"] = d["list_words"] * d["stage_a"]
    d["alpha_stage_2"] = Fraction(d["list_words"] * d["stage_2"], 2 ** STAGE_2_LOG2_SHARE)
    d["alpha_ops"] = budget(RULE_CONDITIONS, d["list_words"])
    d["alpha_charged"] = Fraction(str(CHARGE)) * d["members"]
    if d["alpha_ops"] >= d["alpha_charged"]:
        raise SystemExit("the charge per trial does not cover the budgeted batches")
    d["rule_share"] = Fraction(7, 2 ** d["rule_conditions"])
    if not d["rule_share"] < Fraction(1, 2 ** STAGE_2_LOG2_SHARE):
        raise SystemExit("the stage-2 budget is not above seven times the pass rate of rule A")
    d["alpha_expected"] = d["alpha_stage_a"] + d["list_words"] * d["stage_2"] * d["rule_share"] + PREP_OPS
    # memory of the search
    d["data_words"] = -(-(d["list_words"] + 256) // 1024) * 1024
    d["data_bytes"] = 32 * d["data_words"]
    d["online_bytes"] = 2 ** 19 + d["data_bytes"]
    d["online_log2"] = math.ceil(math.log2(d["online_bytes"]))
    return d


# =====================================================================================================
# PART C: readers of the result files
# =====================================================================================================
def read(path):
    return path.read_text(encoding="ascii", errors="replace") if path.exists() else None


def need(path):
    text = read(path)
    if text is None:
        raise SystemExit(f"missing {path.relative_to(PKG)} (tools/fetch_h8.py brings the copies of the groundwork's files)")
    return text


def integer(text):
    return int(text.replace(",", ""))


def word(n, capital=False):
    w = WORDS[n] if 0 <= n < len(WORDS) else str(n)
    return w.capitalize() if capital else w


def join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def k_of(beta):
    return bin(rol(int(beta, 16), 12) & 0x7FFFFFFF).count("1")


def program_sha():
    return hashlib.sha256(PROGRAM.read_bytes()).hexdigest()


def chi2_sf(x, k):
    """Upper tail of the chi-square distribution with k degrees of freedom (regularized incomplete gamma)."""
    a, x = k / 2.0, x / 2.0
    if x <= 0:
        return 1.0
    if x < a + 1:                                   # series for the lower part
        term = total = 1.0 / a
        n = a
        for _ in range(10000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        return max(0.0, 1.0 - total * math.exp(-x + a * math.log(x) - math.lgamma(a)))
    b = x + 1 - a                                   # continued fraction for the upper part
    c, dd = 1e300, 1.0 / b
    h = dd
    for i in range(1, 10000):
        an = -i * (i - a)
        b += 2
        dd = an * dd + b
        dd = 1e-300 if abs(dd) < 1e-300 else dd
        c = b + an / c
        c = 1e-300 if abs(c) < 1e-300 else c
        dd = 1.0 / dd
        delta = dd * c
        h *= delta
        if abs(delta - 1) < 1e-15:
            break
    return h * math.exp(-x + a * math.log(x) - math.lgamma(a))


def spread(xs):
    """(mean, variance over mean, chi-square on n - 1, its upper tail) of counts."""
    n, mean = len(xs), sum(xs) / len(xs)
    var = sum((x - mean) ** 2 for x in xs) / (n - 1)
    return mean, var / mean, (n - 1) * var / mean, chi2_sf((n - 1) * var / mean, n - 1)


def read_outcomes():
    """The count from the outcomes with their two factors (evidence/pairs_recount_<eta>.txt, tools/outcomes_h8.py).

    Returns dict: prod {(beta, tau, eps): Fraction}, e1n3 {(beta, tau, eps): (E1, N3)}, part {beta: Fraction},
    sampled {beta: outcomes of the beta through the random-subset branch}, order (betas, heaviest first)."""
    text = need(EVID / f"pairs_recount_{ETA:08x}.txt")
    check = need(EVID / "count_h8.txt")
    if "RESULT: all comparisons hold" not in check:
        raise SystemExit("evidence/count_h8.txt does not end with 'all comparisons hold': run tools/outcomes_h8.py")
    prod, e1n3, sampled, snapped = {}, {}, {}, 0
    for line in text.split("\n"):
        f = line.split()
        if len(f) > 2 and f[0] == "PAIR" and "sampled" in f:
            sampled[f[2]] = int(f[f.index("sampled") + 1])
        elif len(f) > 8 and f[0] == "OUTX":
            key = (f[2], f[3], f[4])
            # The calculator prints E1 through a logarithm (evidence/h8/H8_count.txt, section 8): a printed value within
            # a relative 10^-11 of (small odd) * 2^j is that integer. N3 is printed as an integer and is taken as it is.
            e1 = snap(int(f[6]))
            snapped += e1 != int(f[6])
            e1n3[key] = (e1, int(f[8]))
            prod[key] = Fraction(e1 * int(f[8]), 2 ** 83)
    part = {}
    for (beta, _, _), v in prod.items():
        part[beta] = part.get(beta, 0) + v
    order = sorted(part, key=lambda b_: (-part[b_], b_))
    return dict(prod=prod, e1n3=e1n3, part=part, sampled=sampled, order=order, snapped=snapped)


def read_gpt():
    """The independent recount: ({beta: Fraction}, total, sha of its program, True if the rerun equals the file received)."""
    folder = EVID / "gpt_recount"
    rerun, received = folder / "gpt_sol_parts_A.csv", folder / "as_received_parts_A.csv"
    text = need(rerun)
    parts = {}
    for row in text.strip().split("\n")[1:]:
        f = row.split(",")
        parts[f[0]] = parts.get(f[0], 0) + Fraction(int(f[7]), int(f[8]))
    total_file = need(folder / "gpt_sol_total_A.txt")
    m = re.search(r"R_numerator=(\d+)\s+R_denominator=(\d+)\s+positive_betas=(\d+)\s+parity_checked=(\d+)", total_file)
    total = Fraction(int(m.group(1)), int(m.group(2)))
    if total != sum(parts.values()) or int(m.group(3)) != len(parts):
        raise SystemExit("the independent recount: its total is not the sum of its parts")
    same = received.exists() and received.read_bytes().replace(b"\r\n", b"\n") == rerun.read_bytes().replace(b"\r\n", b"\n")
    log = read(folder / "rerun_all32.log") or ""
    visited = re.search(r"FINAL feasible_betas=(\d+) parity_checked=(\d+)", log)
    return dict(parts=parts, total=total, sha=hashlib.sha256((folder / "gpt_sol_independent_a.rs").read_bytes()).hexdigest(),
                same=same, visited=int(visited.group(1)) if visited else None, checked=int(m.group(4)),
                ended="exit 0" in log)


def read_count_table():
    """Figures of the table of the count, evidence/h8/H8_count.txt (the groundwork's own summary of its files)."""
    text = need(H8 / "H8_count.txt")
    out = {}

    def grab(name, pattern, flags=0):
        m = re.search(pattern, text, flags)
        if not m:
            raise SystemExit(f"evidence/h8/H8_count.txt: no line for {name}")
        out[name] = m.groups()

    grab("valid", r"D11 0a08818b: valid x in all (\d+)")
    grab("k14", r"list counted: every beta with k <= 14: (\d+) betas; no eps .*? (\d+); enumerated completely (\d+); with a part (\d+)")
    grab("outcomes14", r"outcomes that pass the necessary conditions ([\d,]+); with a nonzero E3 count (\d+); of them with a nonzero "
                       r"E1 count \(nonzero product\) (\d+)")
    grab("solver", r"betas finished by the calculator ([\d,]+) of ([\d,]+) valid betas; betas decided by the solver ([\d,]+) "
                   r"\(SAT (\d+), UNSAT ([\d,]+), undecided (\d+)\); SAT models that check in plain arithmetic (\d+) of (\d+)")
    grab("estimates", r"NOT EXACT: betas with an outcome through the random-subset branch of the E3 count or an E1 formula "
                      r"fallback: (\d+) \(sampled outcomes (\d+), formula fallbacks (\d+)\), lightest k (\d+); their parts "
                      r"\(estimates\) add up to ([\d.]+)")
    grab("amc_e1", r"SUMMARY e1: compared (\d+) of (\d+), mean log2\(calculator/ApproxMC\) ([-+][\d.]+), largest \|difference\| "
                   r"([\d.]+) bits, ApproxMC zero (\d+), no answer (\d+)")
    grab("amc_e3", r"SUMMARY e3: compared (\d+) of (\d+), mean log2\(calculator/ApproxMC\) ([-+][\d.]+), largest \|difference\| "
                   r"([\d.]+) bits, ApproxMC zero (\d+), no answer (\d+)")
    grab("top16", r"the 16 together: ([\d,.]+) = ([\d.]+) of the count")
    grab("sys", r"\[check_sys.txt\] SUMMARY sys: betas (\d+), SAT (\d+), UNSAT (\d+), undecided (\d+); SAT models that are solutions "
                r"in plain arithmetic (\d+) of (\d+)")
    grab("bf_e1", r"\[check_bf8.txt\] delta \+-8: E1 exact count against brute force at 8-bit words: (\d+) cases, (\d+) outcomes with "
                  r"solutions: (\d+) equal, (\d+) different; zero outcomes sampled: (\d+) agree, (\d+) disagree")
    grab("bf_e1b", r"\[check_bf8.txt\] delta \+-8, seed 808, 60 cases: E1 exact count against brute force at 8-bit words: (\d+) cases, "
                   r"(\d+) outcomes with solutions: (\d+) equal, (\d+) different")
    grab("bf_e3", r"\[check_bf8.txt\] E3 count n3x against brute force at 8-bit words: (\d+) cases, outcomes with solutions (\d+): "
                  r"(\d+) equal, (\d+) different .*?empty outcomes sampled: (\d+) agree, (\d+) disagree")
    grab("sampler_sum", r"the same over the 16 seeds \(the betas share their seeds\): mean of the sums ([\d,]+), standard error "
                        r"([\d,]+), deviation ([-+][\d.]+); smallest and largest sum of a seed ([\d,]+), ([\d,]+)")
    grab("sampler_exact", r"\[confirm_H8.txt\] sampler, four betas together: ([\d,]+) against ([\d,]+) counted")
    out["sampler"] = {m.group(1): (integer(m.group(2)), integer(m.group(3)), m.group(4)) for m in re.finditer(
        r"^\s+([0-9a-f]{8})\s+\d+\s+\d+\s+[\d,.]+\s+[\d.]+\s+([\d,]+) \+-\s*([\d,]+)\s+([-+][\d.]+)\s*$", text, re.M)}
    return out


def read_sat(n):
    """The solver answers for the rule with n conditions: (first {key: (all answer, model ok, violate answer, model
    ok and violating)}, [(solver, answers equal, base satisfiable, outcomes)] of the second formula, EXAMPLE and
    SOLUTION lines as dicts)."""
    text = need(EVID / f"rule_a_sat_{ETA:08x}_rule{n}.txt")
    first, lines = {}, {}
    for line in text.split("\n"):
        f = line.split()
        if len(f) >= 5 and f[0] in ("ALL", "VIOLATE"):
            entry = first.setdefault((f[1], f[2], f[3]), {})
            entry[f[0]] = (f[4], " solution 1" in line, " rule_A 1" in line)
        elif f and f[0] in ("EXAMPLE", "SOLUTION"):
            lines[f[0]] = dict(beta=f[1], tau=f[2], eps=f[3], **{f[i]: f[i + 1] for i in range(4, len(f) - 1, 2)})
    second = []
    for solver in ("cadical", "cryptominisat5"):
        other = read(EVID / f"rule_a_sat2_{solver}_{ETA:08x}_rule{n}.txt")
        if other is None:
            continue
        ans, base = {}, 0
        for line in other.split("\n"):
            f = line.split()
            if len(f) >= 5 and f[0] == "VIOLATE":
                ans[(f[1], f[2], f[3])] = f[4]
            elif len(f) >= 5 and f[0] == "BASE":
                base += f[4] == "SAT" and " solution 1" in line
        version = re.search(r"# solver version: (.*)", other)
        second.append((solver, sum(ans.get(k) == v["VIOLATE"][0] for k, v in first.items()), base, len(ans),
                       re.sub(r"^c\s+", "", version.group(1).strip()) if version else ""))
    return first, second, lines


def rule_count(n, outcomes):
    """The conservative count of the rule with n conditions and what belongs to it (see tools/conservative_h8.py)."""
    first, second, lines = read_sat(n)
    prod, sampled = outcomes["prod"], outcomes["sampled"]
    if set(first) != set(prod):
        raise SystemExit(f"rule {n}: the SAT answers are not for the outcomes of the count: run tools/rule_a_sat.py {n}")
    for key, v in first.items():
        a, w = v.get("ALL", ("?", False, False)), v.get("VIOLATE", ("?", False, False))
        if a[0] != "SAT" or not a[1] or w[0] not in ("SAT", "UNSAT") or (w[0] == "SAT" and (not w[1] or w[2])):
            raise SystemExit(f"rule {n}: a SAT answer is missing or a model failed its check for outcome {key}")
    for solver, same, base, total, _ in second:
        if same != len(first) or total != len(first) or base != len(first):
            raise SystemExit(f"rule {n}: {solver} with the second formula does not give the same answers for every outcome")
    estimated = {b_ for b_, s in sampled.items() if s}
    exact = {k: v for k, v in prod.items() if k[0] not in estimated}
    violable = {k for k, v in first.items() if v["VIOLATE"][0] == "SAT"}
    kept = {k: v for k, v in exact.items() if k not in violable}
    return dict(first=first, second=second, lines=lines, estimated=estimated, exact=exact, violable=violable, kept=kept,
                count=sum(kept.values()), full=sum(exact.values()), models_passing=sum(v["ALL"][2] for v in first.values()))


def selftest():
    """The JSON line of the self-test of the program in the package (run now; it takes a few seconds)."""
    done = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), "--selftest", *SELFTEST], stdin=subprocess.DEVNULL, capture_output=True)
    if done.returncode != 0:
        raise SystemExit("the self-test of experiments/halfsearch.py does not end with exit status 0:\n" + done.stdout.decode()[:600])
    return json.loads(done.stdout.decode("ascii"))


def read_big_selftest(n):
    """The long self-test of the rule with n conditions, if it is for the program as it is now with that rule; else None."""
    text = read(EVID / f"selftest_1000000_rule{n}_{BIG_SELFTEST_SEED}.json")
    if not text:
        return None
    head, _, body = text.partition("\n")
    m = re.match(r"PROGRAM sha256 ([0-9a-f]{64}) RULE_CONDITIONS (\d) \(package: (\d)\) copy sha256 ([0-9a-f]{64}) exit (\d+)", head)
    if not m or int(m.group(2)) != n or m.group(5) != "0":
        return None
    # the run was made on a copy of the program whose only difference is the line RULE_CONDITIONS; for the rule of
    # the package the copy is the program itself
    if n == RULE_CONDITIONS and not (m.group(1) == m.group(4) == program_sha()):
        return None
    try:
        r = json.loads(body.strip().split("\n")[0])
    except ValueError:
        return None
    good = (r["lanes_right"] == r["lanes_checked"] == 7 * r["cases"] and r["counts_equal_table"] and r["same_counts_in_every_case"]
            and r["sums_below_bounds"] and r["rule_conditions"] == n and r["registers"] <= 16
            and (r["stage_a"]["operations"], r["stage_a"]["loads"]) == STAGE_A_BY_RULE[n]
            and (r["stage_2"]["operations"], r["stage_2"]["loads"]) == (STAGE_2_OPS, STAGE_2_LOADS))
    return r if good else None


def read_rule_share_h8(layout=False, run=None):
    """The result of tools/rule_share_h8.py for RULE_SHARE_H8_RUN (or, with layout, for RULE_SHARE_H8_LAYOUT), per
    number of conditions; None if it is not usable.

    It is used only while the program and the tool have the SHA-256 written in the first line of the file, all
    anchors are equal and the counts are for the class of the package (members and batches per context). Under
    "spread" it has, per rule, the share of the trials of one context in units of 2^-n: mean, standard deviation
    between contexts, smallest, largest, and (layout) the number of pairs, the standard error from the scatter of the
    pair means and the means of the quadruples."""
    d = derive()
    if layout:
        quads, pairs, values, seed = RULE_SHARE_H8_LAYOUT
        contexts = quads * pairs * values
        path = EVID / f"rule_share_h8_layout_{quads}x{pairs}x{values}_{seed}.txt"
    else:
        contexts, seed = run or RULE_SHARE_H8_RUN
        path = EVID / f"rule_share_h8_{contexts}_{seed}.txt"
    if not path.exists():
        return None
    lines = path.read_text(encoding="ascii").split("\n")
    head = re.match(r"PROGRAM sha256 ([0-9a-f]{64}) TOOL rule_share_h8.py sha256 ([0-9a-f]{64})$", lines[0])
    info = re.match(r"contexts (\d+) \(seed text (.+?)\), members (\d+), trials (\d+), batches (\d+) \((\d+) per context, .*?: "
                    r"(\d+) of (\d+) equal;", lines[1])
    tool = hashlib.sha256((TOOLS / "rule_share_h8.py").read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    if not head or not info or head.group(1) != program_sha() or head.group(2) != tool:
        return None
    c, _, members, trials, batches, per, good, anchors = info.groups()
    if (int(c), int(members), int(per)) != (contexts, d["members"], d["list_words"]) or good != anchors or int(anchors) < 1 \
            or int(trials) != contexts * d["members"] or int(batches) != contexts * d["list_words"]:
        return None
    if layout and (f"LAYOUT quadruples of seed words (S11, S4, X13, w0) {quads} | pairs (vc, vd) per quadruple {pairs}, vd below "
                   f"2^{d['d_bits']} | consecutive values of X14 per pair {values}, from a random start") not in lines:
        return None
    out = {"contexts": contexts, "trials": int(trials), "batches": int(batches), "anchors": int(anchors), "spread": {}}
    if layout:
        out.update(quads=quads, pairs=pairs, values=values)
    for line in lines[3:]:
        m = re.match(r"RULE (\d) \| (\d+) \| [0-9.]+ \| 2\^-([0-9.]+) \| (\d+) \| ([0-9.]+) \| ([0-9.]+) \| \S+ = ([0-9.]+) \| "
                     r"([0-9.]+) \(context \d+\) ([0-9.]+) \(context \d+\) \| ([0-9.]+)$", line)
        if m:
            out[int(m.group(1))] = dict(passes=int(m.group(2)), log2=float(m.group(3)), entered=int(m.group(4)),
                                        largest=float(m.group(8)), smallest=float(m.group(9)), largest_rate=float(m.group(10)))
        m = re.match(r"SPREAD (\d) \| share of the trials of one context over 2\^-\d: mean ([\d.]+) \| standard deviation between "
                     r"contexts ([\d.]+) \| smallest ([\d.]+) largest ([\d.]+)(?: \| standard error of the mean ([\d.]+))?"
                     r"(?: \| pair means: (\d+), smallest ([\d.]+) largest ([\d.]+), standard error of the mean from their scatter "
                     r"([\d.]+) \| quadruple means: ([\d. ]+))?$", line)
        if m:
            out["spread"][int(m.group(1))] = dict(
                mean=float(m.group(2)), sd=float(m.group(3)), low=float(m.group(4)), high=float(m.group(5)),
                se=float(m.group(6) or m.group(10)), pairs=int(m.group(7) or 0),
                quads=[float(v) for v in (m.group(11) or "").split()])
    return out if all(n in out and n in out["spread"] for n in RULES) else None


def sha_of(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_e3_share():
    """The exact share, under M, of the listed partial E3 events whose h1 satisfies each rule (evidence/
    e3_rule_share_h8.txt, tools/e3_rule_share_h8.py): events, {n: Fraction}, the probability of the event per trial."""
    text = need(EVID / "e3_rule_share_h8.txt")
    head = re.match(r"INPUT evidence/h8/e3p_expected_H8.txt sha256 ([0-9a-f]{64})", text)
    m = re.search(r"^SHARE events (\d+) equal (\d+) count (\d+) rule4 (\d+) rule5 (\d+) rule6 (\d+)$", text, re.M)
    if not head or not m or head.group(1) != sha_of(H8 / "e3p_expected_H8.txt") or m.group(1) != m.group(2):
        raise SystemExit("evidence/e3_rule_share_h8.txt is not for the list of events as it is, or a count differs: run "
                         "tools/e3_rule_share_h8.py")
    count = int(m.group(3))
    return dict(events=int(m.group(1)), share={n: Fraction(int(m.group(n)), count) for n in (4, 5, 6)},
                p_event=Fraction(count, 2 ** 115))


def read_n3_rule():
    """The exact count of the E3 side split by the rule (evidence/n3_rule_h8.txt, tools/n3_rule_h8.py)."""
    text = need(EVID / "n3_rule_h8.txt")
    head = re.match(r"INPUT evidence/pairs_recount_830303cf.txt sha256 ([0-9a-f]{64})", text)
    same = re.search(r"N3 of this enumeration equal to the calculator's N3: (\d+) of (\d+) outcomes of the betas counted in full; "
                     r"(\d+) of (\d+) outcomes of the betas that hold estimates", text)
    tot = re.search(r"count of all solutions with this enumeration's N3 and the calculator's E1: ([\d,.]+) .*?the betas with "
                    r"estimates here: ([\d.]+)", text)
    if not head or not same or not tot or head.group(1) != sha_of(EVID / f"pairs_recount_{ETA:08x}.txt"):
        raise SystemExit("evidence/n3_rule_h8.txt is not for the outcome file as it is: run tools/n3_rule_h8.py")
    out = dict(same=tuple(int(v) for v in same.groups()), total=float(tot.group(1).replace(",", "")), estimates=float(tot.group(2)))
    for m in re.finditer(r"rule (\d): outcomes whose every solution satisfies the rule \(N3 = N3_rule\), by this count: (\d+); the "
                         r"solver files say UNSAT for (\d+); the two sets are equal: (\w+); of them in betas with estimates: (\d+)\n"
                         r"\s+conservative count \(kept outcomes, betas in full\): ([\d,.]+); exact rate of the solutions that "
                         r"satisfy the rule under M, r_A: betas in full ([\d,.]+), all (\d+) betas ([\d,.]+)", text):
        out[int(m.group(1))] = dict(kept=int(m.group(2)), unsat=int(m.group(3)), equal=m.group(4) == "True", est=int(m.group(5)),
                                    cons=float(m.group(6).replace(",", "")), r_full=float(m.group(7).replace(",", "")),
                                    betas=int(m.group(8)), r_all=float(m.group(9).replace(",", "")))
    if any(n not in out for n in RULES):
        raise SystemExit("evidence/n3_rule_h8.txt does not have the three rules")
    return out


def read_drat():
    """The third formula, the DRAT proofs of the kept outcomes and the controls of the checker (tools/rule_formula3_h8.py,
    rule_drat_h8.py, rule_drat_control_h8.py; they are written for the rule with five conditions). None if a file is
    missing."""
    f3, proofs, control = read(EVID / "rule_formula3_h8.txt"), read(EVID / "rule_drat_h8.txt"), read(EVID / "rule_drat_control_h8.txt")
    if not (f3 and proofs and control):
        return None
    a = re.search(r"SAT \(reviewer's formula, kissat, \d+ workers, \d+ s\): base satisfiable (\d+) of (\d+), models that are solutions "
                  r"with Y4 in the class (\d+)", f3)
    b = re.search(r"SAT second question .*?: UNSAT (\d+), SAT (\d+) \(models that are solutions and violate rule A: (\d+)\), undecided "
                  r"(\d+); answers equal to the package's: (\d+) of (\d+); reviewer's kept set = package's kept set: (\w+)", f3)
    enc = re.search(r"ENCODING: .*? for (\d+) of (\d+) random inputs; .*? right on (\d+) of 64 bit patterns", proofs)
    pr = re.search(r"PROOFS: kept outcomes (\d+) \(sum ([\d.]+)\); proofs verified by the reviewer's checker (\d+), carrying ([\d.]+) "
                   r"of the count that the claim uses; not verified (\d+); clauses checked in all (\d+); largest proof (\d+)", proofs)
    trim = re.search(r"PROOFS: drat-trim (is not installed|verified (\d+) of (\d+))", proofs)
    if not (a and b and enc and pr and trim):
        return None
    keys = set(re.findall(r"^PROOF ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) adds [\d.]+ VERIFIED ", proofs, re.M))
    return dict(base=(int(a.group(1)), int(a.group(2)), int(a.group(3))), unsat=int(b.group(1)), sat=int(b.group(2)),
                sat_ok=int(b.group(3)), undecided=int(b.group(4)), equal=(int(b.group(5)), int(b.group(6))), same_set=b.group(7) == "True",
                encoding=(int(enc.group(1)), int(enc.group(2)), int(enc.group(3))), kept=int(pr.group(1)), verified=int(pr.group(3)),
                carried=float(pr.group(4)), failed=int(pr.group(5)), clauses=int(pr.group(6)), largest=int(pr.group(7)),
                trim=None if trim.group(1) == "is not installed" else (int(trim.group(2)), int(trim.group(3))), keys=keys,
                controls=len(re.findall(r"proof against its formula: VERIFIED \(\d+ clauses\); .*?formula without it is SAT and the same "
                                        r"proof against it: NOT VERIFIED .*?first half of the proof: NOT VERIFIED", control)),
                controls_ok="CONTROLS: checker accepts the right proof and rejects both wrong ones in all cases" in control)


def read_share_review():
    """The reviewing agent's measurement of the share of the trials that satisfy the rules, run again
    (evidence/rule_share_review_h8.txt, tools/rule_share_review_h8.py). Per block a..d and rule n."""
    text = need(EVID / "rule_share_review_h8.txt")
    c0 = re.match(r"0\. construction from the text on real messages \(organizer's 2-round hash\): \{'trials': (\d+), 'lengths': (\d+), "
                  r"'zero': (\d+), 'half': (\d+), 'y4': (\d+), 'h1': (\d+), 'own': (\d+), 'pin': (\d+), 'eta': (\d+)\}", text)
    if not c0:
        raise SystemExit("evidence/rule_share_review_h8.txt: the check on real messages is missing")
    trials, lengths, zero, half, y4, h1, own, pin, eta = (int(v) for v in c0.groups())
    if not (trials == lengths == zero == half == y4 == own == pin) or h1 < 1 or eta < 1:
        raise SystemExit("evidence/rule_share_review_h8.txt: a check on real messages fails")
    out = dict(trials=trials)
    for key in ("a", "b"):
        line = re.search(rf"^{key}\. [^\n]*?: (\d+) contexts \| ([^\n]*)$", text, re.M)
        out[key] = {"contexts": int(line.group(1))}
        for m in re.finditer(r"rule (\d): mean ([\d.]+) \+- ([\d.]+) of 2\^-\d \(s\.d\. of one context ([\d.]+), min ([\d.]+), max "
                             r"([\d.]+)\)", line.group(2)):
            out[key][int(m.group(1))] = dict(mean=float(m.group(2)), se=float(m.group(3)), sd=float(m.group(4)), low=float(m.group(5)),
                                             high=float(m.group(6)))
    for key in ("c", "d"):
        out[key] = {}
        for m in re.finditer(rf"^{key}\. [^\n]*? \| rule (\d): (\d+) sets x (\d+) contexts; mean over all ([\d.]+) of 2\^-\d; set means "
                             r"from ([\d.]+) to ([\d.]+) \(standard error of one set mean ([\d.]+)\); homogeneity chi-square [\d.]+ on "
                             r"\d+, p ([\d.]+)", text, re.M):
            out[key][int(m.group(1))] = dict(sets=int(m.group(2)), per=int(m.group(3)), mean=float(m.group(4)), low=float(m.group(5)),
                                             high=float(m.group(6)), se=float(m.group(7)), p=float(m.group(8)))
    if any(n not in out[key] for key in "abcd" for n in RULES):
        raise SystemExit("evidence/rule_share_review_h8.txt does not have the four blocks for the three rules")
    return out


def read_layout_review():
    """The second review program's count of rule A over whole contexts, run again (evidence/rule_layout_review_h8.txt,
    tools/rule_layout_review_h8.py). None if the file is missing or does not have the lines that are read.

    lanes: lanes compared with h1 of the real message, all right. contexts: independent contexts of part A.
    r4, r5: mean share over 2^-4 or 2^-5, (r5 only: log2), standard deviation between contexts in percent of the mean,
    smallest, largest. batches: mean, smallest, largest share of the batches of one context. values: consecutive values
    of X14 per pair in part B. pairs: per pair mean, low, high (five conditions, over 2^-5) and the share of the
    batches with its largest value. six: smallest and largest pair mean, their scatter in percent, the number of
    contexts and the scatter that independent contexts would give."""
    text = read(EVID / "rule_layout_review_h8.txt")
    if not text:
        return None
    lanes = re.search(r"lanes compared with rule A on h1 of the complete compression of the real message A: (\d+) of (\d+) right", text)
    part_a = re.search(r"^A\. (\d+) independent contexts, all 524,288 members each", text, re.M)
    r4 = re.search(r"four conditions: mean share ([\d.]+) x 2\^-4, per context sd ([\d.]+)% of the mean, range ([\d.]+) to ([\d.]+) x 2\^-4", text)
    r5 = re.search(r"five conditions: mean share ([\d.]+) x 2\^-5 \(2\^-([\d.]+)\), per context sd ([\d.]+)% of the mean, range ([\d.]+) to "
                   r"([\d.]+) x 2\^-5", text)
    rb = re.search(r"batches that hold a trial satisfying rule A: mean share ([\d.]+), range ([\d.]+) to ([\d.]+)", text)
    part_b = re.search(r"^B\. layout of 6\.4: seed words held, vd < 2\^19, (\d+) consecutive values of X14 per pair", text, re.M)
    pairs = re.findall(r"seed set \d+ pair \d+: five conditions mean ([\d.]+) x 2\^-5 \(sd between contexts [\d.]+%, range ([\d.]+) to "
                       r"([\d.]+)\); four conditions mean [\d.]+ x 2\^-4; batches entering stage 2 ([\d.]+) \(max ([\d.]+)\)", text)
    six = re.search(r"pair means, five conditions: ([\d.]+) to ([\d.]+) x 2\^-5, sd ([\d.]+)%; expected from the between-context sd of "
                    r"part A over (\d+) contexts: ([\d.]+)%", text)
    if not (lanes and part_a and r4 and r5 and rb and part_b and pairs and six) or lanes.group(1) != lanes.group(2) \
            or derive()["members"] != 524288 or derive()["d_bits"] != 19:
        return None
    return dict(lanes=int(lanes.group(1)), contexts=int(part_a.group(1)), r4=tuple(float(v) for v in r4.groups()),
                r5=tuple(float(v) for v in r5.groups()), batches=tuple(float(v) for v in rb.groups()), values=int(part_b.group(1)),
                pairs=[dict(mean=float(p[0]), low=float(p[1]), high=float(p[2]), batch=float(p[3]), batch_max=float(p[4])) for p in pairs],
                six=(float(six.group(1)), float(six.group(2)), float(six.group(3)), int(six.group(4)), float(six.group(5))))


def read_prep():
    """(operations, loads, stores) of the work per value of X14 (evidence/prep_count.txt), for the program as it is."""
    text = need(EVID / "prep_count.txt")
    head = re.match(r"PROGRAM sha256 ([0-9a-f]{64})", text)
    m = re.search(r"total (\d+) operations \+ (\d+) loads \+ (\d+) stores = (\d+)", text)
    if not head or head.group(1) != program_sha() or not m or "RESULT: the count holds and PREP_OPS covers it" not in text:
        raise SystemExit("evidence/prep_count.txt is not for the program as it is: run tools/prep_count.py")
    ops, loads, stores, total = (int(v) for v in m.groups())
    if ops + loads + stores != total or total > PREP_OPS:
        raise SystemExit("the counted work per value of X14 is above PREP_OPS")
    return ops, loads, stores


def read_lane_bound():
    text = read(EVID / "lane_bound.txt") or ""
    head = re.match(r"PROGRAM sha256 ([0-9a-f]{64})", text)
    return bool(head and head.group(1) == program_sha() and "RESULT: all bounds hold" in text
                and f"rule A with {RULE_CONDITIONS} conditions" in text)


GPU_STATS = ("rule on h1 passes", "listed beta (any)", "beta and listed tau (any)", "listed E1 outcome (any)",
             "listed partial E3 event (any)")


def read_gpu():
    """What the text quotes of evidence/h8/H8_gpu_compare.txt: the deep counts against the exact expectations, the
    comparisons real against model, and the list of everything beyond three standard deviations."""
    text = need(H8 / "H8_gpu_compare.txt")
    lines = text.split("\n")
    out = {"deep": {}, "pairs": [], "beyond": []}
    block = None
    start = next(i for i, l in enumerate(lines) if l.startswith("6. DEEP COUNTS"))
    end = next(i for i, l in enumerate(lines) if l.startswith("7. EVERYTHING BEYOND"))
    for line in lines[start:end]:
        m = re.match(r"   (\S.*?): 2\^([\d.]+) trials", line)
        if m:
            block = out["deep"].setdefault(m.group(1), {"log2": float(m.group(2))})
            continue
        m = re.match(r"      (.+?)\s+observed\s+(\d+)\s+exact\s+([\d.]+)\s+z\s+([-+][\d.]+)\s+p\s+(\S+)", line)
        if m and block is not None:
            block[m.group(1).strip()] = (int(m.group(2)), float(m.group(3)), float(m.group(4)), m.group(5))
            continue
        m = re.match(r"      listed partial E3 events whose h1 passes the rule: (\d+) of (\d+)", line)
        if m and block is not None:
            block["e3 pass"] = (int(m.group(1)), int(m.group(2)))
        m = re.match(r"      ([0-9a-f]{8})\s+\d+ /\s+[\d.]+ / [-+][\d.]+\s+\d+ /\s+[\d.]+ / [-+][\d.]+\s+(\d+) /\s+([\d.]+) / p ([\d.]+)", line)
        if m:
            out.setdefault("per_beta", []).append((m.group(1), int(m.group(2)), float(m.group(3))))
    m = re.search(r"7\. EVERYTHING BEYOND 3 STANDARD DEVIATIONS \(p < 0.0027\); tests made: (\d+), so about ([\d.]+) such lines", text)
    out["tests"], out["chance"] = int(m.group(1)), float(m.group(2))
    out["beyond"] = [l.strip() for l in lines[end + 1:] if re.match(r"\s+\S+ \| ", l)]
    # sections "REAL 2^a AGAINST MODEL 2^b (independent contexts ..)": every statistic with a z of A against B
    for i, line in enumerate(lines):
        m = re.match(r"(\w+)\. REAL 2\^(\d+) AGAINST MODEL 2\^(\d+) \(independent contexts", line)
        if not m:
            continue
        rows = []
        for l in lines[i + 3:]:
            if not l.startswith("   ") or not l.strip():
                break
            r = re.match(r"   (.+?)\s{2,}(\d+)\s+(\d+)\s+([-+]\d+\.\d+)", l)
            if r:
                rows.append((r.group(1).strip(), int(r.group(2)), int(r.group(3)), float(r.group(4))))
        out["pairs"].append((int(m.group(2)), int(m.group(3)), rows))
    return out


STAT_NAMES = {"beta and listed tau (any)": "listed beta with a listed tau", "listed beta (any)": "listed beta",
              "listed E1 outcome (any)": "listed E1 outcome", "listed partial E3 event (any)": "listed partial E3 event",
              "word 0 zero": "the first residual word zero", "word 1 zero": "the second residual word zero",
              "word 2 zero": "the third residual word zero", "word 3 zero": "the fourth residual word zero",
              "E1 requires the eta of Y4": "passes of the E1 test", "rule on h1 passes": "the first four conditions of rule A"}


def stat_name(name):
    """A statistic of the comparing program in the words of the text."""
    if name in STAT_NAMES:
        return STAT_NAMES[name]
    m = re.fullmatch(r"trailing zeros = (\d+)", name)
    if m:
        return f"residuals with exactly {m.group(1)} trailing zero bit{'s' if m.group(1) != '1' else ''}"
    m = re.fullmatch(r"trailing zeros >= (\d+)", name)
    if m:
        return f"residuals with at least {m.group(1)} trailing zero bits"
    return name


RUNS = H8 / "runs"                # the raw result files of the runs on the graphics card (tools/fetch_h8.py)
RUN_PATTERNS = dict(
    head=r"STAT (real|model) trials 2\^([\d.]+)\s+bad (\d+)",
    early=r"early test passes: (\d+) .*?E1 requires the eta of Y4: (\d+) .*?contradictions \(must be 0\): (\d+)",
    e1=r"trials with a listed beta (\d+) .*?trials with a listed E1 outcome (\d+)",
    e3=r"trials with a listed partial E3 event (\d+)",
    rule=r"rule on h1 \(bits 0=0, 1=1, 16=0, 17=0\): passes (\d+) .*?listed partial E3 events that pass it: (\d+)")


def read_run(name):
    """The counts of one run from its raw result file; the build stops if the file is missing or not complete."""
    text = read(RUNS / f"{name}.txt")
    m = {k: re.search(p, text or "") for k, p in RUN_PATTERNS.items()}
    if not all(m.values()):
        raise SystemExit(f"evidence/h8/runs/{name}.txt is missing or not complete: run tools/fetch_h8.py")
    log2 = float(m["head"].group(2))
    if abs(log2 - round(log2)) > 1e-9 or int(m["head"].group(3)) or int(m["early"].group(3)):
        raise SystemExit(f"evidence/h8/runs/{name}.txt: not a power of two of trials, or a bad trial or a contradiction is reported")
    per = re.findall(r"E1 beta ([0-9a-f]{8}): trials \d+\s+with a listed tau (\d+)\s+with a listed outcome (\d+)", text)
    outer = re.search(r"layout run \d+: outer words (.*?), X14 from ([0-9a-f]{8}), (\d+) values of X14, each with all (\d+) members", text)
    line = re.search(r"^RUN (\S+): \S+ (?:real|model)((?: \S+)*?) ; exit (\d+) ;", text, re.M)
    if line and (line.group(1) != name or line.group(3) != "0"):
        raise SystemExit(f"evidence/h8/runs/{name}.txt: its RUN line is of another run or reports an exit status other than 0")
    return dict(name=name, kind=m["head"].group(1), log2=round(log2), trials=2 ** round(log2), early=int(m["early"].group(1)),
                e1pass=int(m["early"].group(2)), beta=int(m["e1"].group(1)), outcome=int(m["e1"].group(2)), e3=int(m["e3"].group(1)),
                rule=int(m["rule"].group(1)), joint=int(m["rule"].group(2)), tau=sum(int(v[1]) for v in per),
                per_beta={v[0]: int(v[2]) for v in per}, outer=outer.groups() if outer else None,
                args=line.group(2).split() if line else None)


def read_runs():
    """Every finished run on the graphics card, pooled by the data module from the raw files: runs with independent
    contexts (2^40, 2^42, 2^45 and the later runs of 2^45 with seeds 8201.., as far as tools/fetch_h8.py found them
    finished), the 24 layout runs, the 8 spread runs and the three runs of draws from M."""
    seeds = sorted(p.stem for p in RUNS.glob("h8_real45_seed*.txt"))
    out = dict(independent=[read_run(n) for n in ["h8_real40", "h8_real42", "h8_real45"] + seeds],
               layout=[read_run(f"h8_layout_run{i}") for i in range(1, 25)],
               spread=[read_run(f"h8_spread_run{i}") for i in range(1, 9)],
               model=[read_run(n) for n in ("h8_model40", "h8_model42", "h8_model44")],
               seeds=[s.rsplit("seed", 1)[1] for s in seeds])
    if any(r["kind"] != ("model" if group == "model" else "real") for group in ("independent", "layout", "spread", "model")
           for r in out[group]) or any(r["log2"] != 40 for r in out["layout"] + out["spread"]):
        raise SystemExit("a run file is not of the kind or the size of its group")
    members = str(derive()["members"])
    if any(not r["outer"] or r["outer"][2:] != (str(2 ** 21), members) for r in out["layout"] + out["spread"]) \
            or len({r["outer"][0] for r in out["layout"]}) != len(out["layout"]):
        raise SystemExit("a layout or spread run does not have 2^21 values of X14 with all members, or two layout runs share a sextuple")
    for a, b_ in zip(out["layout"], out["spread"]):
        # a spread run: the sextuple, the first X14 and the arguments of its layout run, and one more argument, the step
        if a["outer"] != b_["outer"] or not a["args"] or not b_["args"] or b_["args"][:-1] != a["args"] or int(b_["args"][-1], 16) % 2 != 1:
            raise SystemExit("a spread run is not its layout run with one more argument, an odd step of X14")
    return out


def read_deep_expected():
    """Exact probabilities per trial under M of the listed events (evidence/h8/h8_deep_expected.txt)."""
    text = need(H8 / "h8_deep_expected.txt")
    m = re.search(r"^SUM beta (\S+) bt (\S+) out (\S+) e3 (\S+) rule (\S+)", text, re.M)
    rows = [l.split() for l in text.split("\n") if l.startswith("BETA ")]
    if not m or not rows:
        raise SystemExit("evidence/h8/h8_deep_expected.txt does not have the lines that are read")
    return dict(beta=float(m.group(1)), tau=float(m.group(2)), outcome=float(m.group(3)), e3=float(m.group(4)),
                per_beta=[(f[2], float(f[9])) for f in rows])


def zbin(k, n, p):
    """Deviation of a binomial count k of n at probability p, in standard deviations."""
    return (k - n * p) / math.sqrt(n * p * (1 - p))


def poisson_two_sided(k, mu):
    """Probability of a Poisson count at least as unlikely as k when the mean is mu."""
    def pk(j):
        return math.exp(-mu + j * math.log(mu) - math.lgamma(j + 1))
    p0 = pk(k)
    return min(1.0, sum(pk(j) for j in range(0, int(mu * 6) + 60) if pk(j) <= p0 * (1 + 1e-12)))


def rule_runs(rows, context_variance, members):
    """The four-condition rule over runs of equal size: largest relative distance of a run from 2^-4 (parts in
    100,000), runs below, variance over binomial variance, the pooled deviation in binomial standard deviations, in
    standard errors of the runs' own scatter, and with the variance between independent contexts."""
    n, k = rows[0]["trials"], len(rows)
    counts = [r["rule"] for r in rows]
    expect, binvar, mean = n / 16, n * 15 / 256, sum(counts) / k
    var = sum((c - mean) ** 2 for c in counts) / (k - 1)
    if any(r["trials"] != n for r in rows):
        raise SystemExit("runs of different sizes in one group")
    return dict(runs=k, parts=max(abs(c / expect - 1) for c in counts) * 1e5, below=sum(c < expect for c in counts),
                disp=var / binvar, pooled=(sum(counts) - k * expect) / math.sqrt(k * binvar),
                own=(mean - expect) / math.sqrt(var / k),
                indep=(sum(counts) - k * expect) / math.sqrt(k * (n / members) * context_variance))


def read_ctx():
    """Per-context statistics of the four-condition rule (evidence/h8/h8_ctx_independent.txt)."""
    text = need(H8 / "h8_ctx_independent.txt")
    head = re.search(r"CTX (\d+) independent contexts \(seven random words, seed (\d+)\); (\d+) members each; bad (\d+)", text)
    rule = re.search(r"CTX rule on h1 passes\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+([\d.]+)", text)
    beta = re.search(r"CTX listed beta \(any\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", text)
    bit = re.search(r"CTX h1 bit 0 = 0 \(one of the four rule bits\)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)", text)
    rate = re.search(r"CTX rule on h1: mean pass rate 2\^-([\d.]+)", text)
    if not (head and rule and beta and bit and rate):
        raise SystemExit("evidence/h8/h8_ctx_independent.txt does not have the lines that are read")
    return dict(contexts=int(head.group(1)), members=int(head.group(3)), mean=float(rule.group(1)), var=float(rule.group(2)),
                binomial=float(rule.group(3)), dispersion=float(rule.group(4)), low=int(rule.group(5)), high=int(rule.group(6)),
                sd_rel=float(rule.group(7)), beta_dispersion=float(beta.group(4)), bit_dispersion=float(bit.group(4)),
                bit_low=int(bit.group(5)), bit_high=int(bit.group(6)), rate=float(rate.group(1)))


def read_ctx_run(kind):
    """Per-context statistics of the four-condition rule for contexts of the sextuple of layout run 1, with consecutive
    values of X14 (kind "consecutive") or values a fixed odd step apart ("spread"): evidence/h8/h8_ctx_run1_<kind>.txt."""
    text = need(H8 / f"h8_ctx_run1_{kind}.txt")
    head = re.search(r"CTX (\d+) contexts: outer words of layout run 1, X14 = ([0-9a-f]{8}) \+ i \* ([0-9a-f]{8}); (\d+) members each; "
                     r"bad (\d+)", text)
    rule = re.search(r"CTX rule on h1 passes\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)\s+(\d+)\s+(\d+)\s+([\d.]+)", text)
    if not (head and rule) or int(head.group(5)) or int(head.group(3), 16) % 2 != 1 \
            or (int(head.group(3), 16) == 1) != (kind == "consecutive"):
        raise SystemExit(f"evidence/h8/h8_ctx_run1_{kind}.txt does not have the lines that are read")
    return dict(contexts=int(head.group(1)), start=head.group(2), members=int(head.group(4)), mean=float(rule.group(1)),
                dispersion=float(rule.group(4)), low=int(rule.group(5)), high=int(rule.group(6)))


def read_host():
    """Checks of the GPU program and of the reference on real messages: dict of counts, None where a line is missing."""
    check = need(H8 / "h8_check.txt")
    ref = need(H8 / "h8_ref_check.txt")
    out = {}
    m = re.search(r"CHECK (\d+) of (\d+) class-search trials", check)
    out["gpu_check"] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r"VECTORS host: message words equal (\d+), digest of A \(55 bytes\) equal (\d+), digest of B \(63 bytes\) equal (\d+)", check)
    out["vectors"] = tuple(int(v) for v in m.groups()) if m else None
    m = re.search(r"CHECK member order: (\d+) of (\d+)", check)
    out["order"] = (int(m.group(1)), int(m.group(2))) if m else None
    m = re.search(r"hash2 vs organizer verifier.blake3\(.,2\) on (\d+) random msgs \(len 0..64\): all_equal=(\w+)", ref)
    out["ref_hash"] = (int(m.group(1)), m.group(2) == "True") if m else None
    m = re.search(r"triples: (\d+) contexts x (\d+) members = (\d+) total", ref)
    counts = dict(re.findall(r"^\s+(\w+)\s+= (\d+) / \d+$", ref, re.M))
    out["ref_triples"] = (int(m.group(3)), int(m.group(1)), all(int(v) == int(m.group(3)) for v in counts.values()), len(counts)) if m else None
    full = need(H8 / "H8_fullcheck.txt")
    m = re.search(r"lanes fully right \(half AND n-match\): (\d+) / (\d+)", full)
    out["fullcheck"] = (int(m.group(1)), int(m.group(2))) if m else None
    rate = need(H8 / "H8_passrate.txt")
    m = re.search(r"trials (\d+) \(2\^([\d.]+)\) contexts (\d+)", rate)
    m2 = re.search(r"E1 test \(Lemma N word n == 0\): passes (\d+)", rate)
    m3 = re.search(r"on h1: passes (\d+)\s+rate \S+\s+2\^-([\d.]+)", rate)
    out["passrate"] = (int(m.group(1)), int(m.group(3)), int(m2.group(1)), int(m3.group(1)), float(m3.group(2))) if m and m2 and m3 else None
    return out


def neighbours_sentence():
    """The classes near the class of the package that the groundwork's grid counted (evidence/h8/H8_count.txt)."""
    text = need(H8 / "H8_count.txt")
    grid = re.search(r"etas in the grid list (\d+), betas in the grid list (\d+)", text)
    with_part = re.search(r"classes with a part in the grid so far: (\d+)", text)
    rows = re.findall(r"CLASS ([0-9a-f]{8}) fixed_bits \d+ members 2\^(\d+) betas_with_a_part \d+ total ([\d.]+)", text)
    if not (grid and with_part and len(rows) >= 2 and rows[0][0] == hx(ETA)):
        return "The classes near this one were not counted for this text."
    return (f"Of {grid.group(1)} classes near this one, counted over a list of {grid.group(2)} betas of their own, "
            f"{with_part.group(1)} have a part; this class has the largest, {num(float(rows[0][2]))} on that list, and the next "
            f"is eta = {rows[1][0]}, with 2^{rows[1][1]} members and {num(float(rows[1][2]))}.")


def read_search():
    """The solver search for other length differences: (sets found, sets for this length difference, the line of
    this package's pin as a dict, the longest run in seconds), and the counts of the candidates."""
    text = need(H8 / "trail5_lx.log")
    want = ",".join(hx(PIN[k]) for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
    found = [l for l in text.split("\n") if "status=SATISFIABLE" in l]
    same_len = [l for l in found if f"model=pin-lx{LEN_A ^ LEN_B} " in l]
    mine = [l for l in found if f"PIN={want}" in l]
    if not mine:
        raise SystemExit("the pin of PART A is not in the solver log evidence/h8/trail5_lx.log")
    m = re.search(r"model=(\S+) bound=(\d+) .*? t=(\d+)s .*? cost=(\d+) .*? eta=([0-9a-f]{8}) beta=([0-9a-f]{8}) tau=([0-9a-f]{8}) "
                  r"eps=([0-9a-f]{8})", mine[0])
    info = dict(model=m.group(1), bound=int(m.group(2)), seconds=int(m.group(3)), cost=int(m.group(4)), eta=m.group(5),
                beta=m.group(6), tau=m.group(7), eps=m.group(8))
    longest = max((int(v) for v in re.findall(r" t=(\d+)s status=SATISFIABLE", text)), default=0)
    cands = []
    for line in need(H8 / "cand_exact_lx.txt").split("\n"):
        c = re.match(r"(\S+) proxy (\d+) class 2\^(\d+) \| pin (\S+) \| .*? \| eta ([0-9a-f]{8}) beta ([0-9a-f]{8}) \| positive (\d+) \| "
                     r"exact ([\d.]+)", line)
        if c:
            cands.append((float(c.group(8)), c.group(4), c.group(1)))
    return len(found), len(same_len), info, longest, cands, want


# ---- the log of the local validation (validate_pkg6.sh writes it)
VALIDATION_LOG = EVID / "validation_log.txt"


def read_validation():
    """What the last local validation showed, if it was made on the files as they are now; else None."""
    text = read(VALIDATION_LOG)
    if text is None:
        return None
    hashes = {m.group(2): m.group(1) for m in re.finditer(r"^sha256 ([0-9a-f]{64})\s+(\S+)$", text, re.M)}
    for rel in ("proof.md", "claim.json", "experiments/manifest.json", "experiments/halfsearch.py"):
        path = CAND / rel
        if not path.exists() or hashes.get(rel) != hashlib.sha256(path.read_bytes()).hexdigest():
            return None
    tests = re.search(r"Ran (\d+) tests", text)
    valid = '"status": "mechanically_valid"' in text
    passed = "experiment status: passed" in text
    exps = re.findall(r"^\s+(half-collision|residual-search): trials=(\d+) successes=(\d+) .*replay identical=(\w+)(?: tries mean=([\d.]+) "
                      r"max=(\d+))?", text, re.M)
    if not (tests and valid and passed and len(exps) == 2):
        return None
    if any(a != b_ or ident != "True" for _, a, b_, ident, _, _ in exps):
        return None
    tries = [e[4] for e in exps if e[4]]
    obs = dict(re.findall(r"^\s+observation (batch_\w+): \d+ rows, values (\[[^\]]*\])", text, re.M))
    entered = re.search(r"^\s+observation batch_stage_2_entered: (\d+) rows, values \[[^\]]*\], sum (\d+)", text, re.M)
    want = {"batch_stage_a_operations": f"[{STAGE_A_OPS}]", "batch_stage_a_loads": f"[{STAGE_A_LOADS}]",
            "batch_stage_2_operations": f"[{STAGE_2_OPS}]", "batch_stage_2_loads": f"[{STAGE_2_LOADS}]", "batch_lanes_right": "[7]"}
    if not entered or any(obs.get(k) != v for k, v in want.items()) or int(entered.group(1)) != int(exps[0][1]):
        return None
    return {"tests": int(tests.group(1)), "pairs": int(exps[0][1]), "tries": tries[0] if tries else "an unrecorded number of",
            "entered": int(entered.group(2))}


def read_filed():
    """Figures of the filed package c47c1a80 from its claim.json (research/pkg5): for the comparing sentences."""
    c = json.loads(need(FILED_CLAIM))
    r3 = c["restrictions"][3]
    h = c["heuristics"][0]
    m = re.search(r"stage A, (\d+) operations .*? plus (\d+) loads, and only .*? runs stage 2, (\d+) operations plus (\d+) loads; with "
                  r"stage 2 counted for (one \w+) of the batches.*?a trial is charged ([\d.]+) operations", r3)
    n = re.search(r"the count is ([\d,]+) times.*?leaving ([\d,]+)", h["extrapolation"])
    f = re.search(r"The factor ([\d,]+) is assumed", h["limitations"])
    if not (m and n and f) or c["claim"]["time_log2"] != float(SUBMISSIONS[-1][1]):
        raise SystemExit("the claim of the filed package does not have the sentences that are read")
    return dict(time=c["claim"]["time_log2"], a_ops=int(m.group(1)), a_loads=int(m.group(2)), s2_ops=int(m.group(3)),
                s2_loads=int(m.group(4)), share=m.group(5), charge=float(m.group(6)), count=integer(n.group(1)),
                rule_count=integer(n.group(2)), factor=integer(f.group(1)))


def read_proof_lines():
    """Trials of tools/proof_lines_check.py, if its file is for the program and for src/proof_head.md as they are; else None."""
    text = read(EVID / "proof_lines_check.txt") or ""
    m = re.match(r"PROGRAM sha256 ([0-9a-f]{64}); src/proof_head.md sha256 ([0-9a-f]{64}); python -B tools/proof_lines_check.py (\d+)", text)
    head = PKG / "src" / "proof_head.md"
    if not m or m.group(1) != program_sha() or m.group(2) != hashlib.sha256(head.read_bytes()).hexdigest() \
            or "RESULT: all hold" not in text:
        return None
    return int(m.group(3))


def read_check_run():
    """(trials, lines marked ok) of the last full run of tools/selftest_pkg6.py that is on file, if its program steps hold."""
    text = read(EVID / "selftest_pkg6_all.txt") or read(EVID / "selftest_pkg6_program.txt") or ""
    m = re.search(r"\(a\) formulas of the family against a forward 2-round compression, (\d+) random trials", text)
    n = re.search(r"lines marked ok: (\d+); exit status 0", text)
    if m and n and "RESULT (a), (b): all checks of the program passed" in text:
        return int(m.group(1)), int(n.group(1))
    return None


# =====================================================================================================
# PART D: tokens, tables and paragraphs
# =====================================================================================================
def exact(v, digits=4):
    """A fraction as a decimal number: in full when it has at most `digits` decimals, else rounded to that many."""
    v = Fraction(v)
    for i in range(0, digits + 1):
        if (v * 10 ** i).denominator == 1:
            return f"{float(v):,.{max(i, 1)}f}"
    return f"{float(v):,.{digits}f}"


def odd_power(v):
    """A positive integer as an odd number times a power of two, if a small odd fits; else in full."""
    j = (v & -v).bit_length() - 1
    odd = v >> j
    if odd < 2 ** 20:
        return f"2^{j}" if odd == 1 else f"{odd} * 2^{j}"
    # a value printed through a logarithm: the nearest small odd multiple (the text says so)
    m, e = math.frexp(float(v))
    for bits in range(1, 21):
        o = round(m * 2 ** bits)
        if o % 2 == 1 and abs(o / 2 ** bits - m) < 1e-11:
            return f"{o} * 2^{e - bits}"
    return f"{v:,}"


def snap(v):
    """The integer of the form (small odd) * 2^j nearest to a factor that the calculator printed through a logarithm."""
    m, e = math.frexp(float(v))
    for bits in range(1, 21):
        o = round(m * 2 ** bits)
        if o % 2 == 1 and abs(o / 2 ** bits - m) < 1e-11:
            return o * 2 ** (e - bits) if e >= bits else v
    return v


def rule_text(rule):
    """A rule in words: the lines of the display in 6.3 (one bit, value 0 first; then pairs)."""
    single, equal, differ = [], [], []
    for mask, value in sorted(rule, key=lambda c: (bin(c[0]).count("1") != 1, c[1], c[0])):
        bits = [i for i in range(32) if mask >> i & 1]
        if len(bits) == 1:
            single.append(f"bit {bits[0]} of h1 is {value}")
        elif len(bits) == 2:
            (differ if value else equal).append(f"{bits[0]} and {bits[1]}")
        else:
            raise SystemExit("rule A: a condition on more than two bits has no wording here")
    return single + [f"bits {p} of h1 are equal" for p in equal] + [f"bits {p} of h1 differ" for p in differ]


def program_tokens(d):
    """The names that src/manifest.json uses: figures of the experiment program, from derive() and PART A alone."""
    n = d["rule_conditions"]
    bound = f"{float(d['rule_share']):.6f}".rstrip("0")
    measured = read_rule_share_h8()
    if measured:
        r = measured[n]
        share = Fraction(r["entered"], measured["batches"])
        if not 7 * Fraction(r["passes"], measured["trials"]) < Fraction(1, 2 ** STAGE_2_LOG2_SHARE):
            raise SystemExit("the measured share of the trials that satisfy rule A, times seven, is not below the stage-2 budget")
        sentence = (
            f"batch_stage_2_entered = 1 is expected for a share of about {float(share):.3f} of the seeds: in the participant's "
            f"count over {num(measured['contexts'])} random contexts with all {num(d['members'])} members each, a share of "
            f"{float(share):.4f} of the batches held a trial that satisfies rule A, and 2^-{r['log2']:.3f} of the trials satisfied "
            f"it (at most 7 * 2^-{n} = {bound} of the batches hold such a trial if a trial satisfies the rule with probability "
            f"2^-{n}, whatever the dependence between the seven trials of a batch, which are consecutive members of the class "
            f"and are not independent). For 256 seeds that is about {256 * float(share):.0f} seeds with a standard deviation of "
            f"about {math.sqrt(256 * float(share) * (1 - float(share))):.0f}, so the count of one run says little and is no "
            f"test of H3.")
    else:
        sentence = (
            f"batch_stage_2_entered = 1 is expected for at most a share of 7 * 2^-{n} = {bound} of the seeds on average if a "
            f"trial satisfies rule A with probability 2^-{n}, whatever the dependence between the seven trials of a batch, "
            f"which are consecutive members of the class and are not independent; the share has not been measured for this "
            f"state of the program. The count of one run of 256 seeds is no test of H3.")
    return dict(
        entered_sentence=sentence,
        members=num(d["members"]),
        stage_a_ops=str(STAGE_A_OPS), stage_a_loads=str(STAGE_A_LOADS),
        stage_2_ops=str(STAGE_2_OPS), stage_2_loads=str(STAGE_2_LOADS),
        rule_pass_exp=str(d["rule_conditions"]), rule_share=bound,
        stage2_share_words=WORDS_SHARE[STAGE_2_LOG2_SHARE])


def claim_tokens(d):
    """Constants, class, cost and claim: everything that follows from derive() alone."""
    t = {}
    for k in ("X3", "X7", "X11", "X15", "W4", "W13"):
        t[k] = hx(PIN[k])
    for k in ("KW4", "W4B", "delta", "Y3", "Y3B", "Y11", "Y11B", "DY3", "DY11", "x", "qsum", "qhalf", "qmask", "qvalue", "K"):
        t[k] = hx(d[k])
    t["eta"] = hx(ETA)
    lx = LEN_A ^ LEN_B
    minus = d["delta"] == (-lx) & M32
    t["delta_note"] = f", that is {'-' if minus else ''}{lx} modulo 2^32"
    t["delta_signed"] = f"{'-' if minus else '+'} {lx}"
    t["factp_table"] = "\n".join(
        f"    {label}a1={hx(r['a1'])} d1={hx(r['d1'])} c1={hx(r['c1'])} b1={hx(r['b1'])}\n"
        f"               a2={hx(r['a2'])} d2={hx(r['d2'])} c2={hx(r['c2'])} b2={hx(r['b2'])}"
        for label, r in (("w4 = W4    ", d["A"]), ("w4 = W4'   ", d["B"])))
    t["P_d2"], t["P_b2"] = hx(d["A"]["d2"]), hx(d["A"]["b2"])
    t["x_bit31_sentence"] = ("Here x has bit 31, so m is x without that bit." if d["x"] >> 31 else
                             "Here x has no bit 31, so m = x.")
    t["fixed_bits"], t["free_bits"] = str(d["fixed"]), str(d["free"])
    t["group_trials_exp"] = str(d["d_bits"] + d["free"])      # pairs (vc, vd) with one difference, times the members
    t["members"], t["members_plain"] = num(d["members"]), str(d["members"])
    t["list_words"], t["full_batches"], t["rest"] = num(d["list_words"]), num(d["full_batches"]), str(d["rest"])
    t["rest_words"] = WORDS[d["rest"]]
    t["last_batch"] = ("one that holds the last member" if d["rest"] == 1 else f"one that holds the last {WORDS[d['rest']]} members")
    t["last_word_spare"] = (f"the {WORDS[d['spare']]} spare lanes of the last word repeat its last member" if d["spare"] != 1 else
                            "the spare lane of the last word repeats its last member")
    F, T = LOG2_FACTOR, d["T"]
    l_charge = math.log2(CHARGE)
    t.update(F=str(F), F1=str(F + 1), T=str(T), T1=str(T + 1), factor=num(2 ** F), charge=str(CHARGE),
             ctx=str(d["ctx"]), d_bits=str(d["d_bits"]),
             pass_budget=str(d["pass_budget"]), pass_shift=str(PASS_SHIFT), pass_ops=str(d["pass_ops"]),
             ctx_ops=str(d["ctx_ops"]), lists_ops=str(d["lists_ops"]), sel_ops=str(SELECTION_OPS_LOG2),
             main_exp=f"{d['main_exp']:.5f}", log_charge=f"{l_charge:.6f}", log_unit=f"{math.log2(C_UNIT):.6f}",
             rest_exp=f"{up(d['rest_exp'], 2) if up(d['rest_exp'], 2) > d['rest_exp'] else up(d['rest_exp'], 2) + 0.01:.2f}",
             seventh=f"{math.floor(d['seventh'] * 1000) / 1000:.3f}", total_exp=f"{d['total_exp']:.4f}",
             total_bound=f"{d['total_bound']:.2f}", time_log2=f"{d['time_log2']:.1f}", slack=f"{d['slack']:.2f}",
             pass_share=f"{math.floor(d['pass_share'] * 100) / 100:.2f}", f_min=num(d["f_min"]),
             uniform_exp=f"{d['uniform_exp']:.5f}",
             uniform_time=f"{up(d['uniform_total'], 1):.1f}", uniform_total2=f"{d['uniform_total']:.2f}",
             alt_F=str(F - 1), alt_T=str(T + 1), alt_time=f"{d['time_log2'] + 1:.1f}", alt_factor=num(2 ** (F - 1)),
             memory_log2=str(MEMORY_LOG2), online_log2=str(d["online_log2"]), preprocessing_log2=str(PREPROCESSING_LOG2),
             advice_log2=str(ADVICE_LOG2), data_words=num(d["data_words"]), data_bytes=num(d["data_bytes"]),
             stage_a_ops=str(STAGE_A_OPS), stage_a_loads=str(STAGE_A_LOADS), stage_a_total=str(d["stage_a"]),
             stage_2_ops=str(STAGE_2_OPS), stage_2_loads=str(STAGE_2_LOADS), stage_2_total=str(d["stage_2"]),
             alphas_exp=str(d["alphas_exp"]), stage2_den=str(2 ** STAGE_2_LOG2_SHARE),
             stage2_share_words=WORDS_SHARE[STAGE_2_LOG2_SHARE],
             stage2_budget=f"{num(d['list_words'])} * 2^{d['stage2_shift']}", batches_total=f"{num(d['list_words'])} * 2^{d['alphas_exp']}",
             stage2_trial_share=f"{math.floor((math.log2(d['list_words']) + d['stage2_shift'] - T) * 100) / 100:.2f}",
             alpha_ops=f"{float(d['alpha_ops']):,.2f}", alpha_charged=f"{float(d['alpha_charged']):,.1f}",
             per_trial=f"{up(float(d['alpha_ops'] / d['members']), 3):.3f}",
             per_trial_expected=f"{up(float(d['alpha_expected'] / d['members']), 3):.3f}",
             alpha_margin_pct=f"{math.floor(1000 * float(d['alpha_charged'] / d['alpha_ops'] - 1)) / 10:.1f}",
             rule_conditions=WORDS[d["rule_conditions"]], rule_pass_exp=str(d["rule_conditions"]),
             rule_share=f"{float(d['rule_share']):.6f}".rstrip("0"),
             budget_over_rule=f"{down(float(Fraction(d['list_words'] * 2 ** d['rule_conditions'], 2 ** (d['free'] + STAGE_2_LOG2_SHARE))), 3):.3f}",
             advice_bytes=str(d["advice_bytes"]), advice_limit=str(2 ** ADVICE_LOG2),
             advice_rule_words=WORDS[d["advice_rule_words"]], advice_rule_bytes=str(4 * d["advice_rule_words"]),
             prep_bound=num(PREP_OPS),
             sol_exp=str(192 + d["free"] - 128), space_exp=str(192 + d["free"]), share_exp=str(d["fixed"]),
             submission_state=SUBMISSION_STATE)
    if PREP_OPS != 1024:
        raise SystemExit("PREP_OPS changed: the sentence of Section 8 on the work per value of X14 states it as a number; read it")
    # the budget in trials against the pass rate of the rule: list_words * 2^(T - free - share) / 2^T * 2^n
    t["submissions"] = join(f"`{s}`" for s, _ in SUBMISSIONS[:-1])
    t["submissions_plain"] = join(s for s, _ in SUBMISSIONS)
    t["submission_scores"] = join(v for _, v in SUBMISSIONS)
    t["submission_scores_before"] = join(v for _, v in SUBMISSIONS[:-1])
    t["last_submission"], t["last_score"] = SUBMISSIONS[-1]
    # ---- rule A in words and Lemma A
    lines = rule_text(RULE_A[ETA])
    t["rule_a_block"] = "\n".join("    " + l + (";" if i + 1 < len(lines) else ".") for i, l in enumerate(lines))
    t["rule_a_inline"] = join(lines)
    zl = [f"bit {low} of z is {value}" if high is None else f"bits {low} and {high} of z {'differ' if value else 'are equal'}"
          for low, high, value, _, _ in d["z_conditions"]]
    t["rule_z_block"] = "\n".join("    " + l + (";" if i + 1 < len(zl) else ".") for i, l in enumerate(zl))
    hbits = sorted({b_ for c in d["z_conditions"] for b_ in c[3]})
    ebits = sorted({b_ for c in d["z_conditions"] for b_ in c[4]})
    t["rule_h_bits"], t["rule_e_bits"] = join(str(b_) for b_ in hbits), join(str(b_) for b_ in ebits)
    t["rule_e_values"] = join(f"bit {b_} is {d['qvalue'] >> b_ & 1}" for b_ in ebits)
    t["rule_z_bits_count"] = WORDS[len({b_ for c in d["z_conditions"] for b_ in c[:2] if b_ is not None})]
    shifts = d["a_shifts"]
    pairs = sum(1 for c in d["z_conditions"] if c[1] is not None)
    singles = len(d["z_conditions"]) - pairs
    names = {dist: ("S" if len(shifts) == 1 else f"S{dist}") for dist, _ in shifts}
    t["rule_c_put"] = "Put " + ", ".join([f"{names[dist]} = {hx(mask)}" for dist, mask in shifts] + [f"ALL = {hx(d['a_all'])}"]) \
        + f" and V = {hx(d['a_value'])}."
    inner = "z" + "".join(f" XOR ((z >> {dist}) AND {names[dist]})" for dist, _ in shifts)
    t["rule_c_formula"] = f"    (({inner}) AND ALL) XOR V" if shifts else "    (z AND ALL) XOR V"
    if len(t["rule_c_formula"]) > 79:
        raise SystemExit("the formula of Lemma A (c) is over 79 characters: break it in pkg6_data.py")
    if not shifts:
        t["rule_c_proof"] = ("Every condition is on one bit of z. ALL holds the positions of the conditions and V the required "
                             "values.")
    elif len(shifts) == 1:
        dist = shifts[0][0]
        t["rule_c_proof"] = (
            f"Bit p of z XOR ((z >> {dist}) AND S) is the XOR of bits p and p + {dist} of z at the positions p of S and bit p of "
            f"z elsewhere. S holds the lower position{'s' if pairs != 1 else ''} of the {WORDS[pairs]} condition{'s' if pairs != 1 else ''} "
            f"on two bits, ALL holds {'these' if pairs != 1 else 'it'} and the positions of the {WORDS[singles]} conditions on one "
            f"bit, and V holds the required values.")
    else:
        t["rule_c_proof"] = (
            "Bit p of the word in the inner brackets is, for each distance s, the XOR of bits p and p + s of z at the positions "
            "p of the mask of that distance (" + join(f"{names[dist]} for s = {dist}" for dist, _ in shifts) + "), and bit p of z "
            "at the other positions; no position lies in two masks. Each mask holds the lower positions of the conditions on "
            f"two bits at its distance, ALL holds these and the positions of the {WORDS[singles]} conditions on one bit, and V "
            "holds the required values.")
    ops, loads = 6 + 3 * len(shifts), 5 + len(shifts)
    if (sum(x[0] for x in ((3, 1), (10, 8), (16, 10), (17, 7))) + ops, sum(x[1] for x in ((3, 1), (10, 8), (16, 10), (17, 7))) + loads) \
            != (STAGE_A_OPS, STAGE_A_LOADS) or (3 + 12 + 27 + 18 + 40 + 15, 1 + 4 + 13 + 8 + 15 + 7) != (STAGE_2_OPS, STAGE_2_LOADS):
        raise SystemExit("the parts of the table of 6.5 do not add up to the stage counts")
    t["rule_part_ops"], t["rule_part_loads"] = str(ops), str(loads)
    t["rule_part_cells"] = f"word ({ops - 4}), flags and branch (4) | {ops} | {loads}"
    t["rule_part_sentence"] = (
        "In the rule A part the word of Lemma A (c) is "
        + ("an AND with ALL and an XOR with V (2 operations, 2 loads)." if not shifts else
           f"a shift, an AND with {'S' if len(shifts) == 1 else 'its mask'} and an XOR for "
           f"{'the one distance' if len(shifts) == 1 else 'each of the ' + WORDS[len(shifts)] + ' distances'} "
           f"({3 * len(shifts)} operations, {len(shifts)} load{'s' if len(shifts) != 1 else ''}), then an AND with ALL and an XOR "
           f"with V (2 operations, 2 loads)."))
    return t


def alternatives(d, outcomes, counts):
    """Rows for the table of the other rules and the other factor: per rule (n, count, margins, stage A, budgeted per
    trial, charge at the margin of the package, time_log2 per factor)."""
    own = d["alpha_ops"] / d["members"]
    ratio = Fraction(str(CHARGE)) / own
    rows = []
    for n in sorted(RULES):
        per = budget(n, d["list_words"]) / d["members"]
        charge = math.ceil(float(per * ratio) * 10 - 1e-9) / 10
        times = {F: total_exponents(charge, 127 - F, d["free"])[4] for F in ALT_FACTORS}
        rows.append(dict(n=n, count=counts[n]["count"], per=float(per), charge=charge, times=times,
                         lost=float(1 - counts[n]["count"] / counts[n]["full"]), stage=STAGE_A_BY_RULE[n]))
    return rows


def build_tokens():
    if not TEXT_PORTED:
        raise SystemExit("pkg6_data.py: TEXT_PORTED is False")
    d = derive()
    t = claim_tokens(d)
    t.update(program_tokens(d))
    F, T = LOG2_FACTOR, d["T"]
    filed = read_filed()

    # ---- the local validation
    li = read_validation()
    if li:
        t["local_checks"] = (
            "- `python3 scripts/local_tracks.py check blake3-r2-exploratory`: `mechanically_valid`.\n"
            f"- Repo tests pass ({li['tests']} tests).\n"
            "- Organizer intake run locally with the pinned Docker image: both experiments `passed`, "
            f"{li['pairs']} of {li['pairs']} mask events each, stdout byte-identical on replay; the toy search tried "
            f"{li['tries']} class members on average, more than the 256 that independent uniform low bytes would give, "
            f"and for its counted batch it returned {STAGE_A_OPS} operations and {STAGE_A_LOADS} loads for stage A, "
            f"{STAGE_2_OPS} and {STAGE_2_LOADS} for stage 2 and 7 of 7 lanes right on every one of the {li['pairs']} seeds; "
            f"a lane passed rule A in {li['entered']} of these {li['pairs']} batches (observations of the "
            "program, not checked by the runner).")
    else:
        t["local_checks"] = "- The organizer intake has not been run locally on this state of the package."

    # ---- the self-test of the program in the package
    st = selftest()
    order = ("C0 backwards", "D0 and D1", "C2 to z", "rule A", "C2, rest", "D0 and D1, rest", "C1 to Y1", "E1, A and B", "E1 test")
    sums = [f"{st['parts'][p]['largest_sum']:.3f}" for p in order]
    patterns = 1 << len({b_ for c in d["z_conditions"] for b_ in c[:2] if b_ is not None})
    if not ((st["stage_a"]["operations"], st["stage_a"]["loads"]) == (STAGE_A_OPS, STAGE_A_LOADS)
            and (st["stage_2"]["operations"], st["stage_2"]["loads"]) == (STAGE_2_OPS, STAGE_2_LOADS)
            and [st["parts"][p]["bound"] for p in order] == [2, 4, 5, 2, 6, 5, 9, 13, 2]
            and st["lanes_right"] == st["lanes_checked"] and st["counts_equal_table"] and st["same_counts_in_every_case"]
            and st["members_in_list"] == d["members"] and st["list_words"] == d["list_words"] and st["zero_test_words"] == 0
            and st["zero_lane_patterns_right"] == 128 and st["rule_a_patterns_right"] == st["rule_a_patterns"] == patterns
            and st["sums_below_bounds"] and st["per_context_constants"] == 8 and st["per_x14_constants"] == 13
            and st["message_bytes"] == [LEN_A, LEN_B] and st["rule_conditions"] == RULE_CONDITIONS
            and st["rule_a_on_z"] == {"shifts": [[dist, hx(mask)] for dist, mask in d["a_shifts"]], "all": hx(d["a_all"]),
                                      "value": hx(d["a_value"])}):
        raise SystemExit("the self-test does not report what the text states; read its JSON line")
    t.update(st_cases=num(st["cases"]), st_seed=str(st["seed"]), st_lanes=num(st["lanes_checked"]),
             st_sums=", ".join(sums[:-1]) + " and " + sums[-1], st_registers=str(st["registers"]),
             st_ctx_constants=str(st["per_context_constants"]), st_x14_constants=str(st["per_x14_constants"]),
             st_largest=f"{st['largest_lane'] / 2 ** 32:.3f}", st_pass_a=num(st["lanes_passing_rule_a"]),
             st_entered=num(st["batches_entering_stage_2"]), st_a_satisfied=str(st["rule_a_patterns_satisfied"]),
             st_a_patterns=str(st["rule_a_patterns"]))
    big = read_big_selftest(RULE_CONDITIONS)
    if big:
        t["big_selftest_sentence"] = (
            f"A longer run of the same self-test, {num(big['cases'])} batches with seed {big['seed']}, reports "
            f"{num(big['lanes_right'])} of {num(big['lanes_checked'])} lanes right, the same counts in every case, at most "
            f"{big['registers']} registers and a largest sum of {big['largest_lane'] / 2 ** 32:.3f} * 2^32; "
            f"{num(big['lanes_passing_rule_a'])} of its lanes satisfy rule A, a share of "
            f"2^{math.log2(big['lanes_passing_rule_a'] / big['lanes_checked']):.3f}, in {num(big['batches_entering_stage_2'])} "
            f"batches. Its contexts are random or extreme by design and are not laid out as a run of 6.4.")
        t["big_note_sentence"] = (f"A longer run, {num(big['cases'])} batches with seed {big['seed']}: all "
                                  f"{num(big['lanes_checked'])} lanes right.")
        t["big_claim"] = f", and {num(big['lanes_passing_rule_a'])} of {num(big['lanes_checked'])} in a longer run"
    else:
        t["big_selftest_sentence"] = "No longer run of the self-test is on file for this state of the program."
        t["big_note_sentence"], t["big_claim"] = "", ""
    t["bound_tool_sentence"] = (
        "A separate participant tool derives the bounds of the sums for all inputs by interval arithmetic on a second "
        "machine and finds every one below the bound of its part." if read_lane_bound() else "")
    prep = read_prep()
    t.update(prep_ops=str(prep[0]), prep_loads=str(prep[1]), prep_stores=str(prep[2]), prep_total=str(sum(prep)))

    # ---- the count
    oc = read_outcomes()
    ct = read_count_table()
    gpt = read_gpt()
    prod, part, order_b, sampled = oc["prod"], oc["part"], oc["order"], oc["sampled"]
    total = sum(part.values())
    flagged = [b_ for b_ in order_b if sampled.get(b_)]
    light = [b_ for b_ in order_b if k_of(b_) <= 14]
    heavy = [b_ for b_ in order_b if k_of(b_) >= 15]
    valid = int(ct["valid"][0])
    n14, noeps14, enum14, part14 = (int(v) for v in ct["k14"])
    finished, valid2, decided, sat_b, unsat_b, undecided, models_ok, models = (integer(v) for v in ct["solver"])
    est_betas, est_outcomes, est_fallbacks, est_k, est_sum = ct["estimates"]
    if (valid2, decided, undecided, sat_b, models_ok) != (valid, valid, 0, len(order_b), models) or part14 != len(light) \
            or int(est_fallbacks) != 0 or abs(float(est_sum) - float(sum(part[b_] for b_ in flagged))) > 5e-6:
        raise SystemExit("the table of the count (evidence/h8/H8_count.txt) and the outcome file do not agree")
    counts = {n: rule_count(n, oc) for n in sorted(RULES)}
    own = counts[RULE_CONDITIONS]
    used = int(own["count"])                                   # rounded down
    full_exact = own["full"]
    lost = full_exact - own["count"]
    if used < MIN_MARGIN * 2 ** F:
        raise SystemExit(f"the count with rule A is less than {MIN_MARGIN} times the assumed factor: change the rule or the factor")
    best = min((n for n in RULES if int(counts[n]["count"]) >= MIN_MARGIN * 2 ** F), key=lambda n: budget(n, d["list_words"]))
    if best != RULE_CONDITIONS:
        raise SystemExit(f"the rule of PART A is not the cheapest rule with a margin of {MIN_MARGIN}: that is the rule with {best} conditions")
    heaviest = order_b[0]
    top2 = sum(part[b_] for b_ in order_b[:2])
    by_size = sorted(prod.values(), reverse=True)
    top16 = sum(by_size[:16])
    t.update(exact_total=num(total), exact_log2=f"{math.log2(total):.2f}", hit_exp=f"{128 - math.log2(total):.2f}",
             rule_count=num(used), rule_lost=f"about {float(total - own['count']) / 1e6:.2f} million", rule_outcomes=str(len(prod)),
             rule_ok=str(len(prod) - len(own["violable"])), rule_bad=str(len(own["violable"])),
             rule_lost_pct=f"{100 * float(lost / full_exact):.2f}", flagged_betas=WORDS[len(flagged)],
             exact_over_factor=f"{down(used / 2 ** F, 2):.2f}", exact_over_alt=f"{down(used / 2 ** (F - 1), 1):.1f}",
             per_run=f"{down(used / 2 ** (F + 1), 2):.2f}", cluster_max=f"{down(used / d['f_min'], 2):.2f}",
             assumed_per_run="0.5", heaviest_share=f"{100 * float(part[heaviest] / total):.0f}",
             top2_share=f"{100 * float(top2 / total):.0f}", top_outcomes="sixteen", top_outcomes_share=f"{100 * float(top16 / total):.0f}",
             heavy_betas=str(len(heavy)), unsat_betas=num(unsat_b - (n14 - part14)))
    if not math.ceil(total) - used >= lost:
        raise SystemExit("the printed difference is below what is left out")
    filed_lost = 100 * (filed["count"] - filed["rule_count"]) / filed["count"]
    t.update(filed_lost_pct=f"{filed_lost:.2f}", filed_count=num(filed["count"]), filed_members=num(FILED_MEMBERS))

    k14_sum = sum(part[b_] for b_ in light)
    k15_sum = sum(part[b_] for b_ in heavy)
    t["count_paragraph"] = (
        f"For these constants {num(valid)} words occur as beta. The {num(n14)} betas with k at most 14 were given to the "
        f"calculator: for {num(noeps14)} of them beta XOR ROR(eta, 1) has odd weight, so that no eps exists; the other "
        f"{num(enum14)} were enumerated completely, without a limit on the weight of tau, and {word(part14)} of them have a "
        f"nonzero part. These parts add up to {exact(k14_sum)}, from {sum(1 for k in prod if k_of(k[0]) <= 14)} outcomes with a "
        f"nonzero product; no outcome of these betas went through either fallback, so this figure is a count. The "
        f"{num(valid - n14)} betas with k of 15 or more were treated in two ways. A SAT solver (kissat) was asked, for every "
        f"beta, whether the whole system (E1 and E3 for both messages, a zero residual, Y4 in the class, this beta) has a "
        f"solution: it answered that it has none for {num(unsat_b - (n14 - part14))} of them and returned a solution for "
        f"{len(heavy)}, and every returned solution has a zero residual in plain arithmetic. The calculator, with a pruned "
        f"search over tau that gives the same outcomes on the betas where both were run, finished {num(finished - n14)} of "
        f"these betas before it was stopped, among them all {len(heavy)} that the solver found satisfiable; these "
        f"{len(heavy)} have parts that add up to {exact(k15_sum)}. In {word(len(flagged))} of them, outcomes went through the "
        f"random-subset branch of step 3; their parts, {float(sum(part[b_] for b_ in flagged)):.3f} together, are estimates. "
        f"In all the count is {exact(total)}, from {len(order_b)} betas and {len(prod)} outcomes; without the "
        f"{word(len(flagged))} betas that hold estimates it is {exact(full_exact)}, from {len(order_b) - len(flagged)} betas and "
        f"{len(own['exact'])} outcomes. It is about 2^{math.log2(total):.2f}, so that under M a trial has R = 0 with "
        f"probability about 2^-{128 - math.log2(total):.2f}. That every beta is covered rests on the solver's answers for "
        f"the betas with k of 15 or more, which are answers without a proof certificate, and on the recount reported below.")
    head = ("| beta | k | Outcomes | Exact part | Sampler | Error | Deviation |\n"
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
    rows = []
    for b_ in light:
        s = ct["sampler"].get(b_)
        cells = f"| {b_} | {k_of(b_)} | {sum(1 for k in prod if k[0] == b_)} | {exact(part[b_])} |"
        rows.append(cells + (f" {num(s[0])} | {num(s[1])} | {s[2]} |" if s else " | | |"))
    rows.append(f"| {len(heavy)} betas, k >= 15 | | {sum(1 for k in prod if k_of(k[0]) >= 15)} | {exact(k15_sum)} | | | |")
    rows.append(f"| sum | | {len(prod)} | {exact(total)} | | | |")
    t["exact_table"] = head + "\n".join(rows)
    s_mean, s_err, s_dev, s_low, s_high = ct["sampler_sum"]
    s_betas = [b_ for b_ in light if b_ in ct["sampler"]]
    t["exact_table_paragraph"] = (
        f"In the table, k is the number of bits that beta fixes in c1, \"outcomes\" is the number of outcomes (tau, eps) with "
        f"P1 * N3 > 0, and \"exact part\" is the class-rate part of the beta. The heaviest beta, {heaviest}, carries "
        f"{100 * float(part[heaviest] / total):.0f}% of the count, the two heaviest together {100 * float(top2 / total):.0f}% "
        f"and the four heaviest {100 * float(sum(part[b_] for b_ in order_b[:4]) / total):.0f}%. The last three columns come "
        f"from the sampler of the first submissions, which is used here as a check and not for the figure: for one beta it "
        f"draws d1 among the values with that beta and b1, a2 uniformly, and counts E3 for each draw with the count of step "
        f"3. {word(len(s_betas), True)} betas were given 16 runs each, with the same seeds for every beta. \"Sampler\" is the "
        f"mean of the runs, \"error\" the standard deviation of the runs divided by the square root of their number, and "
        f"\"deviation\" the difference from the exact part in units of that error. For the {word(len(s_betas))} betas together "
        f"the sums of the 16 seeds have mean {s_mean} with standard error {s_err}, against {ct['sampler_exact'][1]} counted "
        f"({s_dev} standard errors). This is a weak check: the quantity is heavy-tailed, and the sums of single seeds range "
        f"from {s_low} to {s_high}. The sampler shares the E3 count with the calculator.")
    # the independent recount
    exact_betas = [b_ for b_ in order_b if b_ not in flagged]
    g_equal = sum(1 for b_ in exact_betas if abs(gpt["parts"].get(b_, 0) - part[b_]) <= Fraction(1, 10 ** 9) * max(part[b_], 1))
    g_ident = sum(1 for b_ in exact_betas if gpt["parts"].get(b_) == part[b_])
    if set(gpt["parts"]) != set(part) or g_equal != len(exact_betas) or not gpt["same"] or not gpt["ended"]:
        raise SystemExit("the independent recount does not agree beta by beta, or its rerun is not complete")
    g_flag = sum(gpt["parts"][b_] for b_ in flagged)
    t["recount_paragraph"] = (
        f"After the count was finished, another AI model, GPT Sol 6.1 (OpenAI), was given the definition of the seven-word "
        f"system, the constants and the class, and was asked to count the class rate with a method and a program of its "
        f"own; by its own account it did not read or use the participant's counting programs. The recount was not blind: "
        f"the request also stated the participant's total, the parts of the four heaviest betas and the number of betas "
        f"with a part, as figures to be confirmed or refuted, and it offered a hint at the method (fix beta, enumerate the "
        f"differences that are possible, carry conditions of single additions). The parts of the other {len(part) - 4} "
        f"betas and the two factors of every outcome were not given to it. Its program is integer "
        f"arithmetic throughout: it visits every word that can occur as beta ({num(gpt['visited'])} of them, {num(gpt['checked'])} "
        f"with an eps), and for every outcome it counts both sides with carry automata of its own design. Its result is "
        f"r = {gpt['total'].numerator} / {gpt['total'].denominator} = {float(gpt['total']):,.4f}, from {len(gpt['parts'])} "
        f"betas. For this text its program was compiled and run again by the participant's helper agent, with the same "
        f"output, and its parts were compared with the count beta by beta. The same {len(part)} betas have a part. For the "
        f"{len(exact_betas)} betas that the count has in full, the two parts are "
        + ("identical as fractions" if g_ident == len(exact_betas) else
           f"equal: identical as fractions in {g_ident} and equal to within 10^-9 of their value in the other "
           f"{word(len(exact_betas) - g_ident)}")
        + (f" (the calculator prints the factor N1 through a logarithm; in {word(oc['snapped'])} outcome"
           f"{'s' if oc['snapped'] != 1 else ''} the printed value misses an odd multiple of a power of two by a relative "
           f"error below 10^-11 and is read as that multiple)" if oc["snapped"] else "")
        + f". For the {word(len(flagged))} betas in which the count holds estimates, the "
        f"recount gives {float(g_flag):.6f} where the count has {float(sum(part[b_] for b_ in flagged)):.6f}. The recount is "
        f"larger than the count by {float(gpt['total'] - total):.4f} in all. It confirms the count; the figure that the claim "
        f"uses is not taken from it. What was checked of it here is that its program reproduces its figures and that they "
        f"agree with the count; its method was read in its own description and not re-derived.")
    # the outcomes of the heaviest beta
    hrows = sorted(((prod[k], k) for k in prod if k[0] == heaviest), reverse=True)
    lines = ["| tau | eps | N1 | N3 | Adds |", "| --- | --- | ---: | ---: | ---: |"]
    for v, k in hrows:
        e1, n3 = oc["e1n3"][k]
        lines.append(f"| {k[1]} | {k[2]} | {odd_power(snap(e1))} | {odd_power(snap(n3))} | {exact(v)} |")
    lines.append(f"| sum | | | | {exact(part[heaviest])} |")
    t["outcome_table"] = "\n".join(lines)
    t["outcome_paragraph"] = (
        f"The table lists the {len(hrows)} outcomes with a nonzero product of the heaviest beta, {heaviest} "
        f"(k = {k_of(heaviest)}). N1 is the number of triples (c1, b1, a2), with c1 XOR (c1 + DY11) = ROL(beta, 12), for "
        f"which E1 produces tau and eps; it is P1 times 2^{96 - k_of(heaviest)}. N3 is the number of quadruples "
        f"(Y4, h1, Y9, w8) of step 3. \"Adds\" is N1 * N3 / 2^{96 - d['fixed']}, what the outcome adds to the class-rate part "
        f"of the beta. Both counts can be recomputed with a model counter from the definitions of 6.2 and of steps 2 to 4, "
        f"without the calculator.")

    # ---- rule A
    bad_betas = {k[0] for k in own["violable"]}
    kept = own["kept"]
    kept_betas = sorted({k[0] for k in kept}, key=lambda b_: (-sum(v for k, v in kept.items() if k[0] == b_), b_))
    t["rule_paragraph"] = (
        f"Which outcomes these are was decided with a SAT solver. For each of the {len(prod)} outcomes with a nonzero product "
        f"P1 * N3, over all {len(order_b)} betas with a part, the E3 system of step 3 was written as a CNF formula from its "
        f"definition: the unknowns Y4, h1, Y9 and w8, E3 for both messages, and the four XOR differences that the outcome "
        f"prescribes. The solver kissat was asked two questions. First, whether the formula has a solution. It has one for "
        f"all {len(prod)} outcomes, and every model, evaluated again in plain arithmetic, is a solution of its outcome with Y4 "
        f"in the class; {own['models_passing']} of these models satisfy rule A. Second, whether the formula has a solution "
        f"together with the clause that h1 violates rule A. For {len(prod) - len(own['violable'])} outcomes the answer is "
        f"that it has none: if these answers are right, every solution of these outcomes satisfies rule A, and stage A drops "
        f"none of them. For the other {len(own['violable'])} outcomes, in {len(bad_betas)} betas, the solver returned a "
        f"solution that violates rule A, and each was evaluated again in plain arithmetic. So most outcomes of the count "
        f"have solutions that rule A drops. The count that the claim uses keeps only the outcomes without such a solution, "
        f"and only from the {len(order_b) - len(flagged)} betas that were counted in full. Per beta, for the betas with a "
        f"part of at least one:")
    rhead = "| beta | k | Outcomes | Kept | Part of the beta | Part kept |\n| --- | ---: | ---: | ---: | ---: | ---: |\n"
    rrows, small_kept, small_part, small_n, small_keptn = [], 0, 0, 0, 0
    for b_ in order_b:
        keys = [k for k in prod if k[0] == b_]
        kb = [k for k in keys if k in kept]
        if part[b_] >= 1 and b_ not in flagged:
            rrows.append(f"| {b_} | {k_of(b_)} | {len(keys)} | {len(kb)} | {exact(part[b_])} | {exact(sum(kept[k] for k in kb))} |")
        else:
            small_part += part[b_]
            small_kept += sum(kept[k] for k in kb)
            small_n += len(keys)
            small_keptn += len(kb)
    rrows.append(f"| {len(order_b) - len(rrows)} others | | {small_n} | {small_keptn} | {exact(small_part)} | {exact(small_kept)} |")
    rrows.append(f"| sum | | {len(prod)} | {len(kept)} | {exact(total)} | {exact(own['count'])} |")
    t["rule_table"] = rhead + "\n".join(rrows)
    t["rule_kept_paragraph"] = (
        f"The {len(kept)} outcomes that are kept, one by one, so that the two questions can be put again to any SAT solver "
        f"from the definitions of 6.2 and 6.3; \"Adds\" is what the outcome adds to the count, as in the table of the "
        f"heaviest beta:")
    krows = sorted(((v, k) for k, v in kept.items()), reverse=True)
    t["rule_kept_table"] = ("| beta | tau | eps | Adds |\n| --- | --- | --- | ---: |\n"
                            + "\n".join(f"| {k[0]} | {k[1]} | {k[2]} | {exact(v)} |" for v, k in krows)
                            + f"\n| sum | | | {exact(own['count'])} |")
    worst = max(((prod[k], k) for k in own["violable"] if k in own["exact"]))
    n3 = read_n3_rule()
    n3r = n3[RULE_CONDITIONS]
    t["rule_count_before"] = f"The kept outcomes add up to {exact(own['count'])}. The claim uses this figure rounded down,"
    t["rule_count_after"] = (
        f"It is {100 * float(own['count'] / total):.2f}% of the count of all solutions; {exact(lost)} is given up with the "
        f"{len([k for k in own['violable'] if k in own['exact']])} outcomes that have a violating solution, and "
        f"{float(total - full_exact):.3f} with the betas that hold estimates. The largest outcome given up is tau = "
        f"{worst[1][1]}, eps = {worst[1][2]} of beta {worst[1][0]}, with {exact(worst[0])}. Under M the figure is a lower "
        f"bound for the rate of the trials with R = 0 that satisfy rule A, provided that the {len(kept)} answers \"no "
        f"solution\" behind it are right. The true rate under M is larger, because the outcomes given up also have "
        f"solutions that satisfy the rule. An exact count that is described below gives it: r_A = {n3r['r_all']:,.2f} over "
        f"all {n3r['betas']} betas ("
        + join(f"the rule with {WORDS[n]} conditions has {n3[n]['r_all']:,.2f}" for n in sorted(RULES) if n != RULE_CONDITIONS)
        + f"). So the figure that the claim uses is {100 * float(own['count']) / n3r['r_all']:.1f}% of the model's own value "
          f"of r_A. The claim keeps the smaller figure.")
    sec = own["second"]
    t["rule_second_paragraph"] = (
        (f"The two questions were put a second time with another formula and other solvers. The second formula has the "
         f"unknown Y14 in place of h1 and prescribes the four output differences of E3 in place of the differences inside "
         f"it; it was written by a reviewing helper agent of the filed package from the text of that package, and for this "
         f"package only its constants and its rule were changed. " + join(
             f"{solver} ({version})" if version else solver for solver, _, _, _, version in sec)
         + f" each answered both questions for all {len(prod)} outcomes with the same result as kissat: every base formula "
           f"satisfiable, and the same {len(prod) - len(own['violable'])} outcomes without a violating solution. The three "
           f"solvers are different programs; these runs kept no proof certificate.")
        if len(sec) == 2 else "The two questions were not put a second time with another formula.")
    # Two further checks of the kept outcomes: programs of reviewing helper agents, copied to tools/ and run again
    # (tools/rule_drat_all.sh for the third formula, the proofs and the controls; tools/n3_rule_h8.py for the exact
    # count). The first three are written for the rule with five conditions.
    drat = read_drat() if RULE_CONDITIONS == 5 else None
    if n3["same"][0] != n3["same"][1] or n3["same"][1] != len(own["exact"]) or any(
            not n3[n]["equal"] or n3[n]["est"] or n3[n]["kept"] != n3[n]["unsat"]
            or n3[n]["kept"] != len(prod) - len(counts[n]["violable"]) or abs(n3[n]["cons"] - float(counts[n]["count"])) > 1e-3
            for n in RULES) or abs(n3["total"] - float(gpt["total"])) > 1e-4:
        raise SystemExit("evidence/n3_rule_h8.txt does not confirm the solver answers, the conservative counts and the recount: read it")
    if drat and not (drat["keys"] == set(kept) and drat["kept"] == drat["verified"] == len(kept) and drat["failed"] == 0
                     and abs(drat["carried"] - float(own["count"])) < 1e-3 and drat["controls"] >= 1 and drat["controls_ok"]
                     and drat["base"][0] == drat["base"][1] == drat["base"][2] == len(prod) and drat["unsat"] == len(kept)
                     and drat["sat"] == drat["sat_ok"] == len(own["violable"]) and drat["undecided"] == 0
                     and drat["equal"] == (len(prod), len(prod)) and drat["same_set"]
                     and drat["encoding"][0] == drat["encoding"][1] and drat["encoding"][2] == 64):
        raise SystemExit("the third formula or the proofs of the kept outcomes do not hold as the text says: read evidence/rule_drat_*.txt")
    t["rule_checks_paragraph"] = (
        "*Two further checks of the kept outcomes (programs of reviewing helper agents, run again for this text).* "
        + ((f"First, a helper agent that reviewed this text put the two questions again with a third formula of its own: two "
            f"full G calls, the class by the mask of Lemma Q, and R = 0 on the four output differences. With it kissat gave "
            f"the same answers for all {drat['equal'][0]} outcomes. For the {drat['kept']} kept outcomes cadical, run "
            f"without preprocessing, wrote a DRAT proof of its answer \"unsatisfiable\", and a checker that the same agent "
            f"wrote, which accepts a clause only when unit propagation derives a conflict from its negation, accepted all "
            f"{drat['verified']} proofs, {num(drat['clauses'])} clauses in all. In {word(drat['controls'])} controls the "
            f"checker rejected the same proof for the formula without the clause of the rule, which is satisfiable, and "
            f"rejected a proof cut in half. "
            + ("No standard proof checker was used: the checker is a participant-side program, and the formula that it "
               "checks is that agent's. " if drat["trim"] is None else
               f"The standard checker drat-trim accepted {drat['trim'][0]} of {drat['trim'][1]} of these proofs. "))
           if drat else "")
        + f"{'Second, another' if drat else 'A'} helper agent that reviewed this text wrote an exact count of the E3 side "
          f"split by the rule: for an outcome, the number of quadruples (Y4, h1, Y9, w8) of step 3 whose h1 satisfies the "
          f"rule and the number whose h1 violates it, in integers, from the definitions of 6.2 and without a solver. Its "
          f"N3 equals the calculator's for all {n3['same'][1]} outcomes of the betas counted in full and for {n3['same'][2]} "
          f"of the {n3['same'][3]} outcomes of the betas that hold estimates. The outcomes in which no quadruple violates "
          f"the rule are exactly the {n3r['kept']} for which the solvers answered \"unsatisfiable\" ("
        + join(f"{n3[n]['kept']} for the rule with {WORDS[n]} conditions" for n in sorted(RULES) if n != RULE_CONDITIONS)
        + f", again the solvers' sets), and they add up to the figure above. So the {len(kept)} answers behind the figure "
          f"are confirmed by a count as well as by solvers. For the betas that hold estimates this count gives "
          f"{n3['estimates']:.6f} where the calculator's estimates add up to {float(sum(part[b_] for b_ in flagged)):.6f}; "
          f"with it the count of all solutions is {n3['total']:,.4f}, the figure of the independent recount. Both programs "
          f"are the work of helper agents of the participant, instances of the same AI model. The answers behind \"no "
          f"further beta has a part\" remain answers of one solver without certificates.")
    cert = bool(drat) and drat["trim"] is None
    t["rule_cert_limit"] = (
        ("These answers come from three solvers on two formulas, which kept no proof certificate; from a third formula, for "
         "which one solver wrote proofs that a checker written by a helper agent accepted, no standard proof checker being "
         "used; and from an exact count of the E3 side split by the rule. " if cert else
         "These answers come from three solvers on two formulas, which kept no proof certificate, and from an exact count "
         "of the E3 side split by the rule. ")
        + "All of these programs were written and run by the participant's helper agents, instances of the same AI model.")
    t["rule_cert_claim"] = (
        "that it loses no more rests on solver answers and on an exact count of one call split by the rule, all made by the "
        "participant's helper agents"
        + ("; the solver answers have proofs that only a participant-side checker has accepted, no standard proof checker"
           if cert else "; the solver answers have no proof certificates"))
    t["rule_cert_note"] = (
        "that it loses no more rests on the answers \"unsatisfiable\" of SAT solvers and on an exact count of the second "
        "call split by the rule, both by my helper agents"
        + ("; the solver answers have proofs that a checker of a helper agent accepted, and no standard proof checker was "
           "used" if cert else "; the solver answers have no checked certificate"))
    t["rule_exact_claim"] = (
        f"An exact count of the second call split by the rule, by a reviewing helper agent's program, finds no violating "
        f"solution in the same {n3r['kept']} outcomes and gives {num(n3r['r_all'])} as the model's own value of the rate with "
        f"rule A; the claim keeps the smaller figure.")
    ex, so = own["lines"].get("EXAMPLE"), own["lines"].get("SOLUTION")
    if not ex or not so or ex.get("checked") != "1" or so.get("checked") != "1":
        raise SystemExit("the two completed solutions are missing: run tools/rule_a_sat.py <rule> example")

    def words_of(s):
        return (f"Y1 = {s['Y1']}, Y6 = {s['Y6']}, Y12 = {s['Y12']}, w12 = {s['w12']}, w5 = {s['w5']}, Y4 = {s['Y4']}, "
                f"Y9 = {s['Y9']}, Y14 = {s['Y14']}, w15 = 0, w8 = {s['w8']}.")
    t["solutions_paragraph"] = (
        f"*Two solutions, written out.* A complete solution of the seven-word system with Y4 in the class, which satisfies "
        f"rule A, in the names of 6.2: {words_of(so)} It has beta = {so['beta']}, tau = {so['tau']}, eps = {so['eps']} and "
        f"h1 = {so['h1']}. A complete solution of the seven-word system with Y4 in the class that violates rule A: "
        f"{words_of(ex)} It has beta = {ex['beta']}, tau = {ex['tau']}, eps = {ex['eps']} and h1 = {ex['h1']}. For both, E1 "
        f"and E3 evaluated for A and B with the G function alone give R = 0. They are solutions of the system, not messages: "
        f"no context is known that produces these seven words.")

    # ---- the other rules and the other factor
    alts = alternatives(d, oc, counts)
    t["rules_alt_paragraph"] = (
        f"Three rules were prepared, with four, five and six conditions, each containing the one before it: the rule with "
        f"four conditions is the first four lines of rule A, and the rule with six adds that bits 7 and 8 of h1 differ. The "
        f"submitted program contains all three and the long self-test was run for each. The same solver questions were put "
        f"for each rule. A rule with more conditions makes a trial cheaper, because fewer batches run stage 2, and gives up "
        f"more of the count. The package uses the cheapest rule that leaves the count at least {MIN_MARGIN} times the assumed "
        f"factor. The table gives, per rule (named by its number of conditions), the count that H1 would be set against, its ratio to the factors 2^{ALT_FACTORS[0]} "
        f"and 2^{ALT_FACTORS[1]}, the operations and loads of stage A, the budgeted and (in brackets) the charged cost of a "
        f"trial with the margin of this package, and the scalar that the package would submit with each factor.")
    ah = (f"| Rule | Count for H1 | / 2^{ALT_FACTORS[0]} | / 2^{ALT_FACTORS[1]} | Stage A | Per trial | 2^{ALT_FACTORS[0]} | 2^{ALT_FACTORS[1]} |\n"
          "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |\n")
    arows = []
    for r in alts:
        arows.append(f"| {r['n']} | {num(int(r['count']))} | {down(float(r['count']) / 2 ** ALT_FACTORS[0], 2):.2f} | "
                     f"{down(float(r['count']) / 2 ** ALT_FACTORS[1], 2):.2f} | {r['stage'][0]} + {r['stage'][1]} | "
                     f"{up(r['per'], 3):.3f} ({r['charge']}) | {r['times'][ALT_FACTORS[0]]:.1f} | {r['times'][ALT_FACTORS[1]]:.1f} |")
    t["rules_alt_table"] = ah + "\n".join(arows)
    mine = next(r for r in alts if r["n"] == RULE_CONDITIONS)
    if mine["charge"] != CHARGE or mine["times"][F] != d["time_log2"]:
        raise SystemExit("the row of the package in the table of the other rules is not the claim")
    r6 = next((r for r in alts if r["n"] == 6), None)
    t["rules_alt_after"] = (
        f"This package is the row with {WORDS[RULE_CONDITIONS]} conditions and the factor 2^{F}. The other rows and the "
        f"other column are stated so that the choice can be seen; none of them is claimed. With the factor 2^{F + 1} the "
        f"count of every rule is less than {MIN_MARGIN} times the factor.")
    t["rule6_lost_pct"] = f"{100 * r6['lost']:.1f}" if r6 else ""
    t["rule6_margin"] = f"{down(float(r6['count']) / 2 ** F, 2):.2f}" if r6 else ""

    # ---- checks of the calculator
    a1, a3 = ct["amc_e1"], ct["amc_e3"]
    t["check_amc_paragraph"] = (
        f"First, the two counts at 32 bits against the approximate model counter ApproxMC (tolerance 0.4, confidence 0.9), "
        f"for the sixteen outcomes with the largest products, which carry {100 * float(ct['top16'][1]):.0f}% of the count: the "
        f"E1 system and the E3 system of an outcome were each written as CNF straight from their definitions and their "
        f"solutions were counted. For E1, {a1[0]} of {a1[1]} outcomes were compared; the mean of log2(calculator / ApproxMC) "
        f"is {a1[2]} and the largest difference {a1[3]} bits. For E3, {a3[0]} of {a3[1]}; mean {a3[2]}, largest difference "
        f"{a3[3]} bits. ApproxMC is approximate, so this check excludes an error of a factor of two in a large outcome, not "
        f"a small one.")
    sy = ct["sys"]
    t["check_sys_paragraph"] = (
        f"Second, which betas have a part. For all {num(int(sy[0]))} betas with k at most 14 the solver was asked whether "
        f"the whole system has a solution with that beta: {sy[1]} are satisfiable, {num(int(sy[2]))} are not, none is "
        f"undecided; the {sy[1]} satisfiable ones are exactly the {word(part14)} betas with a part, and all {sy[5]} models "
        f"are solutions in plain arithmetic. Over all {num(valid)} betas the satisfiable ones ({sat_b}) are exactly the betas "
        f"with a part ({len(order_b)}).")
    b1, b1b, b3 = ct["bf_e1"], ct["bf_e1b"], ct["bf_e3"]
    t["check_bf_paragraph"] = (
        f"Third, both counts against brute force with 8-bit words. The E1 count with a difference of 8 or -8 between the two "
        f"words: for {b1[0]} random cases, all {num(int(b1[1]))} outcomes that have solutions were compared and "
        f"{num(int(b1[2]))} are equal; of the outcomes without solutions, {num(int(b1[4]) + int(b1[5]))} were sampled and "
        f"{num(int(b1[4]))} are zero in the calculator as well. A second seed with {b1b[0]} cases gave {num(int(b1b[2]))} of "
        f"{num(int(b1b[1]))}. The E3 count: for {b3[0]} cases, {num(int(b3[2]))} of {num(int(b3[1]))} outcomes with solutions "
        f"equal, and {num(int(b3[4]))} sampled outcomes without solutions agree.")
    t["check_sampler_paragraph"] = (
        "Fourth, the sampler, for the four heaviest betas, as reported under the table of the count. Fifth, the independent "
        "recount reported above: another method, another program, integer arithmetic, every beta. It is the only one of "
        "these checks that covers both factors of every outcome. It was a confirmation with the total and four parts "
        "known to the other model, not a blind recount.")

    # ---- the solver search
    found, same_len, info, longest, cands, want = read_search()
    own_c = [c for c in cands if c[1] == want]
    others = sorted((c for c in cands if c[1] != want), reverse=True)
    vals = sorted(c[0] for c in others)
    median = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
    if info["eta"] != hx(ETA) or not own_c or abs(own_c[0][0] - float(part.get(info["beta"], 0))) > 0.06:
        raise SystemExit("the solver's solution is not in the class of the package, or its beta does not have the part of the count")
    t["search_paragraph"] = (
        f"The constants come from the solver search of submission {SUBMISSIONS[-1][0]}, not from farming random sets. One CNF "
        f"instance holds, with real word values: the call C3 for both messages with equal b and d outputs, so that every "
        f"model is a set of constants with the property of Fact P; E1 and E3 for both messages; a zero residual; and a bound "
        f"on the number of bit positions, bit 31 excepted, at which a difference is active in six additions of E1 and E3. "
        f"For this package the instance was changed in two places: the two words w4 differ as the length cancellation "
        f"prescribes for the XOR of the two lengths, and the top byte of the pinned word 13 is zero. The solver is kissat. "
        f"The search was run for several XORs of the two lengths other than 2; its log holds {found} sets of constants, "
        f"{same_len} of them for the XOR {LEN_A ^ LEN_B}, from runs of up to {-(-longest // 60)} minutes each. The constants of 3.2 came from an instance "
        f"with bound {info['bound']}, after {num(info['seconds'])} seconds, with {info['cost']} active positions; the "
        f"solver's solution has eta = {info['eta']} and beta = {info['beta']}. The class of this package is the class of "
        f"that solution, and its beta is the heaviest beta of the count. For every set of the log, the beta of the solver's "
        f"solution was counted in the class of that solution: the constants of 3.2 had the largest value, "
        f"{num(own_c[0][0])}; the largest of the others was {num(others[0][0])} and their median {num(median)}. The bound "
        f"steers the search towards solutions that are reached with high probability under M; the count, not the bound, is "
        f"what H1 is set against. " + neighbours_sentence())
    t["search_note"] = (f"The search returned {found} sets of constants for several length XORs other than 2, {same_len} of them "
                        f"for the XOR {LEN_A ^ LEN_B}; the one used here came from an instance with bound {info['bound']} after "
                        f"{num(info['seconds'])} seconds.")
    t["search_choice_note"] = (
        f"For every set that the search returned, the beta of the solver's solution was counted in the class of that "
        f"solution. The constants used here had the largest value, {num(own_c[0][0])}; the largest of the others was "
        f"{num(others[0][0])}. The class is the class of the solver's solution.")

    # ---- checks of the construction on real messages
    host = read_host()
    chk = read_check_run()
    pieces = []
    if host["ref_triples"] and host["ref_triples"][2] and host["ref_hash"] and host["ref_hash"][1]:
        pieces.append(
            f"A reference program for steps S1 and T, written before this text from the solved equations and not from the "
            f"experiment program, built {num(host['ref_triples'][0])} trials ({num(host['ref_triples'][1])} random contexts, 50 "
            f"members each) and hashed both messages of each with a forward compression that equals the organizer's reference "
            f"hash on {num(host['ref_hash'][0])} random messages: in all of them the lengths are 55 and 63, the last eight "
            f"bytes of B and the words 14 and 15 are zero, the states after round 0 are equal, the four constants are in "
            f"place, Y4 is the prescribed member in A and in B, digest words 0, 2, 5 and 7 agree and the difference of E3's "
            f"first-half d value is eta.")
    if chk:
        pieces.append(
            f"A second program, written separately from the experiment program, has the lines of steps S1 and T a second "
            f"time, name by name; on {num(chk[0])} random trials it runs round 0 and round 1 forwards on the trial's words and "
            f"compares every one of the nine calls of Lemmas S, F and Y, with all its eight values, with the names of the "
            f"lines, and checks Lemmas L, Q, T, E, N and A on the same trials; all of its checks hold.")
    typed = read_proof_lines()
    if typed:
        pieces.append(
            f"The lines of the two displays of Section 4 were also typed again from this text, with its names, and run on "
            f"{num(typed)} trials, half of them with a word y outside the class: the sixteen words are those of the submitted "
            f"program, a forward round 0 gives the state S and the state X of the text, and each of the nine calls has the "
            f"eight values that Lemmas S, F and Y state.")
    else:
        print("NOTE: evidence/proof_lines_check.txt is not for src/proof_head.md as it is; its sentence is left out "
              "(python -B tools/proof_lines_check.py, then build again)")
    if host["gpu_check"] and host["vectors"]:
        pieces.append(
            f"The program that produced the measurements below was checked against {num(host['vectors'][0])} test vectors of "
            f"the reference (message words and both digests equal in all) and on {num(host['gpu_check'][1])} of its own "
            f"trials, rebuilt as real strings of 55 and 63 bytes and hashed completely on the host: "
            + ("all" if host["gpu_check"][0] == host["gpu_check"][1] else num(host["gpu_check"][0]))
            + " agree on digest words 0, 2, 5 and 7, have Y4 in the class, the pinned words in place and the residual that "
              "6.2 computes.")
    pieces.append(
        f"The self-test of the submitted program checks every lane of its batches against the complete digests of the two "
        f"messages of the lane's trial (6.5).")
    if host["fullcheck"] and host["fullcheck"][0] == host["fullcheck"][1]:
        pieces.append(
            f"An earlier scalar program for the same batch checked {num(host['fullcheck'][1])} trials of 32 contexts in the same "
            f"way: all agree on the four digest words, and in all the word n of Lemma N equals D3 XOR ROL(D6, 8) of the two "
            f"digests.")
    pieces.append("These are checks on random inputs. They do not prove the lemmas; Section 4 does.")
    t["construction_checks_paragraph"] = " ".join(pieces)
    t["construction_note"] = (
        (f"A reference program built {num(host['ref_triples'][0])} trials and hashed both messages of each with a compression "
         f"that equals the organizer's reference hash: all agree on digest words 0, 2, 5, 7 and have the prescribed Y4. "
         if host["ref_triples"] and host["ref_triples"][2] else "")
        + (f"The program of the measurements was checked on {num(host['gpu_check'][1])} of its own trials, hashed completely "
           f"on the host." if host["gpu_check"] else ""))
    t["check_trials"] = num(chk[0]) if chk else "20,000"
    t["check_result"] = f"{chk[1]} checks, all hold" if chk else "run with the validation, see FILE_STEPS"
    t["exact_review_sentence"] = EXACT_REVIEW
    t["review_claim"] = REVIEW_CLAIM
    t["version_review_sentence"] = VERSION_REVIEW

    # ---- the model on real messages
    # Every count of this part is added up here from the raw result files of the runs (evidence/h8/runs, copied by
    # tools/fetch_h8.py), so that runs finished after the groundwork's comparing file was written are in the text. The
    # comparing file (evidence/h8/H8_gpu_compare.txt) is quoted for its comparisons of real trials with draws from M
    # and for its list of deviations only.
    gpu = read_gpu()
    runs = read_runs()
    dexp = read_deep_expected()
    ctx = read_ctx()
    ind, lay, spr, mod, seeds = runs["independent"], runs["layout"], runs["spread"], runs["model"], runs["seeds"]
    if (len(lay), len(spr)) != (24, 8):
        raise SystemExit("the text describes 24 layout runs (eight first, sixteen later) and eight spread runs")

    def pooled(rows):
        s = {k: sum(r[k] for r in rows) for k in ("trials", "beta", "tau", "outcome", "e3", "rule", "joint", "early", "e1pass")}
        s["log2"] = math.log2(s["trials"])
        return s

    def deep_line(s, key, label):
        e, z = s["trials"] * dexp[key], zbin(s[key], s["trials"], dexp[key])
        return f"{label} {num(s[key])} against {e:,.0f} expected ({z:+.2f})" if e >= 1e6 else \
            f"{label} {num(s[key])} against {e:,.2f} expected ({z:+.2f})"

    def outcome_line(s):
        return f"{s['outcome']} against {s['trials'] * dexp['outcome']:.2f}"

    p_ind, p_lay, p_spr, p_mod, p_real = pooled(ind), pooled(lay), pooled(spr), pooled(mod), pooled(ind + lay + spr)
    cmp_old, cmp_new = gpu["deep"]["all real trials pooled"], pooled(ind[:3] + lay[:8])
    if tuple(cmp_old[k][0] for k in GPU_STATS) != tuple(cmp_new[k] for k in ("rule", "beta", "tau", "outcome", "e3")) \
            or abs(cmp_old["log2"] - cmp_new["log2"]) > 0.005:
        raise SystemExit("the counts added up from the raw run files are not those of the groundwork's comparing file for its runs")
    t["gpu_layout_note"] = (
        "Three layouts of real trials were used. In the runs with *independent contexts* every thread of the generating "
        "program draws its own context, seven random words, and makes its trials in it with random members of the class. In "
        "a *layout run* one sextuple (vc, vd, S11, S4, X13, w0) is drawn at random and held, X14 runs through 2^21 "
        "consecutive values and every member of the class is tried for each: 2^40 trials. A layout run is laid out like the "
        "work of step 2 for one pair (vc, vd), of which it covers a share 2^-11, except that its vd is a random 32-bit "
        f"word and not one below 2^{d['d_bits']}. Different layout runs have different sextuples. A *spread run* has the "
        "sextuple and the first value of X14 of one of the first eight layout runs, and its 2^21 values of X14 lie a fixed "
        "odd step apart, so that they are spread over all 2^32 values; the eight spread runs were made as a diagnostic "
        "after the first eight layout runs. No run has the structure of a whole run of 6.4, in which all pairs share four "
        "seed words.")
    pair_text = []
    for la, lb, rows in gpu["pairs"]:
        rows = [r for r in rows if r[1] + r[2] >= 30]
        worst = max(rows, key=lambda r: abs(r[3]))
        pair_text.append(f"2^{la} real trials against 2^{lb} draws from M: {len(rows)} statistics with at least 30 events, "
                         f"largest deviation {worst[3]:+.2f} standard deviations ({stat_name(worst[0])})")
    beyond_rule = [l for l in gpu["beyond"] if "rule on h1 passes" in l]
    beyond_spread = [l for l in beyond_rule if re.match(r"5[bc] \| ", l)]
    beyond_other = [l for l in gpu["beyond"] if "rule on h1 passes" not in l]
    pattern_ab = re.compile(r"(\d+) \| (.+?): A (\d+), B (\d+), z ([-+][\d.]+)")
    others_ab = [pattern_ab.match(l) for l in beyond_other]
    if not others_ab or any(m is None for m in others_ab) or len({(m.group(1), m.group(3), m.group(4)) for m in others_ab}) != 1:
        raise SystemExit("the list of deviations beyond three standard deviations is not the one that the text describes")
    ab_section, ab_real, ab_model = others_ab[0].group(1), others_ab[0].group(3), others_ab[0].group(4)
    ab_level = {"1": 40, "2": 42}.get(ab_section)
    if ab_level is None or not beyond_spread:
        raise SystemExit("the deviations beyond three standard deviations are not those that the text describes")
    t["real_model_paragraph"] = (
        "*Real trials against draws from M, independent contexts.* " + "; ".join(pair_text) + ". "
        f"The comparing program of the groundwork had the runs with independent contexts of 2^40, 2^42 and 2^45 trials, the "
        f"first eight layout runs, the eight spread runs and the draws from M. Over all comparisons that it made, between "
        f"these runs and with the exact expectations, {num(gpu['tests'])} tests in all, {len(gpu['beyond'])} are beyond three "
        f"standard deviations, where about {gpu['chance']:.1f} are expected by chance. {word(len(beyond_rule), True)} of them "
        f"concern the first four conditions of rule A in the layout runs and the spread runs, {word(len(beyond_spread))} of "
        f"the {word(len(beyond_rule))} in the spread runs; they are the subject of the next heading. The other "
        f"{word(len(beyond_other))} are one event counted under {word(len(beyond_other))} names, the first residual word being "
        f"zero, in the comparison at 2^{ab_level} ({num(int(ab_real))} real against {num(int(ab_model))} from M); it does not "
        f"repeat in the larger comparison.")
    t["deep_exp"] = f"{-math.log2(dexp['outcome']):.0f}"
    seeds_text = (f" and {word(len(seeds))} later run{'s' if len(seeds) != 1 else ''} of 2^45 trials each, those that were "
                  f"finished when this text was built" if seeds else "")
    six = [b_ for b_, _ in dexp["per_beta"][:6]]
    six_label = "the six heaviest betas" if set(six) == set(order_b[:6]) else "the first six betas of the list"
    real_rows = ind + lay + spr
    t["deep_paragraph"] = (
        f"*Real trials against exact expectations.* For the events whose probability under M is known from the count, the "
        f"counts were added up from the result files of every finished run with real trials: {word(len(ind))} runs with "
        f"independent contexts (2^40, 2^42 and 2^45 trials{seeds_text}), the {len(lay)} layout runs and the "
        f"{word(len(spr))} spread runs, 2^{p_real['log2']:.2f} trials together. They give: "
        + deep_line(p_real, "beta", "listed beta,") + "; "
        + deep_line(p_real, "tau", "listed beta with a listed tau,") + "; "
        + deep_line(p_real, "e3", "listed partial E3 event,")
        + f"; and listed E1 outcome, {outcome_line(p_real)} expected (a Poisson count; the probability of a count this far "
          f"from its mean is {poisson_two_sided(p_real['outcome'], p_real['trials'] * dexp['outcome']):.2f}). The numbers in "
          f"brackets are standard deviations. The runs with independent contexts alone, 2^{p_ind['log2']:.2f} trials, give: "
        + deep_line(p_ind, "beta", "listed beta,") + "; " + deep_line(p_ind, "tau", "with a listed tau,") + "; "
        + deep_line(p_ind, "e3", "listed partial E3 event,") + f"; listed E1 outcome, {outcome_line(p_ind)}. "
        + f"The listed E1 outcome has probability about 2^-{-math.log2(dexp['outcome']):.1f} per trial and the listed "
          f"partial E3 event about 2^-{-math.log2(dexp['e3']):.1f}; these are the deepest events on which M was compared "
          f"with real messages, each on one call alone. Per beta, the listed E1 outcomes observed and expected in all real "
          f"runs for {six_label} are "
        + join(f"{sum(r['per_beta'].get(b_, 0) for r in real_rows)} and {p_real['trials'] * p_:.2f}" for b_, p_ in dexp["per_beta"][:6])
        + f". The same events in the 2^{p_mod['log2']:.2f} draws from M agree with the exact expectations as well ("
        + deep_line(p_mod, "beta", "listed beta,") + "; " + deep_line(p_mod, "tau", "with a listed tau,") + "; "
        + deep_line(p_mod, "e3", "listed partial E3 event,") + f"; listed E1 outcome, {outcome_line(p_mod)}), which checks "
          f"the expectations against the program that draws from M.")
    early = [r["early"] for r in lay]
    e1p = [r["e1pass"] for r in lay]
    m_all, d_all, c_all, p_all = spread(early)
    m_8, d_8, c_8, p_8 = spread(early[:8])
    m_16, d_16, c_16, p_16 = spread(early[8:])
    _, d_e1, c_e1, p_e1 = spread(e1p)
    model_early = next((r["early"] for r in mod if r["log2"] == 40), None)
    t["layout_runs"] = str(len(lay))
    t["layout_paragraph"] = (
        f"*Layout runs.* {len(lay)} layout runs of 2^40 trials were made, eight first and sixteen later with the same "
        f"program and arguments. The passes of the early test per run have mean {m_all:,.1f}"
        + (f" (the model run of 2^40 draws gave {num(model_early)})" if model_early else "")
        + f" and a ratio of variance to mean of {d_all:.3f}, where 1 is the value for independent trials (chi-square "
          f"{c_all:.2f} on {len(lay) - 1} degrees of freedom, probability {p_all:.2f}). The first eight runs alone have "
          f"{d_8:.2f} (chi-square {c_8:.2f} on 7, probability {p_8:.3f}) and the sixteen later ones {d_16:.3f} (probability "
          f"{p_16:.2f}). The value of the first eight was known before the sixteen were started, and the sixteen were made "
          f"to see whether it would repeat; it did not. The passes of the E1 test per run have a ratio of {d_e1:.2f} "
          f"(probability {p_e1:.2f}). In the {len(lay)} runs together the listed events are "
        + deep_line(p_lay, "beta", "listed beta,") + "; "
        + deep_line(p_lay, "tau", "with a listed tau,") + "; "
        + deep_line(p_lay, "e3", "listed partial E3 event,")
        + f"; listed E1 outcome, {outcome_line(p_lay)}. These runs test the spread between pairs (vc, vd) with independent "
          f"seed words on events of probability about 2^-24 and above. They do not test a run of 6.4.")
    s_early = [r["early"] for r in spr]
    _, d_s, c_s, p_s = spread(s_early)
    t["spread_paragraph"] = (
        f"*Spread runs.* The {word(len(spr))} spread runs, 2^40 trials each, have " + ", ".join(num(v) for v in s_early[:-1])
        + f" and {num(s_early[-1])} passes of the early test, a ratio of variance to mean of {d_s:.2f} (chi-square {c_s:.2f} "
          f"on {len(spr) - 1}, probability {p_s:.2f}). Their listed events together are "
        + deep_line(p_spr, "beta", "listed beta,") + "; " + deep_line(p_spr, "tau", "with a listed tau,") + "; "
        + deep_line(p_spr, "e3", "listed partial E3 event,") + f"; listed E1 outcome, {outcome_line(p_spr)}.")
    t["layout_limit_sentence"] = (
        f"The layout runs hold one sextuple of outer words each and cover 2^21 of the 2^32 values of X14; the first eight "
        f"had a ratio of variance to mean of {d_8:.2f} in the passes of the early test, which the sixteen later runs did not "
        f"repeat ({d_16:.2f}; all {len(lay)}: {d_all:.2f}). No run on the graphics card shares seed words between pairs as a "
        f"run of 6.4 does, or has a vd below 2^{d['d_bits']}; the processor runs that do, reported under rule A, measure "
        f"only the share of the trials that satisfy the rule.")
    t["layout_claim_limit"] = (
        f"Real trials in a layout with shared outer words exist on the graphics card only as {len(lay)} runs of 2^40 trials, "
        f"each a share 2^-11 of the work for one pair of enumerated words, and eight more with the third enumerated word "
        f"spread out; the ratio of variance to mean of the early-test passes of the {len(lay)} is {d_all:.2f} (first eight "
        f"alone {d_8:.2f}).")
    t["layout_limit_note"] = (
        f"The {len(lay)} runs laid out with shared outer words each cover a share 2^-11 of the work for one pair; the "
        f"ratio of variance to mean of their early-test passes is {d_all:.2f} (first eight alone {d_8:.2f}). No run on the "
        f"graphics card shares seed words between pairs.")

    # ---- rule A on real trials
    p4 = 2.0 ** -4
    lo_r, hi_r = ctx["low"] / ctx["members"] / p4, ctx["high"] / ctx["members"] / p4
    rr = {name: rule_runs(rows, ctx["var"], ctx["members"]) for name, rows in
          (("first", lay[:8]), ("later", lay[8:]), ("all", lay), ("spread", spr), ("both", lay + spr))}
    share = read_rule_share_h8()
    share2 = read_rule_share_h8(run=RULE_SHARE_H8_SECOND)
    lshare = read_rule_share_h8(layout=True)
    if not (share and share2 and lshare):
        raise SystemExit("a file of tools/rule_share_h8.py is missing or is not for the program and the tool as they are: run it "
                         "for RULE_SHARE_H8_RUN, RULE_SHARE_H8_SECOND and RULE_SHARE_H8_LAYOUT (FILE_STEPS.md)")
    rev = read_share_review()
    lrev = read_layout_review()
    n_r = RULE_CONDITIONS
    if n_r != 5 or lrev is None:
        raise SystemExit("the paragraphs on rule A on the processor are written for the rule with five conditions and need "
                         "evidence/rule_layout_review_h8.txt (tools/rule_layout_review_h8.py)")
    # smallest and largest share of the trials of ONE context, over 2^-n, in every sample on the processor
    ext4 = [(share["spread"][4]["low"], share["spread"][4]["high"]), (share2["spread"][4]["low"], share2["spread"][4]["high"]),
            (lshare["spread"][4]["low"], lshare["spread"][4]["high"]), (rev["a"][4]["low"], rev["a"][4]["high"]),
            (rev["b"][4]["low"], rev["b"][4]["high"]), lrev["r4"][2:4]]
    ext5 = [(share["spread"][5]["low"], share["spread"][5]["high"]), (share2["spread"][5]["low"], share2["spread"][5]["high"]),
            (lshare["spread"][5]["low"], lshare["spread"][5]["high"]), (rev["a"][5]["low"], rev["a"][5]["high"]),
            (rev["b"][5]["low"], rev["b"][5]["high"]), lrev["r5"][3:5]] + [(p_["low"], p_["high"]) for p_ in lrev["pairs"]]
    low4, high4 = min(v[0] for v in ext4), max(v[1] for v in ext4)
    low5, high5 = min(v[0] for v in ext5), max(v[1] for v in ext5)
    batch_max = max([share[n_r]["largest"], share2[n_r]["largest"], lshare[n_r]["largest"], lrev["batches"][2]]
                    + [p_["batch_max"] for p_ in lrev["pairs"]])
    batch_contexts = share["contexts"] + share2["contexts"] + lshare["contexts"] + lrev["contexts"] + len(lrev["pairs"]) * lrev["values"]
    budget_share = 1 / 2 ** STAGE_2_LOG2_SHARE
    if not batch_max < budget_share:
        raise SystemExit("a context of the samples reaches the stage-2 budget in batches: the text says none does")
    zi = zbin(p_ind["rule"], p_ind["trials"], p4)
    t["ctx_paragraph"] = (
        f"The programs for the graphics card record the first four conditions of rule A (bits 0, 1, 16 and 17 of h1), which "
        f"a uniform word satisfies with probability 2^-4. In a sample of {num(ctx['contexts'])} independent contexts, each "
        f"with all {num(ctx['members'])} members, the number of members that satisfy them has mean {ctx['mean']:,.1f}, which "
        f"is 2^-{ctx['rate']:.4f} of the members, but a variance of {ctx['var']:,.0f} where independent trials would give "
        f"{ctx['binomial']:,.0f}: {ctx['dispersion']:.0f} times as much. In that sample a single context has between "
        f"{num(ctx['low'])} and {num(ctx['high'])} such members, that is between {lo_r:.2f} and {hi_r:.2f} times 2^-4. These "
        f"are the smallest and the largest value of one sample and not bounds: the samples on the processor reported below "
        f"have values from {down(low4, 2):.2f} to {up(high4, 2):.2f}. So inside one context the trials do not satisfy the "
        f"conditions like independent uniform words: the share depends on the context, with a standard deviation of "
        f"{100 * ctx['sd_rel']:.1f}% of its mean. In the same contexts a single one of the four conditions is far more "
        f"regular than independent trials would be (its count has {ctx['bit_dispersion']:.3f} of the binomial variance), and "
        f"the event that E1 has a listed beta is as for independent trials (ratio {ctx['beta_dispersion']:.3f}). The cause "
        f"of this structure was not analysed. Averaged over contexts the share is the model's: in all runs with independent "
        f"contexts together, {num(p_ind['rule'])} trials satisfy the four conditions where 2^-4 of the trials is "
        f"{p_ind['trials'] / 16:,.0f} ({zi:+.2f} standard deviations of a binomial count).")

    def parts(x):
        return f"{math.ceil(x - 1e-9)} parts in 100,000"

    def side(z):
        return "below" if z < 0 else "above"

    ra, r8, r16, rs_ = rr["all"], rr["first"], rr["later"], rr["spread"]
    cc, cs = read_ctx_run("consecutive"), read_ctx_run("spread")
    if not (cc["start"] == cs["start"] == lay[0]["outer"][1]) or not (cc["members"] == cs["members"] == ctx["members"]):
        raise SystemExit("the per-context files of layout run 1 do not start at the X14 of that run or have other members")
    mean_ppm = (p_lay["rule"] / (p_lay["trials"] / 16) - 1) * 1e6
    if max(abs(r_["own"]) for r_ in (ra, r8, r16, rs_)) >= 2.5:
        raise SystemExit("a group of layout or spread runs differs from 2^-4 by 2.5 standard errors of its own scatter: the "
                         "text says that none differs significantly")
    t["rule_runs_paragraph"] = (
        f"*The four conditions in the layout runs and the spread runs.* In a layout run 2^21 contexts share their outer "
        f"words and have consecutive values of X14. In each of the {ra['runs']} layout runs the share of the trials that "
        f"satisfy the four conditions is within {parts(ra['parts'])} of 2^-4; {ra['below']} of the {ra['runs']} are below it, "
        f"and their mean is {abs(mean_ppm):.1f} parts in a million {side(mean_ppm)} it. The variance of the {ra['runs']} "
        f"counts is {ra['disp']:.1f} times the binomial one (first eight {r8['disp']:.1f}, the sixteen later ones "
        f"{r16['disp']:.1f}). Added up, the {ra['runs']} runs are {abs(ra['pooled']):.2f} binomial standard deviations "
        f"{side(ra['pooled'])} 2^-4; the first eight alone are {abs(r8['pooled']):.2f} {side(r8['pooled'])} and the sixteen "
        f"later ones {abs(r16['pooled']):.2f} {side(r16['pooled'])}. The binomial yardstick does not fit, because the runs "
        f"scatter more than binomial counts do. Measured with the scatter of the runs themselves, the {ra['runs']} together "
        f"are {abs(ra['own']):.1f} standard errors {side(ra['own'])} 2^-4 ({ra['runs'] - 1} degrees of freedom), the first "
        f"eight alone {abs(r8['own']):.1f} {side(r8['own'])} (7 degrees of freedom) and the sixteen later ones "
        f"{abs(r16['own']):.1f} {side(r16['own'])} (15 degrees of freedom). The variance between independent contexts found "
        f"above is not the yardstick either. Single contexts of a layout run do scatter like independent contexts: for the "
        f"sextuple of layout run 1 the program that counts per context was run on {num(cc['contexts'])} contexts with "
        f"consecutive values of X14 and on {num(cs['contexts'])} with values a fixed odd step apart, and the count of one "
        f"context has {cc['dispersion']:.0f} and {cs['dispersion']:.0f} times the binomial variance and lies between "
        f"{down(cc['low'] / cc['members'] / p4, 2):.2f} and {up(cc['high'] / cc['members'] / p4, 2):.2f}, and between "
        f"{down(cs['low'] / cs['members'] / p4, 2):.2f} and {up(cs['high'] / cs['members'] / p4, 2):.2f}, times 2^-4. A run of "
        f"independent contexts would then have about {ctx['dispersion']:.0f} times the binomial variance, and the layout "
        f"runs have {ra['disp']:.1f}: the deviations of the contexts of a run largely cancel in its sum (with the variance "
        f"of independent contexts the first eight would be {abs(r8['indep']):.1f} standard deviations {side(r8['indep'])} "
        f"2^-4 and all {ra['runs']} {abs(ra['indep']):.1f}). The {word(rs_['runs'])} spread runs have {rs_['disp']:.1f} times "
        f"the binomial variance; each is within {parts(rs_['parts'])} of 2^-4, and together they are {abs(rs_['pooled']):.2f} "
        f"binomial standard deviations {side(rs_['pooled'])} it, which is {abs(rs_['own']):.1f} standard errors of their own "
        f"scatter (7 degrees of freedom). So these runs show the dependence on the context again, and measured with the "
        f"scatter of the runs themselves no group of runs differs significantly from 2^-4.")
    # the rule together with a deep event of E3
    e3s = read_e3_share()
    if abs(float(e3s["p_event"]) / dexp["e3"] - 1) > 1e-12:
        raise SystemExit("evidence/e3_rule_share_h8.txt and evidence/h8/h8_deep_expected.txt differ on the listed partial E3 event")
    s4 = float(e3s["share"][4])

    def joint(s, label):
        return (f"{label} {num(s['joint'])} of {num(s['e3'])}, a share of {s['joint'] / s['e3']:.4f} "
                f"({zbin(s['joint'], s['e3'], s4):+.2f})")

    z_mod = zbin(p_mod["joint"], p_mod["e3"], s4)
    t["joint_paragraph"] = (
        f"*The four conditions together with an event of E3.* The programs for the graphics card also count, among the "
        f"listed partial E3 events, those whose h1 satisfies the four conditions. This is the one measurement that joins "
        f"the rule with a deep event of the call that h1 belongs to; the event has probability about "
        f"2^-{-math.log2(dexp['e3']):.1f} per trial. The share to expect under M is far from 2^-4, because the event and "
        f"the rule both depend on h1. It was computed exactly, by an enumeration that a reviewing helper agent wrote from "
        f"the definitions of 6.2 and that was run again for this text: its counts of the {e3s['events']} listed events equal "
        f"those of the list for all {e3s['events']}, and under M a share of {s4:.6f} of the listed partial E3 events have an "
        f"h1 that satisfies the four conditions ({float(e3s['share'][5]):.6f} for the five conditions of rule A, "
        f"{float(e3s['share'][6]):.6f} for six). On real trials: "
        + joint(p_real, "all runs together,") + "; " + joint(p_ind, "the runs with independent contexts,") + "; "
        + joint(p_lay, f"the {len(lay)} layout runs,") + "; " + joint(p_spr, "the spread runs,")
        + f". The numbers in brackets are standard deviations from the exact share. The draws from M have "
          f"{num(p_mod['joint'])} of {num(p_mod['e3'])}, a share of {p_mod['joint'] / p_mod['e3']:.4f}, which is "
          f"{abs(z_mod):.2f} standard deviations {side(z_mod)} the exact share under M itself: where the real trials look low "
          f"against these draws, it is the draws that are high. So where the first four conditions of the rule meet an "
          f"event of E3 of this depth, the real trials have the model's share. This measurement does not have the fifth "
          f"condition, it is an event of one call, and it is far from R = 0.")
    # rule A with all its conditions, on the processor
    rs, rs2, rl = share[n_r], share2[n_r], lshare[n_r]
    sp, sp2, spl = share["spread"][n_r], share2["spread"][n_r], lshare["spread"][n_r]
    rate = rs["passes"] / share["trials"]
    if not 7 * max(rate, rs2["passes"] / share2["trials"], rl["passes"] / lshare["trials"]) < budget_share:
        raise SystemExit("seven times a measured share is not below the stage-2 budget")
    t["ctx_share_max"] = f"{up(high5, 2):.2f}"
    t["batch_share_random"] = f"{rs['entered'] / share['batches']:.4f}"
    t["batch_share_layout"] = f"{rl['entered'] / lshare['batches']:.4f}"
    t["batch_share_max"] = f"{up(batch_max, 4):.4f}"
    t["batch_contexts"] = num(batch_contexts)
    t["budget_share"] = f"{budget_share:.2f}"
    t["rule_real_paragraph"] = (
        f"*Rule A with all its conditions (processor).* The fifth condition is not recorded by the programs for the "
        f"graphics card. A participant tool that uses the context and the trial of the submitted program counted the three "
        f"rules on the processor, for {num(share['contexts'])} random contexts with all {num(d['members'])} members each, 2^"
        f"{math.log2(share['trials']):.0f} real trials: {num(rs['passes'])} trials satisfy rule A, a share of "
        f"2^-{rs['log2']:.4f}. They are {rs['passes'] / share[4]['passes']:.5f} of the trials that satisfy the first four "
        f"conditions, so the fifth condition halves the count. The share of one context is {sp['mean']:.4f} times 2^-{n_r} on "
        f"average, with a standard error of {sp['se']:.4f}, and in that sample it lies between {down(sp['low'], 2):.2f} and "
        f"{up(sp['high'], 2):.2f} times 2^-{n_r}. {num(rs['entered'])} of the {num(share['batches'])} batches hold a trial that "
        f"satisfies rule A, a share of {rs['entered'] / share['batches']:.4f}; in that sample the share of the batches of one "
        f"context lies between {rs['smallest']:.4f} and {rs['largest']:.4f}. A second run of the tool with another seed, "
        f"again {num(share2['contexts'])} contexts, gives 2^-{rs2['log2']:.4f}, that is {sp2['mean']:.4f} times 2^-{n_r} with a "
        f"standard error of {sp2['se']:.4f}; one context between {down(sp2['low'], 2):.2f} and {up(sp2['high'], 2):.2f} times "
        f"2^-{n_r}; a share of {rs2['entered'] / share2['batches']:.4f} of the batches, for one context between "
        f"{rs2['smallest']:.4f} and {rs2['largest']:.4f}. The budget of step 4 is {budget_share:.3f} of the batches of a run. "
        f"No context of the samples of this section reaches the budget in batches: the largest share of the batches of one "
        f"context is {up(batch_max, 4):.4f}, among {num(batch_contexts)} contexts. But the bound that H3 uses, one batch per "
        f"trial that satisfies the rule, is exceeded by single contexts and holds only on average: seven times the average "
        f"share of the trials is {7 * rate:.4f}, and seven times the largest share of one context in these samples, "
        f"{up(high5, 2):.2f} times 2^-{n_r}, is {7 * up(high5, 2) / 2 ** n_r:.3f}.")
    qm = spl["quads"]
    if len(qm) != lshare["quads"] or spl["pairs"] != lshare["quads"] * lshare["pairs"]:
        raise SystemExit("the layout run of tools/rule_share_h8.py does not have the means that the text quotes")
    t["rule_layout_paragraph"] = (
        f"*Rule A in the ranges of the algorithm (processor).* The same tool was run with contexts laid out as step 2 lays "
        f"them out: {word(lshare['quads'])} sets of the four seed words, for each set {word(lshare['pairs'])} pairs (vc, vd) "
        f"with vd below 2^{d['d_bits']}, and for each pair {lshare['values']} consecutive values of X14 from a random start; "
        f"{num(lshare['contexts'])} contexts with all members, 2^{math.log2(lshare['trials']):.0f} trials. {num(rl['passes'])} "
        f"trials satisfy rule A, a share of 2^-{rl['log2']:.4f}: {spl['mean']:.4f} times 2^-{n_r}, with a standard error of "
        f"{spl['se']:.4f} from the scatter of the {spl['pairs']} pair means. The means of the {word(lshare['quads'])} sets lie "
        f"between {min(qm):.4f} and {max(qm):.4f}, and single contexts between {down(spl['low'], 2):.2f} and "
        f"{up(spl['high'], 2):.2f}. The share of the batches that hold such a trial is {rl['entered'] / lshare['batches']:.4f}, "
        f"for one context at most {rl['largest']:.4f}; for random contexts it was {rs['entered'] / share['batches']:.4f}. For "
        f"the rules with four and six conditions the shares are {lshare['spread'][4]['mean']:.4f} times 2^-4 and "
        f"{lshare['spread'][6]['mean']:.4f} times 2^-6. The start of X14 is random here; the algorithm starts every pair at "
        f"X14 = 0.")
    ra_, rb_, rc_, rd_ = rev["a"][n_r], rev["b"][n_r], rev["c"][n_r], rev["d"][n_r]
    l5, lb = lrev["r5"], lrev["batches"]
    l5_se = l5[0] * l5[2] / 100 / math.sqrt(lrev["contexts"])
    samples = [("the first run of the participant tool", sp["mean"], sp["se"]), ("its second run", sp2["mean"], sp2["se"]),
               ("its run in the ranges of the algorithm", spl["mean"], spl["se"]),
               ("the first review program, independent contexts", ra_["mean"], ra_["se"]),
               ("the same with vd restricted", rb_["mean"], rb_["se"]),
               ("the second review program, independent contexts", l5[0], l5_se)]
    zs = [(m_ - 1) / se_ for _, m_, se_ in samples]
    if max(abs(z) for z in zs) >= 2.5:
        raise SystemExit("a mean share of rule A on the processor is 2.5 standard errors from 2^-5: the text says none is far")
    t["rule_review_paragraph"] = (
        f"*Two programs of reviewing helper agents, run again (processor).* Two of the helper agents that reviewed this "
        f"text measured the same share with implementations of their own, typed from Sections 1, 4 and 6 of this text and "
        f"not taken from the submitted program. Both programs were run again for this text. The first checks its "
        f"construction on {num(rev['trials'])} real trials with the organizer's reference hash and then counts all members "
        f"of the class in four layouts. In {num(rev['a']['contexts'])} independent contexts the share is {ra_['mean']:.5f} "
        f"times 2^-{n_r}, with a standard error of {ra_['se']:.5f} (single contexts from {ra_['low']:.3f} to {ra_['high']:.3f}). "
        f"In {num(rev['b']['contexts'])} independent contexts with vd below 2^{d['d_bits']} it is {rb_['mean']:.5f}, with "
        f"{rb_['se']:.5f} (single contexts up to {rb_['high']:.3f}). For {rc_['sets']} sets of seed words with {rc_['per']} "
        f"contexts each (vc random, vd below 2^{d['d_bits']}, X14 random) the set means lie between {rc_['low']:.4f} and "
        f"{rc_['high']:.4f}, where the standard error of one set mean is {rc_['se']:.4f}; a chi-square test of equal means "
        f"gives probability {rc_['p']:.2f}. For {rd_['sets']} pairs (vc, vd) with {rd_['per']} random values of X14 each the "
        f"means lie between {rd_['low']:.4f} and {rd_['high']:.4f} (probability {rd_['p']:.2f}). The second program compares "
        f"{num(lrev['lanes'])} of its lanes with rule A on the h1 of the complete compression of the real message A; all are "
        f"right. In {num(lrev['contexts'])} independent contexts it finds {l5[0]:.5f} times 2^-{n_r}, with a standard error "
        f"of {l5_se:.5f} that follows from the scatter between contexts that it prints, and with single contexts "
        f"from {l5[3]:.3f} to {l5[4]:.3f} (for the four conditions from {lrev['r4'][2]:.3f} to {lrev['r4'][3]:.3f} times "
        f"2^-4), and a share of {lb[0]:.4f} of the batches, for one context at most {lb[2]:.4f}. For {word(len(lrev['pairs']))} "
        f"pairs (vc, vd) with vd below 2^{d['d_bits']} and {num(lrev['values'])} consecutive values of X14 each, with seed "
        f"words held, its pair means lie between {lrev['six'][0]:.5f} and {lrev['six'][1]:.5f} times 2^-{n_r}: they scatter by "
        f"{lrev['six'][2]:.3f}% where independent contexts would give {lrev['six'][4]:.3f}%. So the mean over consecutive "
        f"values of X14 is far more regular than a mean over independent contexts, as the layout runs on the graphics card "
        f"show for the four conditions"
        + (f"; and all {word(len(lrev['pairs']))} of these means are above 2^-{n_r}, by {100 * (lrev['six'][0] - 1):.2f}% to "
           f"{100 * (lrev['six'][1] - 1):.2f}%, more than their scatter, so that over windows of this kind the average is not "
           f"exactly 2^-{n_r}; the difference is far inside the budget" if lrev["six"][0] > 1 else "")
        + f". In the {word(len(samples))} processor samples for which a mean and its standard error are given under this and "
          f"the two headings before it, the mean is "
          f"within {up(max(abs(z) for z in zs), 1):.1f} standard errors of 2^-{n_r}; the {word(len(samples))} means lie between "
          f"{min(m_ for _, m_, _ in samples):.4f} and {max(m_ for _, m_, _ in samples):.4f}"
        + (", all on the low side" if all(z < 0 for z in zs) else "")
        + f". No shift from the restricted range of vd or from shared seed words is visible at this size. These are "
          f"processor runs of 2^29 to 2^32 trials, a share of 2^-{d['T'] - 32} of a run or less. A run on the graphics card "
          f"that records all five conditions in the layout of the algorithm is still owed.")
    t["ctx_limit_clause"] = (f"for its first four conditions it lay between {lo_r:.2f} and {hi_r:.2f} times 2^-4 in a sample of "
                             f"{num(ctx['contexts'])} contexts, and other samples have values up to {up(high4, 2):.2f}")
    t["ctx_claim"] = (f"in a sample of {num(ctx['contexts'])} independent contexts the share of the trials of one context that "
                      f"satisfy its first four conditions lay between {lo_r:.2f} and {hi_r:.2f} times 2^-4 (other samples "
                      f"have values up to {up(high4, 2):.2f}), with {ctx['dispersion']:.0f} times the variance of independent "
                      f"trials")
    t["ctx_note"] = (f"for the first four conditions it lay between {lo_r:.2f} and {hi_r:.2f} times 2^-4 in "
                     f"{num(ctx['contexts'])} contexts, and larger values occur ({up(high4, 2):.2f} in another sample)")
    t["joint_limit_clause"] = (
        f"of the listed partial E3 events of all real runs, {num(p_real['joint'])} of {num(p_real['e3'])} have an h1 that "
        f"satisfies the first four conditions, where M gives a share of {s4:.4f}")
    t["h3_limit_sentence"] = (
        f"2^-{rs['log2']:.4f} and 2^-{rs2['log2']:.4f} for rule A in two samples of {num(share['contexts'])} random contexts "
        f"on the processor; 2^-{rl['log2']:.4f} in {num(lshare['contexts'])} contexts laid out in the ranges of the algorithm "
        f"({word(lshare['quads'])} sets of seed words, vd below 2^{d['d_bits']}, consecutive values of X14); and 2^-4 to "
        f"within {abs(zi):.2f} standard deviations for its first four conditions in 2^{p_ind['log2']:.2f} trials with "
        f"independent contexts on the graphics card. The fifth condition was not measured on the graphics card. What step "
        f"4 budgets is batches: the measured share of the batches that hold a trial satisfying rule A is "
        f"{rs['entered'] / share['batches']:.4f} for random contexts and {rl['entered'] / lshare['batches']:.4f} in the ranges "
        f"of the algorithm, against {budget_share:.2f}.")
    t["h3_claim"] = (
        f"in {num(share['contexts'])} random contexts with all members ({num(share['trials'])} trials, on the processor) "
        f"{num(rs['passes'])} trials satisfy rule A, a share of 2^-{rs['log2']:.4f}, and a share of "
        f"{rs['entered'] / share['batches']:.4f} of the batches hold such a trial; in {num(lshare['contexts'])} contexts laid "
        f"out in the ranges of the algorithm ({word(lshare['quads'])} sets of seed words, the second enumerated word below "
        f"2^{d['d_bits']}, consecutive values of the third) the two shares are 2^-{rl['log2']:.4f} and "
        f"{rl['entered'] / lshare['batches']:.4f}; the largest share of the batches of one context in all samples is "
        f"{up(batch_max, 4):.4f}, against the budget of {budget_share:.2f}; two programs that reviewing helper agents wrote "
        f"from the proof text give {ra_['mean']:.4f} and {l5[0]:.4f} times 2^-{n_r} for independent contexts and means from "
        f"{rc_['low']:.4f} to {rc_['high']:.4f} for {rc_['sets']} sets of shared seed words; on the graphics card, where only "
        f"the first four conditions are recorded, 2^{p_ind['log2']:.2f} trials with independent contexts give "
        f"{num(p_ind['rule'])} against {p_ind['trials'] / 16:,.0f} expected at 2^-4, and each of {rr['both']['runs']} runs of "
        f"2^40 trials with shared outer words is within {parts(rr['both']['parts'])} of 2^-4.")
    t["h3_scope_batches"] = (
        f"What the algorithm budgets is batches, and the statement on trials is a sufficient condition for it; the measured "
        f"share of the batches that hold a trial satisfying rule A is {rs['entered'] / share['batches']:.4f} for random "
        f"contexts and {rl['entered'] / lshare['batches']:.4f} in the ranges of the algorithm, less than half the budget.")
    if not 2 * max(rs["entered"] / share["batches"], rl["entered"] / lshare["batches"]) < budget_share:
        raise SystemExit("a measured share of the batches is not below half the stage-2 budget: the claim says half")
    t["h3_owed_claim"] = ("The fifth condition of rule A was measured only on the processor, in runs of 2^29 to 2^32 trials; "
                          "no run on the graphics card records it.")
    t["rule_real_note"] = (
        f"On the processor, in {num(share['contexts'])} random contexts with all members, a share of 2^-{rs['log2']:.4f} of "
        f"the trials pass rule A, and a share of {rs['entered'] / share['batches']:.4f} of the batches hold such a trial "
        f"(budget {budget_share:.2f}); with contexts laid out in the ranges of the algorithm the shares are "
        f"2^-{rl['log2']:.4f} and {rl['entered'] / lshare['batches']:.4f}. Per context the share of the trials reaches "
        f"{up(high5, 2):.2f} times 2^-{n_r} in the samples. Two programs that reviewing helper agents wrote from the proof "
        f"text give the same averages. On the graphics card the first four conditions were counted in 2^{p_ind['log2']:.2f} "
        f"trials with independent contexts: {zi:+.2f} standard deviations from 2^-4 on average, but with "
        f"{ctx['dispersion']:.0f} times the variance of independent trials from context to context. In the {len(lay)} layout "
        f"runs every run is within {parts(ra['parts'])} of 2^-4. Of the listed partial events of the second call, "
        f"{num(p_real['joint'])} of {num(p_real['e3'])} pass the first four conditions, where the model gives a share of "
        f"{s4:.4f}.")
    # the E1 test
    big_pair = max(gpu["pairs"], key=lambda p_: p_[0])
    pass_rate = math.log2(p_ind["e1pass"] / p_ind["trials"])
    p_both = (p_ind["e1pass"] + p_mod["e1pass"]) / (p_ind["trials"] + p_mod["trials"])
    z_e1 = (p_ind["e1pass"] / p_ind["trials"] - p_mod["e1pass"] / p_mod["trials"]) \
        / math.sqrt(p_both * (1 - p_both) * (1 / p_ind["trials"] + 1 / p_mod["trials"]))
    t.update(pass_count=num(p_ind["e1pass"]), pass_trials=f"{p_ind['log2']:.2f}", pass_model_count=num(p_mod["e1pass"]),
             pass_model_trials=f"{p_mod['log2']:.2f}", pass_rate=f"{pass_rate:.2f}", pass_expected=f"{T + pass_rate:.1f}",
             pass_margin=f"{down(d['pass_budget'] - (T + pass_rate), 1):.1f}", pass_layout_count=num(sum(e1p)))
    t["e1_real_paragraph"] = (
        f"*The E1 test.* In the {word(len(ind))} runs with independent contexts together, {num(p_ind['e1pass'])} of "
        f"2^{p_ind['log2']:.2f} real trials pass the E1 test, a share of 2^{pass_rate:.2f}; the 2^{p_mod['log2']:.2f} draws "
        f"from M gave {num(p_mod['e1pass'])}, a share of 2^{math.log2(p_mod['e1pass'] / p_mod['trials']):.2f} ({z_e1:+.2f} "
        f"standard deviations between the two). In the {len(lay)} layout runs {num(sum(e1p))} of 2^{p_lay['log2']:.2f} trials "
        f"pass, a share of 2^{math.log2(p_lay['e1pass'] / p_lay['trials']):.2f}, and in the {word(len(spr))} spread runs "
        f"{num(p_spr['e1pass'])} of 2^{p_spr['log2']:.2f}, a share of 2^{math.log2(p_spr['e1pass'] / p_spr['trials']):.2f}. A "
        f"uniform 32-bit word would be zero with probability 2^-32; the test passes about "
        f"{p_ind['e1pass'] / p_ind['trials'] * 2 ** 32:.1f} times as often, and M predicts that. H2 budgets a share of "
        f"2^-{PASS_SHIFT}.")

    # ---- notes and claims built from the above
    t["count_claim"] = (
        f"Over all {num(valid)} values of beta ({num(n14)} enumerated in full by the calculator, the rest decided by a SAT "
        f"solver on the whole system and counted where it found a solution), {len(order_b)} have a nonzero part and the "
        f"count is {num(total)} times the uniform expectation; {word(len(flagged))} values of beta hold estimates, "
        f"{float(sum(part[b_] for b_ in flagged)):.2f} together.")
    t["recount_claim"] = (
        f"An independent recount by another AI model (GPT Sol 6.1) with a method and a program of its own, in integer "
        f"arithmetic over every value of beta, gives {float(gpt['total']):,.2f} from the same {len(gpt['parts'])} values; its "
        f"program was run again here and its parts agree with the count for all {len(exact_betas)} values counted in full. "
        f"The other model had been told the participant's total, the four heaviest parts and the number of values with a "
        f"part; the other {len(part) - 4} parts and the factors of the outcomes were not given to it.")
    t["checks_claim"] = (
        f"both counts against the approximate model counter ApproxMC for the sixteen largest outcomes (largest difference "
        f"{a1[3]} and {a3[3]} bits); both against brute force with 8-bit words ({num(int(b1[2]))} of {num(int(b1[1]))} and "
        f"{num(int(b3[2]))} of {num(int(b3[1]))} outcomes equal); and a sampler for the four heaviest values of beta "
        f"({s_dev} standard errors for their sum)")
    t["real_claim"] = (
        f"2^{big_pair[0]} real trials against 2^{big_pair[1]} draws from the model without a deviation beyond "
        f"{max(abs(r[3]) for r in big_pair[2] if r[1] + r[2] >= 30):.2f} standard deviations among "
        f"{sum(1 for r in big_pair[2] if r[1] + r[2] >= 30)} statistics; all real trials together (2^{p_real['log2']:.2f}) "
        f"against exact expectations on four events of one call each, down to a probability of about 2^-{t['deep_exp']} "
        f"({p_real['outcome']} events against {p_real['trials'] * dexp['outcome']:.1f} expected); of the "
        f"{num(p_real['e3'])} listed partial events of the second call, {num(p_real['joint'])} satisfy the first four "
        f"conditions of rule A, where the model gives a share of {s4:.4f} ({zbin(p_real['joint'], p_real['e3'], s4):+.2f} "
        f"standard deviations); and {len(lay)} runs with shared outer words")
    t["count_note"] = (
        f"All {num(valid)} words that occur as beta are covered: the {num(n14)} with k at most 14 were enumerated completely "
        f"and {word(part14)} of them have a part, {exact(k14_sum)} together, without any fallback; the others were decided "
        f"by a SAT solver on the whole system, and the {len(heavy)} it found satisfiable were counted and add "
        f"{exact(k15_sum)}. The count is {exact(total)}, about 2^{math.log2(total):.2f}, from {len(order_b)} betas and "
        f"{len(prod)} outcomes. The heaviest beta carries {100 * float(part[heaviest] / total):.0f}% of it and the two "
        f"heaviest {100 * float(top2 / total):.0f}%. {word(len(flagged), True)} betas hold estimates, "
        f"{float(sum(part[b_] for b_ in flagged)):.2f} together.")
    t["recount_note"] = (
        f"GPT Sol 6.1 (OpenAI) was given the definition of the system and counted the rate with a method and a program of "
        f"its own, in integer arithmetic over every beta: {float(gpt['total']):,.4f}, from the same {len(gpt['parts'])} "
        f"betas. I compiled and ran its program again and compared its parts with mine: equal for all {len(exact_betas)} "
        f"betas that I have in full. The recount was not blind: its request stated my total, the four heaviest parts and "
        f"the number of betas with a part, to be confirmed or refuted; the other {len(part) - 4} parts were not given. The "
        f"claim does not use its figure.")
    t["rule_note"] = (
        f"For each of the {len(prod)} outcomes of the count a SAT solver (kissat) was asked whether the E3 system of the "
        f"outcome has a solution that violates rule A: for {len(prod) - len(own['violable'])} its answer is that there is "
        f"none, for {len(own['violable'])} it returned one. Only the outcomes without such a solution are kept, and only "
        f"from the betas counted in full: {len(kept)} outcomes, which add up to {num(used)}, the figure that H1 is set "
        f"against. That is {100 * float(own['count'] / total):.1f}% of the count. "
        + (f"The same answers came from {join(s[0] for s in sec)} on a second formula. " if len(sec) == 2 else "")
        + f"An exact count of the second call split by the rule, by a program of a reviewing helper agent, finds the same "
          f"{n3r['kept']} outcomes and gives {num(n3r['r_all'])} as the model's own rate of trials that collide and pass "
          f"rule A; the claim keeps the smaller figure.")
    other_rows = [r for r in alts if r["n"] != RULE_CONDITIONS]
    t["rules_alt_note"] = (
        f"This package uses the cheapest of three prepared rules that leaves the count at least {MIN_MARGIN} times the "
        f"assumed factor. " + " ".join(
            f"With the rule of {WORDS[r['n']]} conditions the count would be {num(int(r['count']))} "
            f"({down(float(r['count']) / 2 ** F, 2):.2f} times the factor), a trial would be charged {r['charge']} operations "
            f"and the claim would be {r['times'][F]:.1f}." for r in other_rows)
        + f" With the factor 2^{F + 1} this package would claim {mine['times'][F + 1]:.1f}, with a count only "
          f"{down(float(mine['count']) / 2 ** (F + 1), 2):.2f} times the factor. None of these is claimed.")
    t["checks_note"] = (
        f"(1) Both counts at 32 bits against the model counter ApproxMC for the sixteen largest outcomes, "
        f"{100 * float(ct['top16'][1]):.0f}% of the count: largest difference {a1[3]} bits for E1 and {a3[3]} for E3. (2) A "
        f"SAT solver on the whole system: the betas it finds satisfiable are exactly the betas with a part. (3) Brute "
        f"force with 8-bit words: {num(int(b1[2]))} of {num(int(b1[1]))} outcomes equal for E1 and {num(int(b3[2]))} of "
        f"{num(int(b3[1]))} for E3. (4) The sampler of the first submissions for the four heaviest betas: {s_dev} standard "
        f"errors for their sum, a weak check. (5) The independent recount.")
    t["real_note"] = (
        "; ".join(pair_text) + f". Against exact expectations, all real trials together (2^{p_real['log2']:.2f}): "
        f"{p_real['outcome']} listed outcomes of the first call against {p_real['trials'] * dexp['outcome']:.1f} expected, and "
        f"{num(p_real['e3'])} listed partial events of the second against {p_real['trials'] * dexp['e3']:,.0f}. {len(lay)} runs "
        f"of 2^40 trials with shared outer words: ratio of variance to mean of the early-test passes {d_all:.2f} (the first "
        f"eight alone {d_8:.2f}, the sixteen later ones {d_16:.2f}).")
    t["filed_compare_sentence"] = (
        f"Against {SUBMISSIONS[-1][0]}: the class has {num(d['members'])} members in place of {num(FILED_MEMBERS)}; the count "
        f"that H1 is set against is {num(used)} in place of {num(filed['rule_count'])}; the assumed factor is 2^{F} in place "
        f"of {num(filed['factor'])}; stage A is {STAGE_A_OPS} operations and {STAGE_A_LOADS} loads in place of "
        f"{filed['a_ops']} and {filed['a_loads']}, stage 2 {STAGE_2_OPS} and {STAGE_2_LOADS} in place of {filed['s2_ops']} "
        f"and {filed['s2_loads']}, with stage 2 counted for {WORDS_SHARE[STAGE_2_LOG2_SHARE]} of the batches in place of "
        f"{filed['share']}; and a trial is charged {CHARGE} operations in place of {filed['charge']}.")
    t["filed_compare_note"] = (
        f"The class is larger ({num(d['members'])} members in place of {num(FILED_MEMBERS)}) and so is the count under the "
        f"model, which allows an assumed factor of 2^{F} in place of {num(filed['factor'])}; a trial costs a little more "
        f"({CHARGE} charged operations in place of {filed['charge']}).")
    return d, t


def main():
    d, t = build_tokens()
    for k in sorted(t):
        print(f"{k} = {t[k]}")


if __name__ == "__main__":
    main()
