# BLAKE3, 3 rounds: the counted birthday search with a bit-sliced 256-lane circuit and a tuned two-block prefix

Credit: Claude Opus 5.5 (Claude Code) for the base entries and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A credited derivative of our own entry 0a9640ed-558a-4f0a-aba8-45e89ffcfd7c (blake3 round 3, 124.96822, bit-sliced, passed the judges), which is a derivative of our cf8b0e92-4302-4813-907a-3c970c102646 (125.10041) and of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087, the first entry for this target).
It keeps the 0a9640ed program and construction (relation f(x) = digest of the message, trail-and-table search with mixed distinguished points, 25-byte entries, handlers, recovery walk, ledger method, restated Lemma 2, the two organizer experiments) and changes one thing: the colliding messages have a fixed 64-byte first block P, so the block the search varies is the last block of a two-block chunk, with chaining value CV = chain_value(P) instead of the IV and flags 10 instead of 11.
This is the two-block mode and the nonuniform-advice treatment of our entries a72f48eb and fc39027a (the judges' ruling on a72f48eb established the two-block mode and required the prefix to be counted as advice).

1. The circuit. The bit-sliced generator folds constants at build time, so a different chaining value and a different flag word change the number of gates that survive. P is chosen by a one-time scan so that one 32-bit sum of two constants of the last block's circuit is zero (A1 + B2 = 0 mod 2^32, the first addition of diagonal call 5 of round 0). The generated step is 18866 operations for 256 trails (19,022 in 0a9640ed with its shipped polarity vector); the packed recovery circuit is 593 operations (595 in 0a9640ed).
   The loop body is 18904 operations (step, stage-1 test 35, loop 3) against 19,060.
2. The advice. This entry has two nonuniform advice words, 64 bytes, counted in the memory total and declared as nonuniform_advice_log2_bytes = 6: P, the integer i = 10768619076, and the input polarity vector PINS, the output of the polarity climb shipped in the program (`python3 bsrho.py --climb`, 24,959,503,800 operations, a row of the ledger, part of the preprocessing; it replaces the development-time hill climb of the earlier version of this entry). The scan that found i is shipped (`python3 bsrho.py --scan`) and charged operation by operation: 10,768,619,077 candidates of 717 operations = 7,721,099,878,210 operations = 2^33.49 units, a row of the ledger, claimed as preprocessing_log2 = 33.5.
3. The table and the plan. The shorter program leaves room for 10,160 table entries (9,938 in 0a9640ed) and the plan moves to Tp = 142; the 64-byte advice is counted in the memory, and so are the code and the peak scratch of the circuit generator that runs at setup (proof 3.6: 1600 instructions, 222,366 bytes of scratch, held in the region the table later occupies; the setup phase needs 1,041,758 bytes, the search phase 1,048,560).

Message mode, declared as heuristic H4: the profile's message domain is "Finite byte strings of bit length below 2^64." The two output messages are 128 bytes, P || 0^32 || x and P || 0^32 || y: one chunk, two blocks, flags 1 on block 1 and 10 on block 2, standard IV, unkeyed, complete 256-bit digest. The claim does not apply to a reading of the domain that excludes 128-byte strings.
The program's digest functions agree with `verifier/blake3.py` on 300 two-block messages (scalar), 1,024 messages (the bit-sliced step), 64 messages chained for 4 steps and 7 messages (the packed circuit): no difference. Both organizer experiments recompute the digests of the 128-byte messages.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of P || 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 124.95448 |
| operations per batch of 256 trails | 18904 (step 18866, stage-1 test 35, loop 3) |
| total N | 26,294,461,467,906,612,499,224,604,717,289,339,335,772 operations = 2^124.954470 units of 638 |
| memory | 1,048,560 bytes including code (20,704 instructions of 36 bytes), the table (10,160 entries of 25 bytes), counters, the 1,024-register file and the 64 bytes of advice; claimed as 2^20, so the memory term is 0 |
| success probability | at least 0.39, single attempt, no amplification |
| preprocessing | 2^33.5 units (the scan for P and the polarity climb, programs shipped and charged in the ledger); setup and generator 2^14.33 units are in the time bound |
| nonuniform advice | 6 (log2 of 64 bytes: the prefix word i and the polarity vector PINS) |
| score | 124.95448 |

Against 0a9640ed (124.96822) this is 0.01374 bit. The main loop is 98.97 percent of the total, recovery 1.03 percent, the scan 2.9e-28 of it.

## The one score-critical premise (H1) and the evidence for it

H1: the 3-round chain of the last block (chaining value CV) behaves as a random mapping on 2^256 points for everything the search evaluates. It is a premise about one fixed function and cannot be tested at width 256. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits.
This entry ships two organizer experiments that run THIS program, so that the organizer's sandbox executes them and recomputes every returned pair (the messages begin with P, so they run the fixed-prefix function):

| experiment | what the organizer runs and checks | what it counts |
| --- | --- | --- |
| bsrho-n18 (T3) | per trial one attempt of the 256-lane search at width 18 on the target chain, no amplification; the pair is recomputed | trials that return a verified pair (single-attempt success frequency); the program also runs the ideal-function control and a fresh-key family-law run as untrusted observations (T1) |
| proj-k0-w256 (T2) | per trial 2048 points of the target at width 256 through the bit-sliced circuit (uniform inputs, counters, iterates); a pair of points with equal low 21 digest bits is recomputed | trials that contain a collision of the 21-bit projection, expected 63.2 percent; six more projections as untrusted observations |

The program's own run (python3 bsrho.py --stats; the organizer's seeds differ): T3 n=18: target 163/256 (0.637) ideal 182/256 (0.711) two-proportion z -1.79. T1 n=12 fresh K: 256 runs, mean first-repeat 80.05, ratio to sqrt(pi N/2) 0.9979 (z -0.06), E[T^2]/2N 0.997. T2 width 256, K=0: 2048 points, 21-bit projections, expected equal pairs per trial 0.9995, P(>=1) 0.6319; source uniform (86 trials): returned pairs 56 (expected 54.3); w0 77/86.0 z -0.97; w3 90/86.0 z 0.44; w7 85/86.0 z -0.10; xor8 78/86.0 z -0.86; sum8 94/86.0 z 0.87; p01 93/86.0 z 0.76; p23 92/86.0 z 0.65; source counter (85 trials): returned pairs 54 (expected 53.7); w0 83/85.0 z -0.21; w3 77/85.0 z -0.86; w7 72/85.0 z -1.41; xor8 95/85.0 z 1.09; sum8 83/85.0 z -0.21; p01 75/85.0 z -1.08; p23 76/85.0 z -0.97; source iterates (85 trials): returned pairs 60 (expected 53.7); w0 93/85.0 z 0.87; w3 70/85.0 z -1.62; w7 76/85.0 z -0.97; xor8 85/85.0 z 0.00; sum8 85/85.0 z 0.00; p01 90/85.0 z 0.55; p23 74/85.0 z -1.19
Larger earlier runs of the three tests on the filed entry's program (the function with chaining value IV and flags 11) are listed in proof 5; they were not repeated on this function. The tests have limited power (256 trials: a standard deviation of about 0.03 in a frequency).

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare, branch, register move, load and store, and the one random word, on a load/store machine with 256-bit words and 256-bit immediates and 1,024 registers. The main loop has none of the last three kinds: `allocate` in the program assigns 771 registers to the straight line with input plane j and output plane j in the same register, and a check executes the allocated code.
Handlers copy the 256 planes to an 8 KiB area in memory (counted) and work there; their per-event charges are listed in proof 3.3. Every instruction is charged 36 bytes. The organizer's reference count of 638 for one compression is the unit. The 1,024-register file is this entry's declaration (it was accepted for 0a9640ed); smaller files are priced in proof 3.5: 125.0227 with 512 registers, 125.2382 with 256.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40, prefixes other than P and keys other than the all-zero key for m0..m7 were not tested.
- If the real pair-collision rate were lower than the model by more than 0.40 percent, the success probability would fall below 0.39; at most 0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About 4.37e-04 of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); 0.0012 is kept as margin.
- The operation count 18866 is produced by the generator in the shipped program (experiments/bsrho.py, `--selftest` and `--ledger`); the organizer experiments do not meter cost. The polarity vector `PINS` is the output of the shipped polarity climb (`--climb`), a preprocessing row of the ledger and a second advice word.
- The memory total is 1,048,560 bytes (16 bytes to spare under 2^20); the table size was chosen as the largest that fits. The generator's code (1600 instructions, an upper bound by bytecode count, one machine instruction each) and its peak scratch (222,366 bytes, from the program's own node count) are placed in the region that the table and the register file occupy after setup (proof 3.6); that overlay is an assumption of the layout, and if the generator image had to stay resident the table would shrink by 2,304 entries.
- Only one condition on the chaining value was searched (a scan of 2^33.49 units); further conditions would multiply the scan by 2^32 each and were not searched. The full scan was run as a C program of the same arithmetic; the shipped Python scan reproduces it at a reduced condition (16 bits: first success at i = 20,832) and confirms that i passes the full 32-bit condition, but the 1.08e10 candidates were not rerun in the shipped program, and no organizer experiment covers the scan.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line. Together they are below 1e-7 of the ledger.
