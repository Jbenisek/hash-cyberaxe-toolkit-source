# BLAKE3, 4 rounds: bit-sliced 256-lane search, first-collision success proof, rolled recovery circuit (B3R4f)

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

Our entry for BLAKE3 reduced to 4 rounds (blake3-r4-prefix-v1), a plain birthday collision search on the complete 256-bit digest, run as cheaply as the cost model allows; it uses no differential and no structure of the rounds. It is our own a6ee439c-5b82-41f2-8acb-9917c8c70756 (B3R4d, time_log2 125.06000) and 9f69f1cc-f6b2-4e86-a668-19b5a2085a2c (B3R4e, 125.06177, the same program with Lemma 2 v2), both in review; the target, the bit-sliced step, the circuit generator, the search, the handlers, the ledger method, the declared 800-register machine and the experiments are theirs. The lineage: 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (125.02375, rejected on one finding about the success-probability step), our round-4 entry 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (125.35348) and our round-3 entry 62cfd777-5613-463f-b561-e2340e00e528 (124.8123), a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), bit-sliced 256-lane searches with a declared register file, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took the pivot full adder and the mask walk g = f XOR q and re-implemented both in our own generator. We did not use or run any file of that entry. Our program is also derived from cf8b0e92-4302-4813-907a-3c970c102646 and Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.
The target is the plain one: 64-byte messages 0^32 || x, one block, flags 11, standard IV, unkeyed, the complete digest.

## What changed against a6ee439c and 9f69f1cc

1. Success proof (proof Section 4). Lemma 2 now follows the first collision of the run: the free run (all evaluations fresh) is a function of the distinguished-point lottery, the first collision is a collision of the random mapping, and the merged path needs a DP in the batches that are left (the detection delay is the main loss, {t_delay:.4f} of the probability); the pairs whose partner is on the trail of t, on a trail with c evaluations without a DP, or whose merged trail is too old are charged by expectation; the cut count of Step 6 is that of 9f69f1cc. The pair-counting supermartingale and the trail-sum Chernoff bound are gone. P_F >= {Pcert} (exact certificate of Appendix A), with the same B-planning rule (least multiple of 10^24); the old bound needed B = 1.4578e36, this one B = {B}.
2. Rolled recovery circuit. The 7-lane packed circuit is a loop of one generic round: {CODE7} instructions and {PH7} operations per call (it was a straight line of 836 instructions and 836 operations). The static code shrinks by {codesaved} bytes; the recovery batch costs {PH7p} operations instead of 900.
3. 7-byte table entries: a 40-bit key and the 2-byte trail number, stored in three arrays in blocks of 32 entries (7 words); key false matches are charged (P_key = {keyfm:.1e}). The table holds {tmax} entries instead of 5,245; Tp {Tp} (was 67), kappa {kappa} (was 13).
time_log2 {TL} against 125.06000 ({dTLd:+.5f}) and 125.06177 ({dTLe:+.5f}); memory 2^20 as before, no new premise.

## Response to the 41b32afc findings

41b32afc, which this lineage descends from, was rejected as not evaluable on the aggregate `lane_cryptanalysis/heuristic/H4-finished-trail-birthday-conditioning`, from the finding F1-adaptive-finished-trail-conditioning (the step from a random lower bound U on the evaluations of finished trails to the fixed-U birthday product was "not justified"; a proof of conservativeness or an explicit premise was required). It is answered as in a6ee439c: proof Section 4 proves the bound for the random function by lazy sampling (here from the first collision of the run, with no conditioning on which trails finish and no random U), and clause (d) of H1 declares the remaining modelling step. The other material findings of 41b32afc, by id: F2-full-scale-random-function-extrapolation, F-SUCCESS-EXTRAPOLATION, F-EVAL-1, EXP-F1, EXP-F2 and EXP-F3 concern the extrapolation of H1 to width 256 and what the 18-bit and 21-bit program checks can show; they stand as declared (H1 limitations, no number estimated from a count, no new evidence claimed) and the sensitivity of the score to H1 is priced in proof Section 4 and the note. F-COST-REGISTERS (the register-file convention): this entry declares 800 registers, counted as memory (the program uses 771); smaller files are priced in proof 3.5. F-COST-TIGHT-MEMORY (the table sized to leave almost no spare under 2^20): the table is the largest that fits in 2^20 bytes ({spare} bytes under 2^20 in the byte account) and the memory is counted in full, search phase and setup phase (proof 3.6, 7).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | {TL} |
| operations per batch of 256 trails | {body} (step {PH}, stage-1 test {filt}, loop 3) |
| total N | {N} operations = 2^{log2N:.6f} units of 846 |
| memory | {mem} bytes including code ({instr} instructions of 36 bytes), the table ({tmax} entries of 7 bytes), counters and the 800-register file; claimed as 2^20 ({spare} bytes to spare); setup phase {ph1} bytes |
| success probability | at least 0.39, single attempt, no amplification (the proof bounds {Pl:.5f}, exact certificate {Pcert}: Lemma 2 for the random function, no premise besides H1 clause (d)) |
| preprocessing | none offline; setup and generator 2^{log2setup:.2f} units are in the time bound (claimed {preclaim}) |
| nonuniform advice | none |

The main loop is {pmain:.2f} percent of the total, recovery {prec:.2f} percent.

## Premises, and what was checked

H1 (score-critical, model premise, four clauses): success of the attempt on the fixed target is at least the success P_F of the same procedure against a uniformly random function; clause (d) is the lazy-sampling hazard for the program's adaptive choices. It cannot be tested at width 256 and is declared, not proved: an assumption, no proof is known. Lemma 2 proves P_F >= {Pcert} for the random function with no premise besides H1. A hazard deficit eps is repaired by extra time: {sens_short}. H3 (supporting, a declared machine convention): the 800-register machine convention, the 36-byte instruction charge, the charges of the rolled recovery circuit (loop control and moves counted), and the charge of the generator's code at 36 bytes per compiled instruction. Nothing else in the success bound is heuristic.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts. The program's own counts (`python3 bsrho.py --stats`, untrusted, descriptive): {stats1}; {stats2}. The experiments run in {t18} s and {t21} s for 256 trials each on the development machine.
Outside the shipped experiments (on a separate machine), the program's scalar digest was compared with the organizer's reference `blake3(M, r)` at 3, 4 and 7 rounds ({nchk} random messages each), and at 7 rounds also with the `blake3` library (2,000 messages): no differences. The bit-sliced step was compared with `blake3(M, 4)` on 8,192 messages and on 4,096 lanes chained for 4 steps, the rolled packed recovery circuit on {nref_packed} messages, and its flat listing (with the loop control) in an interpreter against the compiled blocks: no differences. The selftest compares the step with the scalar compression on 4,096 lanes and on 4,096 lanes chained for 4 steps, and the rolled circuit with the scalar compression.

## Generator memory

The straight line is generated at setup. Model (proof 3.6): the generator is a freestanding C program of {gencode} compiled instructions ({gencodebytes} bytes at 36 bytes each) with {scratch} bytes of scratch ({nodes} nodes, 4-bit use counts), held in the region that the table and the register file occupy once the search runs (setup phase {ph1} bytes, search phase {mem}). Measured: the C program compiled to WebAssembly in a sandbox whose guest memory is capped at 1,048,576 bytes emits the identical program (instruction text equal line by line, same q), and as a static x86-64 binary without libc it does the same under `prlimit --data=1048576`; its static arrays total {cpst} bytes including the final code region and the counters. The generator of the entry is that C program; the Python generator is only the reference whose output text it reproduces.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and other keys were not tested; H1 is not proved.
- The first-collision proof of Section 4 is a new argument for the random function; it is checked by the program's exact certificate of its numbers (Appendix A) and by its author, and was not run against a simulation of the full process at width 256.
- The 800-register file is this entry's declaration (the generated line needs 771); the profile fixes no register count. Smaller files are priced in proof 3.5 (512 registers: time_log2 {t512_note}; with 256 no table fits).
- The rolled recovery circuit is this entry's reading of the cost model: loop control, moves and the 24 constant loads are counted operations and instructions (36 bytes each); the machine of the model has no instruction set, so a judge may price a loop differently.
- The Python tooling (ledger, selftest, the reference checks, the organizer pipeline) was not run under a cap at the claimed memory: a Python interpreter is not the machine of the model. Only the circuit generator, which defines the circuit, q, the register count and the instruction count, was run under 1 MiB caps.
- The overlay of the generator's code and scratch on the table region is an assumption of the layout.
- The generator's code is charged by the number of WebAssembly instructions of the compiled C program ({gencode}), one instruction each. Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line ({genfuel} wasm operations measured against {genops} charged). Together they are below 1e-7 of the ledger.
