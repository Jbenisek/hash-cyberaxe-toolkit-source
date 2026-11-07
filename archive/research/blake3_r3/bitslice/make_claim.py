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
S7 = span("## 7.", "## Appendix A")

p = b.plan(256)
lg = b.ledger(p)
ls = b.loss(p)
st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
N = lg["total"]
TL = 124.96822
Tp, M = p["Tp"], b.INFLIGHT

H1 = dict(
    id="H1-random-mapping",
    statement=("Score-critical. f(x) = digest(0^32 || x), the 3-round complete hash of a 64-byte message, behaves as a random mapping on N = 2^256 points for everything the search evaluates: "
               "(a) for the inputs the search evaluates, the 256-bit outputs behave as uniform and independent values, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); "
               "(b) the iterates of f from the starts r + t (r a fresh uniform 256-bit word, t < 2^16) have the first-collision law of a random mapping (trails of length near 2^114.9 merge as independent random paths); "
               "(c) whether an iterate is a distinguished point (low 32 bits zero and the next 90 bits below %d) is independent of (a) and (b) and has probability %d / 2^122. Under H1 the success probability of the single attempt is at least 0.39 (proof.md Section 4)." % (Tp, Tp)),
    role="score-critical",
    scope=("The fixed target blake3-r3-prefix-v1, the fixed key m0..m7 = 0, the 2^128-scale evaluation of f along about %d trails of mean length 2^114.89 started from r + t, 256 trails at a time. Not claimed for other keys, other round counts, or evaluations beyond this scale." % round(ls["trails"], -2)),
    extrapolation=("Declared and not proved. The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. Evidence run by this entry's own program: the organizer experiments bsrho-n18 (the 256-lane search at width 18, one attempt per trial; the organizer counts the trials that return a verified pair) and proj-k0-w256 (2048 points of the K = 0 target at width 256 per trial; the organizer counts the trials whose point set contains a collision of a 21-bit projection), "
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
    extrapolation="A machine with fewer than 771 registers would add loads and stores to every batch; proof.md 3.5 gives the cost (time_log2 125.0356 with 512 registers, 125.2538 with 256). The claim assumes the declared 1,024.",
    evidence_ids=[S31, S32, S33, S35, S7],
    limitations="The benchmark profile does not fix a register count; the declaration is this entry's own. The count %d is produced by the generator in the program and the register allocation by `allocate`; smaller files are priced by the program's Belady allocation of the straight line (an upper bound on what a better schedule needs)." % st.ops,
)

R = []
R.append("Two distinct 64-byte messages 0^32 || x and 0^32 || y (x != y, 256-bit little-endian integers): one chunk, one block, flags 11, counter 0, block length 64, standard IV, unkeyed, the complete 256-bit digest of the 3-round hash (blake3-r3-prefix-v1), found as a collision f(x) = f(y) of f(x) = digest(0^32 || x). Plain birthday attack; no differential or structural property of the 3 rounds is used.")
R.append("Machine, a premise of this entry: a classical load/store machine with 256-bit words, 256-bit immediates and 1,024 registers under collision-frontier-v5 (the profile fixes the word size and charges loads and stores, not a register count); 638 operations (C of blake3-r3) to the unit. Charged: every add, AND, OR, XOR, shift, compare, branch, register move, load, store and the random word. The main loop evaluates 256 trails bit-sliced: %d operations per batch (%d gates and XORs with all-ones, a %d-operation stage-1 test, 3 loop operations) with no load, store or move; it needs 771 registers. Smaller files are priced in proof.md 3.5 (125.0356 at 512, 125.2538 at 256)." % (body, st.ops, filt))
R.append("time_log2 is an upper bound: every term of proof.md Section 3.4 is enforced by a halt of the program (B batches, e2max stage-1 hits, %d table keys, 2 cut trails, a recovery of at most c + 2^48 batches, one recovery), and the bound charges each at its limit. The attempt is single: one fresh uniform 256-bit word r, no restart, no amplification, no stored collision, no advice (m0..m7 = 0). Distinguished points: low 32 bits zero and the next 90 bits below %d (density %d / 2^122)." % (tmax, Tp, Tp))
R.append("Memory: %d table entries of 25 bytes (%d bytes) plus %d bytes of code (%d instructions of 36 bytes) plus 16,384 bytes of counters and the plane copy plus 32,768 bytes for the 1,024 registers: %d bytes <= 2^20; claimed as 2^20, so the memory term of the score is 0." % (tmax, tmax * 25, code, body + b.OTHER_CODE, 25 * tmax + code + b.REGFILE + b.COUNTERS))
R.append("Success probability at least 0.39 holds under H1 (proof.md Section 5) with the losses of Section 4 (about %.2e spent of %.2e available). If the pair-collision rate of the evaluated inputs were (1 - eps) of the random-mapping rate, the success probability stays at least 0.39 for eps <= 0.0040, and at most 0.5 * log2(1/(1-eps)) more bits (0.0072 for eps = 0.01) restore it beyond." % (ls["sum"], ls["P_lower"] - 0.39 + ls["sum"]))
R.append("The declared experiments run this program in the organizer sandbox: bsrho-n18 (one attempt of the 256-lane search per trial at width 18, DP = low 2 bits zero) and proj-k0-w256 (2048 points of the K = 0 target at width 256 per trial, a pair when two digests agree in the low 21 bits). Each returns pairs whose complete 3-round digests agree in the stated low bits. They check the circuit, bookkeeping and recovery on the real target and give organizer-counted frequencies; not the cost or success probability at width 256. No outside code or library is used.")
for r in R:
    assert len(r) <= 1024, len(r)

claim = {
    "schema_version": 3, "target_profile": "blake3-r3-prefix-v1", "attack_class": "ordinary-collision", "rounds": 3,
    "claim": {"time_log2": TL, "time_unit": "target-compressions", "memory_log2_bytes": 20, "preprocessing_log2": 14.4,
              "success_probability": 0.39, "nonuniform_advice_log2_bytes": 0},
    "restrictions": R, "baseline_improved": "blake3-r3-nominal-v2",
    "certificate_manifest": "certificates/manifest.json", "experiment_manifest": "experiments/manifest.json",
    "heuristics": [H1, H2, H3], "submission_state": "ready", "lane": "exploratory",
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
     "scope": ("The blake3-r3-prefix-v1 target, collision of the low 18 bits of the complete digest. Each trial runs ONE attempt of the shipped 256-lane search (plan(18): distinguished points with the low 2 bits zero, %d batches of 256 lanes, cut rule, table, recovery on the packed circuit) from a word derived from the trial seed, with no amplification, and returns the two messages 0^32 || x and 0^32 || y when the attempt found a pair, two nulls otherwise. "
               "The same program also runs the same attempt on an ideal function of the same width (keyed blake2b) and one family-law run with a fresh key at n = 12; these are reported as untrusted observations only." % b.plan(18)["B"]),
     "hypothesis": ("For every returned pair the two messages are distinct and their complete 3-round digests agree in the low 18 bits (digest bytes 0 and 1 and the low 2 bits of byte 2). This is exact: the program recovers a merge of two trails of the chain x -> low 18 bits of the digest of 0^32 || x. "
                    "The number of trials that return a pair is the number of single attempts that succeeded; expected about 0.66 of the trials (the program's own run gave 170 of 256), and equal to the ideal-function control within sampling error (two-proportion |z| below 3.5 expected). Observations (untrusted, the program's own): target_ok, ideal_ok, batches, halts, t1_steps (mean about sqrt(pi 2^12 / 2) = 80.2). Not shown: any width-256 cost or success probability."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m18, "expected_hex": zero}},
    {"id": "proj-k0-w256", "kind": "python-message-pairs-v1",
     "scope": ("The blake3-r3-prefix-v1 target at full width 256 with the key m0..m7 = 0. Each trial evaluates 2048 points x with the shipped bit-sliced circuit (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of f from 256 seed-derived starts), "
               "and returns two distinct points whose complete digests agree in the low 21 bits when the set contains such a pair, two nulls otherwise. Untrusted observations: the numbers of equal pairs in seven 21-bit projections of the digest."),
     "hypothesis": ("For every returned pair the two messages 0^32 || x and 0^32 || y are distinct and their complete 3-round digests agree in the low 21 bits (digest bytes 0 and 1 and the low 5 bits of byte 2). This is exact. "
                    "If f is uniform on the points sampled, a trial returns a pair with probability 1 - exp(-C(2048, 2) / 2^21) = 0.632 (expected about 162 of 256 trials; the program's own run gave 155 to 166 over seeds), and each projection has mean 0.9995 equal pairs per trial. Observations (untrusted): source, dup_w0, dup_w3, dup_w7, dup_xor8, dup_sum8, dup_p01, dup_p23. Not shown: collision structure at 2^128 evaluations."),
     "program": "experiments/bsrho.py", "event": {"kind": "digest-xor-mask", "mask_hex": m21, "expected_hex": zero}},
]}
write(os.path.join(PKG, "blake3", "experiments", "manifest.json"), json.dumps(manifest, indent=2) + "\n")

deps = [{"submissionId": "cf8b0e92-4302-4813-907a-3c970c102646",
         "rationale": "Our own entry for blake3 round 3 (125.10041). This entry keeps its relation, trail-and-table search, recovery walk, packed 595-operation circuit (now the recovery circuit), ledger method and premise tests, and replaces the chain-step circuit by a 256-lane bit-sliced one with a declared register file, a new loop, new handlers and a restated Lemma 2.",
         "evidence": "proof.md first paragraph, Sections 2, 3.2, 3.3 and 4, Appendix A."}]
write(os.path.join(PKG, "dependencies.json"), json.dumps(deps, indent=2) + "\n")
write(os.path.join(PKG, "dependencies_check.txt"), "")
os.remove(os.path.join(PKG, "dependencies_check.txt"))

note = """# BLAKE3, 3 rounds: the counted birthday search with a bit-sliced 256-lane circuit

Credit: Claude Opus 5.5 (Claude Code) for the base entry and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A credited derivative of our own entry cf8b0e92-4302-4813-907a-3c970c102646 (blake3 round 3, 125.10041), which is itself a derivative of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087, the first entry for this target).
It keeps the relation (collision of f(x) = digest(0^32 || x)), the trail-and-table search with distinguished points, the recovery walk, the ledger method and the form of the premise tests T1 to T3, and it changes the circuit that evaluates the chain step:

1. Bit-slicing. The state of 256 independent trails is held as bit planes: plane j is a 256-bit word whose bit l is bit j of the state of trail l. A 32-bit word is 32 planes, so the 80 variable rotations of the three rounds are renaming and cost nothing, XOR/AND/OR are one operation per plane, and an addition is a ripple of full adders (5 gates per bit).
   The program generates the straight line at run time (a few KB of generator source; the generator's own work is charged): %(PH)d operations for 256 trails, %(perlane).2f per trail, against 85 per trail (595 for 7 lanes) in the filed entry. The chain feed is renaming (the digest planes are the next input planes); output j is written into the register of input j.
2. A declared register file. The straight line needs %(regs)d live planes. The benchmark's cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares 1,024 registers of 256 bits and counts them as 32,768 bytes of memory. This is a premise of the entry (H3 in the claim), not a theorem. With 512 registers the program's own spill allocation gives 125.0356, with 256 registers 125.2538 (proof 3.5).
3. 256 trails in flight, one batch per loop pass, a stage-1 test of 35 operations per 256 trails, handlers for the rare events (a lane whose 32 low bits are zero, a finished trail, a cut trail) that store the planes to memory and work there. The packed 7-lane 595-operation circuit of the filed entry is kept for the recovery only.
4. A restated Lemma 2: the 256 unfinished trails at the halt hold at most %(M)d L points except with probability 1e-6; cut trails, key false matches and the table-capacity abort are priced as before. The longer program (%(instr)s instructions of 36 bytes) leaves room for %(tmax)s table entries (the filed entry had 26,791), so trails are longer (L = 2^114.89 against 2^113.36) and the %(M)d L allowance costs %(inflpct).1f percent of the evaluations.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of the message 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds. The two colliding messages are 0^32 || x and 0^32 || y: 64 bytes, one chunk, one block, flags 11, standard IV, unkeyed, complete 256-bit digest.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | %(TL)s |
| operations per batch of 256 trails | %(body)d (step %(PH)d, stage-1 test 35, loop 3) |
| total N | %(N)s operations = 2^%(log2N).6f units of 638 |
| memory | %(mem)s bytes including code (20,860 instructions of 36 bytes), the table (%(tmax)s entries of 25 bytes), counters and the 1,024-register file; claimed as 2^20, so the memory term is 0 |
| success probability | at least 0.39, single attempt, no amplification |
| preprocessing | the generator and the 256 starts, 13,267,200 operations = 2^14.34 units (claimed 14.4), included in N |
| score | %(TL)s |

Against the filed entry (125.10041) this is 0.13 bit. The main loop is %(pmain).2f percent of the total, recovery %(prec).2f percent.

## The one score-critical premise (H1), and the new evidence for it

H1: the 3-round chain behaves as a random mapping on 2^256 points for everything the search evaluates. It is a premise about one fixed function and cannot be tested at width 256. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits.
The filed entry's tests T1 to T3 were run on its own program and were not organizer-run; its evidence was judged unsupported. This entry ships two organizer experiments that run THIS program, so that the organizer's sandbox executes them and recomputes every returned pair:

| experiment | what the organizer runs and checks | what it counts |
| --- | --- | --- |
| bsrho-n18 (T3) | per trial one attempt of the 256-lane search at width 18 on the K = 0 target, no amplification; the pair is recomputed | trials that return a verified pair (single-attempt success frequency); the program also runs the ideal-function control and a fresh-key family-law run as untrusted observations (T1) |
| proj-k0-w256 (T2) | per trial 2048 points of the K = 0 target at width 256 through the bit-sliced circuit (uniform inputs, counters, iterates); a pair of points with equal low 21 digest bits is recomputed | trials that contain a collision of the 21-bit projection, expected 63.2 percent; six more projections as untrusted observations |

The program's own run (python3 bsrho.py --stats; the organizer's seeds differ): %(t3)s. %(t1)s. T2: returned pairs 58 of 86 (expected 54.3) for uniform inputs, 51 of 85 (53.7) for counters and 57 of 85 (53.7) for iterates; the 21 projection counts have |z| at most 1.30.
Larger earlier runs of the three tests on the filed entry's program (same chain function) are listed in proof 5. The tests have limited power (256 trials: a standard deviation of about 0.03 in a frequency).

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare, branch, register move, load and store, and the one random word, on a load/store machine with 256-bit words and 256-bit immediates and 1,024 registers. The main loop has none of the last three kinds: `allocate` in the program assigns %(regs)d registers to the straight line with input plane j and output plane j in the same register, and a check executes the allocated code.
Handlers copy the 256 planes to an 8 KiB area in memory (counted) and work there; their per-event charges are listed in proof 3.3. Every instruction is charged 36 bytes. The organizer's reference count of 638 for one compression is the unit.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and keys other than the all-zero key were not tested.
- If the real pair-collision rate were lower than the model by more than 0.40 percent, the success probability would fall below 0.39; at most 0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About %(sumloss).2e of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); %(margin).4f is kept as margin.
- The 1,024-register file is this entry's declaration; the profile fixes no register count. Smaller files cost 0.067 bit (512) and 0.285 bit (256).
- The operation count %(PH)d is produced by the generator in the shipped program (experiments/bsrho.py, `--selftest` and `--ledger`); the organizer experiments do not meter cost. The step was compared with the organizer's reference blake3(M(x), 3) on 10,240 messages and on 2,560 messages chained four steps: no difference.
- The memory total has 14 bytes to spare under 2^20; the table size was chosen as the largest that fits.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line. Together they are below 1e-7 of the ledger.
"""
vals = dict(PH=st.ops, perlane=st.ops / 256, regs=771, M=M, instr="{:,}".format(body + b.OTHER_CODE), tmax="{:,}".format(tmax),
            inflpct=100 * (M * float(p["L"]) / float(p["Q"])), TL=TL, body=body, N="{:,}".format(N), log2N=log2(N / 638),
            mem="{:,}".format(25 * tmax + code + b.REGFILE + b.COUNTERS), pmain=100 * float(lg["parts"]["main"]) / float(N),
            prec=100 * float(lg["parts"]["recovery"]) / float(N), sumloss=ls["sum"], margin=ls["P_lower"] - 0.39,
            t3=open(os.path.join(HERE, "stats_out.txt")).read().split("\n")[0], t1=open(os.path.join(HERE, "stats_out.txt")).read().split("\n")[1])
write(os.path.join(PKG, "submission-note.md"), note % vals)
print("note bytes", len((note % vals).encode()))
print(S31, S32, S33, S34, S35, S4, S5, S6, S7)
