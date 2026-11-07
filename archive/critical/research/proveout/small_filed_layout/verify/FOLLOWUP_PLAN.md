# Follow-up by the checker: are runs without a collision more frequent than independent trials give?

Written 2026-10-06 by the checking agent, BEFORE any run of it was started (the time stamps of this file and of
`followup_plan.txt` against `logs/v6_log.txt` show the order). It is an addition of the checker, not part of the
builder's test, and it changes nothing in the builder's folder.

Changed once before any run: the first draft (21:39) had 8 runs per set (48 runs, about 90 s of GPU alone). At 21:41
the card was at 95 % with another job's process on it, so the plan was cut to 4 runs per set to stay well inside the
three minutes allowed even when the card is shared. No run had been started; the limits below were recomputed.

## Why

The filed layout takes ONE quadruple of seed words (S11, S4, X13, w0) for a whole run. The one figure of the test that
bears on whether the number of collisions depends on the quadruple is in the builder's second plan, part B: of 12
runs that take every pair (vc, vd) at W = 10 (L = 3.66 to 4.16 each), 2 have no collision, where independent trials
give 0.246 such runs (exact probability of two or more: 0.0241; recomputed in `out/v5_stats.txt`). The builder found
it after the fact and left it unexplained. With the declared reading of PLAN.md (z of the number of runs with a
collision) that figure is 10 against 11.75, sd 0.49, z = -3.57.

## What is run

- Program: the BUILDER's GPU program `~/hashsmash/proveout_small_filed/build/bin/small_fl_w10` (sha256 begins
  bcf17ffb32f1310a; unchanged since 20:52), mode `plan`, with the builder's `sets_w10.txt`. It is started only after
  the checker's independent recount of one whole W = 10 run of the first plan (`out/vrun_w10_run.txt`) has ended and
  agrees with the builder's line; every collision line of the new runs is checked again with the checker's own hash
  and trial (`v6_followup.py`).
- Runs (`followup_plan.txt`): W = 10, the six constant sets with 32-member classes (2, 3, 4, 10, 11, 12), series
  label 2 (the builder used 0, 1 and 9, so no seed is repeated), runs 0..3 of each, NOUTER = 2^20 = every pair
  (vc, vd) for one quadruple of seed words. 24 runs, 2^35 trials each, 2^39.58 trials.
- Predicted by the model (L = sumper / 2^30 per run: 4.15625 for sets 2, 10, 11; 3.65625 for sets 3, 4; 3.7109375
  for set 12): 93.97 collisions (sd 9.69); runs without a collision: 0.492 expected.
- GPU: six program starts of about 8 s each when the card is free (more when shared); nothing is started when the
  time used plus 24 s would pass 170 s (the parts left would then be reported as NOT run). No other job is stopped.

## Fixed in advance

- Every run is reported; none is repeated with other seeds, left out or added afterwards.
- Primary figure: E = the number of the 24 runs without a collision, with the exact probability of E or more under
  independent trials (each run empty with probability exp(-L)). Under that model P(E >= 2) is about 0.09 and
  P(E >= 3) about 0.014 (the script prints the exact values).
  - E <= 1: ordinary. The two empty runs of the builder's part B are then taken as chance.
  - E = 2: said, not explained.
  - E >= 3: reported as an excess of runs without a collision, that is as evidence that the count of a run depends
    on its seed quadruple beyond the model. That would bear directly on the filed layout.
- Secondary: found against 93.97 (z); the extra relative variance c in Var K = L + c L^2 over the 24 runs (its
  standard error under the model is about 0.08): beyond 3 standard errors is reported as OFF.
- The 24 runs pooled with the 12 of part B are also given, marked as biased upward (part B is what raised the
  question).
- Must be zero: `bad`, `bogus`, and any collision line that the checker's hash or trial does not confirm.

## What it cannot show

Only W = 10, six constant sets of one kind, every pair per run (not a share of 2^-13 as in the filed package), the
unfiltered search. A dependence on the seed quadruple that removes fewer than roughly one run in six would pass.
