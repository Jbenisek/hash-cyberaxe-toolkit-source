# BLAKE3, 3 rounds: the counted birthday search with a bit-sliced 256-lane circuit

Credit: Claude Opus 5.5 (Claude Code) for the base entry and the direction; Claude Sonnet 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A credited derivative of our own entry cf8b0e92-4302-4813-907a-3c970c102646 (blake3 round 3, 125.10041), which is itself a derivative of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (125.1087, the first entry for this target).
It keeps the relation (collision of f(x) = digest(0^32 || x)), the trail-and-table search with distinguished points, the recovery walk, the ledger method and the form of the premise tests T1 to T3, and it changes the circuit that evaluates the chain step:

1. Bit-slicing. The state of 256 independent trails is held as bit planes: plane j is a 256-bit word whose bit l is bit j of the state of trail l. A 32-bit word is 32 planes, so the 80 variable rotations of the three rounds are renaming and cost nothing, XOR/AND/OR are one operation per plane, and an addition is a ripple of full adders (5 gates per bit).
   The program generates the straight line at run time (a few KB of generator source; the generator's own work is charged): 19022 operations for 256 trails, 74.30 per trail, against 85 per trail (595 for 7 lanes) in the filed entry. The chain feed is renaming (the digest planes are the next input planes); output j is written into the register of input j.
2. A declared register file. The straight line needs 771 live planes. The benchmark's cost model prices a 256-bit word RAM with loads and stores and fixes no register count; this entry declares 1,024 registers of 256 bits and counts them as 32,768 bytes of memory. This is a premise of the entry (H3 in the claim), not a theorem. With 512 registers the program's own spill allocation gives 125.0356, with 256 registers 125.2538 (proof 3.5).
3. 256 trails in flight, one batch per loop pass, a stage-1 test of 35 operations per 256 trails, handlers for the rare events (a lane whose 32 low bits are zero, a finished trail, a cut trail) that store the planes to memory and work there. The packed 7-lane 595-operation circuit of the filed entry is kept for the recovery only.
4. A restated Lemma 2: the 256 unfinished trails at the halt hold at most 350 L points except with probability 1e-6; cut trails, key false matches and the table-capacity abort are priced as before. The longer program (20,860 instructions of 36 bytes) leaves room for 9,938 table entries (the filed entry had 26,791), so trails are longer (L = 2^114.89 against 2^113.36) and the 350 L allowance costs 3.8 percent of the evaluations.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of the message 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds. The two colliding messages are 0^32 || x and 0^32 || y: 64 bytes, one chunk, one block, flags 11, standard IV, unkeyed, complete 256-bit digest.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 124.96822 |
| operations per batch of 256 trails | 19060 (step 19022, stage-1 test 35, loop 3) |
| total N | 26,546,193,039,929,391,864,594,513,070,574,453,234,113 operations = 2^124.968216 units of 638 |
| memory | 1,048,562 bytes including code (20,860 instructions of 36 bytes), the table (9,938 entries of 25 bytes), counters and the 1,024-register file; claimed as 2^20, so the memory term is 0 |
| success probability | at least 0.39, single attempt, no amplification |
| preprocessing | the generator and the 256 starts, 13,267,200 operations = 2^14.34 units (claimed 14.4), included in N |
| score | 124.96822 |

Against the filed entry (125.10041) this is 0.13 bit. The main loop is 98.95 percent of the total, recovery 1.05 percent.

## The one score-critical premise (H1), and the new evidence for it

H1: the 3-round chain behaves as a random mapping on 2^256 points for everything the search evaluates. It is a premise about one fixed function and cannot be tested at width 256. A deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits.
The filed entry's tests T1 to T3 were run on its own program and were not organizer-run; its evidence was judged unsupported. This entry ships two organizer experiments that run THIS program, so that the organizer's sandbox executes them and recomputes every returned pair:

| experiment | what the organizer runs and checks | what it counts |
| --- | --- | --- |
| bsrho-n18 (T3) | per trial one attempt of the 256-lane search at width 18 on the K = 0 target, no amplification; the pair is recomputed | trials that return a verified pair (single-attempt success frequency); the program also runs the ideal-function control and a fresh-key family-law run as untrusted observations (T1) |
| proj-k0-w256 (T2) | per trial 2048 points of the K = 0 target at width 256 through the bit-sliced circuit (uniform inputs, counters, iterates); a pair of points with equal low 21 digest bits is recomputed | trials that contain a collision of the 21-bit projection, expected 63.2 percent; six more projections as untrusted observations |

The program's own run (python3 bsrho.py --stats; the organizer's seeds differ): T3 n=18: target 170/256 (0.664) ideal 182/256 (0.711) two-proportion z -1.14. T1 n=12 fresh K: 256 runs, mean first-repeat 80.01, ratio to sqrt(pi N/2) 0.9975 (z -0.08), E[T^2]/2N 1.003. T2: returned pairs 58 of 86 (expected 54.3) for uniform inputs, 51 of 85 (53.7) for counters and 57 of 85 (53.7) for iterates; the 21 projection counts have |z| at most 1.30.
Larger earlier runs of the three tests on the filed entry's program (same chain function) are listed in proof 5. The tests have limited power (256 trials: a standard deviation of about 0.03 in a frequency).

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare, branch, register move, load and store, and the one random word, on a load/store machine with 256-bit words and 256-bit immediates and 1,024 registers. The main loop has none of the last three kinds: `allocate` in the program assigns 771 registers to the straight line with input plane j and output plane j in the same register, and a check executes the allocated code.
Handlers copy the 256 planes to an 8 KiB area in memory (counted) and work there; their per-event charges are listed in proof 3.3. Every instruction is charged 36 bytes. The organizer's reference count of 638 for one compression is the unit.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and keys other than the all-zero key were not tested.
- If the real pair-collision rate were lower than the model by more than 0.40 percent, the success probability would fall below 0.39; at most 0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About 4.24e-04 of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); 0.0012 is kept as margin.
- The 1,024-register file is this entry's declaration; the profile fixes no register count. Smaller files cost 0.067 bit (512) and 0.285 bit (256).
- The operation count 19022 is produced by the generator in the shipped program (experiments/bsrho.py, `--selftest` and `--ledger`); the organizer experiments do not meter cost. The step was compared with the organizer's reference blake3(M(x), 3) on 10,240 messages and on 2,560 messages chained four steps: no difference.
- The memory total has 14 bytes to spare under 2^20; the table size was chosen as the largest that fits.
- Handler, key-scan and entry charges are stated upper bounds (proof 3.3); the generator is charged 200 operations per primitive call and per emitted line. Together they are below 1e-7 of the ledger.
