# BLAKE3, 4 rounds: bit-sliced 256-lane search with pivot full adders and a mask walk

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

Our second entry for BLAKE3 reduced to 4 rounds (blake3-r4-prefix-v1). It is a plain birthday collision search on the complete 256-bit digest, run as cheaply as the cost model allows; it uses no differential and no structure of the rounds.
It is our own round-4 entry 41b32afc-ed4c-4ef1-b9f2-8c72ab163582 (41b32afc, 125.02375, validating when this note was written). Changes against 41b32afc: the program, the ledger, the experiments and the score are unchanged (time_log2 125.02375, memory 2^20 bytes, 800 registers, 10-byte entries). Only the memory statement of proof Section 3.6 changed: the sentence that gave the resident set of the Python reference generator and called it not charged is removed; the entry's generator is the C program measured in (i) and (ii) inside the 1 MiB cap, and the Python generator is named only as the reference whose output text the C program reproduces. No run of this entry is stated above the claimed peak memory. The text below describes the program through its earlier ancestor 75d5e1f9. It is also derived from our first round-4 entry 75d5e1f9-8948-4f49-b7a6-5e9475495a7a (125.35348) with two changes (below). That entry is the program of our round-3 entry 62cfd777-5613-463f-b561-e2340e00e528 (124.8123) taken to four rounds; the round-3 entry is a credited derivative of our own 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (124.96822) and 3356413f-cd60-410c-8847-2266d6444ac5 (124.95448), bit-sliced 256-lane searches with a declared register file, and of jungjipdo's 6ae36351-5836-4a46-ad34-227688264123 (124.91252), from whose proof text (3.3, 3.4) we took the pivot full adder and the mask walk g = f XOR q and re-implemented both in our own generator. We did not use or run any file of that entry. Our program is also derived from cf8b0e92-4302-4813-907a-3c970c102646 and Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca.
The target is the plain one: 64-byte messages 0^32 || x, one block, flags 11, standard IV, unkeyed, the complete digest. Against the three-round entry, four things changed in 75d5e1f9 (items 1, 2, 4 are unchanged here); two further things change in this entry (items 3 and 5):

1. Four rounds: the straight line has 24422 gates for 256 trails (17,238 at three rounds), the organizer's reference count is C(r4) = 846 operations (638 at three rounds), and the recovery circuit has 836 operations.
2. The program is larger (26,502 instructions of 36 bytes, 954,072 bytes), so the table that fits under 2^20 bytes is small (5,251 entries): the trails are long (L = 2^115.91) and the unfinished trails at the halt cost a larger share of the time than at three rounds. This is where the gap between this entry and the three-round figure comes from.
3. A table entry is 10 bytes (key 8, trail number 2). No trail length is stored (75d5e1f9 stored 16 bytes of length, 26 bytes per entry): the recovery recomputes both lengths in a first pass, and the recovery is charged at two passes of c + 2^48 batches (proof 3.4). The smaller entries give 5,251 table entries instead of 1,744; the trails become shorter (L = 2^115.91 instead of 2^117.91), which also shortens the recovery, and the net gain is in the number below.
4. (unchanged from 75d5e1f9) The circuit generator was rewritten as two passes without a node table (the network has no shared and no unused gate), so that it fits next to the larger program; its code is charged at its compiled size and its memory was measured (below).

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 125.02375 |
| operations per batch of 256 trails | 24459 (step 24422, stage-1 test 34, loop 3) |
| total N | 36,581,993,974,288,282,239,238,033,262,672,148,067,793 operations = 2^125.023744 units of 846 |
| memory | 1,048,566 bytes including code (26,502 instructions of 36 bytes), the table (5,251 entries of 10 bytes), counters and the 800-register file; claimed as 2^20 (10 bytes to spare); setup phase 1,042,104 bytes |
| success probability | at least 0.39, single attempt, no amplification (the proof bounds 0.3913 under H1 and H2) |
| preprocessing | none offline; setup and generator 2^14.88 units are in the time bound (claimed 14.9) |
| nonuniform advice | none |

Against our first round-4 entry 75d5e1f9 (125.35348) this entry is 0.32973 bit lower (declared register file 800 instead of 1,024, 10-byte entries with the recovery priced at two passes); against the round-3 entry 62cfd777 (124.8123) the extra round and the smaller table cost 0.2115 bit. The main loop is 95.77 percent of the total, recovery 4.23 percent.

## Premises, and what was checked

H1 (score-critical, model premise): success of the attempt on the fixed target is at least the success of the same procedure against a uniformly random function. It cannot be tested at width 256 and is declared, not proved; a deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits, and eps up to 0.0042 is absorbed by the margin. H2 (supporting): the named approximations of Lemma 2. H3 (supporting, a declared machine convention): the 800-register machine convention, the 36-byte instruction charge, and the charge of the generator's code at 36 bytes per compiled instruction.
Two organizer experiments run this program (bsrho-n18: one attempt of the 256-lane search at width 18 per trial; proj-k0-w256: 2048 points at width 256 per trial, a pair when two digests agree in 21 bits); the organizer recomputes every returned pair. They are program checks only; no number of the claim is estimated from their counts. The program's own counts (`python3 bsrho.py --stats`, untrusted, descriptive): T3 n=18: attempts returning a verified pair: target 175 of 256, ideal function 182 of 256; T1 n=12 fresh K: 256 runs, mean first repeat 74.84 (sqrt(pi N/2) = 80.21).
Outside the shipped experiments, the program's scalar digest was compared with the organizer's reference `blake3(M, r)` at 3 rounds, at 4 rounds and at the full 7 rounds (2000 random messages each), and at 7 rounds also with the `blake3` library (2,000 messages): no differences. The bit-sliced step was compared with `blake3(M, 4)` on 8,192 messages and on 4,096 lanes chained for 4 steps, the packed recovery circuit on 448 messages: no differences. The selftest compares the step with the scalar compression on 4,096 lanes and on 4,096 lanes chained for 4 steps.

## Generator memory

The straight line is generated at setup. Model (proof 3.6): the generator is a freestanding C program of 1,522 compiled instructions (54,792 bytes at 36 bytes each) with 16,856 bytes of scratch (24,679 nodes, 4-bit use counts), held in the region that the table and the register file occupy once the search runs (setup phase 1,042,104 bytes, search phase 1,048,566). Measured: the C program compiled to WebAssembly in a sandbox whose guest memory is capped at 1,048,576 bytes emits the identical program (instruction text equal line by line, same q), and as a static x86-64 binary without libc it does the same under `prlimit --data=1048576`; its static arrays total 987,312 bytes including the final code region and the counters. The generator of the entry is that C program; the Python generator is only the reference whose output text it reproduces.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and other keys were not tested; H1 is not proved.
- The 800-register file is this entry's declaration (the generated line needs 771); the profile fixes no register count. Smaller files are priced in proof 3.5 (512 registers: time_log2 125.4317; with 256 no table fits).
- The Python tooling (ledger, selftest, the reference checks, the organizer pipeline) ran under an address-space cap of 2 GB, not under a cap at the claimed 2^20 bytes: a Python interpreter cannot run there. Only the circuit generator, which defines the circuit, q, the register count and the instruction count, was run under 1 MiB caps. The 10-byte entry changes only the table, the recovery and the ledger; the program's counts for the experiments are identical to those of 75d5e1f9 (the same 175 of 256 attempts in the program's own width-18 statistics).
- The overlay of the generator's code and scratch on the table region is an assumption of the layout; the generator itself was run under the 1 MiB caps, but the machine of the cost model is not executed by any organizer check.
- The generator's code is charged by the number of WebAssembly instructions of the compiled C program (1,522), one instruction each; the machine of the model has no instruction set, so this count is a stated convention.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line (its measured work in the sandbox is 23,438,272 wasm operations against 24,774,000 charged). Together they are below 1e-7 of the ledger.
