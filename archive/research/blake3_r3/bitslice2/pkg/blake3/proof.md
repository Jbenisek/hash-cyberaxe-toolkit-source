# blake3-r3: plain birthday with 256 bit-sliced lanes and a fixed first block

Credited derivative of our own 0a9640ed (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges), itself a derivative of our own cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). It adds the two-block message mode with a fixed first block P, declared as nonuniform advice, that our entries a72f48eb and fc39027a used (the judges' ruling on a72f48eb: the two-block mode H4 is established; the prefix must be counted as advice, which this entry does). This entry keeps the relation, the trail-and-table search with distinguished points, the recovery walk, the
packed 7-lane circuit (now used by the recovery only), the ledger method and the form of the premise tests T1 to T3. It changes the circuit that evaluates the chain: the chain step is evaluated for 256 independent trails at once in bit-sliced form (one 256-bit word holds bit j of all 256 states),
so the 80 variable rotations of a step are renaming and cost nothing, and the step is 18869 operations for 256 trails, 73.71 per trail against 85 (595 / 7) for the packed circuit of the filed entry and 84.7 (593 / 7) for its two-block form. The price is a declared register file of 1,024 words of 256 bits (counted as memory), a longer program (20,707 instructions), a table of
10157 entries instead of 26,791, and 256 trails in flight at the halt instead of 7. No differential, no structure of the 3-round compression is used. The claim is the price of the birthday attack on the complete 3-round hash when the compression is evaluated for 256 instances at a time and every operation is counted.

## 1. Target and relation

Target `blake3-r3-prefix-v1`. Message mode (declared as heuristic H4, the two-block mode of our entries a72f48eb and fc39027a): the profile's message domain is "Finite byte strings of bit length below 2^64"; this entry's two colliding messages are 128 bytes,
M(x) = P || 0^32 || x with P a fixed 64-byte string (Section 8) and x a 256-bit integer (little endian). It is one chunk of two blocks. Block 1 = P (flags 1 = CHUNK_START, counter 0, length 64, chaining value IV) gives the chaining value CV = chain_value(P) (rounds 0..2, feed-forward v[i] XOR v[i+8] for i < 8).
Block 2 = 0^32 || x (words m0..m7 = 0, m8..m15 = the eight little-endian words of x, counter 0, block length 64, flags 10 = CHUNK_END|ROOT, chaining value CV) is the root compression; digest = the 8 words, little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit
little-endian integer. The attack outputs x != y with f(x) = f(y); then M(x) != M(y) are two distinct messages in the domain with equal 256-bit digests. The claim does not apply to a reading of the domain that excludes 128-byte strings. The scalar digest of the program (`digest_words`) was compared outside the shipped experiments with the organizer reference `blake3(M(x), 3)` on 300 random messages of this form: 0 differences.
The bit-sliced step was compared with the organizer reference on 1,024 random messages (one step) and on 64 messages chained for 4 steps: 0 differences; the packed recovery circuit on 7 messages: 0 differences. The program's own selftest (`python3 bsrho.py --selftest`) compares the bit-sliced step, the packed circuit and the register-allocated code with the scalar digest.

## 2. The attack (program `experiments/bsrho.py`, sections 3 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is
below Tp = 142. The density is theta = 142 / 2^122 and L = 1 / theta = 2^114.8503. The key of a DP is the 56 bits of x above bit 121 followed by the 8 low bits of F (F < 142 < 2^8, so those 8 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of all 256 lanes by the generated straight line of section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (section 3.3) forms the 256-bit mask of lanes whose 32 low digest bits are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, section 7) and
   start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 11 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 10157 keys, when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps, then step both together; at the first step
   with f(a) = f(b) and a != b output (a, b). Both lanes of one packed circuit (593 operations, used by nothing else) are used. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = 142, L = 2658455991569831745807614120560689152 / 71, B = 1376632466298024011573195735026287425, Q = 256 B = 1.03566 * 2^128 evaluations,
e2max = 164107378279927255102776972718, c = 411873463482649988787095145438980010 (= 2^118.310), table capacity tmax = 10157 entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= 10157, cut trails <= 2, plus the 256 starts) and every length is below c + S < 2^119, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; the only advice is the prefix word i = 10768619076 (Section 8), one 256-bit word counted as memory (nonuniform_advice_log2_bytes = 5).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry. The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores, and it gives no register count.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 1,024 registers (a premise of the entry, H3, Section 3.5 prices smaller files). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each.
The main loop has no loads, stores or moves: the generated straight line needs 771 registers (`allocate` in the program assigns them; output plane j is written into the register that held input plane j, so the next batch reads the same registers), leaving 253 of the 1,024 for the loop counter, the limit and the handlers' temporaries. The file of 1,024 registers is counted as memory: 32,768 bytes (section 7).
Constants are immediates. The organizer's reference count C(r3) = 638 (222, 430 and 638 for 1, 2 and 3 rounds) is used only as the unit: Unit = 638 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers.

### 3.2 One batch = 18869 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j is a 256-bit integer whose bit l is bit j of the word of lane l. A rotation is a renaming of planes (no operation). XOR, AND, OR of words are 32 operations each. The sum of two words is a ripple of full adders over the planes: with carry c, x = a xor c, y = b xor c, sum = x xor b, carry = (x and y) xor c (5 gates); the lowest bit has 2 gates (no carry in), the highest 3 (no carry out). The program generates the straight line at run time (`trace`, `Step`): constants (the chaining value CV, IV, the zero words m0..m7, length, flags) are folded at build time, gates are hash-consed,
a gate whose result no output uses is dropped, and each signal carries a polarity bit so that AND of an inverted and an upright plane costs 2 gates and AND/OR of two inverted planes 1. The chain feed is renaming: the 256 digest planes are the 256 input planes of the next batch. Output planes whose polarity differs from the input plane they feed are fixed by one XOR with the all-ones word; the program chose the input polarity vector by a hill climb at development time (constant `PINS`) and 120 of the 256 planes need the fix.
The generated line (`python3 bsrho.py --ledger`, `--selftest`): 18749 gates = 15694 XOR + 2305 AND + 750 OR, plus 120 XORs with all-ones = **18869 operations**. Per trail 73.707 operations = 0.1155 unit, against 1 unit for a compression and 0.1332 unit for the packed circuit.
Validation: 256 lanes against the scalar digest in the selftest; 1,024 lanes and 64 lanes chained for 4 steps against the organizer reference (section 1); the register-allocated code executed on a register file gives the same planes as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (section 3.3).

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 18869 + stage-1 test 35 + loop control 3 = 18907 operations. Stage 1: the 32 low planes of digest word 0 are combined into the mask of zero lanes: 29 ORs over the 30 upright planes, 1 AND over the 2 inverted planes (15 and 30), a complement and a combining OR, a final complement, a compare of the mask with zero and a branch: 35 operations (`stage1_ops`). The test loses no event: a DP has all 32 low bits zero, so its lane is flagged.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no flagged lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers):
- Stage-1 hit (a flagged lane): store the 256 planes to a 8 KiB copy in memory (256 stores), then a loop over the planes: load, shift right by the lane number, AND 1, shift left by the plane number, OR into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), polarity XOR, window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit. The hit budget e2max is enforced by a halt.
- Finished trail (a DP, new start): key formation, three read-modify-write field stores of the 25-byte entry, the new start r + t' (1 add, 1 XOR with the polarity vector), insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Total below 3,550; charged **3,800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 1,024), slice counter: charged **1,300** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **4,200**; at most 2 cut trails (a halt on the third).
- Recovery batch (both lanes in one packed circuit, 593 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch (657 per batch). The first l1 - l2 steps move one lane only and need no test (593 + 13), also inside the 659.
- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; fixed part charged 813,600. The generator: 42,942 primitive calls (hash-consed gate constructors) and 18869 emitted lines, each charged 200 word operations: 12,362,200. Setup and generator together 13,175,800 operations = 2^14.33 units, charged in the time bound (3.4). The prefix scan (Section 8) is a separate one-time program of 7,721,099,878,210 operations = 2^33.49 units, charged in the same total and claimed as the preprocessing (preprocessing_log2 = 33.5).
Code size, instructions: loop body 18907 + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery 640 (the 593-operation circuit and its loop) + setup, cut and slice 160 = 20,707 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 18907 | 26,027,990,040,296,739,986,814,411,762,142,016,344,475 (= 2.6028e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6.358e+24 |
| stage-1 hits: e2max * 2,800 | 4.5950e+32 |
| finished trails: 10157 * (3,800 + 3 * 10157) | 348,090,547 |
| cut trails: 2 * 4,200 | 8,400 |
| recovery: (c + 2^48) * 657 + 600, c + 2^48 = 2^118.310 | 2.7060e+38 |
| setup and generator | 13,175,800 |
| prefix scan (Section 8): 10,768,619,077 candidates * 717 + 1 | 7,721,099,878,210 |
N = 26,298,591,365,305,506,571,259,324,304,469,458,500,594 = 2.629859e+40 operations.
N / 638 = 4.1220e+37 units = 2^124.954697. Claim `time_log2` = 124.9547 (integer power certificate in Appendix A, rounded up with 3.3e-06 of slack). The main loop is 98.97 percent of it, recovery 1.03 percent.

### 3.5 Register file and smaller files
Premise H3: the machine has 1,024 registers of 256 bits. The generated line needs 771 (peak live planes 771, no spills: `spill_ops(1024)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch, and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,024 (claimed) | 0 | 18,907 | 10,157 | 142 | 124.95470 | 0.39121 |
| 512 | 862 | 19,769 | 9,571 | 133 | 125.02292 | 0.39124 |
| 256 | 3,422 | 22,329 | 6,212 | 82 | 125.23976 | 0.39129 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= 771; 1,024 is declared.

## 4. Success probability

Heuristic H1 (premise, section 5): f behaves as a random mapping on N = 2^256 points for the points the search evaluates: for every set of distinct inputs, the outputs are
uniform and independent, and whether a value is a DP is an independent event of probability theta = 142 / 2^122. Then (sub-claims proved here, Lemma 2 is a computation under H1; the numbers below are printed by `python3 bsrho.py --loss`):

Lemma 1. A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and
the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S).
The key determines F (F < 142 < 2^8 and the key holds its 8 low bits), so equal keys of two DPs differ only if their bits above 177 differ. The lanes do not interact: the generated step applies the same function to every lane (section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2. Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 256 B = 1.03566 * 2^128. Under H1 (c) the DP indicators of the successive points of one trail are independent with probability theta, so the age of the trail of one lane at the halt (steps since its last restart) satisfies P(age >= a) <= (1 - theta)^a <= exp(-a / L), and the
256 ages are independent: each is stochastically dominated by an exponential with mean L. The sum of 256 such variables exceeds M L with probability at most exp(-256 (x - 1 - ln x)), x = M / 256 (Chernoff); for M = 350 this is 8.88e-07 <= 1e-6. So the 256 unfinished trails hold at most 350 L points except with probability 1e-6.
Cut trails cost at most c + S, that is 1.1687e-03 Q each; the number K of cut trails is Poisson with mean (Q / L) e^-11 = 9412 e^-11 = 0.1572 (P(K=0,1,2) = 0.8545, 0.1343, 0.01056; P(K>=3) = 5.76e-04, and the third cut is a halt, charged as failure).
The allowance 1.5e-4 Q already in U covers 0.13 of one cut trail; for K = 1 and K = 2 the remaining loss lowers the success probability by 6.16e-04 and 1.32e-03 (slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss), and K >= 3 is charged as failure, so the cut-trail deficit is 0.1343 * 6.16e-04 + 0.01056 * 1.32e-03 + 5.76e-04 * 0.3916 = 3.222e-04. Hence U >= (1 - 1.5e-4) Q - 350 L - 1 = 0.99700 * 2^128 when K = 0 and the ages are within the bound. For U distinct inputs the probability of no colliding pair is
prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497) (the program's B is the least that gives U(U-1) >= 2 * 0.497 N). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^-13.10 = 1.14e-04. The expected number of key false matches (two different DP ends with the same 64-bit key: the key space is 2^56 * 142 = 2^63.15) is below 10157^2 / 2 / 2^63.15 = 5.0e-12.
Programmed aborts. Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations, binomial with mean Q / L = 9412 (and no more than a Poisson count of the same mean in the Chernoff bound); the abort needs 10158 or more, probability at most exp(-mean) (e mean / 10158)^10158 = 2^-41.6 = 3.1e-13 (Chernoff bound). Stage-1 budget: the number of stage-1 hits is at most binomial with
mean mu2 = Q / 2^32 = 8.21e+28 and the abort needs 2 mu2 + 65, probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.2e+28). A recovery that finds no pair needs a key false match or a start lying on another trail (at most 5.0e-12 + 2^-100).
The losses add to 1e-06 + 1.14e-04 + 3.222e-04 + 5.0e-12 + 3.1e-13 + 7.9e-31 < 4.371e-04, so P(success) >= 1 - e^-0.497 - 4.371e-04 = 0.3912 >= 0.39. The 0.0012 left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0040, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 has three parts: (a) for the inputs the search evaluates, the 256-bit outputs behave as uniform and independent values, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t
have the first-collision law of a random mapping; (c) the DP indicator is independent of the collision events. Parts (a) and (b) are premises on the fixed function f, K = 0, and cannot be tested at width 256. They are declared and not proved.
The full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Section 4 and in the note.
The evidence for H1 is run by this program, in the organizer's sandbox, at reduced widths (Section 6), and the same program prints the statistics (`python3 bsrho.py --stats`, seeds from SHA-256 of a counter). The three tests are the same three as in the filed entry (a frozen plan written before any counted run; the organizer's seeds differ from the ones below):
T1 (family law, 3 rounds, fresh random 256-bit key K per run, chain truncated to n bits; scalar digest of the program): T1 n=12 fresh K: 256 runs, mean first-repeat 80.05, ratio to sqrt(pi N/2) 0.9979 (z -0.06), E[T^2]/2N 0.997
T2 (the fixed K = 0 function at full width 256, 256-bit digests from the bit-sliced circuit, 2048 points per trial and 256 trials; sources: uniform inputs, counter inputs r + i, iterates of f from 256 random starts, by trial index mod 3; seven 21-bit projections; equal pairs counted as points minus distinct values against C(2048, 2)/2^21 = 0.9995 per trial): 
    T2 width 256, K=0: 2048 points, 21-bit projections, expected equal pairs per trial 0.9995, P(>=1) 0.6319
    source uniform (86 trials): returned pairs 56 (expected 54.3); w0 77/86.0 z -0.97; w3 90/86.0 z 0.44; w7 85/86.0 z -0.10; xor8 78/86.0 z -0.86; sum8 94/86.0 z 0.87; p01 93/86.0 z 0.76; p23 92/86.0 z 0.65
    source counter (85 trials): returned pairs 54 (expected 53.7); w0 83/85.0 z -0.21; w3 77/85.0 z -0.86; w7 72/85.0 z -1.41; xor8 95/85.0 z 1.09; sum8 83/85.0 z -0.21; p01 75/85.0 z -1.08; p23 76/85.0 z -0.97
    source iterates (85 trials): returned pairs 60 (expected 53.7); w0 93/85.0 z 0.87; w3 70/85.0 z -1.62; w7 76/85.0 z -0.97; xor8 85/85.0 z 0.00; sum8 85/85.0 z 0.00; p01 90/85.0 z 0.55; p23 74/85.0 z -1.19
T3 (the search of Section 2 at width 18, DP = low 2 bits zero, 256 lanes, plan(18), one attempt per trial, no amplification, on the target chain K = 0 and on an ideal function of the same width, a keyed blake2b, fresh key per trial): T3 n=18: target 163/256 (0.637) ideal 182/256 (0.711) two-proportion z -1.79
Run by the organizer's pipeline on this program with the public seed (the numbers are reproducible; the pipeline reruns each experiment and requires identical output):
    bsrho-n18 (organizer run, public seed): 176 of 256 trials returned a pair that the organizer verified (0.688); ideal-function control 167 of 256; two-proportion z 0.85; family-law runs at n = 12: mean first repeat 82.56, ratio to sqrt(pi N/2) 1.0293 (z 0.90), E[T^2]/2N 1.058; halts target 80, ideal 88.
    proj-k0-w256 (organizer run): 162 of 256 trials returned a verified pair (expected 161.8); by source: uniform 54 of 86 (expected 54.3); counter 47 of 85 (expected 53.7); iterates 61 of 85 (expected 53.7); equal pairs in the seven projections, total over 256 trials against 255.9 expected: w0 260, w3 256, w7 281, xor8 241, sum8 246, p01 277, p23 252; z 0.26, 0.01, 1.57, -0.93, -0.62, 1.32, -0.24.
Every unsuccessful attempt of the width-18 experiment ended with a halt of the program (the halts equal the unsuccessful trials); in a local run with other seeds all 76 halts of 256 attempts were "recovery found no pair", which is the case of a trail start lying on another trail. At width 18 this has probability about 0.3 per attempt; at width 256 it has probability below 2^-100 (Section 4). It happens equally for the ideal function (88 halts against 91). 
In the organizer's run the T3 target attempts and the T2 point sets are executed by the organizer's sandbox and every returned pair is recomputed by the organizer (Section 6): the number of trials that return a pair is the organizer-checked count of attempts that found a collision (T3) and of point sets that contain a collision of the 21-bit projection (T2). The remaining observations (ideal control, family law, the other six projections) are the program's own and are labelled as such.
These tests have limited power: 256 trials give a standard deviation of about 0.03 in a success frequency, and 85 trials per source give a standard deviation of about 9 in a pair count of 85. They show no deviation at the sizes run; they do not show that none exists. Larger earlier runs of T1 to T3 on the filed entry's program (the function with chaining value IV and flags 11, message 0^32 || x, per-batch search; the function of this entry differs in the 8 constant words of the chaining value and one flag word; not repeated here) gave: T1 n = 32, 2000 runs, ratio 1.0075 (z 0.64) and n = 40, 300 runs, ratio 0.9712 (z -0.95); T2 at width 256, 2^26 points per statistic, 42 statistics, observed / expected between 0.9546 and 1.0342, largest |z| 2.29; T3 n = 32, 4000 attempts each, target 0.443 against ideal 0.4535 (z -0.94), n = 40, 480 attempts each, 0.440 against 0.471 (z -0.97).
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; the bit-sliced search above width 18. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bsrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`bsrho-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 8 batches, cut rule, table, recovery on the packed circuit) on the target chain K = 0 (the last block, chaining value CV); the trial returns the two 128-byte messages P || 0^32 || x, P || 0^32 || y when the attempt succeeded and two nulls otherwise. The checked event is that the complete 3-round digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 12.
`proj-k0-w256`: per trial, 2048 points of the K = 0 target at width 256 evaluated with the bit-sliced circuit (source by trial index mod 3), returning two points whose digests agree in the low 21 bits when the set contains such a pair. The checked event is that the digests agree in the low 21 bits and the messages are distinct. Observations (untrusted): equal-pair counts of seven projections.
They check the circuit at full width, the bit-sliced search, lane insertion and extraction, the table, the recovery and the message construction on the real target, and give organizer-counted success frequencies for T2 and T3 at the sizes above. They do not measure the cost or the success probability at width 256. Running times on the development machine: 2.7 s and 4.1 s.

## 7. Memory

Table: 10157 entries * 25 bytes = 253,925 bytes. An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 20,707 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 745,452 bytes (loop body 18907, handlers 1,000, recovery 640, setup, cut and slice 160).
Counters and copies: 16,384 bytes (trail numbers 512, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 1,024 registers, counted as memory: 32,768 bytes. The advice word: 32 bytes (one 256-bit word holding the prefix integer i; P and CV are derived from it by the program, the output of P is written from it). Total 1,048,561 bytes <= 2^20 = 1,048,576. Claim `memory_log2_bytes` = 20. `python3 bsrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 745,452 - 32,768 - 16,384 - 32) / 25) = 10157, and Tp = 142 is the largest integer for which the table-capacity bound of section 4 stays below 2^-40 (Appendix A computes both).

## 8. The prefix P and its scan (nonuniform advice)

P is the 64-byte string whose little-endian words are w0 = i mod 2^32, w1 = i >> 32 and w2..w15 = 0, with i = 10768619076 (34 bits). The integer i is this entry's nonuniform advice: one 256-bit word, 32 bytes, counted in the memory total (Section 7) and declared as nonuniform_advice_log2_bytes = 5. The program derives P and CV from it (`PREFIX`, `CV`).
P was chosen by a one-time scan, whose program is shipped (`scan_prefix`, `scan_ops`, `scan_report`; `python3 bsrho.py --scan`). Candidate i = 0, 1, 2, ... gives the first block P(i); the scan computes CV(i) = chain_value(P(i)) and tests whether one 32-bit sum of the last block's circuit is zero: in round 0 of the last block the column calls 1 and 2 give A1 = v[1] and B2 = v[6], and the first addition of diagonal call 5 is
(A1 + B2) + m10, where m10 is a variable word of x. The condition is (A1 + B2) mod 2^32 = 0 (`prefix_condition`). It stops at the first i that passes. A candidate costs 717 operations (5 to form the block, 16 to set the 16 state words, 638 for the compression, 56 for the two G calls, the sum, the mask, the compare and the branch, 2 for the loop);
the scan examined 10,768,619,077 candidates (i = 0 .. 10768619076), so it costs 7,721,099,878,210 operations = 2^33.4945 units, charged in the total (Section 3.4) and claimed as preprocessing_log2 = 33.5. The scan keeps 40 live words, within the 1,024 registers, with no load or store.
The reduced scan (condition mod 2^16) is rerun by `--scan`: first success at i = 20,832 after 20,833 candidates; the same command checks that the shipped i satisfies the full 32-bit condition. The 1.08e10 candidates of the full scan were run as a C program of the same arithmetic and were not rerun in the shipped Python program; the shipped program confirms that i passes the full condition and reproduces the reduced scan.
Effect on the circuit: with the condition, the sum of two circuit constants vanishes, and every constant bit of CV and of the flags changes which gates fold away in the bit-sliced generator. Measured at development time with the same generator and the same polarity hill climb (the climb itself is not shipped; the shipped constant `PINS` is its result): the step is 18869 operations with P and CV (flags 10), against 19,014 operations for the filed bit-sliced entry's function (chaining value IV, flags 11) after the same polarity hill climb, and 19,022 for the filed entry's polarity vector. The packed recovery circuit has 593 operations against 595. Only the one condition was searched; each further 32-bit condition would multiply the scan by 2^32 and was not searched.
P is not claimed to be random: the premise H1 is declared for the function f of this section's P, which is one fixed function; nothing in the argument depends on P beyond the shipped scan condition. The organizer experiments run the fixed-P function (their messages begin with P).

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 bsrho.py --ledger`.

```python
from fractions import Fraction
from math import isqrt, log, exp, log2

PH, FILT, LOOP, LANES = 18869, 35, 3, 256      # operations of the bit-sliced step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 42942                               # generator primitive calls (python3 bsrho.py --ledger)
PH7, EXTRA = 593, 64                            # packed recovery circuit, extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 11          # width, stage-1 bits, window bits (D = 122), age cap in units of L
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE = 36, 1800, 1024 * 32, 16384, 25, 32
SCAN_PER, PREFIX_I = 5 + 16 + 638 + 56 + 2, 10768619076    # operations per scan candidate (proof 8), the prefix integer
TAIL_AGES = 1e-6


def inflight_m():                               # smallest M with P(sum of 256 exponential ages > M L) <= 1e-6 (Chernoff)
    m = LANES
    while exp(-LANES * (m / LANES - 1 - log(m / LANES))) > TAIL_AGES:
        m += 1
    return m


M = inflight_m()
body = PH + FILT + LOOP                                        # one batch = one loop body = 19,060 operations
code_bytes = (body + OTHER_CODE) * INSTR
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def plan(Tp):
    L = Fraction(1 << D, Tp)                                   # trail length scale 1/theta, theta = Tp / 2^D
    ureq = isqrt(2 * Nn * LAM.numerator // LAM.denominator) + 2
    num, den = ureq + M * L + 1, CUT.denominator
    q = -(-(num * den) // (den - CUT.numerator))
    b = -(-q // LANES)
    c = -(-KAPPA * L.numerator // L.denominator)
    return L, b, c


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


Tp = max(t for t in range(1, 4097)
         if float(plan(t)[1] * LANES / plan(t)[0]) < tmax + 1
         and tail_log2(float(plan(t)[1] * LANES / plan(t)[0]), tmax + 1) <= -40)
L, B, c = plan(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 18907", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 4200", CMAX * CUTOPS),
        ("recovery: (c + 2^48) * (593 + 64) + 600", capr * (PH7 + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen),
        ("prefix scan: (i + 1) * 717 + 1", (PREFIX_I + 1) * SCAN_PER + 1)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("M =", M, " Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 638
a = (N ** P // C ** P).bit_length() - 1                        # 2^a * C^P <= N^P < 2^(a+1) * C^P
while (1 << (a + 1)) * C ** P <= N ** P:
    a += 1
while (1 << a) * C ** P > N ** P:
    a -= 1
print("certificate: 2^%d * %d^%d <= N^%d < 2^%d * %d^%d" % (a, C, P, P, a + 1, C, P))
print("log2(N/C) = %.10f" % (log2(N) - log2(C)))
print("time_log2 = %.5f" % ((a + 1) / P))
```

Output:

```
M = 350  Tp = 142  tmax = 10157  B = 1376632466298024011573195735026287425  e2max = 164107378279927255102776972718  c = 411873463482649988787095145438980010
memory bytes = 1048561
main loop: B * 18907                                 26027990040296739986814411762142016344475
slice checks: ceil(B / 2^48) * 1300                  6358015291807217348624600
stage-1 hits: e2max * 2800                           459500659183796314287775523610400
finished trails: tmax * (3800 + 3 * tmax)            348090547
cut trails: 2 * 4200                                 8400
recovery: (c + 2^48) * (593 + 64) + 600              270600865508101042633306439613108768162
setup and generator                                  13175800
prefix scan: (i + 1) * 717 + 1                       7721099878210
N = 26298591365305506571259324304469458500594
certificate: 2^12495469 * 638^100000 <= N^100000 < 2^12495470 * 638^100000
log2(N/C) = 124.9546967081
time_log2 = 124.95470
```
