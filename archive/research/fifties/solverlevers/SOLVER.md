# SOLVER: two solver levers on real passing steps (2026-10-09)

Research only. No yukon, no package touched, nothing written outside this folder. Source: HOTSPOT_STATUS.md 4-5.
Labels: MEASURED (run here), DERIVED (follows from stated numbers), GUESS.

## Verdict
- **(a) H-A as a solver guard: CLOSED.**
  - It saves 0 on the credit as charged, which uses static caps (DERIVED).
  - It saves 0.11% of measured solver units (MEASURED), or 0.26% with the Q* checks added.
- **(b) Y9-score skip at s = 1/4, 1/16, 1/64: CLOSED.** m is 0.70 / 0.37 / 0.15, against break-even 0.82 / 0.77 / 0.76
  (MEASURED m).
- **(b') A mild skip IS WORTH PRICING.**
  - Rank by the J1 count of the searched rows and drop the lowest 40-50% of PC steps.
  - m is 0.965 at s = 0.6. The net is **-0.089 bit** before the cost of computing the score (DERIVED from the
    STATUS break-even).
- **Side find, UNCLEAR:**
  - The credit charges a mean static cap of 16,683 units per PC step. The solver really spends 8,197 (MEASURED).
  - Charging at a run-total budget would be worth about -0.19 bit (DERIVED).
  - Not checked: whether the judge accepts it, and whether it was tried before.

## Data and checks
- **PC steps:** 136,649 real PC steps (pass + pre-check), all from `impl/memberloop/roots/val_ctx.bin` and
  `val_ctrl.bin`.
- **Root steps:** 81,001 real root steps (88,896 roots), all from `roots/prod/ctx.roots` and `ctrl.roots`
  (27.3M contexts/blocks).
- **Solver:** each step was rebuilt with `outer.scalar_outer` and solved by a copy of `solver.traverse` with the
  guards added. MEASURED: counters and root sets are identical to `solver.solve(g7=True, precheck=True)` on
  217,650 of 217,650 steps.
- **Score check:** the J1 count is positive exactly when `solver.j1_exists`, on every step (MEASURED).
- **Run time:** 14 s on 20 CPU processes. The GPU is not needed at this size; it stayed with the other job.

## (a) The G7-style c1 guard
- **How it works (DERIVED).**
  - The path from h to c1 is c1 = Y11 + ROR((ROR(((ROL(h,16) ^ e1) + C2.c1) ^ C2.b1, 7) + Y1 + w12) ^ Y12, 16).
  - After h bits 0..j+7 are decided, c1 bits 16..j are exact, provided the carry into c1[16] is fixed.
  - Q* fixes that carry: c1[16] = 0. Because Y11[15] = 0, Q* c1[15] = 1 also forces the carry to 0, which gives
    a check at node 24.
  - Checks: Q16 at node 24, Q19 (c1[19] = 0) at node 27, and H-A (c1[20] != c1[22]) at node 30.
  - c1[11] and c1[12] wrap through three additions, so they are known at the leaf only. There is no saving there.
- **Exactness (MEASURED, 559,680 leaves).**
  - Each check computed on the partial path agrees with the same check on the full h: 0 mismatches.
  - c1 matches `search.c1_of` everywhere.
  - 34,569 leaves have c1[15,16,19] = (1,0,0) and c1[20] != c1[22]. The guard kills 0 of them.
  - 69 leaves are fully in Q* and satisfy H-A, 15 of them real roots. The guard kills 0 of them.
  - There are 53 Q* roots among the 88,896 roots; 43 were expected.
  - So every root that can reach an E1 outcome is kept, given H-A. H-A's 20/22 half is empirical, from
    11,427 of 11,427 outcomes.
- **Why it cannot lower the static cap (DERIVED).**
  - The free positions are 9, 13, 15 and 30.
  - Position 30 sets c1[23], which nothing constrains. Positions 9 and 13 set c1[2] and c1[6], which are free.
  - Position 15 sets the Q* bit c1[8], but only through three carries that are still unknown at node 15.
  - The checks sit at forced positions (24, 27, 30), so the worst-case tree is unchanged.

| PC steps (136,649) | units | share of measured | share of node+leaf |
|---|---:|---:|---:|
| measured solver units | 1,120,074,388 | 100% | |
| fixed (step, family, row) | 1,107,528,448 | 98.88% | |
| nodes + leaves | 12,545,940 | 1.12% | 100% |
| saved, H-A only | 1,253,392 | 0.112% | 9.99% (leaves 50.4%) |
| saved, Q16 + Q19 | 2,623,988 | 0.234% | 20.9% |
| saved, all three | 2,933,860 | 0.262% | 23.4% (leaves 87.8%) |

- **Root steps.** On root steps alone the saving is larger: all three checks save 48.0% of node+leaf units, and
  H-A alone saves 22.0%. These steps are rare, though.
- **Price (DERIVED).**
  - At the static-cap credit: 0 bit.
  - If the credit were charged at measured units: -0.0009 bit.
  - The STATUS GUESS of -0.05 to -0.07 bit assumed that one free position would become forced. That does not happen.

## (b) Y9-score skip of the solver
- **The score.** It is the exact J1 count, #h with (Y9+h)^(Y9+(h^ETA)) = theta, the same DP as `dp_y9` in
  `newpaths/hotspot/followup.py`. Three versions:
  - hot14: the hotspot ranking, summed over the 14 R = 0 targets;
  - S6: summed over the six solver rows;
  - T: summed over the rows the step searches.
- **The threshold.** It is set on the PC-step distribution; tied steps are split pro rata.
- **What s and m mean.**
  - s is the kept credit share, weighting each step by its static cap C(T).
  - m is the share of root steps kept, with SE about 0.0016. The roots-weighted m differs by less than 0.012.
  - Root steps score 2.5x (hot14) to 3.4x (T) the PC mean.

| score | m at 1/4 | m at 1/16 | m at 1/64 | net bit at 1/4, 1/16, 1/64 |
|---|---:|---:|---:|---|
| hot14 (asked) | 0.699 | 0.366 | 0.147 | +0.23, +1.08, +2.37 |
| S6 | 0.716 | 0.360 | 0.142 | +0.20, +1.11, +2.42 |
| T rows | 0.762 | 0.412 | 0.171 | +0.11, +0.91, +2.15 |

- **Inside the passing set the ranking is much flatter.** The uniform-h1 DP gave m = 0.72 at 1/64; here it is 0.15.
- **The fine grid (`skip_curve.json`) has a minimum near s = 0.5-0.7.**
  - T: -0.081 at 0.5, **-0.089 at 0.6**, -0.080 at 0.7.
  - S6: -0.074 at 0.6. hot14: -0.057 at 0.7.
  - All of these are before the cost of computing the score on every PC step.
- **What pricing (b') still needs.**
  - The cost of the score. GUESS: a 4-state DP over 32 bits per searched row, a few hundred units against a mean
    cap of 16,683. That is roughly +0.005 to +0.02 bit.
  - A success figure m the judge accepts. Here m is measured on 81,001 root steps, not exact.
  - The certificate is assumed independent of Y9 (GUESS; HOTSPOT found no coupling between the sides).
  - The break-even line, re-derived for the 64.87 line. STATUS took it from pkgCA; its use for 64.87 is a GUESS.

## Files
- `levers.py`: the solver copy with the guards, the leaf and root checks, and the scores.
  It writes `levers_full.json`, `scores_pc.txt` and `scores_rootsteps.txt`.
- `skip_mass.py` writes `skip_mass.json`. `skip_curve.py` writes `skip_curve.json`.
- `run_full.sh`, `full.log`, `run_smoke.sh`, `smoke.json`, `smoke.log`.
- `my_pids.txt`: the one job has finished.
