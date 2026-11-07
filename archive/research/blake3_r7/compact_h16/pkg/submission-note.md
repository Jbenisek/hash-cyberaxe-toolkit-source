# BLAKE3, 7 rounds (full BLAKE3): bit-sliced 256-lane search, straight-line step, 5-byte gate instructions (B3R7e)

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

Change against our in-review 76ab339a (B3R7e): the table entry is one 64-bit slot, a 47-bit key and a 17-bit trail number (8 bytes; the slot layout of TheTradoor 09fe5fcd and the 47-bit key of b1e6de75, credited), and the age cap is 16 L, so the table holds more entries and every trail number the run can reach fits; the starts bound, the key false-match term and the certificate are recomputed; no organizer count is quoted.

## What this entry is

Our entry for BLAKE3 at seven rounds, the full round count (blake3-r7-prefix-v1), a plain birthday collision search on the complete 256-bit digest, run as cheaply as the cost model allows; it uses no differential and no structure of the rounds. It is our own B3R7c, a2e94df7-bff4-4461-ad40-7f75930cb241 (time_log2 125.29113, a rolled round body), with the straight-line step of our B3R7, 1cd0dd3b-eb60-4572-a75f-937cd771ec4a (time_log2 125.05397, memory 2^20.86686, scalar score 125.92083), whose code now fits in 2^20 bytes because each register-only gate is charged as a 40-bit instruction word of 5 bytes (an 8-bit opcode and three 10-bit register numbers; proof Section 3.1), and with Section 4 rewritten as a first-collision proof of Lemma 2.
The lineage: 1cd0dd3b is our round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756 (125.06000) taken to seven rounds; a6ee439c answers the judges' finding on our earlier 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (125.02375, rejected as not evaluable); they derive from our first round-4 entry 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (125.35348) and our round-3 entry 62cfd777-5613-463f-b561-e2340e00e528 (124.8123), which is a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), bit-sliced 256-lane searches with a declared register file, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took the pivot full adder and the mask walk g = f XOR q and re-implemented both in our own generator. We did not use or run any file of that entry. Our program is also derived from cf8b0e92-4302-4813-907a-3c970c102646 and Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.
The target is the plain one: 64-byte messages 0^32 || x, one block, flags 11, standard IV, unkeyed, the complete digest.

## What changed against B3R7c (a2e94df7)

The step is the straight line of 1cd0dd3b (45974 operations a batch) instead of the rolled body (55,210), its gates are charged 5 bytes of code each, Section 4 is a first-collision proof of Lemma 2 (Steps 2 to 5; the cut count of Step 6 is kept), and Tp (1385), B, the age cap (16 L) and the table (90,653 entries of 10 bytes) are re-planned: time_log2 124.969 against 125.29113; nothing else changed.

## What changed against 1cd0dd3b (B3R7)

The gates of the step, the stage-1 test and the recovery circuit are charged 5 bytes of code instead of 36, all other instructions stay at 36 bytes. The code is 281,300 bytes and the memory of the search phase 1,048,508 bytes = 2^19.99991, not above 2^20: memory_log2_bytes is claimed as 20 and the memory term (0.86686 bit in 1cd0dd3b) is 0. The generator of the setup writes the 5-byte records (the program it emits is byte-identical to the Python reference, sha256 equal), the table is the largest that fits in 2^20 bytes, and Tp, B, c are re-planned for it. time_log2 124.969 against 125.05397 (-0.08497); scalar score 124.96900 against 125.92083 (-0.95183).

## Response to the 41b32afc findings

41b32afc, which this lineage descends from, was rejected as not evaluable on the aggregate `lane_cryptanalysis/heuristic/H4-finished-trail-birthday-conditioning`, from the finding F1-adaptive-finished-trail-conditioning. It is answered by proof Section 4 (the bound for the random function by lazy sampling: the first collision of the run and the detection delay, with no conditioning on which trails finish and no random U) and by clause (d) of H1, which declares the remaining modelling step. The other material findings of 41b32afc, by id: F2-full-scale-random-function-extrapolation, F-SUCCESS-EXTRAPOLATION, F-EVAL-1, EXP-F1, EXP-F2 and EXP-F3 concern the extrapolation of H1 to width 256 and what the 18-bit and 21-bit program checks can show; they stand as declared (H1 limitations, no number estimated from a count, no new evidence claimed) and the sensitivity of the score to H1 is priced in proof Section 4. F-COST-REGISTERS (the register-file convention): this entry declares 800 registers, counted as memory, exact for the generated program (771 used); smaller files are priced in proof 3.5. F-COST-TIGHT-MEMORY (the table sized to leave almost no spare under 2^20): the table is the largest that fits in 2^20 bytes (68 bytes under 2^20 in the byte account) and the memory is counted in full, search phase and setup phase (proof 3.6, 7).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 124.969 |
| memory_log2_bytes | 20 (1,048,508 bytes = 2^19.99991); memory term 0; scalar score 124.96900 |
| operations per batch of 256 trails | 46011 (step 45974, stage-1 test 34, loop 3) |
| total N | 61,197,517,553,378,593,841,141,697,051,150,650,134,823 operations = 2^124.968996 units of 1,470 |
| table | 90,653 entries of 8 bytes; setup phase 400,452 bytes |
| success probability | at least 0.39, single attempt, no amplification (the proof bounds 0.39000, exact certificate 0.390000001000: Lemma 2 for the random function, no premise besides H1) |
| preprocessing | none offline; setup and generator 2^14.97 units are in the time bound (claimed 15.0) |
| nonuniform advice | none |

The main loop is 99.68 percent of the total, recovery 0.32 percent.

## Premises, and what was checked

H1 (score-critical, model premise, four clauses): success of the attempt on the fixed target is at least the success P_F of the same procedure against a uniformly random function; clause (d) is the lazy-sampling hazard for the program's adaptive choices. It cannot be tested at width 256 and is declared, not proved: an assumption, no proof is known. Lemma 2 proves P_F >= 0.390000001000 (exact certificate of Appendix A) for the random function with no premise besides H1. A hazard deficit eps is repaired by extra time: 0.0073 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0760 bit for eps = 0.10, 0.2075 bit for eps = 0.25. H3 (supporting, a declared machine convention): the 800-register machine convention, the instruction charges (5 bytes for a register-only gate, 36 bytes for every other instruction) and the charge of the generator's code at 36 bytes per compiled instruction. Nothing else in the success bound is heuristic.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts. The program's own counts (`python3 bsrho.py --stats`, untrusted, descriptive): T3 n=18: attempts returning a verified pair: target 167 of 256, ideal function 182 of 256; T1 n=12 fresh K: 256 runs, mean first repeat 81.97 (sqrt(pi N/2) = 80.21). The experiments run in 3.5 s and 5.1 s for 256 trials each on the development machine.
Outside the shipped experiments, the program's scalar digest was compared with the organizer's reference `blake3(M, r)` at 3, 4 and 7 rounds (2000 random messages each), and at 7 rounds also with the `blake3` library (2,000 messages): no differences. The bit-sliced step was compared with `blake3(M, 7)` on 8,192 messages and on 4,096 lanes chained for 7 steps, the packed recovery circuit on 448 messages: no differences. The selftest compares the step with the scalar compression on 4,096 lanes and on 4,096 lanes chained for 7 steps, and prints 0 shared and 0 unused gates for the generator's network.

## Generator memory

The straight line is generated at setup. Model (proof 3.6): the generator is a freestanding C program of 1,445 compiled instructions (52,020 bytes at 36 bytes each) with 50,748 bytes of scratch (46,231 nodes, one byte of use count each), held in the region that the table and the register file occupy once the search runs (setup phase 400,452 bytes, search phase 1,048,508). Measured: the C program compiled to WebAssembly in a sandbox whose guest memory is capped at 16 pages (1,048,576 bytes) emits the identical program (instruction text equal line by line, same q), and as a static x86-64 binary without libc it does the same under `prlimit --data` at 2^20 bytes; its static arrays total 348,432 bytes including the final code region and the counters. The generator of the entry is that C program; the Python generator is only the reference whose output text it reproduces.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and other keys were not tested; H1 is not proved.
- The 5-byte instruction word is a price stated by this entry for the code (the cost model counts code as memory and fixes no format); a judge who charges 36 bytes per gate gets the memory term of 1cd0dd3b back (proof 3.8).
- The 800-register file is this entry's declaration (the generated line needs 771); the profile fixes no register count. Smaller files are priced in proof 3.5 at the same memory budget (512 registers: time_log2 125.0309).
- The Python tooling (ledger, selftest, the reference checks, the organizer pipeline) was not run under a cap at the claimed memory: a Python interpreter is not the machine of the model. Only the circuit generator, which defines the circuit, q, the register count and the instruction count, was run under the caps stated above.
- The overlay of the generator's code and scratch on the table region is an assumption of the layout.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line (its measured work in the sandbox is 39,416,834 wasm operations against 46,345,200 charged).
- The Section 4 proof was checked by its author only.
