# Skeptic check of S8 (sidepaths): two-block message, CV chosen with 2^85 preprocessing

Claim under test (from `..\sidepaths\SIDEPATHS.md` S8 and the workflow): under model M the rate depends only on C3's
outputs and the w5 difference, not on the CV; the realizable deviation is the certified +-8.4 % outer-word effect;
projected exponent 92.41 (= 92.53 - log2 1.08389).
Research only; no yukon, nothing filed, no credential file read; only my own processes.

## Verdict: REFUTED as a projection. S8 is worth exactly 0 bit, not up to 0.12. Corrected: 92.54 (literal, with the 2^85 charged), 92.53 if nothing is spent.

1. The construction moves to a last block unchanged (COMPUTED, `twoblock.py`, `twoblock_out.txt`). With the
   pin written in CV-free coordinates T = X3 + X7 - K, Q = K + W4 (K = cv2 + cv6), X7, X11, X15, W13, 300 pairs over
   12 chaining values (IV with flags 11, plus 11 chained CVs with flags 10) half-collide on digest words 0, 2, 5, 7 under
   the organizer's `verifier/blake3.py` at 2 rounds (119- and 127-byte messages). C3's eight outputs (both messages)
   and the w5 difference (fffffff8) are the same single tuple for every CV.
2. Hence the pin set, the class of Y4 and the model-M count are CV-independent (DERIVED). This also means every
   z3 pin result in `sidepaths` (parity rule, no triples, no double pairs) already covers all CVs: they were run with
   T and Q free.
3. Partial residual events do not move with the CV (COMPUTED, `cvrates.py`, `cvrates_2p24.txt`): 2^24 members per CV,
   IV vs 3 chained CVs, 7 events at 2^-7.3 to 2^-12.1; all 28 z-scores within +-1.64.
4. The +-8.4 % is NOT a CV effect. It needs bits 22, 23 of u = Y12 = (ROL(y,7) XOR b) - c constant over all 2^17
   members of an outer step; that depends only on (b, c) = (ROR(X4 XOR Cc1, 12), Cc1). The CV enters only X4 (through
   S14 <- K2.b1 <- cv6), and X4 is uniform over outer steps for every CV because S9 is free (DERIVED). Measured
   (COMPUTED, `cube_realize.py`, `cube_realize_out.txt`, brute force over all 2^17 members, 40,000 outer steps each):
   IV 0.620 % +- 0.039, chained CV 0.555 % +- 0.037 (difference 1.2 sd; cloud reference 0.590 %). The CV cannot raise
   the realization rate, and whatever gain the cube gives is available in one block with CV = IV.
5. Cost, counted literally (DERIVED): preprocessing is charged time (`hash-smash\docs\TIME_ONLY_REORG.md`: "table
   construction and preprocessing still cost time"). Spending 2^85 units for a CV that buys nothing gives
   log2(2^92.53 + 2^85) = 92.538. There is also no criterion to select on: the effect lives at 2^-100, and an
   unbounded "choose the best CV" step is exactly the judge's earlier fatal finding F-COST-PREPROCESSING-UNBOUNDED
   (END_OF_LINE 3.6).
6. 32-bit lens: the +-8.389 % is exact at 32 bits under model M (cloud REPORT.md section 5.2), so no word-size
   extrapolation is involved; my partial-event tests reach only 2^-12 and cannot see an 8 % effect at 2^-100.
   They support "no CV dependence" only together with the structural argument in 2 and 4.

## Side note for the main session (not S8; GUESS / DERIVED, not tested end to end)

END_OF_LINE 3.5 rates the cube at +0.0495 % (0.0007 bit) = realization rate x gain, i.e. it assumes every outer step is
searched. Outer steps are not scarce (2^192 available, about 2^51.5 needed at 2^49 trials each). Searching ONLY outer
steps where bits 22..26 of u are constant with the pattern matching a pre-fixed w5 (low 24 bits, e.g. 001fec for
u22 = u23 = 1, u24 = v24; acceptance about 0.59 % x 1/8) would take the full +8.385 % (Q5, with the h1 conditions),
about 0.116 bit, for a brute-force filter costing about 2^29 operations per accepted outer step (2^17 members x
about 1,360 candidates) against about 2^49.7 for its trials (2^49 trials x 1.65 operations) (DERIVED). That is the 92.41 figure, but as an S12 / outer-step-selection lever in one block, not S8. Open: whether the
cluster yield (H4), gate rates and rule A hold on selected outer steps; whether the judge accepts a model-M-certified
conditional gain. The "costs supply" objection in the record does not survive the count above (DERIVED).

## Files

`twoblock.py` + `twoblock_out.txt` (construction with any CV/flags, reference check), `cvrates.py` +
`cvrates_2p24.txt` (partial rates per CV), `cube_realize.py` + `cube_realize_out.txt` (cube realization per CV).
Run with PYTHONPATH = `./hash-smash` (read-only import of the organizer reference).
