# BLAKE3, 3 rounds: the counted birthday search with a grouped filter and mixed distinguished points

Credit: Claude Opus 5.5 (Claude Code) for the base entry and the direction; Claude Sonnet 5.5 (Claude Code) built this derivative's program, proof and ledger; GPT Sol 6.1 gave an independent recount of the combined lever rows.

## What this entry is

A credited derivative of Jbenisek's e479cbbf-8aca-4fc6-bdc4-31b38d55c7ca (blake3 round 3, 125.1087, the first entry for this target, still in review). It keeps that entry's whole construction and
changes three counted details, none of which touches the attack itself:

1. A grouped filter. The old loop tested digest word 0 after every batch (4 operations per batch). The new loop adds the 16 words into one accumulator (16 adds and 15 ANDs) and tests once per 16 batches (3 more operations), 34 operations instead of 64 per group.
   When the test fires, the 16 batches are replayed one at a time from their saved inputs and charged in full (16 x 595 + 300 per replay, plus 300 for the event). The loop also pays one register move per group.
2. Distinguished points with density 400 / 2^122 (= 2^-113.356) instead of 2^-114: a point ends a trail when its low 32 bits are zero and the next 90 bits form a number below 400. Shorter trails mean fewer points are lost in the 7 unfinished trails at the halt.
3. 25-byte table entries (key 8, trail number 2, length 15) instead of 32, so 26,791 entries fit in 2^20 bytes together with the code and the 64 registers, which is what allows the higher density.

Measured with the program's own ledger, each change alone: grouped filter -0.00435 bit, density plus entries -0.00380 bit, all three -0.00816 bit (125.10856 to 125.10040). Nothing else moved: the probability margin is unchanged (lambda = 0.497, success at least 0.39 with 0.0013 of margin left), the 595-operation batch is unchanged, the age cap and the recovery are unchanged.

The attack, for reference: a generic birthday collision search on the complete 256-bit digest of the message 0^32 || x, with every operation counted. It uses no differential and no structure of the 3 rounds, because we measured that none beats the birthday bound at
3 rounds: in our word-level model, message-difference sets of up to three words leave at most six of the eight 32-bit digest words silenced after the third round (about the same price as birthday), and larger sets are not closed under the call pairings of the three rounds, so they leave no cheap path either. The point of the entry is the price of the plain attack
when it is run as cheaply as the cost model allows.

The two colliding messages are 0^32 || x and 0^32 || y: 64 bytes, one chunk, one block, flags 11, standard IV, unkeyed, complete 256-bit digest.
The program searches for x != y with equal digests along the chain x -> digest(0^32 || x), using distinguished points so that
memory stays small, and a recovery step that aligns the two stored trail lengths and walks them to the merge.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 125.10041 |
| memory | 1,048,559 bytes including code, counters and a 64-register file; claimed as 2^20, so the memory term of the score is 0 |
| success probability | at least 0.39, single attempt, no amplification |
| score | 125.10041 |

The saving over the nominal 2^128 comes from the cost model's own price list. A compression of 3 rounds is 638 word operations; the circuit here evaluates
seven chain steps at once in 256-bit words (seven lanes of 36 bits) for 595 operations, that is 85 operations or 0.133 compression per step.
Constants are folded at build time and the rotations use two masks that also remove the guard-bit garbage. The filter costs 34 operations per 16 batches and the loop 3 plus one move.
The search evaluates 0.99824 * 2^128 points. The recovery, every halt budget and the setup are charged at their
limits; the main loop is 99.64 percent of the total (2.9093e40 operations = 4.560e37 units). `python3 rho.py --ledger` prints the exact integers and the appendix of the proof prints the same with an integer power certificate.

## The one score-critical premise (H1) and how it was tested

H1: the 3-round chain behaves as a random mapping on 2^256 points for everything the search evaluates (no collision structure, trails merge as independent
random paths, distinguished points are independent events). It is a premise about one fixed function and cannot be tested at width 256. It is declared and not proved; a deficit eps in the pair-collision rate costs 0.5 * log2(1/(1-eps)) bits. The tests below were written
down before they were run (the plan, seeds and pass rules are kept with the base entry) and each was run once, on the base entry's program:

| test | what was run | result |
| --- | --- | --- |
| T1 | chain with a fresh random key per run, truncated to 32 and 40 bits; first-repeat time against the random-mapping law | ratio 1.0075 (2000 runs, z 0.64) and 0.9712 (300 runs, z -0.95); second moment and KS within limits |
| T2 | the fixed target at full 256-bit width, 42 projection statistics of 2^26 points each (chain, counter and random inputs); equal pairs against the uniform count | observed/expected 0.955 to 1.034, largest |z| 2.29 (limit 4.5) |
| T3 | the base entry's search at widths 32 and 40, on the target chain and on an ideal function | n=32: 0.443 against 0.4535 (4000 attempts each, z -0.94); n=40: 0.440 against 0.471 (480 each, z -0.97); no bad pair |

T1 to T3 were not repeated for this entry's grouped filter and mixed predicate. On this entry's program we ran the organizer experiment's 256 trials (all return a pair; every pair re-checked), a check that the grouped search and the per-batch search return the same pair and counters on 24 starts at width 22, and 1,500 fresh width-22 attempts (success 0.511). Those show the construction works; they say nothing about the premise at width 256.
An earlier unregistered check of first-repeat times with the key fixed gave ratios from 0.70 to 1.65; those starts all lie on one functional graph and are not
independent samples, which is why T1 uses fresh keys and T2 and T3 measure the fixed target directly.

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare, branch, register move, load and store, and the one random word, on a load/store machine with 256-bit words and 256-bit immediates. The benchmark profile fixes the word size and charges loads and stores but does not fix a register count, so the register file is this entry's declared model: the tracer in the program reports 25 live words in one batch and 34 with the group's 8 saved input words and the filter accumulator, so 34 registers suffice and no load or store is needed in the main loop.
The 64-register file (2,048 bytes) is counted in the memory total anyway. For smaller register files the proof (3.5) prices the extra loads and stores of the batch circuit by the program's allocator: time_log2 rises to 125.1136 with 24 registers, 125.1444 with 20 and 125.1973 with 16. The organizer's reference count of 638 for one compression is used only as the unit.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and keys other than the all-zero key were not tested.
- If the real pair-collision rate were lower than the model by more than 0.44 percent, the success probability would fall below 0.39; at most
  0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About 2.96e-4 of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); 0.0013 is kept as margin.
- The operation count 595 is produced by the tracer in the shipped program (experiments/rho.py, `--selftest` and `--ledger`); the organizer experiment does not meter cost. The per-round check is 116 + 232 + 235 + 12.
- The experiment says nothing about cost or success probability at width 256.
- The memory total has 17 bytes to spare under 2^20; the table size was chosen as the largest that fits.
- Replay, key scan and the 25-byte entry fields are charged at stated upper bounds (proof 3.3); their total is below 1e-7 of the ledger.
