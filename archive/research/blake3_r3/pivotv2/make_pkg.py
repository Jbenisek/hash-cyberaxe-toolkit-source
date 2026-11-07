"""Builds proof.md, claim.json, experiments/manifest.json, submission-note.md, dependencies.json of the bit-sliced entry from the program's own numbers."""
import sys
import json
import re
import os
from math import log2, exp, log
HERE = os.path.dirname(os.path.abspath(__file__))
PKG = os.path.join(HERE, "pkg")
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(PKG, "blake3", "experiments"))
import bsrho as b

p = b.plan(256)
lg = b.ledger(p)
ls = b.loss(p)
st = b.step256()
ph, filt, body, code, tmax = b.machine_constants(st)
PH7 = b.PH7
N = lg["total"]
TL = 124.95448
assert abs(log2(N / 638) - TL) < 1e-5 and TL >= log2(N / 638)
parts = lg["parts"]
frac = {k: float(v) / float(N) for k, v in parts.items()}
x = float(b.LAMBDA)
slope = 2 * x * exp(-x)
f1 = ls["cut_one_trail"]
mu = ls["mean_cut_trails"]
pk = [exp(-mu) * mu ** j / (1, 1, 2)[j] for j in range(3)]
cut1 = pk[1] * (f1 - 1.5e-4) * slope
cut2 = pk[2] * (2 * f1 - 1.5e-4) * slope
cut3 = (1 - sum(pk)) * (1 - exp(-x))
L = p["L"]
Q = p["Q"]
U = (Q * (1 - b.CUTLOSS) - b.INFLIGHT * L - 1) / 2 ** 128
sumloss = ls["sum"]
# eps: largest deficit with P >= 0.39
eps = 0
for k in range(1, 20000):
    e = k / 1e5
    if 1 - exp(-x * (1 - e)) - sumloss >= 0.39:
        eps = e
rows_R = {}
for R in (1024, 512, 256):
    lgR = b.ledger(None, None, R)
    lsR = b.loss(lgR["plan"])
    rows_R[R] = (b.step256().spill_ops(R) if R < 1024 else 0, lgR["body"], lgR["plan"]["tmax"], lgR["plan"]["Tp"], log2(lgR["total"] / 638), lsR["P_lower"])
    assert lsR["P_lower"] >= 0.39, (R, lsR["P_lower"])
stats_txt = open(os.path.join(HERE, "stats_out.txt")).read().strip().split("\n")
appA = open(os.path.join(HERE, "appA.py")).read().rstrip("\n")
appOut = open(os.path.join(HERE, "appA.out")).read().rstrip("\n")


def fm(v):
    return "{:,}".format(int(v))


def f2(v, d=3):
    return ("%." + str(d) + "g") % v


proof = """# blake3-r3: plain birthday with 256 bit-sliced lanes and a fixed first block

Credited derivative of our own 0a9640ed (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges), itself a derivative of our own cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). It adds the two-block message mode with a fixed first block P, declared as nonuniform advice, that our entries a72f48eb and fc39027a used (the judges' ruling on a72f48eb: the two-block mode H4 is established; the prefix must be counted as advice, which this entry does). This entry keeps the relation, the trail-and-table search with distinguished points, the recovery walk, the
packed 7-lane circuit (now used by the recovery only), the ledger method and the form of the premise tests T1 to T3. It changes the circuit that evaluates the chain: the chain step is evaluated for 256 independent trails at once in bit-sliced form (one 256-bit word holds bit j of all 256 states),
so the 80 variable rotations of a step are renaming and cost nothing, and the step is {PH} operations for 256 trails, {perlane:.2f} per trail against 85 (595 / 7) for the packed circuit of the filed entry and 84.7 (593 / 7) for its two-block form. The price is a declared register file of 1,024 words of 256 bits (counted as memory), a longer program ({instr} instructions), a table of
{tmax} entries instead of 26,791, and 256 trails in flight at the halt instead of 7. No differential, no structure of the 3-round compression is used. The claim is the price of the birthday attack on the complete 3-round hash when the compression is evaluated for 256 instances at a time and every operation is counted.

## 1. Target and relation

Target `blake3-r3-prefix-v1`. Message mode (declared as heuristic H4, the two-block mode of our entries a72f48eb and fc39027a): the profile's message domain is "Finite byte strings of bit length below 2^64"; this entry's two colliding messages are 128 bytes,
M(x) = P || 0^32 || x with P a fixed 64-byte string (Section 8) and x a 256-bit integer (little endian). It is one chunk of two blocks. Block 1 = P (flags 1 = CHUNK_START, counter 0, length 64, chaining value IV) gives the chaining value CV = chain_value(P) (rounds 0..2, feed-forward v[i] XOR v[i+8] for i < 8).
Block 2 = 0^32 || x (words m0..m7 = 0, m8..m15 = the eight little-endian words of x, counter 0, block length 64, flags 10 = CHUNK_END|ROOT, chaining value CV) is the root compression; digest = the 8 words, little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit
little-endian integer. The attack outputs x != y with f(x) = f(y); then M(x) != M(y) are two distinct messages in the domain with equal 256-bit digests. The claim does not apply to a reading of the domain that excludes 128-byte strings. The scalar digest of the program (`digest_words`) was compared outside the shipped experiments with the organizer reference `blake3(M(x), 3)` on 300 random messages of this form: 0 differences.
The bit-sliced step was compared with the organizer reference on 1,024 random messages (one step) and on 64 messages chained for 4 steps: 0 differences; the packed recovery circuit on 7 messages: 0 differences. The program's own selftest (`python3 bsrho.py --selftest`) compares the bit-sliced step, the packed circuit and the register-allocated code with the scalar digest.

## 2. The attack (program `experiments/bsrho.py`, sections 3 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is
below Tp = {Tp}. The density is theta = {Tp} / 2^122 and L = 1 / theta = 2^{log2L:.4f}. The key of a DP is the 56 bits of x above bit 121 followed by the 8 low bits of F (F < {Tp} < 2^8, so those 8 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of all 256 lanes by the generated straight line of section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (section 3.3) forms the 256-bit mask of lanes whose 32 low digest bits are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, section 7) and
   start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = {kappa} L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds {tmax} keys, when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps, then step both together; at the first step
   with f(a) = f(b) and a != b output (a, b). Both lanes of one packed circuit ({PH7} operations, used by nothing else) are used. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = {Tp}, L = {Lnum} / {Lden}, B = {B}, Q = 256 B = {Qratio:.5f} * 2^128 evaluations,
e2max = {e2max}, c = {c} (= 2^{log2c:.3f}), table capacity tmax = {tmax} entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= {tmax}, cut trails <= 2, plus the 256 starts) and every length is below c + S < 2^119, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; the only advice is two 256-bit words counted as memory: the prefix word i = {PREFIXI} (Section 8) and the input polarity vector PINS (Section 3.6), nonuniform_advice_log2_bytes = 6.

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry. The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores, and it gives no register count.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 1,024 registers (a premise of the entry, H3, Section 3.5 prices smaller files). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each.
The main loop has no loads, stores or moves: the generated straight line needs {regs} registers (`allocate` in the program assigns them; output plane j is written into the register that held input plane j, so the next batch reads the same registers), leaving {spare} of the 1,024 for the loop counter, the limit and the handlers' temporaries. The file of 1,024 registers is counted as memory: 32,768 bytes (section 7).
Constants are immediates. The organizer's reference count C(r3) = 638 (222, 430 and 638 for 1, 2 and 3 rounds) is used only as the unit: Unit = 638 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers.

### 3.2 One batch = {PH} operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j is a 256-bit integer whose bit l is bit j of the word of lane l. A rotation is a renaming of planes (no operation). XOR, AND, OR of words are 32 operations each. The sum of two words is a ripple of full adders over the planes: with carry c, x = a xor c, y = b xor c, sum = x xor b, carry = (x and y) xor c (5 gates); the lowest bit has 2 gates (no carry in), the highest 3 (no carry out). The program generates the straight line at run time (`trace`, `Step`): constants (the chaining value CV, IV, the zero words m0..m7, length, flags) are folded at build time, gates are hash-consed,
a gate whose result no output uses is dropped, and each signal carries a polarity bit so that AND of an inverted and an upright plane costs 2 gates and AND/OR of two inverted planes 1. The chain feed is renaming: the 256 digest planes are the 256 input planes of the next batch. Output planes whose polarity differs from the input plane they feed are fixed by one XOR with the all-ones word; the input polarity vector `PINS` is the output of the shipped polarity climb (Section 3.6) and {nfix} of the 256 planes need the fix.
The generated line (`python3 bsrho.py --ledger`, `--selftest`): {gates} gates = {xor} XOR + {and_} AND + {or_} OR, plus {nfix} XORs with all-ones = **{PH} operations**. Per trail {perlane:.3f} operations = {unit:.4f} unit, against 1 unit for a compression and 0.1332 unit for the packed circuit.
Validation: 256 lanes against the scalar digest in the selftest; 1,024 lanes and 64 lanes chained for 4 steps against the organizer reference (section 1); the register-allocated code executed on a register file gives the same planes as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (section 3.3), its code and peak storage are accounted in section 3.6 and section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: {PH} + stage-1 test {filt} + loop control {loopops} = {body} operations. Stage 1: the 32 low planes of digest word 0 are combined into the mask of zero lanes: {orops} ORs over the 30 upright planes, 1 AND over the 2 inverted planes (15 and 30), a complement and a combining OR, a final complement, a compare of the mask with zero and a branch: {filt} operations (`stage1_ops`). The test loses no event: a DP has all 32 low bits zero, so its lane is flagged.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no flagged lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers):
- Stage-1 hit (a flagged lane): store the 256 planes to a 8 KiB copy in memory (256 stores), then a loop over the planes: load, shift right by the lane number, AND 1, shift left by the plane number, OR into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), polarity XOR, window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail (a DP, new start): key formation, three read-modify-write field stores of the 25-byte entry, the new start r + t' (1 add, 1 XOR with the polarity vector), insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Total below 3,550; charged **3,800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 1,024), slice counter: charged **1,300** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **4,200**; at most {cmax} cut trails (a halt on the third).
- Recovery batch (both lanes in one packed circuit, {PH7} operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch ({PH7p} per batch). The first l1 - l2 steps move one lane only and need no test ({PH7} + 13), also inside the 659.
- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; fixed part charged {setupfixed}. The generator: {gencalls} primitive calls (hash-consed gate constructors) and {PH} emitted lines, each charged 200 word operations: {gen}. Setup and generator together {setupall} operations = 2^{log2setup:.2f} units, charged in the time bound (3.4). The prefix scan (Section 8) is a separate one-time program of {scanops} operations = 2^{log2scan:.2f} units, charged in the same total and claimed as the preprocessing (preprocessing_log2 = 33.5).
Code size, instructions: loop body {body} + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery 640 (the {PH7}-operation circuit and its loop) + setup, cut and slice 160 = {instr} instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * {body} | {main} (= {mainsci}) |
| slice checks: ceil(B / 2^48) * 1,300 | {slices_sci} |
| stage-1 hits: e2max * 2,800 | {hits_sci} |
| finished trails: {tmax} * (3,800 + 3 * {tmax}) | {events} |
| cut trails: 2 * 4,200 | 8,400 |
| recovery: (c + 2^48) * {PH7p} + 600, c + 2^48 = 2^{log2capr:.3f} | {rec_sci} |
| setup and generator | {setupall} |
| prefix scan (Section 8): {scancand} candidates * {scanper} + 1 | {scanops} |
| polarity climb (Section 3.6): 200 * ({climbcalls} + {climbnodes}) + {climbevals} * 4,000 | {climbops} |
N = {N} = {Nsci} operations.
N / 638 = {Nunits} units = 2^{log2N:.6f}. Claim `time_log2` = {TL} (integer power certificate in Appendix A, rounded up with {slack:.1e} of slack). The main loop is {pmain:.2f} percent of it, recovery {prec:.2f} percent.

### 3.6 Polarity climb, generator code and peak storage of the setup
The input polarity vector `PINS` (256 bits) is computed by `climb_pins` of the shipped program (`python3 bsrho.py --climb` reruns it and checks the constants below). It starts at the all-zero vector (no outside constant), makes {climbevals_m1} steps, each flipping 1 to 3 of the input planes whose output polarity differs from their input polarity (and with probability 1/5 one random plane) and keeping the result when gates plus XORs with all-ones do not rise, with its own splitmix64 generator (seed 2; no dependence on the Python version). It ends at {PH} operations (the all-zero vector gives 18,960). The climb is a one-time program like the scan of Section 8: {climbevals} evaluations of the generator, {climbcalls} primitive calls and {climbnodes} nodes in all, charged 200 word operations per call and per node plus 4,000 per evaluation (mismatch list, flips, comparison): {climbops} operations = 2^{log2climb:.2f} units, a row of the ledger in Section 3.4 and part of the claimed preprocessing (scan and climb together 2^{log2pre:.3f} units, preprocessing_log2 = 33.5). Its result `PINS` is nonuniform advice of one 256-bit word, counted in the memory (Section 7) and declared in nonuniform_advice_log2_bytes = 6 with the prefix word i. The program takes `PINS` as the input polarity of the generator at setup.
The generator that builds the straight line at the start of the run is part of the machine code of this entry: the hash-consing network builder (`Gen`), `trace`, the reachability and emission pass (`Step.__init__`, `_last`) and the register allocator (`allocate`), which are {gencode} bytecode instructions (`python3 bsrho.py --gencode`, one instruction each) and are charged {gencode_ch} instructions * 36 bytes = {gencodebytes} bytes. Its peak storage (`gen_scratch` of the program, {nodes} nodes of the network): trace phase, node table 4 bytes per node (2-bit operation, two 15-bit operands) = {nbytes} bytes, hash-consing table 2^15 slots * 2 bytes = 65,536, signal state 10,240: {trace_phase} bytes; emit phase (the hash-consing table is dead), node table 4 + reachability mark 1 + last use 4 + register 2 = 11 bytes per node, a 2,048-byte heap and the state: {emit_phase} bytes. Peak scratch {scratch} bytes.
Layout. The setup phase holds the main code (counted at its final size, {codebytes} bytes; it is written as the generator emits it), the two advice words (64), the counters and plane copy (16,384), the generator's code image ({gencodebytes}) and its scratch ({scratch}): {ph1} bytes. The generator is never called after setup. In the search phase the same region holds the table ({tablebytes} bytes), the register file (32,768) and the counters: main code + advice + counters + register file + table = {ph2} bytes. The memory of the entry is the larger of the two, {ph2} bytes ({memspare} bytes to spare under 2^20); the region is {region} bytes against {genneed} bytes of generator image and scratch. The table size of Section 7 is the largest that fits with this layout.

### 3.5 Register file and smaller files
Premise H3: the machine has 1,024 registers of 256 bits. The generated line needs {regs} (peak live planes {peak}, no spills: `spill_ops(1024)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch, and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,024 (claimed) | {s1024} | {b1024} | {t1024} | {tp1024} | {tl1024:.5f} | {pl1024:.5f} |
| 512 | {s512} | {b512} | {t512} | {tp512} | {tl512:.5f} | {pl512:.5f} |
| 256 | {s256} | {b256} | {t256} | {tp256} | {tl256:.5f} | {pl256:.5f} |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= {regs}; 1,024 is declared.

## 4. Success probability

Heuristic H1 (premise, section 5): f behaves as a random mapping on N = 2^256 points for the points the search evaluates: for every set of distinct inputs, the outputs are
uniform and independent, and whether a value is a DP is an independent event of probability theta = {Tp} / 2^122. Then (sub-claims proved here, Lemma 2 is a computation under H1; the numbers below are printed by `python3 bsrho.py --loss`):

Lemma 1. A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and
the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S).
The key determines F (F < {Tp} < 2^8 and the key holds its 8 low bits), so equal keys of two DPs differ only if their bits above 177 differ. The lanes do not interact: the generated step applies the same function to every lane (section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2. Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 256 B = {Qratio:.5f} * 2^128. Under H1 (c) the DP indicators of the successive points of one trail are independent with probability theta, so the age of the trail of one lane at the halt (steps since its last restart) satisfies P(age >= a) <= (1 - theta)^a <= exp(-a / L), and the
256 ages are independent: each is stochastically dominated by an exponential with mean L. The sum of 256 such variables exceeds M L with probability at most exp(-256 (x - 1 - ln x)), x = M / 256 (Chernoff); for M = {M} this is {tailages:.2e} <= 1e-6. So the 256 unfinished trails hold at most {M} L points except with probability 1e-6.
Cut trails cost at most c + S, that is {f1:.4e} Q each; the number K of cut trails is Poisson with mean (Q / L) e^-{kappa} = {trails:.0f} e^-{kappa} = {mu:.4f} (P(K=0,1,2) = {pk0:.4f}, {pk1:.4f}, {pk2:.5f}; P(K>=3) = {pk3:.2e}, and the third cut is a halt, charged as failure).
The allowance 1.5e-4 Q already in U covers {allow:.2f} of one cut trail; for K = 1 and K = 2 the remaining loss lowers the success probability by {d1:.2e} and {d2:.2e} (slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = {slope:.3f} per unit of relative loss), and K >= 3 is charged as failure, so the cut-trail deficit is {pk1:.4f} * {d1:.2e} + {pk2:.5f} * {d2:.2e} + {pk3:.2e} * 0.3916 = {cutdef:.3e}. Hence U >= (1 - 1.5e-4) Q - {M} L - 1 = {Uratio:.5f} * 2^128 when K = 0 and the ages are within the bound. For U distinct inputs the probability of no colliding pair is
prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497) (the program's B is the least that gives U(U-1) >= 2 * 0.497 N). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^{log2inside:.2f} = {inside:.2e}. The expected number of key false matches (two different DP ends with the same 64-bit key: the key space is 2^56 * {Tp} = 2^{log2keys:.2f}) is below {tmax}^2 / 2 / 2^{log2keys:.2f} = {keyfm:.1e}.
Programmed aborts. Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations, binomial with mean Q / L = {trails:.0f} (and no more than a Poisson count of the same mean in the Chernoff bound); the abort needs {tmaxp1} or more, probability at most exp(-mean) (e mean / {tmaxp1})^{tmaxp1} = 2^{log2cap:.1f} = {cap:.1e} (Chernoff bound). Stage-1 budget: the number of stage-1 hits is at most binomial with
mean mu2 = Q / 2^32 = {mu2:.2e} and the abort needs 2 mu2 + 65, probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-{mu2c:.1e}). A recovery that finds no pair needs a key false match or a start lying on another trail (at most {keyfm:.1e} + 2^-100).
The losses add to {unf:.0e} + {inside:.2e} + {cutdef:.3e} + {keyfm:.1e} + {cap:.1e} + 7.9e-31 < {sumloss:.3e}, so P(success) >= 1 - e^-0.497 - {sumloss:.3e} = {Pl:.4f} >= 0.39. The {margin:.4f} left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= {eps:.4f}, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 has three parts: (a) for the inputs the search evaluates, the 256-bit outputs behave as uniform and independent values, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t
have the first-collision law of a random mapping; (c) the DP indicator is independent of the collision events. Parts (a) and (b) are premises on the fixed function f, K = 0, and cannot be tested at width 256. They are declared and not proved.
The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Section 4 and in the note.
The evidence for H1 is run by this program, in the organizer's sandbox, at reduced widths (Section 6), and the same program prints the statistics (`python3 bsrho.py --stats`, seeds from SHA-256 of a counter). The three tests are the same three as in the filed entry (a frozen plan written before any counted run; the organizer's seeds differ from the ones below):
T1 (family law, 3 rounds, fresh random 256-bit key K per run, chain truncated to n bits; scalar digest of the program): {t1line}
T2 (the fixed K = 0 function at full width 256, 256-bit digests from the bit-sliced circuit, 2048 points per trial and 256 trials; sources: uniform inputs, counter inputs r + i, iterates of f from 256 random starts, by trial index mod 3; seven 21-bit projections; equal pairs counted as points minus distinct values against C(2048, 2)/2^21 = 0.9995 per trial): {t2lines}
T3 (the search of Section 2 at width 18, DP = low 2 bits zero, 256 lanes, plan(18), one attempt per trial, no amplification, on the target chain K = 0 and on an ideal function of the same width, a keyed blake2b, fresh key per trial): {t3line}
Run by the organizer's pipeline on this program with the public seed (the numbers are reproducible; the pipeline reruns each experiment and requires identical output):
{orgsum}
Every unsuccessful attempt of the width-18 experiment ended with a halt of the program (the halts equal the unsuccessful trials); in a local run with other seeds all 76 halts of 256 attempts were "recovery found no pair", which is the case of a trail start lying on another trail. At width 18 this has probability about 0.3 per attempt; at width 256 it has probability below 2^-100 (Section 4). It happens equally for the ideal function (88 halts against 91). 
In the organizer's run the T3 target attempts and the T2 point sets are executed by the organizer's sandbox and every returned pair is recomputed by the organizer (Section 6): the number of trials that return a pair is the organizer-checked count of attempts that found a collision (T3) and of point sets that contain a collision of the 21-bit projection (T2). The remaining observations (ideal control, family law, the other six projections) are the program's own and are labelled as such.
These tests have limited power: 256 trials give a standard deviation of about 0.03 in a success frequency, and 85 trials per source give a standard deviation of about 9 in a pair count of 85. They show no deviation at the sizes run; they do not show that none exists. Larger earlier runs of T1 to T3 on the filed entry's program (the function with chaining value IV and flags 11, message 0^32 || x, per-batch search; the function of this entry differs in the 8 constant words of the chaining value and one flag word; not repeated here) gave: T1 n = 32, 2000 runs, ratio 1.0075 (z 0.64) and n = 40, 300 runs, ratio 0.9712 (z -0.95); T2 at width 256, 2^26 points per statistic, 42 statistics, observed / expected between 0.9546 and 1.0342, largest |z| 2.29; T3 n = 32, 4000 attempts each, target 0.443 against ideal 0.4535 (z -0.94), n = 40, 480 attempts each, 0.440 against 0.471 (z -0.97).
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; the bit-sliced search above width 18. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bsrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`bsrho-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low 2 bits zero, plan(18): {B18} batches, cut rule, table, recovery on the packed circuit) on the target chain K = 0 (the last block, chaining value CV); the trial returns the two 128-byte messages P || 0^32 || x, P || 0^32 || y when the attempt succeeded and two nulls otherwise. The checked event is that the complete 3-round digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 12.
`proj-k0-w256`: per trial, 2048 points of the K = 0 target at width 256 evaluated with the bit-sliced circuit (source by trial index mod 3), returning two points whose digests agree in the low 21 bits when the set contains such a pair. The checked event is that the digests agree in the low 21 bits and the messages are distinct. Observations (untrusted): equal-pair counts of seven projections.
They check the circuit at full width, the bit-sliced search, lane insertion and extraction, the table, the recovery and the message construction on the real target, and give organizer-counted success frequencies for T2 and T3 at the sizes above. They do not measure the cost or the success probability at width 256. Running times on the development machine: {t18} s and {t21} s.

## 7. Memory

Table: {tmax} entries * 25 bytes = {tablebytes} bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: {instr} instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = {codebytes} bytes (loop body {body}, handlers 1,000, recovery 640, setup, cut and slice 160).
Counters and copies: 16,384 bytes (trail numbers 512, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 1,024 registers, counted as memory: 32,768 bytes. The advice: 64 bytes (two 256-bit words: the prefix integer i, from which the program derives P and CV and writes the output P, and the polarity vector PINS). Total {mem} bytes <= 2^20 = 1,048,576. This is the search phase; the setup phase, in which the circuit generator runs, is smaller ({ph1} bytes, section 3.6). Claim `memory_log2_bytes` = 20. `python3 bsrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - {codebytes} - 32,768 - 16,384 - 64) / 25) = {tmax}, and Tp = {Tp} is the largest integer for which the table-capacity bound of section 4 stays below 2^-40 (Appendix A computes both).

## 8. The prefix P and its scan (nonuniform advice)

P is the 64-byte string whose little-endian words are w0 = i mod 2^32, w1 = i >> 32 and w2..w15 = 0, with i = {PREFIXI} (34 bits). The integer i is one of this entry's two nonuniform advice words (the other is PINS, Section 3.6): one 256-bit word, 32 bytes, counted in the memory total (Section 7); together they are declared as nonuniform_advice_log2_bytes = 6. The program derives P and CV from it (`PREFIX`, `CV`).
P was chosen by a one-time scan, whose program is shipped (`scan_prefix`, `scan_ops`, `scan_report`; `python3 bsrho.py --scan`). Candidate i = 0, 1, 2, ... gives the first block P(i); the scan computes CV(i) = chain_value(P(i)) and tests whether one 32-bit sum of the last block's circuit is zero: in round 0 of the last block the column calls 1 and 2 give A1 = v[1] and B2 = v[6], and the first addition of diagonal call 5 is
(A1 + B2) + m10, where m10 is a variable word of x. The condition is (A1 + B2) mod 2^32 = 0 (`prefix_condition`). It stops at the first i that passes. A candidate costs {scanper} operations ({scangen} to form the block, {scaninit} to set the 16 state words, 638 for the compression, {scancond} for the two G calls, the sum, the mask, the compare and the branch, {scanloop} for the loop);
the scan examined {scancand} candidates (i = 0 .. {PREFIXI}), so it costs {scanops} operations = 2^{log2scan:.4f} units, charged in the total (Section 3.4) and claimed as preprocessing_log2 = 33.5. The scan keeps 40 live words, within the 1,024 registers, with no load or store.
The reduced scan (condition mod 2^16) is rerun by `--scan`: first success at i = 20,832 after 20,833 candidates; the same command checks that the shipped i satisfies the full 32-bit condition. The 1.08e10 candidates of the full scan were run as a C program of the same arithmetic and were not rerun in the shipped Python program; the shipped program confirms that i passes the full condition and reproduces the reduced scan.
Effect on the circuit: with the condition, the sum of two circuit constants vanishes, and every constant bit of CV and of the flags changes which gates fold away in the bit-sliced generator. The step is {PH} operations with P and CV (flags 10) and the polarity vector of the climb of Section 3.6 (18,960 with the all-zero vector), against 19,022 operations for the filed bit-sliced entry's function (chaining value IV, flags 11) with its shipped polarity vector. The packed recovery circuit has {PH7} operations against 595. Only the one condition was searched; each further 32-bit condition would multiply the scan by 2^32 and was not searched.
P is not claimed to be random: the premise H1 is declared for the function f of this section's P, which is one fixed function; nothing in the argument depends on P beyond the shipped scan condition. The organizer experiments run the fixed-P function (their messages begin with P).

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 bsrho.py --ledger`.

```python
{appA}
```

Output:

```
{appOut}
```
"""

t18, t21 = "2.7", "4.1"
vals = dict(
    PH=st.ops, perlane=st.ops / 256, tmax=tmax, Tp=p["Tp"], log2L=log2(L), kappa=b.KAPPA_256,
    Lnum=L.numerator, Lden=L.denominator, B=p["B"], Qratio=Q / 2 ** 128, e2max=p["e2max"], c=p["c"], log2c=log2(p["c"]),
    regs=771, spare=1024 - 771, PH7=PH7, PH7p=PH7 + b.RECOVER_EXTRA, PREFIXI=b.PREFIX_I, scanper=b.SCAN_PER, scangen=b.SCAN_GEN, scaninit=b.SCAN_INIT, scancond=b.SCAN_COND, scanloop=b.SCAN_LOOP, scancand=fm(b.PREFIX_I + 1), scanops=fm(b.scan_ops()), log2scan=log2(b.scan_ops() / 638), nfix=len(st.fix), gates=st.gates, xor=st.by["x"], and_=st.by["a"], or_=st.by["o"],
    unit=st.ops / 256 / 638, filt=filt, loopops=b.LOOP_OPS, body=body, orops=29, cmax=b.CMAX, setupfixed=fm(b.SETUP_FIXED),
    gencalls=fm(st.gen_calls), gen=fm(lg["gen"]), setupall=fm(b.SETUP_FIXED + lg["gen"]), log2setup=log2((b.SETUP_FIXED + lg["gen"]) / 638),
    instr=fm(body + b.OTHER_CODE), main=fm(parts["main"]), mainsci="%.4e" % float(parts["main"]), slices_sci="%.3e" % float(parts["slices"]),
    hits_sci="%.4e" % float(parts["stage1_hits"]), events=fm(parts["events"]), log2capr=log2(p["capr"]), rec_sci="%.4e" % float(parts["recovery"]),
    climbevals=fm(b.CLIMB_EVALS), climbevals_m1=fm(b.CLIMB_EVALS - 1), climbcalls=fm(b.CLIMB_CALLS), climbnodes=fm(b.CLIMB_NODES), climbops=fm(lg['climb']), log2climb=log2(lg['climb'] / 638), log2pre=log2((b.scan_ops() + lg['climb']) / 638), gencode=fm(1595), gencode_ch=fm(b.GEN_CODE), gencodebytes=fm(b.GEN_CODE * b.INSTR_BYTES), nodes=fm(b.gen_scratch()[3]), nbytes=fm(4 * b.gen_scratch()[3]), trace_phase=fm(b.gen_scratch()[1]), emit_phase=fm(b.gen_scratch()[2]), scratch=fm(b.gen_scratch()[0]), ph1=fm(b.phase_bytes(code, tmax)[0]), ph2=fm(b.phase_bytes(code, tmax)[1]), memspare=b.MEM_LIMIT - b.phase_bytes(code, tmax)[1], region=fm(b.gen_idle(tmax)), genneed=fm(b.GEN_CODE * b.INSTR_BYTES + b.gen_scratch()[0]), N=fm(N), Nsci="%.6e" % N, Nunits="%.4e" % (N / 638), log2N=log2(N / 638), TL=TL, slack=TL - log2(N / 638), pmain=100 * frac["main"],
    prec=100 * frac["recovery"], peak=st.peak_live(),
    M=b.INFLIGHT, tailages=exp(-256 * (b.INFLIGHT / 256 - 1 - log(b.INFLIGHT / 256))), f1=f1, trails=ls["trails"], mu=mu, pk0=pk[0], pk1=pk[1], pk2=pk[2],
    pk3=1 - sum(pk), allow=1.5e-4 / f1, d1=(f1 - 1.5e-4) * slope, d2=(2 * f1 - 1.5e-4) * slope, slope=slope, cutdef=cut1 + cut2 + cut3,
    Uratio=U, log2inside=log2(ls["inside_trail"]), inside=ls["inside_trail"], log2keys=56 + log2(p["Tp"]), keyfm=ls["key_false_match"],
    tmaxp1=tmax + 1, log2cap=log2(ls["table_capacity"]), cap=ls["table_capacity"], mu2=float(Q) / 2 ** 32, mu2c=float(Q) / 2 ** 32 * (2 * log(2) - 1),
    unf=1e-6, sumloss=sumloss, Pl=ls["P_lower"], margin=ls["P_lower"] - 0.39, eps=eps,
    t1line=stats_txt[1], t2lines="; ".join(s.strip() for s in stats_txt[2:]) if False else "\n" + "\n".join("    " + s.strip() for s in stats_txt[2:]),
    t3line=stats_txt[0], B18=b.plan(18)["B"], t18=t18, t21=t21,
    tablebytes=fm(tmax * 25), codebytes=fm(code), mem=fm(25 * tmax + code + b.REGFILE + b.COUNTERS + b.ADVICE), appA=appA, appOut=appOut, orgsum=chr(10).join("    " + l for l in open(os.path.join(HERE, "organizer_summary.txt")).read().strip().split(chr(10))),
)
for R in (1024, 512, 256):
    s_, b_, t_, tp_, tl_, pl_ = rows_R[R]
    vals.update({"s%d" % R: fm(s_), "b%d" % R: fm(b_), "t%d" % R: fm(t_), "tp%d" % R: tp_, "tl%d" % R: tl_, "pl%d" % R: pl_})
text = proof.format(**vals)
open(os.path.join(PKG, "blake3", "proof.md"), "w", newline="\n", encoding="utf-8").write(text)
print("proof bytes", len(text.encode()), "lines", text.count("\n"))
print("eps", eps, "U", U, "Pl", ls["P_lower"], "sumloss", sumloss)
