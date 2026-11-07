# HOTSPOT_STATUS: the near-miss "hot spot" lead against the current front line (2026-10-09)

Read-only survey. Tags: PROVED, MEASURED, DERIVED (exact arithmetic), GUESS. Sources:
`research\newpaths\hotspot\HOTSPOT.md`, `research\pkg13\stack_gpu2\{run.sh,main_U.txt,analyze2_out.txt}`,
`research\pkg13\direct\DIRECT.md` (item 5), HANDOFF.md lines 1136-1153, `research\frontline\ca\CA.md` section 4,
`research\frontline\pkgF\pkg\blake3-r2\proof.md` (front matter, 9.4 tree table, C(T) ledger),
`research\impl\memberloop\deep\DEEP.md`. `research\pkg13\stack_gpu\` is an empty first attempt (main_U.txt 0 bytes).

## 1. What the hot spot is
Pivot ran a map on 2026-10-08 of where the partial events of the counter arrangement (pkg11/pkg12 lineage) concentrate.
It found three cheap coordinates:
- **H-A (inner, c1 sub-cube):** c1[11] != c1[12] and c1[20] != c1[22]. It keeps 1/4 of the 2^21 cube and contains
  every listed E1 outcome.
- **H-B (outer, Y9):** Y9 = 0 mod 4, Y9[16] != Y9[17], Y9[24] = Y9[25] (the last only in the sub-class). It keeps 1/16
  of outer steps and gives eps* partial E3 x16.
- **H-C (outer, Y12/KY):** Y12[16] != KY[16] and KY[15:12] = 0, where KY = Y1 + w12. It keeps 1/32 of outer steps and
  gives listed E1 outcome x2.
The near-miss part was a side result: R-word near-misses (one word zero, HW(R) <= 23) showed only x1.0-1.8 inside the
hot spots. The closest eps* event was 5 bits off on Delta g2 (2 events). That part found nothing further.

## 2. What was measured
- **PROVED.** No c1 with c1[11] = c1[12] gives eps* for any of the 14 listed taus (dp_proof.py, an exact carry DP).
  Y9 = 0 mod 4 is necessary for Delta f1 to lie in tau ^ ror(tau,1) (exact DP, checked against 2^24 samples per Y9).
  Together these are the "x8 proved part".
- **MEASURED, hotspot run** (sub-class 2^44.81 trials, seed 201, 1,128 s; whole class 2^43.00 trials, seed 202, 329 s;
  the even/odd discovery/held-out split was fixed before looking):
  - H-A held in 11,427 of 11,427 E1 outcomes.
  - Y9[16] != Y9[17] held in 1,126 of 1,126 eps* partial E3 events (307 outer steps).
  - In the H-A + H-B region: E1 x4.20 and eps* x14.7.
  - Coupling between the two sides was about x0.89 pooled, which is not significant.
  - 9,594 records were recomputed by an independent port with 0 mismatches.
- **MEASURED, stack_gpu2 rerun** (2^25 = 33,554,432 filter-passing steps x 2^21 trials, seed 811, 817 s, RTX 3090):

| split | baseline E1 rate | H-A | H-C vs marginal | H-A and H-C | hc1 events |
|---|---|---|---|---|---|
| discovery (10,076 events) | 2^-31.70 | x4.00 (all events inside) | x2.10 +- 0.08 | x8.72 +- 0.35 | 662 |
| held-out (10,096 events) | 2^-31.70 | x4.00 (all events inside) | x2.01 +- 0.08 | x8.32 +- 0.34 | 634 |

  - H-A is x4.00 in both hc strata, so there is no coupling.
  - The hc1 share of passing steps is 2^-5.0: 1,048,078 of 33,554,432 here, and 213 of 6,818 in DIRECT.

## 3. Was it ever priced into a construction?
- Only on the old inner-enumeration ledger: VALUE.md 84.96 -> about 78.0 (DERIVED by its author, never run through
  value_calc.py). That ledger is superseded.
- It was never in a filed or staged package. A case-sensitive grep over `research` finds no H-A, H-C or hot-spot rule
  in pkg12, pkg13, pkgF or pkgCA. The only "E1-side" hits are generic: the MITM verdict, and pkgF's statement that E1-side
  events do not cluster by context.
- HANDOFF ~20:15 2026-10-08 closed it for the solver line:
  - H-A gives no gain for V4, because V4 lists roots.
  - H-C pays only if hc1 steps can be generated directly.

## 4. What blocked it
- **H-A.** Once a solver lists roots per passing step, there is no c1 enumeration left for H-A to cut. H-A can only act
  after the inverse of Lemma IP, and roots occur at about 2.2e-5 per solver step (DEEP.md: 763 roots in about 31e6
  solver steps). The saving there is nil.
  - It was never tried as a pre-traversal guard on the solver's free positions (9, 13, 15, 30), which is how G7 used
    two E1.b1 bits. This is the one untested angle.
- **H-B.** Subsumed. The exact filter (V3, now direct table T1 on Y9) already enforces every Y9 necessary condition.
  - What is left is the Y9 *ranking* inside the support, "not done" in HOTSPOT.md 3. Exact DP on Delta f1 mass
    (MEASURED): the best 1/64 of support carries x46, which is 72% of the mass.
- **H-C.** It cannot be generated. DIRECT found an exact obstruction: KY needs Y1, {Y4, E1.d1, Y1} has no triangular
  basis, and 0 of 3,000 bases move KY without moving Q or E. As a filter it loses (DERIVED, section 5).

## 5. Can it combine with the front line (member loop over contexts, omega-first batch)?
Front-line cost structure (DERIVED from CA.md section 4 rows, pkgCA draft 64.9868). GUESS: the 64.87 line has
similar shares.

| row | share of T | units per passing step |
|---|---|---|
| batches (67/batch) | 49.6% | 9,086 |
| E lanes (78 each) | 23.4% | 4,281 |
| solver credit (G7) | 24.2% | 4,423 (2^12.11) |
| passing lane (512) | 2.8% | 512 |
| contexts, once, SEL | 0.1% | 14 |

- Generation is 73% of the cost: 13,367 units per pass (2^13.71). Every hot spot is a re-allocation of a fixed success
  mass, so none of them touches generation. The only work a hot spot can remove is the work after the filter
  (credit + passing lane).
  - **Hard ceiling for any hot-spot lever: -0.453 bit** (DERIVED: all post-filter work removed with no loss of success).
  - **So this lead cannot reach the low 60s or high 50s.** Those need about -5 to -8 bits, which means cutting
    generation by roughly 2^5 or more.
- **H-C as a filter at the passing lane:** +3.56 bits worse (DERIVED: kept mass 2^-5 x 2.08 = 0.065, against a skip of
  only the solver). It would pay only if downstream cost per pass exceeded about 2^20.6 (DIRECT); the front line's is
  2^12.1. **Dead.**
- **H-C or E1 as context selection:** dead. Contexts cost 0.02%, but pkgF/DEEP measured no context clustering of E1-side
  or residual events (MEASURED), so selecting contexts concentrates no mass. Y12 and Y1 are member lines (CA.md 1).
- **H-A as a solver guard (G7-style):** compatible with the member loop, because it lives inside the credit row only.
  - G7's own effect was CBAR -4.83%, which is **-0.017 bit** (DERIVED).
  - If H-A fixed one more free position on every row, the credit would fall about 15-20% (GUESS), which is
    **-0.05 to -0.07 bit** (DERIVED from the GUESS).
  - Open, GUESS: H-A may be the c1-space image of the same E1 fact as G7, in which case it gives 0.
- **Y9-score skip of the solver (from H-B's ranking):** compatible; it acts on the credit row only.
  - Break-even (DERIVED): kept root mass m must exceed 0.758 + 0.2415 s, where s is the kept share of passes:
    0.818 at s = 1/4, 0.773 at 1/16, 0.762 at 1/64.
  - The best case is -0.40 bit (all roots in a vanishing share).
  - The Delta f1 DP gives 0.72 at s = 1/64 (MEASURED on uniform h1). That is just below break-even, about +0.08 bit
    worse, if it carries to passing steps (GUESS).
  - Whether the ranking is steeper or flatter inside the filter-passing set is unmeasured.

## 6. Cheapest next test (CPU-first, no package change)
**T1. Y9-score skip, about 15-25 min wall** (GUESS: GPU dump seconds, Python DP minutes).
- (a) Rerun `impl\memberloop\deep` deep.cu on about 2,048 contexts, which gives about 2.7e5 solver steps. The earlier
  dump is deleted; the full 120k-context run took 16 s on the GPU (MEASURED).
- (b) Score each step's Y9 with the exact per-Y9 DP from `newpaths\hotspot\followup.py` / `dp_proof.py`.
- (c) Score the Y9 of the 692 root steps (763 roots) kept in `deep\ctx_solve.json` and `ctrl_solve.json`
  (roots_detail.eight -> outer.scalar_outer).
- (d) Read m(s) at s = 1/4, 1/16, 1/64 and compare it with 0.818 / 0.773 / 0.762. The SE on m is about 0.015 at
  n = 763 (DERIVED, binomial).
- Premise to state: roots stand in for successes. 0 of 763 passed Q*. E1 is about independent of Y9 (x1.05, z +1.2,
  MEASURED).
- Value if it passes: at most -0.40 bit, realistically 0-0.2 (GUESS).

**T2. H-A guard, about 30-45 min** (GUESS). Instrument a copy of `impl\solver.py` (g7=True) on the same steps.
- At every leaf, invert to c1 and test whether c1[11]^c1[12] or c1[20]^c1[22] is fixed by a free position (9, 13, 15,
  30) together with the outer words.
- If yes, price the halved leaves with the C(T) ledger (4,096 + 2,304F + 1,280A + 20Nf + 48Nr + 4Ns + 368Lf).
- Value: at most about -0.07 bit (GUESS).

Neither test is a path to the 50s. The ceiling (-0.45 bit, DERIVED) rules this lead out as a big lever. It is a small
polish on the credit row at best.
