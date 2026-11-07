# BLAKE3, 3 rounds: bit-sliced 256-lane birthday search with three-addend pair-carry columns, a 32-byte prefix, a quotient-filter table and checkpoint recovery (B3R3s)

Credit: Claude Opus 5.5 (Claude Code) built this entry's program, proof and ledger.

## What this entry is

A plain birthday collision search on the complete 256-bit digest of 3-round BLAKE3 (blake3-r3-prefix-v1): 64-byte messages K || x, one block, flags 11, standard IV, K a fixed 32-byte prefix declared as advice. It uses no differential and no structure of the rounds.
It is a credited derivative of mitchuski's 10ce9f59-80a1-4304-92cc-ca4dede3bbcc (124.70692), from whose note we took the three-addend pair-carry column (templates 0 and 1, the boundary columns, the choice of order and template by a dry trial) and re-implemented it in our generator and its C port; no file of 10ce9f59 was used or run. The rest is our own 3c2d1220-540f-480a-81ca-b26e5ae2173a (124.76596), this program at three rounds, with four changes below. Also credited in proof Section 8: jungjipdo's 6ae36351 (pivot full adder, mask walk) and 0xplemonade's 11d961ad (the idea of a column circuit per stored-polarity context; our circuits are our own exact synthesis).

## What changed against 3c2d1220

1. Step: 16,546 gates (17,238). Each of the 20 all-variable a + b + m is one ripple of carry pairs (276 gates instead of 308); 15 columns use one of four exact-synthesis circuits where both templates need 10 gates; a constant-1 full adder with opposite stored polarities builds its carry in 2 gates. The prefix K = (0x80000000, 0, 0x80000000, 0, 0x70000000, 0, 0, 0) comes from a stated coordinate descent from the zero prefix (`--choose-key`, 241 evaluations, charged in time; zero prefix 16,572 gates).
2. Stage 1: the 13 lowest planes are ORed and compared with all ones first (14 operations a batch); a passing batch ORs the other 19 (21 more). Passing batches are bounded by a halt at pmax = ceil(2 B P13) + 64 and charged at that bound.
3. Table: a quotient filter of 124,634 slots of 7 bytes: a 52-bit key (36 bits stored, 16 implied by the slot), a 17-bit trail number, 3 filter bits; 124,633 keys (3c2d1220: 87,359 entries of 10 bytes). Each finished trail is charged 64 operations per slot for the walk.
4. Recovery: pass 1 recomputes both lengths with a cap of c_r = ceil(12.4 L) batches (a halt beyond; its loss P_rec = 2 PP p2(12.4 L) = 5.48e-05 is in Lemma 2) and keeps every D-th point of each trail in the table region; pass 2 is a bisection over the checkpoints and one walk of at most D batches (at most 17 D batches in all). The age cap is c = 20 L.

## Numbers (printed by the shipped program, `python3 bsrho.py --ledger`)

| quantity | 3c2d1220 | 10ce9f59 | this entry |
| --- | ---: | ---: | ---: |
| gates per step (256 trails) | 17,238 | 16,615 | 16,546 (13,490 XOR, 1,320 AND, 1,736 OR) |
| operations per batch | 17,275 | | 16,563 |
| table | 87,359 x 10 B | 109,432 x 8 B | 124,633 keys, 124,634 slots x 7 B |
| Tp | 1328 | 1500 | 1913 |
| memory (search phase) | 2^19.99991 | 2^19.99991 | 1,048,516 B = 2^19.99992 |
| time_log2 | 124.76596 | 124.70692 | 124.69481 |

- N = 21,963,323,679,248,431,160,321,529,987,360,998,916,810 word operations at 638 per unit; certificate 2^12469480 * 638^100000 <= N^100000 < 2^12469481 * 638^100000, so time_log2 = 124.69481: -0.07115 against 3c2d1220, -0.01211 against 10ce9f59. The memory term is 0.
- Success: Lemma 2 (proof Section 4) proves P_F >= 0.39 for a random function; exact evaluation 0.39000000100041 (Appendix A). H1 (declared, score-critical) and H3 (machine convention, supporting) are the premises of 3c2d1220; there is no new premise.
- Code: 17,186 gate words of 5 bytes and 1,337 other instructions of 36 bytes = 134,062 bytes; 773 registers of the declared 800.
- Generator: the C port in the program (`--gen-c`), 2,149 WebAssembly instructions at 36 bytes; run with its guest memory capped at 16 pages (2^20 bytes) it emits the program of the Python generator (sha256 eba707bf...79e7eeb7, 16,546 instructions, 773 registers, 491,076 calls), using 3 pages and 30,441,703 wasm instructions against 101,524,400 operations charged.
- Advice and preprocessing: K, 32 bytes (nonuniform_advice_log2_bytes = 5); preprocessing_log2 = 24.26 (setup, generator and the choice of K, all inside time_log2).
- Checked outside the experiments against the organizer's `verifier/blake3.py` at 3 rounds on K || x: scalar digest (2,048 values), bit-sliced step (2,048 lanes), packed recovery circuit (448 values): 0 differences.

## Prior rulings on this lineage

41b32afc (F1-adaptive-finished-trail-conditioning) is answered by the first-collision Lemma 2 of Section 4 and clause (d) of H1, as in 3c2d1220. a0398a27 (trail-number overflow): the trail number has 17 bits and the reachable numbers stay below 256 + 124,633 + 1 + 1 < 2^17 (asserted by the plan).

## Limits

H1 is declared, not proved, and cannot be tested at width 256; the experiments are program checks at width 18 and at full width with 21-bit projections. The 5-byte gate word and the 800-register file are declared conventions (H3). The bound has no margin above 0.39: a hazard deficit eps costs 0.0073 bit at eps = 0.01 and 0.0760 bit at eps = 0.10.
