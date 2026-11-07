# SHA3-256-r6: 3-round affine fields with NON-identity chi1/chi2 transitions (scout, 2026-10-10 ~00:55)

Labels: COMPUTED (run here), DERIVED (arithmetic from computed or cited numbers), GUESS. Our own research; nothing filed.
Target as in linstruct3/isd: one 135-byte block, byte 135 = 0x86, capacity 0, 1,080 free bits, prefix rounds.
Question: with chi transitions allowed to change the difference pattern, is there a 3-round affine field of GF(2) rank >= 3?

## Answer: best rank found = 2 (COMPUTED, certified). No rank >= 3 anywhere we looked. The obstruction is still theta3.

| test | scope | result |
|---|---|---|
| complete, exact (`stage6b.py`) | all 120 six-bit seed words, all 7,140 pairs, all 64 kernel-preserving chi1 transitions per word, chi2 constants free (z3) | 1,552 exact rank-2 variant pairs on **247** word pairs (stopped transitions: 32, isd), max degree 6, **0 triangles** (COMPUTED) |
| sample, exact (`stage2.py` + `exact.py`) | all 1,157 seed words (120 six-bit, 1,037 eight-bit), 273,152 kernel-preserving chi1 variants; variant level for 9,195 of 156,142 word pairs left after the screen (5.9%) | 8,904 relaxed triangles; 8,864 checked exactly: 3,964 need two values for one shared chi1 constant, 4,268 z3 UNSAT, 632 fail on fixed bits; **0 survive** (COMPUTED) |
| certificate, known field | isd words 0+46 through the new pipeline | rank 2, condition rank 266, free outer 812; 2,000 D_aD_b checks at 3 rounds: **0 fails** (COMPUTED) |
| certificate, NEW non-identity field | words 19+1072, non-identity chi1 transitions on both directions, 6 non-identity chi2 bits | rank 2, condition rank 369, free outer 709; 2,000 D_aD_b checks: **0 fails** (COMPUTED) |

Certificates use the organizer reference `hash-smash/verifier/keccak.py` `_permute_lanes` on the full 1,600-bit state, on
base points that solve all conditions. Controls fail as they should: 4 rounds 300/300, unconditioned base 300/300 (both
fields). The message encoding matches `sha3_256(msg135, rounds=3 and 6)`, and byte 135 = 0x86 with zero capacity holds (COMPUTED).
The non-identity field is the first NATIVE 3-round field we have whose chi1 transitions are not the identity. Astra 22 had only
abstract periodic non-stop spaces with no native base. The rebuilt isd pair also uses 6 non-identity chi2 bits, because z3 picks any valid
constants. The new field is no better for the low-degree route: 182 chi3-input bits in its union, against 190 for the isd pair (COMPUTED).

## The obstruction, with numbers
1. **A transition cannot remove a bit's own theta3 spread (the lemma is DERIVED; the numbers are COMPUTED).** For a bit that is alone in its chi row, the output
   always keeps the bit. A transition only adds x-1 and/or x-2 in the same row and slice. So the bit's column stays odd, and its two
   theta3 effect columns (10 bits) stay, unless another active bit shares the slice. Measured over every transition: the chi3-input bits that are active for
   EVERY chi2 choice still number **>= 50** per direction for kernel-preserving chi1 choices (stopped weight 56). For the other chi1
   choices the minimum is **67** and the median 189 (all 4,096 choices for six-bit words, 4,096 sampled of 65,280 for eight-bit words).
   Free transitions remove at most 6 of the 56 persistent bits.
2. **Compatible pairs exist only at fixed z-offsets that never close a triangle (COMPUTED, `offsets.py`).** The 120 six-bit words are
   two translation classes (64 + 56). The exact rank-2 pairs occur only at these offsets: class 0 with class 0 {32}; class 1 with class 1 {+-1, +-26};
   class 0 with class 1 {49, 52}. No two allowed offsets differ by an allowed offset: **0 closed offset triples**. Free transitions raise
   the number of rank-2 pairs 7.7-fold (32 -> 247, DERIVED) without creating a single triangle.
3. **The relaxation is far too optimistic; the exact test kills almost everything (COMPUTED).** Of the 77,796 six-bit variant pairs that pass the
   relaxed test, 1.99% are real. Of 205 relaxed non-identity pairs sampled in `validate.py`, 1 is real. Every relaxed triangle died under
   one common set of chi2 constants.

## What this means for the low-degree route (DERIVED)
The ceiling found is rank 2, so the chi6-input degree stays 8 and the route's cost is unchanged. The target n >= 20 is far away.
With the linearised chi2 helper conditions used here, each direction costs 133 (stopped) to 185 (non-identity) conditions (from the
condition ranks above). n = 20 would need 2,660-3,700 conditions against 1,080 bits. Without helpers the raw count is
about 24 per six-bit direction (12 chi1 + 12 chi2 neighbour bits), so the binding limit is the chi3 compatibility, not the degrees of freedom.
GUESS: with >= 50 persistent chi3 bits per direction, random pairwise compatibility is about exp(-2*50*50/1600) = 4%. Twenty
directions need 190 compatible pairs, so the route through sparse double-kernel seeds is closed.

## Method (scripts in this folder)
- `common.py`: P, an OR-version of theta (union of supports), the per-direction chi relaxation, and the conflict test (adjacent forms fixed, nonzero, different).
- `stage1.py`: for each seed (the 1,157 linstruct3 cycle words = the isd space-C words of weight 6/8), the chi1 output is enumerated over the
  product of the row affine spaces U(delta) (= every compatible output difference = every choice of neighbour constants).
  chi2 is relaxed. K = chi3-input bits active for every chi2 choice; N = bits never active.
  `test_relax.py`: 0 violations in 1,000 real random pairs (organizer permutation). The relaxation is sound because each direction's real
  chi3-input difference is a single-direction trail.
- `stage2.py`: pair screen. Exact chi1 test, exact chi2-input test, K/N chi3 test; word level, then variant level, then triangles.
  For d = 3, the pairwise tests on a basis are equivalent to the full row test (DERIVED: any two different nonzero forms differ on some
  coordinate pair).
- `exact.py`: chi1 constants from the variants must agree where directions share a neighbour. z3 then looks for ONE set of chi2
  row constants (all 5 bits of each active row are free Bools, a superset of the native choices, so UNSAT is sound). Output forms
  follow the exact rule g = f + (c1+1)f2 + c2 f1 + [f1=f2!=0] f2, and the chi3 row test is applied to h = P(g). Native stage: ls3's linear chi1
  conditions, chi2 constants linearised with helpers (extended: helper on a_{k+2} when a_{k+1} is active), forced values honoured,
  patterns recomputed, chi3 re-tested, and every condition row must vanish on every direction.
- `validate.py`: the pipeline accepts known positives (above). `stage6.py` / `stage6b.py`: the six-bit family; 6b caches verdicts by
  simultaneous z-translation (pattern-level checks commute with z-rotation; native checks are run per concrete triple).
- No z3 call timed out (outcomes are only sat/unsat).

## Not done / limits (stated plainly)
- Eight-bit family: the word-level screen is complete, but the variant level covers only 5.9% of the surviving word pairs, and 40 of the 8,904 relaxed
  triangles were not checked (time cap). A complete run with the translation cache would take about 1 hour (GUESS: about 18 translation
  classes, about 2,450 distinct pair classes, about 28 relaxed variant pairs each, 55 ms per z3 pair check).
- Chi1 choices that leave the theta2 kernel were not used in any pair or triangle test. Only their persistent-core statistics were computed (min 67, median 189).
- Directions outside the 1,157 sparse double-kernel seeds were not searched; isd shows the denser kernel words weigh >= 262.
- Chi2 rows with two adjacent active bits of equal form are modelled in z3, but the native builder rejects them. This was never reached:
  no triple was SAT.
- The leader's 32 z-directions: not checked (no rank-3 field to check).
- Compute: 8 sequential single-process runs, each under 10 minutes (stage1 31 s, stage2 424 s, exact 300 s, validate < 10 min,
  stage6 353 s, stage6b 171 s, plus short tests), about 25 minutes in total. No tool call was refused or stopped.

Files: common.py, test_relax.py, stage1.py, stage2.py, exact.py, validate.py, stage6.py, stage6b.py, offsets.py; out_*.txt;
stage1_kp.npz, stage1_stats.json, stage2.json, exact_result.json, validate_result.json, stage6.json, stage6b.json,
rank2_nonidentity_field.json (conditions of the new certified field).
Note: stage1_kp.npz is 160 MB. `python stage1.py` regenerates it in 31 s, so it can be deleted if it bloats backups.
