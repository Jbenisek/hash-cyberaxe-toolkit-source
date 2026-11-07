# 3-round BLAKE3 differential kill-switch: result (single pass, ~45 min)

Verdict: NOTHING found that beats birthday. No placement has a measurable (>2^-17) probability
at round 1, let alone round 3. Estimates below for best achievable are GUESSES.

## Method (files in this folder)
- b3.py: own numpy BLAKE3 compression; 7-round version reproduces the official empty-input
  hash af1349b9...3262 (blocklen 0, flags 11). Used 3 rounds, blocklen 64, flags 11 for experiments.
- exp1/exp4: all 512 single-bit xor diffs, 512 additive +-2^b diffs, 120 word pairs x 64 bit-pairs
  (bits 0,1,7,8,12,16,24,31) xor. Random messages, per-round activity / HW / digest agreement.
- exp2/exp3: modal exact state-difference frequency per round (conditional on previous round's mode).
- exp6/exp7: backward (inverse round 3) from a collision-shaped digest diff (x,x), then forward test.

## Measured
- Round 0: only words 8..15 keep it inside one G (4 active state words); a MSB flip in an odd-position
  word (9,11,13,15 bit 7 or 31) gives the modal exact round-0 state diff with p = 2^-1 (mean HW ~6);
  other bits 2^-2; even/other words 2^-7/-8; first-half G words often 2^-15 or worse (below resolution).
- Round 1: complete diffusion. All 16 state words active for EVERY tested placement (single and pair).
  Mean state-diff HW = 254 (random = 256); lowest sample HW over ~130k+ samples = 198.
  Modal exact round-1 diff given modal round-0 diff: unique in 2^17 samples, i.e. p < 2^-17 (resolution wall).
- Round 2: HW 255, min 207. Round 3 digest: 0 of 8 words equal in every config, ever
  (min digest HW 92 of 256 over ~260k configs-samples; random expectation ~100, so nothing).
- Digest word agreement: best 0/8 forward in all tests. Best near-collision weight 92 (random level).
- Backward direction (the only structure seen): from digest diff (x,x), x = bit 31 of word i, inverting
  round 3 gives a pre-round state diff of HW ~47 mean, min 31, 14 of 16 words active. Forward from such a
  pre-round-3 diff (HW 32) to full digest collision: 12 of 1,048,576 random states = ~2^-16.4. So round 3 alone,
  entered at a specific diff, costs about 2^-16. Hits come in groups of 4 or 8 equal words (column structure).

## Conditions vs freedom (estimates)
- Round 0: state is constants, so conditions (carry/bit patterns, ~2-4 bits for a 1-bit start) sit directly
  on message words; free, absorbed by message modification.
- Round 1: 4 G calls each with one active input plus a message diff; roughly 4-8 bits per G to stay sparse
  (~20-30 bits), partly absorbable with the 14 spare words (2^20-2^30 work), but sparse is still HW>=~30.
- Round 2: sparse (or not) round-1 output enters 4 diagonal G calls with several active inputs each:
  est. 40-80 bits, NOT absorbable (message words already spent in rounds 0/1, different permutation slots
  only partly free). Then round 2 must land exactly on the 14-active-word, HW~32 pre-round-3 diff, then 2^-16.
- Free message bits 512, but the digest needs 256-bit cancellation unless the trail is exactly that backward form.

## GUESS (not measured)
Best trail probability for a 3-round collision from a 1- or 2-word message diff: roughly 2^-100 to 2^-180
(central guess ~2^-130), before message modification; modification might recover 20-40 bits, so effective cost
~2^-80 to 2^-150. This straddles birthday 2^128 and is NOT demonstrated better. A real answer needs a
weight-minimizing trail search (SAT/MILP on carries) for rounds 1-2 plus the backward round-3 shape above;
the one lead worth that effort is the (x,x) backward form (round 3 ~2^-16) joined to a sparse round-2 diff.
Untested: multi-word (3+) diffs, non-bit-aligned cancelling pairs inside one G across rounds, rotational/modular diffs.

## Addendum: 2^22-sample run, diff = bit 31 of word 13 (exp5.py)
min state-diff HW: round0 4, round1 188, round2 198; min digest diff HW 88; digest words equal: 0 in all 4,194,304 samples.
