# blake3-r4: plain birthday with 256 bit-sliced lanes, pivot full adders and a mask walk

Credited derivative of our own 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (blake3 round 4, 125.35348: this program with a 1,024-register file, 26-byte table entries with stored lengths and a one-pass recovery), of our own 62cfd777-5613-463f-b561-e2340e00e528 (blake3 round 3, 124.8123: this program at three rounds), of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, bit-sliced 256-lane chain, 124.96822, passed the judges) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448, two-block mode with a fixed first block; this entry does not use that mode), which are derivatives of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087). It also uses two circuit and walk ideas from jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), whose proof text (3.3, 3.4) we read as data and re-implemented in our own generator without using or running any file of that entry: (1) the pivot full adder, (2) the mask walk g = f XOR q in which the digest planes are fed back exactly as the circuit stores them. Everything else is the program of those entries: relation, trail-and-table search with distinguished points, handlers, recovery walk, ledger method, the register file and the 36-byte instruction charge.
The target is the plain one: the message is 64 bytes, 0^32 || x, one block, flags 11, standard IV; no prefix, no advice, no polarity climb, no scan. The chain step is 24422 operations for 256 trails (95.40 per trail; 17,238 for the three-round step of 62cfd777). What four rounds change against the three-round entry: the straight line has 24422 gates and a program of 26,502 instructions of 36 bytes (954,072 bytes) leaves 52,510 bytes (5,251 entries of 10 bytes) for the table inside 2^20 bytes (with the declared 800-register file), so the trails are long (L = 2^115.91) and the unfinished trails at the halt cost a larger share; the circuit generator of the setup was rewritten in two passes without a node table so that it fits beside the larger program (Section 3.6); a table entry holds only the key and the trail number (10 bytes): the trail lengths are not stored, and the recovery recomputes them in a first pass (step 6, Section 3.4, Section 7).

## 1. Target and relation

Target `blake3-r4-prefix-v1` (the benchmark's blake3 round-4 profile). The two colliding messages are 64 bytes, M(x) = 0^32 || LE32(x): 32 zero bytes (words m0..m7 = 0) followed by the 256-bit integer x (words m8..m15, little endian). It is one chunk of one block: chaining value IV, counter 0, block length 64, flags 11 = CHUNK_START | CHUNK_END | ROOT, 4 rounds with the BLAKE3 message permutation between rounds, digest = the 8 words v[i] XOR v[i+8] (i < 8), little endian (this is `verifier/blake3.py:blake3(M(x), 4)`). Write f(x) for the digest read as a 256-bit little-endian integer.
The walk is on g(x) = f(x) XOR q, where q is the fixed 256-bit mask (weight 130) of the polarities of the 256 digest planes of the circuit that the generator of Section 3.2 builds; q is printed by `python3 bsrho.py --ledger`. g(x) = g(y) if and only if f(x) = f(y): XOR with a constant is a bijection. The attack outputs x != y with g(x) = g(y), hence f(x) = f(y), and M(x) != M(y) are two distinct messages with equal complete 256-bit digests (a finite byte string of 64 bytes is in the profile's message domain, "Finite byte strings of bit length below 2^64").
The scalar digest of the program (`digest_words`) was compared outside the shipped experiments (`ext/ref_check.py` and `ext/ref_regress.py`, not shipped) with the organizer reference `verifier/blake3.py:blake3(M, r)` first at 3 rounds, then at 4 rounds (the target) and at the full 7 rounds, on 2000 random 64-byte messages each (half of the form 0^32 || x): 0 differences. At 7 rounds the program's digest and the organizer reference were also compared with the `blake3` library (version 1.0.11) on 2,000 random 64-byte messages, the reference also on ten lengths from 0 to 3,000 bytes: 0 differences. The bit-sliced step was compared with the organizer reference `blake3(M(x), 4)` on 8,192 random messages (one step: stored planes equal blake3(M(x), 4) XOR q) and on 4,096 lanes (16 x 256) chained for 4 steps, the packed recovery circuit on 448 messages, the scalar digest on 300 messages: 0 differences in each. The program's own selftest (`python3 bsrho.py --selftest`) compares the step against the scalar compression on 4,096 lanes (16 batches of 256, the full 256-bit g), 4,096 lanes chained for 4 steps, the register-allocated code executed on a register file, the width-18 chain, the packed circuit, and prints the counts of shared and unused gates of the generator (both 0).

## 2. The attack (program `experiments/bsrho.py`, sections 3 to 6)

Parameters for n = 256: N = 2^256, 256 lanes. A point x is distinguished (a DP) when its low 32 bits are zero and the 90-bit number F = (x >> 32) mod 2^90 is below Tp = 68. The density is theta = 68 / 2^122 and L = 1 / theta = 2^115.9125. The key of a DP is the 57 bits of x above bit 121 followed by the 7 low bits of F (F < 68 <= 2^7, so those 7 bits are F); 64 bits in all.
One fresh uniform 256-bit word r (one operation).
Trail t (t = 0, 1, 2, ...) starts at s_t = r + t mod 2^256 and follows x -> g(x) until a DP.
1. 256 trails run in the 256 lanes: lane l of the bit planes holds the current point of its trail. A batch is one evaluation of g for all 256 lanes by the generated straight line of Section 3.2. Batch counter b = 0, 1, ...; the start of a trail is the point of its lane before the batch in which it was inserted.
2. After every batch the stage-1 test (Section 3.3) forms the 256-bit mask of lanes whose 32 low planes are all zero. If it is zero, the next batch runs at once.
3. For each set bit of the mask (a stage-1 hit) the lane is extracted and the window test F < Tp decides whether it is a DP. A lane at a DP ends its trail: key as above. If the key is in the table, go to 6. Otherwise store t under the key (10-byte entry: key and t, no length, Section 7) and
   start trail t' = next index in that lane (insert the 256 bits of r + t' into the lane).
4. At every multiple of S = 2^48 batches: a lane whose trail has age >= c = 11 L batches is restarted with a new index (a cut trail).
5. The search halts (failure) after B batches, after e2max stage-1 hits, when the table holds 5,251 keys, when a third trail would be cut, or if step 6 finds no pair.
6. Recovery, two passes, each of at most capr batches. Pass 1 (lengths): the two trails t and t' with the same key are walked together from their starts r + t and r + t' (both lanes of one packed circuit), one step per batch, and after each step each lane that has not finished is tested for being a DP (low 32 bits zero, then the next 90 bits below Tp); the step count at which a lane first is a DP is its length, l1 for the longer trail, l2 for the other. Pass 2: advance the longer trail from its start by l1 - l2 steps of g, then step both together; at the first step
   with g(a) = g(b) and a != b output (a, b). Both lanes of one packed circuit (836 operations: the compression and one XOR of each of the 8 output words with the 32-bit word of q; used by nothing else) are used. At most capr = c + S batches are run in each pass (the program halts if a lane has not reached a DP after capr steps in pass 1, or if l1 > capr).
Constants (all computed by `plan(256)` of the program from the stated formulas, printed by `python3 bsrho.py --ledger`): Tp = 68, L = 1329227995784915872903807060280344576 / 17, B = 1432349394108965344396540883412795810, Q = 256 B = 1.07758 * 2^128 evaluations,
e2max = 170749353660221736955230341428, c = 860088703154945564820110450769634726 (= 2^119.372), table capacity tmax = 5,251 entries of 10 bytes. The trail numbers t stay below 2^16 (finished trails <= 5,251, cut trails <= 2, plus the 256 starts), so the 2-byte field of an entry never overflows (the program asserts it when it stores an entry); every length is below c + S < 2^119.4 and is recomputed by pass 1 of the recovery, not stored.
Per attempt: one fresh r; no restart, no amplification, no stored collision; no nonuniform advice (the mask q is derived by the generator at setup and is also written into the recovery circuit as immediates).

## 3. Operation ledger

### 3.1 Machine
Machine model declared by this entry (as in 0a9640ed, which passed the judges with it). The benchmark's cost model reads (collision-frontier-v5, `cost_model`): "Classical probabilistic 256-bit word RAM. One selected-round target compression or sponge permutation costs one unit; every other primitive word operation costs 1/C units"; its primitive operations are "256-bit load or store", "addition/subtraction modulo 2^256", "bitwise AND/OR/XOR/NOT", "shift or rotation", "comparison", "conditional branch", "independent uniform random 256-bit word"; its memory includes "code", "working state", "tables". It fixes the word size and prices loads and stores, and it gives no register count.
This entry therefore declares a load/store machine with 256-bit words, 256-bit immediates and R = 800 registers (a declared convention of the entry, H3, supporting; Section 3.5 prices smaller files). Charged: every addition, AND, OR, XOR, shift, comparison, conditional branch and the one random word; every load of a word from memory and every store of a word to memory, one operation each; every register move, one operation each.
The main loop has no loads, stores or moves: the generated straight line needs 771 registers (`allocate` in the program assigns them; output plane j is written into the register that held input plane j, so the next batch reads the same registers), leaving 29 of the 800 for the loop counter, the limit and the handlers' temporaries. The file of 800 registers is counted as memory: 25,600 bytes (Section 7).
Constants are immediates. The organizer's reference count C(r4) = 846 (222, 430, 638 and 846 for 1 to 4 rounds, the value of the organizer's `pareto/targets.py:reference_cost('blake3', r)`) is used only as the unit: Unit = 846 operations. Every instruction is charged 36 bytes of code (opcode, registers and an inline 256-bit immediate), also those with three registers; the straight line is not given a shorter encoding.

### 3.2 One batch = 24459 operations for 256 trails
Representation: a 32-bit word is 32 planes; plane j is a 256-bit integer whose bit l is bit j of the word of lane l. A rotation is a renaming of planes (no operation). XOR, AND, OR of words are 32 operations each. The sum of two words is a ripple of full adders over the planes; the lowest bit has 2 gates (no carry in) and the highest 2 (no carry out), and constants (the IV words, the zero words m0..m7, the length and the flag word) are folded at build time.
The full adder is the pivot adder of 6ae36351 (our re-implementation, `Gen.fa`). Each signal is a pair (node, polarity): the register holds the node's value and the true plane is that value XOR polarity, so complements are free. Of three variable inputs a, b, c, two have the same polarity (pigeonhole); take the third as the pivot p and the two equal ones as x and y. With u = x XOR p and v = y XOR p: sum = u XOR y, carry = (u AND v) XOR p, because maj(x, y, p) = p XOR ((x XOR p) AND (y XOR p)). u and v have equal polarity, so the AND is always one gate (an AND of two upright planes, or an OR of two inverted planes, with the result's polarity set); every full adder with three variable inputs is 5 gates (XOR for u, XOR for the sum, XOR for v, the AND, XOR for the carry). With one constant input, sum = x XOR y XOR k and carry = x AND y or x OR y (2 or 3 gates); with two the plane passes through. The program generates the straight line at run time. At this target no two gates of the network are equal and every gate is used (the reference generator `Gen`/`Step`, which would share equal gates and drop unused ones, finds none: the selftest prints 0 shared and 0 unused gates), so the machine generator of Section 3.6 builds the network in two passes and keeps no node table.
The mask walk: the circuit's 256 output planes are stored in registers exactly as the circuit produces them (a register holds the node value, the digest plane is that value XOR q_j, q_j the polarity of the signal) and they are the 256 input planes of the next batch. So no operation complements a plane, no polarity vector is chosen, and the chain is x -> g(x) = f(x) XOR q. q is a fixed constant of the circuit (weight 130 of 256); the generator derives it while it builds the circuit, and the recovery circuit uses it as 8 immediates. Equality under g is equivalent to equality under f (Section 1), so a collision of g is a collision of f.
The generated line (`python3 bsrho.py --ledger`, `--selftest`): 24422 gates = 20092 XOR + 1448 AND + 2882 OR = **24422 operations**, no complement operation. Per trail 95.398 operations = 0.1128 unit, against 1 unit for a compression.
Validation: 4,096 lanes against the scalar digest in the selftest (stored planes = f XOR q); 8,192 lanes and 4,096 lanes chained for 4 steps against the organizer reference (Section 1); the register-allocated code executed on a register file gives the same planes as the generated function (selftest).
The generator itself runs once at the start; its work is charged in the setup row (Section 3.3), its code and peak storage are accounted in Section 3.6 and Section 7.

### 3.3 Loop, stage 1, handlers and the other events
Loop body = one batch: 24422 + stage-1 test 34 + loop control 3 = 24459 operations. Stage 1: the 32 low planes of digest word 0 (stored planes, which are the planes of the next point x) are combined into the mask of zero lanes: 31 ORs over the 32 planes, a complement, a compare of the mask with zero and a branch: 34 operations (`stage1_ops`). The test loses no event: a DP has all 32 low bits zero, so its lane is flagged.
Loop control: batch counter increment, compare with the next slice limit, branch back: 3 operations. A batch with no flagged lane (probability about 1 - 2^-24) does nothing else.
Handlers (charged per event at the stated bounds; instruction sequences use the same registers):
- Stage-1 hit (a flagged lane): store the 256 planes to a 8 KiB copy in memory (256 stores), then a loop over the planes: load, shift right by the lane number, AND 1, shift left by the plane number, OR into the accumulator, address increment, plane counter increment, compare, branch (9 per plane, 2,304), find the lane in the mask (at most 8 halving steps of 5), window test of F < Tp (3 extractions and at most 12 further operations), counters. Total below 2,800; charged **2,800** per hit (the polarity XOR of the earlier entries is not needed any more). The hit budget e2max is enforced by a halt.
- Finished trail (a DP, new start): key formation, two read-modify-write field stores of the 10-byte entry, the new start r + t' (1 add), insertion of the 256 bits of the new start in the lane: per plane load, shift, AND 1, shift left by the lane number, AND with the complement of the lane bit, OR, store, address and counter increments, compare, branch (12 per plane, 3,072), reload of the 256 planes (256), lane arrays and counters (below 200). Total below 3,550; charged **3,800**. The key scan of the table is charged separately: the key array holds 4 keys per word, testing a word costs 8 operations, charged 3 per key. At most tmax finished trails (a halt on a full table).
- Slice check (every 2^48 batches): the 256 births (load, subtract, compare, branch: 1,024), slice counter: charged **1,300** each. Cut trail: insertion of the new start as above plus bookkeeping, charged **4,200**; at most 2 cut trails (a halt on the third).
- Recovery batch (both lanes in one packed circuit, 836 operations, the last 8 of them the XORs with q) plus the exact equality test of lane 0 and lane 1 on the 8 output words, which is 8 shifts, 8 XORs, 7 ORs combining the 8 words, 1 AND with the lane-0 mask, 1 compare with zero and 1 branch = 26 operations, plus loop increment, compare and branch = 3: 29 operations, plus call and return 2 and 8 moves of the digest: 39, charged as 64 per recovery batch (900 per batch). The first l1 - l2 steps of pass 2 move one lane only and need no test, also inside the 900. A pass-1 batch (both lanes in the same packed circuit) has no equality test; it needs the loop increment, compare and branch (3), call and return and the 8 moves (10), the DP test of each of the two lanes (low-32-bit word: shift, AND, branch; window test: shift, AND, compare, branch; 7 operations per lane, 14 for the two) and the two finished flags (6): 33 operations, also inside the 900. The recovery is charged as two passes of capr batches each, every batch at 900: the passes are bounded by halts (a lane that has not reached a DP after capr steps, or l1 > capr, halts the program).
- Setup and generator: 1 random word; the 256 starts r + t inserted in memory (256 x 3,100 = 793,600, each at most 12 x 256 + 28) and one reload; counters; fixed part charged 813,600. The generator: 99,448 primitive calls (two passes of 49,724 gate-constructor calls each) and 24422 emitted lines, each charged 200 word operations: 24,774,000. Setup and generator together 25,587,600 operations = 2^14.88 units, charged in the time bound (3.4). There is no other preprocessing: no scan, no climb, no advice.
Code size, instructions: loop body 24459 + handlers 1,000 (256 stores, 256 reloads, the loops and the event logic) + recovery 883 (the 836-operation circuit, the test, the loop, the call and the moves) + setup, cut and slice 160 = 26,502 instructions.

### 3.4 Total
All counts are upper bounds enforced by halts (Section 2, step 5). The exact integers are printed by the program of Appendix A.
| item | bound (operations) |
| --- | --- |
| main loop: B * 24459 | 35,033,833,830,511,183,358,594,993,467,393,572,716,790 (= 3.5034e+40) |
| slice checks: ceil(B / 2^48) * 1,300 | 6.615e+24 |
| stage-1 hits: e2max * 2,800 | 4.7810e+32 |
| finished trails: 5,251 * (3,800 + 3 * 5,251) | 102,672,803 |
| cut trails: 2 * 4,200 | 8,400 |
| recovery: 2 passes * (c + 2^48) * (836 + 64) + 600, c + 2^48 = 2^119.372 | 1.5482e+39 |
| setup and generator | 25,587,600 |
N = 36,581,993,974,288,282,239,238,033,262,672,148,067,793 = 3.658199e+40 operations.
N / 846 = 4.3241e+37 units = 2^125.023744. Claim `time_log2` = 125.02375 (integer power certificate in Appendix A, rounded up with 6.3e-06 of slack). The main loop is 95.77 percent of it, recovery 4.23 percent.

### 3.5 Register file and smaller files
Convention H3: the machine has 800 registers of 256 bits. The generated line needs 771 (peak live planes 771, no spills: `spill_ops(800)` = 0; `allocate` gives the registers and a check executes the allocated code). If the machine has fewer registers, the program's Belady allocation of the straight line (farthest next use, `spill_ops(R)`) adds loads and stores to every batch, and the table shrinks because the code grows:
| R | loads+stores per batch | operations per batch | table entries | Tp | time_log2 | success lower bound |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 800 (claimed) | 0 | 24,459 | 5,251 | 68 | 125.02374 | 0.39126 |
| 512 | 1,162 | 25,621 | 1,989 | 20 | 125.43167 | 0.39054 |
Each row is the ledger of the program with that R (register file R x 32 bytes counted as memory, spill instructions counted as code). With 256 registers the 4,715 spill loads and stores per batch make the program 1,123,812 bytes, which with its register file and counters is above 2^20 bytes, so no table fits. The claim assumes R >= 771; 800 is declared.

### 3.6 Generator code and peak storage of the setup
The generator that builds the straight line at the start of the run is part of the machine code of this entry. It is the freestanding C program `GEN_C` embedded in `experiments/bsrho.py` (`python3 bsrho.py --gen-c`, 8,620 bytes). It builds the network of Section 3.2 with the pivot adders and allocates the registers in two passes and keeps no node table. Pass 0 builds the network and counts the uses of every node (4 bits per node). Pass 1 builds the same network again; every signal carries its register, an operand whose use count reaches zero frees its register (registers 256 and above; the output planes are pinned, output plane j in register j), the result takes the lowest free register or a new one, and the instruction record is written. This is possible because the network has no shared and no unused gate (Section 3.2), and its output gates are the last 256 gates in order (the generator checks the second, the selftest the first). It emits the same program as the reference generator (`Step`, `allocate`) of the Python program. The code of the generator is charged at its size compiled to WebAssembly by clang -Os: 1,522 instructions (`llvm-objdump -d`, one line per instruction), 36 bytes each = 54,792 bytes. There is no polarity vector to search and nothing to store: q falls out of the generator, and it is written into the recovery circuit as 8 immediates.
Its scratch (the static arrays of the C program, `gen_scratch` of the program): use counts 24,679 nodes x 4 bits = 12,340 bytes, signal state 2,400 (the 16 x 32 state words 2,048, two 32-word temporaries 256, the free-register bitmap 96), shadow stack 2,048, result record 68: 16,856 bytes. The generator builds the network twice; its work is charged in the setup row (Section 3.3).
Layout. The setup phase holds the main code (counted at its final size, 954,072 bytes; it is written as the generator emits it), the counters and plane copy (16,384), the generator's code image (54,792) and its scratch (16,856): 1,042,104 bytes. The generator is never called after setup. In the search phase the same region holds the table (52,510 bytes), the register file (25,600) and the counters: main code + counters + register file + table = 1,048,566 bytes. The memory of the entry is the larger of the two, 1,048,566 bytes (10 bytes to spare under 2^20); the region is 94,494 bytes against 71,648 bytes of generator image and scratch. The table size of Section 7 is the largest that fits with this layout.
Measured peak memory of the generator (not the machine model, which is the byte account above): (i) the circuit generator written in freestanding C (source embedded in `experiments/bsrho.py` as `GEN_C`, printed by `python3 bsrho.py --gen-c`, 8,620 bytes) compiled to WebAssembly (clang -Os, 2,048-byte shadow stack) and run in a sandbox whose guest linear memory is capped at 16 pages = 1,048,576 bytes emits the identical program: 24,422 instructions, 771 registers, 24,679 nodes, 99,448 primitive calls (both passes), the same q, and the instruction text equal line by line to the Python generator's (sha256 equal). Its static arrays total 987,312 bytes (the final code region 954,072, the counters 16,384, its own scratch 16,856); the guest uses 16 pages and leaves 61,264 bytes of the 1 MiB unused (the generator's code image, charged in the model at 54,792 bytes, lies outside the guest memory in this sandbox). It needs 23,438,272 wasm operations, below the 24,774,000 word operations the ledger charges for the generator. (ii) The same C program as a static x86-64 binary without libc (a 3,229-byte text segment, 985,336 bytes of bss) runs under `prlimit --data=1048576 --stack=65536` and writes the identical program (sha256 equal); it also runs under `prlimit --as=1,179,648` and does not start under 1,114,112 of address space, where the kernel's own stack and vdso mappings no longer fit. (iii) The Python reference generator alone (`ext/gen_only.py`, not shipped) has a peak resident set of 111.3 MB under memmeter (the bare interpreter 10.0 MB); that is the footprint of the interpreter and its objects, not of the machine model, and it is not charged.
No other run determines a number of the claim: the circuit, its size, its registers, q and the instruction count come from the generator, which was run under the 1 MiB caps above; the plan (Tp, B, c, tmax) is a deterministic computation of `plan(256)` from the stated formulas, and the experiments and checks of Sections 1, 5 and 6 test the program and select nothing.

### 3.7 Preprocessing
None offline. The generator is run inside every attempt and is charged in the setup row; the claim declares preprocessing_log2 = 14.9, the setup and generator row, which is also inside time_log2. The memory figure of Section 7 covers this preprocessing: the generator runs in the setup phase of the same attempt, its code image and scratch are in the setup-phase total of Section 3.6 (1,042,104 bytes), and nothing it produces is stored outside the 1,048,566 bytes of the search phase.

## 4. Success probability

Heuristic H1 (model premise, Section 5). Let F be a uniformly random function from 256-bit values to 256-bit values. The attack uses the walk function only by evaluating g at points that the procedure chooses. Write A_F for the same procedure with every evaluation of g replaced by F (lazy sampling), and P_F for its success probability, taken over the fresh word r and over F. H1 states that the probability that the single attempt succeeds on the fixed target is at least P_F. The premise compares two success events; it is not a statement about the entropy of r or about the target as a random object, and it is declared, not proved. Sub-claims under it (the numbers below are printed by `python3 bsrho.py --loss`) are computations for the random function F, with the approximations named as the supporting heuristic H2 (they are not proved here):
H2 (a) the age of the trail of one lane at the halt is dominated by an exponential with mean L, and the 256 ages are independent, although restarts depend on the history of the run; (b) the number of cut trails is Poisson with the stated mean; (c) the loss for a cut trail enters linearly with the stated slope; (d) trail lengths are geometric with mean L (used for the repeats inside one trail).

Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 68 <= 2^7 and the key holds its 7 low bits), so equal keys of two DPs differ only if their bits above 178 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A pair inside one trail makes a cycle with no DP (the trail is then cut). A 64-bit key match without a merge ends the run (failure, cost bounded by one recovery).

Lemma 2 (for the random function F, under H2). Let U be the number of evaluations on trails finished before the halt. The number of evaluations is Q = 256 B = 1.07758 * 2^128. For F the DP indicators of the successive points of one trail are independent with probability theta, so the age of the trail of one lane at the halt (steps since its last restart) satisfies P(age >= a) <= (1 - theta)^a <= exp(-a / L), and (H2 a) the
256 ages are independent: each is stochastically dominated by an exponential with mean L. The sum of 256 such variables exceeds M L with probability at most exp(-256 (x - 1 - ln x)), x = M / 256 (Chernoff); for M = 350 this is 8.88e-07 <= 1e-6. So the 256 unfinished trails hold at most 350 L points except with probability 1e-6.
Cut trails cost at most c + S, that is 2.3456e-03 Q each; the number K of cut trails is (H2 b) Poisson with mean (Q / L) e^-11 = 4690 e^-11 = 0.0783 (P(K=0,1,2) = 0.9247, 0.0724, 0.00284; P(K>=3) = 7.55e-05, and the third cut is a halt, charged as failure).
The allowance 1.5e-4 Q already in U covers 0.06 of one cut trail; for K = 1 and K = 2 the remaining loss lowers the success probability by 1.33e-03 and 2.75e-03 (H2 c: slope of 1 - exp(-U^2/2N) at the target, 2 * 0.497 * e^-0.497 = 0.605 per unit of relative loss), and K >= 3 is charged as failure, so the cut-trail deficit is 0.0724 * 1.33e-03 + 0.00284 * 2.75e-03 + 7.55e-05 * 0.3916 = 1.335e-04. Hence U >= (1 - 1.5e-4) Q - 350 L - 1 = 0.99700 * 2^128 when K = 0 and the ages are within the bound. For U distinct inputs the probability of no colliding pair is
prod (1 - i/N) <= exp(-U(U-1)/(2N)) <= exp(-0.497) (the program's B is the least that gives U(U-1) >= 2 * 0.497 N). The expected number of colliding pairs inside a single trail is at most Q L / N = 2^-11.98 = 2.48e-04 (H2 d: a trail of length l has at most l(l-1)/2 pairs, E[l^2] <= 2 L^2, and there are Q / L trails). The expected number of key false matches (two different DP ends with the same 64-bit key: the key space is 2^57 * 68 = 2^63.09) is below 5,251^2 / 2 / 2^63.09 = 1.4e-12.
Programmed aborts. Table capacity: the number of finished trails is at most the number of DP events among the Q evaluations, binomial with mean Q / L = 4690 (and no more than a Poisson count of the same mean in the Chernoff bound); the abort needs 5,252 or more, probability at most exp(-mean) (e mean / 5,252)^5,252 = 2^-46.8 = 8.1e-15 (Chernoff bound). Stage-1 budget: the number of stage-1 hits is at most binomial with
mean mu2 = Q / 2^32 = 8.54e+28 and the abort needs 2 mu2 + 65, probability at most e^(-mu2 (2 ln 2 - 1)) = e^(-3.3e+28). A recovery that finds no pair needs a key false match or a start lying on another trail (at most 1.4e-12 + 2^-100).
The losses add to 1e-06 + 2.48e-04 + 1.335e-04 + 1.4e-12 + 8.1e-15 + 7.9e-31 < 3.821e-04, so P_F >= 1 - e^-0.497 - 3.821e-04 = 0.3913 >= 0.39. The 0.0013 left over is kept as margin.
If the real pair-collision rate is (1 - eps) of the model, P stays at least 0.39 for eps <= 0.0042, and in general at most 0.5 * log2(1/(1-eps)) more bits of time restore 0.39: 0.0072 for eps = 0.01, 0.037 for 0.05, 0.076 for 0.10, 0.21 for 0.25.

## 5. Premise H1 and its evidence

H1 is the model premise of Section 4. It is a premise about one fixed function g and about one attempt; it cannot be tested at width 256: the full 256-bit functional graph, trails longer than 2^40 and 2^128 evaluations cannot be observed. It is declared and not proved. Its content, in the terms the ledger uses, is: (a) for the inputs the search evaluates, the outputs behave as the outputs of F, uniform and independent, so that two distinct evaluated inputs collide with probability 2^-256 (this entry uses no input difference and does not claim that none exists); (b) the iterates of g from the starts r + t have the first-collision law of a random mapping; (c) whether an iterate is a DP is independent of the collision events and has probability 68 / 2^122. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits (0.0072 for eps = 0.01), listed in Section 4 and in the note.
Evidence that the program is right and that nothing gross is wrong is produced by the two organizer experiments (Section 6). They are program checks: the organizer recomputes every returned pair, the counts of returned pairs are reported, and they are not used as estimates of any number of this entry. No quantitative inference is drawn from a count, no confidence interval is formed, and the entry does not rely on the independence of trials (the trial seeds are public and the experiment is a check of the program). The program also prints its own observations (`python3 bsrho.py --stats`, seeds from SHA-256 of a counter), which are untrusted and are only descriptive:
    T3 n=18: attempts returning a verified pair: target 175 of 256, ideal function 182 of 256
    T1 n=12 fresh K: 256 runs, mean first repeat 74.84 (sqrt(pi N/2) = 80.21)
    T2 width 256, K=0: 2048 points, 21-bit projections, equal pairs per trial if uniform 0.9995, trials with a pair if uniform 0.6319
      source uniform (86 trials): returned pairs 44 (uniform reference 54.3); w0 73 (uniform reference 86.0); w3 105 (uniform reference 86.0); w7 91 (uniform reference 86.0); xor8 76 (uniform reference 86.0); sum8 97 (uniform reference 86.0); p01 85 (uniform reference 86.0); p23 81 (uniform reference 86.0)
      source counter (85 trials): returned pairs 58 (uniform reference 53.7); w0 99 (uniform reference 85.0); w3 91 (uniform reference 85.0); w7 80 (uniform reference 85.0); xor8 76 (uniform reference 85.0); sum8 80 (uniform reference 85.0); p01 80 (uniform reference 85.0); p23 71 (uniform reference 85.0)
      source iterates (85 trials): returned pairs 51 (uniform reference 53.7); w0 71 (uniform reference 85.0); w3 90 (uniform reference 85.0); w7 82 (uniform reference 85.0); xor8 102 (uniform reference 85.0); sum8 93 (uniform reference 85.0); p01 68 (uniform reference 85.0); p23 90 (uniform reference 85.0)
Run by the organizer's pipeline on this program with the public seed (the pipeline reruns each experiment and requires identical output), reported without inference:
    bsrho-n18 (organizer run, public seed): 174 of 256 trials returned a pair that the organizer verified; ideal-function control (program's own) 165 of 256; family-law runs at n = 12 (program's own): mean first repeat 76.22; halts target 80, ideal 91.
    proj-k0-w256 (organizer run): 159 of 256 trials returned a verified pair; by source: uniform 60 of 86; counter 43 of 85; iterates 56 of 85; equal pairs in the seven projections (program's own), total over 256 trials: w0 270, w3 251, w7 242, xor8 269, sum8 266, p01 227, p23 271.
Every unsuccessful attempt of the width-18 experiment ended with a halt of the program (the halts equal the unsuccessful trials). At width 18 a halt "recovery found no pair" (a trail start lying on another trail) is frequent; at width 256 it has probability below 2^-100 (Section 4). It happens equally for the ideal function.
Not tested: the full 256-bit functional graph; iterations of length above 2^40; other values of K; the bit-sliced search above width 18. A deviation of g from H1 that raises the collision rate only helps; one that lowers it by eps costs the table of Section 4.

## 6. Experiments

Two organizer experiments run the shipped program `experiments/bsrho.py` (the program dispatches on the experiment id; no outside code or library is used; the standard library only).
`bsrho-n18`: per trial, from the trial seed, one attempt of the 256-lane search at width n = 18 (DP = low 2 bits zero, plan(18): 8 batches, cut rule, table, recovery on the packed circuit) on the target chain g (K = 0: the block 0^32 || x, the low 18 bits of g); the trial returns the two 64-byte messages 0^32 || x, 0^32 || y when the attempt succeeded and two nulls otherwise. The checked event is that the complete 4-round digests agree in the low 18 bits and the messages are distinct. Observations (untrusted): the same attempt on the ideal function, and one family-law run with a fresh key at n = 12.
`proj-k0-w256`: per trial, 2048 points of the K = 0 target at width 256 evaluated with the bit-sliced circuit (source by trial index mod 3), returning two points whose digests agree in the low 21 bits when the set contains such a pair. The digests are recovered from the stored planes by XOR with q before the projections are formed. The checked event is that the digests agree in the low 21 bits and the messages are distinct. Observations (untrusted): equal-pair counts of seven projections.
They check the circuit at full width, the bit-sliced search, lane insertion and extraction, the table, the recovery, the mask q and the message construction on the real target. They do not measure the cost or the success probability at width 256. Running times on the development machine: 2.5 s and 4.1 s.

## 7. Memory

Table: 5,251 entries * 10 bytes = 52,510 bytes (the table region is empty until the search starts). An entry is the key (8 bytes) and the trail number t (2 bytes), kept in two arrays (keys 4 per word, numbers 16 per word); no length is stored (a length is below c + 2^48 < 2^119.4 and is recomputed by pass 1 of the recovery, charged in Section 3.4); `pack_entry` of the program builds and checks it.
Code: 26,502 instructions * 36 bytes (opcode, registers and an inline 256-bit immediate) = 954,072 bytes (loop body 24459, handlers 1,000, recovery 883, setup, cut and slice 160).
Counters and copies: 16,384 bytes (trail numbers 512, birth batches 4,096, counters, and the 8,192-byte copy of the 256 planes used by the handlers). The 800 registers, counted as memory: 25,600 bytes. No advice. Memory peak = max(setup phase 1,042,104, search phase 1,048,566) = 1,048,566 bytes <= 2^20 = 1,048,576; the preprocessing is inside the setup phase. This is the search phase; the setup phase, in which the circuit generator runs, is smaller (1,042,104 bytes, Section 3.6). Claim `memory_log2_bytes` = 20. `python3 bsrho.py --ledger` prints the total.
The table size is the largest that fits: tmax = floor((2^20 - 8 - 954,072 - 25,600 - 16,384) / 10) = 5,251 (8 bytes are left unused on purpose), and Tp = 68 is the largest integer for which the table-capacity bound of Section 4 stays below 2^-40 (Appendix A computes both).

## 8. Heuristics, conventions and what is credited

The premises of this entry are: H1 (the model premise of Section 4, score-critical), H2 (the named approximations of Lemma 2, supporting), H3 (the 800-register machine convention and the 36-byte instruction charge, supporting). There is no prefix, no advice and no polarity climb; the entry has no two-block mode.
Credited to 6ae36351 (jungjipdo): the pivot full adder (Section 3.2) and the mask walk g = f XOR q with the digest planes fed back as stored (Sections 1, 3.2); we wrote both from the text of its proof and did not use or run its files. Credited to our 62cfd777, 0a9640ed, 3356413f and cf8b0e92 and to Jbenisek's e479cbbf: the relation, the trail-and-table search, the handlers, the recovery, the ledger method, the declared register file and the experiments' form.
The recovery circuit has 8 more operations than in 0a9640ed (the XOR with q) and the generator is new (Section 3.6), charged.

## Appendix A. Exact ledger program and its output

The program uses integers and fractions only (the floating-point Chernoff bounds only select M and Tp; the printed rows do not depend on rounding). It prints the exact integer N and the certificate. The same numbers come from `python3 bsrho.py --ledger`.

```python
from fractions import Fraction
from math import isqrt, log, exp, log2

PH, FILT, LOOP, LANES = 24422, 34, 3, 256      # operations of the bit-sliced step (generator), stage-1 test, loop control, lanes
GEN_CALLS = 99448                               # generator primitive calls, both passes (the C port; 2 x 49,724 in python3 bsrho.py --ledger)
PH7, EXTRA, PASSES = 836, 64, 2                            # packed recovery circuit (with the 8 XORs of q), extra operations per recovery batch
N_BITS, S1, W, KAPPA = 256, 32, 90, 11          # width, stage-1 bits, window bits (D = 122), age cap in units of L
LAM, CUT = Fraction(497, 1000), Fraction(15, 100000)
HIT, EVENT, CUTOPS, SLICE, GEN_FACTOR = 2800, 3800, 4200, 1300, 200
SETUP_FIXED, CMAX = 256 * 3100 + 20000, 2
INSTR, OTHER_CODE, REGFILE, COUNTERS, ENTRY, ADVICE, SPARE = 36, 2043, 800 * 32, 16384, 10, 0, 8
TAIL_AGES = 1e-6


def inflight_m(lanes=LANES, eps=TAIL_AGES):    # smallest M with P(sum of `lanes` exponential ages > M L) <= eps (Chernoff, exact in the exponent)
    m = lanes
    while True:
        x = m / lanes
        if exp(-lanes * (x - 1 - log(x))) <= eps:
            return m
        m += 1


M = inflight_m()
body = PH + FILT + LOOP                                        # one batch = one loop body = 24,459 operations
code_bytes = (body + OTHER_CODE) * INSTR
tmax = ((1 << 20) - SPARE - code_bytes - REGFILE - COUNTERS - ADVICE) // ENTRY  # table entries that fit in 2^20 bytes with the code
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


Tp = max(t for t in range(1, 4097)
         if float(plan_tp(t)[1] * LANES / plan_tp(t)[0]) < tmax + 1
         and tail_log2(float(plan_tp(t)[1] * LANES / plan_tp(t)[0]), tmax + 1) <= -40)
L, B, c = plan_tp(Tp)
e2max = 2 * B * LANES // (1 << S1) + 64
capr = c + SB
gen = GEN_FACTOR * (GEN_CALLS + PH)
rows = [("main loop: B * 24459", body * B),
        ("slice checks: ceil(B / 2^48) * 1300", -(-B // SB) * SLICE),
        ("stage-1 hits: e2max * 2800", e2max * HIT),
        ("finished trails: tmax * (3800 + 3 * tmax)", tmax * (EVENT + 3 * tmax)),
        ("cut trails: 2 * 4200", CMAX * CUTOPS),
        ("recovery: 2 * (c + 2^48) * (836 + 64) + 600", PASSES * capr * (PH7 + EXTRA) + 600),
        ("setup and generator", SETUP_FIXED + gen)]
N = int(sum(v for _, v in rows))
assert N == sum(v for _, v in rows)
print("M =", M, " Tp =", Tp, " tmax =", tmax, " B =", B, " e2max =", e2max, " c =", c)
print("memory bytes =", ENTRY * tmax + code_bytes + REGFILE + COUNTERS + ADVICE)
for k, v in rows:
    print(k.ljust(52), int(v))
print("N =", N)
P, C = 100000, 846
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
M = 350  Tp = 68  tmax = 5251  B = 1432349394108965344396540883412795810  e2max = 170749353660221736955230341428  c = 860088703154945564820110450769634726
memory bytes = 1048566
main loop: B * 24459                                 35033833830511183358594993467393572716790
slice checks: ceil(B / 2^48) * 1300                  6615345470854290069395600
stage-1 hits: e2max * 2800                           478098190248620863474644955998400
finished trails: tmax * (3800 + 3 * tmax)            102672803
cut trails: 2 * 4200                                 8400
recovery: 2 * (c + 2^48) * (836 + 64) + 600          1548159665678902016676705466343421688200
setup and generator                                  25587600
N = 36581993974288282239238033262672148067793
certificate: 2^12502374 * 846^100000 <= N^100000 < 2^12502375 * 846^100000
log2(N/C) = 125.0237436566
time_log2 = 125.02375
```
