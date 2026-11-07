# sha256-r39: plain birthday search with 7 packed lanes per 256-bit word

This is the first entry on this lane. It is a credited derivative of our own earlier blake3 round-3 entries on other boards: 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822), 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), cf8b0e92-4302-4813-907a-3c970c102646 (125.10041, the packed-lane chain), our Pareto entry 62cfd777 (blake3 round 3, 124.8123), and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087), whose relation and trail-and-table search with distinguished points we reuse. A Pareto submission may list dependencies only from its own challenge, and this lane has no submission yet, so no dependency is declared; the credit is given in this text. What is reused: the search with distinguished points, the handlers, the recovery walk, the ledger method and the form of the success argument. What is new here: the compression is 39-step SHA-256, the kernel is a generated straight line of 2426 operations that evaluates 7 chains in the 36-bit lanes of a 256-bit word, and every number is recomputed for this target.
The target is the plain one: the message is the 32-byte string x, one block with FIPS padding, standard IV, 39 steps, feed-forward, the complete 256-bit digest; no prefix, no advice, no differential or structural property of the 39 steps is used. The chain step is 2426 operations for 7 trails (347.57 per trail, 0.1236 of the 2812 operations of one reference compression). The price is a declared register file of 64 words of 256 bits (counted as memory, every transfer charged; the line needs 43), a program of 5,523 instructions of 36 bytes and a table of 33,662 entries.

## 1. Target and relation

Target `sha256-r39-prefix-v1` (the Pareto lane `sha256`, round 39). The two colliding messages are 32 bytes: M(x) = the 256-bit integer x written big-endian. FIPS 180-4 padding makes one block: words W0..W7 are the eight big-endian 32-bit words of M(x), W8 = 0x80000000, W9..W14 = 0, W15 = 0x100 (the length in bits). The compression executes the steps with indices 0 to 38 of the standard schedule and constants, starts from the standard IV, and adds the incoming state to the working state at the end; the digest is the eight state words, big-endian (this is `verifier/hash_functions.py:digest(M(x), "sha256", 39)`). Write f(x) for the digest read as a 256-bit big-endian integer.
The walk is x -> f(x); the digest words H0..H7 are the next input words W0..W7. The attack outputs x != y with f(x) = f(y); M(x) != M(y) are two distinct messages with equal complete 256-bit digests (a 32-byte string is in the profile's message domain, "finite byte strings of bit length below 2^64").
The scalar digest of the program (`digest_words`) was compared outside the shipped experiments with the organizer reference `digest(M(x), "sha256", 39)` on 300 random messages: 0 differences. The packed kernel (`ext_regress.py`, not shipped) was compared with the reference on 8,197 random messages (one step) and on 7 chains of 64 steps; 0 differences in each. (The same check confirmed that the organizer reference at 64 steps equals hashlib.sha256 on 50 messages.) The program's own selftest (`python3 shrho.py --selftest`) compares the kernel with the scalar compression on 4,102 lanes (586 batches of 7, the full 256-bit f), on all-zero and all-one inputs, on 7 lanes chained for 4 steps, runs the register-allocated code on a register file, and runs the width-18 chain and search.

## 2. The attack (program `experiments/shrho.py`, sections 4 to 6)

Parameters for n = 256: N = 2^256, 7 lanes. A point x is distinguished (a DP) when its low 32 bits are zero (the word W7 of M(x)) and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 505. The density is theta = 505 / 2^122 and L = 1 / theta = 2^113.0199. The key of a DP is the 55 bits of x above bit 121 followed by the 9 low bits of F (F < 505 < 2^9, so those bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> f(x) until a DP.
1. 7 trails run in the 7 lanes: lane l of the packed words holds the current point of its trail. A batch is one evaluation of f for all 7 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the mask of lanes whose low 32 bits (packed word 7) are all zero. If it is zero, the next batch runs at once.
3. For each set lane (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, Section 7) and start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 12 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 33,662 keys, when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of f, then step both together; at the first step with f(a) = f(b) and a != b output (a, b). Both lanes of one evaluation of the same kernel (the 2426 operations appear twice in the program, in the loop and in the recovery routine) are used, with an exact equality test of the two lanes on the 8 output words. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 shrho.py --ledger`): Tp = 505, L = 5316911983139663491615228241121378304 / 505, B = 48521120621377244089789062617386381958, Q = 7 B = 0.99814 * 2^128 evaluations, e2max = 158160852431152345905324182686, c = 126342462965694974058183641373181267 (= 2^116.605), table capacity tmax = 33,662 entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= 33,662, cut trails <= 2, plus the 7 starts) and every length is below c + S < 2^119, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice.

## 3. Operation ledger

### 3.1 Machine
Machine convention declared by this entry (supporting heuristic H3; the benchmark fixes none of the three points below). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores; it gives no register count, no rule for constants and no rule for packing several independent computations into one word.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 64 registers (Section 3.5 prices smaller files and the absence of immediates). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word, one operation each; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each. Constants (masks, the round constants, the IV words) are immediate operands, as in the organizer's reference count, which charges none for them. A word holds 7 independent values (lanes) of 36 bits; one machine operation on the word is one operation, the cost model pricing a word operation at 1/C whatever the word holds.
The main loop has no loads, stores or moves: the generated straight line needs 43 registers (`allocate` in the program assigns them; output word j is written into the register that held input word j, so the next batch reads the same registers), leaving 21 of the 64 for the loop counter, the limit and the handlers' temporaries. The register file is counted as memory: 2,048 bytes (Section 7).
The organizer's reference count C(sha256-r39) = 2812 (2,644 for 37 steps and 2,728 for 38 in the benchmark's table; the value for 39 is computed by the organizer's counter, `reference_operation_cost` 2812 in `pareto_candidate.py --family sha256 --rounds 39 --show-contract`) is used only as the unit: Unit = 2812 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers; the straight line is not given a shorter encoding.

### 3.2 One batch = 2433 operations for 7 trails
Representation: lane l of a packed word occupies bits 36 l to 36 l + 35 of the 256-bit word (7 lanes, 252 bits): 32 data bits and 4 guard bits above them. The kernel is a straight line of 2426 operations on registers and immediates of the form REP * c (REP has a 1 at bit 36 l of every lane; c a 32-bit constant): add, AND, OR, XOR, shift left and shift right by an immediate.
Field invariant, enforced by the generator (`Tracer`): every register carries an upper bound on the value of a lane; the data bits of a result are always the 32-bit result of the corresponding SHA-256 expression, because additions are emitted only when the sum of the two bounds stays below 2^36 (otherwise the larger operand is first ANDed with REP * 0xFFFFFFFF), so no carry leaves a lane, and XOR and AND never leave the lane. The low 32 bits of a sum depend only on the low 32 bits of the operands, so garbage in the guard bits is harmless to the data bits. Rotation by r of the 32-bit lane: (x >> r) AND REP * (2^(32-r) - 1), then (x << (32-r)) AND REP * ((2^r - 1) << (32-r)), then OR: 5 operations. The first mask removes the bits that cross in from the next lane and the guard bits of the lane itself, which land at bit 32 - r and above; the second removes everything but the r wrapped bits (shifted-up guard bits land at bit 32 or above, and bits that overflow into the next lane land below bit 32 - r), so a rotation is correct for any lane value below 2^36 and needs no clean input. A shift right by k (the sigma functions) is 2 operations. The top lane's shifted-out bits (above bit 255) are lost in the machine and are masked off in every use.
Lines of the kernel (counted by the tracer; `python3 shrho.py --selftest` prints the counts per operation): 2426 = 1,500 rotation operations (300 rotations of 5) + 72 for 36 shifts right + 375 XOR + 76 AND (the choice and majority functions) + 316 additions + 87 masks that keep sums below 2^36. Per step of the compression: Sigma0 and Sigma1 are 17 operations each (3 rotations and 2 XOR); the choice is 3 (g ^ (e & (f ^ g))), the majority is 3 (it reuses the XOR a ^ b of the previous step as b ^ c); 7 additions (four for T1, one for T2, one for the new a, one for the new e) and 2 masks (new a, new e). Each schedule word W16..W38 costs 14 + 14 operations for the two sigma functions and 3 additions (and a mask when the bound requires it). The first steps fold the constant IV and the constant words W8..W15 at build time; the IV is added again in the feed-forward (8 additions, with the masks they need).
Validation: 4,102 lanes against the scalar digest in the selftest; 8,197 messages and 7 lanes chained for 64 steps against the organizer reference (Section 1); the register-allocated code executed on a register file gives the same words as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 2426 + stage-1 test 4 + loop control 3 = 2433 operations. Stage 1: the packed word 7 of the output (the low 32 bits of the next point, guard bits clear because the kernel's outputs are masked) is added to REP * 0xFFFFFFFF, ANDed with REP << 32 (bit 32 of a lane is set exactly when the lane's low word is non-zero), compared with REP << 32 and a branch: 4 operations (`FILT_OPS`). The test loses no event: a DP has all 32 low bits zero, so its bit 32 stays clear and the comparison fails.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no hit lane (probability about 1 - 2^-29) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers; every operation is one of the model's primitives):
- Stage-1 hit: XOR with REP << 32 gives the hit lanes at bit 36 l + 32. Scanning the 7 lanes costs at most 7 * 7 = 49 operations (shift by 36 l, AND, branch, increment, compare, branch). For a hit lane (shift register s = 36 l): the words 6, 5 and 4 are extracted ((P >> s) AND 0xFFFFFFFF: 2 operations each), the window test F < Tp is a compare and branch on word 6 and two zero tests on word 5 and on word 4 AND (2^26 - 1): 13 operations. Total below 100 per hit lane; charged **400** per hit lane (the hit budget e2max is enforced by a halt).
- Finished trail (a DP, new start): extraction of words 3 and 2 and key formation (about 25 operations), three read-modify-write field stores of the 25-byte entry (about 30), length = b - birth (3), the new start r + t' (1 add), insertion of its 256 bits in the lane: for each of the 8 words extract (2), shift left by s (1), clear the lane in the packed word (1) and OR (1): 40, plus the lane mask (2), lane arrays and counters (about 20). Total below 200; charged **800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 7 births (load, subtract, compare, branch: 4 each) and the slice counter: charged **120** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **800**; at most 2 cut trails (a halt on the third).
- Recovery batch (both lanes in one evaluation of the kernel, 2426 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the inputs (needed to output the colliding pair): 39, charged as 64 per recovery batch (2490 per batch). The first l1 - l2 steps move one lane only and need no test, also inside the 2490.
- Setup and generator: 1 random word; the 7 starts r + t inserted in the lanes; counters; fixed part charged 4,800. The generator: 3,468 calls of the tracer and 2426 emitted lines, each charged 400 word operations: 2,357,600. Setup and generator together 2,362,400 operations = 2^9.71 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size, instructions: loop body 2433 + recovery copy of the kernel with its test 2490 + handlers, key scan, cut and slice checks and setup 600 = 5,523 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 2433 | 118,051,886,471,810,834,870,456,789,348,101,067,303,814 (= 1.1805e+41) |
| slice checks: ceil(B / 2^48) * 120 | 2.069e+25 |
| stage-1 hits: e2max * 400 | 6.3264e+31 |
| finished trails: 33,662 * (800 + 3 * 33,662) | 3,426,320,332 |
| cut trails: 2 * 800 | 1,600 |
| recovery: (c + 2^48) * (2426 + 64) + 600, c + 2^48 = 2^116.605 | 3.1459e+38 |
| setup and generator | 2,362,400 |
N = 118,366,479,267,859,777,014,121,178,925,464,971,134,656 = 1.183665e+41 operations.
N / 2812 = 4.2093e+37 units = 2^124.984932. Claim `time_log2` = 124.98494 (integer power certificate in Appendix A, rounded up with 8.4e-06 of slack). The main loop is 99.73 percent of it, recovery 0.27 percent.

### 3.5 Register file, immediates and smaller files
Premise H3: the machine has 64 registers of 256 bits. The generated line needs 43 (peak live words 39, no spills: `spill_ops(64)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch (to the recovery copy too), and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 64 (claimed) | 0 | 2,433 | 33,662 | 505 | 124.98493 | 0.39115 |
| 32 | 14 | 2,447 | 33,662 | 505 | 124.99321 | 0.39115 |
| 16 | 57 | 2,490 | 33,559 | 504 | 125.01835 | 0.39115 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= 43; 64 is declared.
Immediates. The kernel has 788 operations with a 256-bit immediate operand (78 distinct patterns: the lane masks of the rotations and shifts, 0xFFFFFFFF, the round constants, the IV words). If the machine had no immediates, the 21 registers left over could hold the 21 most used patterns for the whole run (loaded once at setup) and every other use would be one load: 95 loads per batch (also in the recovery copy), table 33,388 entries, time_log2 125.04023.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry: the tracer (`Tracer`, with `build_lines`) and the register allocator (`allocate`), which are 1,167 bytecode instructions (`python3 shrho.py --gencode`, one instruction each) and are charged 1,170 instructions * 36 bytes = 42,120 bytes. It keeps no node table: the emitted lines are the code records themselves. Its scratch (model `GEN_SCRATCH` = 16,384 bytes): the last use and the register of each emitted line (2 + 2 bytes each, 2426 lines), 256 free-register flags, the output marks, and the 16-byte values of the 39 schedule words and the state.
Layout. The setup phase holds the main code (counted at its final size, 198,828 bytes; it is written as the generator emits it), the counters (6,144), the generator's code image (42,120) and its scratch (16,384): 263,476 bytes. The generator is never called after setup. In the search phase the same region holds the table (841,550 bytes), the register file (2,048) and the counters: main code + counters + register file + table = 1,048,570 bytes. The memory of the entry is the larger of the two, 1,048,570 bytes (6 bytes to spare under 2^20); the region is 849,742 bytes against 58,504 bytes of generator image and scratch. The table size of Section 7 is the largest that fits.
Measured peak memory of the generator (not the machine model, which is the byte account above): (i) the circuit generator written in freestanding C (source embedded in `experiments/shrho.py` as `GEN_C`, printed by `python3 shrho.py --gen-c`, 9,295 bytes) compiled to WebAssembly and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: 2,426 instructions, 43 registers, 3,468 tracer calls, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total 218,820 bytes, of which 198,828 are the code region (36-byte records) and 6,144 the counters; its scratch is 13,096 bytes and its values 752 bytes; it needs 1,267,939 wasm operations, below the 2,357,600 word operations the ledger charges for the generator. The guest links in 4 pages. (ii) The Python generator alone has a peak resident set of tens of megabytes (the interpreter and its objects); that is the footprint of the interpreter, not of the machine model, and it is not charged.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 9.8, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (263,476 bytes), and nothing it produces is stored outside the 1,048,570 bytes of the search phase.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values. The attack uses the walk function only by evaluating f at points that the procedure chooses. Write A_F for the same procedure with every evaluation of f replaced by F (lazy sampling), and P_F for its success probability, taken over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Sub-claims under it (the numbers below are printed by `python3 shrho.py --loss`) are computations for the random function F, with the approximations named as the supporting heuristic H2 (they are not proved here):
H2 (a) the age of the trail of one lane at the halt is dominated by an exponential with mean L, and the 7 ages are independent, although restarts depend on the history of the run; (b) the number of cut trails is Poisson with the stated mean; (c) the loss for a cut trail enters linearly with the stated slope; (d) trail lengths are geometric with mean L (used for the repeats inside one trail).

Lemma 1 (a statement about f itself, no premise). A pair x != y of evaluated inputs on two different finished trails with f(x) = f(y) is output: both trails continue identically from f(x), so they end at the same DP with the same key and the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies f(x) = f(y) with x != y; the recovery checks equality before it returns.
The key determines F (F < 505 < 2^9 and the key holds its 9 low bits), so equal keys of two DPs differ only if their bits above 121 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds f^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F, under H2). Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 7 B = 0.99814 * 2^128. For F the DP indicators of the successive points of one trail are independent with probability theta, so the age of the trail of one lane at the halt (steps since its last restart) satisfies P(age >= a) <= (1 - theta)^a <= exp(-a / L), and (H2 a) the 7 ages are independent: each is stochastically dominated by an exponential with mean L. The sum of 7 such variables exceeds M L with probability at most exp(-7 (x - 1 - ln x)), x = M / 7 (Chernoff); for M = 32 this is 5.79e-07 <= 1e-6. So the 7 unfinished trails hold at most 32 L points except with probability 1e-6.
Cut trails cost at most c + S, that is 3.7198e-04 Q each; the number K of cut trails is (H2 b) Poisson with mean (Q / L) e^-12 = 32260 e^-12 = 0.1982 (P(K=0,1,2) = 0.8202, 0.1626, 0.01611; P(K>=3) = 1.12e-03, and the third cut is a halt, charged as failure).
The allowance 1.5e-4 Q already in U covers 0.40 of one cut trail; for K = 1 and K = 2 the remaining loss lowers the success probability by 1.34e-04 and 3.59e-04 (H2 c: slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss), and K >= 3 is charged as failure, so the cut-trail deficit is 0.1626 * 1.34e-04 + 0.01611 * 3.59e-04 + 1.12e-03 * 0.3916 = 4.660e-04. Hence U >= (1 - 1.5e-4) Q - 32 L - 1 = 0.99700 * 2^128 when K = 0 and the ages are within the bound. For U distinct inputs the probability of no colliding pair is
prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497) (the program's B is the least that gives U(U-1) >= 2 * 0.497 N). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^-14.98 = 3.09e-05 (H2 d: a trail of length l has at most l(l-1)/2 pairs, E[l^2] <= 2 L^2, and there are Q / L trails). The expected number of key false matches (two different DP ends with the same 64-bit key: the key space is 2^55 * 505 = 2^63.98) is below 33,662^2 / 2 / 2^63.98 = 3.1e-11.
Programmed aborts. Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations, binomial with mean Q / L = 32260 (and no more than a Poisson count of the same mean in the Chernoff bound); the abort needs 33,663 or more, probability at most exp(-mean) (e mean / 33,663)^33,663 = 2^-43.4 = 8.6e-14 (Chernoff bound). Stage-1 budget: the number of stage-1 hits is at most binomial with mean mu2 = Q / 2^32 = 7.908e+28 and the abort needs 2 mu2 + 65, probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.1e+28). A recovery that finds no pair needs a key false match or a start lying on another trail (at most 3.1e-11 + 2^-100).
The losses add to 1e-06 + 3.09e-05 + 4.660e-04 + 3.1e-11 + 8.6e-14 + 7.9e-31 < 4.979e-04, so P_F >= 1 - e^-0.497 - 4.979e-04 = 0.3911 >= 0.39. The 0.0011 left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0038, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function f and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved. Its content, in the terms the ledger uses, is: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of f from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 505 / 2^122. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Section 4 and in the note.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). The program also prints its own observations (`python3 shrho.py --stats`, seeds from SHA-256 of a counter), which are untrusted and are only descriptive:
    T3 n=18: attempts returning a verified pair: target 109 of 256, ideal function 119 of 256
    T1 n=10 fresh K: 256 runs, mean first repeat 40.24 (sqrt(pi N/2) = 40.11)
    T2 width 256: 448 points, 16-bit projections, equal pairs per trial if uniform 1.5278, trials with a pair if uniform 0.7830
      source uniform (86 trials): returned pairs 71 (uniform reference 67.3); w0 142 (uniform reference 131.4); w3 127 (uniform reference 131.4); w7 126 (uniform reference 131.4); xor8 126 (uniform reference 131.4); sum8 126 (uniform reference 131.4); p01 143 (uniform reference 131.4); p23 121 (uniform reference 131.4)
      source counter (85 trials): returned pairs 68 (uniform reference 66.6); w0 137 (uniform reference 129.9); w3 132 (uniform reference 129.9); w7 121 (uniform reference 129.9); xor8 127 (uniform reference 129.9); sum8 137 (uniform reference 129.9); p01 121 (uniform reference 129.9); p23 109 (uniform reference 129.9)
      source iterates (85 trials): returned pairs 70 (uniform reference 66.6); w0 136 (uniform reference 129.9); w3 138 (uniform reference 129.9); w7 133 (uniform reference 129.9); xor8 145 (uniform reference 129.9); sum8 125 (uniform reference 129.9); p01 137 (uniform reference 129.9); p23 107 (uniform reference 129.9)
Run by the organizer's pipeline on this program with the public seed (the pipeline reruns each experiment and requires identical output), reported without inference:
    shrho-n18 (organizer run, public seed): 116 of 256 trials returned a pair that the organizer verified; ideal-function control (program's own) 117 of 256; family-law runs at n = 10 (program's own): mean first repeat 39.90; halts target 47, ideal 63.
    proj-k0-w256 (organizer run): 200 of 256 trials returned a verified pair; by source: uniform 67 of 86; counter 68 of 85; iterates 65 of 85; equal pairs in the seven projections (program's own), total over 256 trials: w0 391, w3 405, w7 397, xor8 377, sum8 418, p01 399, p23 392.
An unsuccessful attempt of the width-18 experiment either ends with a halt of the program (a budget, or "recovery found no pair" when a trail start lies on another trail, which is frequent at width 18 and has probability below 2^-100 at width 256, Section 4) or runs its 92 batches without finding a pair; the single attempt is not amplified. The ideal function behaves the same way.
Toy-scale end-to-end runs (outside the shipped experiments, same program, same kernel, development machine; `toy_run.py`, not shipped): n = 40 (plan(40): DP = low 6 bits zero and a 4-bit window, 154,052 batches of 7 lanes per attempt): 3 of 10 single attempts returned a pair, 3 of 3 confirmed by the organizer reference (distinct messages, equal low 40 bits of the complete 39-step digests); 97 s in all. n = 48 (plan(48): DP = low 8 bits zero and a 6-bit window, 2,464,813 batches of 7 lanes per attempt): 2 of 5 single attempts returned a pair, 2 of 2 confirmed by the organizer reference (distinct messages, equal low 48 bits of the complete 39-step digests); 828 s in all.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; the search above width 48. A deviation of f from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/shrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`shrho-n18`: per trial, from the trial seed, one attempt of the 7-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 92 batches of 7 lanes, cut rule, table, recovery with the same kernel) on the target chain f (the low 18 bits of the digest of the 32-byte message x < 2^18); the trial returns the two 32-byte messages M(x), M(y) when the attempt succeeded and two nulls otherwise. The checked event is that the complete 39-step digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 10.
`proj-k0-w256`: per trial, 448 points of the target at full width 256 evaluated with the packed kernel (source by trial index mod 3: uniform inputs from the seed, counter inputs r + i, iterates of f from 7 seed-derived starts), returning two distinct points whose complete digests agree in the low 16 bits when the set contains such a pair, two nulls otherwise. The checked event is that the digests agree in the low 16 bits and the messages are distinct. Observations (untrusted): the numbers of equal pairs in seven 16-bit projections of the digest.
They check the kernel at full width, the packed search, lane insertion and extraction, the table, the recovery and the message construction on the real target. They do not measure the cost or the success probability at width 256. Running times on the development machine: 4.5 s and 2.8 s.

## 7. Memory

Table: 33,662 entries * 25 bytes = 841,550 bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 5,523 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 198,828 bytes (loop body 2433, recovery copy 2490, handlers, key scan, cut, slice and setup 600).
Counters and copies: 6,144 bytes (trail numbers, birth batches, counters and the lane arrays used by the handlers, about 2,048 bytes, and a reserve of 4,096 bytes for the stack, alignment and anything not itemised). The 64 registers, counted as memory: 2,048 bytes. No advice. Memory peak = max(setup phase 263,476, search phase 1,048,570) = 1,048,570 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. This is the search phase; the setup phase, in which the circuit generator runs, is smaller (263,476 bytes, Section 3.6). Claim `memory_log2_bytes` = 20. `python3 shrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 198,828 - 2,048 - 6,144) / 25) = 33,662, and Tp = 505 is the largest integer for which the table-capacity bound of Section 4 stays below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Section 4, score-critical), H2 (the named approximations of Lemma 2, supporting), H3 (the machine convention: 64 registers, immediates, lanes of 36 bits in a word, 36-byte instruction charge; supporting: it is a declared convention priced in Section 3.5, not a statistical premise, and the success argument does not depend on it). There is no prefix, no advice and no polarity climb; the entry has no two-block mode.
Credited to our earlier entries 0a9640ed, 3356413f, cf8b0e92 (the packed-lane chain), 62cfd777 (declared register file and generator accounting) and to Jbenisek's e479cbbf: the relation, the trail-and-table search, the handlers, the recovery, the ledger method and the experiments' form. The kernel, the target and every number here are new.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 shrho.py --ledger`.

```python
from fractions import Fraction
from math import isqrt, log, exp, log2

PH, FILT, LOOP, LANES = 2426, 4, 3, 7           # operations of the packed step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 3468                                # generator calls (python3 shrho.py --ledger)
EXTRA = 64                                      # extra operations per recovery batch beyond the kernel
N_BITS, S1, W, KAPPA = 256, 32, 90, 12          # width, stage-1 bits, window bits (D = 122), age cap in units of L
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 400, 800, 800, 120, 400
SETUP_FIXED, CMAX = 7 * 400 + 2000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE = 36, 600, 64 * 32, 6144, 25, 0
TAIL_AGES = 1e-6


def inflight_m(lanes=LANES, eps=TAIL_AGES):    # smallest M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


M = inflight_m()
body = PH + FILT + LOOP                                        # one batch = one loop body = 2,433 operations
code_bytes = (body + (PH + EXTRA) + OTHER_CODE) * INSTR        # main body + recovery copy of the kernel + handlers
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY    # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def plan_tp(Tp):
    L = Fraction(1 << D, Tp)                                   # trail length scale 1/theta, theta = Tp / 2^D
    ureq = isqrt(2 * Nn * LAM.numerator // LAM.denominator) + 2
    num, den = ureq + M * L + 1, CUT.denominator
    q = -(-(num * den) // (den - CUT.numerator))
    b = -(-q // LANES)
    c = -(-KAPPA * L.numerator // L.denominator)
    return L, b, c


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


Tp = max(t for t in range(1, 8193)
         if float(plan_tp(t)[1] * LANES / plan_tp(t)[0]) < tmax + 1
         and tail_log2(float(plan_tp(t)[1] * LANES / plan_tp(t)[0]), tmax + 1) <= -40)
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 2433", body * B),
        ("slice checks: ceil(B / 2^48) * 120", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 400", e2max * HIT),
        ("finished trails: tmax * (800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 800", CMAX * CUTOPS),
        ("recovery: (c + 2^48) * (2426 + 64) + 600", capr * (PH + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("M =", M, " Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 2812
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
M = 32  Tp = 505  tmax = 33662  B = 48521120621377244089789062617386381958  e2max = 158160852431152345905324182686  c = 126342462965694974058183641373181267
memory bytes = 1048570
main loop: B * 2433                                  118051886471810834870456789348101067303814
slice checks: ceil(B / 2^48) * 120                   20685797873075519571183240
stage-1 hits: e2max * 400                            63264340972460938362129673074400
finished trails: tmax * (800 + 3 * tmax)             3426320332
cut trails: 2 * 800                                  1600
recovery: (c + 2^48) * (2426 + 64) + 600             314592732784580485405578139711230888870
setup and generator                                  2362400
N = 118366479267859777014121178925464971134656
certificate: 2^12498493 * 2812^100000 <= N^100000 < 2^12498494 * 2812^100000
log2(N/C) = 124.9849315869
time_log2 = 124.98494
```
