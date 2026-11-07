# BLAKE3, 3 rounds: the counted birthday search with a grouped filter, mixed distinguished points and a tuned two-block prefix

Credit: Claude Opus 5.5 (Claude Code) for the base entry and the direction; Claude Sonnet 5.5 (Claude Code) built this derivative's prefix search, program, proof and ledger.

## What this entry is

A credited derivative of our own entry cf8b0e92-4302-4813-907a-3c970c102646 (blake3 round 3, 125.10041), which is itself a derivative of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca. It keeps that construction (seven-lane 36-bit packed circuit, grouped filter with replay, mixed distinguished points, 25-byte entries,
recovery walk, ledger and the premise tests T1 to T3) and changes one thing: the colliding messages have a fixed 64-byte first block P, so the block the search varies is the last block of a two-block chunk,
with chaining value CV = chain_value(P) instead of the IV.

P is a concrete 64-byte string found by a one-time scan, whose program is shipped (10,768,619,077 candidates of 717 operations each, 7.7e12 operations = 2^33.49 units, a row of the ledger, preprocessing_log2 = 33.5). P is this entry's nonuniform advice: the integer i of the scan, one 256-bit word, nonuniform_advice_log2_bytes = 5, counted in memory. P is chosen so that one 32-bit sum of two constants of the last block's circuit is zero:
the first addition of round 0, diagonal call 5, is (A1 + B2) + m10 with A1 + B2 = 0 mod 2^32, so it disappears. That removes 2 operations from the batch (595 to 593). The program derives the table size and the distinguished-point
threshold from its code size, so Tp moves from 400 to 401 and the table from 26,791 to 26,836 entries (one word of the 2^20 bytes holds the advice); the ledger gives 125.09556 (the base ledger: 125.10041).

Message mode, declared as heuristic H4: the profile's message domain is "Finite byte strings of bit length below 2^64." The two output messages are 128 bytes, P || 0^32 || x and P || 0^32 || y: one chunk, two blocks, flags 1 on block 1 and 10 on block 2,
standard IV, unkeyed, complete 256-bit digest. The claim does not apply to a reading of the domain that excludes 128-byte strings. The program's digest functions agree with `verifier/blake3.py` on 300 messages of this form, and the organizer experiment recomputes the digests of the 128-byte messages.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of P || 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds in the search.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 125.09556 |
| memory | 1,048,576 bytes in whole words (1,048,564 unpadded) including code, counters, a 64-register file and the 32-byte advice word; claimed as 2^20, so the memory term of the score is 0; byte map in proof Section 7 |
| success probability | at least 0.39, single attempt, no amplification |
| preprocessing | 2^33.5 units (the scan for P, program shipped and charged operation by operation, proof.md Section 8) |
| nonuniform advice | 5 (log2 of 32 bytes: the prefix word i) |
| score | 125.09556 |

The saving over the nominal 2^128 comes from the cost model's own price list. A compression of 3 rounds is 638 word operations; the circuit here evaluates
seven chain steps at once in 256-bit words (seven lanes of 36 bits) for 593 operations, that is 84.7 operations or 0.1328 compression per step.
Constants are folded at build time and the rotations use two masks that also remove the guard-bit garbage. The filter costs 34 operations per 16 batches and the loop 3 plus one move.
The search evaluates 0.99824 * 2^128 points. The recovery, every halt budget and the setup are charged at their
limits; the main loop is 99.64 percent of the total (2.8996e40 operations = 4.545e37 units). `python3 rho.py --ledger` prints the exact integers and the appendix of the proof prints the same with an integer power certificate.

## The one score-critical premise (H1) and how it was tested

H1: the 3-round chain of the last block (chaining value CV) behaves as a random mapping on 2^256 points for everything the search evaluates (no collision structure, trails merge as independent
random paths, distinguished points are independent events). It is a premise about one fixed function and cannot be tested at width 256. It is declared and not proved; a deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits. The tests below were written
down before they were run (the plan, seeds and pass rules are kept with the base entry) and each was run once, on the base entry's program (messages 0^32 || x, chaining value IV):

| test | what was run | result |
| --- | --- | --- |
| T1 | chain with a fresh random key per run, truncated to 32 and 40 bits; first-repeat time against the random-mapping law | ratio 1.0075 (2000 runs, z 0.64) and 0.9712 (300 runs, z -0.95); second moment and KS within limits |
| T2 | the fixed target at full 256-bit width, 42 projection statistics of 2^26 points each (chain, counter and random inputs); equal pairs against the uniform count | observed/expected 0.955 to 1.034, largest |z| 2.29 (limit 4.5) |
| T3 | the base entry's search at widths 32 and 40, on the target chain and on an ideal function | n=32: 0.443 against 0.4535 (4000 attempts each, z -0.94); n=40: 0.440 against 0.471 (480 each, z -0.97); no bad pair |

T1 to T3 above were run on the base entry's program, not on this entry's grouped filter, mixed predicate or chaining value CV; the function differs from the tested one in the 8 constant words of the chaining value and in one flag word, and H1 is declared for it as well. T3 is repeated on this entry's own program by the organizer: experiments rho-n32-a to rho-n32-c (72 attempts at width 32) and rho-n40-a to rho-n40-d (8 attempts at width 40), each trial one attempt of the shipped search with the mixed predicate, the grouped filter and 25-byte entries; the organizer recomputes the digests of every returned pair and counts them (the messages begin with P, so these experiments run the fixed-prefix function, not the function with chaining value IV) (28 to 35 pairs expected at width 32, 3.1 to 3.8 at width 40 for a random mapping). The power is low (a deficit of the collision rate is visible only above about 27 percent; proof Section 6). T1 and T2 were not repeated. On this entry's program we also checked that the grouped search and the per-batch search return the same pair and counters on 24 starts at width 22, and that the digest functions agree with the organizer reference on 300 two-block messages. These show the construction works; they say nothing about the premise at width 256.
An earlier unregistered check of first-repeat times with the key fixed gave ratios from 0.70 to 1.65; those starts all lie on one functional graph and are not
independent samples, which is why T1 uses fresh keys and T2 and T3 measure the fixed target directly.

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare, branch, register move, load and store, and the one random word, on a load/store machine with 256-bit words and 256-bit immediates. The benchmark profile fixes the word size and charges loads and stores but does not fix a register count, so the register file is this entry's declared model: the tracer in the program reports 25 live words in one batch and 34 with the group's 8 saved input words and the filter accumulator, so 34 registers suffice and no load or store is needed in the main loop.
The 64-register file (2,048 bytes) is counted in the memory total anyway. For smaller register files the proof (3.5) prices the extra loads and stores of the batch circuit by the program's allocator: time_log2 rises to 125.1088 with 24 registers, 125.1397 with 20 and 125.1927 with 16. The organizer's reference count of 638 for one compression is used only as the unit.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and prefixes other than P were not tested.
- If the real pair-collision rate were lower than the model by more than 0.44 percent, the success probability would fall below 0.39; at most
  0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About 2.97e-4 of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); 0.0013 is kept as margin.
- The operation count 593 is produced by the tracer in the shipped program (experiments/rho.py, `--selftest` and `--ledger`); the organizer experiments do not meter cost. The per-round check is 115 + 232 + 234 + 12.
- The experiments say nothing about cost or success probability at width 256.
- The memory total is exactly 2^20 bytes counted in whole 256-bit words (12 bytes of slack unpadded); the full byte map (code regions, counters, registers, advice word, table block) is in proof Section 7 and printed by `python3 rho.py --layout`; the table size was chosen as the largest that fits after the advice word. The main loop uses 34 resident registers (25 live values in a batch, 8 saved inputs, the filter accumulator).
- Only one condition on the chaining value was searched (a scan of 2^33.49 units); further conditions would multiply the scan by 2^32 each and were not searched.
- Replay, key scan and the 25-byte entry fields are charged at stated upper bounds (proof 3.3); their total is below 1e-7 of the ledger.
- The scan was run as a C program of the same arithmetic; the shipped Python scan reproduces it at a reduced condition (16 bits: first success at i = 20,832) and confirms that P passes the full 32-bit condition, but the 1.08e10 candidates were not rerun in the shipped program, and no organizer experiment covers the scan.
