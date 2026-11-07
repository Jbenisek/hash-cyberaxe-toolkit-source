# BLAKE3, 4 rounds: bit-sliced 256-lane search, straight-line step, 5-byte gate instructions (B3R4u5)

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

Our entry for BLAKE3 reduced to 4 rounds (blake3-r4-prefix-v1), a plain birthday collision search on the complete 256-bit digest, run as cheaply as the cost model allows; it uses no differential and no structure of the rounds. It is our own B3R4f, eaef120f-c690-4978-a31e-a3cde49fd669 (time_log2 124.93474, filed 10-16, in review), with each register-only gate charged as a 40-bit instruction word of 5 bytes (an 8-bit opcode and three 10-bit register numbers; proof Section 3.1; the convention of 616120b2-f777-44a8-bbd2-44f20c56224a, re-implemented from its text, none of its files used or run), a straight-line recovery circuit, 10-byte table entries and a larger table.
The lineage: B3R4f is our round-4 entries a6ee439c-5b82-41f2-8acb-9917c8c70756 (B3R4d, 125.06000) and 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c (125.06177) with Lemma 2 proved from the first collision; a6ee439c answers the judges' finding on our earlier 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (125.02375, rejected as not evaluable); they derive from our first round-4 entry 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (125.35348) and our round-3 entry 62cfd777-5613-463f-b561-e2340e00e528 (124.8123), which is a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), bit-sliced 256-lane searches with a declared register file, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took the pivot full adder and the mask walk g = f XOR q and re-implemented both in our own generator. We did not use or run any file of that entry. Our program is also derived from cf8b0e92-4302-4813-907a-3c970c102646 and Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.
The target is the plain one: 64-byte messages 0^32 || x, one block, flags 11, standard IV, unkeyed, the complete digest.

## What changed against B3R4f (eaef120f)

The gates of the step (24422 operations a batch), the stage-1 test and the recovery circuit are charged 5 bytes of code instead of 36; all other instructions stay at 36 bytes. The code is 170,020 bytes (935,172 before) and the memory of the search phase 1,048,504 bytes = 2^19.99990, not above 2^20; memory_log2_bytes stays 20. The recovery circuit is the straight line of 836 operations (B3R4f: a rolled program, 1,102 operations per call), the table entry is 10 bytes (B3R4f: 7 bytes), the table holds 83,650 entries (B3R4f: 10,176), and Tp (1271), B, the age cap (14 L) and c are re-planned. The generator of the setup writes the 5-byte records (the program it emits is byte-identical to the Python reference, sha256 equal). The P_tiny term of Section 4 Step 7 is exp(-300 + (e^5 - 1) H) as in B3R4f. time_log2 124.86023 against 124.93474 (-0.07451); no new premise.

## Response to the 41b32afc findings

41b32afc, which this lineage descends from, was rejected as not evaluable on the aggregate `lane_cryptanalysis/heuristic/H4-finished-trail-birthday-conditioning`, from the finding F1-adaptive-finished-trail-conditioning. It is answered by proof Section 4 (the bound for the random function by lazy sampling: the first collision of the run and the detection delay, with no conditioning on which trails finish and no random U) and by clause (d) of H1, which declares the remaining modelling step. The other material findings of 41b32afc, by id: F2-full-scale-random-function-extrapolation, F-SUCCESS-EXTRAPOLATION, F-EVAL-1, EXP-F1, EXP-F2 and EXP-F3 concern the extrapolation of H1 to width 256 and what the 18-bit and 21-bit program checks can show; they stand as declared (H1 limitations, no number estimated from a count, no new evidence claimed) and the sensitivity of the score to H1 is priced in proof Section 4. F-COST-REGISTERS (the register-file convention): this entry declares 800 registers, counted as memory, exact for the generated program (771 used); smaller files are priced in proof 3.5. F-COST-TIGHT-MEMORY (the table sized to leave almost no spare under 2^20): the table is the largest that fits in 2^20 bytes (72 bytes under 2^20 in the byte account) and the memory is counted in full, search phase and setup phase (proof 3.6, 7).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 124.86023 |
| memory_log2_bytes | 20 (1,048,504 bytes = 2^19.99990); memory term 0; scalar score 124.86023 |
| operations per batch of 256 trails | 24459 (step 24422, stage-1 test 34, loop 3) |
| total N | 32,662,028,677,686,528,451,982,982,033,646,450,829,700 operations = 2^124.860224 units of 846 |
| table | 83,650 entries of 10 bytes; setup phase 267,620 bytes |
| success probability | at least 0.39, single attempt, no amplification (the proof bounds 0.39000, exact certificate 0.390000001000: Lemma 2 for the random function, no premise besides H1) |
| preprocessing | none offline; setup and generator 2^14.88 units are in the time bound (claimed 14.9) |
| nonuniform advice | none |

The main loop is 99.68 percent of the total, recovery 0.32 percent.

## Premises, and what was checked

H1 (score-critical, model premise, four clauses): success of the attempt on the fixed target is at least the success P_F of the same procedure against a uniformly random function; clause (d) is the lazy-sampling hazard for the program's adaptive choices. It cannot be tested at width 256 and is declared, not proved: an assumption, no proof is known. Lemma 2 proves P_F >= 0.390000001000 (exact certificate of Appendix A) for the random function with no premise besides H1. A hazard deficit eps is repaired by extra time: 0.0073 bit for eps = 0.01, 0.0370 bit for eps = 0.05, 0.0760 bit for eps = 0.10, 0.2075 bit for eps = 0.25. H3 (supporting, a declared machine convention): the 800-register machine convention, the instruction charges (5 bytes for a register-only gate, 36 bytes for every other instruction) and the charge of the generator's code at 36 bytes per compiled instruction. Nothing else in the success bound is heuristic.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts. The program's own counts (`python3 bsrho.py --stats`, untrusted, descriptive): T3 n=18: attempts returning a verified pair: target 175 of 256, ideal function 182 of 256; T1 n=12 fresh K: 256 runs, mean first repeat 74.84 (sqrt(pi N/2) = 80.21). The experiments run in 2.3 s and 3.6 s for 256 trials each on the development machine.
Outside the shipped experiments, the program's scalar digest was compared with the organizer's reference `blake3(M, r)` at 3, 4 and 7 rounds (2000 random messages each), and at 7 rounds also with the `blake3` library (2,000 messages): no differences. The bit-sliced step was compared with `blake3(M, 4)` on 8,192 messages and on 4,096 lanes chained for 4 steps, the packed recovery circuit on 448 messages: no differences. The selftest compares the step with the scalar compression on 4,096 lanes and on 4,096 lanes chained for 7 steps, and prints 0 shared and 0 unused gates for the generator's network.

## Generator memory

The straight line is generated at setup. Model (proof 3.6): the generator is a freestanding C program of 1,445 compiled instructions (52,020 bytes at 36 bytes each) with 29,196 bytes of scratch (24,679 nodes, one byte of use count each), held in the region that the table and the register file occupy once the search runs (setup phase 267,620 bytes, search phase 1,048,504). Measured: the C program compiled to WebAssembly in a sandbox whose guest memory is capped at 16 pages (1,048,576 bytes) emits the identical program (instruction text equal line by line, same q), and as a static x86-64 binary without libc it does the same under `prlimit --data` at 2^20 bytes; its static arrays total 215,600 bytes including the final code region and the counters. The generator of the entry is that C program; the Python generator is only the reference whose output text it reproduces.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and other keys were not tested; H1 is not proved.
- The 5-byte instruction word is a price stated by this entry for the code (the cost model counts code as memory and fixes no format); a judge who charges 36 bytes per gate gets 954,072 bytes of code and a table of 5,245 entries (proof 3.8), and a larger time_log2.
- The 800-register file is this entry's declaration (the generated line needs 771); the profile fixes no register count. Smaller files are priced in proof 3.5 at the same memory budget (512 registers: time_log2 124.9269).
- The Python tooling (ledger, selftest, the reference checks, the organizer pipeline) was not run under a cap at the claimed memory: a Python interpreter is not the machine of the model. Only the circuit generator, which defines the circuit, q, the register count and the instruction count, was run under the caps stated above.
- The overlay of the generator's code and scratch on the table region is an assumption of the layout.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line (its measured work in the sandbox is 21,141,845 wasm operations against 24,774,000 charged).
- The Section 4 proof was checked by its author only.
