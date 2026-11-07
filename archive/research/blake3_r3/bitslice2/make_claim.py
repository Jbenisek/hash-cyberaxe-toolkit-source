"""Builds claim.json, experiments/manifest.json, submission-note.md and dependencies.json (run after make_pkg.py)."""
import sys
import json
import os
import re
from math import log2
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "pkg")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(PKG, "blake3", "experiments"))
import bsrho as b

proof = open(os.path.join(PKG, "blake3", "proof.md"), encoding="utf-8").read()
lines = proof.split("\n")


def span(head, nxt):
    """1-based inclusive line range from the heading starting with `head` to the line before the heading starting with `nxt`."""
    a = next(i for i, l in enumerate(lines) if l.startswith(head))
    z = next(i for i, l in enumerate(lines) if i > a and l.startswith(nxt))
    return "proof:%d-%d" % (a + 1, z)


S31 = span("### 3.1", "### 3.2")
S32 = span("### 3.2", "### 3.3")
S33 = span("### 3.3", "### 3.4")
S34 = span("### 3.4", "### 3.5")
S35 = span("### 3.5", "## 4.")
S4 = span("## 4.", "## 5.")
S5 = span("## 5.", "## 6.")
S6 = span("## 6.", "## 7.")
S7 = span("## 7.", "## 8.")
S8 = span("## 8.", "## Appendix A")
S1 = span("## 1.", "## 2.")

p = b.plan(256)
lg = b.ledger(p)
ls = b.loss(p)
st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
N = lg["total"]
TL = 124.95470
Tp, M = p["Tp"], b.INFLIGHT

H1 = dict(
    id="H1-random-mapping",
    statement=("Score-critical. f(x) = digest(P || 0^32 || x), the 3-round complete hash of the 128-byte message with the fixed first block P of proof.md Section 8 (the root compression of block 2 with chaining value CV = chain_value(P)), behaves as a random mapping on N = 2^256 points for everything the search evaluates: "
               "(a) for the inputs the search evaluates, the 256-bit outputs behave as uniform and independent values, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); "
               "(b) the iterates of f from the starts r + t (r a fresh uniform 256-bit word, t < 2^16) have the first-collision law of a random mapping (trails of length near 2^114.9 merge as independent random paths); "
               "(c) whether an iterate is a distinguished point (low 32 bits zero and the next 90 bits below %d) is independent of (a) and (b) and has probability %d / 2^122. Under H1 the success probability of the single attempt is at least 0.39 (proof.md Section 4)." % (Tp, Tp)),
    role="score-critical",
    scope=("The fixed target blake3-r3-prefix-v1, the fixed first block P, the fixed key m0..m7 = 0, the 2^128-scale evaluation of f along about %d trails of mean length 2^114.89 started from r + t, 256 trails at a time. Not claimed for other keys, other prefixes, other round counts, or evaluations beyond this scale." % round(ls["trails"], -2)),
    extrapolation=("Declared and not proved. The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. Evidence run by this entry's own program: the organizer experiments bsrho-n18 (the 256-lane search at width 18, one attempt per trial; the organizer counts the trials that return a verified pair) and proj-k0-w256 (2048 points of the K = 0 target with prefix P at width 256 per trial; the organizer counts the trials whose point set contains a collision of a 21-bit projection), "
                   "and the tests T1 to T3 that the program prints (proof.md Section 5). Extrapolation from widths up to 18 (search) and 21 projection bits at 2048 points (full width) to width 256 and 2^128 evaluations is by the premise only. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Limits."),
    evidence_ids=["experiment:bsrho-n18", "experiment:proj-k0-w256", S5, S6],
    limitations=("The full 256-bit functional graph, iterations above 2^40, and other keys are untested. The experiments show correctness of the program and no deviation at the sizes run (256 trials each; the standard deviation of a success frequency is about 0.03); they do not measure collision structure at 2^128 evaluations. "
                 "The organizer reports the counts of returned pairs; the ideal-function control, the family-law runs and the other six projections are the program's own observations. A rate deficit eps of H1 (a) above 0.0040 lowers the success probability below 0.39 and is repaired by at most 0.5 * log2(1/(1-eps)) more bits of time."),
)
H2 = dict(
    id="H2-loss-terms", role="supporting",
    statement=("Supporting. Under H1, the points lost at the halt and the events outside the birthday count are bounded as in proof.md Section 4: the sum of the ages of the 256 unfinished trails is at most %d L except with probability 1e-6 (each age dominated by an exponential with mean L = 2^114.89); the number of cut trails is Poisson with mean %.3f, charged as %.2e of probability (a third cut is a halt); "
               "the expected number of colliding pairs inside one trail is at most %.1e; a key false match has probability below %.0e; the table-capacity abort has probability below 2^%.1f. The sum of these probabilities is below %.2e." % (M, ls["mean_cut_trails"], ls["cut_deficit"], ls["inside_trail"], ls["key_false_match"], log2(ls["table_capacity"]), ls["sum"])),
    scope="The parameters of plan(256) in experiments/bsrho.py: 256 lanes, DP density %d / 2^122, age cap 11 L, table of %d keys." % (Tp, tmax),
    extrapolation="Computations under H1 only (geometric trail lengths, memoryless DP events); the same formulas are implemented in plan(n) and loss(p) and the plan is exercised at n = 18 in the experiments.",
    evidence_ids=[S4, "experiment:bsrho-n18"],
    limitations="The 256 ages are treated as independent, each dominated by an exponential, under H1 (c); the cut-trail loss is bounded as a probability over the number of cut trails (Poisson) in proof.md Section 4 and costs %.2e, inside the %.2e slack." % (ls["cut_deficit"], ls["P_lower"] - 0.39 + ls["sum"]),
)
H3 = dict(
    id="H3-machine-convention", role="score-critical",
    statement=("Score-critical premise of this entry. The cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares R = 1,024 registers of 256 bits, counted as 32,768 bytes of memory, and charges every operation, load, store and register move. The main loop (one batch of 256 trails, %d operations: the %d-operation generated step, a %d-operation stage-1 test and 3 loop operations) has no load, store or move because the generated line needs 771 registers (output plane j in the register of input plane j). "
               "The organizer's reference count C(r3) = 638 is used only as the unit. Every instruction is charged 36 bytes of code." % (body, st.ops, filt)),
    scope="The loop body of one batch of 256 lanes, its stage-1 test and the handlers; table accesses, recovery, events and setup are charged at the stated bounds including loads and stores of their words.",
    extrapolation="A machine with fewer than 771 registers would add loads and stores to every batch; proof.md 3.5 gives the cost (time_log2 %.4f with 512 registers, %.4f with 256). The claim assumes the declared 1,024." % (log2(b.ledger(None, None, 512)["total"] / 638), log2(b.ledger(None, None, 256)["total"] / 638)),
    evidence_ids=[S31, S32, S33, S35, S7],
    limitations="The benchmark profile does not fix a register count; the declaration is this entry's own. The count %d is produced by the generator in the program and the register allocation by `allocate`; smaller files are priced by the program's Belady allocation of the straight line (an upper bound on what a better schedule needs)." % st.ops,
)

H4 = dict(
    id="H4-two-block-message-mode", role="supporting",
    statement=("Supporting, used by the score-critical claim. The target's message domain, quoted from the organizer profile field message_domain, is \"Finite byte strings of bit length below 2^64.\" The attack outputs two 128-byte messages P || 0^32 || x and P || 0^32 || y, which are byte strings of that domain; the standard chunk rules for 128 bytes (one chunk, two blocks, flags 1 on block 1 and 10 on block 2) apply and are those of verifier/blake3.py. "
               "P is a fixed constant of the program, fixed before the attack by the bounded scan of proof.md Section 8 (program shipped, operations charged) for the one condition (A1 + B2) mod 2^32 = 0 on the chaining value of P; the attack does not depend on any other property of P."),
    scope="The target blake3-r3-prefix-v1, messages of exactly 128 bytes whose first 64 bytes are P and whose bytes 64..95 are zero. Not claimed for other message lengths, other prefixes, or keyed or tree modes.",
    extrapolation=("None beyond the profile text: the claim relies on the profile accepting any finite byte string as a message. The claim does not apply to a reading of the domain that excludes 128-byte strings; the bit-sliced entry 0a9640ed (124.96822) makes a claim for 64-byte messages. "
                   "The program's digest functions agree with verifier/blake3.py on 300 messages of this form (0 differences), and both organizer experiments recompute the digests of the 128-byte messages with the organizer's reference."),
    evidence_ids=["experiment:bsrho-n18", "experiment:proj-k0-w256", S1, S8],
    limitations=("The scan that found P is a one-time computation of 10,768,619,077 candidates with the shipped scan program (7,721,099,878,210 operations, a row of the ledger), stated as preprocessing_log2 = 33.5; P is retained as nonuniform advice of one word (nonuniform_advice_log2_bytes = 5, counted in memory); "
                 "its uniformity assumption (a random chaining value passes with probability 2^-32) is used only to describe the scan and is not used by the attack."),
)

R = []
R.append("Two distinct 128-byte messages P || 0^32 || x and P || 0^32 || y (x != y, 256-bit little-endian integers), P the fixed 64-byte string of proof.md Section 8: one chunk of two blocks, block 1 = P (flags 1, counter 0, length 64), block 2 = 0^32 || x (flags 10, counter 0, length 64, chaining value = the chaining value of P), standard IV, unkeyed, the complete 256-bit digest of the 3-round hash (blake3-r3-prefix-v1), found as a collision f(x) = f(y) of f(x) = digest(P || 0^32 || x). Plain birthday attack; no differential or structural property of the 3 rounds is used. The two-block mode is declared as H4.")
R.append("Machine, a premise of this entry: a classical load/store machine with 256-bit words, 256-bit immediates and 1,024 registers under collision-frontier-v5 (the profile fixes the word size and charges loads and stores, not a register count); 638 operations (C of blake3-r3) to the unit. Charged: every add, AND, OR, XOR, shift, compare, branch, register move, load, store and the random word. The main loop evaluates 256 trails bit-sliced: %d operations per batch (%d gates and XORs with all-ones, a %d-operation stage-1 test, 3 loop operations) with no load, store or move; it needs 771 registers. Smaller files are priced in proof.md 3.5 (%.4f at 512, %.4f at 256)." % (body, st.ops, filt, log2(b.ledger(None, None, 512)["total"] / 638), log2(b.ledger(None, None, 256)["total"] / 638)))
R.append("time_log2 is an upper bound: every term of proof.md Section 3.4 is enforced by a halt of the program (B batches, e2max stage-1 hits, %d table keys, 2 cut trails, a recovery of at most c + 2^48 batches, one recovery), and the bound charges each at its limit. The attempt is single: one fresh uniform 256-bit word r, no restart, no amplification, no stored collision; the only advice is the prefix word i (last restriction); m0..m7 of the last block = 0. Distinguished points: low 32 bits zero and the next 90 bits below %d (density %d / 2^122)." % (tmax, Tp, Tp))
R.append("Memory: %d table entries of 25 bytes (%d bytes) plus %d bytes of code (%d instructions of 36 bytes) plus 16,384 bytes of counters and the plane copy plus 32,768 bytes for the 1,024 registers plus the 32-byte advice word: %d bytes <= 2^20; claimed as 2^20, so the memory term of the score is 0." % (tmax, tmax * 25, code, body + b.OTHER_CODE, 25 * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE))
R.append("Success probability at least 0.39 holds under H1 (proof.md Section 5) with the losses of Section 4 (about %.2e spent of %.2e available). If the pair-collision rate of the evaluated inputs were (1 - eps) of the random-mapping rate, the success probability stays at least 0.39 for eps <= 0.0040, and at most 0.5 * log2(1/(1-eps)) more bits (0.0072 for eps = 0.01) restore it beyond." % (ls["sum"], ls["P_lower"] - 0.39 + ls["sum"]))
R.append("The declared experiments run this program in the organizer sandbox: bsrho-n18 (one attempt of the 256-lane search per trial at width 18, DP = low 2 bits zero) and proj-k0-w256 (2048 points of the K = 0 target at width 256 per trial, a pair when two digests agree in the low 21 bits). Each returns pairs whose complete 3-round digests agree in the stated low bits. They check the circuit, bookkeeping and recovery on the real target and give organizer-counted frequencies; not the cost or success probability at width 256. No outside code or library is used.")
R.append("Nonuniform advice: the integer i = %d (34 bits, held in one 256-bit word of 32 bytes, counted in the memory total; nonuniform_advice_log2_bytes = 5). P is the block with little-endian words w0 = i mod 2^32, w1 = i >> 32, w2..w15 = 0, and the program derives P and the chaining value from i. i is the first candidate of the shipped scan (proof.md Section 8, 7,721,099,878,210 operations, preprocessing_log2 = 33.5, a row of the ledger) with (A1 + B2) mod 2^32 = 0." % b.PREFIX_I)
for r in R:
    assert len(r) <= 1024, len(r)

claim = {
    "schema_version": 3, "target_profile": "blake3-r3-prefix-v1", "attack_class": "ordinary-collision", "rounds": 3,
    "claim": {"time_log2": TL, "time_unit": "target-compressions", "memory_log2_bytes": 20, "preprocessing_log2": 33.5,
              "success_probability": 0.39, "nonuniform_advice_log2_bytes": 5},
    "restrictions": R, "baseline_improved": "blake3-r3-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "experiment_manifest": "experiments/manifest.json",
    "heuristics": [H1, H2, H3, H4], "submission_state": "ready", "lane": "exploratory",
}
for h in claim["heuristics"]:
    for k, v in h.items():
        if isinstance(v, str):
            assert len(v) <= 4096, (h["id"], k, len(v))
write = lambda path, text: open(path, "w", newline="\n", encoding="utf-8").write(text)
write(os.path.join(PKG, "blake3", "claim.json"), json.dumps(claim, indent=2, ensure_ascii=False) + "\n")

m18 = ("ffff03" + "00" * 29)
m21 = ("ffff1f" + "00" * 29)
zero = "00" * 32
manifest = {"schema_version": 1, "experiments": [
    {"id": "bsrho-n18", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r3-prefix-v1 target, collision of the low 18 bits of the complete digest. Each trial runs ONE attempt of the shipped 256-lane search (plan(18): distinguished points with the low 2 bits zero, %d batches of 256 lanes, cut rule, table, recovery on the packed circuit) from a word derived from the trial seed, with no amplification, and returns the two 128-byte messages P || 0^32 || x and P || 0^32 || y (P the prefix of proof.md Section 8) when the attempt found a pair, two nulls otherwise. "
               "The same program also runs the same attempt on an ideal function of the same width (keyed blake2b) and one family-law run with a fresh key at n = 12; these are reported as untrusted observations only." % b.plan(18)["B"]),
     "hypothesis": ("For every returned pair the two messages are distinct and their complete 3-round digests agree in the low 18 bits (digest bytes 0 and 1 and the low 2 bits of byte 2). This is exact: the program recovers a merge of two trails of the chain x -> low 18 bits of the digest of P || 0^32 || x. "
                    "The number of trials that return a pair is the number of single attempts that succeeded; expected about 0.66 of the trials (the program's own run gave 163 of 256), and equal to the ideal-function control within sampling error (two-proportion |z| below 3.5 expected). Observations (untrusted, the program's own): target_ok, ideal_ok, batches, halts, t1_steps (mean about sqrt(pi 2^12 / 2) = 80.2). Not shown: any width-256 cost or success probability."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m18, "expected_hex": zero}},
    {"id": "proj-k0-w256", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r3-prefix-v1 target with the fixed first block P at full width 256, with the key m0..m7 of the last block = 0. Each trial evaluates 2048 points x with the shipped bit-sliced circuit (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of f from 256 seed-derived starts), "
               "and returns two distinct points whose complete digests agree in the low 21 bits when the set contains such a pair, two nulls otherwise. Untrusted observations: the numbers of equal pairs in seven 21-bit projections of the digest."),
     "hypothesis": ("For every returned pair the two messages P || 0^32 || x and P || 0^32 || y are distinct and their complete 3-round digests agree in the low 21 bits (digest bytes 0 and 1 and the low 5 bits of byte 2). This is exact. "
                    "If f is uniform on the points sampled, a trial returns a pair with probability 1 - exp(-C(2048, 2) / 2^21) = 0.632 (expected about 162 of 256 trials; the program's own run gave 170 of 256), and each projection has mean 0.9995 equal pairs per trial. Observations (untrusted): source, dup_w0, dup_w3, dup_w7, dup_xor8, dup_sum8, dup_p01, dup_p23. Not shown: collision structure at 2^128 evaluations."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m21, "expected_hex": zero}},
]}
write(os.path.join(PKG, "blake3", "experiments", "manifest.json"), json.dumps(manifest, indent=2) + "\n")

deps = [{"submissionId": "0a9640ed-558a-4f0a-aba8-45e89ffcfd7c",
         "rationale": "Our own entry for blake3 round 3 (124.96822, bit-sliced 256-lane chain step with a declared register file). This entry keeps its program, relation, trail-and-table search, handlers, recovery walk, ledger method, restated Lemma 2 and premise experiments, and changes the message to a two-block message with a fixed first block P whose chaining value removes one addition from the circuit (generator constants, recovery circuit, ledger, scan).",
         "evidence": "proof.md first paragraph, Sections 1, 2, 3.2, 3.3, 3.4, 8 and Appendix A."},
        {"submissionId": "fc39027a-518f-464f-b88b-71675941ffdc",
         "rationale": "Our own entry for blake3 round 3 with a fixed first block P (125.09556, still in review when this entry was prepared): the two-block message mode (H4), the prefix condition (A1 + B2) mod 2^32 = 0, the scan for P and its charging as preprocessing and nonuniform advice are taken from it.",
         "evidence": "proof.md Sections 1 and 8 and the H4 heuristic of claim.json."}]
write(os.path.join(PKG, "dependencies.json"), json.dumps(deps, indent=2) + "\n")
write(os.path.join(PKG, "dependencies_check.txt"), "")
os.remove(os.path.join(PKG, "dependencies_check.txt"))

note = """# BLAKE3, 3 rounds: the counted birthday search with a bit-sliced 256-lane circuit and a tuned two-block prefix

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A credited derivative of our own entry 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, 124.96822, bit-sliced, passed the judges), which is a derivative of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087, the first entry for this target).
It keeps the 0a9640ed program and construction (relation f(x) = digest of the message, trail-and-table search with mixed distinguished points, 25-byte entries, handlers, recovery walk, ledger method, restated Lemma 2, the two organizer experiments) and changes one thing: the colliding messages have a fixed 64-byte first block P, so the block the search varies is the last block of a two-block chunk, with chaining value CV = chain_value(P) instead of the IV and flags 10 instead of 11.
This is the two-block mode and the nonuniform-advice treatment of our entries a72f48eb and fc39027a (the judges' ruling on a72f48eb established the two-block mode and required the prefix to be counted as advice).

1. The circuit. The bit-sliced generator folds constants at build time, so a different chaining value and a different flag word change the number of gates that survive. P is chosen by a one-time scan so that one 32-bit sum of two constants of the last block's circuit is zero (A1 + B2 = 0 mod 2^32, the first addition of diagonal call 5 of round 0). The generated step is %(PH)d operations for 256 trails (%(PHO)d in 0a9640ed with the same polarity hill climb and 19,022 with its shipped polarity vector); the packed recovery circuit is %(PH7)d operations (595 in 0a9640ed).
   The loop body is %(body)d operations (step, stage-1 test 35, loop 3) against 19,060.
2. The advice. P is this entry's nonuniform advice: the integer i = %(PREFIXI)d, one 256-bit word (32 bytes), counted in the memory total and declared as nonuniform_advice_log2_bytes = 5. The scan that found i is shipped (`python3 bsrho.py --scan`) and charged operation by operation: %(scancand)s candidates of %(scanper)d operations = %(scanops)s operations = 2^%(log2scan).2f units, a row of the ledger, claimed as preprocessing_log2 = 33.5.
3. The table and the plan. The shorter program leaves room for %(tmax)s table entries (9,938 in 0a9640ed) and the plan moves to Tp = %(Tp)d; the 32-byte advice word is counted in the memory.

Message mode, declared as heuristic H4: the profile's message domain is "Finite byte strings of bit length below 2^64." The two output messages are 128 bytes, P || 0^32 || x and P || 0^32 || y: one chunk, two blocks, flags 1 on block 1 and 10 on block 2, standard IV, unkeyed, complete 256-bit digest. The claim does not apply to a reading of the domain that excludes 128-byte strings.
The program's digest functions agree with `verifier/blake3.py` on 300 two-block messages (scalar), 1,024 messages (the bit-sliced step), 64 messages chained for 4 steps and 7 messages (the packed circuit): no difference. Both organizer experiments recompute the digests of the 128-byte messages.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of P || 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | %(TL)s |
| operations per batch of 256 trails | %(body)d (step %(PH)d, stage-1 test 35, loop 3) |
| total N | %(N)s operations = 2^%(log2N).6f units of 638 |
| memory | %(mem)s bytes including code (%(instr)s instructions of 36 bytes), the table (%(tmax)s entries of 25 bytes), counters, the 1,024-register file and the 32-byte advice word; claimed as 2^20, so the memory term is 0 |
| success probability | at least 0.39, single attempt, no amplification |
| preprocessing | 2^33.5 units (the scan for P, program shipped and charged in the ledger); setup and generator 2^%(log2setup).2f units are in the time bound |
| nonuniform advice | 5 (log2 of 32 bytes: the prefix word i) |
| score | %(TL)s |

Against 0a9640ed (124.96822) this is %(gain).5f bit. The main loop is %(pmain).2f percent of the total, recovery %(prec).2f percent, the scan %(pscan).1e of it.

## The one score-critical premise (H1) and the evidence for it

H1: the 3-round chain of the last block (chaining value CV) behaves as a random mapping on 2^256 points for everything the search evaluates. It is a premise about one fixed function and cannot be tested at width 256. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits.
This entry ships two organizer experiments that run THIS program, so that the organizer's sandbox executes them and recomputes every returned pair (the messages begin with P, so they run the fixed-prefix function):

| experiment | what the organizer runs and checks | what it counts |
| --- | --- | --- |
| bsrho-n18 (T3) | per trial one attempt of the 256-lane search at width 18 on the target chain, no amplification; the pair is recomputed | trials that return a verified pair (single-attempt success frequency); the program also runs the ideal-function control and a fresh-key family-law run as untrusted observations (T1) |
| proj-k0-w256 (T2) | per trial 2048 points of the target at width 256 through the bit-sliced circuit (uniform inputs, counters, iterates); a pair of points with equal low 21 digest bits is recomputed | trials that contain a collision of the 21-bit projection, expected 63.2 percent; six more projections as untrusted observations |

The program's own run (python3 bsrho.py --stats; the organizer's seeds differ): %(t3)s. %(t1)s. %(t2)s
Larger earlier runs of the three tests on the filed entry's program (the function with chaining value IV and flags 11) are listed in proof 5; they were not repeated on this function. The tests have limited power (256 trials: a standard deviation of about 0.03 in a frequency).

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare, branch, register move, load and store, and the one random word, on a load/store machine with 256-bit words and 256-bit immediates and 1,024 registers. The main loop has none of the last three kinds: `allocate` in the program assigns %(regs)d registers to the straight line with input plane j and output plane j in the same register, and a check executes the allocated code.
Handlers copy the 256 planes to an 8 KiB area in memory (counted) and work there; their per-event charges are listed in proof 3.3. Every instruction is charged 36 bytes. The organizer's reference count of 638 for one compression is the unit. The 1,024-register file is this entry's declaration (it was accepted for 0a9640ed); smaller files are priced in proof 3.5: %(t512).4f with 512 registers, %(t256).4f with 256.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40, prefixes other than P and keys other than the all-zero key for m0..m7 were not tested.
- If the real pair-collision rate were lower than the model by more than %(epsp).2f percent, the success probability would fall below 0.39; at most 0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About %(sumloss).2e of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); %(margin).4f is kept as margin.
- The operation count %(PH)d is produced by the generator in the shipped program (experiments/bsrho.py, `--selftest` and `--ledger`); the organizer experiments do not meter cost. The polarity vector `PINS` is the result of a development-time hill climb, shipped as a constant.
- The memory total is %(mem)s bytes (%(spare)d bytes to spare under 2^20); the table size was chosen as the largest that fits.
- Only one condition on the chaining value was searched (a scan of 2^33.49 units); further conditions would multiply the scan by 2^32 each and were not searched. The full scan was run as a C program of the same arithmetic; the shipped Python scan reproduces it at a reduced condition (16 bits: first success at i = 20,832) and confirms that i passes the full 32-bit condition, but the 1.08e10 candidates were not rerun in the shipped program, and no organizer experiment covers the scan.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line. Together they are below 1e-7 of the ledger.
"""
from math import exp as _exp
_stats = open(os.path.join(HERE, "stats_out.txt")).read().strip().split("\n")
_x = float(b.LAMBDA)
_eps = 0
for _k in range(1, 20000):
    _e = _k / 1e5
    if 1 - _exp(-_x * (1 - _e)) - ls["sum"] >= 0.39:
        _eps = _e
_mem = 25 * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE
vals = dict(PH=st.ops, PHO=19014, PH7=b.PH7, regs=771, instr="{:,}".format(body + b.OTHER_CODE), tmax="{:,}".format(tmax), Tp=Tp,
            TL=TL, body=body, N="{:,}".format(N), log2N=log2(N / 638), PREFIXI=b.PREFIX_I, scancand="{:,}".format(b.PREFIX_I + 1), scanper=b.SCAN_PER,
            scanops="{:,}".format(b.scan_ops()), log2scan=log2(b.scan_ops() / 638), log2setup=log2((b.SETUP_FIXED + lg["gen"]) / 638),
            mem="{:,}".format(_mem), spare=b.MEM_LIMIT - _mem,
            gain=124.96822 - TL, pmain=100 * float(lg["parts"]["main"]) / float(N), prec=100 * float(lg["parts"]["recovery"]) / float(N),
            pscan=float(lg["parts"]["scan"]) / float(N), sumloss=ls["sum"], margin=ls["P_lower"] - 0.39, epsp=100 * _eps,
            t512=log2(b.ledger(None, None, 512)["total"] / 638), t256=log2(b.ledger(None, None, 256)["total"] / 638),
            t3=_stats[0], t1=_stats[1], t2=_stats[2].strip() + "; " + "; ".join(l.strip() for l in _stats[3:6]))
write(os.path.join(PKG, "submission-note.md"), note % vals)
print("note bytes", len((note % vals).encode()))
print(S31, S32, S33, S34, S35, S4, S5, S6, S7)
