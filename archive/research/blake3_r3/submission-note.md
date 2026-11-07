# BLAKE3, 3 rounds: a carefully counted birthday search

Credit: Claude Opus 5.5 (Claude Code).

## What this entry is

This is the first entry for BLAKE3 reduced to 3 rounds (blake3-r3-prefix-v1). It is a generic birthday collision search on the complete 256-bit digest,
with every operation counted. It uses no differential and no structure of the 3 rounds, because we measured that none beats the birthday bound at
3 rounds: in our word-level model, message-difference sets of up to three words leave at most six of the eight 32-bit digest words silenced after the third round (about the same price as birthday), and larger sets are not closed under the call pairings of the three rounds, so they leave no cheap path either. The point of the entry is the price of the plain attack
when it is run as cheaply as the cost model allows.

The two colliding messages are 0^32 || x and 0^32 || y: 64 bytes, one chunk, one block, flags 11, standard IV, unkeyed, complete 256-bit digest.
The program searches for x != y with equal digests along the chain x -> digest(0^32 || x), using distinguished points (low 114 bits zero) so that
memory stays small, and a recovery step that aligns the two stored trail lengths and walks them to the merge.

## Numbers

| quantity | value |
| --- | --- |
| time_log2 (target-compressions, upper bound) | 125.1087 |
| memory | 966,272 bytes (2^19.88), claimed as 2^20, so the memory term of the score is 0 |
| success probability | at least 0.39, single attempt, no amplification |
| score | 125.1087 |

The saving over the nominal 2^128 comes from the cost model's own price list. A compression of 3 rounds is 638 word operations; the circuit here evaluates
seven chain steps at once in 256-bit words (seven lanes of 36 bits) for 595 operations, that is 85 operations or 0.133 compression per step.
Constants are folded at build time and the rotations use two masks that also remove the guard-bit garbage. A distinguished-point filter costs 4 operations per
batch and loop control 3 per 16 batches. The search evaluates 0.99885 * 2^128 points. The recovery, every halt budget and the setup are charged at their
limits; the main loop is 99.44 percent of the total (2.9258e40 operations = 4.586e37 units). `python3 rho.py --ledger` prints the exact integers.

## The one score-critical premise (H1) and how it was tested

H1: the 3-round chain behaves as a random mapping on 2^256 points for everything the search evaluates (no collision structure, trails merge as independent
random paths, distinguished points are independent events). It is a premise about one fixed function and cannot be tested at width 256. We wrote the tests
down before running them (the plan, seeds and pass rules are kept with the entry) and ran each once:

| test | what was run | result |
| --- | --- | --- |
| T1 | chain with a fresh random key per run, truncated to 32 and 40 bits; first-repeat time against the random-mapping law | ratio 1.0075 (2000 runs, z 0.64) and 0.9712 (300 runs, z -0.95); second moment and KS within limits |
| T2 | the fixed target at full 256-bit width, 42 projection statistics of 2^26 points each (chain, counter and random inputs); equal pairs against the uniform count | observed/expected 0.955 to 1.034, largest |z| 2.29 (limit 4.5) |
| T3 | the shipped search at widths 32 and 40, on the target chain and on an ideal function | n=32: 0.443 against 0.4535 (4000 attempts each, z -0.94); n=40: 0.440 against 0.471 (480 each, z -0.97); no bad pair |

An earlier unregistered check of first-repeat times with the key fixed gave ratios from 0.70 to 1.65; those starts all lie on one functional graph and are not
independent samples, which is why T1 uses fresh keys and T2 and T3 measure the fixed target directly. The organizer-run experiment returns pairs at width 22
(256 of 256 trials, replay identical); it checks the circuit, the bookkeeping and the recovery on the real target, not the cost at width 256.

## Machine convention (H3)

The ledger counts every add, AND, OR, XOR, shift, compare and branch, and the one random word, on a load/store machine with 256-bit words, 64 registers
and 256-bit immediates. The main loop has no loads or stores because its working set (16 state words, 8 message words, a few temporaries) lives in
registers, and the digest registers of one batch are the input registers of the next copy of the unrolled body, so no register moves are charged. This is
the same convention as the organizer's count of 638 for the reference compression, which also leaves out memory traffic. The cost model does not fix a register
count; with fewer than about 40 registers the main loop would need loads and stores and the cost would rise.

## Limits

- The full 256-bit functional graph, iterations beyond 2^40 and keys other than the all-zero key were not tested.
- If the real pair-collision rate were lower than the model by more than 0.46 percent, the success probability would fall below 0.39; at most
  0.5 * log2(1/(1-eps)) more bits of time restore it (0.0072 for a 1 percent deficit).
- About 1.6e-4 of success probability is spent on the stated losses (unfinished and cut trails, repeats inside one trail, key false matches, programmed aborts); 0.0015 is kept as margin.
- The experiment says nothing about cost or success probability at width 256.
