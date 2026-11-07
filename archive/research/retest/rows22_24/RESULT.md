# Rows 22-24 retest (r37 exact-event ratio) - cross-check of automaton vs Monte Carlo

VERDICT: WIN as verification of the filed 2.458 (no new gain). KILL for GPT 5.5's reduction as stated, for alternative signings as a gain, and for stacking relaxation 2 on relaxation 3.

## Same quantity?
Both condition on rows <= 21 following chi (same SMC proposal, smc_exact.c) and the same sign convention (n = 0->1, chi W22 = n24 n23 u15, W24 = n29). They differ only in the W22/W24 distribution: automaton = exact uniform plus real F6/F7/W8-variant replay; MC mode 2 = uniform through the schedule. MC mode 1 (W24 independent of W22) is a different quantity, an artifact (x128 from the 7 unpaid W22 conditions); discarded.

## Agreement
- Uniform: exact 1275/512 = 2.49023; MC 2.4925 [2.4883, 2.4967]. Agree.
- Real pipeline: automaton 2.4648 +/- 0.0145 contains the earlier 2.45789. Agree. The 1% uniform-vs-real gap is explained (W24 = s1(W22)+W8+const correlation; W22 ratio 2.339 vs 75/32).
- Shares cross-check: W24 n30u29 5.84% (MC) vs 1/17 = 5.88%; W22 patterns match enum.txt (xor 01808000/02808000/02818000/... = 32/32/8/2/0.5/0.5 of 75). Note: the automaton report's table drops bit 23 from the non-chi patterns; enum.txt and MC show it (e.g. {25,23,16,15}).
- eq36/eq24: 0.0664 (MC) / 0.0657 (real) vs 17/256 = 0.0664.

## Reduction
Corrected form confirmed by both: eq36 <=> eq24 AND dW26 = 0 (forward PROVED by invertibility; reverse COMPUTED, 0 exceptions in 2^31 and 2^34). Rows 25-36 are NOT free: the W26 cancellation costs 17/256. ("W26 or W31" in the MC report: consts.txt proves dW31 = 0 constant; only dW26 varies.)

## Alternative signings
None gives Pr > 0 (sign.txt). Only same-modular-difference XOR variants exist, already inside 1275/2^24, and they change no message word difference (dW22, dW24 are schedule-forced), so support and characteristic are unchanged.

## A filing could claim
Nothing new. It may cite exact q_event = 1275/2^24 = 2^-13.684 vs q_cell = 2^-15 (uniform), and the real-pipeline 2.465 +/- 0.015 as independent confirmation of 2.458.

Open: no exact count under the real F6/F7/variant distribution; dW26 != 0 => no collision is computed only.
