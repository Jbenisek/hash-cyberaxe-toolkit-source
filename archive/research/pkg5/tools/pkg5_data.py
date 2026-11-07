#!/usr/bin/env python3
"""Every figure of the fifth package that depends on the pinned call, the class or the rate. ONE place.

To swap the class or the pin, edit PART A below and nothing else, then run

    python -B tools/build_pkg5.py            (renders src/* into the package files and the note)
    python -B tools/fmt_pkg5.py              (format checks, ranges, field lengths, drift)

PART A  the pin, the class, the assumed factor, and the names of the result files that hold the
        measured figures (the figures themselves are read from those files, not typed here).
PART B  everything that follows by arithmetic: Fact P, Lemma Q, the lists, the cost, the claim.
PART C  readers of the result files.
PART D  the tokens {{name}} that the templates in src/ use, and the paragraphs and tables that are
        written from the result files (so that a missing file gives a true sentence, not a gap).

    python -B tools/pkg5_data.py             prints every token
    python -B tools/pkg5_data.py --recount-env   shell variables for tools/recount_exact.sh
Research helper, not submitted.
"""
import json
import math
import re
from fractions import Fraction
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
TOOLS = Path(__file__).resolve().parent
PKG = TOOLS.parent
RESEARCH = PKG.parent
NIGHT = RESEARCH / "night" / "main"
EVID = PKG / "evidence"
CAND = PKG / "blake3-r2"
PROGRAM = CAND / "experiments" / "halfsearch.py"

# =====================================================================================================
# PART A: what a person edits
# =====================================================================================================
PIN = {"X3": 0xD5D881CA, "X7": 0xAA277E35, "X11": 0x1F208000, "X15": 0x123F2142, "W4": 0x7FFFFFFF, "W13": 0xFFFD6E01}
PIN_NAME = "pinB"                 # prefix of the night's result files for this pin

# THE CLASS OF THE PACKAGE: one of the keys of CLASSES below. Changing this one line and running
# tools/build_pkg5.py moves proof, claim, note, manifest and experiment program to that class.
ETA = 0xE7C1815F

# What is known about each class of this pin that has been counted. log2_factor: H1 assumes a rate of
# 2^log2_factor times the uniform one for that class (the filed rule: a power of two at least 2.9 times below the
# count). real / layout / deep: the night's files with the real-message runs of that class. e3check, e1amc: the
# files with the checks of the two counters against independent counters for that class; e3check_betas: the betas
# whose sampler outcomes the E3 check used (None: not known). layout_planned (optional): the number of layout runs
# that the night's script makes for the class; while fewer are in the file the text says that more are under way.
# extra_betas: betas
# outside the enumerated list that were counted as well, (beta, class-rate part, positive outcomes, source).
# extra_sampler: sampler runs that are not in FILES["sampler"], (beta, value, standard error, log2 draws, seed,
# source). sampler_note: a remark on the sampler runs in the words of the text (true as written, or empty).
CLASSES = {
    0xE5C1815F: dict(
        log2_factor=21, real="gpu_pinB.txt", layout="pinB_layout.txt", deep="pinB_deep.txt",
        e3check="pinB_e3check.txt", e3check_betas=("581c6852", "581c5852"), e1amc="e1_amc_pinB.txt",
        extra_betas=[("f8345852", 103968.0, 50, "cand_exact.txt")],
        extra_sampler=[("f8345852", 103129.4, 4320.5, 41, 8101, "confirm_ab.txt"),
                       ("f8345852", 103296.8, 4295.5, 41, 8102, "confirm_ab.txt"),
                       ("581c5852", 1818368.0, 70851.0, 38, 8201, "confirm_b2.txt")],
        sampler_note="The sampler runs are short because the sampler fails when a run is long and the rate is as high as here: with "
                     "2^38 draws its run for the heaviest beta ended with an illegal memory access (its output buffer), "
                     "and that run is not used."),
    0xE7C1815F: dict(
        log2_factor=23, real="gpu_pinB3.txt", layout="pinB3_layout.txt", deep="pinB3_deep.txt",
        e3check="e3check_e7c1815f.txt", e3check_betas=("481c6852", "58146852", "481c5852", "58145852"),
        e1amc="e1_amc_e7c1815f.txt", layout_planned=8,
        extra_betas=[], extra_sampler=[],
        sampler_note="The sampler runs are short because the sampler fails when a run is long and the rate is as high as here (its "
                     "output buffer overflows)."),
    0xE74181DF: dict(
        log2_factor=23, real="gpu_pinB4.txt", layout="pinB4_layout.txt", deep="pinB4_deep.txt",
        e3check="e3check_e74181df.txt", e3check_betas=None, e1amc="e1_amc_e74181df.txt",
        extra_betas=[], extra_sampler=[],
        sampler_note="The sampler runs are short because the sampler fails when a run is long and the rate is as high as here (its "
                     "output buffer overflows)."),
    0xE741835E: dict(
        log2_factor=22, real="gpu_pinB2.txt", layout="pinB2_layout.txt", deep="pinB2_deep.txt",
        e3check="e3check_e741835e.txt", e3check_betas=None, e1amc="e1_amc_e741835e.txt",
        extra_betas=[], extra_sampler=[],
        sampler_note="The sampler runs are short because the sampler fails when a run is long and the rate is as high as here (its "
                     "output buffer overflows)."),
}
# real-message runs of OTHER classes of the same pin, used with their class named when the class of the package
# has no finished run yet (in this order)
REAL_FALLBACK = (0xE5C1815F, 0xE741835E, 0xE7C1815F)
# The exact grid over neighbouring classes (grid_run.sh Bnear), which was stopped before it had finished (its
# output ~/hashsmash/night_main/grid_Bnear.out in WSL has no final CLASS lines): number of classes and of betas (line
# counts of grid_Bnear.etas and .betas there, read 2026-10-06 04:55 and 06:35), Hamming distance from the two
# centres, largest k of its betas. None: say nothing about a grid.
GRID = dict(classes=2847, betas=522, distance=6, kmax=12)
# A solution of the seven-word system with Y4 in the class, per class, in the names of 6.2 (w15 = 0). It is
# evaluated at every build with the G function alone; the build stops if its residual is not zero.
CLASS_SOLUTION = {
    0xE7C1815F: dict(Y1=0x00000000, Y6=0x7E1401E5, Y12=0x5A538AB4, w12=0x00000000, w5=0x234E3245, Y4=0x0AD073E5,
                     Y9=0x61E4852D, Y14=0xDDCC82F4, w8=0xA2EE086C),          # review/judge.md, section 1
}
# RULE A of the two-stage batch (proof 6.3, Lemma A): conditions on h1, the first-half d value of E3 on message A.
# Each entry (mask, value) says: the XOR of the bits of h1 in mask equals value. The rule belongs to the class: it
# was read off the E3 counts of the class, split by the bits of h1 (research/night/cheaper, files pinB3_rules.txt),
# and it is NOT a consequence of R = 0 (tools/rule_a_sat.py says for which outcomes it can be violated).
RULE_A = {
    0xE7C1815F: ((0x00010000, 1), (0x00000003, 0), (0x00000006, 0), (0x0000000C, 0), (0x00000018, 1), (0x01800000, 1)),
}
LOG2_FACTOR = CLASSES[ETA]["log2_factor"]
# "draft" until the owner says go for this package; then "ready" (see FILE_STEPS.md). It goes into claim.json.
SUBMISSION_STATE = "ready"
LOG2_X12 = 8                      # contexts: X12 < 2^LOG2_X12, X14 arbitrary, X13 gets the remaining bits
CHARGE = 17.4                     # primitive operations charged per trial: the budgeted cost of derive() plus a margin
PASS_SHIFT = 16                   # budget on passes of the E1 test (Lemma N): trials * 2^-PASS_SHIFT
STAGE_2_LOG2_SHARE = 3            # budget on stage-2 entries: a share 2^-STAGE_2_LOG2_SHARE of the batches of a run
PASS_OPS_LOG2 = 10                # a passing trial is recomputed in below 2^10 operations
MEMORY_LOG2 = 35                  # declared: preprocessing (host below 2^34 bytes, graphics card below 10 GB) and search
PREPROCESSING_LOG2 = 63
ADVICE_LOG2 = 6                   # 28 bytes of constants and eta, 12 bytes of the three constants of rule A
ADVICE_BYTES = 28 + 12
SELECTION_OPS_LOG2 = 60           # bound stated for all preprocessing computations (participant estimate)
SELFTEST = ("2000", "1")          # cases and seed of the self-test quoted in the text

# result files of the night (research/night/main), read by PART C
FILES = {
    "total": f"{PIN_NAME}_{ETA:08x}.total",        # exact class-rate part per beta: beta, k, positive outcomes, part
    "sampler": "confirm_b3.txt",                   # 16 sampler runs of 2^34 draws per beta, all classes
    "real": CLASSES[ETA]["real"],                  # host check, then real against model
    "layout": CLASSES[ETA]["layout"],              # runs in the layout of the algorithm, one line per run
    "deep": CLASSES[ETA]["deep"],                  # real against model with more trials
    "e1bf": "e1_bf.txt",                           # exact E1 count against brute force at 8-bit words
    "search": "trail5.log",                        # the solver search that produced the pins
    "candidates": "cand_totals.txt",               # every pin of the search: its solution's class counted over a few betas
}
CAND_BETAS = 150                  # lightest betas counted per candidate pin (cand_totals_loop.sh)
EXTRA_BETAS = {eta: c["extra_betas"] for eta, c in CLASSES.items()}
EXTRA_SAMPLER = {eta: c["extra_sampler"] for eta, c in CLASSES.items()}
SAMPLER_NOTE = {eta: c["sampler_note"] for eta, c in CLASSES.items()}
# the calculator against the sampler on other constants: (what, exact, outcomes through the random-subset branch of
# the E3 count, [(sampler value, standard error, which run)]); exact figures in evidence/other_pairs_recount.txt
OTHER_CHECKS = [
    ("the constants of submission 04638ed8, class e96d6d6b, beta 953908d0", 6164.7, 0,
     [(6168.0, 809.6, "third pass"), (6218.0, 771.8, "second pass")]),
    ("the same class, beta 953f08d0", 945.7, 7, [(1140.4, 104.4, "third pass"), (948.9, 94.6, "second pass")]),
    ("the same constants, class e96d7579, beta 953908d0", 2549.9, 0, [(2489.1, 147.0, "third pass"), (2545.7, 149.4, "second pass")]),
    ("another pin of the same solver search (eta 31b13fea, beta c93210a5)", 106520.0, 0,
     [(119740.4, 7337.5, "seed 8101"), (91882.3, 6147.2, "seed 8102")]),
]
SUBMISSIONS = (("17bba2ae", "123.5"), ("5ceb1802", "121.5"), ("04638ed8", "112.4"))
PREVIOUS_LOG2_FACTOR = 11         # the factor that H1 of the last of them assumes (2,048)
PREVIOUS_CHARGE = 34              # what the filed packages charge per trial (one-stage batch, 154 operations + 74 loads)
PREVIOUS_BATCH = (154, 74)
# What has been reviewed of THIS version (the two-stage batch, rule A, the count with rule A). Change the sentences
# when the state of the reviews changes. State on 2026-10-06: three helper agents reviewed the version before the
# present one (reports returned to the main session as findings; their programs and outputs are in review/); the
# findings were worked in (round 1). A fourth helper agent then read proof, claim, manifest and note in full, checked
# that round against the files, and ran the validation and the three programs again with the same output
# (review/wf6_recheck.json). Its four small findings were worked in after that (round 2), and nobody has read the text
# since; so the last sentence of each constant speaks of "what was changed after that check" and stays true after small
# later edits. VERSION_REVIEW is the sentence of the note,
# VERSION_REVIEW_PROOF the paragraph of Section 10; the results of the reviewers' programs are not typed here, they
# are read from the files that tools/rule_share.sh, tools/rule_share_seeds.py and tools/rule_a_sat2.py write.
VERSION_REVIEW = ("Three further helper agents of the same model then reviewed the version with rule A and the two-stage "
                  "batch, one for the mathematics and the cost, one for the figures and one reading as a hostile judge. "
                  "They are not independent parties. Their findings were worked into this text by a helper agent that "
                  "maintains the package, three of their programs were taken into its tools and run again, and the text "
                  "says where a result comes from them. A further helper agent of the same model then checked these "
                  "changes against the files and ran the three programs once more, with the same output; what was changed "
                  "after that check has not been reviewed.")
VERSION_REVIEW_PROOF = (
    "Three further helper agents, again instances of the same AI model and not independent parties, reviewed the "
    "version of this package before the present one, which already had rule A, the two-stage batch and the count "
    "with rule A. Three programs of theirs are reported in this section, each where its subject is treated and named "
    "there as a reviewing helper agent's: a second CNF formula for the questions on rule A, the count of rule A and of "
    "the batches that run stage 2 in the layout of 6.4, and the same over many sets of seed words. Each of them was "
    "run again for this text, and the figures printed are those of the second runs. A further helper agent, also an "
    "instance of the same AI model and not an independent party, then checked the changes made after their findings "
    "against the files and ran the three programs once more, with the same output; what was changed after that check "
    "has not been reviewed.")
# The runs of the three programs taken over from that review that the text quotes: the seed of tools/rule_share.sh;
# (sets of seed words, log2 of the batches per set, first set) of tools/rule_share_seeds.py; the solvers of
# tools/rule_a_sat2.py.
RULE_SHARE_RUN = "20261006"
RULE_SHARE_SEEDS_RUN = (8192, 15, 0)
RULE_SAT2_SOLVERS = ("cadical", "cryptominisat5")
# The unfiled draft that this package extends (research/pkg4): its claim, its charge per trial and its count, read
# from its own data module when that folder is there (None otherwise; the text then names no figure of it).
DRAFT_BEFORE = "pkg4"
SAMPLER_SEEDS = "8301 to 8316"    # confirm_b3.sh: seed 8300 + i for run i, the same for every beta and every class
# The local dry run of the intake is not typed here: validate_pkg5.sh writes evidence/validation_log.txt, and the
# note quotes it only while proof.md, claim.json, the manifest and the program have the sizes listed in that log.

# =====================================================================================================
# PART B: arithmetic
# =====================================================================================================
M32 = 0xFFFFFFFF
IV = (0x6A09E667, 0xBB67AE85, 0x3C6EF372, 0xA54FF53A, 0x510E527F, 0x9B05688C, 0x1F83D9AB, 0x5BE0CD19)
C_UNIT = 430
STAGE_A_OPS, STAGE_A_LOADS = 64, 36       # stage A of a batch (proof 6.5); the build compares them with the program's table
STAGE_2_OPS, STAGE_2_LOADS = 96, 42       # stage 2, the count of its own entry (3 operations, 1 load) included
RULE_A_PROBES = tuple((0x9E3779B9 * (i + 1) ^ (i << 13)) & 0xFFFFFFFF for i in range(4096))


def rule_a(h1, eta=None):
    """Rule A on the word h1 (PART A)."""
    return all(bin(h1 & mask).count("1") & 1 == value for mask, value in RULE_A[ETA if eta is None else eta])


def rule_a_on_z(qmask, qvalue):
    """Lemma A (b), (c): rule A as conditions on z for the class, and the three constants of the stage-A word.

    Returns (conditions, S, ALL, V); a condition is (lower bit of z, upper bit of z or None, wanted XOR, the bits of
    h1 it comes from, the bits of e1 that were inserted)."""
    conditions, shift, everything, wanted = [], 0, 0, 0
    for mask, value in RULE_A[ETA]:
        hbits = [i for i in range(32) if mask >> i & 1]
        ebits = [(i + 16) % 32 for i in hbits]
        if any(not qmask >> e & 1 for e in ebits):
            raise SystemExit("rule A reads a bit of h1 that meets a free bit of e1: the batch would need a second list")
        for e in ebits:
            value ^= qvalue >> e & 1
        low = sorted((i + 24) % 32 for i in hbits)
        if not (len(low) == 1 or (len(low) == 2 and low[1] == low[0] + 1)) or everything >> low[0] & 1:
            raise SystemExit("rule A: a condition is neither one bit nor two neighbouring bits of z, or two share a position")
        if len(low) == 2:
            shift |= 1 << low[0]
        everything |= 1 << low[0]
        wanted |= value << low[0]
        conditions.append((low[0], low[1] if len(low) == 2 else None, value, tuple(hbits), tuple(ebits)))
    return conditions, shift, everything, wanted
WORDS = ("zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "eleven", "twelve")
WORDS_SHARE = {1: "one half", 2: "one quarter", 3: "one eighth", 4: "one sixteenth"}       # 2^-n in words


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


def derive():
    d = {}
    p = PIN
    K = (IV[2] + IV[6]) & M32
    w4b = ((((K + p["W4"]) & M32) ^ 2) - K) & M32
    a = g_steps(p["X3"], p["X7"], p["X11"], p["X15"], p["W4"], p["W13"])
    b = g_steps(p["X3"], p["X7"], p["X11"], p["X15"], w4b, p["W13"])
    if a["d2"] != b["d2"] or a["b2"] != b["b2"] or a == b:
        raise SystemExit("PIN does not have the property of Fact P")
    d.update(K=K, KW4=(K + p["W4"]) & M32, W4B=w4b, delta=(p["W4"] - w4b) & M32, A=a, B=b,
             Y3=a["a2"], Y3B=b["a2"], Y11=a["c2"], Y11B=b["c2"])
    if d["delta"] not in (2, M32 - 1):
        raise SystemExit("W4 - W4' is neither +2 nor -2")
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
    d["ctx"] = T - 32 - d["free"]
    d["x13"] = d["ctx"] - LOG2_X12 - 32
    if not 0 <= d["x13"] <= 32:
        raise SystemExit("the context ranges do not fit: change LOG2_X12")
    d["pass_budget"] = T - PASS_SHIFT
    d["alphas_exp"] = d["ctx"] + 32                              # pairs of a context and an alpha: 2^alphas_exp
    d["stage2_shift"] = d["alphas_exp"] - STAGE_2_LOG2_SHARE     # stage-2 budget: list_words * 2^stage2_shift batches
    d["z_conditions"], d["a_shift"], d["a_all"], d["a_value"] = rule_a_on_z(d["qmask"], d["qvalue"])
    d["rule_conditions"] = len(RULE_A[ETA])
    if d["a_all"] >> 31 or d["a_shift"] >> 31:
        raise SystemExit("rule A reads bit 31 of z: the text of 6.5 on the word of Lemma A (c) says it does not")
    if ADVICE_BYTES > 2 ** ADVICE_LOG2:
        raise SystemExit("the stored constants do not fit the declared advice")
    d["pass_ops"] = d["pass_budget"] + PASS_OPS_LOG2
    d["ctx_ops"] = d["ctx"] + 11
    d["lists_ops"] = d["free"] + 6
    l_charge, l_unit = math.log2(CHARGE), math.log2(C_UNIT)
    d["main_exp"] = T + l_charge - l_unit
    rest = 2.0 ** d["pass_ops"] + 2.0 ** d["ctx_ops"] + 2.0 ** SELECTION_OPS_LOG2 + 2.0 ** d["lists_ops"] + 2.0 ** 11 + 1
    d["rest_exp"] = math.log2(rest)
    d["seventh"] = T + l_charge - 7
    if not d["rest_exp"] < d["seventh"]:
        raise SystemExit("the terms after the first are not below a share 2^-7 of the main loop")
    d["total_exp"] = math.floor((up(d["main_exp"], 5) + 0.01123) * 1e4 + 1) / 1e4
    d["total_bound"] = up(d["total_exp"], 2)
    d["time_log2"] = up(d["total_bound"], 1)
    true_total = math.log2((CHARGE * 2.0 ** T + rest) / C_UNIT + 2 + 2.0 ** 63)
    if not true_total < d["total_exp"] < d["total_bound"] <= d["time_log2"]:
        raise SystemExit("cost arithmetic does not chain")
    d["true_total"] = true_total
    d["slack"] = 2 ** (d["time_log2"] - d["total_exp"])
    d["pass_share"] = T + l_charge - d["pass_ops"]
    d["f_min"] = math.ceil(2.0 ** (LOG2_FACTOR + 1) * -math.log(0.607))
    if not d["f_min"] <= 2 ** LOG2_FACTOR:
        raise SystemExit("the assumed factor does not give 0.39")
    d["uniform_exp"] = 127 + l_charge - l_unit
    # The total of Section 8 for a factor f between 1 and 2^LOG2_FACTOR (2^127 / f trials): the terms after the first
    # stay below a share 2^-7 of the main loop (the pass budget and the contexts grow with the trials, the other terms
    # do not grow), so the same chain gives a total below 2^(uniform_total - log2 f). Checked here at both ends.
    d["uniform_total"] = up(math.floor((up(d["uniform_exp"], 5) + 0.01123) * 1e4 + 1) / 1e4, 2)
    rest_uniform = 2.0 ** (127 - PASS_SHIFT + PASS_OPS_LOG2) + 2.0 ** (127 - 32 - d["free"] + 11) + 2.0 ** SELECTION_OPS_LOG2 \
        + 2.0 ** d["lists_ops"] + 2.0 ** 11 + 1
    true_uniform = math.log2((CHARGE * 2.0 ** 127 + rest_uniform) / C_UNIT + 2 + 2.0 ** 63)
    if not (true_uniform < d["uniform_total"] and abs(d["uniform_total"] - LOG2_FACTOR - d["total_bound"]) < 1e-9
            and math.log2(rest_uniform) < 127 + l_charge - 7):
        raise SystemExit("the total for a general factor is not the stated bound minus log2 f at both ends")
    # the two logarithms as the text prints them (six decimals) must give the main exponent as it prints it (five)
    if f"{T + round(l_charge, 6) - round(l_unit, 6):.5f}" != f"{d['main_exp']:.5f}":
        raise SystemExit("the printed logarithms of the charge and of 430 do not add up to the printed main exponent")
    # per alpha, on average over a run: stage A of every batch, stage 2 of the budgeted share of the batches, and the
    # work before the batches (below 256 operations). Exact fractions.
    from fractions import Fraction
    d["stage_a"], d["stage_2"] = STAGE_A_OPS + STAGE_A_LOADS, STAGE_2_OPS + STAGE_2_LOADS
    d["alpha_stage_a"] = d["list_words"] * d["stage_a"]
    d["alpha_stage_2"] = Fraction(d["list_words"] * d["stage_2"], 2 ** STAGE_2_LOG2_SHARE)
    d["alpha_ops"] = d["alpha_stage_a"] + d["alpha_stage_2"] + 256
    d["alpha_charged"] = Fraction(str(CHARGE)) * d["members"]
    if d["alpha_ops"] >= d["alpha_charged"]:
        raise SystemExit("the charge per trial does not cover the budgeted batches")
    # what a trial costs when a trial satisfies rule A with probability 2^-conditions: at most 7 times that share of
    # the batches enter stage 2 (expected cost; the claim uses the budgeted cost above)
    d["rule_share"] = Fraction(7, 2 ** d["rule_conditions"])
    if not d["rule_share"] < Fraction(1, 2 ** STAGE_2_LOG2_SHARE):
        raise SystemExit("the stage-2 budget is not above seven times the pass rate of rule A")
    d["alpha_expected"] = d["alpha_stage_a"] + d["list_words"] * d["stage_2"] * d["rule_share"] + 256
    # memory of the search
    d["data_words"] = -(-(d["list_words"] + 256) // 1024) * 1024
    d["data_bytes"] = 32 * d["data_words"]
    d["online_bytes"] = 2 ** 19 + d["data_bytes"]
    d["online_log2"] = math.ceil(math.log2(d["online_bytes"]))
    return d


# =====================================================================================================
# PART C: readers of the result files
# =====================================================================================================
def night(name):
    return frozen(FILES[name])


# The night's files that were still growing when the package was written. tools/snapshot_logs.py copies them to
# evidence/snapshot/, and a copy there is read in place of the file in research/night/main, so that the text does
# not move with a running job. Delete a copy, or run the tool again, to take the file as it is now.
SNAPSHOT_FILES = ("trail5.log", "cand_totals.txt", f"pinclasses_{PIN_NAME}.txt", f"{PIN_NAME}_classes_table.txt",
                  "extend_totals.txt") + tuple(f"{PIN_NAME}_{e:08x}.total" for e in CLASSES)


def frozen(name):
    """The path of one of the night's files: its snapshot in evidence/ if there is one, else research/night/main."""
    snap = EVID / "snapshot" / name
    return snap if name in SNAPSHOT_FILES and snap.exists() else NIGHT / name


def read(path):
    return path.read_text(encoding="ascii", errors="replace") if path.exists() else None


def read_total(eta=None, longest=True):
    """[(beta, k, positive outcomes or None, part or None)] in file order; None where the calculator gave no result.

    The file is the night's (research/night/main). With longest, a copy of the same name in evidence/ is read in its
    place when it holds more betas (tools/fetch_totals.sh brings the files for the longer list of betas there)."""
    eta = ETA if eta is None else eta
    path = frozen(f"{PIN_NAME}_{eta:08x}.total")
    text = read(path)
    if longest:
        other = read(EVID / path.name)
        if other is not None and len(other.split()) > len((text or "").split()):
            text = other
    if text is None:
        if eta == ETA:
            raise SystemExit(f"missing {path}")
        return []
    rows = []
    for line in text.split("\n"):
        t = line.split()
        if len(t) == 4:
            rows.append((t[0], int(t[1]), int(t[2]), float(t[3])))
        elif len(t) == 2:
            rows.append((t[0], int(t[1]), None, None))
    return rows


def no_eps(beta, eta=None):
    """True when beta XOR ROR(eta,1) has odd weight: no eps exists and the pair contributes exactly zero."""
    return bin(int(beta, 16) ^ ror(ETA if eta is None else eta, 1)).count("1") & 1 == 1


def read_recount():
    """{beta: (part, outcomes with a nonzero E3 count, of them through the random-subset branch, formula fallbacks,
    outcomes whose exact E1 count is nonzero as well, or None if the recount did not record it)} from the recount."""
    text = read(EVID / f"pairs_recount_{ETA:08x}.txt")
    out = {}
    if text is None:
        return out
    pos = {}
    for line in text.split("\n"):
        m = re.match(r"PAIR ([0-9a-f]{8}) ([0-9a-f]{8}) .*? positive (\d+) sampled (\d+)", line)
        if m and int(m.group(1), 16) == ETA:
            pos[m.group(2)] = (int(m.group(3)), int(m.group(4)))
        m = re.match(r"EXACT-E1 ([0-9a-f]{8}) ([0-9a-f]{8}) .*class-rate part ([\d.]+) .*formula fallbacks (\d+)", line)
        if m and int(m.group(1), 16) == ETA and m.group(2) in pos:
            out[m.group(2)] = (float(m.group(3)),) + pos[m.group(2)] + (int(m.group(4)), None)
        m = re.match(r"OUTS ([0-9a-f]{8}) ([0-9a-f]{8}) written (\d+) nonzero (\d+) zero (\d+)", line)
        if m and int(m.group(1), 16) == ETA and m.group(2) in out:
            if int(m.group(3)) != out[m.group(2)][1]:
                raise SystemExit(f"recount of beta {m.group(2)}: the outcomes written are not those counted")
            out[m.group(2)] = out[m.group(2)][:4] + (int(m.group(4)),)
    return out


def class_check(key):
    """(path, eta) of a check of one of the counters: for the class of the package if that file exists, else for
    another class of the same pin; (None, None) if there is none."""
    for eta in (ETA,) + tuple(e for e in CLASSES if e != ETA):
        path = NIGHT / CLASSES[eta][key]
        if path.exists():
            return path, eta
    return None, None


def read_sampler(eta=None):
    """{beta: (mean, standard error, runs, log2 draws, failed, min, max)} for a class."""
    eta = ETA if eta is None else eta
    text = read(night("sampler")) or ""
    out = {}
    for m in re.finditer(r"eta ([0-9a-f]{8}) beta ([0-9a-f]{8}): (\d+) runs of 2\^(\d+) draws \((\d+) failed\): "
                         r"class-rate part (\d+) \+- (\d+)\s+\(min (\d+), max (\d+)\)", text):
        if int(m.group(1), 16) == eta:
            out[m.group(2)] = (float(m.group(6)), float(m.group(7)), int(m.group(3)), int(m.group(4)), int(m.group(5)),
                               float(m.group(8)), float(m.group(9)))
    return out


ORD = ("first", "second", "third", "fourth")


def read_stats(path, eta=None):
    """{'check': line, 'real': stats, 'model': stats} of an r2_class_gpu output for a class; stats: key -> (phrase, count)."""
    eta = ETA if eta is None else eta
    out = {"check": None, "real": None, "model": None}
    text = read(path)
    if text is None:
        return out
    mode = None
    for line in text.split("\n"):
        m = re.match(r"(check|real|model): pin .* eta ([0-9a-f]{8})", line)
        if m:
            mode = m.group(1) if int(m.group(2), 16) == eta else None
            if mode in ("real", "model"):
                out[mode] = {}
            continue
        if mode == "check" and line.startswith("CHECK"):
            out["check"] = line.strip()
            continue
        m = re.match(r"STAT (real|model) (.*)", line)
        if not m or m.group(1) != mode:
            continue
        s, body = out[mode], m.group(2)
        if body.startswith("trials"):
            s["trials"] = ("log2 of the number of trials", float(re.search(r"2\^([\d.]+)", body).group(1)))
            s["bad"] = ("trials with a wrong Y4", int(body.split("bad")[1]))
        elif body.startswith("early test passes"):
            s["early"] = ("early test passes", int(re.search(r"passes:\s*(\d+)", body).group(1)))
            s["eta"] = ("trials in which E1 requires the class", int(re.search(r"eta of Y4:\s*(\d+)", body).group(1)))
            s["contra"] = ("contradictions", int(re.search(r"contradictions \(must be 0\):\s*(\d+)", body).group(1)))
        elif body.startswith("word zero"):
            for i, v in enumerate(re.findall(r"(\d+) \(2\^", body)):
                s[f"wz{i}"] = (f"the {ORD[i]} residual word zero", int(v))
        elif body.startswith("low 16 zero"):
            for i, v in enumerate(re.findall(r"(\d+) \(2\^", body)):
                s[f"lz{i}"] = (f"the low 16 bits of the {ORD[i]} residual word zero", int(v))
        elif body.startswith("low 16 of two"):
            for a, b, v in re.findall(r"(\d)(\d):(\d+)", body):
                s[f"l2{a}{b}"] = (f"the low 16 bits of the {ORD[int(a)]} and {ORD[int(b)]} residual words both zero", int(v))
        elif body.startswith("two words zero"):
            for a, b, v in re.findall(r"(\d)(\d):(\d+)", body):
                s[f"w2{a}{b}"] = (f"the {ORD[int(a)]} and {ORD[int(b)]} residual words both zero", int(v))
        elif body.startswith("low 8 of all four"):
            s["z8"] = ("all four residual words with a zero low byte", int(re.search(r"four:\s*(\d+)", body).group(1)))
            w = re.search(r"16/24/32/40:\s*(\d+) (\d+) (\d+) (\d+)", body)
            for k, v in zip((16, 24, 32, 40), w.groups()):
                s[f"wt{k}"] = (f"residual of weight at most {k}", int(v))
        elif body.startswith("trailing zero bits"):
            for k, v in re.findall(r"(\d+):(\d+)", body.split(":", 1)[1]):
                s[f"tz{k}"] = (f"at least {k} trailing zero residual bits", int(v))
    for side in ("real", "model"):
        if out[side] is not None and "wt40" not in out[side]:
            out[side] = None                      # block not complete yet
    return out


def deviations(real, model, least=30):
    """[(|z|, z, key)] for the statistics with at least `least` events in the two runs together, largest first."""
    rows = []
    for k, (_, a) in real.items():
        if k in ("trials", "bad", "contra") or k not in model:
            continue
        b = model[k][1]
        if a + b >= least:
            z = (a - b) / math.sqrt(a + b)
            rows.append((abs(z), z, k))
    return sorted(rows, reverse=True)


def read_layout(path):
    """[(run, early-test passes, trials in which E1 requires the class, contradictions)] of the layout runs."""
    text = read(path) or ""
    return [tuple(int(v) for v in m.groups()) for m in re.finditer(
        r"layout run (\d+): early test passes: (\d+) .*?eta of Y4: (\d+) .*?contradictions \(must be 0\): (\d+)", text)]


def read_e3check(path):
    text = read(path)
    if text is None:
        return None
    m0 = re.search(r"outcomes (\d+); random-subset branch: (\d+) with a nonzero estimate, (\d+) with zero; share of the whole sum "
                   r"that comes from this branch ([\d.]+)", text)
    mt = re.search(r"group T .*?: (\d+) outcomes, (\d+) counted by ApproxMC, (\d+) have NO solution at all, (\d+) undecided; sum of "
                   r"estimates / sum of independent counts = ([\d.]+); log2 difference mean [-+\d.]+, sd [\d.]+, range ([-+\d.]+) to ([-+\d.]+)", text)
    mp = re.search(r"group P .*?: (\d+) outcomes, (\d+) counted by ApproxMC, (\d+) have NO solution at all, (\d+) undecided; sum of "
                   r"estimates / sum of independent counts = ([\d.]+); log2 difference mean [-+\d.]+, sd [\d.]+, range ([-+\d.]+) to ([-+\d.]+)", text)
    mz = re.search(r"group Z .*?: (\d+) outcomes, (\d+) truly have no solution, (\d+) have solutions, (\d+) undecided", text)
    if not (m0 and mt and mz):
        return None
    # the checker was run with --full: its "random-subset branch" header then counts the outcomes enumerated in full.
    # The line "distinct outcomes: .. random-subset branch: N", written by the calling script, is the number of
    # outcomes that the sampler itself had counted through the random-subset branch (None if the file has no such line).
    md = re.search(r"distinct outcomes: (\d+), nonzero: (\d+), random-subset branch: (\d+)", text)
    return dict(outcomes=int(m0.group(1)), nonzero=int(m0.group(2)), zero=int(m0.group(3)), share_full=float(m0.group(4)),
                branch=int(md.group(3)) if md and int(md.group(1)) == int(m0.group(1)) else None,
                top=(int(mt.group(1)), int(mt.group(2)), float(mt.group(5)), mt.group(6), mt.group(7)),
                rest=(int(mp.group(1)), int(mp.group(2)), float(mp.group(5)), mp.group(6), mp.group(7)) if mp else None,
                zeros=(int(mz.group(1)), int(mz.group(2)), int(mz.group(3)), int(mz.group(4))))


def read_e1amc(path):
    text = read(path)
    m = text and re.search(r"beta ([0-9a-f]{8}): (\d+) outcomes compared, mean log2\(calculator/ApproxMC\) ([-+\d.]+), largest \|difference\| "
                           r"([\d.]+) bits; ApproxMC zero (\d+), timeouts (\d+)", text)
    return m and dict(beta=m.group(1), compared=int(m.group(2)), mean=m.group(3), largest=m.group(4), zero=int(m.group(5)),
                      timeouts=int(m.group(6)))


def read_e1bf():
    text = read(night("e1bf"))
    m = text and re.search(r"(\d+) cases, (\d+) outcomes with solutions: (\d+) equal, (\d+) different; zero outcomes sampled: (\d+) agree, "
                           r"(\d+) disagree", text)
    return m and dict(zip(("cases", "outcomes", "equal", "different", "zero_agree", "zero_disagree"), (int(v) for v in m.groups())))


def read_search():
    """The solver search: (number of lines with a pin found without a fixed pin, the line of this package's pin)."""
    text = read(night("search")) or ""
    want = ",".join(hx(PIN[k]) for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
    found = [l for l in text.split("\n") if "status=SATISFIABLE" in l and "fixed=no" in l]
    mine = [l for l in found if f"PIN={want}" in l]
    info = None
    if mine:
        m = re.search(r"bound=(\d+) .*? t=(\d+)s .*? cost=(\d+) x1w=(\d+) .*? eta=([0-9a-f]{8}) beta=([0-9a-f]{8}) tau=([0-9a-f]{8}) "
                      r"eps=([0-9a-f]{8}) parts=(\S+) sol=(\S+)", mine[0])
        info = dict(bound=int(m.group(1)), seconds=int(m.group(2)), cost=int(m.group(3)), x1w=int(m.group(4)), eta=m.group(5),
                    beta=m.group(6), tau=m.group(7), eps=m.group(8), sol=[int(v, 16) for v in m.group(10).split(",")])
    return len(found), info, max((int(m) for m in re.findall(r" t=(\d+)s status=SATISFIABLE", text)), default=0)


def read_candidates():
    """[(count over the lightest betas, pin text, eta)] for every pin of the solver search."""
    text = read(night("candidates")) or ""
    rows = []
    for line in text.split("\n"):
        m = re.match(r"([0-9a-f,]+) \| .*? \| ([0-9a-f]{8}) class 2\^\d+ \| betas with mass \d+ \| exact class rate (\d+) \|", line)
        if m:
            rows.append((int(m.group(3)), m.group(1), m.group(2)))
    return rows


def selftest():
    """The JSON line of the self-test of the program in the package (run now; it takes a few seconds)."""
    done = subprocess.run([sys.executable, "-B", "-s", str(PROGRAM), "--selftest", *SELFTEST], stdin=subprocess.DEVNULL, capture_output=True)
    if done.returncode != 0:
        raise SystemExit("the self-test of experiments/halfsearch.py does not end with exit status 0:\n" + done.stdout.decode()[:600])
    return json.loads(done.stdout.decode("ascii"))


# =====================================================================================================
# PART D: tokens, tables and paragraphs
# =====================================================================================================
def exact_table(d, eta=None):
    """Rows of a class: betas with a nonzero part, heaviest first, then the betas counted outside the list."""
    eta = ETA if eta is None else eta
    rows = read_total(eta)
    listed = sorted(((part, beta, k, pos) for beta, k, pos, part in rows if part), reverse=True)
    extra = [(part, beta, bin(rol(int(beta, 16), 12) & 0x7FFFFFFF).count("1"), pos) for beta, part, pos, _ in EXTRA_BETAS.get(eta, [])]
    sampler = read_sampler(eta)
    recount = read_recount() if eta == ETA else {}
    return rows, listed, extra, sampler, recount


def z_text(z):
    return f"{z:+.1f}".replace("+0.0", "0.0").replace("-0.0", "0.0")


def word(n, capital=False):
    w = WORDS[n] if 0 <= n < len(WORDS) else str(n)
    return w.capitalize() if capital else w


def join(items):
    items = list(items)
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def build_tokens():
    d = derive()
    t = {}
    for k in ("X3", "X7", "X11", "X15", "W4", "W13"):
        t[k] = hx(PIN[k])
    for k in ("KW4", "W4B", "delta", "Y3", "Y3B", "Y11", "Y11B", "DY3", "DY11", "x", "qsum", "qhalf", "qmask", "qvalue"):
        t[k] = hx(d[k])
    t["K"] = hx(d["K"])
    t["eta"] = hx(ETA)
    t["delta_note"] = ", that is -2 modulo 2^32" if d["delta"] == M32 - 1 else ""
    t["delta_signed"] = "- 2" if d["delta"] == M32 - 1 else "+ 2"
    t["factp_table"] = "\n".join(
        f"    {label}a1={hx(r['a1'])} d1={hx(r['d1'])} c1={hx(r['c1'])} b1={hx(r['b1'])}\n"
        f"               a2={hx(r['a2'])} d2={hx(r['d2'])} c2={hx(r['c2'])} b2={hx(r['b2'])}"
        for label, r in (("w4 = W4    ", d["A"]), ("w4 = W4'   ", d["B"])))
    t["P_d2"], t["P_b2"] = hx(d["A"]["d2"]), hx(d["A"]["b2"])
    t["x_bit31_sentence"] = ("Here x has bit 31, so m is x without that bit." if d["x"] >> 31 else
                             "Here x has no bit 31, so m = x.")
    t["fixed_bits"], t["free_bits"] = str(d["fixed"]), str(d["free"])
    t["members"], t["members_plain"] = num(d["members"]), str(d["members"])
    t["list_words"], t["full_batches"], t["rest"] = num(d["list_words"]), num(d["full_batches"]), str(d["rest"])
    t["spare_words"] = WORDS[d["spare"]]
    t["last_batch"] = ("one that holds the last member" if d["rest"] == 1 else f"one that holds the last {WORDS[d['rest']]} members")
    t["last_word_spare"] = (f"the {WORDS[d['spare']]} spare lanes of the last word repeat its last member" if d["spare"] != 1 else
                            "the spare lane of the last word repeats its last member")
    # the claim
    F, T = LOG2_FACTOR, d["T"]
    t.update(F=str(F), F1=str(F + 1), T=str(T), T1=str(T + 1), factor=num(2 ** F), charge=str(CHARGE),
             ctx=str(d["ctx"]), x12_bits=str(LOG2_X12), x13_bits=str(d["x13"]),
             pass_budget=str(d["pass_budget"]), pass_shift=str(PASS_SHIFT), pass_ops=str(d["pass_ops"]),
             ctx_ops=str(d["ctx_ops"]), lists_ops=str(d["lists_ops"]), sel_ops=str(SELECTION_OPS_LOG2),
             main_exp=f"{d['main_exp']:.5f}", main_exp2=f"{up(d['main_exp'], 2):.2f}",
             log_charge=f"{math.log2(CHARGE):.6f}", log_unit=f"{math.log2(C_UNIT):.6f}",
             rest_exp=f"{up(d['rest_exp'], 2) if up(d['rest_exp'], 2) > d['rest_exp'] else up(d['rest_exp'], 2) + 0.01:.2f}",
             seventh=f"{math.floor(d['seventh'] * 1000) / 1000:.3f}", total_exp=f"{d['total_exp']:.4f}",
             total_bound=f"{d['total_bound']:.2f}", time_log2=f"{d['time_log2']:.1f}", slack=f"{d['slack']:.2f}",
             pass_share=f"{math.floor(d['pass_share'] * 100) / 100:.2f}", f_min=num(d["f_min"]),
             uniform_exp=f"{d['uniform_exp']:.5f}", uniform_exp2=f"{up(d['uniform_exp'], 2):.2f}",
             uniform_time=f"{up(up(d['uniform_exp'] + 0.01123, 2), 1):.1f}",
             uniform_total2=f"{d['uniform_total']:.2f}",
             alt_F=str(F - 1), alt_T=str(T + 1), alt_exp2=f"{up(d['main_exp'], 2) + 1:.2f}", alt_time=f"{d['time_log2'] + 1:.1f}",
             alt_factor=num(2 ** (F - 1)),
             memory_log2=str(MEMORY_LOG2), online_log2=str(d["online_log2"]), preprocessing_log2=str(PREPROCESSING_LOG2),
             advice_log2=str(ADVICE_LOG2), data_words=num(d["data_words"]), data_bytes=num(d["data_bytes"]),
             stage_a_ops=str(STAGE_A_OPS), stage_a_loads=str(STAGE_A_LOADS), stage_a_total=str(d["stage_a"]),
             stage_2_ops=str(STAGE_2_OPS), stage_2_loads=str(STAGE_2_LOADS), stage_2_total=str(d["stage_2"]),
             stage_2_lanes_total=str(d["stage_2"] - 4), both_stages_total=str(d["stage_a"] + d["stage_2"]),
             alphas_exp=str(d["alphas_exp"]), stage2_den=str(2 ** STAGE_2_LOG2_SHARE), stage2_log=str(STAGE_2_LOG2_SHARE),
             stage2_share_words=WORDS_SHARE[STAGE_2_LOG2_SHARE],
             stage2_share=f"{1 / 2 ** STAGE_2_LOG2_SHARE:.3f}",
             stage2_budget=f"{num(d['list_words'])} * 2^{d['stage2_shift']}", batches_total=f"{num(d['list_words'])} * 2^{d['alphas_exp']}",
             stage2_trial_share=f"{math.floor((math.log2(d['list_words']) + d['stage2_shift'] - T) * 100) / 100:.2f}",
             alpha_stage_a=num(d["alpha_stage_a"]), alpha_stage_2=f"{float(d['alpha_stage_2']):,.2f}",
             alpha_ops=f"{float(d['alpha_ops']):,.2f}", alpha_charged=f"{float(d['alpha_charged']):,.1f}",
             per_trial=f"{up(float(d['alpha_ops'] / d['members']), 3):.3f}",
             per_trial_expected=f"{up(float(d['alpha_expected'] / d['members']), 3):.3f}",
             alpha_margin=num(math.floor(float(d["alpha_charged"] - d["alpha_ops"]) / 100) * 100),
             alpha_margin_pct=f"{math.floor(1000 * float(d['alpha_charged'] / d['alpha_ops'] - 1)) / 10:.1f}",
             rule_conditions=WORDS[d["rule_conditions"]], rule_pass_exp=str(d["rule_conditions"]),
             rule_share=f"{float(d['rule_share']):.6f}".rstrip("0"),
             # the observation batch_stage_2_entered of the declared experiment over 256 seeds, if the seven trials of
             # a batch satisfy rule A independently with probability 2^-conditions: share, expected count and its
             # standard deviation (the manifest says that one run of 256 seeds is no test of H3)
             entered_share=f"{1 - (1 - 2.0 ** -d['rule_conditions']) ** 7:.3f}",
             entered_256=f"{256 * (1 - (1 - 2.0 ** -d['rule_conditions']) ** 7):.0f}",
             entered_256_sd=f"{math.sqrt(256 * (1 - (1 - 2.0 ** -d['rule_conditions']) ** 7) * (1 - 2.0 ** -d['rule_conditions']) ** 7):.0f}",
             budget_over_rule=f"{math.floor(1000 * float(Fraction(1, 2 ** STAGE_2_LOG2_SHARE) / d['rule_share'])) / 1000:.3f}",
             a_shift=hx(d["a_shift"]), a_all=hx(d["a_all"]), a_value=hx(d["a_value"]),
             advice_bytes=str(ADVICE_BYTES), advice_limit=str(2 ** ADVICE_LOG2),
             previous_charge=str(PREVIOUS_CHARGE), charge_gain=f"{math.log2(PREVIOUS_CHARGE / CHARGE):.2f}",
             sol_exp=str(192 + d["free"] - 128), space_exp=str(192 + d["free"]),
             share_exp=str(d["fixed"]), draws_exp=str(96), draws_ratio_exp=str(d["fixed"]))
    ranges = [f"X12 < 2^{LOG2_X12}"] + ([f"X13 < 2^{d['x13']}"] if d["x13"] < 32 else [])
    t["ctx_ranges"] = " and ".join(ranges)
    t["ctx_product"] = " * ".join([f"2^{LOG2_X12}", f"2^{d['x13']}", "2^32"])
    t["submissions"] = ", ".join(f"`{s}`" for s, _ in SUBMISSIONS[:-1]) + f" and `{SUBMISSIONS[-1][0]}`"
    t["submissions_plain"] = ", ".join(s for s, _ in SUBMISSIONS[:-1]) + f" and {SUBMISSIONS[-1][0]}"
    t["submission_scores"] = ", ".join(v for _, v in SUBMISSIONS[:-1]) + f" and {SUBMISSIONS[-1][1]}"
    t["last_submission"], t["last_score"] = SUBMISSIONS[-1]
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
        t["local_checks"] = ("- The organizer intake has not been run locally on this state of the package.")

    # ---- the self-test of the program in the package
    st = selftest()
    order = ("C0 backwards", "K3", "C2 to z", "rule A", "C2, rest", "D1", "C1 to Y1", "E1, A and B", "E1 test")
    sums = [f"{st['parts'][p]['largest_sum']:.3f}" for p in order]
    if not ((st["stage_a"]["operations"], st["stage_a"]["loads"]) == (STAGE_A_OPS, STAGE_A_LOADS)
            and (st["stage_2"]["operations"], st["stage_2"]["loads"]) == (STAGE_2_OPS, STAGE_2_LOADS)
            and [st["parts"][p]["bound"] for p in order] == [2, 6, 8, 2, 3, 2, 6, 10, 2]
            and st["lanes_right"] == st["lanes_checked"] and st["counts_equal_table"] and st["same_counts_in_every_case"]
            and st["members_in_list"] == d["members"] and st["list_words"] == d["list_words"] and st["zero_test_words"] == 0
            and st["zero_lane_patterns_right"] == 128 and st["rule_a_patterns_right"] == st["rule_a_patterns"] == 256
            and st["sums_below_bounds"] and st["per_context_constants"] == 14 and st["per_alpha_constants"] == 7
            and st["rule_a_on_z"] == {"shift_mask": hx(d["a_shift"]), "all": hx(d["a_all"]), "value": hx(d["a_value"])}):
        raise SystemExit("the self-test does not report what the text states; read its JSON line")
    t.update(st_cases=num(st["cases"]), st_seed=str(st["seed"]), st_lanes=num(st["lanes_checked"]),
             st_sums=", ".join(sums[:-1]) + " and " + sums[-1], st_registers=str(st["registers"]),
             st_ctx_constants=str(st["per_context_constants"]), st_alpha_constants=str(st["per_alpha_constants"]),
             st_largest=f"{st['largest_lane'] / 2 ** 32:.3f}", st_pass_a=num(st["lanes_passing_rule_a"]),
             st_entered=num(st["batches_entering_stage_2"]), st_a_satisfied=str(st["rule_a_patterns_satisfied"]),
             st_a_patterns=str(st["rule_a_patterns"]))

    # ---- the exact count
    rows, listed, extra, sampler, recount = exact_table(d)
    evaluated = [r for r in rows if r[3] is not None]
    skipped = [r for r in rows if r[3] is None]
    if any(not no_eps(r[0]) for r in skipped) or any(no_eps(r[0]) for r in evaluated):
        raise SystemExit("a beta without a result is not explained by the parity rule (timeout?): look at the .total file")
    weights = sorted({r[1] for r in rows})
    listed_sum = sum(p for p, *_ in listed)
    extra_sum = sum(p for p, *_ in extra)
    total = listed_sum + extra_sum
    counted = listed + extra
    if total < 2 ** F:
        raise SystemExit("the exact count is below the assumed factor")
    heaviest = counted and max(counted)
    t.update(betas_enumerated=num(len(rows)), betas_evaluated=num(len(evaluated)), betas_no_eps=num(len(skipped)),
             betas_with_mass=str(len(listed)), k_min=str(weights[0]), k_max=str(weights[-1]),
             exact_listed=num(listed_sum), exact_extra=num(extra_sum), exact_total=num(total),
             exact_over_factor=f"{total / 2 ** F:.2f}",
             exact_over_alt=f"{total / 2 ** (F - 1):.1f}",
             per_run=f"{total / 2 ** (F + 1):.2f}", cluster_max=f"{math.floor(total / d['f_min'] * 100) / 100:.2f}",
             assumed_per_run=f"{2 ** F / 2 ** (F + 1):.1f}",
             exact_log2=f"{math.log2(total):.2f}",
             hit_exp=f"{128 - math.log2(total):.2f}",
             heaviest_beta=heaviest[1], heaviest_part=num(heaviest[0]), heaviest_share=f"{100 * heaviest[0] / total:.0f}")
    # Rule A: the count that the claim uses. From here on exact_over_factor, exact_over_alt, per_run and cluster_max are
    # those of the count with rule A (rule_count); exact_total, exact_log2 and hit_exp stay those of the count of all
    # solutions, and full_over_factor is its ratio to the assumed factor.
    t.update(rule_tokens(d, counted, total, rows))
    t.update(followup_tokens(d, st))
    top2 = sorted(counted, reverse=True)[:2]
    t["top2_share"] = f"{100 * sum(p for p, *_ in top2) / total:.0f}"
    # The .total file gives, per beta, the outcomes with a nonzero E3 count; the exact E1 count of some of them is
    # zero. The recount records how many have a nonzero product; the table shows that number when it is known for
    # every beta of the table, and says which of the two it shows.
    paths = {b: recount[b][4] for _, b, _, _ in counted if b in recount and recount[b][4] is not None}
    full = len(paths) == len(counted)
    shown = {b: (paths[b] if full else pos) for _, b, _, pos in counted}
    t["outcomes_meaning"] = ("the number of outcomes (tau, eps) with P1 * N3 > 0" if full else
                             "the number of outcomes (tau, eps) with a nonzero E3 count, of which some have P1 = 0")
    e3_positive = heaviest[3]
    t["fifth_detail"] = (f"For the heaviest beta, {heaviest[1]}, it finds {e3_positive} outcomes with a nonzero E3 count"
                         + (f", of which {shown[heaviest[1]]} have a nonzero product." if full else "."))
    t["top2_outcomes_clause"] = (f"with {sum(shown[b] for _, b, _, _ in top2)} outcomes (tau, eps) between them" if full else
                                 f"with at most {sum(shown[b] for _, b, _, _ in top2)} outcomes (tau, eps) between them")
    head = ("| beta | k | Outcomes | Exact part | Sampler | Error | Deviation |\n"
            "| --- | ---: | ---: | ---: | ---: | ---: | ---: |\n")
    lines, s_exact, s_samp, s_var, n_samp = [], 0.0, 0.0, 0.0, 0
    for part, beta, k, pos in counted:
        if beta in sampler:
            mean, se = sampler[beta][0], sampler[beta][1]
            lines.append(f"| {beta} | {k} | {shown[beta]} | {num(part)} | {num(mean)} | {num(se)} | {z_text((mean - part) / se)} |")
            s_exact, s_samp, s_var, n_samp = s_exact + part, s_samp + mean, s_var + se * se, n_samp + 1
        else:
            lines.append(f"| {beta} | {k} | {shown[beta]} | {num(part)} | | | |")
    lines.append(f"| sum | | {sum(shown.values())} | {num(total)} | | | |")
    t["exact_table"] = head + "\n".join(lines)
    t["beta_cover_sentence"], t["betas_list"], t["betas_left_out"], _ = beta_cover(rows, d["DY11"])
    t.update(classes_tokens(d, total, rows))
    runs = {v[2:5] for v in sampler.values()}
    t["sampled_betas"] = word(n_samp)
    t["sampled_betas_cap"] = word(n_samp, True)
    t["sampled_count"] = str(n_samp)
    if n_samp:
        r, lg, failed = sorted(runs)[0]
        se = math.sqrt(s_var)
        t["sampler_setup"] = (f"{r} runs of 2^{lg} draws" if len(runs) == 1 else "several runs")
        diffs = [(sampler[b][0] - p, (sampler[b][0] - p) / sampler[b][1], b) for p, b, _, _ in counted if b in sampler]
        zmin, zmax = min(z for _, z, _ in diffs), max(z for _, z, _ in diffs)
        t["sampler_sum_sentence"] = (
            f"For these {t['sampled_betas']} betas together the sampler gives {num(s_samp)} with standard error {num(se)} "
            f"against {num(s_exact)} counted; the single betas lie between {z_text(zmin)} and {z_text(zmax)} standard errors."
            + (f" That the sums agree so closely is a cancellation: the {t['sampled_betas']} differences are "
               + join(f"{dv / 1e6:+.2f}" for dv, _, _ in diffs) + " million." if n_samp > 1 and abs(s_samp - s_exact) < 0.25 * se else ""))
        far = [(z, b) for _, z, b in diffs if abs(z) >= 2.0]
        t["sampler_far_sentence"] = ("" if not far else
                                     f"The deviation of {z_text(far[0][0])} for beta {far[0][1]} is not explained." if len(far) == 1 else
                                     "The deviations of " + join(f"{z_text(z)} for beta {b}" for z, b in far) + " are not explained.")
        t["sampler_far_betas"] = str(len(far))
        t["sampled_share"] = f"{100 * s_exact / total:.0f}"
        t["sampler_sum"], t["sampler_sum_se"], t["sampled_exact_sum"] = num(s_samp), num(se), num(s_exact)
        t["factor_over_sampled"] = f"{math.floor(s_samp / 2 ** F * 10) / 10:.1f}"
    else:
        t["sampler_setup"] = "runs"
        t["sampler_far_sentence"], t["sampler_far_betas"] = "", "0"
        t["sampler_sum_sentence"] = "No beta of this class has been sampled yet."
        t["sampled_share"], t["sampler_sum"], t["sampler_sum_se"], t["sampled_exact_sum"], t["factor_over_sampled"] = "0", "0", "0", "0", "0"
    by_beta = {b: p for p, b, _, _ in counted}
    more = []
    for beta, value, se, lg, seed, _ in EXTRA_SAMPLER.get(ETA, []):
        if beta in by_beta:
            more.append(f"beta {beta} with 2^{lg} draws (seed {seed}): {num(value)} with standard error {num(se)} against "
                        f"{num(by_beta[beta])} counted")
    t["extra_sampler_sentence"] = ("Single larger sampler runs, each counted with the same E3 count: " + "; ".join(more) + "."
                                   if more else "")
    t["sampler_note"] = SAMPLER_NOTE.get(ETA, "")
    t["outside_clause"] = (", and the " + ("betas" if len(extra) != 1 else "beta") + " counted outside that list "
                           + ("are" if len(extra) != 1 else "is") + " named above" if extra else "")
    t["outside_claim"] = " and the values counted outside that list" if extra else ""
    if extra:
        t["extra_betas_sentence"] = (
            "Outside that list, " + " and ".join(f"the beta {b} (k = {k}), which the solver search had returned, was counted as well: "
                                                 f"{num(p)} from {pos} outcomes" for p, b, k, pos in extra)
            + f". Together the count is {num(total)}.")
    else:
        t["extra_betas_sentence"] = f"No beta outside that list was counted, so the count is {num(total)}."
    if recount:
        missing = [b for _, b, _, _ in counted if b not in recount]
        differ = [b for p, b, _, _ in counted if b in recount and abs(recount[b][0] - p) > 0.06]
        if differ:
            raise SystemExit(f"the recount differs from the night's figures for {differ}")
        branch = sum(recount[b][2] for _, b, _, _ in counted if b in recount)
        fallback = sum(recount[b][3] for _, b, _, _ in counted if b in recount)
        t["recount_sentence"] = (
            f"The calculator was run a second time for {'all ' + str(len(counted)) if not missing else str(len(counted) - len(missing)) + ' of the ' + str(len(counted))} "
            f"betas with a nonzero part and returned the same parts. Its output states, for every one of them, how many "
            f"outcomes went through the random-subset branch of the E3 count and how many E1 counts fell back to a product "
            f"formula: {branch} and {fallback} in all." + ("" if branch == 0 and fallback == 0 else
                                                          " Where either number is not zero the part is not an exact count.")
            + (f" Of the {sum(recount[b][1] for _, b, _, _ in counted)} outcomes of these betas that have a nonzero E3 count, "
               f"{sum(paths.values())} have a nonzero E1 count as well; only these enter the sum." if full else ""))
        t["recount_exact"] = "yes" if branch == 0 and fallback == 0 and not missing else "no"
        # calc2_flag_short (rule_tokens): what the second count of the whole list reports for betas without a part
        t["recount_short"] = ("No part used an approximating fallback of the program" + t.get("calc2_flag_short", "") + "."
                              if t["recount_exact"] == "yes" else
                              "In a second run of the counting program some outcomes used one of its two approximating "
                              "fallbacks or were not rerun, so the figure is not a count in full.")
    else:
        t["recount_sentence"] = ("Whether an outcome of these betas went through the random-subset branch of the E3 count was "
                                 "not recorded for this class.")
        t["recount_exact"] = "unknown"
        t["recount_short"] = ("Whether an outcome used one of the counting program's two approximating fallbacks was not "
                              "recorded for this class.")

    # ---- checks of the counters: for the class of the package if its files exist, else for another class (named)
    path, e3_eta = class_check("e3check")
    e3 = read_e3check(path) if path else None
    if e3:
        own = e3_eta == ETA
        where = "the class of this package" if own else f"another class of the same constants, eta = {hx(e3_eta)}"
        e3_betas = CLASSES[e3_eta]["e3check_betas"]
        runs_of = (f"The sampler runs of the beta{'s' if len(e3_betas) != 1 else ''} {join(e3_betas)}" if e3_betas else
                   "Sampler runs of that class")
        top, rest_g, zeros = e3["top"], e3["rest"], e3["zeros"]
        all_rest = rest_g and top[0] + rest_g[0] == e3["nonzero"]
        t["e3check_paragraph"] = (
            f"Fourth, the E3 count for these constants and {where}. {runs_of} produced {e3['outcomes']} different outcomes, "
            f"{e3['nonzero']} with a nonzero E3 count and {e3['zero']} with zero"
            + ("" if e3["branch"] is None else ", none of them counted through the random-subset branch" if e3["branch"] == 0 else
               f", {e3['branch']} of them counted through the random-subset branch")
            + f". They were given to a SAT solver and to the approximate model "
            f"counter ApproxMC (tolerance 0.4, confidence 0.9) with the checking program of the earlier submissions. For the "
            f"{top[0]} largest counts the sum of the counter's values is {top[2]:.3f} times the sum of the independent counts, "
            f"with log2 differences between {top[3]} and {top[4]}"
            + (f"; for {'the other ' + str(rest_g[0]) if all_rest else str(rest_g[0]) + ' others drawn at random'} the ratio is "
               f"{rest_g[2]:.3f}, with log2 differences between {rest_g[3]} and {rest_g[4]}" if rest_g else "")
            + f". Of the {e3['zero']} zero counts, {zeros[0]} drawn at random were tested and "
            + ("none has a solution" if zeros[1] == zeros[0] else f"{zeros[1]} have no solution")
            + ("" if zeros[2] == 0 and zeros[3] == 0 else f" ({zeros[2]} have solutions, {zeros[3]} undecided)") + ".")
        t["e3_summary"] = (("" if own else f"for another class of them (eta = {hx(e3_eta)}), ")
                           + f"ratio of sums {top[2]:.3f} for the {top[0]} largest counts"
                           + (f" and {rest_g[2]:.3f} for {'the other' if all_rest else 'another'} {rest_g[0]}" if rest_g else "")
                           + f", and the {zeros[0]} zero counts tested have no solution")
        t["e3check_cover"] = (f"for the outcomes of {word(len(e3_betas)) if e3_betas else 'some'} beta{'s' if not e3_betas or len(e3_betas) != 1 else ''}"
                              + ("" if own else " of another class of the same constants"))
        t["e3check_claim"] = ("and of its count for the second call against a SAT solver and an independent model counter on the "
                              f"outcomes of {word(len(e3_betas)) if e3_betas else 'some'} value{'s' if not e3_betas or len(e3_betas) != 1 else ''} "
                              "of beta" + ("" if own else " of another class of the same constants"))
    else:
        t["e3check_paragraph"] = "Fourth, the E3 count for these constants has not been compared with an independent counter."
        t["e3_summary"] = "not made"
        t["e3check_cover"] = "not at all for these constants"
        t["e3check_claim"] = "and no check of its count for the second call with these constants"
    path, amc_eta = class_check("e1amc")
    amc = read_e1amc(path) if path else None
    if amc:
        own = amc_eta == ETA
        where1 = "the class of this package" if own else f"another class of the same constants, eta = {hx(amc_eta)},"
        # which of the outcomes the calculator itself counts as zero is known from the recount of this class only
        rc = recount.get(amc["beta"]) if own else None
        known = bool(rc and rc[4] is not None and amc["compared"] == rc[4] and amc["zero"] == rc[1] - rc[4] and amc["timeouts"] == 0)
        if rc and rc[4] is not None and not known and amc["compared"] + amc["zero"] + amc["timeouts"] == rc[1]:
            raise SystemExit("the ApproxMC check of E1 and the recount disagree on which outcomes have an E1 count of zero")
        nz = amc["zero"]
        zero_text = ("" if nz == 0 else
                     f"; for the {word(nz)} outcome{'s' if nz != 1 else ''} that the calculator counts as zero, ApproxMC finds no "
                     f"solution either" if known else
                     f"; for {word(nz)} further outcome{'s' if nz != 1 else ''} ApproxMC finds no solution")
        t["e1amc_paragraph"] = (
            f"Third, the exact E1 count at 32 bits against ApproxMC, for these constants, {where1} and beta {amc['beta']}: the "
            f"E1 system of an outcome was written as CNF straight from its definition and its solutions were counted. For "
            f"{amc['compared']} outcomes with a nonzero count the mean of log2(calculator / ApproxMC) is {amc['mean']} and the "
            f"largest difference is {amc['largest']} bits" + zero_text
            + ("" if amc["timeouts"] == 0 else f" ({amc['timeouts']} runs timed out)") + "."
            + (" These are all outcomes of that beta with a nonzero E3 count." if known else ""))
        t["e1amc_summary"] = (("" if own else f"for another class of them (eta = {hx(amc_eta)}), ")
                              + f"{amc['compared']} outcomes of one beta with a largest difference of {amc['largest']} bits"
                              + ("" if nz == 0 else f", and {word(nz)} outcome{'s' if nz != 1 else ''} that it counts as zero "
                                 f"{'have' if nz != 1 else 'has'} no solution" if known else
                                 f", and {word(nz)} further outcome{'s' if nz != 1 else ''} without a solution"))
        t["e1amc_cover"] = "for one beta at 32 bits" + ("" if own else ", of another class of the same constants")
        t["e1amc_claim"] = (" and against an independent model counter on outcomes of one value of beta at 32 bits"
                            + ("" if own else " of another class of the same constants"))
        t["e1amc_limit"] = (" and against an independent counter for one value of beta"
                            + ("" if own else " of another class of the same constants"))
    else:
        t["e1amc_paragraph"] = "Third, the exact E1 count has not been compared with an independent counter at 32 bits."
        t["e1amc_summary"] = "not made"
        t["e1amc_cover"] = "not at all at 32 bits"
        t["e1amc_claim"], t["e1amc_limit"] = "", ""
    bf = read_e1bf()
    if bf:
        t["e1bf_paragraph"] = (
            f"Second, the exact E1 count against brute force with 8-bit words: for {bf['cases']} random cases, all "
            f"{num(bf['outcomes'])} outcomes that have solutions were compared and {num(bf['equal'])} are equal"
            + ("" if bf["different"] == 0 else f" ({bf['different']} differ)")
            + f"; of the outcomes without solutions, {num(bf['zero_agree'] + bf['zero_disagree'])} were sampled and "
            f"{num(bf['zero_agree'])} are zero in the calculator as well.")
        t["bf_summary"] = (f"all {num(bf['outcomes'])} outcomes with solutions of {bf['cases']} random cases equal"
                           if bf["different"] == 0 else f"{bf['different']} of {num(bf['outcomes'])} outcomes differ")
    else:
        t["e1bf_paragraph"] = "Second, the exact E1 count has not been compared with brute force."
        t["bf_summary"] = "not made"
    parts = []
    for what, exact, branch, runs_ in OTHER_CHECKS:
        runs_text = " and ".join(f"{num(v)} with standard error {num(se)} ({name})" for v, se, name in runs_)
        parts.append(f"for {what}, {num(exact) if exact >= 1000 and abs(exact - round(exact)) < 0.05 else f'{exact:,.1f}'} against {runs_text}"
                     + (f"; here {branch} of the calculator's outcomes went through the random-subset branch of the E3 count" if branch else ""))
    zs = [abs(v - exact) / se for _, exact, _, runs_ in OTHER_CHECKS for v, se, _ in runs_]
    apart = [abs(r[0][0] - r[1][0]) / math.hypot(r[0][1], r[1][1]) for _, _, _, r in OTHER_CHECKS if len(r) == 2]
    t["other_checks_paragraph"] = (
        "First, the calculator against the sampler on other constants, where the sampler figures are those of the earlier "
        "submissions or of the night's runs: " + "; ".join(parts) + f". The {len(zs)} sampler figures are between "
        f"{min(zs):.1f} and {max(zs):.1f} standard errors from the calculator's."
        + (f" In the last case the two sampler runs differ from each other by {apart[-1]:.1f} of their combined standard "
           f"errors, and the calculator's figure lies between them." if apart and apart[-1] >= 2.5 else ""))

    # ---- the solver search
    found, info, longest = read_search()
    t["search_pins"] = WORDS[found] if found < len(WORDS) else str(found)
    if info:
        t["search_bound"], t["search_cost"], t["search_seconds"] = str(info["bound"]), str(info["cost"]), num(info["seconds"])
        t["search_eta"], t["search_beta"] = info["eta"], info["beta"]
        t["search_sol"] = " ".join(hx(v) for v in info["sol"])
        t["search_tau"], t["search_eps"] = info["tau"], info["eps"]
        apart = bin(int(info["eta"], 16) ^ ETA).count("1")
        t["search_class_sentence"] = (
            "The class of this package is the one of that solution." if apart == 0 else
            f"The class of this package is not the class of that solution; its eta differs from that of the solver's "
            f"solution in {word(apart)} bit{'s' if apart != 1 else ''}. It is one of the classes of the table above, where "
            f"the choice among them is described.")
        t["search_class_sentence_note"] = t["search_class_sentence"].replace(
            "It is one of the classes of the table above, where the choice among them is described.",
            "How it was chosen among the classes counted is said under \"The choice of the class\" above.")
        t["solution_paragraph"], sol_outcome = class_solution_paragraph(d, info)
        if ETA in CLASS_SOLUTION and "with Y4 in the class" in t["solution_paragraph"]:
            cs = CLASS_SOLUTION[ETA]
            sol_h1 = ror(cs["Y14"] ^ ((d["Y3"] + cs["Y4"]) & M32), 16)
            t["solution_paragraph"] += (f" For the solution printed here h1 = {hx(sol_h1)}, which "
                                        f"{'satisfies' if rule_a(sol_h1) else 'does not satisfy'} rule A.")
        t.update(outcome_tokens(d, heaviest[1], heaviest[0], heaviest[2], sol_outcome))
        t["solver_beta_sentence"] = (
            f"The beta of the solver's solution need not be a heavy one: here it carries {num(by_beta[info['beta']])} of the count."
            if int(info["eta"], 16) == ETA and info["beta"] in by_beta else "")
    else:
        raise SystemExit("the pin of PART A is not in the solver log")
    t["search_longest_min"] = str(-(-longest // 60))
    cands = read_candidates()
    mine = ",".join(hx(PIN[k]) for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
    own = [c for c in cands if c[1] == mine]
    others = sorted((c for c in cands if c[1] != mine), reverse=True)
    if own and others:
        best = "the largest count" if own[0][0] > others[0][0] else "not the largest count"
        vals = sorted(c[0] for c in others)
        median = vals[len(vals) // 2] if len(vals) % 2 else (vals[len(vals) // 2 - 1] + vals[len(vals) // 2]) / 2
        t["cand_sentence"] = (
            (f"For each of these sets" if len(cands) == found else f"For {len(cands)} of these sets")
            + f", the class of the solver's solution was counted over its "
            f"{CAND_BETAS} lightest betas. The constants of 3.2 had {best}, {num(own[0][0])}; the largest of the others was "
            f"{num(others[0][0])} and their median {num(median)}.")
    else:
        t["cand_sentence"] = "The sets of constants of the log were compared by the count of the class of the solver's solution."
    t["cand_sentence_note"] = (t["cand_sentence"].replace("For each of these sets", "For each set that the search returned")
                               .replace("of these sets", "of the sets that the search returned")
                               .replace("The constants of 3.2", "The constants used here"))

    # ---- real messages: the class of the package, or (named as such) another class of the same pin
    real, other = read_stats(night("real")), None
    deep, layout = read_stats(night("deep")), read_layout(night("layout"))
    layout_from = None        # (eta, its run with independent contexts) when the layout runs used are another class's
    if real["real"] is None:
        for e in REAL_FALLBACK:
            st = read_stats(NIGHT / CLASSES[e]["real"], e) if e != ETA else {"real": None}
            if st["real"] is not None:
                real, other = st, e
                deep, layout = read_stats(NIGHT / CLASSES[e]["deep"], e), read_layout(NIGHT / CLASSES[e]["layout"])
                break
    elif not layout:
        for e in REAL_FALLBACK:
            st = read_stats(NIGHT / CLASSES[e]["real"], e) if e != ETA else {"real": None}
            rows_e = read_layout(NIGHT / CLASSES[e]["layout"]) if e != ETA else []
            if rows_e and st["real"] is not None:
                layout, layout_from = rows_e, (e, st["real"])
                break
    host = real["check"]
    m = host and re.match(r"CHECK (\d+) of (\d+)", host)
    which = "this class" if other is None else f"another class of them, eta = {hx(other)}"
    if m:
        t["host_check_sentence"] = (
            f"A host program built the messages of {num(int(m.group(2)))} random trials of 6.1 with these constants and "
            f"{which}, and evaluated the complete 2-round hash of both messages of every trial: "
            + ("all" if m.group(1) == m.group(2) else f"{num(int(m.group(1)))}")
            + " agree on digest words 0, 2, 5 and 7, have Y4 in the class and the pinned words in place, and have the "
              "residual that 6.2 computes."
            + ("" if other is None else " The same check for the class of this package was not finished when this text "
                                        "was written."))
        t["host_check_note"] = (f"A host program rebuilt the messages of {num(int(m.group(2)))} random trials of the class "
                                f"search with these constants and {which}, and hashed both messages of each in full: all "
                                f"agree on digest words 0, 2, 5, 7, have Y4 in the class and the residual the proof computes.")
    else:
        t["host_check_sentence"] = "A host check of trials of 6.1 with these constants was not available for this text."
        t["host_check_note"] = "A host check on real messages was not available for this text."
    t.update(real_tokens(real, deep, layout, d, other, layout_from))
    t.update(toyalg_tokens(float(t["per_run"])))
    t.update(e1deep_tokens())
    t.update(e3deep_tokens(t["e1deep_runs"] == "2" and E3DEEP_REAL == E1DEEP_RUNS[-1]))
    t["submission_state"] = SUBMISSION_STATE
    rv = review_tokens()
    rows_h = read_outcomes(heaviest[1])
    if rows_h and rv["review_checks_paragraph"]:
        by_counts = sum(r[2] for r in rows_h) * 2.0 ** 39 / 2.0 ** (96 - heaviest[2])
        if abs(by_counts - 628.2) >= 0.05:
            rv["review_checks_paragraph"] = rv["review_checks_paragraph"].replace(
                "against 628.2 predicted", f"against 628.2 predicted ({by_counts:.2f} by the counts N1 of the table above; the "
                "report worked from logarithms kept to two decimals)")
    t.update(rv)
    # the remarks on the sampler that rest on a reviewer's computation apply to the class and betas it looked at
    if not (ETA == 0xE7C1815F and t.get("sampler_far_betas") == "1" and "58146852" in t.get("sampler_far_sentence", "")):
        t["review_sampler_sentence"], t["review_seed_sentence"] = "", ""
    # what bears on a spread of the layout runs beyond chance (only said when there is one)
    if t["layout_dispersed"] == "yes":
        items = []
        if t["deep_present"] == "yes":
            items.append(t["deep_bearing"])
        if t["toyalg_present"] == "yes":
            items.append(t["toyalg_bearing"])
        if t.get("class_spread_item"):
            items.append(t["class_spread_item"])
        items.append(f"the remark at the end of Section 7: under M the count gives {t['per_run']} expected trials with R = 0 "
                     f"and rule A per run, so the bound 0.39 would survive a clustering of them by a factor of up to "
                     f"{t['cluster_max']}")
        ordinal = ("First", "Second", "Third", "Fourth", "Fifth")
        t["dispersion_paragraph"] = (
            f"What this means for the three heuristics. The count that differs between runs is that of the early test of "
            f"Lemma E, which the algorithm of this package does not use. H2 is about the E1 test of Lemma N. Its passes "
            f"are the trials in which E1 requires the class; "
            + ("their counts in these runs show no such spread, and" if t["layout_e1_quiet"] == "yes" else
               "their counts in these runs are given above, and")
            + f" the budget of H2 is 2^{t['layout_margin']} above their mean. H3 is about rule A, which these runs did not "
            f"record; {t['a_runs']} other runs in the same layout did, and each has a share of trials that satisfy rule A "
            f"within {t['a_rel']} of 2^-{t['rule_pass_exp']}, relatively (reported below). For H1 it is a warning. H1 "
            f"treats the trials of a "
            f"run as independent with respect to its event, and here another event of the same trials, at a depth of about "
            f"2^{t['early_rate']}, is seen to depend on the seed words that all trials of a run share. "
            + t["layout_e1_clause"]
            + f" {word(len(items), True)} thing{'s' if len(items) != 1 else ''} bear{'' if len(items) != 1 else 's'} on the "
              f"question; none settles it for 32-bit words. "
            + " ".join(f"{ordinal[i]}, {it}." for i, it in enumerate(items)))
    else:
        t["dispersion_paragraph"] = ""
    t["sampler_seeds"] = SAMPLER_SEEDS
    cap = lambda text: text[0].upper() + text[1:]
    dispersed = t["layout_dispersed"] == "yes"
    t["betas_list_claim"] = f"the {t['betas_enumerated']} lightest values of beta"
    far = re.search(r"deviation of ([-+\d.]+) for beta", t.get("sampler_far_sentence", ""))
    t["sampler_far_claim"] = (f" (for one of them the sampler is {far.group(1).lstrip('+-')} standard errors "
                              f"{'above' if far.group(1).startswith('+') else 'below'} the counted value, which is not "
                              f"explained)" if far else "")
    t["review_claim"] = ("; and from checks by the participant's reviewing helper agents with programs of their own: the "
                         "whole count against a brute force of the seven-word system at 8-bit words, and Monte Carlo "
                         "estimates of both calls at 32 bits"
                         if t["review_present"] == "yes" else "")
    t["layout_e1_note"] += (f"; {t['a_runs']} further runs of 2^{t['a_run_trials']} trials in the same layout gave "
                            f"{t['a_e1_passes']} passes in all")
    t["h3_spread_claim"] = (
        f" The count of another test of the same trials, the early test of Lemma E, varies between runs with shared seed "
        f"words by more than chance, by about {t['layout_rel']}% of its value; that is far below the margin of this budget, "
        f"but it shows that such a count can depend on the seed words." if dispersed and t.get("layout_rel") else "")
    t["h2_limit_claim"] = (
        (f"; in {t['layout_runs_text']} with shared seed words the counts of this event show no spread beyond chance"
         if t["layout_e1_quiet"] == "yes" else "")
        + (", while the counts of another test of the same trials, the early test of Lemma E that the algorithm does not "
           "use, differ between these runs by more than chance" if dispersed and t["layout_e1_quiet"] == "yes" else
           f"; {t['layout_runs_text']} with shared seed words differ from each other by more than chance in another test "
           f"of the same trials" if dispersed else ""))
    t["review_note_sentence"] = (t["review_note"] + ". They are helper agents of mine, not independent parties."
                                 if t["review_present"] == "yes" else "None is reported here.")
    t["real_notes_claim"] = "; ".join(x for x in (t["real_model_claim"], t["deep_claim"], t["e1deep_claim"],
                                                  t["e3deep_claim"], t["layout_note_short"]) if x)
    e1d, e3d = t["e1deep_state"] == "done", t["e3deep_state"] == "done"
    depth_c = re.search(r"probability of 2\^(-[\d.]+) per trial", t["e1deep_paragraph"])
    t["deep_limit_claim"] = (
        f" (below that depth each of the two calls has been counted on real messages only by itself: the first on an "
        f"event of probability 2^{depth_c.group(1)} per trial, the second, without the third of its conditions, on one of "
        f"{t['e3deep_total']}; nothing tests the full count of the second call or the two calls together)"
        if e3d and depth_c else
        " (below that depth only the first call has been counted on real messages, by itself)" if e1d else "")
    extra = [x for x in (t["e1deep_high_claim"], t["e1deep_beta_claim"]) if x]
    t["deep_caveats_claim"] = (" " + " ".join(extra)) if extra else ""
    t["deep_limit_note"] = (" (somewhat deeper for one call at a time, E3 only without its third condition)" if e3d else
                            " (somewhat deeper for E1 alone)" if e1d else "")
    t["deep_counts_note"] = (
        (cap(t["e1deep_note"]) + ". " if t["e1deep_note"] else "")
        + (cap(t["e3deep_note"]) + ". " if t["e3deep_note"] else "")
        + (t["e1deep_beta_note"] + " " if t["e1deep_beta_note"] else "")
        + ("These counts test E1 alone, and E3 alone without the third of its conditions. Nothing tests the full E3 "
           "count or E1 and E3 together on real messages." if e3d else
           "These counts test E1 alone. Nothing tests E3 or the two calls together at that depth." if e1d else
           "No such count is reported here."))
    t["deep_note_sentence"] = cap(t["deep_note"]) + "."
    t["e1deep_note_sentence"] = cap(t["e1deep_note"]) + "." if t["e1deep_note"] else ""
    spread_words = re.search(r"the ratio of their variance to their mean is ([\d.]+)", t["layout_note"])
    t["layout_claim_limit"] = (
        f"{cap(t['layout_runs_text'])} with shared seed words differ by more than chance in their passes of the "
        f"early test of Lemma E "
        f"(variance over mean {spread_words.group(1)}); that is unexplained and is a dependence on shared words of "
        f"the kind that the independence assumed here excludes for the event of H1." if dispersed and spread_words else "")
    t["layout_spread_note"] = ("The number of trials in which E1 requires the class shows no such excess. The spread bears on "
                               "the independence that H1 assumes; the proof says what was measured on it."
                               if dispersed else "")
    t["layout_spread_limit"] = ("On real messages the number of passes of the early test of Lemma E, which this package's "
                                "algorithm does not use, varies between runs by more than chance, which I have not explained."
                                if dispersed else "")
    toy_now = t["toyalg_present"] == "yes"
    t["run_distribution_claim"] = (
        f"Scaled-down runs in the algorithm's own layout count the runs with at least one collision, but for words of "
        f"{t['toyalg_bits']} and with other constants; so the distribution of collisions within one run of the algorithm "
        f"has been tested directly only at those word sizes." if toy_now else
        "The scaled-down runs hold other words fixed than a run of the algorithm does and use other constants. So the "
        "distribution of collisions within one run of the algorithm has not been tested directly.")
    t["run_distribution_note"] = (
        f"The distribution of collisions within one run of the algorithm has been tested directly only for words of "
        f"{t['toyalg_bits']} and with other constants." if toy_now else
        "The distribution of collisions within one run of the algorithm has not been tested directly at any word size.")
    t["toyalg_note_sentence"] = (
        f"The same attack was run with words of {t['toyalg_bits']} in the layout of the algorithm itself: four seed words "
        f"per run, the contexts in a fixed order, every alpha and every member of the best class, with the number of "
        f"contexts set so that the model predicts 0.5 or 1.7 collisions per run. Result: {t['toyalg_note']}. "
        + t["toyalg_added_note"]
        + f"This is the direct test of \"at least one collision per run\" that the note of `{SUBMISSIONS[-1][0]}` named as "
          f"missing. It is at small word sizes and with other constants, not evidence for these constants."
        if toy_now else "No such runs are reported here.")
    state = t["e1deep_state"]
    depth_open = re.search(r"probability of 2\^(-[\d.]+) per trial", t["e1deep_paragraph"])
    t["e1deep_open"] = (
        f"the counts of E1 outcomes reach about 2^{depth_open.group(1)} and the count of partial E3 events "
        f"{t['e3deep_total']}, each for one call alone"
        if state == "done" and depth_open and t["e3deep_state"] == "done" else
        f"a run that counts the E1 outcomes of the heavy betas on real messages reaches about 2^{depth_open.group(1)}, for "
        f"one call alone" if state == "done" and depth_open else
        f"a run that counts the E1 outcomes of the heavy betas on real messages, at about 2^{depth_open.group(1)} and for "
        f"one call alone, was under way when this was written" if state == "running" and depth_open else
        "the outcomes of one call alone can be counted on real messages somewhat below that")
    t["classes_counted_cap"] = cap(t["classes_counted"])
    depth = re.search(r"probability of 2\^(-[\d.]+) per trial", t["e1deep_paragraph"])
    if t["e1deep_state"] == "done" and depth:
        e3d = t["e3deep_state"] == "done"
        t["real_depth_sentence"] = (
            f"The comparisons with M concern events of probability about 2^-32 and above. The counts of E1 outcomes "
            f"concern an event of probability 2^{depth.group(1)} per trial, all listed outcomes together, for E1 alone"
            + (f"; the count of partial E3 events concerns one of {t['e3deep_total']}, with single events from "
               f"{t['e3deep_depth']}, for E3 alone and without its third condition" if e3d else "")
            + ". None of them reaches the event R = 0, and none joins the two calls.")
        t["e1deep_limit_clause"] = (
            f"; below that, E1 alone has been counted on an event of probability 2^{depth.group(1)}"
            + (f", and E3 alone, without its third condition, on one of {t['e3deep_total']}" if e3d else ""))
    else:
        t["real_depth_sentence"] = ("These statistics concern events of probability about 2^-32 and above. They do not "
                                    "reach the event R = 0.")
        t["e1deep_limit_clause"] = ""
    toy = t["toyalg_present"] == "yes"
    t["toy_bits_all"] = "8 to 10 bits" if toy else "8 and 10 bits"
    t["toyalg_forward_sentence"] = (
        "For the class search that is tested by the runs in the layout of the algorithm reported further below, and for "
        "the unrestricted search in the paragraph that follows." if toy else
        "For the class search that is not tested; it is tested only for the unrestricted search, in the paragraph that "
        "follows.")
    t["run_distribution_sentence"] = (
        t["toyalg_limit"] + " So the distribution of collisions within one run of 6.4 has been tested directly only at "
        "those word sizes, and not for 32-bit words or for the constants of this package." if toy else
        "The scaled-down runs count actual collisions, but with other constants, and a run there holds X2, X9, X13 and "
        "X14 fixed, not the seed words. So the distribution of collisions within one run of 6.4 has not been tested "
        "directly at any word size.")
    t["class_rank_sentence"] = (f"Among the {t['classes_counted']} classes of these constants that were counted, the class "
                                f"used is the {t['class_rank']}.")
    t["intro_choice_sentence"] = (
        "The six constants and the class were found by a solver search and chosen by this count."
        if t["class_rank"] == "largest" else
        f"The six constants were found by a solver search and chosen by this count. The class is the {t['class_rank']} by "
        f"this count among the {t['classes_counted']} classes of these constants that were counted; Section 10 says why it "
        f"is used.")
    t["h2_limit_sentence"] = (
        (f"In the {t['layout_runs_text']} with shared seed words the counts of this event are {t['layout_e1_counts']}"
         + (", with no spread beyond chance" if t["layout_e1_quiet"] == "yes" else "")
         + f"; the budget is 2^{t['layout_margin']} above their mean.") if t["layout_runs"] != "0" else "")
    step = float(SUBMISSIONS[-1][1]) - d["time_log2"]
    t["previous_F"], t["previous_factor"] = str(PREVIOUS_LOG2_FACTOR), num(2 ** PREVIOUS_LOG2_FACTOR)
    t.update(draft_tokens(d, t))
    if t["draft_present"] != "yes":
        t["draft_note"] = "The earlier version of this package is not at hand, so no comparison with it is made here."
    t["previous_batch"] = f"{PREVIOUS_BATCH[0]} operations and {PREVIOUS_BATCH[1]} loads for every batch"
    t["a_runs_cap"] = cap(t["a_runs"])
    t["rule_amc_note_sentence"] = (cap(t["rule_amc_note"]) + " (a check of the E3 count for this class, made by the thread "
                                   "that found rule A)." if t["rule_amc_note"] else "")
    t["toystage_note_sentence"] = (
        cap(t["toystage_note"]) + ". The rule on h1 in these runs is of the kind that every solution satisfies, found by "
        "brute force; every collision found passed it and the second test, and the test word of every trial equalled the "
        "word of the residual that the proof's Lemma N names. They test the logic of dropping trials early and the second "
        "test, not rule A of this package, which loses solutions." if t["toystage_note"] else "No such runs are reported here.")
    t["rule_example_note"] = ("The proof prints one complete solution of the system that violates rule A."
                              if t["rule_example_state"] == "yes" else "")
    t["big_note_sentence"] = (f"Longer runs of the same self-test: {t['big_lanes']} lanes, all right."
                              if t["big_runs"] != "0" else "")
    t["version_review_sentence"] = VERSION_REVIEW
    # VERSION_REVIEW and VERSION_REVIEW_PROOF say that three programs of the reviewers were run again and are reported;
    # that is only true while their three result files are there and sound
    if not (t["rule_solvers"] != WORDS[1] and t["lay_state"] != "none" and t["seeds_state"] != "none"):
        raise SystemExit("VERSION_REVIEW (PART A) names three programs of the reviewers whose results the text reports, but a "
                         "result file is missing or not sound: run tools/rule_a_sat2.py, tools/rule_share.sh and "
                         "tools/rule_share_seeds.py, or change the two sentences")
    t["review2_paragraph"] = VERSION_REVIEW_PROOF
    t["review_reruns_note"] = (
        f"Three programs of reviewing helper agents were run again for this version: the questions on rule A with a "
        f"second formula and other solvers ({t['rule_solvers']} solvers in all, the same answer for each of the "
        f"{t['rule_outcomes']} outcomes), and two counts of rule A and of the batches that run stage 2 on real trials in "
        f"the algorithm's layout ({t['lay_state']} trials; {t['seeds_state']}).")
    gain = math.log2(PREVIOUS_CHARGE / CHARGE)
    if f"{gain:.2f}" != t["charge_gain"]:
        raise SystemExit("the gain of the charge per trial is printed with two different roundings")
    if CHARGE != PREVIOUS_CHARGE:
        t["step_sentence"] = (
            f"The claimed scalar is {step:.1f} below that of submission {SUBMISSIONS[-1][0]}. Of that difference, "
            f"{LOG2_FACTOR - PREVIOUS_LOG2_FACTOR} bits are the factor that H1 assumes, 2^{LOG2_FACTOR} here against "
            f"2^{PREVIOUS_LOG2_FACTOR} there, and about {gain:.2f} bits are the cost charged per trial, {CHARGE} operations "
            f"here against {PREVIOUS_CHARGE} there; the rest is rounding of the two bounds.")
        t["step_note"] = (
            f"The claim is {step:.1f} bits below that of `{SUBMISSIONS[-1][0]}`: {LOG2_FACTOR - PREVIOUS_LOG2_FACTOR} bits "
            f"are the factor that H1 assumes, 2^{LOG2_FACTOR} = {num(2 ** LOG2_FACTOR)} here and 2^{PREVIOUS_LOG2_FACTOR} = "
            f"{num(2 ** PREVIOUS_LOG2_FACTOR)} there, and about {gain:.2f} bits are the cost of a trial, {CHARGE} charged "
            f"operations here and {PREVIOUS_CHARGE} there; the rest is rounding.")
    elif abs(step - (LOG2_FACTOR - PREVIOUS_LOG2_FACTOR)) < 1e-9:
        t["step_sentence"] = (
            f"The claimed scalar is {step:.0f} below that of submission {SUBMISSIONS[-1][0]}. All of that difference is "
            f"the factor that H1 assumes, 2^{LOG2_FACTOR} here against 2^{PREVIOUS_LOG2_FACTOR} there; the cost charged "
            f"per trial is the same.")
        t["step_note"] = (
            f"The claim is {step:.0f} bits below that of `{SUBMISSIONS[-1][0]}`. All {step:.0f} bits are the factor that "
            f"H1 assumes: 2^{LOG2_FACTOR} = {num(2 ** LOG2_FACTOR)} here, 2^{PREVIOUS_LOG2_FACTOR} = "
            f"{num(2 ** PREVIOUS_LOG2_FACTOR)} there. The cost of a trial is unchanged.")
    else:
        t["step_sentence"] = (
            f"The claimed scalar is {step:.1f} below that of submission {SUBMISSIONS[-1][0]}; the factor that H1 assumes "
            f"is 2^{LOG2_FACTOR} here against 2^{PREVIOUS_LOG2_FACTOR} there.")
        t["step_note"] = (f"The claim is {step:.1f} bits below that of `{SUBMISSIONS[-1][0]}`; the factor that H1 assumes "
                          f"is 2^{LOG2_FACTOR} here against 2^{PREVIOUS_LOG2_FACTOR} there.")
    return d, t


def solution_paragraph(d, info):
    """The solver's solution of the seven-word system, written as the inputs of E1 and E3 of 6.2, and checked here."""
    d1, b1, a2, y4, h1, y9, w8 = info["sol"]
    a1, w12 = 0, 0                                    # E1's first sum is free: take a1 = 0 with w12 = 0
    y12 = rol(d1, 16) ^ a1
    y6 = rol(b1, 12) ^ ((d["Y11"] + d1) & M32)
    y1 = (a1 - y6 - w12) & M32
    w5 = (a2 - a1 - b1) & M32
    y14 = rol(h1, 16) ^ ((d["Y3"] + y4) & M32)
    pa = g_steps(y1, y6, d["Y11"], y12, w12, w5)
    pb = g_steps(y1, y6, d["Y11B"], y12, w12, (w5 + d["delta"]) & M32)
    qa = g_steps(d["Y3"], y4, y9, y14, 0, w8)
    qb = g_steps(d["Y3B"], y4, y9, y14, 0, w8)
    residual = (pa["a2"] ^ qa["c2"] ^ pb["a2"] ^ qb["c2"], qa["a2"] ^ pa["c2"] ^ qb["a2"] ^ pb["c2"],
                qa["b2"] ^ pa["d2"] ^ qb["b2"] ^ pb["d2"], pa["b2"] ^ qa["d2"] ^ pb["b2"] ^ qb["d2"])
    if any(residual) or (pa["d1"], pa["b1"], pa["a2"], qa["d1"]) != (d1, b1, a2, h1):
        raise SystemExit("the solver's solution does not give a zero residual in 6.2")
    in_class = ((d["Y3"] + y4) & d["qmask"]) == d["qvalue"]
    where = ("with Y4 in the class" if in_class else
             f"whose Y4 is not in the class of this package (its eta is {info['eta']})")
    return (f"A complete solution of the seven-word system {where}, which can be checked by hand from 6.2: "
            f"Y1 = {hx(y1)}, Y6 = {hx(y6)}, Y12 = {hx(y12)}, w12 = {hx(w12)}, w5 = {hx(w5)}, Y4 = {hx(y4)}, Y9 = {hx(y9)}, "
            f"Y14 = {hx(y14)}, w15 = 0, w8 = {hx(w8)}. For these values the four residual words of 6.2 are zero; E1 has "
            f"beta = {info['beta']}, and the XOR differences of its a and c outputs are {info['tau']} and {info['eps']}. It is the "
            f"solution that the solver search returned with the constants. It shows that the constants do not exclude "
            f"R = 0; it does not show that a message reaches such values.")


def real_tokens(real, deep, layout, d, other=None, layout_from=None):
    """Paragraphs on the real-message runs and the figures H2 uses; every sentence is true for the files as they are.

    other: None when the runs are of the class of the package, else the eta of the class of the same pin they are of.
    layout_from: None when the layout runs are of the same class as the other runs; else (eta, the run with
    independent contexts of that class), when only the layout runs are another class's."""
    t = {}
    T = d["T"]
    r, m = real["real"], real["model"]
    if r is None:
        raise SystemExit("no real-message run for any class of this pin: H2 has no measured pass rate (see CLASSES)")
    if other is None:
        of, lead, short = ("the constants and the class of this package", "For the constants and the class of this package",
                           "these constants and this class")
        t["pass_measured_on"] = "real trials of the class search"
        t["real_scope"] = "these constants"
        note_prefix = ""
    else:
        of = f"another class of the same constants, eta = {hx(other)}"
        lead = (f"No run of this kind had finished for the class of this package when this text was written. For another "
                f"class of the same constants, eta = {hx(other)}")
        short = f"another class of these constants (eta = {hx(other)})"
        t["pass_measured_on"] = (f"real trials of the class search for another class of the same constants, eta = {hx(other)} "
                                 f"(no run for the class of this package had finished when this text was written),")
        t["real_scope"] = f"these constants, in another class (eta = {hx(other)}),"
        note_prefix = f"for another class of the same constants (eta = {hx(other)}), "
    t["real_class"] = of
    t["pass_measured_short"] = short
    lt = round(r["trials"][1])
    # H2 is about the E1 test of Lemma N. The programs print its passes as "E1 requires the eta of Y4" (key "eta"):
    # the trials in which E1 alone requires the class of the trial's Y4, that is eps XOR ROL(beta XOR eps, 1) = eta.
    rate = math.log2(r["eta"][1]) - lt
    t["pass_rate"] = f"{up(rate, 2):.2f}"
    t["pass_expected"] = f"{up(T + rate, 2):.2f}"
    t["pass_margin"] = f"{math.floor((d['pass_budget'] - (T + rate)) * 100) / 100:.2f}"
    t["pass_count"], t["pass_trials"] = num(r["eta"][1]), str(lt)
    t["early_rate"] = f"{math.log2(r['early'][1]) - lt:.2f}"       # the early test of Lemma E, which the algorithm does not use
    if d["pass_budget"] - (T + rate) < 8:
        raise SystemExit("the budget on passes of the E1 test is less than 2^8 above the expected number: raise it (PASS_SHIFT)")

    def quad(s):
        return ", ".join(num(s[f"wz{i}"][1]) for i in range(4))

    def compare(rr, mm, label):
        pair = lambda k: f"{num(rr[k][1])} / {num(mm[k][1])}"
        az, z, key = deviations(rr, mm)[0]
        side = "the model higher" if z < 0 else "real messages higher"
        text = (f"{label}, with 2^{round(rr['trials'][1])} trials of each kind (real messages / model): early test passes "
                f"{pair('early')}; trials in which E1 requires the class {pair('eta')}; the four residual words zero {quad(rr)} "
                f"/ {quad(mm)}; residual of weight at most 32: {pair('wt32')}; of weight at most 40: {pair('wt40')}; all four "
                f"residual words with a zero low byte: {pair('z8')}. Among all the statistics that the two programs print "
                f"with at least 30 events, the largest deviation is {az:.1f} standard deviations, {side} ({rr[key][0]}: "
                f"{pair(key)}).")
        many = sum(1 for a, _, _ in deviations(rr, mm) if a >= 2.0)
        uniform = 2.0 ** (round(rr["trials"][1]) - 32)
        often = [(i, min(rr[f"wz{i}"][1], mm[f"wz{i}"][1]) / uniform) for i in range(4)
                 if min(rr[f"wz{i}"][1], mm[f"wz{i}"][1]) > 2 * uniform]
        for i, ratio in often:
            text += (f" The {ORD[i]} residual word is zero about {ratio:.0f} times as often as a uniform word would be "
                     f"({num(uniform)} expected), on real messages and in the model alike.")
        return text, az, len(deviations(rr, mm)), many

    def count_text(count, many):
        return (f" {count} statistics were compared; {many} of them deviate{'s' if many == 1 else ''} by 2.0 standard "
                f"deviations or more.")

    if m is not None:
        text, az, count, many = compare(r, m, lead)
        t["real_model_paragraph"] = text + count_text(count, many) + (
            " A standard deviation here is the square root of the sum of the two counts.")
        t["real_largest_clause"] = f", with a largest deviation of {az:.1f} standard deviations"
        t["real_model_claim"] = (f"{note_prefix}2^{lt} trials of each kind: early test passes {num(r['early'][1])} on real "
                                 f"messages against {num(m['early'][1])} in the model, largest deviation among the printed "
                                 f"statistics {az:.1f} standard deviations")
        t["real_model_note"] = (f"{note_prefix}2^{lt} trials of each kind: early test passes {num(r['early'][1])} on real "
                                f"messages against {num(m['early'][1])} in the model; residuals of weight at most 32: "
                                f"{num(r['wt32'][1])} against {num(m['wt32'][1])}; the largest deviation among the printed "
                                f"statistics is {az:.1f} standard deviations")
    else:
        t["real_model_paragraph"] = (
            f"{lead}, 2^{lt} real trials gave {num(r['early'][1])} early-test "
            f"passes. The run of the model with the same number of draws was not finished when this text was written, so "
            f"no comparison is made here.")
        t["real_largest_clause"] = ""
        t["real_model_note"] = (f"{note_prefix}2^{lt} real trials: {num(r['early'][1])} early-test passes; the model run is "
                                f"not finished")
        t["real_model_claim"] = t["real_model_note"]
    t["real_wrong_y4"] = str(r["bad"][1])
    if deep["real"] is not None and deep["model"] is not None:
        text, az, count, many = compare(deep["real"], deep["model"], "A second comparison")
        t["deep_paragraph"] = text + count_text(count, many)
        t["deep_largest"] = f"{az:.1f}"
        t["deep_present"] = "yes"
        dr, dm = deep["real"], deep["model"]
        dl = round(dr["trials"][1])
        per = 2.0 ** (lt - dl)
        t["deep_bearing"] = (
            f"averaged over independent contexts the pass rate agrees with M: {num(dr['early'][1])} passes against "
            f"{num(dm['early'][1])} in 2^{dl} trials of each kind (above), that is {dr['early'][1] * per:,.0f} against "
            f"{dm['early'][1] * per:,.0f} per 2^{lt} trials"
            + (f", and the mean of the {word(len(layout))} layout runs is {sum(p for _, p, _, _ in layout) / len(layout):,.0f}; "
               f"it is the spread between runs that M does not give" if layout and layout_from is None else ""))
        t["deep_claim"] = (f"2^{dl} trials of each kind: {num(dr['early'][1])} against {num(dm['early'][1])}, largest "
                           f"deviation {az:.1f}")
        t["deep_note"] = (f"a second comparison with 2^{dl} trials of each kind: early test passes {num(dr['early'][1])} "
                          f"against {num(dm['early'][1])}, trials in which the first call requires the class "
                          f"{num(dr['eta'][1])} against {num(dm['eta'][1])}, largest deviation {az:.1f} standard deviations")
    else:
        t["deep_paragraph"] = ("A larger comparison of this kind was not finished when this text was written; none is used "
                               "here.")
        t["deep_largest"], t["deep_present"] = "none", "no"
        t["deep_bearing"], t["deep_note"], t["deep_claim"] = "", "a larger comparison was not finished", ""
    if layout:
        passes = [p for _, p, _, _ in layout]
        mean = sum(passes) / len(passes)
        n = len(passes)
        lead_l, own_gap, lr = "", "", r
        if layout_from is not None:
            e, lr = layout_from
            of = f"another class of the same constants, eta = {hx(e)}"
            short = f"another class of these constants (eta = {hx(e)})"
            note_prefix = f"for another class of the same constants (eta = {hx(e)}), "
            lead_l = ("No run in the layout of the algorithm had finished for the class of this package when this text "
                      "was written. ")
            own_gap = ("For the class of this package no run in the layout of the algorithm had finished when this text "
                       "was written. ")
        r, lt = lr, round(lr["trials"][1])        # from here on: the run with independent contexts of the layout's class
        ref = r["early"][1]                       # same number of trials per run assumed (2^lt)
        runs_text = f"{word(n)} run{'s' if n != 1 else ''}"
        text = (f"{lead_l}A second measurement uses the layout of the algorithm, for {of}: "
                f"{runs_text} of 2^{lt} real trials of 6.1. {'Each' if n != 1 else 'The'} run has its "
                f"own four seed words X2, X5, X6 and X9, shared by all its contexts. A context is one thread of the "
                f"program: a random (X12, X13, X14) with X12 < 2^{LOG2_X12}, and 4,096 trials, each with a random alpha and a "
                f"random member of the class. Two things differ from 6.4: X13 is not restricted, and the program leaves "
                f"the context word X10 random in every thread where step 1 sets it to zero, so that S5, which the "
                f"algorithm holds fixed over a run, changes from context to context. Early-test passes: "
                + join(num(p) for p in passes) + (f", in all {num(sum(passes))}" if n > 1 else "")
                + f". The run with independent contexts{' of that class' if layout_from is not None else ''} gave "
                  f"{num(ref)} in the same number of trials")
        if n > 1:
            z = (mean - ref) / math.sqrt(mean / n + ref)
            text += (f"; the mean of the runs, {mean:,.1f}, is {abs(z):.1f} standard deviations "
                     f"{'below' if z < 0 else 'above'} it")
        e1s = [e for _, _, e, _ in layout]
        text += "."
        e1_sentence = (" E1 required the class of the trial's Y4 in " + join(num(e) for e in e1s)
                       + f" trials, against {num(r['eta'][1])} with independent contexts.")
        if any(c for _, _, _, c in layout):
            raise SystemExit("a layout run reports contradictions")
        dispersed, disp_note, disp_h2 = False, "", ""
        t["layout_e1_clause"] = ""
        if n >= 4:
            _, ratio, chi, p_chi = spread(passes)
            _, _, chi1, p1 = spread(e1s)
            t["layout_e1_chi"] = (f", with no spread beyond chance (chi-square {chi1:.1f} on {n - 1} degrees of freedom)"
                                  if p1 >= 0.05 else f", with a spread beyond chance (chi-square {chi1:.1f} on {n - 1} degrees of freedom)")

            def away(j):
                rest = [x for i, x in enumerate(passes) if i != j]
                mo = sum(rest) / len(rest)
                return (passes[j] - mo) / math.sqrt(mo * (1 + 1 / len(rest)))

            j = max(range(n), key=lambda i: abs(away(i)))
            text += (f" The ratio of the variance of the {word(n)} pass counts to their mean is {ratio:.1f}, where "
                     f"independent trials give 1 on average; the chi-square statistic against a common mean is {chi:.1f} "
                     f"on {n - 1} degrees of freedom, which chance exceeds with probability {prob(p_chi)}.")
            if p_chi < 0.05:
                dispersed = True
                rel = 100 * math.sqrt(max(ratio - 1, 0) / mean)
                t["layout_rel"] = f"{rel:.1f}"
                text += (f" Run {layout[j][0]} is {abs(away(j)):.1f} standard deviations "
                         f"{'above' if away(j) > 0 else 'below'} the mean of the other {word(n - 1)}. So the number of "
                         f"early-test passes of a run differs between runs by more than chance: it depends on the seed "
                         f"words of the run, by about {rel:.1f}% of its value. The cause was not found.")
                disp_note = (f"; the ratio of their variance to their mean is {ratio:.1f} (chi-square {chi:.1f} on {n - 1} "
                             f"degrees of freedom), so the pass count of a run varies between runs by more than chance, "
                             f"which is not explained")
                disp_h2 = (f": their pass counts lie between {num(min(passes))} and {num(max(passes))} and differ from run "
                           f"to run by more than chance, by about {rel:.1f}% of the count")
            else:
                text += " That is what independent trials give."
            text += e1_sentence
            e1_sentence = ""
            text += (f" For these counts the chi-square statistic is {chi1:.1f} on {n - 1} degrees of freedom"
                     + (", no excess." if p1 >= 0.05 else f", probability {prob(p1)}."))
            t["layout_e1_clause"] = (
                f"The number of trials in which E1 requires the class, an event that R = 0 needs, shows no such dependence "
                f"at a depth of about 2^{math.log2(sum(e1s) / n) - lt:.1f}, but that is far from the depth of R = 0."
                if p1 >= 0.05 else
                f"The number of trials in which E1 requires the class, an event that R = 0 needs, varies between runs as "
                f"well (chi-square {chi1:.1f} on {n - 1} degrees of freedom).")
        text += e1_sentence
        t["layout_dispersed"] = "yes" if dispersed else "no"
        text += (f" {'These runs record' if n != 1 else 'This run records'} these two counts and nothing else; in "
                 f"particular no residual words and no pair statistics.")
        t["layout_e1_note"] = (f"{note_prefix}{runs_text} of 2^{lt} real trials with shared seed words gave "
                               + join(num(e) for e in e1s) + " passes" + t.get("layout_e1_chi", ""))
        mean_e1 = sum(e1s) / len(e1s)                # H2: passes of the E1 test in the layout runs
        t["layout_margin"] = f"{math.floor((d['pass_budget'] - (T + math.log2(mean_e1) - lt)) * 100) / 100:.2f}"
        t["layout_e1_counts"] = join(num(e) for e in e1s)
        t["layout_e1_rate"] = f"{math.log2(mean_e1) - lt:.2f}"
        planned = CLASSES[ETA if (layout_from is None and other is None) else (layout_from[0] if layout_from else other)].get("layout_planned")
        if planned and n < planned:
            text += " More runs of this kind were under way when this text was written."
        t["layout_paragraph"] = text
        t["layout_runs"] = str(n)
        t["layout_runs_text"] = runs_text
        e1_quiet = n >= 4 and spread(e1s)[3] >= 0.05
        t["h2_support"] = (f"; Section 10 reports {runs_text} of 2^{lt} trials in the layout of the algorithm"
                           + (", made for another class of the same constants," if layout_from is not None else "")
                           + (f", with between {num(min(e1s))} and {num(max(e1s))} passes of the E1 test each"
                              + (" and no spread beyond chance" if e1_quiet else "")))
        t["layout_e1_quiet"] = "yes" if e1_quiet else "no"
        t["layout_note"] = (f"{note_prefix}{runs_text} of 2^{lt} real trials with shared seed words gave "
                            + join(num(p) for p in passes) + f" early-test passes ({num(ref)} with independent contexts)"
                            + disp_note)
        t["layout_note_short"] = (
            (f"{note_prefix}{runs_text} of 2^{lt} real trials with shared seed words gave between {num(min(passes))} and "
             f"{num(max(passes))} early-test passes ({num(ref)} with independent contexts)" + disp_note)
            if n > 2 else t["layout_note"])
        t["layout_note_sentence"] = (t["layout_note"][0].upper() + t["layout_note"][1:]
                                     + f". {'These runs record' if n != 1 else 'This run records'} only the early test and the "
                                       f"number of trials in which E1 requires the class.")
        t["layout_limit_sentence"] = (
            f"{own_gap}For {short} there {'are' if n != 1 else 'is'} {runs_text} of 2^{lt} trials in the layout of the "
            f"algorithm, in which S5 was not shared and X13 was not restricted; {'they record' if n != 1 else 'it records'} "
            f"only the early test and the number of trials in which E1 requires the class"
            + (", and their pass counts differ by more than chance." if dispersed else "."))
    else:
        t["layout_paragraph"] = ("Runs in the layout of the algorithm, with seed words shared by all contexts of a run, were "
                                 "not finished for these constants when this text was written. The comparison above is "
                                 "therefore the only measurement on real messages that is used here.")
        t["layout_runs"], t["h2_support"] = "0", ""
        t["layout_runs_text"] = "no runs"
        t["layout_margin"] = ""
        t["layout_e1_counts"], t["layout_e1_rate"], t["layout_e1_quiet"] = "", "", "no"
        t["layout_e1_note"] = "runs with shared seed words were not finished for these constants"
        t["layout_dispersed"], t["layout_e1_clause"] = "no", ""
        t["layout_note"] = "runs with shared seed words were not finished for these constants"
        t["layout_note_short"] = t["layout_note"]
        t["layout_note_sentence"] = "Runs with shared seed words were not finished for these constants."
        t["layout_limit_sentence"] = ("For these constants no run in the layout of the algorithm had finished when this "
                                      "text was written.")
    return t


# =====================================================================================================
# PART E: readers and paragraphs of the second round (classes of the pin, statistics of the layout runs,
#         scaled-down runs in the layout of the algorithm, the deep E1 run, the reviewers' checks,
#         the solution inside the class, the outcomes of the heaviest beta, the validation log)
# =====================================================================================================
def chi2_sf(x, k):
    """Upper tail of the chi-square distribution with k degrees of freedom (regularised incomplete gamma)."""
    a, x = k / 2.0, x / 2.0
    if x <= 0:
        return 1.0
    front = math.exp(-x + a * math.log(x) - math.lgamma(a))
    if x < a + 1:
        term = total = 1.0 / a
        n = a
        for _ in range(1000):
            n += 1
            term *= x / n
            total += term
            if term < total * 1e-16:
                break
        return 1.0 - total * front
    tiny = 1e-300
    b = x + 1 - a
    c, dd = 1 / tiny, 1 / b
    h = dd
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2
        dd = an * dd + b
        dd = tiny if abs(dd) < tiny else dd
        c = b + an / c
        c = tiny if abs(c) < tiny else c
        dd = 1 / dd
        delta = dd * c
        h *= delta
        if abs(delta - 1) < 1e-16:
            break
    return front * h


def prob(p):
    return "below 0.001" if p < 0.001 else f"about {p:.3f}" if p < 0.1 else f"about {p:.2f}"


def spread(xs):
    """(mean, variance over mean, chi-square against a common mean, its upper-tail probability)."""
    m = sum(xs) / len(xs)
    chi = sum((x - m) ** 2 for x in xs) / m
    return m, chi / (len(xs) - 1), chi, chi2_sf(chi, len(xs) - 1)


def beta_census(dy11):
    """{k: number of betas with k mask bits} over ALL betas that occur for the pin.

    beta = ROR(c1 XOR (c1 + DY11), 12). Bit i of x = c1 XOR (c1 + DY11) is DY11_i XOR carry_i; where it is 0 the
    carry stays, where it is 1 the next carry is free. So the words x are the carry sequences, counted here by
    the number of their one bits below bit 31."""
    states = {0: {0: 1}}
    for i in range(32):
        di, nxt = (dy11 >> i) & 1, {}
        for carry, dist in states.items():
            if di == carry:
                targets, add = (carry,), 0
            else:
                targets, add = ((0, 1) if i < 31 else (0,)), (1 if i < 31 else 0)
            for c2 in targets:
                tgt = nxt.setdefault(c2, {})
                for k, n in dist.items():
                    tgt[k + add] = tgt.get(k + add, 0) + n
        states = nxt
    out = {}
    for dist in states.values():
        for k, n in dist.items():
            out[k] = out.get(k, 0) + n
    return out


def beta_cover(rows, dy11):
    """What the list of betas holds, in words, and the share of all d1 whose beta is in the list."""
    census, have = beta_census(dy11), {}
    for _, k, _, _ in rows:
        have[k] = have.get(k, 0) + 1
    if any(have[k] > census.get(k, 0) for k in have):
        raise SystemExit("the list of betas holds more betas of some weight than exist: look at the .total file")
    top = max(have)
    below = [k for k in census if k < top]
    if any(have.get(k, 0) != census[k] for k in below):
        raise SystemExit("the list of betas is not complete below its largest weight")
    n_below = sum(census[k] for k in below)
    share = sum(n * 2.0 ** -k for k, n in have.items())
    if have[top] == census[top]:
        text = (f"The list given to the calculator holds every beta with k at most {top}: {num(len(rows))} betas, the "
                f"smallest k being {min(have)}.")
        short = f"all {num(len(rows))} betas with k at most {top}"
        left = f"all betas with k above {top}"
    else:
        text = (f"The list given to the calculator holds the {num(len(rows))} lightest: all {num(n_below)} betas with k at "
                f"most {top - 1}, the smallest k being {min(have)}, and {num(have[top])} of the {num(census[top])} with "
                f"k = {top}.")
        short = f"the {num(len(rows))} lightest betas"
        left = f"{num(census[top] - have[top])} betas with k = {top} and all betas with k above {top}"
    text += (f" A uniform d1 has a beta of the list with probability {share:.3f}; that is not the share of the class "
             f"rate that the list holds, which is not known.")
    return text, short, left, top


CLASS_TABLE_FILE = f"{PIN_NAME}_classes_table.txt"     # one line per class with a full count over the common list
CLASS_SEARCH_FILE = f"pinclasses_{PIN_NAME}.txt"       # the solver search with the constants fixed: one pair per line
EXTENDED_FILE = "extend_totals.txt"                    # counts over a longer list of betas, one class per line


def read_class_table():
    """([(count, eta, log2 members, betas with a part)] largest first, length of the common list) of every class
    of the pin that has a full count.

    The night's table gives a class over the list its scan file has. Where that is longer than the common list,
    the figures of the common list are taken from the per-beta file of the common length (research/night/main, or
    its snapshot)."""
    raw = []
    for line in (read(frozen(CLASS_TABLE_FILE)) or "").split("\n"):
        m = re.match(r"([0-9a-f]{8}) members 2\^(\d+) betas (\d+) with mass (\d+) total (\d+) ", line)
        if m:
            raw.append((int(m.group(1), 16), int(m.group(2)), int(m.group(3)), int(m.group(4)), int(m.group(5))))
    if not raw:
        return [], 0
    lengths = [r[2] for r in raw]
    common = max(set(lengths), key=lengths.count)
    rows = []
    for eta, lg, betas, mass, total in raw:
        per = read_total(eta, longest=False)
        if betas != common:
            if len(per) != common:
                raise SystemExit(f"class {hx(eta)}: the table has it over {betas} betas, and no per-beta file over the common "
                                 f"{common} betas is here")
            total, mass = int(round(sum(p for *_, p in per if p))), sum(1 for *_, p in per if p)
        elif len(per) == common and abs(sum(p for *_, p in per if p) - total) > 1.0:
            raise SystemExit(f"class {hx(eta)}: the table and its per-beta file disagree")
        rows.append((total, eta, lg, mass))
    return sorted(rows, reverse=True), common


def read_class_search():
    """(pairs, different classes) that the solver search with the constants fixed returned."""
    pairs = [l.split()[:2] for l in (read(frozen(CLASS_SEARCH_FILE)) or "").split("\n") if re.match(r"[0-9a-f]{8} [0-9a-f]{8} \|", l)]
    return len(pairs), len({p[0] for p in pairs})


def read_extended():
    """{eta: (betas, betas with a part, count)} of the counts over a longer list."""
    out = {}
    for m in re.finditer(r"class ([0-9a-f]{8}): (\d+) betas evaluated, (\d+) with mass, exact class rate ([\d.]+)", read(frozen(EXTENDED_FILE)) or ""):
        out[int(m.group(1), 16)] = (int(m.group(2)), int(m.group(3)), float(m.group(4)))
    return out


def sampler_of_class(eta):
    """(betas sampled, sum of the sampler, its error, sum counted for them, smallest and largest deviation) or None."""
    sampler, parts = read_sampler(eta), {b: p for b, _, _, p in read_total(eta) if p}
    for beta, part, _, _ in EXTRA_BETAS.get(eta, []):
        parts[beta] = part
    both = [b for b in sampler if b in parts]
    if not both:
        return None
    zs = [(sampler[b][0] - parts[b]) / sampler[b][1] for b in both]
    each = sorted(((parts[b], sampler[b][0], sampler[b][1], b) for b in both), reverse=True)
    return (len(both), sum(sampler[b][0] for b in both), math.sqrt(sum(sampler[b][1] ** 2 for b in both)),
            sum(parts[b] for b in both), min(zs), max(zs), each)


CLASS_TABLE_ROWS = 10             # classes shown in the table of the proof; the others are summarised in a sentence


def left_out_betas(common):
    """The betas of the largest weight of the common list that the list leaves out (from the longer list of the
    class of the package), or [] if that cannot be told."""
    short, full = read_total(ETA, longest=False), read_total(ETA)
    if len(short) != common or len(full) <= common:
        return [], 0
    top = max(k for _, k, _, _ in short)
    have = {b for b, _, _, _ in short}
    return [b for b, k, _, _ in full if k == top and b not in have], top


def classes_tokens(d, own_total, own_rows):
    """How the class was chosen: the table of the classes counted, the largest of them, and what exists for it."""
    t = {}
    table, common = read_class_table()
    if not table:
        raise SystemExit(f"missing or empty {frozen(CLASS_TABLE_FILE)}")
    order = [r[1] for r in table]
    if ETA not in order:
        raise SystemExit("the class of the package is not in the table of classes")
    n, rank = len(table), order.index(ETA) + 1
    own_common = table[rank - 1][0]
    pairs, found = read_class_search()
    best_count, best_eta, best_log, best_mass = table[0]
    shown = table[:max(CLASS_TABLE_ROWS, rank)]
    rest = table[len(shown):]
    lines = ["| eta | Members | Betas with a part | Count |", "| --- | ---: | ---: | ---: |"]
    for count, eta, lg, mass in shown:
        lines.append(f"| {hx(eta)} | {num(2 ** lg)} | {mass} | {num(count)} |")
    t["class_table"] = "\n".join(lines)
    empty = sum(1 for r in rest if r[0] == 0)
    t["class_table_rest"] = (
        "" if not rest else
        f"The table shows the {word(len(shown))} largest. The other {len(rest)} classes have counts from {num(rest[0][0])} down "
        f"to {num(rest[-1][0])}" + (f"; {word(empty)} of them have no part at all" if empty else "") + ".")
    t["classes_counted"] = word(n)
    t["class_rank"] = ("largest", "second largest", "third largest")[rank - 1] if rank <= 3 else f"number {rank} by size"
    t["class_search_sentence"] = (
        (f"A solver search with the constants held fixed, which asks for a solution with a pair (eta, beta) not seen "
         f"before, returned {pairs} pairs in {found} different classes. " if pairs else "")
        + (f"An exact grid over {num(GRID['classes'])} classes within Hamming distance {GRID['distance']} of the first two, "
           f"restricted to the {num(GRID['betas'])} betas with k at most {GRID['kmax']}, was stopped before it had finished; the "
           f"classes that its partial output showed as strong were counted in full as well. " if GRID else "")
        + "This exploration was closed before the text was finished, so the figures that follow are its final state. ")
    t["class_common"] = num(common)
    t["class_own_common"] = num(own_common)
    # the common list is not even-handed between classes: say so if it can be shown from the files
    left, top = left_out_betas(common)
    closed = [eta for _, eta, _, _ in table if left and all(no_eps(b, eta) for b in left)]
    opened = [(c, eta) for c, eta, _, _ in table if left and all(not no_eps(b, eta) for b in left)]
    if left and ETA in closed and len(closed) + len(opened) == n:
        below = [(c, eta) for c, eta in opened if c < own_common]
        above = [(c, eta) for c, eta in opened if c >= own_common]
        near = max(below) if below else None
        t["class_list_caveat"] = (
            f"The common list is not even-handed between classes. It leaves out {len(left)} betas with k = {top}. For a class "
            f"whose eta has {'odd' if bin(ETA).count('1') % 2 else 'even'} weight, as for the class of this package"
            + (f" and for {hx(best_eta)}" if best_eta != ETA and best_eta in closed else "")
            + f", none of these betas has an eps, so the list is complete for it up to k = {top}; for a class whose eta has "
            f"{'even' if bin(ETA).count('1') % 2 else 'odd'} weight every one of them has an eps, and its count could still "
            f"rise"
            + (f" ({join(hx(eta) for _, eta in sorted(opened, reverse=True) if eta in [r[1] for r in shown])} among the "
               f"classes shown)" if any(eta in [r[1] for r in shown] for _, eta in opened) else "")
            + (f". The nearest of these, {hx(near[1])}, would need {100 * (own_common - near[0]) / near[0]:.0f}% more to pass the "
               f"class used; that was not counted" if near and not above else "")
            + ". The claim does not depend on the rank.")
    else:
        t["class_list_caveat"] = ""
    ext = read_extended()
    if rank == 1:
        t["class_spread_item"] = ""
        t["class_choice_paragraph"] = f"The class of this package has the largest count of the {word(n)}."
        t["class_choice_short"] = f"it has the largest count of the {word(n)} classes counted"
        t["class_choice_claim"] = f"the class used has the largest count of the {n} classes counted"
        t["class_choice_restr"] = f"the class used has the largest count of the {n} classes counted"
    else:
        s = sampler_of_class(best_eta)
        e = ext.get(best_eta)
        best_long = e[2] if e else best_count
        both = sorted((best_long, own_total))
        counted, real, there_short, missing, spread_item = best_class_real(d, best_eta)
        t["class_spread_item"] = spread_item
        text = (f"The class of this package is the {t['class_rank']} of them, with {num(own_common)} over that list. The "
                f"largest, eta = {hx(best_eta)}, a class of {num(2 ** best_log)} members, has {num(best_count)}"
                + (f", and {num(e[2])} over all {num(e[0])} betas with k at most {d_kmax(e[0], d)}" if e and d_kmax(e[0], d) else "")
                + f". It is not used here, and the reason is not its evidence: this text, the run that counts partial E3 "
                f"events and the reviews were made for the class of the package, before the checks of {hx(best_eta)} "
                f"existed. For {hx(best_eta)} there are the count"
                + (f"; the sampler on {word(s[0])} of its betas, with "
                   + join(f"{num(v)} +- {num(se)} against {num(part)} counted ({'beta ' if i == 0 else ''}{b})"
                          for i, (part, v, se, b) in enumerate(s[6]))
                   + f", that is between {z_text(s[4])} and {z_text(s[5])} standard errors" if s else "")
                + (f"; {counted}" if counted else "")
                + (f"; and on real messages {real}" if real else "")
                + ". "
                + (f"It lacks {join(missing)}, which the class of the package has. " if missing else
                   "Every check made for the class of the package exists for it as well. ")
                + (f"So the other class has the larger count and nearly the same checks. " if len(missing) <= 1 else "")
                + other_rule_sentence(best_eta)
                + f"The two counts are "
                f"{math.floor(both[0] / 2 ** LOG2_FACTOR * 100) / 100:.2f} and {math.floor(both[1] / 2 ** LOG2_FACTOR * 100) / 100:.2f} "
                f"times the assumed 2^{LOG2_FACTOR} (rounded down; for the class of the package this is the count of all "
                f"solutions, before rule A); against the next power of two, 2^{LOG2_FACTOR + 1}, they would leave factors of only "
                f"{math.floor(both[0] / 2 ** (LOG2_FACTOR + 1) * 100) / 100:.2f} and "
                f"{math.floor(both[1] / 2 ** (LOG2_FACTOR + 1) * 100) / 100:.2f}.")
        t["class_choice_paragraph"] = text
        t["class_choice_short"] = (
            f"it is the {t['class_rank']} of the {word(n)} classes counted: eta = {hx(best_eta)} has {num(best_count)} "
            f"over the same list" + (f" and {num(e[2])} over {num(e[0])} betas" if e else "")
            + (f", and nearly the same checks ({there_short})" if there_short and len(missing) <= 1 else
               f", and checks of its own ({there_short})" if there_short else "")
            + (f"; it lacks {join(missing)}" if missing else "")
            + ". The class used is kept because this note, the proof, the run on partial E3 events and the reviews were "
              "made for it, and because rule A and the two-stage batch are worked out for it alone; with a batch of one "
              "stage the assumed factor and the claim would be the same for either class")
        same_list = e and len(own_rows) == e[0]
        t["class_choice_claim"] = (
            f"the class used is the {t['class_rank']} of {n} classes of these constants that were counted; the largest, eta "
            f"= {hx(best_eta)}, has {num(e[2]) if same_list else num(best_count)} over "
            + ("the same values of beta" if same_list else f"the {num(common)} lightest values of beta, where the class used has "
               f"{num(own_common)},")
            + (" and nearly the same checks" if len(missing) <= 1 else " and fewer checks")
            + ", but no rule A or two-stage count exists for it")
        t["class_choice_restr"] = (f"by that count the class used is the {t['class_rank']} of {n} classes of these "
                                   f"constants that were counted")
    others = []
    for count, eta, _, _ in table:
        if eta in (ETA, best_eta):
            continue
        s = sampler_of_class(eta)
        if s:
            others.append(f"eta = {hx(eta)} on {word(s[0])} betas ({num(s[1])} with standard error {num(s[2])} against {num(s[3])} "
                          f"counted; single betas between {z_text(s[4])} and {z_text(s[5])} standard errors)")
    t["class_other_samplers"] = ("The sampler was also run for " + join(others) + "." if others else "")
    return t


def d_kmax(n_betas, d):
    """The k up to which a list of n_betas betas is complete, or None if it is not a complete list."""
    census, total = beta_census(d["DY11"]), 0
    for k in sorted(census):
        total += census[k]
        if total == n_betas:
            return k
        if total > n_betas:
            return None
    return None


# ---- scaled-down runs in the layout of the algorithm (research/night/pairstat)
TOYALG = RESEARCH / "night" / "pairstat"


def read_toyalg():
    """{target: [block]} of toyalg_result.txt; a block is one job or one total, with its counts."""
    text = read(TOYALG / "toyalg_result.txt")
    if text is None:
        return None
    out, target, cur = {}, None, None
    for line in text.split("\n"):
        m = re.match(r"=== target L\* = ([\d.]+)", line)
        if m:
            target, cur = m.group(1), None
            out[target] = []
            continue
        m = re.match(r"(?:job (\w), (\d+)-bit words|ALL JOBS WITH (\d+)-BIT WORDS|ALL JOBS POOLED): (\d+) configurations, (\d+) runs", line)
        if m and target:
            cur = dict(job=m.group(1), bits=m.group(2) or m.group(3), pooled=line.startswith("ALL JOBS POOLED"),
                       configs=int(m.group(4)), runs=int(m.group(5)))
            out[target].append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"\s+runs with a collision: (\d+) observed, ([\d.]+) \+- ([\d.]+) predicted \(([-+\d.]+) sd\); fraction ([\d.]+) \+- "
                     r"([\d.]+) against ([\d.]+)", line)
        if m:
            cur.update(hit=int(m.group(1)), hit_pred=float(m.group(2)), hit_sd=float(m.group(3)), hit_z=float(m.group(4)),
                       frac=m.group(5), frac_se=m.group(6), frac_pred=m.group(7))
        m = re.match(r"\s+collisions: (\d+) observed, ([\d.]+) predicted \(([-+\d.]+) Poisson sd", line)
        if m:
            cur.update(coll=int(m.group(1)), coll_pred=float(m.group(2)), coll_z=float(m.group(3)))
        m = re.match(r"\s+dispersion sum \(K-L\)\^2 / sum L: ([\d.]+) \+- ([\d.]+)", line)
        if m:
            cur.update(disp=m.group(1), disp_se=m.group(2))
        m = re.match(r"\s+heterogeneity .*chi-square ([\d.]+) on (\d+) d\.f\., upper-tail probability ([\d.]+)", line)
        if m:
            cur.update(het=m.group(1), het_df=m.group(2), het_p=float(m.group(3)))
        m = re.match(r"\s+pairs of collisions of one run in the same context: (\d+) ", line)
        if m:
            cur.update(same_ctx=int(m.group(1)))
        m = re.match(r"\s+trials with a wrong Y4 or S5: (\d+); hits failing the full-hash check: (\d+)", line)
        if m:
            cur.update(bad=int(m.group(1)), failed=int(m.group(2)))
    return out


def toyalg_tokens(per_run):
    """The runs in the layout of the algorithm at short word sizes: a table, the paragraph after it, short forms."""
    t = {"toyalg_present": "no", "toyalg_table": "", "toyalg_results": "", "toyalg_note": "", "toyalg_claim": "",
         "toyalg_limit": "", "toyalg_bearing": "", "toyalg_intro": "", "toyalg_scope": "", "toyalg_bits": "",
         "toyalg_added_note": ""}
    data = read_toyalg()
    if not data or "0.5" not in data:
        return t
    half = data["0.5"]
    jobs = [b for b in half if b["job"]]
    pooled = [b for b in half if b["pooled"]]
    if len(pooled) != 1 or any("hit" not in b or "coll" not in b for b in jobs + pooled):
        raise SystemExit("toyalg_result.txt: a block is incomplete")
    al = pooled[0]
    if any(b.get("bad") or b.get("failed") for b in jobs + pooled):
        raise SystemExit("toyalg_result.txt reports wrong trials or hits that fail the full hash")
    plan = read(TOYALG / "PLAN_followup.txt") or ""
    added = re.findall(r"^\s+([A-Z])\s+\d+ bits", plan.split("Amendment", 1)[1], re.M) if "Amendment" in plan else []
    added += re.findall(r"job ([A-Z]), the same settings", plan)
    lines = ["| Job | W | Configs | Runs | With collision | Predicted | Coll. | Predicted |",
             "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    for b in jobs:
        lines.append(f"| {b['job']} | {b['bits']} | {b['configs']} | {num(b['runs'])} | {num(b['hit'])} | "
                     f"{b['hit_pred']:,.1f} +- {b['hit_sd']:.1f} | {num(b['coll'])} | {b['coll_pred']:,.1f} |")
    lines.append(f"| all | | {al['configs']} | {num(al['runs'])} | {num(al['hit'])} | {al['hit_pred']:,.1f} +- {al['hit_sd']:.1f} | "
                 f"{num(al['coll'])} | {al['coll_pred']:,.1f} |")
    t["toyalg_table"] = "\n".join(lines)
    out = [b for b in jobs if abs(b["hit_z"]) >= 2.0 or abs(b["coll_z"]) >= 2.0]
    text = (f"In the table, \"configs\" is the number of configurations, \"with collision\" the number of runs with at "
            f"least one collision, followed by its prediction and the standard deviation of the prediction, and \"coll.\" "
            f"the number of collisions. With L = 0.5 a run has a collision with probability 1 - exp(-1/2) = "
            f"{al['frac_pred']} when the trials are "
            f"independent. Over all jobs the observed fraction is {al['frac']} with standard error {al['frac_se']}: "
            f"{num(al['hit'])} of {num(al['runs'])} runs against {al['hit_pred']:,.1f} predicted. The collisions number "
            f"{num(al['coll'])} against {al['coll_pred']:,.1f} predicted. The ratio of the variance of the collisions per run "
            f"to its prediction, 1 for independent trials, is {al['disp']} with standard error {al['disp_se']}."
            + (" No two collisions of a run fell in the same context." if al.get("same_ctx") == 0 else
               f" {al.get('same_ctx')} pairs of collisions of a run fell in the same context.")
            + " No trial had a wrong Y4 or S5, and no collision failed the full re-hash.")
    for b in out:
        text += (f" Job {b['job']} is the one job beyond two standard deviations: {num(b['hit'])} runs with a collision "
                 f"against {b['hit_pred']:,.1f} +- {b['hit_sd']:.1f} ({z_text(b['hit_z'])}), and {num(b['coll'])} collisions against "
                 f"{b['coll_pred']:,.1f} ({z_text(b['coll_z'])})." if len(out) == 1 else
                 f" Job {b['job']} is beyond two standard deviations: {num(b['hit'])} runs with a collision against "
                 f"{b['hit_pred']:,.1f} +- {b['hit_sd']:.1f}, and {num(b['coll'])} collisions against {b['coll_pred']:,.1f}.")
    if not out:
        text += " No job is beyond two standard deviations."
    if added:
        names = sorted(set(added))
        times = re.findall(r"Amendment, (\d\d:\d\d)", plan)
        text += (f" Job{'s' if len(names) != 1 else ''} {join(names)} {'were' if len(names) != 1 else 'was'} added to the plan "
                 f"after earlier jobs had been read, which the plan records"
                 + (f" (amendments of {join(times)})" if len(times) == len(names) else "")
                 + (f"; job {names[-1]} repeats the settings of job {out[0]['job']} with a new seed, as a test fixed after "
                    f"{out[0]['job']} was read" if len(out) == 1 and names[-1] != out[0]["job"] and len(names) > 1 else "")
                 + ". All jobs are in the totals.")
    if added:
        names = sorted(set(added))
        t["toyalg_added_note"] = (f"{word(len(names), True)} of the {word(len(jobs))} jobs {'were' if len(names) != 1 else 'was'} "
                                  f"added after earlier ones had been read, which the plan records. ")
    more = data.get("1.7")
    if more:
        p17 = [b for b in more if b["pooled"]][0]
        odd = [b for b in more if b["job"] and b.get("het_p", 1) < 0.05]
        text += (f" With L = 1.7, {p17['configs']} configurations and {num(p17['runs'])} runs gave {num(p17['hit'])} runs with a "
                 f"collision against {p17['hit_pred']:,.1f} +- {p17['hit_sd']:.1f} predicted, and {num(p17['coll'])} collisions "
                 f"against {p17['coll_pred']:,.1f}."
                 + "".join(f" In job {b['job']} of that series the configurations differ from each other more than chance "
                           f"would often give (chi-square {b['het']} on {b['het_df']} degrees of freedom, probability "
                           f"{b['het_p']:.3f}); its totals agree with the prediction." for b in odd))
    recheck = " ".join((read(REVIEW / "recheck_figures.md") or "").split())
    if ("recounted by me from 22,380 RUN and 390 CFG lines" in recheck
            and "has it written at 03:22:16, unchanged as the first 4,084 characters of today's file" in recheck):
        text += (" A reviewing helper agent recounted every figure of the table and of the series with L = 1.7 from the "
                 "raw lines of the runs and found the same. It also found the plan in the helper's log at 03:22, "
                 "unchanged as the beginning of the plan file.")
    t["toyalg_results"] = text
    bits = sorted({int(b["bits"]) for b in jobs})
    sizes = f"{bits[0]} to {bits[-1]} bits"
    t["toyalg_present"] = "yes"
    t["toyalg_bits"] = sizes
    ranges = read(TOYALG / "toyalg_ranges.txt") or ""
    cls = [int(v) for m in re.finditer(r"class size (\d+) to (\d+)", ranges) for v in m.groups()]
    lg = [float(v) for m in re.finditer(r"log2 trials per run ([\d.]+) to ([\d.]+)", ranges) for v in m.groups()]
    runs_per = sorted({b["runs"] // b["configs"] for b in jobs if b["runs"] % b["configs"] == 0})
    t["toyalg_intro"] = (
        "**Scaled-down runs in the layout of the algorithm (participant computation by a helper agent, other "
        "constants).** The runs of the class search above hold other words fixed than a run of 6.4 does, and every one of them had many "
        "collisions. A second set of runs, made in the night before this text, has neither gap. The toy hash is the one "
        f"described above, with W = {join(str(b) for b in bits)}"
        + ("; for W = 9 the rotations are (4, 3, 2, 1)" if 9 in bits else "")
        + ". A run is laid out as in 6.4: its four seed words X2, X5, X6 and X9 are drawn at random, X1 = X10 = 0, the "
        "contexts (X12, X13, X14) are taken in a fixed order, and for every context all 2^W values of alpha and all "
        "members of the class are tried. For every constant set the class with the largest rate per member among the "
        "classes with at least four members is used, with rates computed by brute force as above. A configuration is a "
        "constant set with that class and a number of contexts per run, chosen so that M predicts L collisions per run: "
        f"L = 0.5, the value at which H1 gives its bound, or L = 1.7, close to the {per_run:.2f} that the count of this "
        "package gives per run. The constant sets are drawn at random. "
        + ("Jobs B, C, F and G keep only the sets whose best class has a rate per member above a threshold; every job "
           "skips a configuration that would need more trials per run than a limit; the 10-bit sets of job D are the "
           "three with the largest class rate in an earlier scan of 24 random sets. These rules were fixed beforehand "
           "and use exact rates only, never outcomes. "
           if all(x in plan for x in ("rate >= 8", "rate >= 11.3", "rate >= 4", "uses exact rates only, never outcomes")) else
           "Some jobs keep only sets whose best class has a rate above a threshold fixed beforehand; the 10-bit sets are "
           "the three with the largest class rate in an earlier scan of 24 random sets. ")
        + (f"A configuration has {runs_per[0]} to {runs_per[-1]} runs. " if runs_per else "")
        + "Every collision is confirmed by hashing both messages in full. The jobs, the number of runs per "
        "configuration and the statistics were fixed in a written plan shortly before the first counted run"
        + (" (the plan is of about 03:25 by its own heading; the counted runs started at 03:26)"
           if "about 03:25" in plan and "counted runs started at 03:26" in plan else "")
        + ". The number of configurations of a job was not fixed: a job stops at a time limit, tested between constant "
        "sets. Results for L = 0.5:")
    t["toyalg_scope"] = (
        "These runs test directly, at the depth of actual collisions and in the layout of 6.4, whether a run contains a "
        f"collision as often as independent trials give. The text of submission {SUBMISSIONS[-1][0]} named that test as "
        f"missing. They make it for words of {sizes}"
        + (f", for classes of {min(cls)} to {max(cls)} members" if cls else "")
        + (f", for runs of 2^{min(lg):.1f} to 2^{max(lg):.1f} trials" if lg else "")
        + " and for other constants. They are not evidence about 32-bit words, where a run has 2^" + str(127 - LOG2_FACTOR)
        + " trials, or about the constants of this package, whose count rests on few paths.")
    t["toyalg_note"] = (
        f"{num(al['runs'])} runs at an expected 0.5 collisions per run: {num(al['hit'])} with a collision against "
        f"{al['hit_pred']:,.1f} +- {al['hit_sd']:.1f} predicted, "
        f"{num(al['coll'])} collisions against {al['coll_pred']:,.1f}, and no two collisions of a run in the same context"
        + (f"; {num(p17['runs'])} runs at 1.7 per run: {num(p17['hit'])} against {p17['hit_pred']:,.1f}" if more else "")
        + "".join(f"; one job of the {word(len(jobs))} is {abs(b['hit_z']):.1f} standard deviations low ({num(b['hit'])} against "
                  f"{b['hit_pred']:,.1f})" for b in out[:1] if b["hit_z"] < 0))
    t["toyalg_claim"] = (
        f"And from scaled-down runs in the algorithm's own layout (four seed words per run, contexts in order, all alphas, "
        f"all members; words of {sizes}, other constants), which test whether a run has at least one collision as often "
        f"as independent trials give: " + t["toyalg_note"] + ".")
    t["toyalg_limit"] = (f"The scaled-down runs in the layout of the algorithm count the runs with at least one collision, "
                         f"but for words of {sizes} and with other constants.")
    t["toyalg_bearing"] = (
        f"the scaled-down runs in the layout of the algorithm reported below count collisions per run, at word sizes of "
        f"{sizes} and with other constants: {num(al['hit'])} of {num(al['runs'])} runs had a collision where independent "
        f"trials predict {al['hit_pred']:,.1f}")
    return t


# ---- the deep run on real messages for the E1 outcomes that the count rests on
E1DEEP_EXPECTED = "e1deep_expected.txt"
E1DEEP_RUNS = ("e1deep_real.txt", "e3deep_real.txt")      # real runs that count the listed E1 outcomes, in order
E3DEEP_EXPECTED, E3DEEP_EVENTS = "e3deep_expected.txt", f"e3p_expected_{ETA:08x}.txt"
E3DEEP_REAL, E3DEEP_MODEL = "e3deep_real.txt", "e3deep_model.txt"
E3PARTIAL_CHECK = EVID / "e3partial_bf8.txt"              # written by tools/e3partial_check.sh


def listed_exact(betas, counts):
    """The probability per trial of the listed E1 outcomes, from the integer counts of the recount: the sum of N1
    over the outcomes with a nonzero product of the listed betas, divided by 2^96. None if the recount does not
    hold exactly these outcomes."""
    total = 0.0
    for beta, n in zip(betas, counts):
        rows = read_outcomes(beta)
        if len(rows) != n:
            return None
        total += sum(r[2] for r in rows)
    return total / 2.0 ** 96


def e1deep_tokens():
    """The runs on real messages that count the E1 outcomes the count rests on: every run that is on file."""
    t = {"e1deep_paragraph": "", "e1deep_note": "", "e1deep_claim": "", "e1deep_state": "absent", "e1deep_runs": "0",
         "e1deep_beta_note": "", "e1deep_beta_claim": "", "e1deep_high_claim": ""}
    exp = read(NIGHT / E1DEEP_EXPECTED)
    if exp is None or f"class eta {hx(ETA)}" not in exp:
        return t
    weights = dict(re.findall(r"beta ([0-9a-f]{8}): weight (\d+), listed outcomes \d+", exp))
    betas = re.findall(r"beta ([0-9a-f]{8}): weight \d+, listed outcomes (\d+)", exp)
    per = re.search(r"per trial: P\(listed beta\) 2\^(-[\d.]+); P\(listed E1 outcome\) 2\^(-[\d.]+)", exp)
    if not betas or not per:
        return t
    listed = sum(int(n) for _, n in betas)
    # the probability that the beta of a trial is a listed one is exact: the sum of 2^-k over the listed betas
    p_beta, p_file = sum(2.0 ** -int(k) for k in weights.values()), 2.0 ** float(per.group(2))
    if abs(math.log2(p_beta) - float(per.group(1))) > 0.0002:
        raise SystemExit("e1deep_expected.txt: the weights of the listed betas and its probability of a listed beta disagree")
    p_exact = listed_exact([b for b, _ in betas], [int(n) for _, n in betas])
    p_out = p_exact if p_exact else p_file
    lead = (f"A further measurement goes deeper on the E1 side. It counts, among real trials of 6.1 with independent "
            f"contexts, those whose E1 outcome (beta, tau, eps) is one of the {listed} outcomes with a nonzero product of "
            f"the {word(len(betas))} heaviest betas of the table. The calculator's P1 gives these a probability of "
            f"2^{math.log2(p_out):.2f} per trial.")
    runs = []                                      # (log2 trials, outcomes seen, expected, betas seen, expected)
    file_exp = None
    for name in E1DEEP_RUNS:
        real = read(NIGHT / name) or ""
        if f"eta {hx(ETA)}" not in real:
            continue
        m = re.search(r"STAT real E1 deep: trials with a listed beta (\d+) \(2\^(-?[\d.]+)\)\s+trials with a listed E1 outcome (\d+)", real)
        mt = re.search(r"STAT real trials 2\^([\d.]+)\s+bad (\d+)", real)
        if not (m and mt):
            continue
        lg = round(float(mt.group(1)))
        ex = re.search(rf"expected in 2\^{lg} trials: listed beta (\d+), listed outcome ([\d.]+)", exp)
        file_exp = float(ex.group(2)) if ex else file_exp
        runs.append((lg, int(m.group(3)), p_out * 2.0 ** lg, int(m.group(1)), p_beta * 2.0 ** lg))
    t["e1deep_runs"] = str(len(runs))
    if not runs:
        t["e1deep_paragraph"] = lead + " No such run had finished when this text was written; no result is used."
        t["e1deep_note"] = ("a run that counts real trials with the E1 outcomes that carry most of the count, at a "
                            f"probability of 2^{math.log2(p_out):.2f} per trial, was under way when this text was written")
        t["e1deep_claim"] = ("a run that counts real trials with the outcomes of the first call that carry most of the "
                             "count was under way when this text was written")
        t["e1deep_state"] = "running"
        return t
    z = lambda seen, expected: (seen - expected) / math.sqrt(expected)
    zb = lambda seen, expected: (seen - expected) / math.sqrt(expected * (1 - p_beta))
    seen_all, exp_all = sum(r[1] for r in runs), sum(r[2] for r in runs)
    beta_all, bexp_all = sum(r[3] for r in runs), sum(r[4] for r in runs)
    total_lg = math.log2(sum(2.0 ** r[0] for r in runs))
    total_txt = f"2^{total_lg:.0f}" if abs(total_lg - round(total_lg)) < 1e-9 else f"{len(runs)} * 2^{runs[0][0]}"
    n = len(runs)
    same = len({r[0] for r in runs}) == 1
    source = (f" (from the counts N1 of the recount; the expectation file written before the runs has {file_exp:.2f}, from "
              f"logarithms kept to two decimals)" if p_exact and file_exp and abs(file_exp - runs[0][2]) >= 0.005 else "")
    zbeta = zb(beta_all, bexp_all)
    ppm = abs(beta_all - bexp_all) / bexp_all * 1e6
    if n == 1:
        lg, seen, expected, sb, eb = runs[0]
        body = (f" In 2^{lg} real trials {expected:.2f} such trials are expected{source} and {seen} were seen, "
                f"{z_text(z(seen, expected))} standard deviations of a Poisson count. The beta of a trial was one of the "
                f"{word(len(betas))} in {num(sb)} trials against {num(eb)} expected, {z_text(zb(sb, eb))} standard deviations.")
        short = (f"a run of 2^{lg} real trials found {seen} trials with one of the {listed} {{what}} that carry most of the "
                 f"count, where {{who}} predicts {expected:.2f}")
    else:
        body = (f" {word(n, True)} runs of 2^{runs[0][0]} real trials each, with different random words, " if same else
                f" {word(n, True)} runs with different random words ")
        body += (f"are on file. In each {runs[0][2]:.2f} such trials are expected{source}; " if same else "are on file; ")
        body += ("they found " + join(str(r[1]) for r in runs) + ", that is "
                 + join(z_text(z(r[1], r[2])) for r in runs) + " standard deviations of a Poisson count. Together that is "
                 f"{seen_all} in {total_txt} trials against {exp_all:.2f} expected, {z_text(z(seen_all, exp_all))} standard "
                 f"deviations. The beta of a trial was one of the {word(len(betas))} in " + join(num(r[3]) for r in runs)
                 + f" trials against {num(runs[0][4])} expected per run, " + join(z_text(zb(r[3], r[4])) for r in runs)
                 + f" standard deviations, and together {z_text(zbeta)}"
                 + (f": a shortfall of about {ppm:.0f} in a million that is not explained." if zbeta <= -2.0 else
                    f": an excess of about {ppm:.0f} in a million that is not explained." if zbeta >= 2.0 else "."))
        short = (f"{word(n)} runs of 2^{runs[0][0]} real trials found " + join(str(r[1]) for r in runs)
                 + f" trials with one of the {listed} {{what}} that carry most of the count, together {seen_all} where "
                 f"{{who}} predicts {exp_all:.2f} ({z_text(z(seen_all, exp_all))} standard deviations; the "
                 + ("second" if n == 2 else "last") + f" run alone {z_text(z(runs[-1][1], runs[-1][2]))})")
        if abs(zbeta) >= 2.0:
            side = "rarely" if zbeta < 0 else "often"
            t["e1deep_beta_note"] = (
                f"In both runs the trials whose beta is one of the {word(len(betas))} heaviest are slightly too few: "
                + join(z_text(zb(r[3], r[4])) for r in runs) + f" standard deviations, together {z_text(zbeta)}, about {ppm:.0f} "
                f"in a million. I have not explained it." if zbeta < 0 and n == 2 else
                f"The trials whose beta is one of the {word(len(betas))} heaviest occur about {ppm:.0f} in a million too "
                f"{side} ({z_text(zbeta)} standard deviations over the runs), which I have not explained.")
            t["e1deep_beta_claim"] = (
                f"In these runs the values of beta that carry most of the count occurred about {ppm:.0f} in a million too "
                f"{side} ({z_text(zbeta)} standard deviations over {total_txt} trials), which is not explained.")
        high = [r for r in runs if abs(z(r[1], r[2])) >= 2.0]
        if high:
            t["e1deep_high_claim"] = (
                f"Of the {word(n)} counts of first-call outcomes on real messages one is "
                f"{abs(z(high[0][1], high[0][2])):.1f} standard deviations {'above' if z(high[0][1], high[0][2]) > 0 else 'below'} "
                f"its prediction (together {z_text(z(seen_all, exp_all))}).")
    mdl = read(NIGHT / E3DEEP_MODEL) or ""
    mm = re.search(r"STAT model E1 deep: trials with a listed beta (\d+) \(2\^(-?[\d.]+)\)\s+trials with a listed E1 outcome (\d+)", mdl)
    mmt = re.search(r"STAT model trials 2\^([\d.]+)", mdl)
    if mm and mmt and f"eta {hx(ETA)}" in mdl:
        mlg = round(float(mmt.group(1)))
        body += (f" The same counter on 2^{mlg} draws from M found {mm.group(3)} listed outcomes where "
                 f"{p_out * 2.0 ** mlg:.2f} are expected, and a beta of the list in {num(int(mm.group(1)))} draws against "
                 f"{num(p_beta * 2.0 ** mlg)} expected: a check of the counter and of the expectation, not of real "
                 f"messages.")
    t["e1deep_paragraph"] = (lead + body + " This tests the E1 probabilities of the count on real messages at that depth. "
                             "It does not test the two sides together.")
    t["e1deep_note"] = short.format(what="E1 outcomes", who="the calculator")
    t["e1deep_claim"] = short.format(what="outcomes of the first call", who="the counting program")
    t["e1deep_state"] = "done"
    return t


def e3deep_tokens(second):
    """The run on real messages that counts partial E3 events of the outcomes the count rests on.

    second: True when that run is the second of two runs that count E1 outcomes (it is then called so)."""
    t = {"e3deep_paragraph": "", "e3deep_note": "", "e3deep_claim": "", "e3deep_state": "absent", "e3deep_depth": "",
         "e3deep_total": ""}
    exp = read(NIGHT / E3DEEP_EXPECTED) or ""
    m = re.search(r"events (\d+), probability per trial 2\^(-[\d.]+)", exp)
    events = [float(v) for v in re.findall(r"^E3P [0-9a-f]{8} [0-9a-f]{8} (-[\d.]+)$", read(NIGHT / E3DEEP_EVENTS) or "", re.M)
              if float(v) > -900]
    real = read(NIGHT / E3DEEP_REAL) or ""
    seen = re.search(r"STAT real E3 deep: trials with a listed partial E3 event (\d+)", real)
    mt = re.search(r"STAT real trials 2\^([\d.]+)\s+bad (\d+)", real)
    if not (m and seen and mt and f"eta {hx(ETA)}" in real):
        return t
    n_events, lp = int(m.group(1)), float(m.group(2))
    if events and len(events) != n_events:
        raise SystemExit("the list of partial E3 events and the expectation file disagree on their number")
    lg = round(float(mt.group(1)))
    ex = re.search(rf"in 2\^{lg}: ([\d.]+)", exp)
    expected = float(ex.group(1)) if ex else 2.0 ** (lg + lp)
    got = int(seen.group(1))
    z = (got - expected) / math.sqrt(expected)
    chk = read(E3PARTIAL_CHECK) or ""
    mc = re.search(r"partial E3 count against brute force at 8-bit words: (\d+) cases, outcomes with solutions (\d+) equal, (\d+) "
                   r"different; zero outcomes sampled (\d+) agree, (\d+) disagree", chk)
    checked = ("" if not mc else
               f" At 8-bit words that program was compared with brute force on {mc.group(1)} cases: {num(int(mc.group(2)))} "
               f"outcomes with solutions, "
               + ("all equal" if mc.group(3) == "0" else f"{mc.group(3)} of them different")
               + f", and {num(int(mc.group(4)))} sampled outcomes without solutions, "
               + ("all empty in the program as well." if mc.group(5) == "0" else f"{mc.group(5)} of them not empty in the program."))
    depth = (f"between 2^{min(events):.1f} and 2^{max(events):.1f} each" if events else "")
    t["e3deep_depth"] = (f"2^{max(events):.0f} to 2^{min(events):.0f}" if events else f"2^{lp:.1f} in all")
    t["e3deep_total"] = f"2^{lp:.2f}"
    model = read(NIGHT / E3DEEP_MODEL) or ""
    mm = re.search(r"STAT model E3 deep: trials with a listed partial E3 event (\d+)", model)
    mmt = re.search(r"STAT model trials 2\^([\d.]+)", model)
    model_txt, model_short = "", ""
    if mm and mmt and f"eta {hx(ETA)}" in model:
        mlg = round(float(mmt.group(1)))
        mexp = 2.0 ** (mlg + lp)
        model_txt = (f" The same counter on 2^{mlg} draws from M found {mm.group(1)}, where {mexp:.1f} are expected "
                     f"({z_text((int(mm.group(1)) - mexp) / math.sqrt(mexp))} standard deviations): a check of the counter "
                     f"and of the expectation, not of real messages.")
        model_short = f"; the same counter on 2^{mlg} draws from the model found {mm.group(1)} against {mexp:.1f}"
    t["e3deep_paragraph"] = (
        ("The second of these runs" if second else "A run of the same kind")
        + f" also counts an event on the E3 side. For an outcome (tau, eps), the E3 count of step "
        f"3 puts three conditions on the inputs of E3: the XOR difference of its first-half b value is psi = tau XOR "
        f"ROR(tau, 1), that of its a output is eps, and that of its c output is tau. A partial E3 event is the first two "
        f"of the three, for one of the {n_events} pairs (psi, eps) that belong to the listed outcomes of the "
        f"heaviest betas above. Both differences can be read off the outputs of E3. The third condition is left out, "
        f"because with it the event is too rare to be counted. The probability of a partial event under M comes from a "
        f"program derived from the E3 count: the same enumeration and automata, without the list for the third "
        f"condition.{checked} The {n_events} events have a probability of 2^{lp:.2f} per trial together"
        + (f", {depth}" if depth else "")
        + f". In 2^{lg} real trials {expected:.1f} are expected and {num(got)} were seen, {z_text(z)} standard deviations of "
        f"a Poisson count.{model_txt} So the E3 side is now tested on real messages as well, at these depths, but "
        f"without its third condition. Nothing tests the full E3 count on real messages, and nothing tests E1 and E3 "
        f"together.")
    t["e3deep_note"] = (
        ("the second of these runs also" if second else "a run of the same kind")
        + f" found {num(got)} trials with one of {n_events} partial E3 events, two of the three conditions "
        f"that the E3 count puts on an outcome, where a program derived from that count predicts {expected:.1f}" + model_short)
    t["e3deep_claim"] = (
        f"one of these runs found {num(got)} trials with one of {n_events} partial events of the second call (two of the "
        f"three conditions that its count puts on an outcome) against {expected:.1f} predicted")
    t["e3deep_state"] = "done"
    return t


def best_class_real(d, eta):
    """What exists for another class of the pin beside its count and sampler: (checks of its counts against
    independent counters, runs on real messages, a short form, what it lacks against the class of the package,
    a sentence on its layout runs for the paragraph on the spread or '')."""
    cfg = CLASSES.get(eta)
    if not cfg:
        return "", "", "", ["every other check"], ""
    st = read_stats(NIGHT / cfg["real"], eta)
    deep = read_stats(NIGHT / cfg["deep"], eta)
    layout = read_layout(NIGHT / cfg["layout"])
    amc = (NIGHT / cfg["e1amc"]).exists() and read_e1amc(NIGHT / cfg["e1amc"])
    e3 = (NIGHT / cfg["e3check"]).exists() and read_e3check(NIGHT / cfg["e3check"])
    e1d = read(NIGHT / f"e1deep_real_{eta:08x}.txt") or ""
    e1x = read(NIGHT / f"e1deep_expected_{eta:08x}.txt") or ""
    e1d_m = re.search(r"STAT real E1 deep: trials with a listed beta (\d+) \(2\^(-?[\d.]+)\)\s+trials with a listed E1 outcome (\d+)", e1d)
    e1d_t = re.search(r"STAT real trials 2\^([\d.]+)", e1d)
    counted, real, short, missing, spread_item = [], [], [], [], ""
    if amc:
        counted.append(f"its E1 count against ApproxMC for beta {amc['beta']} ({amc['compared']} outcomes, largest difference "
                       f"{amc['largest']} bits)")
        short.append("ApproxMC on the E1 count")
    else:
        missing.append("the comparison of its E1 count with ApproxMC")
    if e3:
        top, rest_g, zeros = e3["top"], e3["rest"], e3["zeros"]
        counted.append(f"its E3 count against a SAT solver and ApproxMC (ratio of sums {top[2]:.3f} for the {top[0]} largest "
                       f"counts" + (f", {rest_g[2]:.3f} for {rest_g[0]} others" if rest_g else "")
                       + (f"; {zeros[0]} zero counts tested, none with a solution" if zeros[1] == zeros[0] else "") + ")")
        short.append("a SAT solver and ApproxMC on the E3 count")
    else:
        missing.append("the comparison of its E3 count with ApproxMC")
    host = st["check"] and re.match(r"CHECK (\d+) of (\d+)", st["check"])
    if host:
        real.append(f"the host check of the trial ({num(int(host.group(1)))} of {num(int(host.group(2)))} trials)")
    for s, label in ((st, "a comparison"), (deep, "a second comparison")):
        if s["real"] is not None and s["model"] is not None:
            r, m = s["real"], s["model"]
            az = deviations(r, m)[0][0]
            real.append(f"{label} of 2^{round(r['trials'][1])} real trials with M (early test passes {num(r['early'][1])} "
                        f"against {num(m['early'][1])}, trials in which E1 requires the class {num(r['eta'][1])} against "
                        f"{num(m['eta'][1])}, largest deviation {az:.1f} standard deviations)")
            short.append(f"2^{round(r['trials'][1])} real trials against the model")
    if st["real"] is None:
        missing.append("a comparison with real messages")
    if layout and len(layout) >= 4:
        passes = [p for _, p, _, _ in layout]
        _, ratio, chi, p_chi = spread(passes)
        own = read_layout(night("layout"))
        same_seeds = LAYOUT_SEEDS_FROM_RUN and [r for r, *_ in layout] == [r for r, *_ in own]
        real.append(f"{word(len(layout))} runs in the layout of the algorithm"
                    + (", with the same sets of seed words as the runs of the class of this package," if same_seeds else "")
                    + " with " + join(num(p) for p in passes) + f" early-test passes (ratio of their variance to their mean "
                    f"{ratio:.2f}, chi-square {chi:.1f} on {len(layout) - 1} degrees of freedom, "
                    + ("no excess)" if p_chi >= 0.05 else f"probability {prob(p_chi)})"))
        short.append(f"{word(len(layout))} layout runs with variance over mean {ratio:.2f}")
        if same_seeds and own and len(own) >= 4 and p_chi >= 0.05 and len(layout) == len(own):
            op = [p for _, p, _, _ in own]

            def away(xs, j):
                others = [x for i, x in enumerate(xs) if i != j]
                mo = sum(others) / len(others)
                return (xs[j] - mo) / math.sqrt(mo * (1 + 1 / len(others)))

            j = max(range(len(op)), key=lambda i: abs(away(op, i)))
            spread_item = (
                f"{word(len(layout))} runs of the class eta = {hx(eta)} of the same constants, made with the same "
                f"{word(len(layout))} sets of seed words, show no excess: the ratio of the variance of their pass counts to "
                f"their mean is {ratio:.2f} (chi-square {chi:.1f} on {len(layout) - 1} degrees of freedom), and the run with "
                f"the seed words of run {own[j][0]} is {abs(away(passes, j)):.1f} standard deviations "
                f"{'above' if away(passes, j) > 0 else 'below'} the mean of the others there. So those seed words do not give "
                f"a high pass count for every class")
    pb = re.search(r"per trial: P\(listed beta\) 2\^(-[\d.]+)", e1x)
    if e1d_m and e1d_t:
        lg = round(float(e1d_t.group(1)))
        ex = re.search(rf"expected in 2\^{lg} trials: listed beta (\d+), listed outcome ([\d.]+)", e1x)
        if ex:
            seen, expected, sb, eb = int(e1d_m.group(3)), float(ex.group(2)), int(e1d_m.group(1)), int(ex.group(1))
            zb = (sb - eb) / math.sqrt(eb * (1 - (2.0 ** float(pb.group(1)) if pb else 0.0)))
            real.append(f"a run of 2^{lg} real trials that counts its heavy E1 outcomes ({seen} seen where the expectation "
                        f"file of that run has {expected:.2f}, {z_text((seen - expected) / math.sqrt(expected))} standard "
                        f"deviations; trials with one of its listed betas {z_text(zb)})")
            short.append(f"{seen} listed E1 outcomes against {expected:.2f} in 2^{lg} real trials")
        else:
            missing.append("a run that counts its E1 outcomes on real messages")
    else:
        missing.append("a run that counts its E1 outcomes on real messages")
    if not (NIGHT / f"e3deep_real_{eta:08x}.txt").exists():
        missing.append("a run that counts partial E3 events on real messages")
    return join(counted) if counted else "", join(real) if real else "", join(short) if short else "", missing, spread_item


LAYOUT_SEEDS_FROM_RUN = True      # r2_class_gpu.cu: the four seed words of a layout run are derived from its run number



# ---- a solution of the seven-word system inside the class, and the outcomes of the heaviest beta
def class_solution_paragraph(d, info):
    """The solution of CLASS_SOLUTION for the class of the package, checked here with the G function alone."""
    sol = CLASS_SOLUTION.get(ETA)
    solver_eta = info["eta"] if info else None
    other = ("" if not info or int(solver_eta, 16) == ETA else
             f" The solution that the solver search returned with the constants has eta = {solver_eta} and so lies in another "
             f"class.")
    if not sol:
        return ("No solution of the seven-word system with Y4 in the class of this package is printed here." + other), None
    y1, y6, y12, w12, w5, y4, y9, y14, w8 = (sol[k] for k in ("Y1", "Y6", "Y12", "w12", "w5", "Y4", "Y9", "Y14", "w8"))
    pa = g_steps(y1, y6, d["Y11"], y12, w12, w5)
    pb = g_steps(y1, y6, d["Y11B"], y12, w12, (w5 + d["delta"]) & M32)
    qa = g_steps(d["Y3"], y4, y9, y14, 0, w8)
    qb = g_steps(d["Y3B"], y4, y9, y14, 0, w8)
    residual = (pa["a2"] ^ qa["c2"] ^ pb["a2"] ^ qb["c2"], qa["a2"] ^ pa["c2"] ^ qb["a2"] ^ pb["c2"],
                qa["b2"] ^ pa["d2"] ^ qb["b2"] ^ pb["d2"], pa["b2"] ^ qa["d2"] ^ pb["b2"] ^ qb["d2"])
    if any(residual):
        raise SystemExit("CLASS_SOLUTION does not give a zero residual in 6.2")
    if ((d["Y3"] + y4) & d["qmask"]) != d["qvalue"] or (qa["d1"] ^ qb["d1"]) != ETA:
        raise SystemExit("CLASS_SOLUTION is not in the class of the package")
    beta, tau, eps = pa["b1"] ^ pb["b1"], pa["a2"] ^ pb["a2"], pa["c2"] ^ pb["c2"]
    text = (f"A complete solution of the seven-word system with Y4 in the class, which can be checked by hand from 6.2: "
            f"Y1 = {hx(y1)}, Y6 = {hx(y6)}, Y12 = {hx(y12)}, w12 = {hx(w12)}, w5 = {hx(w5)}, Y4 = {hx(y4)}, Y9 = {hx(y9)}, "
            f"Y14 = {hx(y14)}, w15 = 0, w8 = {hx(w8)}. For these values the four residual words of 6.2 are zero. E1 has "
            f"beta = {hx(beta)}, and the XOR differences of its a and c outputs are tau = {hx(tau)} and eps = {hx(eps)}: one "
            f"of the outcomes of the table above. The solution was found by a reviewing helper agent with a short search "
            f"of its own and was evaluated again for this text with the G function alone. It shows that the constants and "
            f"the class do not exclude R = 0; it does not show that a message reaches such values." + other)
    return text, (hx(beta), hx(tau), hx(eps))


def odd_power(v):
    """(text, relative difference) of a positive float as an odd number times a power of two, if a small odd fits."""
    m, e = math.frexp(v)                           # v = m * 2^e, 0.5 <= m < 1
    for bits in range(1, 21):
        odd = round(m * 2 ** bits)
        if odd % 2 == 1 and abs(odd / 2 ** bits - m) < 1e-11:
            j = e - bits
            return (f"2^{j}" if odd == 1 else f"{odd} * 2^{j}"), abs(odd * 2.0 ** j - v) / v, odd * 2.0 ** j
    return f"{v:.6e}", 0.0, v


def read_outcomes(beta):
    """[(tau, eps, E1, N3)] of a beta from the recount of this class: the outcomes with a nonzero product."""
    out = []
    for m in re.finditer(r"^OUTX ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) E1 (\d+) N3 (\d+)$",
                         read(EVID / f"pairs_recount_{ETA:08x}.txt") or "", re.M):
        if int(m.group(1), 16) == ETA and m.group(2) == beta:
            out.append((m.group(3), m.group(4), float(m.group(5)), float(m.group(6))))
    return out


def outcome_tokens(d, beta, part, k, solution):
    """The table of the outcomes of one beta: tau, eps, the two counts and what the outcome adds to the count."""
    t = {"outcome_table": "", "outcome_paragraph": ""}
    rows = read_outcomes(beta)
    if not rows:
        t["outcome_paragraph"] = ("The single outcomes of the heaviest beta were not written out for this class; the package "
                                  "does not hold them.")
        return t
    lines = ["| tau | eps | N1 | N3 | Adds |", "| --- | --- | ---: | ---: | ---: |"]
    total, worst, body = 0.0, 0.0, []
    for tau, eps, e1, n3 in rows:
        s1, r1, v1 = odd_power(e1)
        s3, r3, v3 = odd_power(n3)
        adds = v1 * v3 / 2.0 ** (96 - d["fixed"])
        total, worst = total + adds, max(worst, r1, r3)
        body.append((adds, f"| {tau} | {eps} | {s1} | {s3} | {num(adds)} |"))
    if abs(total - part) > 0.5 + 1e-9 * part:
        raise SystemExit(f"the outcomes of beta {beta} add up to {total}, not to its part {part}")
    lines += [l for _, l in sorted(body, reverse=True)]
    lines.append(f"| sum | | | | {num(total)} |")
    t["outcome_table"] = "\n".join(lines)
    hit = (f" The solution printed below has the outcome tau = {solution[1]}, eps = {solution[2]} of this table."
           if solution and solution[0] == beta and any(r[0] == solution[1] and r[1] == solution[2] for r in rows) else "")
    t["outcome_paragraph"] = (
        f"The table lists the {len(rows)} outcomes with a nonzero product of the heaviest beta, {beta} (k = {k}). N1 is "
        f"the number of triples (c1, b1, a2), with c1 XOR (c1 + DY11) = ROL(beta, 12), for which E1 produces tau and eps; "
        f"it is P1 times 2^{96 - k}. N3 is the number of quadruples (Y4, h1, Y9, w8) of step 3. \"Adds\" is N1 * N3 / "
        f"2^{96 - d['fixed']}, what the outcome adds to the class-rate part of the beta: 2^({d['fixed']} - k) * P1 * N3. "
        f"Both counts can be recomputed with a model counter from the definitions of 6.2 and of steps 2 to 4, without "
        f"the calculator. The calculator computes in floating point; a value shown as an odd number times a power of "
        f"two differs from the computed one by a relative error below "
        f"{'10^-12' if worst < 1e-12 else '10^-9' if worst < 1e-9 else f'{worst:.1e}'}." + hit)
    return t


# ---- the log of the local validation (validate_pkg5.sh writes it)
VALIDATION_LOG = EVID / "validation_log.txt"


def read_validation():
    """What the last local validation showed, if it was made on the files as they are now; else None.

    The log lists the candidate files with their SHA-256; proof.md, claim.json, the manifest and the program must
    have these hashes now, or the log belongs to another state of the package."""
    text = read(VALIDATION_LOG)
    if text is None:
        return None
    import hashlib
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
    if any(a != b or ident != "True" for _, a, b, ident, _, _ in exps):
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


# ---- what the reviewing helper agents computed: quoted from their reports, which must still hold these words
REVIEW = RESEARCH / DRAFT_BEFORE / "review"      # the reports are on the earlier version of this package
REVIEW_QUOTES = (
    ("evidence.md", "60 random constant sets, 1,019 classes (459 with solutions"),
    ("evidence.md", "17,258 (class, beta) pairs, 874 with solutions, 694,652,928 solutions: no pair differs"),
    ("evidence.md", "8,632 no-eps pairs all empty"),
    ("evidence.md", "chi2 12.6/16, 10.6/10, 8.3/10, 16.7/12; sum of P1*N3 = 0.980, 0.990, 1.005, 1.012 of the calculator's"),
    ("evidence.md", "60 cases: 85,908 outcomes with solutions all equal, 60,448 sampled zero outcomes all zero"),
    ("evidence.md", "chi2 29.1 on 10"),
    ("evidence.md", "the other betas fit (9.8/12, 3.3/6, 11.1/10)"),
    ("evidence.md", "1,501,693 against 1,451,568"),
    ("judge.md", "2^39 draws, beta 481c6852): 587 hits on the 16 positive outcomes against 628.2"),
    ("judge.md", "50.06 +-"),
    ("judge.md", "The calculator gives the same list for delta = +2"),
    ("math_cost.md", "10 random cases, half with delta = -2, 182 classes"),
    ("math_cost.md", "all 125 (class, beta) pairs with solutions equal to 3.6e-16, all 46,467 pairs without solutions zero"),
    ("math_cost.md", "E1 probabilities of all 16 outcomes within 0.14 bits of the calculator"),
    ("math_cost.md", "E3 counts of the six largest outcomes 2^50.05, 47.88, 50.01, 47.92, 46.89, 45.08 against 2^50, 48, 50, 48, 47, 45"),
    ("math_cost.md", "**12.20 million +- 0.44 million** against 12.58 million"),
    ("math_cost.md", "with delta = +2 or 2^31 + 2 the calculator returns the same 14,038,016 and 3,956,736"),
    ("judge.md", "0.06, 48.14 +- 0.12, 49.95 +- 0.09, 48.04 +- 0.18 against the calculator's 50.00, 48.00, 50.00, 48.00"),
)


def review_tokens():
    """The paragraph on the reviewers' checks; empty if their reports are not there or no longer say this."""
    t = {"review_checks_paragraph": "", "review_note": "", "review_sampler_sentence": "", "review_seed_sentence": "",
         "review_present": "no"}
    texts = {name: read(REVIEW / name) for name in {q[0] for q in REVIEW_QUOTES}}
    if any(v is None for v in texts.values()):
        return t
    gone = [q for name, q in REVIEW_QUOTES if q not in " ".join(texts[name].split())]
    if gone:                                       # the reports were changed: say nothing rather than something stale
        print("NOTE: the review reports no longer hold these words (REVIEW_QUOTES), so their checks are left out: "
              + " | ".join(gone), file=sys.stderr)
        return t
    t["review_present"] = "yes"
    t["review_checks_paragraph"] = (
        "**Checks by reviewing helper agents (participant computations).** Three helper agents, further instances of "
        "the AI model that wrote this package, reviewed an earlier version of it, which had the same constants, the same "
        "class and the same count and a batch of one stage, and wrote programs of their own from the text of that proof. "
        "They are not independent parties, and what follows is quoted from their reports. Rule A, the two-stage batch "
        "and the count with rule A did not exist then and were not in front of them. One "
        "compared the whole calculation at "
        "8-bit words, that is the enumeration of outcomes, the E1 count, the E3 count, the weights and the sum over "
        "betas, with a brute force of the seven-word system written from 6.2 alone: 60 random constant sets, 1,019 "
        "classes, 17,258 pairs of a class and a beta, 874 of them with solutions, 694,652,928 solutions in all; no pair "
        "differs, and the 8,632 pairs without an eps are all empty. The same agent repeated the brute-force check of the "
        "E1 count at 8 bits with another seed (60 cases, 85,908 outcomes with solutions all equal, 60,448 sampled "
        "outcomes without solutions all zero) and made a Monte Carlo of the E1 probabilities at 32 bits for the four "
        "sampled betas with no code of the project: for their 48 outcomes with a nonzero product the chi-square "
        "statistics are 12.6 on 16, 10.6 on 10, 8.3 on 10 and 16.7 on 12 degrees of freedom, and the sums of P1 * N3 "
        "are 0.980, 0.990, 1.005 and 1.012 of the calculator's. The second agent made a Monte Carlo of E1 for the "
        "heaviest beta with 2^39 draws, 587 hits on its 16 outcomes against 628.2 predicted and none on the outcome "
        "that the calculator counts as zero, and a Monte Carlo of the E3 count for the four heaviest outcomes with 2^36 "
        "draws each: log2 N3 = 50.06 +- 0.06, 48.14 +- 0.12, 49.95 +- 0.09 and 48.04 +- 0.18 against 50, 48, 50 and 48. "
        "It also found the solution inside the class that is printed below. The third agent compared the whole "
        "calculation with a brute force of its own at 8-bit words, for 10 random cases, half of them with delta = -2, and "
        "182 classes: all 125 pairs of a class and a beta with solutions are equal, and all 46,467 pairs without "
        "solutions are zero. With a Monte Carlo of its own at 32 bits it found, for the heaviest beta, the E1 "
        "probabilities of all 16 outcomes within 0.14 bits of the calculator's, and the E3 counts of the six largest "
        "outcomes at 2^50.05, 2^47.88, 2^50.01, 2^47.92, 2^46.89 and 2^45.08 against 2^50, 2^48, 2^50, 2^48, 2^47 and "
        "2^45; for these six outcomes together it gives 12.20 million with standard error 0.44 million against 12.58 "
        "million counted. Two of the agents report that the calculator returns the same outcomes and parts for the "
        "heavy betas when delta = +2 is put in place of -2. So the count does not check the sign of delta; that is "
        "checked by the hash tests of the trial, not by the count.")
    t["review_note"] = (
        "Three reviewing helper agents wrote programs of their own from the proof of an earlier version of this "
        "package (same constants, class and count; rule A and the two-stage batch came later and were not in front of "
        "them). Two of them compared the whole "
        "calculation at 8-bit words with a brute force of the seven-word system (in one case 60 constant sets, 17,258 "
        "pairs of a class and a beta, 694,652,928 solutions, no pair differs). They made Monte Carlo estimates at 32 "
        "bits of the E1 probabilities (sums of P1 * N3 between 0.980 and 1.012 of the calculator's on the four sampled "
        "betas) and of E3 counts (four within 0.14 bit, six within 0.12 bit). One found the solution inside the class "
        "that the proof prints")
    t["review_sampler_sentence"] = (
        "A reviewing helper agent compared the sampler's draws per outcome with the calculator's P1: for this beta the "
        "chi-square statistic is 29.1 on 10 degrees of freedom, for the other three 9.8 on 12, 3.3 on 6 and 11.1 on 10; "
        "its own Monte Carlo of the same probabilities agrees with the calculator. So the excess is on the sampler's "
        "side, and its cause was not found.")
    t["review_seed_sentence"] = ("Taken over the 16 seeds, the error of the sum is 1,501,693 where the single errors "
                                 "combine to 1,451,568. That figure is a reviewing helper agent's; the helper agents "
                                 "named in this section are further instances of the AI model that wrote this package, "
                                 "which the submission note names.")
    return t


# =====================================================================================================
# PART F: rule A and the two-stage batch (fifth package): the SAT answers per outcome, the count that the
#         claim uses, the recount with the calculator as it is, and the result files of the thread that
#         found the rule (copies in evidence/followup/)
# =====================================================================================================
FOLLOWUP = EVID / "followup"


def read_outx():
    """{(beta, tau, eps): (E1, N3)}: both factors of every outcome with a nonzero product, as the recount prints them."""
    text = read(EVID / f"pairs_recount_{ETA:08x}.txt")
    if text is None:
        raise SystemExit("evidence/pairs_recount_<eta>.txt is missing: the count per outcome is not known (tools/recount_exact.sh)")
    out = {}
    for m in re.finditer(r"^OUTX ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) E1 (\d+) N3 (\d+)$", text, re.M):
        if int(m.group(1), 16) == ETA:
            out[(m.group(2), m.group(3), m.group(4))] = (int(m.group(5)), int(m.group(6)))
    return out


def read_rule_sat():
    """({(beta, tau, eps): {"ALL" / "VIOLATE": (answer, model is a solution, model satisfies rule A)}}, example or None)
    from tools/rule_a_sat.py. The file must have been made for the rule of PART A."""
    path = EVID / f"rule_a_sat_{ETA:08x}.txt"
    text = read(path)
    if text is None:
        raise SystemExit(f"missing evidence/{path.name}: run tools/rule_a_sat.py (without it rule A has no count)")
    want = "# rule A on h1 (mask:value, XOR of the masked bits): " + ",".join(f"{m:08x}:{v}" for m, v in RULE_A[ETA])
    if want not in text.split("\n"):
        raise SystemExit(f"evidence/{path.name} was made for another rule A: run tools/rule_a_sat.py again")
    res = {}
    for m in re.finditer(r"^(ALL|VIOLATE) ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) (SAT|UNSAT|\?)(?: .* solution (\d) rule_A (\d))?$", text, re.M):
        res.setdefault((m.group(2), m.group(3), m.group(4)), {})[m.group(1)] = (m.group(5), m.group(6), m.group(7))
    ex = re.search(r"^EXAMPLE ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) Y1 ([0-9a-f]{8}) Y6 ([0-9a-f]{8}) Y12 ([0-9a-f]{8}) w12 ([0-9a-f]{8}) "
                   r"w5 ([0-9a-f]{8}) Y4 ([0-9a-f]{8}) Y9 ([0-9a-f]{8}) Y14 ([0-9a-f]{8}) w8 ([0-9a-f]{8}) h1 ([0-9a-f]{8}) residual_zero 1 "
                   r"rule_A 0 checked 1$", text, re.M)
    return res, (ex.groups() if ex else None)


def read_calc2():
    """The recount with the calculator as it is (tools/recount_calc2.sh mass), or None: (SHA-256 of the binary,
    {beta: part}, {(beta, tau, eps): (log2 P1, log2 N3)} for the outcomes with a nonzero E3 count, number of lines
    that report a fallback or a failed run)."""
    text = read(EVID / f"calc2_recount_{ETA:08x}.txt")
    if text is None:
        return None
    sha = re.search(r"^BINARY night_pair_calc2 sha256 ([0-9a-f]{64})", text, re.M)
    parts = {m.group(1): float(m.group(2)) for m in re.finditer(
        rf"^EXACT-E1 {ETA:08x} ([0-9a-f]{{8}}) .*class-rate part ([\d.]+) ", text, re.M)}
    outs = {(m.group(1), m.group(2), m.group(3)): (float(m.group(4)), float(m.group(5))) for m in re.finditer(
        r"^OUT ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) log2P1 (-?[\d.]+) log2N3 (-?[\d.]+)$", text, re.M)}
    bad = len(re.findall(r"sampled [1-9]|formula fallbacks [1-9]|^DONE \S+ exit [1-9]", text, re.M))
    return (sha.group(1) if sha else None), parts, outs, bad


def read_calc2_total(rows):
    """The recount of every beta of the list with the calculator as it is (tools/recount_calc2.sh all), or None:
    (betas recounted, betas of the list, betas whose line differs from the list's, sum of the recounted parts)."""
    text = read(EVID / f"calc2_total_{ETA:08x}.txt")
    if text is None:
        return None
    got = {}
    for line in text.split("\n"):
        f = line.split()
        if len(f) >= 4:
            got[f[0]] = (float(f[3]), len(f) > 4)
        elif f:
            got[f[0]] = (None, len(f) != 2)
    listed = {beta: part for beta, _, _, part in rows}
    differ = [b for b, (part, flag) in got.items() if b not in listed or (part is None) != (listed[b] is None)
              or (part is not None and abs(part - listed[b]) > 0.06) or (flag and part)]
    # betas whose line carries a remark of the calculator (an outcome through the random-subset branch of the E3 count
    # or an E1 count by the product formula); a remark on a beta with a nonzero part counts as a difference above
    flagged = sorted(b for b, (part, flag) in got.items() if flag)
    remarks = re.findall(r"(sampled|fallbacks)=(\d+)", " ".join(l for l in text.split("\n") if len(l.split()) > 4))
    detail = read(EVID / f"calc2_flagged_{ETA:08x}.txt") or ""
    outs = re.findall(r"^OUT ([0-9a-f]{8}) [0-9a-f]{8} [0-9a-f]{8} log2P1 (-?[\d.]+) ", detail, re.M)
    known = {b for b, _ in outs} == set(flagged) and len(re.findall(r"^DONE \S+ exit 0$", detail, re.M)) == len(flagged)
    return (len(got), len(listed), differ, sum(part for part, _ in got.values() if part), flagged,
            sum(int(n) for kind, n in remarks if kind == "sampled"), sum(int(n) for kind, n in remarks if kind == "fallbacks"),
            (len(outs), sum(float(lp) < -900 for _, lp in outs)) if known else None)


def read_rule_sat2(d, sat):
    """{solver: {(beta, tau, eps): answer to "system AND h1 violates rule A"}} from tools/rule_a_sat2.py, for the
    solvers of RULE_SAT2_SOLVERS whose file is there and sound: the tool as it is now has the constants and the rule
    of PART A, the file covers exactly the outcomes of the count, every base formula is satisfiable with a model that
    is a solution in plain arithmetic, no answer is missing, and every violating model is a solution that violates
    rule A. A file that is there and not sound stops the build."""
    tool = TOOLS / "rule_a_sat2.py"
    code = read(tool)
    out = {}
    if code is None:
        return out
    consts = re.search(r"^ETA, Y3, Y3B = 0x([0-9A-Fa-f]{8}), 0x([0-9A-Fa-f]{8}), 0x([0-9A-Fa-f]{8})$", code, re.M)
    cls = re.search(r"\(\(Y3 \+ y4\) & 0x([0-9A-Fa-f]{8})\) == 0x([0-9A-Fa-f]{8})", code)
    rule = re.search(r"return (b\(.*\))$", code, re.M)
    conds = set(re.findall(r"b\((\d+)\) (==|!=) (?:b\((\d+)\)|(\d))", rule.group(1))) if rule else set()
    want = set()
    for mask, value in RULE_A[ETA]:
        bits = [i for i in range(32) if mask >> i & 1]
        want.add((str(bits[0]), "==", "", str(value)) if len(bits) == 1 else (str(bits[0]), "!=" if value else "==", str(bits[1]), ""))
    same = (consts and cls and [int(v, 16) for v in consts.groups()] == [ETA, d["Y3"], d["Y3B"]]
            and [int(v, 16) for v in cls.groups()] == [d["qmask"], d["qvalue"]] and conds == want)
    for solver in RULE_SAT2_SOLVERS:
        text = read(EVID / f"rule_a_sat2_{solver}_{ETA:08x}.txt")
        if text is None:
            continue
        if not same:
            raise SystemExit("tools/rule_a_sat2.py does not have the constants and the rule of PART A; its output cannot be quoted")
        base, vio = {}, {}
        for m in re.finditer(r"^(BASE|VIOLATE) ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) (SAT|UNSAT|\?)(?: solution (\d) rule_A (\d) h1 [0-9a-f]{8})?$",
                             text, re.M):
            (base if m.group(1) == "BASE" else vio)[(m.group(2), m.group(3), m.group(4))] = (m.group(5), m.group(6), m.group(7))
        if (set(base) != set(sat) or set(vio) != set(sat) or any(v[:2] != ("SAT", "1") for v in base.values())
                or any(v[0] not in ("SAT", "UNSAT") or (v[0] == "SAT" and v[1:] != ("1", "0")) for v in vio.values())):
            raise SystemExit(f"evidence/rule_a_sat2_{solver}_{ETA:08x}.txt is not complete or a model failed its check")
        out[solver] = {k: v[0] for k, v in vio.items()}
    return out


def read_rule_share(d):
    """tools/rule_share.sh: rule A and the batches that enter stage 2 on real trials in the layout of 6.4. None unless
    the output was made by tools/rule_share.c as it is now, that source has the constants of PART A, every vector of
    its check against the real compression agrees, and the run sizes are those of the class. Returns a dict."""
    import hashlib
    src = TOOLS / "rule_share.c"
    text = read(EVID / f"rule_share_{RULE_SHARE_RUN}.txt")
    if text is None or not src.exists():
        return None
    code = src.read_bytes()
    defs = {m.group(1): int(m.group(2), 16) for m in re.finditer(r"^#define (\w+) 0x([0-9A-Fa-f]+)u$", code.decode("ascii"), re.M)}
    want = {"CX3": PIN["X3"], "CX7": PIN["X7"], "CX11": PIN["X11"], "CX15": PIN["X15"], "CW4": PIN["W4"], "CW13": PIN["W13"],
            "CY3": d["Y3"], "QMASK": d["qmask"], "QVALUE": d["qvalue"], "RS": d["a_shift"], "RALL": d["a_all"], "RV": d["a_value"]}
    head = re.match(r"SOURCE tools/rule_share\.c sha256 ([0-9a-f]{64}) arguments (\d+) (\d+) (\d+) (\d+) seconds \d+ threads \d+\n"
                    r"VECTORS (\d+), z and rule A of the C program equal those of the real compression in (\d+); satisfy rule A \d+; "
                    r"digest compared with the organizer's reference hash in (\d+)\n", text)
    # the ranges of X12 and X13 and the sizes of the class loop, as the source has them
    ranges = re.search(r"\(u32\)sm\(&s\) & 0x([0-9A-F]+), \(u32\)sm\(&s\) & 0x([0-9A-F]+), \(u32\)sm\(&s\)\};", code.decode("ascii"))
    layout = (ranges and [int(v, 16) for v in ranges.groups()] == [(1 << LOG2_X12) - 1, (1 << d["x13"]) - 1]
              and f"j < {d['list_words']}; j++" in code.decode("ascii") and f"k < {d['members']}; k++" in code.decode("ascii")
              and "u32 f[9] = {0, X2, X5, X6, X9, 0," in code.decode("ascii"))
    if defs != want or not layout or not head or head.group(1) != hashlib.sha256(code).hexdigest() or head.group(6) != head.group(7):
        print("NOTE: evidence/rule_share_*.txt is not from tools/rule_share.c as it is now, or that source does not have the "
              "constants of PART A; the measurement in the layout of 6.4 is left out", file=sys.stderr)
        return None
    n_runs, ctx, alphas = int(head.group(2)), int(head.group(3)), int(head.group(4))
    runs = [tuple(int(v) for v in r) for r in re.findall(
        r"^RUN \d+ trials (\d+) satisfy_rule_A (\d+) share\*64 [\d.]+ dev_sd [-+\d.]+ batches (\d+) enter_stage_2 (\d+) ", text, re.M)]
    trials, batches = ctx * alphas * d["members"], ctx * alphas * d["list_words"]
    if len(runs) != n_runs or n_runs < 2 or any(r[0] != trials or r[2] != batches for r in runs) or trials & (trials - 1):
        raise SystemExit("evidence/rule_share_*.txt: the runs do not have the sizes that its first line and the class give")
    p = 2.0 ** -d["rule_conditions"]
    passes, entered = [r[1] for r in runs], [r[3] for r in runs]
    q = sum(entered) / (n_runs * batches)
    return dict(runs=n_runs, contexts=ctx, alphas=alphas, trials=trials, batches=batches, vectors=int(head.group(6)),
                with_reference=int(head.group(8)),
                share=[x / (trials * p) for x in passes], share_all=sum(passes) / (n_runs * trials * p),
                chi=sum((x - trials * p) ** 2 / (trials * p * (1 - p)) for x in passes),
                batch=[x / batches for x in entered], batch_all=q,
                batch_chi=sum((x - batches * q) ** 2 / (batches * q * (1 - q)) for x in entered),
                independent=1 - (1 - p) ** 7)


def read_rule_share_seeds(d):
    """tools/rule_share_seeds.py: the same over many sets of seed words, with sampled batches. None unless the file is
    there for RULE_SHARE_SEEDS_RUN, the tool has the rule of PART A as written (it takes the constants and the class
    from the program of the package), and its check against the real messages found nothing wrong. Returns a dict
    computed from the lines per set, not from the summary lines."""
    sets, lg, first = RULE_SHARE_SEEDS_RUN
    text = read(EVID / f"rule_share_seeds_{sets}_{lg}_{first}.txt")
    code = read(TOOLS / "rule_share_seeds.py")
    if text is None or code is None:
        return None
    rule = re.search(r"ok = \(b\(16\) == 1\) & \(b\(0\) == b\(1\)\) & \(b\(1\) == b\(2\)\) & \(b\(2\) == b\(3\)\) & \(b\(3\) != b\(4\)\) & "
                     r"\(b\(23\) != b\(24\)\)", code)
    mine = ((0x00010000, 1), (0x00000003, 0), (0x00000006, 0), (0x0000000C, 0), (0x00000018, 1), (0x01800000, 1))
    check = re.search(r"^SUMMARY check of this file against the real messages \(halfsearch\.reference\): (\d+) lanes compared, (\d+) wrong$",
                      text, re.M)
    rows = [tuple(int(v) for v in r) for r in re.findall(r"^SEED (\d+) batches (\d+) lanes (\d+) pass (\d+) entered (\d+)$", text, re.M)]
    layout = (f"X12 = rng.integers(0, 1 << {LOG2_X12}, B" in code and f"X13 = rng.integers(0, 1 << {d['x13']}, B" in code
              and "X1, X2, X5, X6, X9, X10 = U(0), U(x2), U(x5), U(x6), U(x9), U(0)" in code)
    if not rule or not layout or tuple(RULE_A[ETA]) != mine or not check or check.group(2) != "0" or len(rows) != sets \
            or any(r[1] != 1 << lg for r in rows) or [r[0] for r in rows] != list(range(first, first + sets)):
        print("NOTE: evidence/rule_share_seeds_*.txt is not complete or not for the rule of PART A; it is left out", file=sys.stderr)
        return None
    p = 2.0 ** -d["rule_conditions"]
    lanes, passing, entered = sum(r[2] for r in rows), sum(r[3] for r in rows), sum(r[4] for r in rows)
    batches = sets << lg
    q = entered / batches
    budget_lane = d["list_words"] * 2.0 ** d["stage2_shift"] / 2.0 ** d["T"]
    return dict(sets=sets, log2=lg, lanes=lanes, passing=passing, checked=int(check.group(1)),
                rate=math.log2(passing / lanes), dev=(passing - lanes * p) / math.sqrt(lanes * p * (1 - p)),
                lane_min=min(r[3] / r[2] for r in rows) / p, lane_max=max(r[3] / r[2] for r in rows) / p,
                lane_sd=math.sqrt((1 - p) / (rows[0][2] * p)), lane_need=budget_lane / p,
                chi=sum((r[3] - r[2] * p) ** 2 / (r[2] * p * (1 - p)) for r in rows),
                batch_all=q, batch_min=min(r[4] / r[1] for r in rows), batch_max=max(r[4] / r[1] for r in rows),
                batch_chi=sum((r[4] - r[1] * q) ** 2 / (r[1] * q * (1 - q)) for r in rows),
                over=sum(r[4] / r[1] >= 1 / 2 ** STAGE_2_LOG2_SHARE for r in rows),
                exclude=-math.log(0.05) / sets)


def rule_text():
    """Rule A in words, from PART A: the lines of the display in 6.3, and one sentence."""
    single, equal, differ = [], [], []
    for mask, value in RULE_A[ETA]:
        bits = [i for i in range(32) if mask >> i & 1]
        if len(bits) == 1:
            single.append(f"bit {bits[0]} of h1 is {value}")
        elif len(bits) == 2:
            (differ if value else equal).append(f"{bits[0]} and {bits[1]}")
        else:
            raise SystemExit("rule A: a condition on more than two bits has no wording here")
    lines = single + [f"bits {p} of h1 are equal" for p in equal] + [f"bits {p} of h1 differ" for p in differ]
    return lines


def rule_tokens(d, counted, total, rows):
    """Lemma A, the count that the claim uses, and the paragraphs of Section 10 on rule A."""
    F, t = LOG2_FACTOR, {}
    lines = rule_text()
    t["rule_a_block"] = "\n".join("    " + l + (";" if i + 1 < len(lines) else ".") for i, l in enumerate(lines))
    t["rule_a_inline"] = join(lines)
    zl = []
    for low, high, value, _, _ in d["z_conditions"]:
        zl.append(f"bit {low} of z is {value}" if high is None else
                  f"bits {low} and {high} of z {'differ' if value else 'are equal'}")
    t["rule_z_block"] = "\n".join("    " + l + (";" if i + 1 < len(zl) else ".") for i, l in enumerate(zl))
    hbits = sorted({b for c in d["z_conditions"] for b in c[3]})
    ebits = sorted({b for c in d["z_conditions"] for b in c[4]})
    t["rule_h_bits"], t["rule_e_bits"] = join(str(b) for b in hbits), join(str(b) for b in ebits)
    t["rule_e_values"] = join(f"bit {b} is {d['qvalue'] >> b & 1}" for b in ebits)
    t["rule_z_bits_count"] = WORDS[len({b for c in d["z_conditions"] for b in c[:2] if b is not None})]
    t["rule_pairs"] = WORDS[sum(1 for c in d["z_conditions"] if c[1] is not None)]
    t["rule_singles"] = WORDS[sum(1 for c in d["z_conditions"] if c[1] is None)]

    # ---- the count with rule A
    outx, (sat, example), calc2 = read_outx(), read_rule_sat(), read_calc2()
    if set(sat) != set(outx):
        raise SystemExit("the SAT answers are not for the outcomes of the count: run tools/rule_a_sat.py again")
    for key, v in sat.items():
        a, w = v.get("ALL", ("?", None, None)), v.get("VIOLATE", ("?", None, None))
        if a[0] != "SAT" or a[1] != "1" or w[0] not in ("SAT", "UNSAT") or (w[0] == "SAT" and w[1:] != ("1", "0")):
            raise SystemExit(f"a SAT answer is missing or a model failed its check for outcome {key}: read evidence/rule_a_sat_<eta>.txt")
    scale = 2 ** (96 - d["fixed"])
    prod = {k: Fraction(e * n, scale) for k, (e, n) in outx.items()}
    by_beta = {}
    for (beta, _, _), v in prod.items():
        by_beta[beta] = by_beta.get(beta, 0) + v
    parts = {b: p for p, b, _, _ in counted}
    kof = {b: k for _, b, k, _ in counted}
    if set(by_beta) != set(parts) or any(abs(float(by_beta[b]) - parts[b]) > 0.06 for b in parts):
        raise SystemExit("the outcomes with their two factors in full do not add up to the parts of the count")
    full = sum(prod.values())
    bad = sorted(k for k, v in sat.items() if v["VIOLATE"][0] == "SAT")
    lost = sum(prod[k] for k in bad)
    used = int(round(total)) - math.ceil(lost)          # as printed: the count, minus the dropped part rounded up
    if not used <= full - lost:
        raise SystemExit("rule A: the printed difference is above the count without the dropped outcomes")
    if used < 2.9 * 2 ** F:
        raise SystemExit("the count with rule A is less than 2.9 times the assumed factor: lower log2_factor")
    kept_by_witness = sum(1 for v in sat.values() if v["ALL"][2] == "1")
    t.update(rule_outcomes=str(len(outx)), rule_ok=str(len(outx) - len(bad)), rule_bad=str(len(bad)),
             rule_bad_betas=WORDS[len({k[0] for k in bad})] if len({k[0] for k in bad}) < len(WORDS) else str(len({k[0] for k in bad})),
             rule_lost=num(math.ceil(lost)), rule_count=num(used), rule_count_plain=str(used),
             # the share that is lost, rounded to six decimals, and what is left of 1: the two printed figures add up
             rule_lost_pct=f"{100 * round(float(lost / full), 6):.4f}",
             rule_kept=f"{1 - round(float(lost / full), 6):.6f}",
             rule_models_passing=str(kept_by_witness),
             full_over_factor=f"{math.floor(total / 2 ** F * 100) / 100:.2f}",
             exact_over_factor=f"{math.floor(used / 2 ** F * 100) / 100:.2f}",
             exact_over_alt=f"{math.floor(used / 2 ** (F - 1) * 10) / 10:.1f}",
             per_run=f"{math.floor(used / 2 ** (F + 1) * 100) / 100:.2f}",
             cluster_max=f"{math.floor(used / d['f_min'] * 100) / 100:.2f}",
             rule_log2=f"{math.floor(math.log2(used) * 100) / 100:.2f}",
             rule_hit_exp=f"{up(128 - math.log2(used), 2):.2f}")
    badset = set(bad)

    rounded = {}

    def exact(v, name=None):
        """A sum of products P1 * N3 / 2^(96 - fixed bits) as a decimal number: in full, with at least one decimal,
        when it has at most four decimals; else rounded to one, and its name and value are kept so that the text can
        say so and why."""
        v = Fraction(v)
        for digits in (1, 2, 3, 4):
            if (v * 10 ** digits).denominator == 1:
                return f"{float(v):,.{digits}f}"
        rounded.setdefault(name, set()).add(v)
        return f"{float(v):,.1f}"

    def short(v):
        """The number with at most four decimals nearest to v, as text, and its distance from v."""
        n = Fraction(round(v * 10 ** 4), 10 ** 4)
        digits = next(i for i in range(5) if (n * 10 ** i).denominator == 1)
        return f"{float(n):,.{digits}f}", abs(v - n)

    head = "| beta | k | Outcomes | Dropped | Part of the beta | Part dropped |\n| --- | ---: | ---: | ---: | ---: | ---: |\n"
    body, drows = [], []
    order = sorted({k[0] for k in bad}, key=lambda b: (-sum(prod[k] for k in bad if k[0] == b), b))
    for beta in order:
        drop = sorted((k for k in bad if k[0] == beta), key=lambda k: (-prod[k], k))
        # both columns from the same exact products, so that a beta that is dropped in full shows the same number twice
        body.append(f"| {beta} | {kof[beta]} | {sum(1 for k in outx if k[0] == beta)} | {len(drop)} | "
                    f"{exact(by_beta[beta], 'the part of beta ' + beta)} | {exact(sum(prod[k] for k in drop), 'what is dropped of beta ' + beta)} |")
        drows += [f"| {k[0]} | {k[1]} | {k[2]} | {exact(prod[k], 'an outcome of beta ' + k[0])} |" for k in drop]
    body.append(f"| sum | | | {len(bad)} | | {exact(lost, 'the sum')} |")
    t["rule_table"] = head + "\n".join(body)
    t["rule_dropped_table"] = ("| beta | tau | eps | Adds |\n| --- | --- | --- | ---: |\n" + "\n".join(drows)
                               + f"\n| sum | | | {exact(lost, 'the sum')} |")
    # A figure that is rounded is named, with the reason. The factors are printed by a calculator that computes in
    # floating point (Section 10, steps 1 to 5), so a value from the printed factors can miss a number with at most
    # four decimals by that rounding alone: below 10^-9 it is described as such, and not as a property of the count.
    near = {name: [short(v) for v in sorted(values)] for name, values in rounded.items()}
    noise = sorted(name for name, found in near.items() if all(gap < 1e-9 for _, gap in found))
    real = sorted(name for name in near if name not in noise)
    excepted = []
    if noise:
        size = f"about 10^{round(math.log10(max(gap for name in noise for _, gap in near[name])))}"
        excepted.append(
            f"{noise[0]}, whose value from the printed factors differs from {near[noise[0]][0][0]} by the calculator's "
            f"floating-point rounding ({size}) and is rounded to one decimal"
            if len(noise) == 1 and len(near[noise[0]]) == 1 else
            f"{join(noise)}, whose values from the printed factors differ from numbers with at most four decimals by the "
            f"calculator's floating-point rounding (at most {size}) and are rounded to one decimal")
    if real:
        excepted.append(f"{join(real)}, which {'has' if len(real) == 1 else 'have'} more than four decimals and "
                        f"{'is' if len(real) == 1 else 'are'} rounded to one")
    t["rule_exact_decimals"] = ("The figures of these two tables are printed in full"
                                + (", except " + "; and except ".join(excepted) if excepted else "") + ".")
    worst = max(bad, key=lambda k: (prod[k], k))
    t["rule_worst"] = (f"The largest of them is the outcome tau = {worst[1]}, eps = {worst[2]} of beta {worst[0]}, with "
                       f"{exact(prod[worst])}.")
    # the outcomes of the heaviest beta, whose counts Section 10 prints: can the reader put the question again?
    hv = max(parts, key=lambda b: parts[b])
    hv_keys = [k for k in outx if k[0] == hv]
    clean = [b for b in parts if not any(k[0] == b for k in bad)]
    t["rule_heaviest_sentence"] = (
        f"For all {len(hv_keys)} outcomes of the heaviest beta, {hv}, which are written out above with their two "
        f"counts, the answer is that no solution violates rule A. So for {100 * parts[hv] / total:.0f}% of the count the "
        f"question can be put again to any SAT solver from the definitions of 6.2 and 6.3, without any file of the "
        f"participant. The {len(clean)} betas without a dropped outcome carry "
        f"{math.floor(1e4 * sum(parts[b] for b in clean) / total) / 100:.2f}% of the count."
        if hv_keys and all(sat[k]["VIOLATE"][0] == "UNSAT" for k in hv_keys) else
        f"Among the outcomes of the heaviest beta, {hv}, {sum(sat[k]['VIOLATE'][0] == 'SAT' for k in hv_keys)} have a "
        f"solution that violates rule A.")

    # ---- the same questions with a second CNF formula and other solvers (tools/rule_a_sat2.py)
    other = read_rule_sat2(d, sat)
    mine = {k: v["VIOLATE"][0] for k, v in sat.items()}
    agree = [s for s, ans in other.items() if ans == mine]
    if len(agree) != len(other):
        raise SystemExit("a second solver's answers on rule A differ from those of kissat: read evidence/rule_a_sat2_*.txt; "
                         "an outcome with a violating solution in either file must be left out")
    n_solvers = 1 + len(agree)
    t["rule_solvers"] = WORDS[n_solvers]
    if agree:
        t["rule_solvers_claim"] = f"{WORDS[n_solvers]} SAT solvers find"
        t["rule_unsat_who"] = f"{WORDS[n_solvers]} solvers answer"
        t["rule_unsat_basis"] = (f"the answers of {WORDS[n_solvers]} solvers, {WORDS[len(agree)]} of them on a formula written "
                                 f"separately by a reviewing helper agent, without a checked certificate")
        t["rule_unsat_claim"] = (f"on the uncertified answers of {WORDS[n_solvers]} SAT solvers ({WORDS[len(agree)]} on a "
                                 f"formula of a reviewing helper agent)")
        t["rule_sat2_sentence"] = (
            f"The answers reported so far are those of kissat in one run. The same {len(outx)} pairs of questions were "
            f"then put to {WORDS[len(agree)]} other solver{'s' if len(agree) != 1 else ''}, {join(agree)}, with a CNF formula "
            f"of another making. A reviewing helper agent wrote it from 6.2 alone: its unknown is Y14 where the first "
            f"formula has h1, it prescribes the differences of h1 and of the four outputs of E3 where the first "
            f"prescribes those of e1, g1, e2 and g2, and its clauses for the additions are its own. It was run again "
            f"for this text. {'Each of these solvers' if len(agree) != 1 else 'That solver'} gives "
            f"the answer of kissat for every outcome: a solution for all {len(outx)}, no violating solution for {len(outx) - len(bad)} and one for "
            f"{len(bad)}, and every model was evaluated again in plain arithmetic. So {WORDS[n_solvers]} solvers and two "
            f"formulas agree. No proof certificate was kept or checked for any of them, and both formulas were written by "
            f"instances of the same AI model.")
        t["rule_sat2_note"] = (f"{WORDS[len(agree)].capitalize()} other solver{'s' if len(agree) != 1 else ''} "
                               f"({join(agree)}), on a formula that a reviewing helper agent wrote separately, give the "
                               f"same answer for every outcome; no certificate was checked for any of them.")
        t["rule_unsat_note"] = f"the answers of {WORDS[n_solvers]} SAT solvers for {len(outx) - len(bad)} outcomes"
    else:
        t["rule_solvers_claim"] = "a SAT solver finds"
        t["rule_unsat_who"] = "the solver answers"
        t["rule_unsat_basis"] = "the answers of one solver in one run, without a checked certificate"
        t["rule_unsat_claim"] = "on one SAT solver's uncertified answers"
        t["rule_sat2_sentence"] = ("They are the answers of one solver in one run; no proof certificate was kept or checked.")
        t["rule_sat2_note"] = "The solver's answers \"none\" are one solver's, without a checked certificate."
        t["rule_unsat_note"] = f"a SAT solver's answers for {len(outx) - len(bad)} outcomes"

    # ---- the betas the rule was read from against the betas that the longer list added
    t["rule_fit_sentence"], t["rule_fit_limit"], t["rule_fit_note"], t["rule_fit_claim"] = "", "", "", ""
    seen_text = re.search(r"^BETAS_BY_MASS (\S+)", read(FOLLOWUP / "pinB3_rules.txt") or "", re.M)
    fr = read_followup_rules()
    if seen_text and fr:
        seen = set(seen_text.group(1).split(","))
        inside, outside = [k for k in outx if k[0] in seen], [k for k in outx if k[0] not in seen]
        if seen <= set(parts) and len(seen) == fr[1] and len(inside) == fr[0] and outside:
            def figures(keys):
                drop = [k for k in keys if k in badset]
                betas = {k[0] for k in keys}
                return (len(betas), len(keys), len(drop), sum(prod[k] for k in keys), sum(prod[k] for k in drop),
                        sum(1 for b in betas if all(k in badset for k in keys if k[0] == b)), sorted({kof[b] for b in betas}))
            a, b = figures(inside), figures(outside)
            pa, pb = 100 * float(a[4] / a[3]), 100 * float(b[4] / b[3])
            wn = lambda n: WORDS[n] if n < len(WORDS) else str(n)  # noqa: E731
            ks = f"all with k = {b[6][0]}" if len(b[6]) == 1 else f"with k from {b[6][0]} to {b[6][-1]}"
            if pb > pa:
                t["rule_fit_sentence"] = (
                    f"Rule A was read from the outcomes of these {a[0]} betas. Of their {a[1]} outcomes {a[2]} have a "
                    f"violating solution, and these carry {num(a[4])} of {num(a[3])}, {pa:.3f}%. The longer list of this "
                    f"package adds {wn(b[0])} betas with a part, {ks}, with {num(b[3])} together. Of their {b[1]} outcomes "
                    f"{b[2]} have a violating solution, and these carry {num(b[4])}, {pb:.2f}% of what these betas add: a "
                    f"share about {pb / pa:.0f} times as large, and {wn(b[5])} of the {wn(b[0])} betas are left out in full. "
                    f"So the betas that the rule was not read from comply with it less, and the betas with k above "
                    f"{b[6][-1]}, which are not counted, may violate it more often still. This does not change the figure "
                    f"that the claim uses: it leaves all these outcomes out, and no uncounted beta is in it.")
                t["rule_fit_limit"] = (
                    f"Among the counted betas, those that the rule was not read from comply with it less: the outcomes with "
                    f"a violating solution carry {pb:.2f}% of the part of the {wn(b[0])} betas that were added after the "
                    f"rule was chosen, against {pa:.3f}% for the {a[0]} that it was read from. Solutions of betas outside "
                    f"the list are not in the count; nothing is known about whether they satisfy rule A, and by this "
                    f"comparison they may violate it more often. The claim does not use them.")
                t["rule_fit_note"] = (
                    f"The rule was read from {a[0]} of the {len(parts)} betas. In the {wn(b[0])} that were added later the "
                    f"outcomes with a violating solution carry {pb:.2f}% of their part, against {pa:.3f}% in those "
                    f"{a[0]}; betas that are not counted may violate the rule more often still.")
                t["rule_fit_claim"] = (f" In the {wn(b[0])} counted values of beta that the rule was not read from, the "
                                       f"outcomes left out carry {pb:.2f}% of the part, against {pa:.3f}% in the others.")
    if not t["rule_fit_limit"]:
        t["rule_fit_limit"] = ("Solutions of betas outside the list are not in the count, and nothing is known about whether "
                               "they satisfy rule A; the claim does not use them.")

    # ---- the recount with the calculator as it is
    if calc2 is None:
        t["calc2_sentence"] = ("The parts were not recounted with the calculator in its present form for this package.")
        t["calc2_state"] = "none"
    else:
        sha, cparts, couts, cbad = calc2
        nonzero = {k: v for k, v in couts.items() if v[0] > -900}
        if set(cparts) != set(parts) or any(abs(cparts[b] - parts[b]) > 0.06 for b in parts) or cbad:
            raise SystemExit("the recount with night_pair_calc2 does not give the parts of the count (evidence/calc2_recount_<eta>.txt)")
        if set(nonzero) != set(outx):
            raise SystemExit("the recount with night_pair_calc2 has other outcomes with a nonzero product than the count")
        gap = max(max(abs(math.log2(outx[k][0]) - (96 - kof[k[0]]) - nonzero[k][0]), abs(math.log2(outx[k][1]) - nonzero[k][1]))
                  for k in outx)
        if gap > 0.0051:
            raise SystemExit("an outcome's factors in full do not agree with the logarithms that night_pair_calc2 prints")
        t["calc2_sentence"] = (
            f"For this package the {len(parts)} betas with a nonzero part were counted once more with the compiled calculator "
            f"in its present form, which was run and not built again: it returns the same {len(parts)} parts, "
            f"{num(sum(cparts.values()))} in all, no outcome through either fallback, and the same {len(outx)} outcomes with a "
            f"nonzero product. The products P1 * N3 of the single outcomes are taken from the recount that prints both "
            f"factors in full; their logarithms agree with the two decimals that the calculator prints for every outcome.")
        t["calc2_state"] = "done"
    ct = read_calc2_total(rows)
    t["calc2_flag_note"] = ""
    t["calc2_flag_short"] = ""
    t["enumerated_caveat"] = ""
    if ct is not None and ct[4] and not ct[2] and ct[0] == ct[1]:
        nb, ns, zero_e1 = len(ct[4]), ct[5], bool(ct[7] and ct[7][0] == ct[7][1])
        t["calc2_flag_short"] = (
            f"; for {WORDS[nb] if nb < len(WORDS) else nb} value{'s' if nb != 1 else ''} without a part the second call was "
            f"sampled for {WORDS[ns] if ns < len(WORDS) else ns} outcome{'s' if ns != 1 else ''}"
            + (", and wherever its value there is not zero the first-call count is zero" if zero_e1 else ""))
    if ct is not None and ct[4] and not ct[2]:
        nb = len(ct[4])
        t["enumerated_caveat"] = (f" (for {WORDS[nb] if nb < len(WORDS) else nb} of them, {'all' if nb != 1 else 'which is'} "
                                  f"without a part, not without sampling: see the second count below)")
    if ct is None:
        t["calc2_total_sentence"] = ("The betas without a part were not counted again for this package; that they have none is "
                                     "taken from the count described above.")
        t["calc2_total_state"] = "none"
    else:
        done, listed, differ, csum, flagged, n_sampled, n_formula, detail = ct
        if differ:
            raise SystemExit(f"the recount of the whole list differs from the list for {differ[:6]} (evidence/calc2_total_<eta>.txt)")
        if n_formula:
            raise SystemExit("the recount of the whole list reports E1 counts by the product formula: the text has no words for that")
        remark = ""
        if flagged:
            nb = len(flagged)
            remark = (
                f" For {WORDS[nb] if nb < len(WORDS) else nb} beta{'s' if nb != 1 else ''} of the list, {join(flagged)}, "
                f"{'all' if nb != 1 else 'which is'} without a part, that run reports what the per-beta file of the first "
                f"count does not record: the E3 count of {WORDS[n_sampled] if n_sampled < len(WORDS) else n_sampled} "
                f"outcome{'s' if n_sampled != 1 else ''} went through the random-subset branch, so "
                f"{'these values are estimates' if n_sampled != 1 else 'this value is an estimate'}. "
                + (f"The {detail[0]} outcomes of these betas with a nonzero E3 value all have an exact E1 count of zero, so "
                   f"their product is zero whatever N3 is. " if detail and detail[0] == detail[1] else
                   "Their parts are zero to the one decimal that the calculator prints. ")
                + "An outcome whose E3 value that branch estimated as zero would be missing from the sum; that can only make "
                  "the figure smaller. So for these betas the E3 side was not counted without sampling.")
        if done == listed:
            t["calc2_total_sentence"] = (
                f"The whole list was also counted once more with that binary, all {num(listed)} betas: the same betas have "
                f"no eps, the same {len(parts)} have a part, every part is the same, and the sum is {num(csum)}." + remark)
            t["calc2_total_state"] = "done" + (f", {len(flagged)} betas without a part with a sampled E3 count" if flagged else "")
            t["calc2_flag_note"] = (
                f" In {len(flagged)} betas without a part the E3 count of {n_sampled} outcomes was an estimate from a random "
                f"subset; their exact E1 count is zero." if flagged and detail and detail[0] == detail[1] else
                f" In {len(flagged)} betas without a part the E3 count of {n_sampled} outcomes was an estimate from a random "
                f"subset." if flagged else "")
        else:
            t["calc2_total_sentence"] = (
                f"A second count of the whole list with that binary was not finished when this text was written: "
                f"{num(done)} of the {num(listed)} betas were done, and none of them differs from the list. For the other "
                f"betas, that they have no part is taken from the count described above.")
            t["calc2_total_state"] = f"{done} of {listed}"

    # ---- one complete solution that violates rule A
    if example:
        beta, tau, eps, y1, y6, y12, w12, w5, y4, y9, y14, w8, h1 = example
        v = [int(x, 16) for x in (y1, y6, y12, w12, w5, y4, y9, y14, w8, h1)]
        ea, eb = g_steps(v[0], v[1], d["Y11"], v[2], v[3], v[4]), g_steps(v[0], v[1], d["Y11B"], v[2], v[3], (v[4] + d["delta"]) & M32)
        fa, fb = g_steps(d["Y3"], v[5], v[6], v[7], 0, v[8]), g_steps(d["Y3B"], v[5], v[6], v[7], 0, v[8])
        residual = (ea["a2"] ^ fa["c2"] ^ eb["a2"] ^ fb["c2"], fa["a2"] ^ ea["c2"] ^ fb["a2"] ^ eb["c2"],
                    fa["b2"] ^ ea["d2"] ^ fb["b2"] ^ eb["d2"], ea["b2"] ^ fa["d2"] ^ eb["b2"] ^ fb["d2"])
        if any(residual) or fa["d1"] != v[9] or rule_a(v[9]) or ((d["Y3"] + v[5]) & d["qmask"]) != d["qvalue"]:
            raise SystemExit("the example of a solution that violates rule A does not check (evidence/rule_a_sat_<eta>.txt)")
        fails = [l for l, (mask, value) in zip(rule_text_all(), RULE_A[ETA]) if bin(v[9] & mask).count("1") & 1 != value]
        t["rule_example_paragraph"] = (
            f"A complete solution of the seven-word system with Y4 in the class that violates rule A, which can be checked "
            f"by hand from 6.2: Y1 = {y1}, Y6 = {y6}, Y12 = {y12}, w12 = {w12}, w5 = {w5}, Y4 = {y4}, Y9 = {y9}, "
            f"Y14 = {y14}, w15 = 0, w8 = {w8}. For these values the four residual words of 6.2 are zero, and h1 = {h1} "
            f"does not satisfy rule A: {join(fails)} fail{'s' if len(fails) == 1 else ''}. Its outcome is tau = {tau}, "
            f"eps = {eps} with beta = {beta}, one of the outcomes that the count leaves out. The E3 values are the solver's "
            f"model for that outcome and the E1 values come from a second solver call. It shows that a collision need not "
            f"satisfy rule A; it does not show that a message reaches such values.")
        t["rule_example_state"] = "yes"
    else:
        t["rule_example_paragraph"] = (
            "The solver's models that violate rule A are solutions of the E3 system of their outcomes, and each of these "
            "outcomes has P1 > 0. No complete solution of the seven-word system that violates rule A is printed here.")
        t["rule_example_state"] = "no"
    return t


def other_rule_sentence(best_eta):
    """What is known about a rule A for the class with the largest count, from the thread that found rule A
    (evidence/followup/pinB4_rules.txt); says so when nothing is."""
    lead = ("With a batch of one stage the claim would be the same for both classes. Rule A and the two-stage batch of "
            "this package were worked out, counted and checked for the class of the package only, and that is a second "
            "reason why the other class is not used. ")
    text = read(FOLLOWUP / "pinB4_rules.txt") or ""
    greedy = re.search(r"greedy chain of further conditions: (.*)", text)
    if not text.startswith(f"class {best_eta:08x}:") or not greedy:
        return lead + f"For {hx(best_eta)} no rule of this kind is reported here. "
    # "N conditions keep 1.000000" is a share printed with six decimals, not "all". How many conditions hold for
    # every counted solution is the number of entries of the line RULE_A_ALL and nothing else.
    keeps = [(int(n), k) for n, k in re.findall(r": (\d+) conditions keep ([\d.]+)", greedy.group(1))]
    every = re.search(r"^RULE_A_ALL (\S+)$", text, re.M)
    n_all = len(every.group(1).split(",")) if every else None
    full = max((n for n, k in keeps if k == "1.000000"), default=None)
    nxt = dict(keeps).get(full + 1) if full else None
    if not full or nxt is None or n_all is None or n_all > full:
        return lead + f"For {hx(best_eta)} no rule of this kind is reported here. "
    rest = full - n_all
    return (lead + f"For {hx(best_eta)} the thread that found rule A reports, from the same split of the E3 counts by the "
            f"bits of h1, {WORDS[full]} conditions that keep 1.000000 of the counted rate of its list, to six decimals. "
            + (f"{WORDS[n_all].capitalize()} of them hold for every counted solution; the other {WORDS[rest]} are violated by "
               f"counted solutions, which carry less than 0.000001 of the rate. " if rest else
               "All of them hold for every counted solution. ")
            + f"The best further condition that it found keeps {math.floor(float(nxt) * 1000) / 1000:.3f} of the rate. With "
            f"{WORDS[full]} conditions a trial passes with probability 2^-{full}, so that more batches would run stage 2 "
            f"than here; no batch was written or counted for that class, and no claim is derived for it. ")


def draft_tokens(d, t):
    """What changed against the unfiled draft that this package extends (DRAFT_BEFORE), from that draft's claim.json."""
    text = read(RESEARCH / DRAFT_BEFORE / "blake3-r2" / "claim.json")
    out = {"draft_present": "no", "draft_note": ""}
    if not text:
        return out
    c = json.loads(text)
    flat = " ".join(c["restrictions"]) + " " + " ".join(h["statement"] + " " + h["scope"] + " " + h["extrapolation"]
                                                        for h in c["heuristics"])
    charge = re.search(r"a batch is (\d+) operations .*? plus (\d+) loads and is charged, .*?, as (\d+) per trial", flat)
    count = re.search(r"the count is ([\d,]+) times the uniform expectation", flat)
    factor = re.search(r"\(2\^(\d+) = [\d,]+ times the rate of a uniform 128-bit value\)", flat)
    same = (charge and count and factor and int(charge.group(3)) == PREVIOUS_CHARGE and count.group(1) == t["exact_total"]
            and int(factor.group(1)) == LOG2_FACTOR and c["submission_state"] == "draft"
            and f"eta = {hx(ETA)}" in flat)
    if not same:
        return out
    before = c["claim"]["time_log2"]
    out["draft_present"] = "yes"
    out["draft_time"] = f"{before:.1f}"
    out["draft_note"] = (
        f"An earlier version of this package was prepared and not filed. It has the same constants, the same class "
        f"(eta = {hx(ETA)}), the same count of {t['exact_total']} and the same assumed factor 2^{LOG2_FACTOR}, a batch of one "
        f"stage with {charge.group(1)} operations and {charge.group(2)} loads, {PREVIOUS_CHARGE} charged operations per trial, "
        f"and time_log2 {before:.1f}. Against it, four things are new here. (1) The batch has two stages: stage A, "
        f"{t['stage_a_total']} operations with its loads, tests rule A, {t['rule_conditions']} bit conditions on one "
        f"internal word; only a batch in which a trial passes runs stage 2, {t['stage_2_total']} operations. A trial is "
        f"charged {t['charge']} operations, which lowers the claim by {before - d['time_log2']:.1f} to {t['time_log2']}. "
        f"(2) The test of the second stage is another necessary condition, on one of the two calls alone (Lemma N), in "
        f"place of the early test of Lemma E. (3) Rule A is not implied by a collision, so the figure that H1 is set "
        f"against is smaller: {t['rule_count']}, the count without every outcome for which the solver found a solution "
        f"that violates rule A ({t['rule_bad']} of {t['rule_outcomes']} outcomes, {t['rule_lost']} of the count). "
        f"(4) A third heuristic, H3, is declared: at most {t['stage2_share_words']} of the batches enter stage 2, with a "
        f"budget that the algorithm enforces. The budget on the passes of the second test is now 2^-{PASS_SHIFT} of the "
        f"trials, and H2 and H3 are each allowed a failure probability of 0.0005. The declared advice is "
        f"2^{ADVICE_LOG2} bytes, because the three constants of rule A are stored with the six constants and eta.")
    return out


def rule_text_all():
    """One wording per condition of rule A, in the order of PART A (for naming the conditions that fail)."""
    out = []
    for mask, value in RULE_A[ETA]:
        bits = [i for i in range(32) if mask >> i & 1]
        out.append(f"\"bit {bits[0]} is {value}\"" if len(bits) == 1 else
                   f"\"bits {bits[0]} and {bits[1]} {'differ' if value else 'are equal'}\"")
    return out


def read_followup_real():
    """The follow-up's real trials in the layout of the algorithm, for the class and the rule of the package:
    [(log2 trials, trials that satisfy rule A, trials that pass the E1 test, early-test passes)] per run, or []."""
    text = read(FOLLOWUP / "real32_pinB3.txt") or ""
    pin = " ".join(hx(PIN[k]) for k in ("X3", "X7", "X11", "X15", "W4", "W13"))
    runs = []
    for block in text.split("real: pin ")[1:]:
        if not block.startswith(f"{pin}  eta {ETA:08x}"):
            continue
        m = re.search(r"STAT real trials 2\^([\d.]+)  bad 0\nSTAT real early test passes: (\d+) .*?E1 requires the eta of Y4: (\d+) .*?"
                      r"contradictions \(must be 0\): 0\nSTAT real pass A6: (\d+) ", block)
        if m:
            runs.append((float(m.group(1)), int(m.group(4)), int(m.group(3)), int(m.group(2))))
    return runs


def read_followup_rules():
    """From the follow-up's split of the E3 counts by the bits of h1 (pinB3_rules.txt): (outcomes, betas, rate over
    its list, share of that rate kept by the rule of PART A), or None if the file is not for this class and rule."""
    text = read(FOLLOWUP / "pinB3_rules.txt") or ""
    m = re.search(rf"class {ETA:08x}: (\d+) outcomes with E1 probability > 0, (\d+) betas", text)
    s = re.search(r"calculator's exact sum ([\d.]+)", text)
    chain = re.search(r"^RULE_CHAIN (\S+)", text, re.M)
    greedy = re.search(r"greedy chain of further conditions: (.*)", text)
    if not (m and s and chain and greedy):
        return None
    conds = [(int(p.split(":")[0], 16), int(p.split(":")[1])) for p in chain.group(1).split(",")]
    n = len(RULE_A[ETA])
    if set(conds[:n]) != set(RULE_A[ETA]):
        return None
    k = re.search(rf": {n} conditions keep ([\d.]+)", greedy.group(1))
    return k and (int(m.group(1)), int(m.group(2)), float(s.group(1)), k.group(1))


def read_followup_sat():
    """From the follow-up's solver file (pinB3_sat.txt): ({(beta, tau, eps): answer} for its rule A6, (outcomes
    compared with ApproxMC, share of its rate they carry, mean, largest difference) or None)."""
    text = read(FOLLOWUP / "pinB3_sat.txt") or ""
    have = re.search(r"^# rule A6: (\S+)$", text, re.M)
    if not have or set(have.group(1).split(",")) != {f"{m:08x}:{v}" for m, v in RULE_A[ETA]}:
        return {}, None
    ans = {(m.group(3), m.group(1), m.group(2)): m.group(4) for m in re.finditer(
        r"^A6 ([0-9a-f]{8}) ([0-9a-f]{8}) ([0-9a-f]{8}) (SAT|UNSAT)", text, re.M)}
    sel = re.search(r"AMC selection: the (\d+) outcomes with the largest contribution; they carry ([\d.]+) of the rate", text)
    amc = re.search(r"SUMMARY approxmc: (\d+) outcomes with the largest contribution, (\d+) answered; log2\(exact / approxmc\): mean "
                    r"([-+\d.]+), largest \|difference\| ([\d.]+)", text)
    return ans, (sel and amc and (int(amc.group(2)), sel.group(2), amc.group(3), amc.group(4)))


def read_followup_toy():
    """The follow-up's scaled-down runs with staged tests: per word size (series, predicted, observed, series in which
    every check line is clean, largest |deviation| of a series in Poisson standard deviations)."""
    out = {}
    for bits, name in ((8, "toy2_8.txt"), (10, "toy2_10.txt")):
        text = read(FOLLOWUP / name)
        if text is None:
            continue
        res = [(float(a), int(b)) for a, b in re.findall(r"with A and B: predicted ([\d.]+) observed (\d+)", text)]
        plain = [(float(a), int(b)) for a, b in re.findall(r"no rejection: predicted ([\d.]+) observed (\d+)", text)]
        clean = len(re.findall(r"Y4 wrong 0; .*collisions failing C 0; failing the old test 0; trials where a test word differs from "
                               r"its residual identity 0; hits failing the full-hash check 0", text))
        every = all(a == b for pair in re.findall(r"collisions per seed \(all / passing A and B\): (.*)", text)
                    for a, b in (x.split("/") for x in pair.split()))
        conds = [int(v) for v in re.findall(r"A2: (\d+) XOR conditions hold for all the class mass", text)]
        subs = re.findall(r"RESULT W=\d+ T=(\d+)/(\d+) ka=-1 useb=2 ", text)
        pins = set(re.findall(rf"{bits}-bit words; pin ([0-9a-f ]+);", text))
        if res and res == plain and every and len(conds) == len(subs) == len(res):
            out[bits] = (len(res), sum(p for p, _ in res), sum(o for _, o in res), clean,
                         max(abs(o - p) / math.sqrt(p) for p, o in res), conds, sum(a != b for a, b in subs), len(pins))
    return out


def read_followup_batch():
    """The follow-up's run of its own two-stage batch for this class (JSON line of night_batch4.py), or None."""
    text = read(FOLLOWUP / "batch4_two_class_filed_1200000_s51.json")
    if text is None:
        return None
    r = json.loads(text)
    same = (r["eta"] == hx(ETA) and r["pin"] == [hx(PIN[k]) for k in ("X3", "X7", "X11", "X15", "W4", "W13")]
            and sorted(r["A_rule_on_h1"]) == sorted(f"{m:08x}:{v}" for m, v in RULE_A[ETA]) and r["all_checks_pass"]
            and r["B_test"].startswith("none") and r["convention"] == "filed")
    return r if same else None


def read_big_selftests():
    """[(cases, seed, JSON)] of tools/selftest_big.sh for the program as it is now (same SHA-256, exit status 0)."""
    import hashlib
    now = hashlib.sha256(PROGRAM.read_bytes()).hexdigest()
    out = []
    for path in sorted(EVID.glob("selftest_*_*.json")):
        lines = path.read_text(encoding="ascii", errors="replace").split("\n")
        m = re.match(r"PROGRAM sha256 ([0-9a-f]{64}) exit (\d+) seconds (\d+)", lines[0])
        if m and m.group(1) == now and m.group(2) == "0" and len(lines) > 1 and lines[1].startswith("{"):
            r = json.loads(lines[1])
            out.append((r["cases"], str(r["seed"]), r))
    return out


def followup_tokens(d, st):
    """Section 10 on the two-stage batch: lanes checked, pass rates of rule A on real trials, the checks of the
    rule by the thread that found it, and the scaled-down runs with staged tests. Every figure is read from a file."""
    t = {}
    # ---- lanes checked
    big = read_big_selftests()
    for cases, seed, r in big:
        if not (r["lanes_right"] == r["lanes_checked"] == 7 * cases and r["counts_equal_table"] and r["same_counts_in_every_case"]
                and r["sums_below_bounds"] and r["zero_lane_patterns_right"] == 128 and r["rule_a_patterns_right"] == 256
                and (r["stage_a"], r["stage_2"]) == (st["stage_a"], st["stage_2"])):
            raise SystemExit(f"a long self-test run does not report what the text states: evidence/selftest_{cases}_{seed}.json")
    if big:
        lanes = sum(7 * c for c, _, _ in big)
        passing = sum(r["lanes_passing_rule_a"] for _, _, r in big)
        entered = sum(r["batches_entering_stage_2"] for _, _, r in big)
        cases = sum(c for c, _, _ in big)
        zero = sum(r["zero_test_words"] for _, _, r in big)
        top = max(r["largest_lane"] for _, _, r in big)
        t["big_selftest_sentence"] = (
            f"Longer runs of the same self-test, {join(f'N = {num(c)} with seed {s}' for c, s, _ in big)}, report "
            f"{num(lanes)} of {num(lanes)} lanes right and the same counts in every batch; {num(passing)} lanes pass rule "
            f"A, which is a share of 2^{math.log2(passing / lanes):.3f}, in {num(entered)} of the {num(cases)} batches, "
            f"a share of {entered / cases:.4f} (every fourth batch of the self-test is the last batch of the class, whose "
            f"seven lanes hold only {WORDS[d['rest']] if d['rest'] else 'seven'} different members, so this share is below that of a run); "
            f"{'no' if zero == 0 else num(zero)} stage-2 test word is zero; the largest lane of a sum is {top / 2 ** 32:.3f} "
            f"times 2^32, and at most {max(r['registers'] for _, _, r in big)} registers are in use.")
        t["big_lanes"], t["big_runs"] = num(lanes), str(len(big))
        t["big_note"] = f"{num(lanes)} lanes in longer runs of the program's self-test"
        t["big_claim"] = f", and {num(passing)} of {num(lanes)} in longer runs"
    else:
        t["big_selftest_sentence"] = "No longer run of the self-test of this program is reported here."
        t["big_lanes"], t["big_runs"], t["big_note"], t["big_claim"] = "0", "0", "", ""
    fb = read_followup_batch()
    if fb:
        t["research_batch_sentence"] = (
            f"The batch was first written and counted in the research program in which rule A was found, with the same "
            f"machine and the same primitives: {num(fb['lanes_checked'])} lanes of this class, each compared with the "
            f"complete digests of its two messages, all right; {fb['stage_A']['operations']} operations and "
            f"{fb['stage_A']['loads']} loads for stage A and {fb['stage_B']['operations'] + fb['stage_C']['operations']} and "
            f"{fb['stage_B']['loads'] + fb['stage_C']['loads']} for the rest, which is the stage 2 of this package without "
            f"the count of its own entry; {num(fb['lanes_passing']['A'])} lanes passed rule A, in "
            f"{num(fb['batches_entering']['stage_B'])} of {num(fb['cases'])} batches.")
        t["research_lanes"] = num(fb["lanes_checked"])
    else:
        t["research_batch_sentence"] = ""
        t["research_lanes"] = "0"

    # ---- rule A on real trials
    runs = read_followup_real()
    if not runs:
        raise SystemExit("no real-trial run with the pass rate of rule A for this class: H3 has no measured rate "
                         "(evidence/followup/real32_pinB3.txt)")
    lg = {r[0] for r in runs}
    if len(lg) != 1:
        raise SystemExit("the real-trial runs of rule A do not have one size")
    per = 2.0 ** lg.pop()
    n = len(runs)
    total_trials = n * per
    count = sum(r[1] for r in runs)
    p = 2.0 ** -d["rule_conditions"]
    sd = math.sqrt(per * p * (1 - p))
    devs = [(r[1] - per * p) / sd for r in runs]
    rate = math.log2(count / total_trials)
    share = Fraction(1, 2 ** STAGE_2_LOG2_SHARE)
    measured_share = 7 * count / total_trials
    t.update(a_runs=WORDS[n] if n < len(WORDS) else str(n), a_run_trials=f"{math.log2(per):.0f}",
             a_trials=f"{math.log2(total_trials):.0f}", a_count=num(count), a_rate=f"{rate:.4f}",
             a_counts=join(num(r[1]) for r in runs), a_expected=num(per * p),
             a_devs=join(z_text(z) for z in devs), a_dev_sum=z_text((count - total_trials * p) / math.sqrt(total_trials * p * (1 - p))),
             a_rel=f"{max(abs(r[1] / (per * p) - 1) for r in runs):.1e}",
             a_share=f"{up(measured_share, 5):.5f}",
             a_margin=f"{math.floor(1000 * float(share) / measured_share) / 1000:.3f}",
             a_e1_passes=num(sum(r[2] for r in runs)), a_e1_rate=f"{math.log2(sum(r[2] for r in runs) / total_trials):.2f}",
             a_early_passes=num(sum(r[3] for r in runs)))
    if float(share) / measured_share < 1.05:
        raise SystemExit("the stage-2 budget is less than 5% above seven times the measured pass rate of rule A")

    # ---- rule A and the stage-2 entries in the layout of 6.4 itself (two programs of a reviewing helper agent, run
    #      again with tools/rule_share.sh and tools/rule_share_seeds.py); every figure is recomputed from their lines
    lay, sds = read_rule_share(d), read_rule_share_seeds(d)
    budget = float(share)
    gpu_sentence = (
        f"{t['a_runs'].capitalize()} longer runs of 2^{t['a_run_trials']} trials each, laid out like those of the algorithm "
        f"with the differences stated in Section 10, have a share of trials of 2^{t['a_rate']}; seven times it is at most "
        f"{t['a_share']}, and the budget is larger by a factor of {t['a_margin']}.")
    for key in ("lay_paragraph", "lay_note", "h3_layout_claim", "h3_layout_limit", "h3_spread_layout", "seeds_paragraph",
                "seeds_note", "h3_seeds_claim"):
        t[key] = ""
    t["h3_measured_sentence"] = (
        f"On real trials in runs laid out like those of the algorithm, with the differences stated in Section 10, "
        f"{t['a_runs']} runs of 2^{t['a_run_trials']} trials each, the share measured is 2^{t['a_rate']}; seven times it is "
        f"at most {t['a_share']}, and the budget of {WORDS_SHARE[STAGE_2_LOG2_SHARE]} of the batches is larger by a factor of "
        f"{t['a_margin']}.")
    t["h3_seeds_limit"] = f"{t['a_runs'].capitalize()} runs cannot exclude seed words for which it has."
    t["h3_exclude_claim"] = f", and {t['a_runs']} runs cannot exclude seed words for which it has."
    t["lay_state"], t["seeds_state"] = "none", "none"
    if lay:
        lg = int(math.log2(lay["trials"]))
        smin, smax, bmin, bmax = min(lay["share"]), max(lay["share"]), min(lay["batch"]), max(lay["batch"])
        margin = math.floor(1000 * budget / bmax) / 1000
        if budget / bmax < 1.05:
            raise SystemExit("the stage-2 budget is less than 5% above the largest measured share of batches in the layout of 6.4")
        below = bmax < lay["independent"]
        loose = lay["batch_chi"] > lay["runs"] - 1 + 4 * math.sqrt(2 * (lay["runs"] - 1))       # more than 4 sd above its mean
        rel = 100 * (bmax - bmin) / lay["batch_all"]
        t["lay_state"] = f"{lay['runs']} samples of 2^{lg}"
        t["lay_paragraph"] = (
            f"The layout of 6.4 itself was measured on a CPU, with a program that a reviewing helper agent wrote from "
            f"Sections 4 and 6 and that was run again for this text. It computes the word z of Lemma A for every trial in "
            f"scalar arithmetic. On {num(lay['vectors'])} random trials its z and its verdict on rule A are those of the "
            f"complete compression of the real message A"
            + (", whose digest is that of the organizer's reference hash" if lay["with_reference"] == lay["vectors"] else "")
            + f". A sample has four seed words of its own and X1 = X10 = 0 as in step 1, {num(lay['contexts'])} contexts "
            f"drawn at random with X12 below 2^{LOG2_X12} and X13 below 2^{d['x13']}, {lay['alphas']} random values of alpha "
            f"for each of them, and for every pair of a context and an alpha all {num(d['members'])} members of the class "
            f"in the order of their numbers, seven to a batch: 2^{lg} trials in {num(lay['batches'])} batches. So contexts "
            f"and values of alpha are sampled, and every class loop is complete. In {lay['runs']} samples the share of "
            f"trials that satisfy rule A lies between {smin:.6f} and {smax:.6f} times 2^-{d['rule_conditions']}, and is "
            f"{lay['share_all']:.6f} times that over all of them; the chi-square of the {lay['runs']} counts against "
            f"2^-{d['rule_conditions']} is {lay['chi']:.1f} on {lay['runs']} degrees of freedom. The share of batches that "
            f"run stage 2 lies between {bmin:.6f} and {bmax:.6f} and is {lay['batch_all']:.6f} over all samples; the budget "
            f"of {budget:.3f} is {margin:.3f} times the largest. "
            + (f"In every sample it is below 1 - (1 - 2^-{d['rule_conditions']})^7 = {lay['independent']:.6f}, the value "
               f"for seven independent trials: trials of one batch tend to satisfy rule A together, which lowers the number "
               f"of batches. " if below else "")
            + (f"The {lay['runs']} batch counts differ from each other by more than binomial counts with a common share "
               f"would (chi-square {lay['batch_chi']:,.0f} on {lay['runs'] - 1} degrees of freedom); the largest exceeds the "
               f"smallest by {rel:.2f}% of the common share. So this count depends on the sample, that is on the seed "
               f"words or on the contexts drawn; the cause was not examined." if loose else
               f"The {lay['runs']} batch counts are compatible with a common share (chi-square {lay['batch_chi']:.1f} on "
               f"{lay['runs'] - 1} degrees of freedom)."))
        t["h3_measured_sentence"] = (
            f"On real trials in the layout of 6.4, with contexts and values of alpha sampled and every class loop "
            f"complete, {lay['runs']} samples of 2^{lg} trials each have a share of trials that satisfy rule A between "
            f"{smin:.6f} and {smax:.6f} times 2^-{d['rule_conditions']} and a share of batches that run stage 2 of at "
            f"most {bmax:.6f}; the budget of {WORDS_SHARE[STAGE_2_LOG2_SHARE]} of the batches is larger by a factor of "
            f"{margin:.3f}. " + gpu_sentence)
        t["h3_layout_claim"] = (
            f" In the layout of the algorithm itself, with contexts and alphas sampled and every pass over the class "
            f"complete, {lay['runs']} samples of 2^{lg} trials gave shares of trials between {smin:.6f} and {smax:.6f} "
            f"times 2^-{d['rule_conditions']} and shares of batches that run stage 2 between {bmin:.6f} and {bmax:.6f}, "
            f"against the budget of {budget:.3f}")
        t["h3_layout_limit"] = (f"; on {lay['runs']} samples of 2^{lg} trials in the layout of 6.4, whose shares of batches "
                                f"that run stage 2 are at most {bmax:.6f}")
        t["h3_spread_layout"] = (
            f" The number of batches that run stage 2 differs between the samples in the algorithm's layout by more than "
            f"chance; the largest exceeds the smallest by {rel:.2f}% of the common share." if loose else "")
        t["lay_note"] = (
            f"In the layout of the algorithm itself, on a CPU with contexts sampled and every pass over the class "
            f"complete, {lay['runs']} samples of 2^{lg} trials have a share of trials between {smin:.6f} and {smax:.6f} "
            f"times 2^-{d['rule_conditions']} and a share of batches that run stage 2 between {bmin:.6f} and {bmax:.6f} "
            f"(budget {budget:.3f}); the program is a reviewing helper agent's, run again for this note.")
    if sds:
        if sds["over"]:
            raise SystemExit("a set of seed words has a sampled share of batches at or above the stage-2 budget: H3 must be restated")
        # exclude: the share q with (1 - q)^sets = 0.05, to first order. excl is rounded up (a bound "about"), excl_low
        # is rounded down, and (1 - excl_low)^sets is still above 0.05, which is checked
        e10 = math.floor(math.log10(sds["exclude"]))
        excl = f"{up(sds['exclude'] / 10 ** e10, 1):.1f} * 10^{e10}"
        low = math.floor(sds["exclude"] / 10 ** e10 * 10) / 10
        excl_low = f"{low:.1f} * 10^{e10}"
        if not (1 - low * 10 ** e10) ** sds["sets"] > 0.05:
            raise SystemExit("the share of sets of seed words that the sample cannot exclude is misstated")
        t["seeds_state"] = f"{num(sds['sets'])} sets of seed words with 2^{sds['log2']} sampled batches each"
        t["seeds_paragraph"] = (
            f"A second program of a reviewing helper agent, also run again for this text, takes many sets of seed words "
            f"and, for each, a random sample of the batches of the run that 6.4 defines for it: X1 = X10 = 0, X12 below "
            f"2^{LOG2_X12}, X13 below 2^{d['x13']}, and a context, a value of alpha and a position in the class drawn at "
            f"random for every batch. It computes h1 for the seven trials of a batch; for {num(sds['checked'])} trials "
            f"its h1 was compared with that of the complete compression of the real message, and none differs. For "
            f"{num(sds['sets'])} sets of seed words with 2^{sds['log2']} batches each, {num(sds['lanes'])} trials in all, "
            f"the share of trials that satisfy rule A is 2^{sds['rate']:.4f} ({z_text(sds['dev'])} standard deviations of "
            f"a binomial count from 2^-{d['rule_conditions']}). Per set it lies between {sds['lane_min']:.4f} and "
            f"{sds['lane_max']:.4f} times 2^-{d['rule_conditions']}, where one binomial standard deviation of a set is "
            f"{sds['lane_sd']:.4f} and H3 needs less than {math.floor(sds['lane_need'] * 1e4) / 1e4:.4f}; the chi-square "
            f"of the sets against 2^-{d['rule_conditions']} is {sds['chi']:,.1f} on {num(sds['sets'])} degrees of freedom. "
            f"The share of batches that run stage 2 is {sds['batch_all']:.5f} over all sets and between "
            f"{sds['batch_min']:.5f} and {sds['batch_max']:.5f} per set (chi-square against the common share "
            f"{sds['batch_chi']:,.1f} on {num(sds['sets'] - 1)}); no set reaches the budget of {budget:.3f}. A set here is "
            f"a sample of 2^{sds['log2']} batches of a run, not a run.")
        t["h3_seeds_limit"] = (
            f"Of {num(sds['sets'])} sets of seed words, each sampled with 2^{sds['log2']} batches, none reached the budget; "
            f"the largest share of batches was at most {up(sds['batch_max'], 4):.4f}. If a share q of all sets of seed words gave "
            f"a sample at or above the budget, none among {num(sds['sets'])} would have probability (1 - q)^{sds['sets']}, "
            f"which is still above 0.05 for q = {excl_low}. So sets of seed words that rare are not excluded, and a "
            f"sample of 2^{sds['log2']} batches is not a run.")
        t["h3_exclude_claim"] = (
            f". None of {num(sds['sets'])} sets of seed words, each sampled with 2^{sds['log2']} batches, reached the "
            f"budget; that bounds the share of such sets by about {excl} at 95% confidence and does not exclude rarer "
            f"ones, and a sample of that size is not a run.")
        t["h3_seeds_claim"] = (
            f"; over {num(sds['sets'])} sets of seed words with 2^{sds['log2']} sampled batches each the share of batches "
            f"was {sds['batch_all']:.5f} in all and at most {up(sds['batch_max'], 4):.4f} for one set")
        t["seeds_note"] = (
            f"Over {num(sds['sets'])} sets of seed words, 2^{sds['log2']} sampled batches each, the share of batches that "
            f"run stage 2 is {sds['batch_all']:.5f} in all and at most {up(sds['batch_max'], 4):.4f} for one set.")
    t["h3_note_more"] = (", on samples of real trials in the algorithm's own layout" if lay or sds else "")
    if t["h3_layout_claim"] or t["h3_seeds_claim"]:
        t["h3_layout_claim"] = ((t["h3_layout_claim"] or " In the layout of the algorithm itself") + t["h3_seeds_claim"]
                                + " (programs of a reviewing helper agent, run again by the participant).")

    # ---- what rule A keeps, counted exactly for a shorter list; ApproxMC; the solver answers of the other thread
    fr = read_followup_rules()
    # the shorter list of that thread: the night's own per-beta file (the snapshot), if its sum is the sum of that thread
    short_rows = read_total(ETA, longest=False)
    short_sum = sum(r[3] for r in short_rows if r[3])
    short_list = (f"the {num(len(short_rows))} lightest" if fr and abs(short_sum - fr[2]) < 1.0 else "a shorter list of")
    t["rule_split_sentence"] = (
        f"How much of the rate rule A really keeps was counted for a shorter list. The thread that found the rule split "
        f"the E3 count of every outcome by the bits of h1, with a program of its own, for the {fr[0]} outcomes of the "
        f"{fr[1]} betas with a part among {short_list} betas, whose parts add up to {num(fr[2])}: rule A keeps {fr[3]} of "
        f"that sum. The figure that the claim uses keeps less, because it gives up in full every outcome for which a "
        f"violating solution was found." if fr else
        "How much of the rate rule A really keeps, outcome by outcome, was not counted for this class and rule.")
    t["rule_split_kept"] = fr[3] if fr else "not counted"
    ans, amc = read_followup_sat()
    mine = {k: v["VIOLATE"][0] for k, v in read_rule_sat()[0].items()}
    if ans:
        if any(mine.get(k) != v for k, v in ans.items()):
            raise SystemExit("the solver answers of the follow-up thread and of tools/rule_a_sat.py differ for an outcome")
        t["rule_sat_other"] = (
            f"The same question had been put to the solver before, by the thread that found the rule, for the {len(ans)} "
            f"outcomes of that shorter list: its answers, {sum(v == 'UNSAT' for v in ans.values())} without and "
            f"{sum(v == 'SAT' for v in ans.values())} with a violating solution, are the same as those above for every one "
            f"of these outcomes.")
    else:
        t["rule_sat_other"] = ""
    t["rule_amc_sentence"] = (
        f"That thread also compared the E3 count N3 with the approximate model counter ApproxMC (tolerance 0.4, "
        f"confidence 0.9) on the CNF of the same E3 system, for the {amc[0]} outcomes with the largest products of its "
        f"list, which carry {amc[1]} of its sum: the mean of log2(N3 / ApproxMC) is {amc[2]} and the largest difference "
        f"{amc[3]} bits." if amc else "")
    t["rule_amc_note"] = (f"ApproxMC agrees with the E3 counts of the {amc[0]} heaviest outcomes within {amc[3]} bit" if amc else "")

    # ---- scaled-down runs with staged tests
    toy = read_followup_toy()
    if toy:
        bits = sorted(toy)
        desc = []
        conds = [c for b in bits for c in toy[b][5]]
        halves, series_all = sum(toy[b][6] for b in bits), sum(toy[b][0] for b in bits)
        for b in bits:
            series, pred, obs, clean, worst = toy[b][:5]
            if clean != series:
                raise SystemExit("a scaled-down run with staged tests reports a failed check (evidence/followup/toy2_*.txt)")
            desc.append(f"with {b}-bit words, {series} series: {num(obs)} collisions against {pred:,.1f} predicted, "
                        f"{z_text((obs - pred) / math.sqrt(pred))} standard deviations of a Poisson count"
                        + (f" (single series up to {worst:.1f})" if series > 1 else ""))
        t["toystage_paragraph"] = (
            "**Scaled-down runs with staged tests (participant computation, other constants).** The thread that found "
            "rule A repeated the scaled-down class search of the kind described above with tests placed in front of the "
            "residual computation: a rule on the bits of h1, a rule on beta, and the E1 test of Lemma N, on the toy hash "
            "described above, with " + join(f"{WORDS[toy[b][7]]} constant set{'s' if toy[b][7] != 1 else ''} at {b} bits" for b in bits)
            + ". The rule on h1 used there is not rule A. It is made of the XOR "
            "conditions on bits of h1 that every solution of the class satisfies, found by brute force for each constant "
            f"set; there are between {WORDS[min(conds)]} and {WORDS[max(conds)]} of them, and such a rule loses nothing. "
            f"{WORDS[halves].capitalize()} of the {WORDS[series_all] if series_all < len(WORDS) else series_all} series also "
            "restrict Y4 to half of the class, and all use the rule on beta; this package does neither. A trial "
            "that fails a test is dropped, and the prediction is the brute-force count of the solutions that pass. "
            "Results: " + "; ".join(desc) + ". In every series every collision found passed the rules and the E1 test, "
            "the E1 test word of every trial was equal to the word D3 XOR ROL(D6, r) of its residual, where r is the toy's "
            "third rotation (Lemma N for the toy hash), no "
            "trial had a Y4 outside its class, and no collision failed the full re-hash. These runs test the logic of "
            "dropping trials early and Lemma N, end to end and down to collisions, at small word sizes. They do not test "
            "rule A of this package, which has six conditions and loses solutions, and they are not evidence about its "
            "constants.")
        t["toystage_note"] = ("scaled-down runs with staged tests of the lossless kind: "
                              + "; ".join(f"{num(toy[b][2])} collisions against {toy[b][1]:,.1f} predicted at {b} bits" for b in bits))
        t["toystage_claim"] = (" Scaled-down runs with tests in front of the residual, a lossless rule on h1 and the "
                               "E1 test, found " + " and ".join(f"{num(toy[b][2])} collisions against {toy[b][1]:,.1f} predicted at {b} bits"
                                                              for b in bits) + "; they do not test rule A itself.")
    else:
        t["toystage_paragraph"], t["toystage_note"], t["toystage_claim"] = "", "", ""
    return t


def main():
    if "--recount-env" in sys.argv:
        d = derive()
        rows, listed, extra, _, _ = exact_table(d)
        print(f"D3={hx(d['DY3'])} D11={hx(d['DY11'])} DELTA={hx(d['delta'])} Y3={hx(d['Y3'])} Y11={hx(d['Y11'])} ETA={hx(ETA)}")
        print('BETAS="' + " ".join(b for _, b, _, _ in listed + extra) + '"')
        return 0
    d, t = build_tokens()
    for k in sorted(t):
        v = t[k]
        print(f"{k:24s} {v if len(v) < 150 and chr(10) not in v else v[:140].replace(chr(10), ' / ') + ' ...'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
