# blake3-r6: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk, at 6 rounds, with a rolled round body (B3R6c)

Credited derivative of our own 57174971-f105-4b04-8fc5-c337e5917061 (B3R6b, blake3 round 6, time_log2 125.03893, memory_log2_bytes 20.64109, scalar score 125.68002: the same search, plan method, success proof (Section 4) and experiments; this entry replaces its straight-line six-round step, whose code alone is larger than 2^20 bytes, by a rolled one and so removes the memory term) and of our own a2e94df7-bff4-4461-ad40-7f75930cb241 (B3R7c, blake3 round 7, time_log2 125.29113, memory_log2_bytes 20: the rolled round body, its generator, ledger and proof, here at six rounds), which derive from our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (blake3 round 4, 125.06000, filed 10-15: the entry that introduced the supermartingale Lemma 2 of Section 4 and clause (d) of H1, which answer the finding F1-adaptive-finished-trail-conditioning / H4 of the judges on 41b32afc), of our own 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (blake3 round 4, 125.02375, rejected by the judges on that one finding about the success-probability argument), of our own 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (blake3 round 4, 125.35348), of our own 62cfd777-5613-463f-b561-e2340e00e528 (blake3 round 3, 124.8123: this program at three rounds), of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448, two-block mode with a fixed first block; this entry does not use that mode), which are derivatives of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). It also uses two circuit and walk ideas from jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), whose proof text (3.3, 3.4) we read as data and re-implemented in our own generator without using or running any file of that entry: (1) the pivot full adder, (2) the mask walk g = f XOR q in which the digest planes are fed back exactly as the circuit stores them. Everything else is the program of those entries: relation, trail-and-table search with distinguished points, handlers, recovery walk, ledger method, the register file and the 36-byte instruction charge.
The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. The chain step is 46,214 operations for 256 trails (180.52 per trail; 38,790 for the straight-line six-round step of 57174971, 55,210 for the rolled seven-round step of a2e94df7). What this entry changes against 57174971: the straight-line step has 38,790 instructions and with the other code is larger than 2^20 bytes, so 57174971 claimed memory_log2_bytes 20.64109 and paid 0.64109 bit in the lane's scalar score (`hashsmash-scalar-tm-v1`: time_log2 + max(0, memory_log2_bytes - 20)). Here the step is a ROLLED program: rounds 1 and 2 as straight-line code (constants folded), then one generic round body executed 4 times, with the 16 message words moved between iterations by the BLAKE3 permutation as charged register moves (Section 3.2). The program is 19,803 instructions, the whole code 804,456 bytes, and the memory of the entry is 1,048,512 bytes = 2^19.99992 <= 2^20, so the memory term is 0. The price is time: the loop body has no folded zero message words (+1,232 gates per round), the permutation costs 576 moves per iteration, and the loop control and the setup of the message slots are charged; the step is 46,214 operations against 38,790. time_log2 125.25234 against 125.03893 (+0.21341); scalar score 125.25234 against 125.68002 (-0.42768). The table is the largest that fits in 2^20 bytes (16,828 entries of 10 bytes), and with it Tp, B and c are re-planned (Section 7). The experiments and the proof of Section 4 are those of 57174971 and a2e94df7 with the new numbers.

What changed against a2e94df7 (B3R7c): ROUNDS = 6 (unit 1,262), the round loop runs 4 iterations, the recovery circuit is 1299 operations, and Tp, B, c and the table (16,828 entries) are re-planned by the same program (Tp 241, time_log2 125.25234, success bound certified 0.390000005034); the generator, the ledger method, Section 4 and the experiments are a2e94df7's with these numbers.

## 1. Target and relation

Target `blake3-r6-prefix-v1` (the benchmark's blake3 round-6 profile, six rounds). The two colliding messages are 64 bytes, M(x) = 0^32 || LE32(x): 32 zero bytes (words m0..m7 = 0) followed by the 256-bit integer x (words m8..m15, little endian). It is one chunk of one block: chaining value IV, counter 0, block length 64, flags 11 = CHUNK_START | CHUNK_END | ROOT, 6 rounds with the BLAKE3 message permutation between rounds, digest = the 8 words v[i] XOR v[i+8] (i < 8), little endian (this is `verifier/blake3.py:blake3(M(x), 6)`). Write f(x) for the digest read as a 256-bit little-endian integer.
The walk is on g(x) = f(x) XOR q, where q is the fixed 256-bit mask of the polarities of the 256 digest planes of the circuit that the generator of Section 3.2 builds (the notation of the earlier entries, where q had weight 112); in this rolled program all digest planes are stored upright, q = 0 (printed by `python3 bsrho.py --ledger`), so g = f. g(x) = g(y) if and only if f(x) = f(y): XOR with a constant is a bijection. The attack outputs x != y with g(x) = g(y), hence f(x) = f(y), and M(x) != M(y) are two distinct messages with equal complete 256-bit digests (a finite byte string of 64 bytes is in the profile's message domain, "Finite byte strings of bit length below 2^64").
The scalar digest of the program (`digest_words`) was compared outside the shipped experiments (`ext/ref_check.py` and `ext/ref_regress.py`, not shipped) with the organizer reference `verifier/blake3.py:blake3(M, r)` at 3 rounds, at 4 rounds and at 6 rounds (the target), on 2000 random 64-byte messages each (half of the form 0^32 || x): 0 differences. At 7 rounds (the full BLAKE3, the same round function) the program's digest and the organizer reference were also compared with the `blake3` library (version 1.0.11) on 2,000 random 64-byte messages, the reference also on ten lengths from 0 to 3,000 bytes: 0 differences. The bit-sliced step was compared with the organizer reference `blake3(M(x), 6)` on 8,192 random messages (one step: stored planes equal blake3(M(x), 6)) and on 4,096 lanes (16 x 256) chained for 7 steps, the packed recovery circuit on 448 messages, the scalar digest on 300 messages: 0 differences in each; the rolled step was also compared with the straight-line step of 57174971 (`ext/rolled_vs_straight.py`, not shipped) on 16,384 random lanes, among them inputs with few nonzero planes and sparse or dense inputs, lane by lane: 0 differences. The program's own selftest (`python3 bsrho.py --selftest`) compares the step against the scalar compression on 4,096 lanes (16 batches of 256, the full 256-bit g), 4,096 lanes chained for 7 steps, the flat listing run by an interpreter of its loop control against the compiled step, the width-18 chain, the packed circuit, and prints the counts of shared and unused gates of the generator (both 0).

## 2. The attack (program `experiments/bsrho.py`, sections 3 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 241. The density is theta = 241 / 2^122 and L = 1 / theta = 2^114.0871. The key of a DP is the 56 bits of x above bit 121 followed by the 8 low bits of F (F < 241 <= 2^8, so those 8 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated rolled program of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 32 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above. If the key is in the table, go to 6. Otherwise store t under the key (10-byte entry: key and t, no length, Section 7) and
   start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 13 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 16,828 keys, when a second trail would be cut, or if step 6 finds no pair.
6. Recovery, two passes, each of at most capr batches. Pass 1 (lengths): the two trails t and t' with the same key are walked together from their starts r + t and r + t' (both lanes of one packed circuit), one step per batch, and after each step each lane that has not finished is tested for being a DP (low 32 bits zero, then the next 90 bits below Tp); the step count at which a lane first is a DP is its length, l1 for the longer trail, l2 for the other. Pass 2: advance the longer trail from its start by l1 - l2 steps of g, then step both together; at the first step
   with g(a) = g(b) and a != b output (a, b). Both lanes of one packed circuit (1299 operations: the six-round compression, straight line, no XOR with q since q = 0; used by nothing else) are used. At most capr = c + S batches are run in each pass (the program halts if a lane has not reached a DP after capr steps in pass 1, or if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = 241, L = 5316911983139663491615228241121378304 / 241, B = 1365545272934000000000000000000000000, Q = 256 B = 1.02732 * 2^128 evaluations,
e2max = 162785681835889816284179687564, c = 286804380833259856394182436243061901 (= 2^117.788), table capacity tmax = 16,828 entries of 10 bytes. The trail numbers t stay below 2^16 (finished trails <= 16,828, cut trails <= 1, plus the 256 starts), so the 2-byte field of an entry never overflows (the program asserts it when it stores an entry); every length is below c + S < 2^117.8 and is recomputed by pass 1 of the recovery, not stored.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (q = 0 is derived by the generator).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry (as in 0a9640ed, which passed the judges with it). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores, and it gives no register count.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 1856 registers (a declared convention of the entry, H3, supporting; Section 3.5). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each.
The main loop has no loads and no stores. It has register moves, all charged: the 576 plane copies of the message permutation after each of the first 3 iterations of the round loop (Section 3.2). The generated program needs 1827 registers (`listing` in the program assigns them; the chain output is written into the registers 0..255 that held the input planes, so the next batch reads the same registers), leaving 29 of the 1856 for the loop counters, the limit and the handlers' temporaries. The file of 1856 registers is counted as memory: 59,392 bytes (Section 7).
Constants are immediates. The organizer's reference count C(r6) = 1,262 (222, 430, 638, 846, 1,054, 1,262 for 1 to 6 rounds, that is 14 + 208 r; the value printed by the lane contract, `pareto_candidate.py --family blake3 --rounds 6 --show-contract`: reference_operation_cost 1262) is used only as the unit: Unit = 1,262 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers; the rolled program is not given a shorter encoding, and no instruction is decoded for free: the loop control is instructions that are executed and charged (Section 3.2).

### 3.2 One batch = 46251 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j is a 256-bit integer whose bit l is bit j of the word of lane l. A rotation is a renaming of planes (no operation). XOR, AND, OR of words are 32 operations each. The sum of two words is a ripple of full adders over the planes; the lowest bit has 2 gates (no carry in) and the highest 2 (no carry out), and constants (the IV words, the zero words m0..m7, the length and the flag word) are folded at build time wherever the operand is a constant.
The full adder is the pivot adder of 6ae36351 (our re-implementation, `Gen.fa`). Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free inside a segment. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the third as the pivot p and the two equal ones as x and y. With u = x XOR p and v = y XOR p: sum = u XOR y, carry = (u AND v) XOR p, because maj(x, y, p) = p XOR ((x XOR p) AND (y XOR p)). u and v have equal polarity, so the AND is always one gate (an AND of two upright planes, or an OR of two inverted planes, with the result's polarity set); every full adder with three variable inputs is 5 gates (XOR for u, XOR for the sum, XOR for v, the AND, XOR for the carry). With one constant input, sum = x XOR y XOR k and carry = x AND y or x OR y (2 or 3 gates); with two the plane passes through.
**The rolled program** (`listing` in the program; registers: x and output planes 0..255, state words 256..767, message slots 768..1279, temporaries of the loop body from 1312). One step executes, in this order:
(A) Rounds 1 and 2 as straight-line code with the constants folded: 2,614 + 7,184 = 9,798 gates. Round 1 is cheap because the state is constant and m0..m7 = 0; from round 2 on every plane depends on x (a straight-line round costs 7,184 gates). The 512 state planes are written into the registers 256..767.
(B) A plane that the generator stores inverted (polarity 1) gets one complement, one operation each: 240 operations. This puts all 512 state planes upright, which the loop body needs: its input and output polarity must be equal in every iteration, and for upright inputs the pivot rule produces only upright outputs (the generator checks it: no output of the body has polarity 1).
(C) The message slots of round 3: the 16 slots of 32 planes are set up in registers 768..1279 as the message words of the third round (slot s holds word P^2[s] of 0^32 || x): 256 planes set to zero and 256 planes copied from the x planes: 512 operations.
(D) The round loop, 4 iterations (rounds 3 to 6). The body is ONE generic round of 8,416 gates with no constant operand: all 16 message slots are real operands, so the 8 zero words are not folded (a folded round has 7,184 gates, the generic one 8,416: 1,232 more per round, charged in each of the 4 iterations). The state words are read from and written to the registers 256..767 in place (the 512 output planes of the body are pinned to the registers of the 512 input planes; the generator checks that no input plane is still needed when its register is written), the message operands are read from the slot registers 768..1279 and are not changed by the gates.
(E) The message permutation between iterations. The BLAKE3 permutation of the message words is PERM = (2, 6, 3, 10, 7, 0, 4, 13, 1, 11, 12, 5, 9, 14, 15, 8): slot s takes the content of slot PERM[s]. It consists of two cycles of 8 slots. It is carried out by plane copies (register moves, one operation each): per cycle one word (32 planes) is saved in a temporary word, 7 words are moved and the saved word is moved into its place: 9 word copies = 288 moves per cycle, 576 per permutation. The permutation is executed after iterations 1 to 3 and not after the last one (the loop leaves before it): 3 x 576 = 1,728 operations. Re-indexing instead of copying is not used: an instruction names its registers, and the one copy of the body, executed 4 times, reads the same slot registers each time; so the moves are real operations and are counted as such.
(F) Loop control, charged: the counter is set (1 operation); at the end of each iteration it is decremented, compared with zero and a conditional branch leaves the loop when it is zero (3 operations, 4 times); an unconditional jump to the start of the body (1 operation, 3 times): 16 operations. The five loop-control records are instructions of 36 bytes like the others.
(G) The digest: for each of the 256 digest planes j, state plane j XOR state plane j + 256 (word i XOR word i + 8, plane by plane), written into register j: 256 operations (these are the output planes of the step and the input planes of the next batch).
Executed per step: 9,798 + 240 + 512 + 1 + 4 x (8,416 + 3) + 3 x (576 + 1) + 256 = **46,214 operations** (35,916 XOR, 6,638 AND, 1,164 OR gates and 2,480 complements, copies and zero settings, 16 loop-control operations), no other operation. Per trail 180.523 operations = 0.1430 unit, against 1 unit for a compression. The static code of the step has 19,803 instructions: A 10,550, loop control 5, body 8,416, message permutation 576, digest 256. For comparison the straight-line step of 57174971 has 38,790 gates and 38,790 instructions: the rolled program saves 18,987 instructions of code and costs 7,424 more operations per step (19.1 percent).
The mask walk: the output planes are stored in registers 0..255 exactly as the circuit produces them and they are the 256 input planes of the next batch (a chain with no move), and they are upright: q = 0, g = f; the notation of the mask walk (g = f XOR q, equality under g equivalent to equality under f, Section 1) is kept because the recovery circuit and the experiments use it with q = 0.
Validation: the flat listing of the program (all records including the loop control) was executed by an interpreter and by the compiled step against the scalar digest in the selftest; the compiled rolled step against the straight-line step of 57174971 on 16,384 lanes (0 differences) and against the organizer reference (Section 1).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 46,214 + stage-1 test 34 + batch-loop control 3 = 46251 operations (the batch loop is the loop over batches; the round loop of Section 3.2(F) is inside the 46,214). Stage 1: the 32 low planes of digest word 0 (stored planes, which are the planes of the next point x) are combined into the mask of zero lanes: 31 ORs over the 32 planes, a complement, a compare of the mask with zero and a branch: 34 operations (`stage1_ops`). The test loses no event: a DP has all 32 low bits zero, so its lane is flagged.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no flagged lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers):
- Stage-1 hit (a flagged lane): store the 256 planes to a 8 KiB copy in memory (256 stores), then a loop over the planes: load, shift right by the lane number, AND 1, shift left by the plane number, OR into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit (the polarity XOR of the earlier entries is not needed any more). The hit budget e2max is enforced by a halt.
- Finished trail (a DP, new start): key formation, two read-modify-write field stores of the 10-byte entry, the new start r + t' (1 add), insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Total below 3,550; charged **3,800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 1,024), slice counter: charged **1,300** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **4,200**; at most 1 cut trail (a halt on the second).
- Recovery batch (both lanes in one packed circuit, 1299 operations) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch (1363 per batch). The first l1 - l2 steps of pass 2 move one lane only and need no test, also inside the 1363. A pass-1 batch (both lanes in the same packed circuit) has no equality test; it needs the loop increment, compare and branch (3), call and return and the 8 moves (10), the DP test of each of the two lanes (low-32-bit word: shift, AND, branch; window test: shift, AND, compare, branch; 7 operations per lane, 14 for the two) and the two finished flags (6): 33 operations, also inside the 1363. The recovery is charged as two passes of capr batches each, every batch at 1363: the passes are bounded by halts (a lane that has not reached a DP after capr steps, or l1 > capr, halts the program).
- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; fixed part charged 813,600. The generator: 74,552 primitive calls (two passes over the two segments of the program, 37,276 constructor calls per pass) and 19,803 emitted lines, each charged 200 word operations: 18,871,000. Setup and generator together 19,684,600 operations = 2^13.93 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size, instructions: the step 19,803 + stage-1 test 34 + batch-loop control 3 + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery 1,346 (the 1299-operation circuit, the test, the loop, the call and the moves) + setup, cut and slice 160 = 22,346 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 46251 | 63,157,834,418,470,434,000,000,000,000,000,000,000,000 (= 6.3158e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6.307e+24 |
| stage-1 hits: e2max * 2,800 | 4.5580e+32 |
| finished trails: 16,828 * (3,800 + 3 * 16,828) | 913,491,152 |
| cut trails: 1 * 4,200 | 4,200 |
| recovery: 2 passes * (c + 2^48) * (1299 + 64) + 600, c + 2^48 = 2^117.788 | 7.8183e+38 |
| setup and generator | 19,684,600 |
N = 63,939,663,616,421,815,815,831,575,443,869,985,057,034 = 6.393966e+40 operations.
N / 1,262 = 5.0665e+37 units = 2^125.252339. Claim `time_log2` = 125.25234 (integer power certificate in Appendix A, rounded up with 1.2e-06 of slack). The main loop is 98.78 percent of it, recovery 1.22 percent.

### 3.5 Register file
Convention H3: the machine has R = 1856 registers of 256 bits: 1827 are used by the generated program (an exact count of `listing`, not a bound) and 29 are left for the loop counters, the limit and the handlers' temporaries, as in 57174971. The program uses 256 registers for the x and output planes, 512 for the state, 512 for the 16 message slots, and from register 1312 the temporaries (the loop body needs 515 of them: the generator pins the outputs of the round to the state registers, so the intermediate state words of the round live in temporaries; an allocation that updates the state in place would use fewer registers and was not built; the temporaries include the temporary word of the cycle moves of the message permutation). The register file is counted as memory: 59,392 bytes (Section 7). The straight-line program of 57174971 declared 800 registers; this one is larger because the loop body keeps its message slots, the state words in two places and its temporaries in registers.
We did not price smaller register files for the rolled program: the spill pricing of 57174971 (Belady allocation of the straight line) was written for a straight-line program, and no spill allocator exists for the loop body. A machine with fewer registers would need loads and stores in the loop body; that cost is NOT in this entry and not claimed (limitation of H3).

### 3.6 Generator code and peak storage of the setup
The generator that builds the program at the start of the run is part of the machine code of this entry. It is the freestanding C program `GEN_C` embedded in `experiments/bsrho.py` (`python3 bsrho.py --gen-c`, 10,597 bytes). It builds the two networks of Section 3.2 (segment 0 = rounds 1 and 2, 10,055 nodes; segment 1 = one generic round, 9,441 nodes) with the pivot adders and allocates the registers, each segment in two passes, and keeps no node table. Pass 0 of a segment builds the network, counts the uses of every node (8 bits per node) and records the register of every output node (the output planes are pinned: plane k to register 256 + k). Pass 1 builds the same network again; every signal carries its register, an operand whose use count reaches zero frees its register (temporaries only), the result takes the pinned register of an output node, else the lowest free register, else a new one, and the instruction record is written. This is possible because neither network has a shared or an unused gate (Section 3.2). The generator then writes the complements, the message slots of round 3, the loop-control records, the message-permutation copies and the digest XORs directly. It emits the same listing as the reference generator `listing` of the Python program. The code of the generator is charged at its size compiled to WebAssembly by clang -Os: 2,249 instructions (`llvm-objdump -d`, one line per instruction), 36 bytes each = 80,964 bytes. q = 0 falls out of the generator; nothing is searched or stored.
Its scratch (the static arrays of the C program, `gen_scratch` of the program): per node of the larger segment (10,056 nodes) an 8-bit use count and a 16-bit pinned register = 30,168 bytes, signal state 2,432 (the 16 x 32 state words 2,048, the temporary and message word 128 each, the free-register bitmap 128), shadow stack 2,048, result record 68: 34,716 bytes. The generator builds each segment twice; its work is charged in the setup row (Section 3.3).
Layout. The setup phase holds the main code (counted at its final size, 804,456 bytes; it is written as the generator emits it), the counters and plane copy (16,384), the generator's code image (80,964) and its scratch (34,716): 936,520 bytes. The generator is never called after setup. In the search phase the same region holds the table (168,280 bytes), the register file (59,392) and the counters: main code + counters + register file + table = 1,048,512 bytes. The memory of the entry is the larger of the two, 1,048,512 bytes (64 bytes to spare under the 1,048,576-byte budget = 2^20); the region is 244,056 bytes against 115,680 bytes of generator image and scratch. The setup phase fits inside the search-phase memory with this layout.
Measured peak memory of the generator (not the machine model, which is the byte account above): (i) the circuit generator written in freestanding C (source embedded in `experiments/bsrho.py` as `GEN_C`, printed by `python3 bsrho.py --gen-c`, 10,597 bytes) compiled to WebAssembly (clang -Os, 2,048-byte shadow stack) and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes (the memory budget 2^20) emits the identical program: 19,803 instructions, 1827 registers, 10,055 nodes (larger segment), 74,552 primitive calls (both passes of both segments), q = 0, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total 855,556 bytes (the final code region 804,456, the counters 16,384, its own scratch 34,716); the guest uses 14 pages (highest nonzero byte 855,712) (the generator's code image, charged in the model at 80,964 bytes, lies outside the guest memory in this sandbox). It needs 14,206,554 wasm operations, below the 18,871,000 word operations the ledger charges for the generator. (ii) The same C program as a static x86-64 binary without libc (a 4,003-byte text segment, 853,608 bytes of bss) runs under `prlimit --as=1,048,576` (its whole address space capped at 2^20 bytes) and writes the identical program (sha256 equal); it does not start under 995,328 of address space. (iii) The entry's generator is the C program of (i) and (ii), run within the caps shown; the Python generator in `experiments/bsrho.py` is only the reference whose output text the C program reproduces (sha256 equal).
No other run determines a number of the claim: the program, its size, its registers, q and the instruction count come from the generator, which was run under the caps shown above; the plan (Tp, B, c, tmax) is a deterministic computation of `plan(256)` from the stated formulas, and the experiments and checks of Sections 1, 5 and 6 test the program and select nothing.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 14.0, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (936,520 bytes), and nothing it produces is stored outside the 1,048,512 bytes of the search phase.

### 3.8 Memory and the scalar score
The lane's scoring policy is `hashsmash-scalar-tm-v1` (memoryUnitBytes 1,048,576, minimumMemoryUnits 1): score = time_log2 + max(0, memory_log2_bytes - 20). The byte count of the search phase is 1,048,512 bytes (Section 7), 2^19.99992; the claim states memory_log2_bytes = 20, the log2 of the 2^20-byte budget, which is an upper bound of it: the memory term is 0 and the scalar score is time_log2 = 125.25234. Our B3R6b (57174971) had a straight-line step whose code alone was larger than 2^20 bytes and memory_log2_bytes 20.64109, so its score was 125.03893 + 0.64109 = 125.68002; this entry removes the memory term at the price of +0.21341 bit of time: 125.25234 against 125.68002 (-0.42768). The memory budget is a hard limit here (2^20 bytes, Section 7), and the table is the largest that fits.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values and N = 2^256. Write A_F for the procedure with every evaluation of g replaced by an evaluation of F (lazy sampling), and P_F for its success probability over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Lemma 2 below is a theorem about F: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F); it has no premise besides H1 (a premise about g, not about F). H1 clause (d) (Section 5) is the premise that the lazy-sampling hazard of F also holds for the adaptive choices of the program (which trails finish, are cut or abort depend on earlier outputs). The numbers below are printed by `python3 bsrho.py --loss` (the function `_lossq`; Appendix A recomputes them with its own copy).

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 241 <= 2^8 and the key holds its 8 low bits), so equal keys of two DPs differ only if their bits above 177 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 1.02732 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) the batch of t; N = 2^256, theta_D = Tp / 2^122 = 1 / L, c = ceil(13 L) = 286804380833259856394182436243061901, S = 2^48, M = c + S, h = floor(c / 2), q = Q / L = 15845.42, N' = (1 - theta_D) N, tmax = 16,828, CMAX = 1 (the program halts when a second trail would be cut), H = (Q (Q - 1) / 2 + 2^16 Q) / N' = 0.52770, and z(m) = 128.5 m (m + 1) + 2 Q (m - h)+ (257 / 2 = (LANES + 1) / 2). Let F be a uniformly random function on 256-bit values and P_F the success probability of the attempt when every evaluation of g is replaced by F (lazy sampling). Let k = 16316 be the least integer with e^-q (e q / k)^k <= EPS = 1e-03; let z* L^2 with z* = 6.2414e+06 be a number with e^(-s z*) Phi_up(s)^n <= EPS for some s > 0, where n = k - 1 + 256 = 16571 and Phi_up is the function of Step 5.3; let w >= 1 satisfy ln w >= w kap0 / N' with kap0 = 2 M Q + z(M) (kap0 / N = 0.00269, w = 1.00270). Put
    theta = [ w (P0 - 2 k Q - CUT - z* L^2) - (w - 1) (Q (Q - 1) / 2 + 2^16 Q) ] / N' = 0.50042,
    P0 = 256^2 B (B - 1) / 2,   CUT = M Q + min( (M - h) Q, z* L^2 / 257 + S Q ).
Then, with no premise,
    P_F >= 1 - e^-theta - 2 EPS - P_cut - delta - P_key - P_table - P_long - P_tiny,
where
    P_cut = P(Binomial(k + 257, p) >= 2) + E_S + E_X + E_J2a + E_J2b + E_Y   (Step 6), p = e^(-c/L) >= (1 - 1/L)^c, p2 = e^(-(c-1)/L) (1 + (c - 1) theta_D / (1 - theta_D)), PP = Q (Q - 1) / (2 N'),
        E_S = Q L / N', E_X = (Q / N') L e^(-(c-2)/(2L)) (2 + (c - 1)/L) + PP p2, E_J2a = Q L H / N' + (Q + 2^16) L PP / N', E_J2b = PP (1 - theta_D) p2, E_Y = e^(-(c-1)/L) H,
    delta = M (Q + 2^16) / N'   (Step 3),
    P_key = C(tmax, 2) / (2^kb Tp), kb = 56,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59),
    P_long = (k + 257) e^(-c/L) S / L,
    P_tiny = Q 2^16 / N + Q k / N + k^2 L / N + exp(-300 + (e^5 - 1) H) + 2^-99   (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bsrho.py --loss` (the function `_lossq`; Appendix A recomputes them with its own copy) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000005034 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^24 for which the float bound reaches 0.390000001 (Appendix A). H1 (Section 5) is the only premise of this entry: it states that the real attempt succeeds at least as often as A_F. Lemma 2 is a theorem about F.

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
Claim 1. Let C_t occur with y in Y_t, and assume that after t no fresh evaluation on the trail of y before f(y) is a collision, and that the run does not stop early (second cut, table full, stage-1 budget, key false match). Then the program outputs a pair. Proof. Let x be the input of t and p_k the input of y, so F(x) = F(p_k): the trail of t continues with the points p_(k+1), p_(k+2), ... that the trail of y evaluates after y. The j-th of them is evaluated by the trail of y in batch b(y) + j and by the trail of t in batch b(t) + j > b(y) + j, so the trail of t only repeats points that were already evaluated (not fresh). By (ii), (iii) and the assumption, the trail of y is not cut and its evaluations up to f(y) are fresh with no collision; f(y) is the first position with xi = 1, so the trail of y finishes there, with a DP, within c batches and before the halt. The trail of t reaches the same point d(y) - 1 batches after t, in batch b(t) + d(y) - 1 <= B; before its finishing evaluation it has done at most a(t) + d(y) - 1 <= c - 1 evaluations by (iv), so no slice check cuts it, and it finishes with the same DP. The two trails are different (y is not on the trail of t, (i)), the inputs x and p_k are different (x is fresh) and F(x) = F(p_k): Lemma 1 applies. QED.
Claim 2. For fresh t the values F(y), y in Y_t, are pairwise different. Proof. If y and y' in Y_t, y' evaluated later, had the same value, V_(y') would equal an earlier value, so y' is a collision on its own trail, against (ii). QED.

Step 3 (disturbance). After the first usable collision tau the trail of y has at most c further fresh evaluations before f(y), each a collision with conditional probability at most (Q + 2^16) / N' by (L1); so P(C occurs and the program does not halt early) >= P(C occurs) - delta - P(early halt), delta = M (Q + 2^16) / N' = 8.659e-04.

Step 4 (a supermartingale). S_t = sum of |Y_s| over s <= t; u_t = |Y_t| / N' and h_t = (t - 1 + 2^16 - |Y_t|) / N' (for every t); H_t = sum of the h_s; R_t = number of unusable collisions up to t; w >= 1 a constant; M_t = exp(S_t / N' - (w - 1) H_t) w^(R_t) 1[no usable collision up to t]. For fresh t with xi_t = 0, P(C_t | G_(t-1)) = u_t exactly (L1, Claim 2) and P(D_t | G_(t-1)) <= h_t (at most t - 1 + 2^16 earlier values exist, |Y_t| of them usable), so E[M_t / M_(t-1) | G_(t-1)] <= e^(u_t - (w - 1) h_t) (1 - u_t + (w - 1) h_t) <= 1 (the factor is 1 - P(C) + (w - 1) P(D), and 1 + x <= e^x); for the other t, M_t <= M_(t-1). Hence E M_Q <= 1 and P(M_Q >= e^x) <= e^-x. The same computation with every collision at a fresh t with xi_t = 0 counted (hazard at most (t - 1 + 2^16) / N') gives E[w^(#collisions)] <= e^((w - 1) H), so P(60 or more collisions) <= exp(-300 + (e^5 - 1) H) with w = e^5 (here H = 0.5277; the term is charged in P_tiny).

Step 5 (counting S_Q from below). Let A be the event: no usable collision; the run lasts Q evaluations; K <= 1 (K the number of cut trails); fewer than 60 collisions; no start coincides with a value; no fresh evaluation with xi = 1 returns an earlier DP value; N1 <= k - 1; no free finished trail is longer than c. On A count the pairs (y, t) with b(y) < b(t): P0 = 256^2 B (B - 1) / 2. A pair is in S_Q (y in Y_t, t fresh, xi_t = 0) unless one of the following holds.
5.1 The lost pairs.
(a) xi_t = 1, or y has a DP output: at most 2 k Q pairs (at most k - 1 positions with xi = 1, at most k - 1 fresh DP outputs, (L4); a non-fresh y is on a colliding trail, (b)).
(b) y or t on a colliding trail (a trail that contains a collision): at most 2 M Q pairs per colliding trail, and on A there are at most R_Q of them. Charged as R_Q kap0 with kap0 = 2 M Q + z(M) (the z(M) part is no longer needed with the blocks of 5.2 and is kept as slack).
(c) the cut trail (K <= 1 on A; if it is colliding it is already in (b)). As y: (iii) fails for all its y, at most M Q pairs. As t: its evaluations are fresh with xi = 0 and conditions (i) to (iii) concern y only, so a pair (y, t) is lost through t only by (iv) second part, a(t) + d(y) > c. For a y on a free finished trail with d(y) = d, the evaluations of the cut trail with age above c - d are at most d + S (its ages are below M), so these pairs are at most the sum of d(y) + S over y, which is at most the sum over free finished trails of X(m) + S Q, X(m) = m (m + 1) / 2; and also at most (M - h) Q (the t of age above h, each with at most Q partners; for a(t) <= h the loss needs d(y) > c - h and is charged to y in (g)). Since 257 X(m) <= z(m), on Z <= z* L^2 the cut trail costs at most CUT = M Q + min((M - h) Q, z* L^2 / 257 + S Q).
For the remaining trails (free trails that are finished or open: every evaluation fresh, no collision), with m the length:
(d) y and t on the same trail: at most X(m) pairs.
(e) y on an open trail of age a <= m: (iii) fails (b(f(y)) > B); the pairs with b(t) > b(y) are at most 256 a (a - 1) / 2 <= 256 X(m).
(f) y on a finished free trail: by (iv) first part the batches b(t) > B - d(y) + 1 are lost, at most 256 (d(y) - 1) per y, in all at most 256 X(m).
(g) (iv) second part: a(t) + d(y) > c forces a(t) > h or d(y) > c - h; at most (m - h)+ evaluations of each kind per trail, so at most 2 Q (m - h)+ pairs per trail.
Hence S_Q >= P0 - 2 k Q - R_Q kap0 - CUT - Z, where Z = sum over the free finished or open trails of z(m).
5.2 Trail sums by lottery blocks. A free trail lies in one lottery block of its lane: all its evaluations are fresh, so xi = 0 at every non-final position (the output is not a DP) and, if it finished, xi = 1 at its last. Its length is at most min(beta, M) for that block. Two free trails that are finished or open lie in different blocks: a finished free trail ends at the 1 of its block, and an open trail is the last trail of its lane (the cut trail, which may share a block with one of them, is charged in (c)). As z is increasing, on N1 <= k - 1, by (L3'),
    Z <= sum of z(min(beta, M)) over the blocks of the run <= Z' := sum for i <= k - 1 + 256 of z(min(beta_i, M)),
a sum of n = 16571 independent identically distributed terms, with no selection and no indexing of trails. In particular the sum of X(m) over free finished trails is at most Z / 257.
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

Step 6 (the cut count; no premise). Let K be the number of trails that the run cuts or would cut (the second one halts the run). Split K = K_A + K_B: K_A counts the cut trails whose first c evaluations are all fresh, K_B the others.
(i) K_A. A trail counted by K_A has c fresh evaluations with non-DP outputs at c consecutive positions of its lane, so xi = 0 there; different such trails of a lane use disjoint positions. Scan each lane with trials: a trial starts at the current position u and succeeds if the c positions u, ..., u + c - 1 are all 0 (next trial at u + c); otherwise it fails at its first 1 (next trial after that 1). The scan of a lane stops at the first trial that would start after the run. Inside a maximal run of 0s the trials start at its first position and succeed floor(length / c) times, the largest number of disjoint length-c windows it holds; so K_A on a lane is at most the successes on that lane. Every failure but the last of a lane ends at a 1 of the run, so the failures are at most N1 + 256 <= k - 1 + 256 on N1 <= k - 1. Trial outcomes are independent Bernoulli(p'), p' = (1 - theta_D)^c <= p = e^(-c/L) (disjoint positions of an i.i.d. lottery; lanes concatenated as in (L3')). All successes therefore occur before failure number k + 256 of an infinite i.i.d. trial sequence, and two successes before that failure mean two successes among the first n2 = k + 257 trials:
    P(K_A >= 2, N1 <= k - 1) <= P(Binomial(n2, p) >= 2) = 1 - (1 - p)^n2 - n2 p (1 - p)^(n2 - 1)
(the tail increases with p, so p = e^(-c/L) is allowed).
(ii) K_B. A trail T in K_B has a first non-fresh evaluation at age <= c - 1. Its previous evaluation t (age a(t) <= c - 2, T fresh up to t, so a(t) <= g(t), where g(t) is the number of consecutive 0s of the lottery just before t on its lane) is fresh, and V_t equals the input of an earlier fresh evaluation e' (the first evaluation of that input; a start is excluded). Call t the joining collision of T and e' its target. For a lane position e let rho(e) be the number of positions from e to the first 1 at or after e (inclusive), and f'(e) that position: rho is a function of the lottery, so it is determined by G. Choose T in K_B with the earliest joining collision. One of the following root events occurs:
- S: e' is on T itself. T then cycles through its own non-DP points and is cut.
- X: e' is on another trail T' and a(t) + rho(e') >= c (hence g(t) + rho(e') >= c).
- J2a: e' on T', a(t) + rho(e') <= c - 1, and T' has a collision at a fresh position in [e', f'(e')).
- J2b: e' on T', and e' lies in a run of 0s of length >= c of its lane.
- Y: some trail has a collision at a fresh evaluation t'' while it has been fresh for at least c - 1 evaluations (g(t'') >= c - 1).
Proof that one occurs. Suppose not S, X, J2a. T evaluates the inputs evaluated by T' from e' on, one batch later or more, so T repeats them (non-fresh) while T' is ahead. If T' evaluates e', e' + 256, ..., f'(e') freshly (no collision there by not-J2a, and every non-fresh evaluation of T' is preceded by a collision of T'), the output at f'(e') is a DP (fresh, xi = 1), and T outputs the same DP at age a(t) + rho(e') <= c - 1, before any slice check can cut it: T is not cut, a contradiction. If the run ends first, T, which is behind, is not cut either. So T' is cut before f'(e'), with all its evaluations from e' to the cut fresh. If all evaluations of T' from its start to the cut are fresh, they are >= c consecutive 0s containing e': J2b. Otherwise T' has a non-fresh evaluation before e', hence a joining collision before e' and before t; if it is at age <= c - 1, T' is in K_B with an earlier joining collision than T, against the choice of T; if not, the first c evaluations of T' were fresh and T' collided at age >= c - 1 while fresh: Y. QED.
Expected numbers of root events, each from the hazard (L1) (a collision of t with a given earlier value has conditional probability at most 1 / N' given G_(t-1), which includes the lottery, so lottery conditions can be attached):
- S: the inputs of T before and at t are a(t) + 1 <= g(t) + 1 values; E[g(t) + 1] <= sum for i >= 0 of (1 - theta_D)^i = L, so E_S <= Q L / N' = 6.661e-05.
- X: E_X <= sum over pairs e' < t of P(rho(e') + g(t) >= c) / N'. Different lanes: rho(e') - 1 and g(t) are independent and dominated by geometric variables on {0, 1, ...}, so the probability is at most P(at most one 1 in c - 1 Bernoulli trials) = (1 - theta_D)^(c-1) + (c - 1) theta_D (1 - theta_D)^(c-2) <= p2. Same lane, e' = t - j 256: if a 1 lies between them the two runs of 0s are disjoint and the same bound p2 holds; if the j positions are all 0, the probability is at most (1 - theta_D)^j T(c - 1 - 2j) with T the tail above (T = 1 below 1); the sum over j of these is at most L e^(-(c - 2)/(2L)) (2 + (c - 1)/L). Hence E_X <= (Q / N') L e^(-(c-2)/(2L)) (2 + (c-1)/L) + PP p2 = 1.820e-05.
- J2a: two collisions, t (joining onto e') and t' on T' at a position in [e', f'(e')). If t' < t: for a given t', the e' with t' in [e', f'(e')) on the same lane are at most g(t') + 1, so the targets of t are at most the sum over collisions t' < t of g(t') + 1, and E_J2a1 <= Q L H / N'. If t' > t: the positions in the windows [e', f'(e')) of earlier joining targets number at most the sum of rho(e') over collisions t, with expectation at most L Q (Q - 1) / (2 N') (E rho = L), and each such position is a collision with probability at most (Q + 2^16) / N': E_J2a2 <= (Q + 2^16) L Q (Q - 1) / (2 N'^2). E_J2a = 7.029e-05.
- J2b: P(e' lies in a run of 0s of length >= c) <= (1 - theta_D) p2 (the 0s before and after e' are dominated by two independent geometric variables), so E_J2b <= PP (1 - theta_D) p2 = 1.670e-05.
- Y: P(g(t'') >= c - 1) <= (1 - theta_D)^(c - 1) <= e^(-(c-1)/L), times the collision hazard summed over t'': E_Y <= e^(-(c-1)/L) H = 1.193e-06.
So P(K >= 2) <= P(K_A >= 2, N1 <= k - 1) + P(N1 >= k) + P(K_B >= 1) <= P(Binomial(n2, p) >= 2) + E_S + E_X + E_J2a + E_J2b + E_Y + [P(N1 >= k), charged once as EPS]; P(Binomial(n2, p) >= 2) = 6.843e-04 and P_cut = 8.573e-04 (the program's `cut_halt`). There is no premise about K: the number of cut trails is bounded by this argument, and it needs no distribution of K. The bounds on S and J2a are not small (about Q L / N' each); they are the real cost of trails that close a cycle or join a path that is itself disturbed.

Step 7 (the sum). The attempt fails only if (no usable collision) or (an early halt) or (a disturbance after tau, Step 3). No usable collision is covered by: e^-theta on A and Z' <= z* L^2; P(Z' > z* L^2) <= EPS; P(N1 >= k) <= EPS; the complement of A, whose parts are: K >= 2 (P_cut), 60 or more collisions, a start coincidence (Q 2^16 / N), a fresh evaluation with xi = 1 returning an earlier DP value (at most k (k + 60) L / N <= k^2 L / N + Q k / N), a free finished trail longer than c (P_long), and the early halts. Early halts: the second cut (P_cut, counted once); the table full (finished trails are at most N1 + 59, so tmax keys need N1 >= tmax - 59: P_table = 3.4e-12); a key false match (P_key = 8.2e-12: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^56 * 241 = 2^63.91); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 8.14e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^32 hits with probability at most e^(-0.386 M / 2^32), so with 240 M <= Q (checked: M = 2.868e+35, Q = 3.496e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). P_long: a free finished trail longer than c is fresh from its start, so its lottery from its start has c 0s and a 1 within the next S positions; by (L5) and Wald's identity the expected number of trails with that property is (1 - theta_D)^c (1 - (1 - theta_D)^S) E[J] <= e^(-c/L) (S / L) (q + 256 + H + 1), J the number of trails started (finished trails <= N1 + collisions, at most one cut restart), and k + 257 >= q + 256 + H + 1: P_long = 4.8e-22. All terms of order 2^-99 or below are collected in P_tiny (each of its five terms is below 2^-96; the program charges 2^-90). This proves the lemma. QED.
Consequently P_F >= 1 - e^-theta - 2 EPS - P_cut - delta - P_key - P_table - P_long - P_tiny = 1 - 0.606276812 - 2.000e-03 - 8.573e-04 - 8.659e-04 - 8.2e-12 - 3.4e-12 - 4.8e-22 - 2^-90 = 0.390000001 (float, planned at 0.390000001), and the exact certificate of Appendix A is 0.390000005034 >= 0.39 (B is the least multiple of 10^24 that reaches the planning target).

Sensitivity to H1 (d). If the hazard of a collision is (1 - eps) / N instead of 1 / N (clause (d) of H1; the same sensitivity as a deficit eps of the pair-collision rate in clause (a)), the plan of this program (same lemma with N / (1 - eps)) needs, to restore 0.39: 0.0072 bit for eps = 0.01 (Tp 240); 0.0370 bit for eps = 0.05 (Tp 235); 0.0759 bit for eps = 0.10 (Tp 229); 0.2075 bit for eps = 0.25 (Tp 209).

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved: an assumption, no proof is known. Its content, in the terms Lemma 2 uses, is four clauses: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of g from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 241 / 2^122; (d) adaptivity: the program chooses its points, and which trails finish, are cut or abort, from earlier outputs of g; clause (d) is that this adaptivity does not lower the collision hazard, that is, for every fresh evaluation, given the whole history of the run and which later outputs are distinguished points, the output equals a given earlier non-distinguished output with probability at least 2^-256 (the lazy-sampling hazard that F has by construction, L1 of Section 4). Clause (d) replaces the fixed-U birthday step of the earlier Lemma 2, which the judges asked to be either proved or declared (41b32afc, finding F1-adaptive-finished-trail-conditioning, aggregate heuristic H4); it is both: Lemma 2 now proves the bound for F from the hazard alone (a supermartingale over the evaluations, no conditioning on which trails finish), and (d) is the premise that g has that hazard. Nothing else in the success bound is heuristic: Lemma 1, the lazy-sampling facts, the supermartingale, the counting of pairs, the Chernoff bounds and the cut count are proved in Section 4 for F; Sections 3 and 7 are counts of the program. Sensitivity: a hazard (1 - eps) / N costs the same as a deficit eps in clause (a): 0.0072 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0759 bit for eps = 0.10, 0.2075 bit for eps = 0.25 (Section 4). The only evidence for (a) to (d) is the 18-bit and 21-bit program checks of Section 6, which do not reach the full 256-bit event and are not used as estimates.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). The program also prints its own observations (`python3 bsrho.py --stats`, seeds from SHA-256 of a counter), which are untrusted and are only descriptive:
    T3 n=18: attempts returning a verified pair: target 178 of 256, ideal function 182 of 256
    T1 n=12 fresh K: 256 runs, mean first repeat 82.51 (sqrt(pi N/2) = 80.21)
    T2 width 256, K=0: 2048 points, 21-bit projections, equal pairs per trial if uniform 0.9995, trials with a pair if uniform 0.6319
      source uniform (86 trials): returned pairs 48 (uniform reference 54.3); w0 73 (uniform reference 86.0); w3 72 (uniform reference 86.0); w7 91 (uniform reference 86.0); xor8 84 (uniform reference 86.0); sum8 74 (uniform reference 86.0); p01 64 (uniform reference 86.0); p23 102 (uniform reference 86.0)
      source counter (85 trials): returned pairs 54 (uniform reference 53.7); w0 82 (uniform reference 85.0); w3 90 (uniform reference 85.0); w7 98 (uniform reference 85.0); xor8 83 (uniform reference 85.0); sum8 102 (uniform reference 85.0); p01 86 (uniform reference 85.0); p23 96 (uniform reference 85.0)
      source iterates (85 trials): returned pairs 54 (uniform reference 53.7); w0 85 (uniform reference 85.0); w3 86 (uniform reference 85.0); w7 102 (uniform reference 85.0); xor8 96 (uniform reference 85.0); sum8 81 (uniform reference 85.0); p01 93 (uniform reference 85.0); p23 92 (uniform reference 85.0)
Run by the organizer's pipeline on this program with the public seed (the pipeline reruns each experiment and requires identical output), reported without inference:
    bsrho-n18 (organizer run, public seed): 160 of 256 trials returned a pair that the organizer verified; ideal-function control (program's own) 180 of 256; family-law runs at n = 12 (program's own): mean first repeat 79.92; halts target 96, ideal 76.
    proj-k0-w256 (organizer run): 168 of 256 trials returned a verified pair; by source: uniform 55 of 86; counter 56 of 85; iterates 57 of 85; equal pairs in the seven projections (program's own), total over 256 trials: w0 252, w3 256, w7 240, xor8 277, sum8 245, p01 246, p23 256.
Every unsuccessful attempt of the width-18 experiment ended with a halt of the program (the halts equal the unsuccessful trials). At width 18 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4). It happens equally for the ideal function.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; the bit-sliced search above width 18. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the extra time of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bsrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`bsrho-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 8 batches, cut rule, table, recovery on the packed circuit) on the target chain g (K = 0: the block 0^32 || x, the low 18 bits of g); the trial returns the two 64-byte messages 0^32 || x, 0^32 || y when the attempt succeeded and two nulls otherwise. The checked event is that the complete 6-round digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 12.
`proj-k0-w256`: per trial, 2048 points of the K = 0 target at width 256 evaluated with the bit-sliced circuit (source by trial index mod 3), returning two points whose digests agree in the low 21 bits when the set contains such a pair. The digests are read from the stored planes (q = 0) before the projections are formed. The checked event is that the digests agree in the low 21 bits and the messages are distinct. Observations (untrusted): equal-pair counts of seven projections.
They check the circuit at full width, the bit-sliced search, lane insertion and extraction, the table, the recovery, the mask q and the message construction on the real target. They do not measure the cost or the success probability at width 256. Running times on the development machine: 3.3 s and 4.7 s.

## 7. Memory

Table: 16,828 entries * 10 bytes = 168,280 bytes (the table region is empty until the search starts). An entry is the key (8 bytes) and the trail number t (2 bytes), kept in two arrays (keys 4 per word, numbers 16 per word); no length is stored (a length is below c + 2^48 < 2^117.8 and is recomputed by pass 1 of the recovery, charged in Section 3.4); `pack_entry` of the program builds and checks it.
Code: 22,346 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 804,456 bytes (the rolled step 19,803, stage-1 test 34, batch-loop control 3, handlers 1,000, recovery 1,346, setup, cut and slice 160).
Counters and copies: 16,384 bytes (trail numbers 512, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 1856 registers, counted as memory: 59,392 bytes. No advice. Memory peak = max(setup phase 936,520, search phase 1,048,512) = 1,048,512 bytes = 2^19.99992; the preprocessing is inside the setup phase. This is the search phase; the setup phase, in which the circuit generator runs, is smaller (936,520 bytes, Section 3.6). Claim `memory_log2_bytes` = 20 (the log2 of the 2^20-byte budget; the byte account 1,048,512 is 2^19.99992, below it): the scalar policy adds max(0, 20 - 20) = 0 to time_log2 (Section 3.8). `python3 bsrho.py --ledger` prints the total.
The table size is the largest that fits in 2^20 bytes: tmax = floor((1,048,576 - 64 - 804,456 - 59,392 - 16,384) / 10) = 16,828. A larger table would exceed 2^20 bytes and pay the scalar memory term; a smaller one needs shorter trails and more time (`plan(256)` at fixed code, time_log2 for table sizes 4000 entries: 125.46726; 8000 entries: 125.31634; 12000 entries: 125.27447; 16828 entries: 125.25234). Tp = 241 is the largest integer for which the success bound of Section 4 reaches 0.39 at the largest mean number of trails that the table holds with capacity tail below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Sections 4 and 5, clauses (a) to (d), score-critical) and H3 (the 1856-register machine convention, the rolled-program charges and the 36-byte instruction charge, supporting). There is no prefix, no advice and no polarity climb; the entry has no two-block mode.
Credited to 6ae36351 (jungjipdo): the pivot full adder (Section 3.2) and the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote both from the text of its proof and did not use or run its files. Credited to our 62cfd777, 0a9640ed, 3356413f and cf8b0e92 and to Jbenisek's e479cbbf: the relation, the trail-and-table search, the handlers, the recovery, the ledger method, the declared register file and the experiments' form.
The step is a rolled program and the generator is new (Sections 3.2 and 3.6), charged: the loop control, the message permutation and the message slots are counted operations and instructions. Credited to our own 57174971 and a2e94df7: the search, the plan method, Section 4, the experiments' form, the rolled step and the generator; this entry takes the machine plan of a2e94df7 to six rounds.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 bsrho.py --ledger`.

```python
from fractions import Fraction
from math import log, exp, log2, expm1, log1p

PH, STEPI, FILT, LOOP, LANES = 46214, 19803, 34, 3, 256   # operations executed by one step, instructions of its code, stage-1 test, batch loop control, lanes
GEN_CALLS = 74552                               # generator primitive calls, both passes of both segments (the C port; 2 x 37,276 in python3 bsrho.py --ledger)
PH7, EXTRA, PASSES = 1299, 64, 2                            # packed recovery circuit, extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 13          # width, stage-1 bits, window bits (D = 122), age cap in units of L
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 1
MEM_LIMIT = 1048576                                       # bytes: 2^20
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 2506, 1856 * 32, 16384, 10, 0, 64
P_MIN = 0.390000001                             # plan target: 1e-9 above 0.39 covers float rounding; certify() proves >= 0.39
EPS, HZ, GRAIN = 1e-3, 257 / 2, 10 ** 24        # Lemma 2 tail budgets, weight of a squared trail length, B is a multiple of GRAIN
body = PH + FILT + LOOP                                        # one batch = 46,251 operations
code_bytes = (STEPI + FILT + LOOP + OTHER_CODE) * INSTR
tmax = (MEM_LIMIT - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in MEM_LIMIT bytes with the code
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
    p, hq, ql, n2 = exp(-KAPPA), s0 * l2n, q * l2n, k + LANES + 1
    cuts = -expm1(n2 * log1p(-p)) - n2 * p * exp((n2 - 1) * log1p(-p))   # P(Bin(n2, p) >= 2): fresh cut trails (Step 5b (i))
    cuts += ql * (1 + (2 + KAPPA) * exp(-KAPPA / 2) + 2 * hq) + hq * p * (3 + 2 * KAPPA)   # colliding cut trails: S, X, J2a, J2b, Y (Step 5b (ii))
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
    n2, H, PP = k + LANES + 1, Hs / Np, Fraction(Q * (Q - 1), 2) / Np
    kt = tmax - 59
    terms = [ex(-theta), Dm("0.002"),                            # main; finished-trail count and trail sums (EPS each)
             up(1 - (1 - p) ** n2 - n2 * p * (1 - p) ** (n2 - 1)),   # fresh cut trails: P(Bin(n2, p) >= 2)
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
Tp = next(t for t in range(400, 0, -1) if plower(t, lo) >= P_MIN)  # the largest Tp that reaches 0.39 at that mean
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + STEPI)
rows = [("main loop: B * 46251", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 1 * 4200", CMAX * CUTOPS),
        ("recovery: 2 * (c + 2^48) * (1299 + 64) + 600", PASSES * capr * (PH7 + EXTRA) + 600),
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
P, C = 100000, 1262
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
Tp = 241  tmax = 16828  B = 1365545272934000000000000000000000000  e2max = 162785681835889816284179687564  c = 286804380833259856394182436243061901
memory bytes = 1048512
P_lower = 0.39000
P_lower certified (exact rationals, 60-digit decimals) = 0.390000005034
main loop: B * 46251                                 63157834418470434000000000000000000000000
slice checks: ceil(B / 2^48) * 1300                  6306808781226180826706900
stage-1 hits: e2max * 2800                           455799909140491485595703125179200
finished trails: tmax * (3800 + 3 * tmax)            913491152
cut trails: 1 * 4200                                 4200
recovery: 2 * (c + 2^48) * (1299 + 64) + 600         781828742151466368531308621985099990982
setup and generator                                  19684600
N = 63939663616421815815831575443869985057034
certificate: 2^12525233 * 1262^100000 <= N^100000 < 2^12525234 * 1262^100000
log2(N/C) = 125.2523387547
time_log2 = 125.25234
```
