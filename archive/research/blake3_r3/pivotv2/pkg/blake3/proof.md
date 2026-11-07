# blake3-r3: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk

Credited derivative of our own 62cfd777-5613-463f-b561-e2340e00e528 (blake3 round 3, 124.8123: this program; this entry replaces its Lemma 2 by Lemma 2 v2 and re-plans, see the revision note below), of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges) and of our own 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448, two-block mode with a fixed first block; this entry does not use that mode), which are derivatives of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). It also takes two circuit and walk ideas from jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), whose proof text (3.3, 3.4) we read as data and re-implemented in our own generator without using or running any file of that entry: (1) the pivot full adder, (2) the mask walk g = f XOR q in which the digest planes are fed back exactly as the circuit stores them. Everything else is the program of 62cfd777, 0a9640ed and 3356413f: relation, trail-and-table search with distinguished points, handlers, recovery walk, ledger method, the register file and the 36-byte instruction charge.
The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. The chain step is 17238 operations for 256 trails (67.34 per trail) against 19,022 in 0a9640ed and 18,866 in 3356413f. The price is the declared register file of 1,024 words of 256 bits (counted as memory, every transfer charged), a program of 19,085 instructions of 36 bytes and a table of 12,494 entries.

Revision note. This text revises our filed 62cfd777-5613-463f-b561-e2340e00e528 (B3R3PV, 124.8123): Section 4 (Lemma 2) is replaced by Lemma 2 v2 (a theorem about the random function F with no premise besides H1; the heuristic H2 of the filed text, which stated that the number of cut trails is Poisson and that the 256 trail ages are independent exponentials, is withdrawn and replaced by the proved Step 5.2 and Step 6; the Chernoff quantile is an upper bound certified in exact arithmetic by Appendix A; H1 gets clause (d), the adaptivity clause); the plan is re-run on the new bound (Tp 174 against 177, time_log2 124.83986 against 124.8123); the target, the step, the generator, the program's search and every operation count are those of the filed entry. Section 9 answers the findings of the judges' ruling on 1cd0dd3b (whose Lemma 2 and H2 were the same text) by id.

## 1. Target and relation

Target `blake3-r3-prefix-v1` (the benchmark's blake3 round-3 profile). The two colliding messages are 64 bytes, M(x) = 0^32 || LE32(x): 32 zero bytes (words m0..m7 = 0) followed by the 256-bit integer x (words m8..m15, little endian). It is one chunk of one block: chaining value IV, counter 0, block length 64, flags 11 = CHUNK_START | CHUNK_END | ROOT, 3 rounds, digest = the 8 words v[i] XOR v[i+8] (i < 8), little endian (this is `verifier/blake3.py:blake3(M(x), 3)`). Write f(x) for the digest read as a 256-bit little-endian integer.
The walk is on g(x) = f(x) XOR q, where q is the fixed 256-bit mask (weight 129) of the polarities of the 256 digest planes of the circuit that the generator of Section 3.2 builds; q is printed by `python3 bsrho.py --ledger`. g(x) = g(y) if and only if f(x) = f(y): XOR with a constant is a bijection. The attack outputs x != y with g(x) = g(y), hence f(x) = f(y), and M(x) != M(y) are two distinct messages with equal complete 256-bit digests (a finite byte string of 64 bytes is in the profile's message domain, "Finite byte strings of bit length below 2^64").
The scalar digest of the program (`digest_words`) was compared outside the shipped experiments with the organizer reference `blake3(M(x), 3)` on 300 random messages: 0 differences. The bit-sliced step (`ext` check, not shipped) was compared with the reference on 8,192 random messages (one step: stored planes equal blake3(M(x), 3) XOR q) and on 256 messages chained for 4 steps; the packed recovery circuit on 448 messages: 0 differences in each. The program's own selftest (`python3 bsrho.py --selftest`) compares the step against the scalar compression on 4,096 lanes (16 batches of 256, the full 256-bit g), 256 lanes chained for 3 steps, the register-allocated code executed on a register file, the width-18 chain, and the packed circuit.

## 2. The attack (program `experiments/bsrho.py`, sections 3 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 174. The density is theta = 174 / 2^122 and L = 1 / theta = 2^114.5571. The key of a DP is the 56 bits of x above bit 121 followed by the 8 low bits of F (F < 174 < 2^8, so those 8 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 32 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above, length = batches since the trail started. If the key is in the table, go to 6. Otherwise store (t, length) under the key (25-byte entry, Section 7) and
   start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 11 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 12,494 keys, when a third trail would be cut, or if step 6 finds no pair.
6. Recovery. The two trails have lengths l1 >= l2. Advance the first from its start by l1 - l2 steps of g, then step both together; at the first step
   with g(a) = g(b) and a != b output (a, b). Both lanes of one packed circuit (603 operations: the compression and one XOR of each of the 8 output words with the 32-bit word of q; used by nothing else) are used. At most capr = c + S batches are run (the program halts if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = 174, L = 2658455991569831745807614120560689152 / 87, B = 1392885148265000000000000000000000000, Q = 256 B = 1.04789 * 2^128 evaluations,
e2max = 166044848950505256652832031314, c = 336126619623771829929698337082385985 (= 2^118.016), table capacity tmax = 12,494 entries of 25 bytes. The trail numbers t stay below 2^16 (finished trails <= 12,494, cut trails <= 2, plus the 256 starts) and every length is below c + S < 2^119, so the 2-byte and 15-byte fields of an entry never overflow (the program asserts both when it stores an entry).
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is derived by the generator at setup and is also written into the recovery circuit as immediates).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry (as in 0a9640ed, which passed the judges with it). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores, and it gives no register count.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 1,024 registers (a premise of the entry, H3; Section 3.5 prices smaller files). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each.
The main loop has no loads, stores or moves: the generated straight line needs 771 registers (`allocate` in the program assigns them; output plane j is written into the register that held input plane j, so the next batch reads the same registers), leaving 253 of the 1,024 for the loop counter, the limit and the handlers' temporaries. The file of 1,024 registers is counted as memory: 32,768 bytes (Section 7).
Constants are immediates. The organizer's reference count C(r3) = 638 (222, 430 and 638 for 1, 2 and 3 rounds) is used only as the unit: Unit = 638 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers; the straight line is not given a shorter encoding.

### 3.2 One batch = 17275 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j is a 256-bit integer whose bit l is bit j of the word of lane l. A rotation is a renaming of planes (no operation). XOR, AND, OR of words are 32 operations each. The sum of two words is a ripple of full adders over the planes; the lowest bit has 2 gates (no carry in) and the highest 2 (no carry out), and constants (the IV words, the zero words m0..m7, the length and the flag word) are folded at build time.
The full adder is the pivot adder of 6ae36351 (our re-implementation, `Gen.fa`). Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the third as the pivot p and the two equal ones as x and y. With u = x XOR p and v = y XOR p: sum = u XOR y, carry = (u AND v) XOR p, because maj(x, y, p) = p XOR ((x XOR p) AND (y XOR p)). u and v have equal polarity, so the AND is always one gate (an AND of two upright planes, or an OR of two inverted planes, with the result's polarity set); every full adder with three variable inputs is 5 gates (XOR for u, XOR for the sum, XOR for v, the AND, XOR for the carry). With one constant input, sum = x XOR y XOR k and carry = x AND y or x OR y (2 or 3 gates); with two the plane passes through. The program generates the straight line at run time (`trace`, `Step`): gates are hash-consed, a gate whose result no output uses is dropped.
The mask walk: the circuit's 256 output planes are stored in registers exactly as the circuit produces them (a register holds the node value, the digest plane is that value XOR q_j, q_j the polarity of the signal) and they are the 256 input planes of the next batch. So no operation complements a plane, no polarity vector is chosen, and the chain is x -> g(x) = f(x) XOR q. q is a fixed constant of the circuit (weight 129 of 256); the generator derives it while it builds the circuit, and the recovery circuit uses it as 8 immediates. Equality under g is equivalent to equality under f (Section 1), so a collision of g is a collision of f.
The generated line (`python3 bsrho.py --ledger`, `--selftest`): 17238 gates = 14148 XOR + 1057 AND + 2033 OR = **17238 operations**, no complement operation. Per trail 67.336 operations = 0.1055 unit, against 1 unit for a compression and 0.1332 unit for the packed circuit of cf8b0e92.
Validation: 4,096 lanes against the scalar digest in the selftest (stored planes = f XOR q); 8,192 lanes and 256 lanes chained for 4 steps against the organizer reference (Section 1); the register-allocated code executed on a register file gives the same planes as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 17238 + stage-1 test 34 + loop control 3 = 17275 operations. Stage 1: the 32 low planes of digest word 0 (stored planes, which are the planes of the next point x) are combined into the mask of zero lanes: 31 ORs over the 32 planes, a complement, a compare of the mask with zero and a branch: 34 operations (`stage1_ops`). The test loses no event: a DP has all 32 low bits zero, so its lane is flagged.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no flagged lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers):
- Stage-1 hit (a flagged lane): store the 256 planes to a 8 KiB copy in memory (256 stores), then a loop over the planes: load, shift right by the lane number, AND 1, shift left by the plane number, OR into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit (the polarity XOR of the earlier entries is not needed any more). The hit budget e2max is enforced by a halt.
- Finished trail (a DP, new start): key formation, three read-modify-write field stores of the 25-byte entry, the new start r + t' (1 add), insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Total below 3,550; charged **3,800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 1,024), slice counter: charged **1,300** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **4,200**; at most 2 cut trails (a halt on the third).
- Recovery batch (both lanes in one packed circuit, 603 operations, the last 8 of them the XORs with q) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch (667 per batch). The first l1 - l2 steps move one lane only and need no test, also inside the 667.
- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; fixed part charged 813,600. The generator: 35,340 primitive calls (hash-consed gate constructors) and 17238 emitted lines, each charged 200 word operations: 10,515,600. Setup and generator together 11,329,200 operations = 2^14.12 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size, instructions: loop body 17275 + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery 650 (the 603-operation circuit, the test, the loop, the call and the moves) + setup, cut and slice 160 = 19,085 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 17275 | 24,062,090,936,277,875,000,000,000,000,000,000,000,000 (= 2.4062e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6.433e+24 |
| stage-1 hits: e2max * 2,800 | 4.6493e+32 |
| finished trails: 12,494 * (3,800 + 3 * 12,494) | 515,777,308 |
| cut trails: 2 * 4,200 | 8,400 |
| recovery: (c + 2^48) * (603 + 64) + 600, c + 2^48 = 2^118.016 | 2.2420e+38 |
| setup and generator | 11,329,200 |
N = 24,286,287,856,492,514,305,056,770,173,441,753,898,855 = 2.428629e+40 operations.
N / 638 = 3.8066e+37 units = 2^124.839853. Claim `time_log2` = 124.83986 (integer power certificate in Appendix A, rounded up with 6.8e-06 of slack). The main loop is 99.08 percent of it, recovery 0.92 percent.

### 3.5 Register file and smaller files
Premise H3: the machine has 1,024 registers of 256 bits. The generated line needs 771 (peak live planes 771, no spills: `spill_ops(1024)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch, and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,024 (claimed) | 0 | 17,275 | 12,494 | 174 | 124.83985 | 0.39000 |
| 512 | 862 | 18,137 | 11,908 | 165 | 124.91268 | 0.39000 |
| 256 | 3,423 | 20,698 | 8,548 | 115 | 125.12972 | 0.39000 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). The claim assumes R >= 771; 1,024 is declared.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry: the hash-consing network builder (`Gen`, including the pivot adder `fa`), `trace`, the reachability and emission pass (`Step.__init__`, `_last`) and the register allocator (`allocate`), which are 2,036 bytecode instructions (`python3 bsrho.py --gencode`, one instruction each) and are charged 2,040 instructions * 36 bytes = 73,440 bytes. There is no polarity vector to search and nothing to store: q falls out of the generator.
Its peak storage (`gen_scratch` of the program, 17,495 nodes of the network): trace phase, node table 4 bytes per node (2-bit operation, two 15-bit operands) = 69,980 bytes, hash-consing table 2^15 slots * 2 bytes = 65,536, signal state 10,240: 145,756 bytes; emit phase (the hash-consing table is dead), node table 4 + reachability mark 1 + last use 4 + register 2 = 11 bytes per node, a 2,048-byte heap and the state: 204,733 bytes. Peak scratch 204,733 bytes.
Layout. The setup phase holds the main code (counted at its final size, 687,060 bytes; it is written as the generator emits it), the counters and plane copy (16,384), the generator's code image (73,440) and its scratch (204,733): 981,617 bytes. The generator is never called after setup. In the search phase the same region holds the table (312,350 bytes), the register file (32,768) and the counters: main code + counters + register file + table = 1,048,562 bytes. The memory of the entry is the larger of the two, 1,048,562 bytes (14 bytes to spare under 2^20); the region is 361,502 bytes against 278,173 bytes of generator image and scratch. The table size of Section 7 is the largest that fits with this layout.
Measured peak memory of the generator (not the machine model, which is the byte account above): The circuit generator written in freestanding C (source embedded in `experiments/bsrho.py` as `GEN_C`, printed by `python3 bsrho.py --gen-c`, 10,304 bytes) compiled to WebAssembly and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: 17,238 instructions, 771 registers, 17,495 nodes, 35,340 primitive calls, the same q, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total 902,720 bytes, of which 687,060 are the final code region (36-byte records) and 16,384 the counters; its own scratch peak is 195,005 bytes (emit phase; trace phase 138,140), against the model's 204,733 and 145,756, and it needs 8,562,286 wasm operations, below the 10,515,600 word operations the ledger charges for the generator. The guest links in 14 pages and leaves 145,856 bytes of the 1 MiB unused (the generator's code image, charged in the model at 73,440 bytes, lies outside the guest memory in this sandbox). 

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 14.2, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (981,617 bytes), and nothing it produces is stored outside the 1,048,562 bytes of the search phase.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F); it has no premise besides H1 (a premise about g, not about F). H1 clause (d) (Section 5) is the premise that the lazy-sampling hazard of F also holds for the adaptive choices of the program (which trails finish, are cut or abort depend on earlier outputs). The numbers below are printed by `python3 bsrho.py --loss` (the function `_lossq`; Appendix A recomputes them with its own copy).

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
the stored lengths let step 6 align and walk them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 174 < 2^8 and the key holds its 8 low bits), so equal keys of two DPs differ only if their bits above 177 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 1.04789 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) the batch of t; N = 2^256, theta_D = Tp / 2^122 = 1 / L, c = ceil(11 L) = 336126619623771829929698337082385985, S = 2^48, M = c + S, h = floor(c / 2), q = Q / L = 11669.31, N' = (1 - theta_D) N, tmax = 12,494, CMAX = 2 (the program halts when a third trail would be cut), H = (Q (Q - 1) / 2 + 2^16 Q) / N' = 0.54904, and z(m) = 128.5 m (m + 1) + 2 Q (m - h)+ (257 / 2 = (LANES + 1) / 2). Let F be a uniformly random function on 256-bit values and P_F the success probability of the attempt when every evaluation of g is replaced by F (lazy sampling). Let k = 12074 be the least integer with e^-q (e q / k)^k <= EPS = 1e-03; let z* L^2 with z* = 5.5077e+06 be a number with e^(-s z*) Phi_up(s)^n <= EPS for some s > 0, where n = k - 1 + 256 = 12329 and Phi_up is the function of Step 5.3; let w >= 1 satisfy ln w >= w kap0 / N' with kap0 = 2 M Q + z(M) (kap0 / N = 0.00323, w = 1.00325). Put
    theta = [ w (P0 - 2 k Q - CUT - z* L^2) - (w - 1) (Q (Q - 1) / 2 + 2^16 Q) ] / N' = 0.50206,
    P0 = 256^2 B (B - 1) / 2,   CUT = CMAX (M Q + min( (M - h) Q, z* L^2 / 257 + S Q )) = 2 (M Q + min( (M - h) Q, z* L^2 / 257 + S Q )).
Then, with no premise,
    P_F >= 1 - e^-theta - 2 EPS - P_cut - delta - P_key - P_table - P_long - P_tiny,
where
    P_cut = P(Binomial(k + 258, p) >= 3) + E_S + E_X + E_J2a + E_J2b + E_Y   (Step 6), p = e^(-c/L) >= (1 - 1/L)^c, p2 = e^(-(c-1)/L) (1 + (c - 1) theta_D / (1 - theta_D)), PP = Q (Q - 1) / (2 N'),
        E_S = Q L / N', E_X = (Q / N') L e^(-(c-2)/(2L)) (2 + (c - 1)/L) + PP p2, E_J2a = Q L H / N' + (Q + 2^16) L PP / N', E_J2b = PP (1 - theta_D) p2, E_Y = e^(-(c-1)/L) H,
    delta = M (Q + 2^16) / N'   (Step 3),
    P_key = C(tmax, 2) / (2^kb Tp), kb = 56,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59),
    P_long = (k + 258) e^(-c/L) S / L,
    P_tiny = Q 2^16 / N + Q k / N + k^2 L / N + exp(-300 + (e^5 - 1) H) + 2^-99   (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bsrho.py --loss` (the function `_lossq`; Appendix A recomputes them with its own copy) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000006430 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^24 for which the float bound reaches 0.390000001 (Appendix A). H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F. Lemma 2 is a theorem about F.

Proof.
Step 0 (notation). A trail is the run of evaluations of one lane between two restarts; a(t) is the number of earlier evaluations of the trail of t (its age); the length of a trail is its number of evaluations. A trail is finished when an evaluation returns a distinguished point (DP; that evaluation is its last), cut when a slice check restarts it at age >= c, open when the halt comes first. Every length is at most M, and a trail of length at most c is never cut. An evaluation is fresh when its input has not been evaluated before. A collision is a fresh evaluation whose value equals an earlier value (an earlier output or a start). The starts r + t' (t' < 2^16) differ from every value the run produces except with probability Q 2^16 / N (r is uniform and independent of F); this event is excluded below and charged in P_tiny, so a non-fresh evaluation exists only after a collision on its trail.

Step 1 (lazy sampling with a lottery). Realise F by independent uniform values V_1, V_2, ...: the t-th evaluation returns V_t if it is fresh and the value stored for its input otherwise. This is the lazy sampling of F for every adaptive choice of the points. Put xi_t = 1 when V_t is a DP. The xi_t are independent Bernoulli(theta_D), one per evaluation index, fresh or not; given all of them the V_t are independent and uniform on their class (the DP values, or the other values). Index t belongs to lane (t - 1) mod 256, and the lane positions of a lane are its indices in increasing order; the lottery is extended beyond Q by further independent draws (used in the proof only). G_t is the history of the first t evaluations together with the whole lottery; F_t is the history of the first t evaluations together with xi_1, ..., xi_t only.
(L1) If t is fresh and xi_t = 0, then P(V_t = v | G_(t-1)) = 1 / N' >= 1 / N for every non-DP value v (and 0 for DP values), and the events for different v are disjoint.
(L2) Whether t is fresh, its input, its batch, its age and the trails before t are determined by G_(t-1).
(L3') Lottery blocks. Cut the lottery of a lane after every 1: the blocks (a run of 0s and the 1 that ends it) have independent identically distributed geometric lengths beta on {1, 2, ...}, P(beta >= m) = (1 - theta_D)^(m - 1) (a fixed i.i.d. sequence, no selection). Take on each lane the blocks that begin at a position of the run (batch <= B), lane after lane, then further independent geometric variables: the result is an i.i.d. sequence beta_1, beta_2, ... (the number of blocks taken from a lane is a stopping time of that lane's sequence, and the lanes are independent). The number of blocks taken is at most N1 + 256, since every block but the last of a lane ends with a 1 inside the run.
(L4) N1 = xi_1 + ... + xi_Q is exactly Binomial(Q, theta_D): a sum of Q independent Bernoulli variables by construction. A fresh evaluation outputs a DP if and only if its xi is 1, so the fresh DP outputs are at most N1, and P(N1 >= k) <= e^-q (e q / k)^k <= EPS by the choice of k (Chernoff: the binomial moment generating function is below the Poisson one). Repeated inputs after a merge have correlated DP indicators, but they play no part in N1.
(L5) The run up to evaluation t is F_t-measurable (it depends on V_1, ..., V_t only, and V_s depends on xi_s and an independent uniform). If s is a stopping time of (F_t), for example the start of the j-th trail, the lottery after s is independent of F_s and i.i.d. (strong Markov property of an i.i.d. sequence).

Step 2 (usable collisions). For y an evaluation on a lane let f(y) be the first position >= y on that lane with xi = 1, and d(y) = b(f(y)) - b(y) + 1. For fresh t with xi_t = 0, Y_t is the set of evaluations y with
(i) b(y) < b(t); y is fresh; the output of y is not a DP; y is not on the trail of t;
(ii) every evaluation of the trail of y up to t - 1 is fresh and none of them is a collision;
(iii) b(f(y)) - s(y) + 1 <= c and b(f(y)) <= B, s(y) the batch where the trail of y started;
(iv) b(t) + d(y) - 1 <= B and a(t) + d(y) <= c.
Y_t = empty for other t. Y_t is determined by G_(t-1) (L2). The usable collision C_t is the event that t is fresh, xi_t = 0 and V_t = F(y) for some y in Y_t; D_t is a collision at a fresh t with xi_t = 0 that is not C_t.
Claim 1. Let C_t occur with y in Y_t, and assume that after t no fresh evaluation on the trail of y before f(y) is a collision, and that the run does not stop early (third cut, table full, stage-1 budget, key false match). Then the program outputs a pair. Proof. Let x be the input of t and p_k the input of y, so F(x) = F(p_k): the trail of t continues with the points p_(k+1), p_(k+2), ... that the trail of y evaluates after y. The j-th of them is evaluated by the trail of y in batch b(y) + j and by the trail of t in batch b(t) + j > b(y) + j, so the trail of t only repeats points that were already evaluated (not fresh). By (ii), (iii) and the assumption, the trail of y is not cut and its evaluations up to f(y) are fresh with no collision; f(y) is the first position with xi = 1, so the trail of y finishes there, with a DP, within c batches and before the halt. The trail of t reaches the same point d(y) - 1 batches after t, in batch b(t) + d(y) - 1 <= B; before its finishing evaluation it has done at most a(t) + d(y) - 1 <= c - 1 evaluations by (iv), so no slice check cuts it, and it finishes with the same DP. The two trails are different (y is not on the trail of t, (i)), the inputs x and p_k are different (x is fresh) and F(x) = F(p_k): Lemma 1 applies. QED.
Claim 2. For fresh t the values F(y), y in Y_t, are pairwise different. Proof. If y and y' in Y_t, y' evaluated later, had the same value, V_(y') would equal an earlier value, so y' is a collision on its own trail, against (ii). QED.

Step 3 (disturbance). After the first usable collision tau the trail of y has at most c further fresh evaluations before f(y), each a collision with conditional probability at most (Q + 2^16) / N' by (L1); so P(C occurs and the program does not halt early) >= P(C occurs) - delta - P(early halt), delta = M (Q + 2^16) / N' = 1.035e-03.

Step 4 (a supermartingale). S_t = sum of |Y_s| over s <= t; u_t = |Y_t| / N' and h_t = (t - 1 + 2^16 - |Y_t|) / N' (for every t); H_t = sum of the h_s; R_t = number of unusable collisions up to t; w >= 1 a constant; M_t = exp(S_t / N' - (w - 1) H_t) w^(R_t) 1[no usable collision up to t]. For fresh t with xi_t = 0, P(C_t | G_(t-1)) = u_t exactly (L1, Claim 2) and P(D_t | G_(t-1)) <= h_t (at most t - 1 + 2^16 earlier values exist, |Y_t| of them usable), so E[M_t / M_(t-1) | G_(t-1)] <= e^(u_t - (w - 1) h_t) (1 - u_t + (w - 1) h_t) <= 1 (the factor is 1 - P(C) + (w - 1) P(D), and 1 + x <= e^x); for the other t, M_t <= M_(t-1). Hence E M_Q <= 1 and P(M_Q >= e^x) <= e^-x. The same computation with every collision at a fresh t with xi_t = 0 counted (hazard at most (t - 1 + 2^16) / N') gives E[w^(#collisions)] <= e^((w - 1) H), so P(60 or more collisions) <= exp(-300 + (e^5 - 1) H) with w = e^5 (here H = 0.5490; the term is charged in P_tiny).

Step 5 (counting S_Q from below). Let A be the event: no usable collision; the run lasts Q evaluations; K <= 2 (K the number of cut trails); fewer than 60 collisions; no start coincides with a value; no fresh evaluation with xi = 1 returns an earlier DP value; N1 <= k - 1; no free finished trail is longer than c. On A count the pairs (y, t) with b(y) < b(t): P0 = 256^2 B (B - 1) / 2. A pair is in S_Q (y in Y_t, t fresh, xi_t = 0) unless one of the following holds.
5.1 The lost pairs.
(a) xi_t = 1, or y has a DP output: at most 2 k Q pairs (at most k - 1 positions with xi = 1, at most k - 1 fresh DP outputs, (L4); a non-fresh y is on a colliding trail, (b)).
(b) y or t on a colliding trail (a trail that contains a collision): at most 2 M Q pairs per colliding trail, and on A there are at most R_Q of them. Charged as R_Q kap0 with kap0 = 2 M Q + z(M) (the z(M) part is no longer needed with the blocks of 5.2 and is kept as slack).
(c) the cut trails (K <= CMAX = 2 on A; a cut trail that is colliding is already in (b)). Take one of them, T0. As y: (iii) fails for all its y, at most M Q pairs. As t: its evaluations are fresh with xi = 0 and conditions (i) to (iii) concern y only, so a pair (y, t) is lost through t only by (iv) second part, a(t) + d(y) > c. For a y on a free finished trail with d(y) = d, the evaluations of T0 with age above c - d are at most d + S (its ages are below M), so these pairs are at most the sum of d(y) + S over y, which is at most the sum over free finished trails of X(m) + S Q, X(m) = m (m + 1) / 2; and also at most (M - h) Q (the t of age above h, each with at most Q partners; for a(t) <= h the loss needs d(y) > c - h and is charged to y in (g)). Since 257 X(m) <= z(m), on Z <= z* L^2 each cut trail costs at most M Q + min((M - h) Q, z* L^2 / 257 + S Q), and the at most CMAX = 2 cut trails cost at most CUT = CMAX (M Q + min((M - h) Q, z* L^2 / 257 + S Q)) (each cut trail is bounded on its own; no sharing of the sum is used).
For the remaining trails (free trails that are finished or open: every evaluation fresh, no collision), with m the length:
(d) y and t on the same trail: at most X(m) pairs.
(e) y on an open trail of age a <= m: (iii) fails (b(f(y)) > B); the pairs with b(t) > b(y) are at most 256 a (a - 1) / 2 <= 256 X(m).
(f) y on a finished free trail: by (iv) first part the batches b(t) > B - d(y) + 1 are lost, at most 256 (d(y) - 1) per y, in all at most 256 X(m).
(g) (iv) second part: a(t) + d(y) > c forces a(t) > h or d(y) > c - h; at most (m - h)+ evaluations of each kind per trail, so at most 2 Q (m - h)+ pairs per trail.
Hence S_Q >= P0 - 2 k Q - R_Q kap0 - CUT - Z, where Z = sum over the free finished or open trails of z(m).
5.2 Trail sums by lottery blocks. A free trail lies in one lottery block of its lane: all its evaluations are fresh, so xi = 0 at every non-final position (the output is not a DP) and, if it finished, xi = 1 at its last. Its length is at most min(beta, M) for that block. Two free trails that are finished or open lie in different blocks: a finished free trail ends at the 1 of its block, and an open trail is the last trail of its lane (the cut trails, which may share a block with one of them or with each other, are charged in (c)). As z is increasing, on N1 <= k - 1, by (L3'),
    Z <= sum of z(min(beta, M)) over the blocks of the run <= Z' := sum for i <= k - 1 + 256 of z(min(beta_i, M)),
a sum of n = 12329 independent identically distributed terms, with no selection and no indexing of trails. In particular the sum of X(m) over free finished trails is at most Z / 257.
5.3 The tail of Z'. Coupling: with E ~ Exp(1) and lambda = -ln(1 - theta_D) >= theta_D, beta = ceil(E / lambda) has the law of the block length and beta <= L E + 1. With x = min(beta, M) / L <= min(E + 1/L, uc), uc = M / L, uh = h / L,
    z(min(beta, M)) / L^2 = 128.5 (x^2 + x / L) + 2 q (x - uh)+ <= zeta(x + 1/(2L)),   zeta(v) = 128.5 v^2 + 2 q (v - uh)+,
so z / L^2 <= zeta(V) with V = min(E + delta1, uc'), delta1 = 3/(2L), uc' = uc + 1/(2L). For s > 0,
    Phi(s) = E exp(s zeta(V)) = e^delta1 [ integral from delta1 to uc' of phi(y) dy + phi(uc') ] <= e^delta1 [ integral from 0 to uc' of phi + phi(uc') ],   phi(y) = exp(s zeta(y) - y).
zeta is convex on [0, inf) (128.5 v^2 is convex and 2 q (v - uh)+ is convex; its slope jumps up by 2 q at the hinge), so s zeta(y) - y is convex and phi, the exponential of a convex function, is convex. A convex function lies below its chord on every interval: the integral of phi over a panel [a, b] is at most (b - a)(phi(a) + phi(b)) / 2. Summing over the K panels of [0, K hh] with K hh >= uc' gives
    Phi(s) <= Phi_up(s) := e^delta1 [ hh (phi(0)/2 + phi(hh) + ... + phi((K - 1) hh) + phi(K hh)/2) + phi(uc') ],
an upper bound (a midpoint sum is a lower bound for a convex phi). Chernoff: P(Z' > z L^2) <= e^(-s z) Phi(s)^n <= e^(-s z) Phi_up(s)^n for every s > 0, so z* = (n ln Phi_up(s) - ln EPS) / s gives P(Z' > z* L^2) <= EPS. The exponent s is chosen by a search in floats; only its certified evaluation matters (any s > 0 gives a valid bound).
Arithmetic. The program (`_zq`, K = 20,000 panels) multiplies the float trapezoid sum by 1 + 2^-30, which covers the float rounding of the 20,001-term sum (relative error below 1e-11) and the shifts of order 1 / L < 2^-110; it plans with the target 0.390000001. Appendix A (`certify`) recomputes z* and the whole bound in exact rationals and Python decimal arithmetic at 60 significant digits: the nodes i hh are exact, q is rounded up and uh down inside zeta, uc' is rounded up inside zeta and down inside e^-uc', every exp and ln is correctly rounded by the decimal module, and every transcendental result is moved outward by a relative 1e-40, far above the accumulated rounding (below 1e-50). The certified value is a proved lower bound on P_F.
5.4 theta. Take w >= 1 with ln w >= w kap0 / N' (the program iterates w = exp(w kap0 / N) from 1, which converges to the smallest root from below, and multiplies the result by 1 + 2^-40; Appendix A checks ln w >= w kap0 / N' in decimals). Summing h_t over all t gives H_Q = (Q (Q - 1) / 2 + 2^16 Q - S_Q) / N'. On A, with Z' <= z* L^2 and no usable collision,
    ln M_Q = [w S_Q - (w - 1)(Q (Q - 1) / 2 + 2^16 Q)] / N' + R_Q ln w >= [w (P0 - 2 k Q - CUT - z* L^2) - (w - 1)(Q (Q - 1) / 2 + 2^16 Q)] / N' + R_Q (ln w - w kap0 / N') >= theta.
So P(no usable collision, A, Z' <= z* L^2) <= P(M_Q >= e^theta) <= e^-theta. (No replacement of N' by N and no rounding of P0 is used: P0, k Q, Q (Q - 1) / 2 and N' enter exactly.)

Step 6 (the cut count; no premise). Let K be the number of trails that the run cuts or would cut (the third one halts the run). Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. A trail counted by K_A has c fresh evaluations with non-DP outputs at c consecutive positions of its lane, so xi = 0 there; different such trails of a lane use disjoint positions. Scan each lane with trials: a trial starts at the current position u and succeeds if the c positions u, ..., u + c - 1 are all 0 (next trial at u + c); otherwise it fails at its first 1 (next trial after that 1). The scan of a lane stops at the first trial that would start after the run. Inside a maximal run of 0s the trials start at its first position and succeed floor(length / c) times, the largest number of disjoint length-c windows it holds; so K_A on a lane is at most the successes on that lane. Every failure but the last of a lane ends at a 1 of the run, so the failures are at most N1 + 256 <= k - 1 + 256 on N1 <= k - 1. Trial outcomes are independent Bernoulli(p'), p' = (1 - theta_D)^c <= p = e^(-c/L) (disjoint positions of an i.i.d. lottery; lanes concatenated as in (L3')). All successes therefore occur before failure number k + 256 of an infinite i.i.d. trial sequence, and CMAX + 1 = 3 successes before that failure mean three successes among the first n2 = k + 256 + CMAX = k + 258 trials (three successes and at most k + 255 failures):
    P(K_A >= 3, N1 <= k - 1) <= P(Binomial(n2, p) >= 3) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1) - C(n2, 2) p^2 (1 - p)^(n2 - 2)
(the tail increases with p, so p = e^(-c/L) is allowed).
(ii) K_B. A trail T in K_B has a first non-fresh evaluation at age <= c - 1. Its previous evaluation t (age a(t) <= c - 2, T fresh up to t, so a(t) <= g(t), where g(t) is the number of consecutive 0s of the lottery just before t on its lane) is fresh, and V_t equals the input of an earlier fresh evaluation e' (the first evaluation of that input; a start is excluded). Call t the joining collision of T and e' its target. For a lane position e let rho(e) be the number of positions from e to the first 1 at or after e (inclusive), and f'(e) that position: rho is a function of the lottery, so it is determined by G. Choose T in K_B with the earliest joining collision. One of the following root events occurs:
- S: e' is on T itself. T then cycles through its own non-DP points and is cut.
- X: e' is on another trail T' and a(t) + rho(e') >= c (hence g(t) + rho(e') >= c).
- J2a: e' on T', a(t) + rho(e') <= c - 1, and T' has a collision at a fresh position in [e', f'(e')).
- J2b: e' on T', and e' lies in a run of 0s of length >= c of its lane.
- Y: some trail has a collision at a fresh evaluation t'' while it has been fresh for at least c - 1 evaluations (g(t'') >= c - 1).
Proof that one occurs. Suppose not S, X, J2a. T evaluates the inputs evaluated by T' from e' on, one batch later or more, so T repeats them (non-fresh) while T' is ahead. If T' evaluates e', e' + 256, ..., f'(e') freshly (no collision there by not-J2a, and every non-fresh evaluation of T' is preceded by a collision of T'), the output at f'(e') is a DP (fresh, xi = 1), and T outputs the same DP at age a(t) + rho(e') <= c - 1, before any slice check can cut it: T is not cut, a contradiction. If the run ends first, T, which is behind, is not cut either. So T' is cut before f'(e'), with all its evaluations from e' to the cut fresh. If all evaluations of T' from its start to the cut are fresh, they are >= c consecutive 0s containing e': J2b. Otherwise T' has a non-fresh evaluation before e', hence a joining collision before e' and before t; if it is at age <= c - 1, T' is in K_B with an earlier joining collision than T, against the choice of T; if not, the first c evaluations of T' were fresh and T' collided at age >= c - 1 while fresh: Y. QED.
Expected numbers of root events, each from the hazard (L1) (a collision of t with a given earlier value has conditional probability at most 1 / N' given G_(t-1), which includes the lottery, so lottery conditions can be attached):
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum for i >= 0 of (1 - theta_D)^i = L, so E_S <= Q L / N' = 9.410e-05.
- X: E_X <= sum over pairs e' < t of P(rho(e') + g(t) >= c) / N'. Different lanes: rho(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta_D)^(c-1) + (c - 1) theta_D (1 - theta_D)^(c-2) <= p2. Same lane, e' = t - j 256: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta_D)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 1.150e-04.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of rho(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E rho = L), and each such position is a collision with probability at most (Q + 2^16) / N': E_J2a2 <= (Q + 2^16) L Q (Q - 1) / (2 N'^2). E_J2a = 1.033e-04.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta_D) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta_D) p2 = 1.100e-04.
- Y: P(g(t'') >= c - 1) <= (1 - theta_D)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 9.170e-06.
So P(K >= 3) <= P(K_A >= 3, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 3) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as EPS]; P(Binomial(n2, p) >= 3) = 1.249e-03 and P_cut = 1.680e-03 (the program's `cut_halt`). There is no premise about K: the number of cut trails is bounded by this argument, and it needs no distribution of K. The bounds on S and J2a are not small (about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

Step 7 (the sum). The attempt fails only if (no usable collision) or (an early halt) or (a disturbance after tau, Step 3). No usable collision is covered by: e^-theta on A and Z' <= z* L^2; P(Z' > z* L^2) <= EPS; P(N1 >= k) <= EPS; the complement of A, whose parts are: K >= 3 (P_cut), 60 or more collisions, a start coincidence (Q 2^16 / N), a fresh evaluation with xi = 1 returning an earlier DP value (at most k (k + 60) L / N <= k^2 L / N + Q k / N), a free finished trail longer than c (P_long), and the early halts. Early halts: the third cut (P_cut, counted once); the table full (finished trails are at most N1 + 59, so tmax keys need N1 >= tmax - 59: P_table = 2.1e-11); a key false match (P_key = 6.2e-12: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^56 * 174 = 2^63.44); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 8.30e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^32 hits with probability at most e^(-0.386 M / 2^32), so with 240 M <= Q (checked: M = 3.361e+35, Q = 3.566e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). P_long: a free finished trail longer than c is fresh from its start, so its lottery from its start has c 0s and a 1 within the next S positions; by (L5) and Wald's identity the expected number of trails with that property is (1 - theta_D)^c (1 - (1 - theta_D)^S) E[J] <= e^(-c/L) (S / L) (q + 256 + H + 1), J the number of trails started (finished trails <= N1 + collisions, at most CMAX = 2 cut restarts), and k + 258 >= q + 256 + H + 2: P_long = 1.9e-21. All terms of order 2^-99 or below are collected in P_tiny (each of its five terms is below 2^-96; the program charges 2^-90). This proves the lemma. QED.
Consequently P_F >= 1 - e^-theta - 2 EPS - P_cut - delta - P_key - P_table - P_long - P_tiny = 1 - 0.605284690 - 2.000e-03 - 1.680e-03 - 1.035e-03 - 6.2e-12 - 2.1e-11 - 1.9e-21 - 2^-90 = 0.390000001 (float, planned at 0.390000001), and the exact certificate of Appendix A is 0.390000006430 >= 0.39 (B is the least multiple of 10^24 that reaches the planning target).

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0073 bit for eps = 0.01 (Tp 173); 0.0372 bit for eps = 0.05 (Tp 169); 0.0760 bit for eps = 0.10 (Tp 165); 0.2078 bit for eps = 0.25 (Tp 150).

Remark on CMAX = 2 (the only difference from the CMAX = 1 form of Lemma 2 v2 used in our later entries): every use of CMAX in the proof is explicit. The cut trails enter only through K <= CMAX on A (Step 5), through CUT = CMAX (M Q + min(...)) (5.1 (c), each cut trail bounded on its own), through the number of trials n2 = k + 256 + CMAX and the threshold CMAX + 1 in Step 6 (i), through the term K_B >= 1 (which does not depend on CMAX) and through the restarts counted in P_long (Step 7). Setting CMAX = 1 gives the text of the later entries.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of g from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 174 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Clause (d) replaces the fixed-U birthday step of the earlier Lemma 2 of this entry (62cfd777), which the judges asked to be either proved or declared in their ruling on our round-4 entry 41b32afc (same Lemma 2; finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4); it is both: Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish), and (d) is the premise that g has that hazard. Nothing else in the success bound is heuristic: Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0073 bit for eps = 0.01, 0.0372 bit for eps = 0.05, 0.0760 bit for eps = 0.10, 0.2078 bit for eps = 0.25 (Section 4). The only evidence for (a) to (d) is the 18-bit and 21-bit program checks of Section 6, which do not reach the full 256-bit event and are not used as estimates.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). The program also prints its own observations (`python3 bsrho.py --stats`, seeds from SHA-256 of a counter), which are untrusted and are only descriptive:
    T3 n=18: attempts returning a verified pair: target 178 of 256, ideal function 182 of 256
    T1 n=12 fresh K: 256 runs, mean first repeat 80.01 (sqrt(pi N/2) = 80.21)
    T2 width 256, K=0: 2048 points, 21-bit projections, equal pairs per trial if uniform 0.9995, trials with a pair if uniform 0.6319
      source uniform (86 trials): returned pairs 58 (uniform reference 54.3); w0 83 (uniform reference 86.0); w3 82 (uniform reference 86.0); w7 91 (uniform reference 86.0); xor8 76 (uniform reference 86.0); sum8 74 (uniform reference 86.0); p01 80 (uniform reference 86.0); p23 88 (uniform reference 86.0)
      source counter (85 trials): returned pairs 51 (uniform reference 53.7); w0 91 (uniform reference 85.0); w3 88 (uniform reference 85.0); w7 95 (uniform reference 85.0); xor8 88 (uniform reference 85.0); sum8 86 (uniform reference 85.0); p01 96 (uniform reference 85.0); p23 87 (uniform reference 85.0)
      source iterates (85 trials): returned pairs 59 (uniform reference 53.7); w0 84 (uniform reference 85.0); w3 84 (uniform reference 85.0); w7 72 (uniform reference 85.0); xor8 69 (uniform reference 85.0); sum8 92 (uniform reference 85.0); p01 88 (uniform reference 85.0); p23 89 (uniform reference 85.0)
Run by the organizer's pipeline on this program with the public seed (the pipeline reruns each experiment and requires identical output), reported without inference:
    bsrho-n18 (organizer run, public seed): 167 of 256 trials returned a pair that the organizer verified; ideal-function control (program's own) 167 of 256; family-law runs at n = 12 (program's own): mean first repeat 82.46; halts target 87, ideal 88.
    proj-k0-w256 (organizer run): 165 of 256 trials returned a verified pair; by source: uniform 56 of 86; counter 57 of 85; iterates 52 of 85; equal pairs in the seven projections (program's own), total over 256 trials: w0 261, w3 266, w7 252, xor8 256, sum8 240, p01 287, p23 234.
Every unsuccessful attempt of the width-18 experiment ended with a halt of the program (the halts equal the unsuccessful trials). At width 18 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4). It happens equally for the ideal function.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; the bit-sliced search above width 18. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the extra time of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bsrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`bsrho-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 8 batches, cut rule, table, recovery on the packed circuit) on the target chain g (K = 0: the block 0^32 || x, the low 18 bits of g); the trial returns the two 64-byte messages 0^32 || x, 0^32 || y when the attempt succeeded and two nulls otherwise. The checked event is that the complete 3-round digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 12.
`proj-k0-w256`: per trial, 2048 points of the K = 0 target at width 256 evaluated with the bit-sliced circuit (source by trial index mod 3), returning two points whose digests agree in the low 21 bits when the set contains such a pair. The digests are recovered from the stored planes by XOR with q before the projections are formed. The checked event is that the digests agree in the low 21 bits and the messages are distinct. Observations (untrusted): equal-pair counts of seven projections.
They check the circuit at full width, the bit-sliced search, lane insertion and extraction, the table, the recovery, the mask q and the message construction on the real target. They do not measure the cost or the success probability at width 256. Running times on the development machine: 2.7 s and 4.1 s.

## 7. Memory

Table: 12,494 entries * 25 bytes = 312,350 bytes (the table region is empty until the search starts). An entry is the key (8 bytes), the trail number t (2 bytes) and the length (15 bytes), kept in three arrays (keys 4 per word, numbers 16 per word, lengths one per 15 bytes); `pack_entry` of the program builds and checks it.
Code: 19,085 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 687,060 bytes (loop body 17275, handlers 1,000, recovery 650, setup, cut and slice 160).
Counters and copies: 16,384 bytes (trail numbers 512, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 1,024 registers, counted as memory: 32,768 bytes. No advice. Memory peak = max(setup phase 981,617, search phase 1,048,562) = 1,048,562 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. This is the search phase; the setup phase, in which the circuit generator runs, is smaller (981,617 bytes, Section 3.6). Claim `memory_log2_bytes` = 20. `python3 bsrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 687,060 - 32,768 - 16,384) / 25) = 12,494, and Tp = 174 is the plan of Appendix A: the mean number of trails is the largest that the table holds with a capacity tail below 2^-40, and Tp is the largest integer (found by bisection; any Tp is a valid plan) for which the success bound of Section 4 reaches the planning target 0.390000001 at that mean (Appendix A computes both and certifies P_F >= 0.39 in exact arithmetic).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical) and H3 (the 1,024-register machine convention and the 36-byte instruction charge, score-critical). The cut-count heuristic H2 and the age-independence approximation of the filed text are withdrawn: Lemma 2 v2 proves them. There is no prefix, no advice and no polarity climb; the entry has no two-block mode.
Credited to 6ae36351 (jungjipdo): the pivot full adder (Section 3.2) and the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote both from the text of its proof and did not use or run its files. Credited to our 0a9640ed, 3356413f and cf8b0e92 and to Jbenisek's e479cbbf: the relation, the trail-and-table search, the handlers, the recovery, the ledger method, the declared register file and the experiments' form.
The recovery circuit has 8 more operations than in 0a9640ed (the XOR with q) and the program has a longer generator (the pivot rule), both charged.

## 9. Response to the findings of the judges' rulings

Revision of our own 62cfd777 (B3R3PV, 124.8123, filed 10-14; no ruling of its own yet). The success proof (Section 4, Lemma 2) is replaced by Lemma 2 v2, a theorem about the random function with no premise besides H1 (the cut-count heuristic H2 and the independent-ages approximation of the filed text are withdrawn, the Chernoff tail is an upper bound certified in exact arithmetic by Appendix A); the program changes only in the success-bound functions (`_zq`, `_lossq`, `_b256`, `plan`, `loss`; the generator, the step and the search are unchanged); B and Tp are re-planned (time_log2 124.83986 against 124.8123, Tp 174 against 177); the cut limit CMAX = 2 of the filed program is kept and handled exactly by the proof (Step 6). The findings of the ruling on our B3R7 1cd0dd3b (its Lemma 2 and its heuristic H2 are the same text as the filed text of this entry) are answered here by id, and so are the findings of the ruling on our round-4 entry 41b32afc (the same Lemma 2 of the filed text). 
Ruling on 1cd0dd3b (our B3R7, the sibling entry whose Lemma 2 and H2 are the same text): status refuted, reasons lane_cryptanalysis/F1-mgf-midpoint-not-upper-bound, lane_cryptanalysis/F2-exact-poisson-cut-law-false.
- lane_cost/F1-register-model-conditional (material): Not a Lemma 2 matter and unchanged: the machine convention H3 and the ledger it supports are as in the filed entry (this revision changes no operation count of the main loop; the program differs only in the success-bound functions `_zq`, `_lossq`, `_b256`, `plan`, `loss`, which set Tp and B, and the ledger rows that follow from them).
- lane_cost/F2-full-scale-success-extrapolation (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_cost/F3-obsolete-memory-scalar (minor): Not a Lemma 2 matter; the score text of this entry is unchanged by this revision and is not addressed here.
- lane_cryptanalysis/F1-mgf-midpoint-not-upper-bound (fatal): Confirmed and fixed. The filed `_zq` of this entry (62cfd777) used the same midpoint sum. It is replaced by the trapezoid sum of the same convex integrand, which is an upper bound of the integral (proof Section 4, Step 5.3); the block-length coupling, the shift and the atom at the cap are bounded explicitly and the program multiplies by 1 + 2^-30. Appendix A (`certify`) recomputes z*, w and the whole bound in exact rationals and 60-digit decimals with outward rounding and asserts P_F >= 0.39 (certified value 0.390000006430). B is re-planned on the new bound (Tp 174 against 177, time_log2 124.83986 against 124.8123 of the filed 62cfd777).
- lane_cryptanalysis/F2-exact-poisson-cut-law-false (fatal): Confirmed. H2 is withdrawn (removed from claim.json, the proof, the restrictions and the note): no premise about the cut count remains, and the age-independence approximation of the filed Lemma 2 (the 256 ages independent exponentials) is gone too (Step 5.2 replaces it by i.i.d. lottery blocks without selection). Theorem of proof Section 4, Step 6: K = K_A + K_B; K_A (cut trails whose first c evaluations are fresh) is at most the number of successes of an i.i.d. Bernoulli(p) trial sequence before failure number k + 256, so P(K_A >= 3, N1 <= k - 1) <= P(Binomial(k + 258, p) >= 3) (CMAX = 2 in this entry: the program halts at the third cut trail; the proof is written with CMAX explicit); K_B (cut trails that join another path or close a cycle) needs one of five root events, each bounded by an expected count from the lazy-sampling hazard. P_cut = 1.68e-03; the finite support of K is no longer in conflict with any statement.
- lane_cryptanalysis/F3-h1-full-scale-evidence-gap (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_cryptanalysis/F4-round-number-regression-text (minor): Text only: the validation sentences of this 3-round entry say 3 rounds (blake3(M(x), 3)), the target's round count; unchanged by this revision.
- lane_evaluability/F1-H1-full-scale-evidence-gap (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_evaluability/F2-H2-poisson-support-gap (material): Confirmed. H2 is withdrawn (removed from claim.json, the proof, the restrictions and the note): no premise about the cut count remains, and the age-independence approximation of the filed Lemma 2 (the 256 ages independent exponentials) is gone too (Step 5.2 replaces it by i.i.d. lottery blocks without selection). Theorem of proof Section 4, Step 6: K = K_A + K_B; K_A (cut trails whose first c evaluations are fresh) is at most the number of successes of an i.i.d. Bernoulli(p) trial sequence before failure number k + 256, so P(K_A >= 3, N1 <= k - 1) <= P(Binomial(k + 258, p) >= 3) (CMAX = 2 in this entry: the program halts at the third cut trail; the proof is written with CMAX explicit); K_B (cut trails that join another path or close a cycle) needs one of five root events, each bounded by an expected count from the lazy-sampling hazard. P_cut = 1.68e-03; the finite support of K is no longer in conflict with any statement.
- lane_evaluability/F3-current-scalar-description (minor): Not a Lemma 2 matter; the score text of this entry is unchanged by this revision and is not addressed here.
- lane_experiments/F1-full-scale-extrapolation-gap (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_experiments/F2-no-statistical-inference-from-frequencies (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_experiments/F3-no-trusted-cost-validation (material): Not a Lemma 2 matter and unchanged: the machine convention H3 and the ledger it supports are as in the filed entry (this revision changes no operation count of the main loop; the program differs only in the success-bound functions `_zq`, `_lossq`, `_b256`, `plan`, `loss`, which set Tp and B, and the ledger rows that follow from them).
- lane_experiments/F4-round-reference-typo-in-validation-description (minor): Text only: the validation sentences of this 3-round entry say 3 rounds (blake3(M(x), 3)), the target's round count; unchanged by this revision.
- heuristic assessments H1-random-function-model: unchanged (declared premise, see the H1 / H3 answers above).
- heuristic assessments H2-cut-count (all lanes that rated it): H2 is withdrawn, see the answer to the H2 findings above; nothing remains to be rated.
- heuristic assessments H3-machine-convention: unchanged (declared premise, see the H1 / H3 answers above).
- lane_adjudicator and lane_defender on lane_cryptanalysis/F1-mgf-midpoint-not-upper-bound and lane_cryptanalysis/F2-exact-poisson-cut-law-false (both confirmed): answered as the two findings above (Step 5.3 and Step 6).

Ruling on 41b32afc (our round-4 entry B3R4b, the same Lemma 2 of the filed text): status not_evaluable, reasons lane_cryptanalysis/heuristic/H4-finished-trail-birthday-conditioning.
- lane_cost/F-COST-REGISTERS (material): Not a Lemma 2 matter and unchanged: the machine convention H3 and the ledger it supports are as in the filed entry (this revision changes no operation count of the main loop; the program differs only in the success-bound functions `_zq`, `_lossq`, `_b256`, `plan`, `loss`, which set Tp and B, and the ledger rows that follow from them).
- lane_cost/F-COST-TIGHT-MEMORY (material): Not a Lemma 2 matter and unchanged: the machine convention H3 and the ledger it supports are as in the filed entry (this revision changes no operation count of the main loop; the program differs only in the success-bound functions `_zq`, `_lossq`, `_b256`, `plan`, `loss`, which set Tp and B, and the ledger rows that follow from them).
- lane_cost/F-SUCCESS-EXTRAPOLATION (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_cryptanalysis/F1-adaptive-finished-trail-conditioning (material): Answered by Lemma 2 v2: the fixed-size birthday step (a fixed number U of evaluations on finished trails) is gone. Step 4 is a supermartingale over the evaluations with the hazard (L1) alone, no conditioning on which trails finish; the facts it needs about the adaptivity of the program are declared as clause (d) of H1 (proof Section 5), the premise that g has the lazy-sampling hazard of F. The heuristic H4 of that ruling is therefore no longer an unproved step: Lemma 2 is a theorem about F and (d) is stated openly.
- lane_cryptanalysis/F2-full-scale-random-function-extrapolation (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_evaluability/F-EVAL-1 (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_experiments/EXP-F1 (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_experiments/EXP-F2 (material): Not a Lemma 2 matter and unchanged: H1 remains a declared, score-critical premise (clauses (a) to (d), proof Section 5); Lemma 2 v2 is a theorem about the random function F with no premise besides it. The two organizer experiments remain program checks; no inference is drawn from their counts and no new evidence is claimed.
- lane_experiments/EXP-F3 (material): Not a Lemma 2 matter and unchanged: the machine convention H3 and the ledger it supports are as in the filed entry (this revision changes no operation count of the main loop; the program differs only in the success-bound functions `_zq`, `_lossq`, `_b256`, `plan`, `loss`, which set Tp and B, and the ledger rows that follow from them).
- heuristic assessments H1-random-function-model: unchanged (declared premise, see the H1 / H3 answers above).
- heuristic assessments H2-tail-approximations (all lanes that rated it): H2 is withdrawn, see the answer to the H2 findings above; nothing remains to be rated.
- heuristic assessments H3-machine-convention: unchanged (declared premise, see the H1 / H3 answers above).
- heuristic assessments H4-finished-trail-birthday-conditioning (lane_cryptanalysis, unsupported): answered as the F1-adaptive-finished-trail-conditioning finding above (Step 4 and clause (d) of H1).

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 bsrho.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, log1p, comb

PH, FILT, LOOP, LANES = 17238, 34, 3, 256      # operations of the bit-sliced step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 35340                               # generator primitive calls (python3 bsrho.py --ledger)
PH7, EXTRA = 603, 64                            # packed recovery circuit (with the 8 XORs of q), extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 11          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE = 36, 1810, 1024 * 32, 16384, 25, 0
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
EPS, HZ, GRAIN = 1e-3, 257 / 2, 10 ** 24        # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN
body = PH + FILT + LOOP                                        # one batch = one loop body = 17,275 operations
code_bytes = (body + OTHER_CODE) * INSTR
tmax = ((1 << 20) - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in 2^20 bytes with the code
Nn, D, SB = 1 << N_BITS, S1 + W, 1 << 48


def tail_log2(mean, k):                                        # Chernoff bound on P(count >= k)
    return (-mean + k * (1 + log(mean / k))) / log(2)


def zq(q, uc, uh, n):         # (z*, lam): P(sum of n i.i.d. block terms z(min(beta, c + S)) / L^2 > z*) <= EPS (Chernoff), beta geometric of mean L
    k = 20000                 # UPPER bound on the MGF: beta <= L E + 1, E ~ Exp(1); exp(lam z(u) - u) is convex, so the trapezoid rule (chords) bounds
    h = uc / k                # its integral from above; 1 + 2^-30 covers float rounding and the 1/L shifts; certify() below redoes it in decimals
    us = [i * h for i in range(k + 1)]
    zs = [HZ * u * u + 2 * q * max(0.0, u - uh) for u in us]

    def f(lam):
        a = [lam * z - u for z, u in zip(zs, us)]
        m = max(a)
        e = [exp(x - m) for x in a]
        return (n * (m + log(((sum(e) - (e[0] + e[-1]) / 2) * h + e[-1]) * (1 + 2.0 ** -30))) - log(EPS)) / lam
    lo, hi = -16.0, -4.0
    for _ in range(50):
        m1, m2 = lo + (hi - lo) / 3, hi - (hi - lo) / 3
        lo, hi = (lo, m2) if f(exp(m1)) < f(exp(m2)) else (m1, hi)
    return f(exp((lo + hi) / 2)), exp((lo + hi) / 2)


def plower(Tp, q):            # the lower bound of Lemma 2 (v2) on the success probability, q = Q / L
    L = Fraction(1 << D, Tp)
    c = -(-KAPPA * L.numerator // L.denominator)
    uc, uh = float((c + SB) / L), float((c // 2) / L)
    k = int(q) + 1
    while tail_log2(q, k) > log(EPS, 2) - 1e-6:                 # lottery count N1 ~ Binomial(Q, 1/L) <= k - 1 except with probability EPS
        k += 1
    z = zq(q, uc, uh, k - 1 + LANES)[0]                         # at most k - 1 + LANES lottery blocks
    l2n = float(L * L / Nn)
    kap = (2 * q * uc + HZ * uc * uc + 2 * q * (uc - uh)) * l2n
    w = 1.0
    for _ in range(100):
        w = exp(w * kap)
    w *= 1 + 2.0 ** -40                                          # ln w >= w kap
    s0 = q * q / 2
    th = l2n * (w * (s0 - z - CMAX * (q * uc + min(q * (uc - uh), z / (LANES + 1) + q * float(SB / L)))) - (w - 1) * s0)   # cut trail (Step 5 (c))
    p, hq, ql, n2 = exp(-KAPPA), s0 * l2n, q * l2n, k + LANES + CMAX
    cuts = 1 - sum(comb(n2, j) * p ** j * exp((n2 - j) * log1p(-p)) for j in range(CMAX + 1))   # P(Bin(n2, p) > CMAX): fresh cut trails (Step 6 (i))
    cuts += ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA)   # colliding cut trails: S, X, J2a, J2b, Y (Step 6 (ii))
    keyfm = tmax * (tmax - 1) / 2 * 2.0 ** -(min(64 - (Tp - 1).bit_length(), N_BITS - D) + log2(Tp))
    return 1 - exp(-th) - 2 * EPS - cuts - uc * q * l2n - keyfm - 2.0 ** tail_log2(q, tmax - 59) - n2 * p * float(SB / L) - 2.0 ** -90


def plan_tp(Tp):              # the least B (a multiple of GRAIN) with plower >= 0.39
    L = Fraction(1 << D, Tp)
    lo, hi = 1.0, tmax + 1.0
    for _ in range(40):
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if plower(Tp, mid) >= P_MIN else (mid, hi)
    b = -(-int(hi * L / LANES) // GRAIN) * GRAIN
    while plower(Tp, float(b * LANES / L)) < P_MIN:
        b += GRAIN
    return L, b, -(-KAPPA * L.numerator // L.denominator)

def certify(Tp, B, K=20000):  # Lemma 2 v2 in exact rationals and 60-digit decimals (every exp and ln correctly rounded), results moved outward by 1e-40
    from decimal import Decimal as Dm, getcontext, localcontext, ROUND_CEILING, ROUND_FLOOR
    getcontext().prec = 60
    up = lambda x: x * (1 + Dm("1e-40")) + Dm("1e-58")

    def fd(x, u):             # Fraction -> Decimal rounded up (u) or down
        with localcontext() as cx:
            cx.rounding = ROUND_CEILING if u else ROUND_FLOOR
            return Dm(x.numerator) / Dm(x.denominator)
    ex = lambda x: up(fd(x, True).exp())                         # upper bound on exp(x), x rational
    L = Fraction(1 << D, Tp)
    th_D, Q, Np = 1 / L, LANES * B, Fraction(Nn) * (1 - 1 / L)
    q = Q / L
    c = -(-KAPPA * L.numerator // L.denominator)
    h, M, HF = c // 2, c + SB, Fraction(LANES + 1, 2)
    qu, qd, lnE = fd(q, True), fd(q, False), Dm("0.001").ln()
    k = int(q) + 1                                               # P(N1 >= k) <= e^-q (e q / k)^k <= EPS
    while up(-qd + k * (1 + (qu / k).ln())) > lnE * (1 + Dm("1e-40")):
        k += 1
    n = k - 1 + LANES
    lam = Dm(repr(zq(float(q), float(M / L), float(h / L), n)[1]))
    ucu, ucd, uhd, dl = fd(M / L + th_D / 2, True), fd(M / L + th_D / 2, False), fd(h / L, False), fd(3 * th_D / 2, True)
    with localcontext() as cx:
        cx.prec, cx.rounding = 40, ROUND_CEILING
        hh = ucu / K
    with localcontext() as cx:
        cx.prec = 100
        ys = [i * hh for i in range(K + 1)]                      # exact nodes, K hh >= uc + 1 / (2 L)
    zeta = lambda y: Dm(HF.numerator) / Dm(HF.denominator) * y * y + 2 * qu * max(Dm(0), y - uhd)
    ph = [(lam * zeta(y) - y).exp() for y in ys]
    mgf = up(dl.exp() * (hh * (sum(ph) - (ph[0] + ph[-1]) / 2) + (lam * zeta(ucu) - ucd + dl).exp()))
    zstar = Fraction(up((n * up(mgf.ln()) - lnE) / lam))       # P(trail sums > zstar L^2) <= EPS
    kap = fd((2 * M * Q + HF * M * (M + 1) + 2 * Q * (M - h)) / Np, True)
    w = Dm(1)
    for _ in range(200):
        w = (w * kap).exp()
    w *= 1 + Dm("1e-30")
    assert w.ln() >= w * kap                                    # ln w >= w kap0 / N'
    w = Fraction(w)
    Hs = Fraction(Q * (Q - 1), 2) + (1 << 16) * Q
    theta = (w * (Fraction(LANES * LANES * B * (B - 1), 2) - 2 * k * Q - CMAX * (M * Q + min(Q * (M - h), zstar * L * L / (LANES + 1) + SB * Q)) - zstar * L * L) - (w - 1) * Hs) / Np
    p = ex(-c * th_D)                                            # (1 - 1/L)^c <= e^(-c / L)
    p2 = ex(-(c - 1) * th_D) * fd(1 + (c - 1) * th_D / (1 - th_D), True)
    n2, H, PP = k + LANES + CMAX, Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    kt = tmax - 59
    terms = [ex(-theta), Dm("0.002"),                            # main; finished-trail count and trail sums (EPS each)
             up(1 - sum(comb(n2, j) * p ** j * (1 - p) ** (n2 - j) for j in range(CMAX + 1))),   # fresh cut trails: P(Bin(n2, p) > CMAX)
             fd(Q * L / Np, True),                               # S: a trail closes a cycle
             fd(Q / Np, True) * fd(L, True) * ex(-(c - 2) * th_D / 2) * fd(2 + (c - 1) * th_D, True) + fd(PP, True) * p2,   # X
             fd(Q * L * H / Np + (Q + (1 << 16)) * L * PP / Np, True),   # J2a
             fd(PP * (1 - th_D), True) * p2, ex(-(c - 1) * th_D) * fd(H, True),   # J2b, Y
             fd(M * (Q + (1 << 16)) / Np, True),                 # Step 3
             fd(Fraction(tmax * (tmax - 1), 2 * Tp) / (1 << min(64 - (Tp - 1).bit_length(), N_BITS - D)), True),   # key false match
             up((-qd + kt * (1 + (qu / kt).ln())).exp()),           # table capacity
             n2 * p * fd(SB * th_D, True),                       # long finish
             fd(Fraction(Q << 16, Nn) + Fraction(Q * k, Nn) + k * k * L / Nn, True) + up((-300 + (Dm(5).exp() - 1) * fd(H, True)).exp()) + Dm(2) ** -99]
    assert Fraction(Q, 1 << 32) * Fraction(108, 1000) > 1000 and 240 * M <= Q   # stage-1 budget (Step 6): below e^-1000, inside the last term
    return 1 - sum(terms)


lo, hi = 1.0, tmax + 1.0                                       # the largest mean number of trails the table holds (tail within 2^-40)
for _ in range(60):
    mid = (lo + hi) / 2
    lo, hi = (mid, hi) if tail_log2(mid, tmax + 1) <= -40 else (lo, mid)
a, z = 1, 4097                                                 # bisection: a Tp that reaches 0.39 at that mean (any Tp is a valid plan; not claimed optimal)
while z - a > 1:
    m = (a + z) // 2
    a, z = (m, z) if plower(m, lo) >= P_MIN else (a, m)
Tp = a
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 17275", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 4200", CMAX * CUTOPS),
        ("recovery: (c + 2^48) * (603 + 64) + 600", capr * (PH7 + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
print("P_lower = %.5f" % plower(Tp, float(B * LANES / L)))
pc = certify(Tp, B)
print("P_lower certified (exact rationals, 60-digit decimals) = %s" % str(pc)[:14])
assert pc >= Fraction(39, 100)
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
Tp = 174  tmax = 12494  B = 1392885148265000000000000000000000000  e2max = 166044848950505256652832031314  c = 336126619623771829929698337082385985
memory bytes = 1048562
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000006430
main loop: B * 17275                                 24062090936277875000000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6433078755010868121644600
stage-1 hits: e2max * 2800                           464925577061414718627929687679200
finished trails: tmax * (3800 + 3 * tmax)            515777308
cut trails: 2 * 4200                                 8400
recovery: (c + 2^48) * (603 + 64) + 600              224196455289055810563296534643417460147
setup and generator                                  11329200
N = 24286287856492514305056770173441753898855
certificate: 2^12483985 * 638^100000 <= N^100000 < 2^12483986 * 638^100000
log2(N/C) = 124.8398531735
time_log2 = 124.83986
```
