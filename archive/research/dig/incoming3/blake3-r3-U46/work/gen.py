"""gen.py - writes the 72 cell records (units U46-U54) from steps_out.json, words_out.json, tail_out.json."""
import json, os, sys
from fractions import Fraction
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from b3scan import time_log2
from exp_steps import ih_tail
W = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(W, "steps_out.json")))
WD = json.load(open(os.path.join(W, "words_out.json")))
T = json.load(open(os.path.join(W, "tail_out.json")))
ROOT = os.path.abspath(os.path.join(W, "..", ".."))        # research/dig/incoming3
D = "research/dig/incoming3/blake3-r3-U46/work/"
EV_STEP = (D + "b3scan.py; " + D + "exp_steps.py; " + D + "steps_out.json; research/blake3_r3/candidate_blake3/experiments/rho.py (ledger formula)")
EV_TAIL = D + "exp_tail.py; " + D + "tail_out.json"
EV_WORD = (D + "b3scan.py; " + D + "exp_words.py; " + D + "words_out.json; research/blake3_r3/candidate_blake3/experiments/rho.py (ledger formula)")
VAL = ("Tools first reproduced: 7-round empty-input vector af1349b9...f3262 and verifier blake3.py (rounds 1,2,3,5,7 on 40 random blocks each, "
       "3-round 0^32||x on 100 inputs, all equal); traced circuit = 595 ops and time_log2 125.10856 (shipped), 0 mismatches vs scalar on 200 inputs.")
ONE_OP = time_log2(595) - time_log2(594)
N_SAMP = T["samples"]
UNIT = {"R2D2.q3": "blake3-r3-U46", "R2D2.q4": "blake3-r3-U46", "R2D3.q1": "blake3-r3-U47", "R2D3.q2": "blake3-r3-U47",
        "R2D3.q3": "blake3-r3-U48", "R2D3.q4": "blake3-r3-U48"}
WUNIT = {0: 49, 1: 49, 2: 50, 3: 50, 4: 51, 5: 51, 6: 52, 7: 52, 8: 53, 9: 53, 10: 54, 11: 54}
count = 0


def put(unit, cell, rec):
    global count
    rec.update({"hash": "blake3-r3", "row_i": None, "row_j": None, "source": "our workflow: dig-scan-b3r3", "own_test": True,
                "date": "2026-10-12", "topic": cell})
    rec.setdefault("lever", False)
    rec.setdefault("gain_bits", None)
    rec.setdefault("labels", ["N"])
    d = os.path.join(ROOT, unit)
    os.makedirs(d, exist_ok=True)
    json.dump(rec, open(os.path.join(d, cell.replace("|", "_") + ".json"), "w"), indent=1)
    count += 1


def site(tag, nv=16):
    for s in T["sites"].values():
        if tuple(s["tag"]) == tag and s["nv"] == nv:
            return s


def tailbound(tag):
    s = site(tag)
    c = {int(t): v / N_SAMP for t, v in s["cnt"].items()}
    rmin = min(c[t] / c[t + 1] for t in (10, 11, 12) if c[t + 1] > 0)
    return s, c, rmin, c[13] / rmin ** 3


DESC = {
    "R2D2.q3": ("round 2, call D2 = G(2,7,8,13), quarter-step q3: a = a + b + y; d = ror8(d ^ a), y = m15 (a chain word)", (2, 6, 3)),
    "R2D2.q4": ("round 2, call D2 = G(2,7,8,13), quarter-step q4: c = c + d; b = ror7(b ^ c)", (2, 6, 4)),
    "R2D3.q1": ("round 2, call D3 = G(3,4,9,14), quarter-step q1: a = a + b + x; d = ror16(d ^ a), x = m8 (a chain word)", (2, 7, 1)),
    "R2D3.q2": ("round 2, call D3 = G(3,4,9,14), quarter-step q2: c = c + d; b = ror12(b ^ c)", (2, 7, 2)),
    "R2D3.q3": ("round 2, call D3 = G(3,4,9,14), quarter-step q3: a = a + b + y; d = ror8(d ^ a), y = m1 (a ZERO word: its add is not emitted)", (2, 7, 3)),
    "R2D3.q4": ("round 2, call D3 = G(3,4,9,14), quarter-step q4: c = c + d; b = ror7(b ^ c)", (2, 7, 4)),
}
rows = {v["label"]: v for v in S["variants"]}
nm = S["nomask"]
for loc, (desc, tag) in DESC.items():
    unit = UNIT[loc]
    ps = S["per_step_round2"][loc]
    sk = S["skip"][loc]
    obj = "step " + loc
    has_mask = ps["and"] > 0
    ops_str = "%d ops (add %d, xor %d, rotation %d [5 ops each: shr,and,shl,and,or], and %d)" % (ps["total"], ps["add"], ps["xor"], ps["rot"], ps["and"])
    q1 = ("%s: %s in the shipped 7-lane, pitch-36 circuit; the circuit totals 595 ops = 100 add + 88 xor + 400 rotation + 7 and "
          "(3 internal masks, all at q3 steps of round 2 calls D1, D2, D3; 4 digest masks); time_log2 125.10856. This step is %.2f%% of the 595 ops. "
          "One op in the ledger is worth %.5f bit of time_log2." % (loc, ops_str, 100.0 * ps["total"] / 595, ONE_OP))
    if has_mask:
        s, c, rmin, pb = tailbound(tag)
        q1 += (" The internal mask is the only mask of this step: the a-chain here is a sum of 16 unreduced 32-bit leaves (worst-case bound %.2f units of 2^32, "
               "lane limit 16 units), so the tracer masks before adding y." % s["bound"])
    put(unit, "blake3-r3|%s|step|Q1" % loc, {
        "object": obj, "question": "Q1: %s - the value/count of this step as used in the filed 125.1087 circuit." % desc,
        "status": "COMPUTED", "number": q1, "evidence": EV_STEP,
        "notes": VAL + " Per-step counts come from our own tracer (b3scan.py) with every emitted op tagged by (round, call, quarter); the tags sum to 595 (digest xor and masks = 12). Matches the 595 and the 3 internal masks of research/blake3_r3/levers_step_count.md.",
        "held_fixed": "filed layout (7 lanes, pitch 36, 4 guard bits), unrolled straight line, constants folded, standard 3-round order and permutation",
        "reopen_if": "the filed circuit changes (lane layout, rotation form) or the organizer's op model changes"})
    skdesc = ("Skipping this quarter-step (a, d or c, b left unchanged) removes %d ops (595 -> %d) and would lower time_log2 by %.4f if it were allowed, "
              "but the function is then no longer 3-round BLAKE3: on 1500 random inputs it differs from the true digest in %.1f of 256 bits on average (%.0f of 8 digest words stay equal, the other %.0f change every time). "
              "So the step is necessary: its output reaches the digest, and none of its emitted ops is dead." % (
                  -sk["delta_ops"], sk["ops"], -sk["delta_time_log2"], sk["mean_digest_bits_changed_of_256"],
                  sk["mean_equal_digest_words_of_8"], 8 - sk["mean_equal_digest_words_of_8"]))
    put(unit, "blake3-r3|%s|step|Q2" % loc, {
        "object": obj, "question": "Q2: %s - necessity: leave the step out and recount the exact outcome (ops, ledger time_log2, digest)." % desc,
        "status": "COMPUTED", "number": skdesc, "evidence": EV_STEP,
        "notes": VAL + " The skipped circuit was traced and checked against the scalar skipped function (0 mismatches of 100). Necessity here is functional (the digest is the required hash), not a search property. The op saving shown is hypothetical, not a lever.",
        "held_fixed": "all other quarter-steps and the digest xor unchanged; same 7-lane layout; inputs 0^32||x random",
        "reopen_if": "the target function changes, or a cheaper circuit for the same step is proposed"})
    if has_mask:
        s, c, rmin, pb = tailbound(tag)
        ih13 = float(ih_tail(s["nv"], Fraction(13) - Fraction(s["cs"])))
        n3 = ("Score-optimal value of the one free choice at this step: the internal mask. With it the step is %d ops; without it %d ops (tracer, 0 mismatches vs scalar on 200 inputs), "
              "a saving of 1 op = %.5f bit of time_log2 (all 3 internal masks: 592 ops, %.5f bit). The mask only protects against a lane sum reaching 2^36. "
              "Sampled on %d random inputs with the mask left out: the unreduced a-chain at this step has mean %.3f units (independent-uniform model %.3f), variance %.2f (model %.2f); "
              "P(sum >= 12 units) = %.2e, P(>= 13) = %.2e, largest seen %.2f units; the lane limit is 16. No overflow in the sample. "
              "The independent-uniform model understates the tail (it gives %.1e at 13), so it is not used. Extrapolating by the smallest observed per-unit tail ratio (%.1f): P(>= 16) <= %.1e per evaluation "
              "(an extrapolation, not a proof). An overflow corrupts that lane and its neighbour, so a point is wrong; cost about 4p of success probability, at most %.1e for this site against the 1.5e-3 margin of the filed entry." % (
                  ps["total"], nm["per_step"][loc], ONE_OP, time_log2(595) - time_log2(592), N_SAMP, s["mean_units"], s["nv"] / 2 + s["cs"], s["var_units"], s["nv"] / 12,
                  c[12], c[13], s["max"] / 2 ** 32, ih13, rmin, pb, 4 * pb))
        put(unit, "blake3-r3|%s|step|Q3" % loc, {
            "object": obj, "question": "Q3: %s - degrees of freedom / score-optimal value (here: is the internal overflow mask needed?)." % desc,
            "status": "SAMPLED", "number": n3, "evidence": EV_STEP + "; " + EV_TAIL,
            "lever": True, "gain_bits": round(ONE_OP, 5), "gain_basis": "T", "labels": ["E"],
            "notes": VAL + " LEVER CANDIDATE, small: dropping the mask is exact except with probability p per evaluation that the unreduced sum reaches 2^36; p is bounded here only by sampling plus a ratio extrapolation. Sampling: 51 chunks of 2^20 random inputs (5.3e7), one process, under 5 min. research/blake3_r3/levers_step_count.md called this idea a GUESS that it is false and did not test it; the sampled tail stays well under 16 units (max 14.9). Not filing-ready: needs a rigorous bound (exact chain distribution or importance sampling) and a ledger line for the added failure probability. Gain counts this site only; the three sites together are 0.0072 bit.",
            "held_fixed": "same circuit except the mask at q3 of round 2 call %s; all other masks (160 in rotations, 4 digest masks, the other two internal masks) kept" % loc[3:5],
            "reopen_if": "an importance-sampled or exact distribution of this chain puts P(sum >= 16 units) below 1e-6 (then file the saving), or above 1e-3 (then close)"})
    else:
        others = ", ".join("%s: %d" % (v["label"].split(" (")[0], v["steps"][loc]) for v in S["variants"][1:5])
        put(unit, "blake3-r3|%s|step|Q3" % loc, {
            "object": obj, "question": "Q3: %s - degrees of freedom / score-optimal value." % desc,
            "status": "COMPUTED",
            "number": ("No free parameter at this step in the op model: the rotation amount is fixed by the spec, the operand order does not change the op count, and the step has no internal mask. "
                       "It costs %d ops in the shipped layout and %d ops with all internal masks dropped; other layouts give %s. So %d ops is the score-optimal value found; "
                       "a cheaper-by-one-op case exists only at q3 steps (the internal masks)." % (ps["total"], nm["per_step"][loc], others, ps["total"])),
            "evidence": EV_STEP,
            "notes": VAL + " Only layouts and mask policies were varied (pitch 35, 34, no internal masks, 6/5/4 lanes). The 5-op rotation form and the constant folding were not re-searched; research/blake3_r3/levers_step_count.md reports no saving in its parts (a)-(d) and its brute force over mask choices was not re-run.",
            "held_fixed": "spec rotation amounts, add order a+b+m, xor then rotate; ledger formula of rho.py",
            "reopen_if": "a rotation form under 5 ops for a 36-pitch lane is found, or a merged xor+rotate form"})
    parts = []
    for lab in ("pitch35 x7 (guard 3)", "pitch34 x7 (guard 2)", "pitch36 x7 no internal masks (policy none)", "pitch42 x6", "SWAR pitch32 x8 (6-op masked add)"):
        v = rows[lab]
        parts.append("%s: this step %d ops, circuit %d ops (%.2f per evaluation, time_log2 %.4f)" % (lab, v["steps"][loc], v["ops"], v["ops_per_lane"], v["time_log2_equiv"]))
    put(unit, "blake3-r3|%s|step|Q4" % loc, {
        "object": obj, "question": "Q4: %s - alternatives: the same step in other lane layouts, counted exactly." % desc,
        "status": "COMPUTED",
        "number": ("Shipped pitch36 x7: this step %d ops, circuit 595 (85.00 per evaluation, time_log2 125.1086). Alternatives (exact tracer counts): " % ps["total"]
                   + "; ".join(parts) + ". Only 'no internal masks' is cheaper than shipped, by 3 ops per batch (0.0072 bit); see the Q3 cells of D2.q3 and D3.q3. "
                   "Fewer lanes cost more per evaluation (5 lanes 118.4, 4 lanes 148); fewer guard bits add masks (pitch 35: 603 ops, pitch 34: 622)."),
        "evidence": EV_STEP,
        "notes": VAL + " time_log2 for layouts uses the ledger of rho.py with PH = ops*7/lanes (per-evaluation cost scaled; batch counts and stage overheads approximated). Pitch 33 or less cannot add two 32-bit values without a mask under the tracer rules, so it is not counted. Duplicated-lane 4-op rotation forms were not built (adds corrupt the duplicate). Layout variants were counted, not run in numpy, except the no-mask one.",
        "held_fixed": "spec 3-round function, op model (add, and, or, xor, shl, shr, immediates), 256-bit words, constants folded",
        "reopen_if": "a layout with more lanes per word or a rotation form under 5 ops is found; or the register width in the cost model changes"})

fz = WD["freeze_chain_words"]
for i in range(12):
    w = WD["words"][str(i)]
    unit = "blake3-r3-U%d" % WUNIT[i]
    cell = "m%d" % i
    zero_word = i < 8
    pos = "; ".join("round %d call %s (%s)" % (r, ("C%d" % j) if j < 4 else ("D%d" % (j - 4)), xy) for r, j, xy in w["positions"])
    mo = w["modes"]
    flip = w["flip_mean_bits_of_256"]
    uses = "; ".join("round %d: step ops %d (adds %d)" % (u["round"], u["step_ops"], u["step_adds"]) for u in w["uses"])
    obj = "message word m%d" % i
    if zero_word:
        n1 = ("m%d is the constant 0 (the 32-byte zero prefix of the target). Used 3 times: %s. Because it is zero, no add is emitted for it at any use; cost attributed to the word as used = 0 ops "
              "(its round-0 use sits in a column call that is entirely constant and folds away). Whole-step ops at the uses: %s." % (i, pos, uses))
    else:
        n1 = ("m%d is a chain word (part of x, fed by digest word %d with the identity embedding). Used 3 times: %s. Each use is one add of the variable word into the a-chain; whole-step ops at the uses: %s. "
              "Ops that depend on the word being variable rather than the constant 0: %d of 595 (%.4f bit of time_log2), because a constant word also lets constant-only G calls fold." % (
                  i, i - 8, pos, uses, -mo["zero"]["delta_ops"], -mo["zero"]["delta_time_log2"]))
    put(unit, "blake3-r3|%s|msgword|Q1" % cell, {
        "object": obj, "question": "Q1: value/count of message word m%d as used in the filed circuit." % i,
        "status": "COMPUTED", "number": n1, "evidence": EV_WORD,
        "notes": VAL + " Uses taken from the message permutation applied per round (own word_positions in b3scan.py); ops from the tracer by setting the word to constant 0 and recounting.",
        "held_fixed": "target 0^32||x (m0..m7 = 0, m8..m15 = x), flags 11, counter 0, length 64, 3 rounds; filed layout",
        "reopen_if": "the target prefix or the chain embedding changes"})
    diff = ("Diffusion test (flip each of the 32 bits of m%d, 48 random inputs each, 3 rounds): mean %.1f of 256 digest bits change (per-bit means %.1f to %.1f), and all 8 digest words change in every flip tested "
            "(8 flips per bit class sampled), so the word fully reaches the digest." % (i, flip["mean"], flip["min_bit"], flip["max_bit"]))
    if zero_word:
        n2 = ("Change m%d: to a nonzero constant (0x9e3779b9, 1 and 0xffffffff all give the same): %d ops, +%d (+%.4f bit); to a variable word (as if the prefix were free): %d ops, +%d (+%.4f bit). %s "
              "m%d is fixed to 0 by the target, so the change is not allowed; the numbers show what the zero is worth." % (
                  i, mo["const_9e3779b9"]["ops"], mo["const_9e3779b9"]["delta_ops"], mo["const_9e3779b9"]["delta_time_log2"], mo["var"]["ops"], mo["var"]["delta_ops"], mo["var"]["delta_time_log2"], diff, i))
        nt = VAL + " Variants traced and compared with the scalar function on 60 inputs (0 mismatches)."
        ri = "the target prefix is ever not zero"
    else:
        n2 = ("Change m%d: to the constant 0 (word frozen, not part of the chain): %d ops, %d (%.4f bit); to 0x9e3779b9: %d ops (%d). %s "
              "Structural necessity (argued, NOT run): with m%d frozen the chain function lives on a smaller domain and a full 256-bit digest match then needs many partial collisions "
              "(for one frozen word about 2^32 collisions of a 224-bit function); at memory near 2^20 bytes the parallel-collision-search price per collision (about 2.5*sqrt(N/w), a literature formula applied by hand) "
              "is far above the saving. So the word stays variable; the op saving is not a lever on present knowledge." % (
                  i, mo["zero"]["ops"], mo["zero"]["delta_ops"], mo["zero"]["delta_time_log2"], mo["const_9e3779b9"]["ops"], mo["const_9e3779b9"]["delta_ops"], diff, i))
        nt = VAL + " Variants traced and compared with the scalar function on 60 inputs (0 mismatches). The multi-collision cost is not tested by search."
        ri = "a memory-cheap method to collect many partial collisions is found (then freezing chain words is worth up to 0.18 bit for m8..m11)"
    put(unit, "blake3-r3|%s|msgword|Q2" % cell, {
        "object": obj, "question": "Q2: necessity of m%d - change it and recount the exact outcome (ops, time_log2, digest)." % i,
        "status": "COMPUTED", "number": n2, "evidence": EV_WORD, "notes": nt,
        "held_fixed": "all other words as in the target; same layout; ledger rho.py with PH replaced",
        "reopen_if": ri})
    if zero_word:
        n3 = ("Degrees of freedom of m%d: 0 bits (fixed to 0 by the target). Score-optimal value: 0, because a nonzero constant costs +2 ops (tested 0x9e3779b9, 1, 0xffffffff: %d ops each). "
              "The circuit cost does not depend on which nonzero constant it is." % (i, mo["const_9e3779b9"]["ops"]))
        r3 = "the embedding or the prefix changes"
    else:
        n3 = ("Degrees of freedom of m%d: 32 bits (all used: the chain domain is 2^256). The circuit cost does not depend on the value while it is variable. "
              "If the word were frozen, the score-optimal constant is 0: ops with 0 -> %d, 1 -> %d, 0x9e3779b9 -> %d, 0xffffffff -> %d (baseline 595). Which digest word feeds m%d is free "
              "(relabelling registers costs no op; the tracer does not depend on the naming)." % (
                  i, mo["zero"]["ops"], mo["const_1"]["ops"], mo["const_9e3779b9"]["ops"], mo["const_ffffffff"]["ops"], i))
        r3 = "the embedding of the digest into x gets a non-identity map that costs ops, or a nonzero constant helps through a carry-structure trick"
    put(unit, "blake3-r3|%s|msgword|Q3" % cell, {
        "object": obj, "question": "Q3: degrees of freedom or score-optimal value of m%d." % i,
        "status": "COMPUTED", "number": n3, "evidence": EV_WORD,
        "notes": VAL + " Value dependence tested only on the constants named; cost depends on constant folding of zero and on whether an all-constant G call appears.",
        "held_fixed": "other words as in the target; counts from our tracer", "reopen_if": r3})
    if zero_word:
        n4 = ("Alternatives for m%d: (a) nonzero constant: +%d ops; (b) variable word: +%d ops (+%.4f bit). For the whole prefix: making all of m0..m7 variable costs +%d ops (+%.4f bit); "
              "so the zero prefix of the target is worth %.3f bit to this circuit, and no alternative placement of the prefix exists (target fixed)." % (
                  i, mo["const_9e3779b9"]["delta_ops"], mo["var"]["delta_ops"], mo["var"]["delta_time_log2"], WD["prefix_all_variable"]["delta_ops"],
                  WD["prefix_all_variable"]["delta_time_log2"], WD["prefix_all_variable"]["delta_time_log2"]))
        r4 = "the target changes"
    else:
        n4 = ("Alternatives for m%d: (a) freeze it to 0: %d ops (%d); (b) freeze with neighbours (ops from 595): m8+m9 -> %d (%d), m10+m11 -> %d (%d), m8..m11 -> %d (%d, %.4f bit); "
              "(c) freeze all of m8..m15 -> 0 ops (circuit constant). The savings are real in the op count (a frozen pair makes a round-0 diagonal call all-constant and folds about 18 ops per call) "
              "but the chain then covers fewer than 256 bits, see Q2. OPEN: whether partial-collision harvesting at memory near 2^20 bytes can pay for it." % (
                  i, mo["zero"]["ops"], mo["zero"]["delta_ops"], fz["freeze_zero_8_9"]["ops"], fz["freeze_zero_8_9"]["delta_ops"], fz["freeze_zero_10_11"]["ops"], fz["freeze_zero_10_11"]["delta_ops"],
                  fz["freeze_zero_8_9_10_11"]["ops"], fz["freeze_zero_8_9_10_11"]["delta_ops"], fz["freeze_zero_8_9_10_11"]["delta_time_log2"]))
        r4 = "partial-collision harvesting (many 224- or 192-bit collisions, check the rest) is shown to cost near sqrt(N) per collision at memory about 2^20 bytes; then the frozen-word saving (0.09 to 0.18 bit) would apply"
    put(unit, "blake3-r3|%s|msgword|Q4" % cell, {
        "object": obj, "question": "Q4: alternatives to the filed use of m%d, counted exactly." % i,
        "status": "COMPUTED", "number": n4, "evidence": EV_WORD,
        "notes": VAL + " Alternatives costed in ops and time_log2 only; whether a restricted-domain chain can still deliver a 256-bit collision at 2^20 bytes was not tested by search.",
        "held_fixed": "target fixed; layout fixed; other words as in the target", "reopen_if": r4})
print("cells", count)
