# BLAKE3, 6 rounds: bit-sliced 256-lane search, straight-line step, 5-byte gate instructions (B3R6u5)

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

Our entry for BLAKE3 at six rounds (blake3-r6-prefix-v1), a plain birthday collision search on the complete 256-bit digest, run as cheaply as the cost model allows; it uses no differential and no structure of the rounds. It is our own B3R6d, a5248fe7-07b1-4e54-a3e9-c84b54818d65 (time_log2 125.2309, a rolled round body, first-collision Section 4), with the straight-line step of our B3R6b, 57174971-f105-4b04-8fc5-c337e5917061 (time_log2 125.03893, memory 2^20.64109, scalar score 125.68002), whose code now fits in 2^20 bytes because each register-only gate is charged as a 40-bit instruction word of 5 bytes (an 8-bit opcode and three 10-bit register numbers; proof Section 3.1). The 5-byte gate-instruction convention is credited to 616120b2-f777-44a8-bbd2-44f20c56224a (blake3 round 7, 125.18448): re-implemented from its text; none of its files used or run.
The lineage: 57174971 and the seven-round 1cd0dd3b-eb60-4572-a75f-937cd771ec4a are our round-4 entry a6ee439c-5b82-41f2-8acb-9917c8c70756 (125.06000) taken to six and seven rounds; a6ee439c answers the judges' finding on our earlier 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (125.02375, rejected as not evaluable); they derive from our first round-4 entry 75d5e1f9-8948-4f49-b7a6-5e9475495a7a ({TL1}) and our round-3 entry 62cfd777-5613-463f-b561-e2340e00e528 ({TL3}), which is a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), bit-sliced 256-lane searches with a declared register file, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took the pivot full adder and the mask walk g = f XOR q and re-implemented both in our own generator. We did not use or run any file of that entry. Our program is also derived from cf8b0e92-4302-4813-907a-3c970c102646 and Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.
The target is the plain one: 64-byte messages 0^32 || x, one block, flags 11, standard IV, unkeyed, the complete digest.

## What changed against B3R6d (a5248fe7)

The step is the straight line of 57174971 ({PH} operations a batch) instead of the rolled body (46,214 operations with 576 register moves and 16 loop-control operations), its gates, the stage-1 test and the recovery circuit are charged 5 bytes of code each (all other instructions stay at 36 bytes), so the code is {codebytes} bytes and the memory of the search phase {mem} bytes = 2^{memlog2b:.5f}, not above 2^20; memory_log2_bytes is claimed as 20 and the memory term is 0. The generator of the setup writes the 5-byte records (the program it emits is byte-identical to the Python reference, sha256 equal). Section 4 is that of a5248fe7 (first-collision Lemma 2, P_tiny with its earlier Chernoff constants). The table ({tmax} entries of 10 bytes, the largest that fits in 2^20), Tp ({Tp}), B, c and the age cap ({kappa} L) are re-planned: time_log2 {TL} against 125.2309 ({dTLb:+.5f}).

## What changed against 57174971 (B3R6b)

The same straight-line step with the gates charged 5 bytes instead of 36: the memory term (0.64109 bit in 57174971) is 0, the table is the largest that fits in 2^20 bytes, Section 4 is the first-collision proof. time_log2 {TL} against 125.03893 ({dTL7:+.5f}); scalar score {score:.5f} against 125.68002 ({dSC7:+.5f}).

## Response to the 41b32afc findings

41b32afc, which this lineage descends from, was rejected as not evaluable on the aggregate `lane_cryptanalysis/heuristic/H4-finished-trail-birthday-conditioning`, from the finding F1-adaptive-finished-trail-conditioning. It is answered by proof Section 4 (the bound for the random function by lazy sampling: the first collision of the run and the detection delay, with no conditioning on which trails finish and no random U) and by clause (d) of H1, which declares the remaining modelling step. The other material findings of 41b32afc, by id: F2-full-scale-random-function-extrapolation, F-SUCCESS-EXTRAPOLATION, F-EVAL-1, EXP-F1, EXP-F2 and EXP-F3 concern the extrapolation of H1 to width 256 and what the 18-bit and 21-bit program checks can show; they stand as declared (H1 limitations, no number estimated from a count, no new evidence claimed) and the sensitivity of the score to H1 is priced in proof Section 4. F-COST-REGISTERS (the register-file convention): this entry declares 800 registers, counted as memory, exact for the generated program (771 used); smaller files are priced in proof 3.5. F-COST-TIGHT-MEMORY (the table sized to leave almost no spare under 2^20): the table is the largest that fits in 2^20 bytes ({spare} bytes under 2^20 in the byte account) and the memory is counted in full, search phase and setup phase (proof 3.6, 7).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | {TL} |
| memory_log2_bytes | 20 ({mem} bytes = 2^{memlog2b:.5f}); memory term 0; scalar score {score:.5f} |
| operations per batch of 256 trails | {body} (step {PH}, stage-1 test {filt}, loop 3) |
| total N | {N} operations = 2^{log2N:.6f} units of 1,262 |
| table | {tmax} entries of 10 bytes; setup phase {ph1} bytes |
| success probability | at least 0.39, single attempt, no amplification (the proof bounds {Pl:.5f}, exact certificate {Pcert}: Lemma 2 for the random function, no premise besides H1) |
| preprocessing | none offline; setup and generator 2^{log2setup:.2f} units are in the time bound (claimed {preclaim}) |
| nonuniform advice | none |

The main loop is {pmain:.2f} percent of the total, recovery {prec:.2f} percent.

## Premises, and what was checked

H1 (score-critical, model premise, four clauses): success of the attempt on the fixed target is at least the success P_F of the same procedure against a uniformly random function; clause (d) is the lazy-sampling hazard for the program's adaptive choices. It cannot be tested at width 256 and is declared, not proved: an assumption, no proof is known. Lemma 2 proves P_F >= {Pcert} (exact certificate of Appendix A) for the random function with no premise besides H1. A hazard deficit eps is repaired by extra time: {sens_short}. H3 (supporting, a declared machine convention): the 800-register machine convention, the instruction charges (5 bytes for a register-only gate, 36 bytes for every other instruction) and the charge of the generator's code at 36 bytes per compiled instruction. Nothing else in the success bound is heuristic.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts. The program's own counts (`python3 bsrho.py --stats`, untrusted, descriptive): {stats1}; {stats2}. The experiments run in {t18} s and {t21} s for 256 trials each on the development machine.
Outside the shipped experiments, the program's scalar digest was compared with the organizer's reference `blake3(M, r)` at 3, 4 and 6 rounds ({nchk} random messages each), and at 7 rounds also with the `blake3` library (2,000 messages): no differences. The bit-sliced step was compared with `blake3(M, 6)` on 8,192 messages and on 4,096 lanes chained for 7 steps, the packed recovery circuit on 448 messages: no differences. The selftest compares the step with the scalar compression on 4,096 lanes and on 4,096 lanes chained for 7 steps, and prints 0 shared and 0 unused gates for the generator's network.

## Generator memory

The straight line is generated at setup. Model (proof 3.6): the generator is a freestanding C program of {gencode} compiled instructions ({gencodebytes} bytes at 36 bytes each) with {scratch} bytes of scratch ({nodes} nodes, one byte of use count each), held in the region that the table and the register file occupy once the search runs (setup phase {ph1} bytes, search phase {mem}). Measured: the C program compiled to WebAssembly in a sandbox whose guest memory is capped at 16 pages (1,048,576 bytes) emits the identical program (instruction text equal line by line, same q), and as a static x86-64 binary without libc it does the same under `prlimit --data` at 2^20 bytes; its static arrays total {cpst} bytes including the final code region and the counters. The generator of the entry is that C program; the Python generator is only the reference whose output text it reproduces.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and other keys were not tested; H1 is not proved.
- The 5-byte instruction word is a price stated by this entry for the code (the cost model counts code as memory and fixes no format); a judge who charges 36 bytes per gate gets the memory term of 57174971 back (proof 3.8).
- The 800-register file is this entry's declaration (the generated line needs 771); the profile fixes no register count. Smaller files are priced in proof 3.5 at the same memory budget (512 registers: time_log2 {t512_note}).
- The Python tooling (ledger, selftest, the reference checks, the organizer pipeline) was not run under a cap at the claimed memory: a Python interpreter is not the machine of the model. Only the circuit generator, which defines the circuit, q, the register count and the instruction count, was run under the caps stated above.
- The overlay of the generator's code and scratch on the table region is an assumption of the layout.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line (its measured work in the sandbox is {genfuel} wasm operations against {genops} charged).
- The Section 4 proof was checked by its author only.
