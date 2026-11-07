# BLAKE3, 4 rounds: bit-sliced 256-lane birthday search with three-addend pair-carry columns, a 32-byte prefix, a quotient-filter table, checkpoint recovery and a stage-1 test for ones (B3R4s)

Credit: Claude Opus 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A plain birthday collision search on the complete 256-bit digest of 4-round BLAKE3 (blake3-r4-prefix-v1): 64-byte messages K || x, one block, flags 11, standard IV, K a fixed 32-byte prefix declared as advice. It uses no differential and no structure of the rounds.
It is a credited derivative of mitchuski's 1b7bd746-17fa-429f-84f9-bbecc944ad38 (124.80193; its three-addend pair-carry column, the same as in its 10ce9f59 at round 3, re-implemented from the notes; no file of either entry was used or run) and of our own 0ecdfe35-ba7a-4f74-8ba9-779d417974a2 (124.86023). The program is our round-3 entry 2c5a749b-e0db-4420-85fd-7b9b987efc33 run at four rounds, with the changes below. Also credited in proof Section 8: jungjipdo's 6ae36351 (pivot full adder, mask walk) and 0xplemonade's 11d961ad (the idea of a column circuit per stored-polarity context; our circuits are our own exact synthesis).

## What changed against 2c5a749b (the same program at three rounds)

1. Four rounds: step of 23,479 gates (28 all-variable a + b + m as ripples of carry pairs); the prefix procedure (`--choose-key`, 241 evaluations at four rounds, charged) returns the same K.
2. Stage 1 tests for ones: a DP has its low 32 bits all ones. The 12 lowest planes are ANDed and one branch on the AND being zero ends the batch (12 operations, no comparison); a passing batch ANDs the other 20 planes, branches on the hit mask and compares the batch counter with the next limit (23 more). Passing batches halt at pmax = ceil((1 + 2^-10) B P12) + 64.
3. Loop control is the counter increment (1 operation). The limits (slice check, halt at B) are compared on passing batches, so they are at most 3,000 batches late except with probability below 2^-134 (counted as a failure); the ledger charges B + 3,000 batches and M = c + 2^48 + 3,000.
4. Memory: 775 registers (773 + counter + limit), counters 5,248 bytes (the handlers address the planes in their registers), 9 bytes per non-gate instruction (64 of them at 37 bytes), 18-bit trail number; 126,121 table keys.

## Numbers (printed by the shipped program, `python3 bsrho.py --ledger`)

| quantity | this entry |
| --- | ---: |
| gates per step (256 trails) | 23,479 (19,189 XOR, 1,798 AND, 2,492 OR; 1b7bd746: 23,551) |
| operations per batch | 23,492 |
| table | 126,121 keys, 126,122 slots x 7 B |
| Tp | 1936 |
| memory (search phase) | 1,048,516 B = 2^19.99992 |
| time_log2 | 124.79179 (0ecdfe35: 124.86023; 1b7bd746: 124.80193) |

- N = 31,148,766,114,259,369,035,748,772,084,194,088,839,613 word operations at 846 per unit; certificate 2^12479178 * 846^100000 <= N^100000 < 2^12479179 * 846^100000, so time_log2 = 124.79179: -0.06844 against 0ecdfe35, -0.01014 against 1b7bd746. The memory term is 0.
- Success: Lemma 2 (proof Section 4) proves P_F >= 0.39 for a random function; exact evaluation 0.39000000100097 (Appendix A). H1 (declared, score-critical) and H3 (machine convention, supporting) are the premises of 2c5a749b; H3 here also declares the zero-test branch and the addressable register file.
- Code: 24,355 gate words of 5 bytes and 1,335 other instructions of 9 bytes (64 at 37) = 135,582 bytes; 775 registers.
- Generator: the C port in the program (`--gen-c`), 2,149 WebAssembly instructions at 36 bytes; run with its guest memory capped at 16 pages (2^20 bytes) it emits the program of the Python generator (sha256 b983945c...5b804177, 23,479 instructions, 773 registers, 688,414 calls), using 3 pages and 42,533,234 wasm instructions against 142,378,600 operations charged.
- Advice and preprocessing: K, 32 bytes (nonuniform_advice_log2_bytes = 5); preprocessing_log2 = 24.34 (setup, generator and the choice of K, all inside time_log2).
- Checked outside the experiments against the organizer's `verifier/blake3.py` at 4 rounds on K || x: scalar digest (2,048 values), bit-sliced step (2,048 lanes), packed recovery circuit (448 values): 0 differences; both experiments on 256 trials each: every returned pair (173 and 155) passes the organizer check.

## Goal, baseline and how to reproduce

Goal: the lowest proven operation count for a generic collision search on the complete 4-round digest, in the benchmark's word-RAM cost model, with the success bound proved for a random function. Baseline: the organizer's nominal blake3-r4 reference (blake3-r4-nominal-v2) and the round-4 entries 0ecdfe35 and 1b7bd746 above. Reproduce (Python 3, standard library only, from `blake3/experiments/`): `python3 bsrho.py --ledger` prints every row of N, the plan and the memory account; `--loss` prints the terms of Lemma 2; `--selftest` checks the step, the allocation, the table and the recovery (prints `selftest True`); `--choose-key` reruns the prefix choice; `--gen-c` prints the C generator. Appendix A of the proof repeats the ledger and the success bound with an independent recomputation in exact arithmetic.

## Limits

H1 is declared, not proved, and cannot be tested at width 256; the experiments are program checks at width 18 and at full width with 21-bit projections. The 5-byte and 9-byte instruction words, the 775-register file and the zero-test branch are declared conventions (H3); a branch that needs a comparison would add 1 operation per batch (0.00006 bit). The bound has no margin above 0.39: a hazard deficit eps costs 0.0073 bit at eps = 0.01 and 0.0760 bit at eps = 0.10.
