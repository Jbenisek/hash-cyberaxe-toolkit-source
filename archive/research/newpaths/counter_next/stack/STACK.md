# STACK: which refinements carry over to the counter arrangement, and what each is worth

Folder `research\newpaths\counter_next\stack`. Written 2026-10-08. Research only: no yukon, nothing submitted or posted,
trace untouched, no credential file opened, nothing outside this folder written. pkg11 and every filed package were not
touched (the team's construction solver `verify_ctr.py` and order file were COPIED here; the team's count binary
`~/hashsmash/pkg7_count/bin/pair_calc_sub` was run read-only with its output written here). No GPU. At most two CPU
processes, every run under 3 minutes.
Tags: COMPUTED = run here (file named) or an exact count; DERIVED = follows from a named source or a stated argument;
GUESS = judgement, not checked.

All scores use one formula (stack_calc.py), per WALKED outer step, and reproduce VALUE.md's 84.96:
`T = log2(S * c_step / 430) + 0.02`, `S = 0.5 / (m_step / 2.0)`, `m_step = 2^32 * r * 2^-128` (r = the beta* part of the
Y4 cube, 67,698,688 for the sub-class; one outer step = 2^21 cube trials in VALUE's design), and c_step = word operations
per walked outer step on the filed counting machine (V0: 2^21 x 6.5). Margin 2.0 throughout; the field's 1.4 is -0.515
on every line.

## 0. Answer

1. **New, and larger than every listed refinement: an exact outer-step filter.** In the counter arrangement the E3 call
   sees only ONE moving word. Y4, Y9 and w8 are outer words. So E = Y3 + Y4 + w8 and E' = E + DY3 are fixed per outer step.
   Only h1 moves. COMPUTED: Y9, w8 and Y4 did not move, and h1 did move, over the inner word in 300 of 300 real outer
   steps (real compression).
   - For a beta* outcome, R = 0 forces three exact XOR-difference conditions on E3 (section 1). Two of them depend on
     the inner word through ONE addition each: (1) `(Y9 + h1) ^ (Y9 + (h1 ^ eta)) = G(tau)` and
     (2) `(E + f1) ^ (E' + (f1 ^ ROR(G,12))) = eps`.
   - Whether (1) has ANY solution depends on Y9 alone. Whether (2) has any solution depends on E alone.
   - Exact count over all 2^64 (Y9, E): only **2^-9.813** of outer steps can hold a beta* collision at all.
     Real outer steps of the construction: 1,095 of 1,000,000 pass (2^-9.835 +-3%).
   - Skipping the others loses nothing. It costs about 435 operations per outer step, against 2^23.7 for the 2^21-trial
     enumeration.
   - Own gain **+9.77 bits: 84.96 -> 75.19**, with the enumeration kept as is. Status: pass rate COMPUTED (exact, and
     on real steps); exactness DERIVED (algebra, identities COMPUTED on 200,000 real E3 pairs); cost DERIVED.
2. **Next step on top of it: solve E3 instead of enumerating.** In a passing step, find every h1 that meets (1)-(3)
   directly. Enumerate the f1 solutions of (2), about 2^13.5, then filter by (1) and (3). Map each solution back to c1
   and test E1.
   - The prototype is complete and sound on 300 planted real pairs (0 missed, 0 unsound).
   - On 150 passing steps it costs about 2^18.5 operations per passing step, about 414 per walked step.
   - Own gain **+13.97 bits: 70.99** (DERIVED from measured counts with stated op weights).
   - GUESS refinements: 7 outer steps per packed word gives 70.2. A 2^15 solver gives 68.1.
3. **The listed refinements, each on its own (on V0 = 84.96):**

   | lever | own gain | status |
   |---|---|---|
   | rule A built for beta* from h1 bits only | -0.04 | DERIVED |
   | rule G (condition (1) with Y9 known) as the stage-A test | +0.26 | DERIVED; ops GUESS |
   | Y4 subset chosen for beta* | +0.17 with a rule that keeps all rows; 0 with filed rule A; -1.00 for the whole class with filed rule A (this corrects VALUE.md's +0.083) | COMPUTED |
   | c1-split proofreading stage | 0 (c1 is already forced into the cube) | DERIVED |
   | the same split moved to the listed-tau test | +0.05 | DERIVED |
   | bitslicing | +1.38 (generic) to +2.02 (specialised) | DERIVED; not machine-counted |
   | clusters (variant D) | +2 to +3 | GUESS; brings back exactly H4, H5 and H6 |
   | discount 1.4 | -0.515 on every line | convention, not a gain |

4. **Best candidate variants** (section 4):

   | variant | time_log2 | premise kinds |
   |---|---|---|
   | V0 | 84.96 | H1'-H3' |
   | V0 + bitslicing | 83.5 | H1'-H3' |
   | V0 + clusters | about 82.5 | adds H4-H6 |
   | V3: outer filter, enumeration kept | 75.19 | H1-H3 kinds plus an exact lemma |
   | V3 + bitslicing | 73.3-73.9 | as V3 |
   | V4: filter + E3 solve | 70.99 | H1-H3 kinds |
   | V4p: V4 with packed outer steps | 70.2 | as V4; GUESS |
   | V4s: V4p with a better solver | 68.1 | as V4; GUESS |

5. **Tunnel vision, plainly.** VALUE.md saw the cause and read it as noise. It records that E3 partial events "cluster
   by outer step" and treats that as an averaging issue. Here it is a lever.
   - The counter lever did more than force T1. It moved E3's whole environment into the outer step, so the inner
     enumeration is no longer needed.
   - The per-trial refinements (rule A, the c1 split, bitslicing, clusters) are worth at most about 3 bits. The
     structural change is worth about 14.

## 1. The E3 conditions and the outer filter (e3cond.py, outer_filter.py, real_filter.py)

Per outer step (Sol answer Y section 7; cone4_E1b1_B10.txt; real check above):
- E1 = function of (P = Y12, K = Y1 + w12, J = w5, c1).
- E3 = function of (y = Y4, Q = Y9, W = w8, h1).
- c1 -> h1 is a permutation.

R = 0 with E1 outcome (beta, tau, eps) means four equalities of XOR differences, read from the digest pairing:
- word 1 = E1.a ^ E3.c gives dg2 = tau;
- word 3 = E3.a ^ E1.c gives de2 = eps;
- word 4 = E3.b ^ E1.d gives df2 = ROR(tau, 8);
- word 6 = E1.b ^ E3.d gives Lemma N (n = 0; true for beta* and eps 6e21be55; COMPUTED).

The structure of E3 is fixed:
- dh1 = eta (the class);
- df1 = ROR(dg1, 12);
- df2 = ROR(df1 ^ dg2, 7);
- e2 = E + f1 and e2' = E' + f1', with E' = E + DY3 exactly.

So R = 0 holds exactly when:
- **(1)** dg1 = G(tau) = ROL(tau ^ ROR(tau,1), 12), that is `(Q + h1) ^ (Q + (h1 ^ eta)) = G`;
- **(2)** de2 = eps, that is `(E + f1) ^ (E' + (f1 ^ ROR(G,12))) = eps`, with f1 = ROR(y ^ g1, 12);
- **(3)** dg2 = tau, with dh2 = ROR(eta ^ eps, 8).

Checks (COMPUTED, e3cond_out.txt):
- every identity above on 200,000 real E3 pairs, 0 failures;
- the carry counters against brute force (2,000 cases at 8 bits) and on 600 planted pairs, 0 failures.

The seven G values agree on 27 bits (mask fffff877).

Condition (1) per tau has LM weight 14-15. Its solvability, though, is mostly a condition on Y9: for a fixed Y9 it has
either no solution or about 2^24.5 of them. Condition (2) is the same on E. Exact counts by subset-construction DP over
all 2^32 Y9 and all 2^32 E (outer_filter_bstar.txt):

| | share of outer words with a solution |
|---|---|
| (1), some tau | 2^-4.993 (per tau 2^-6.25 to 2^-8.25) |
| (2), some tau | 2^-4.200 (per tau 2^-4.50 to 2^-6.50) |
| (1) and (2) for the SAME tau: **pass** | **2^-9.8132** (exact, 20,504,986,129,465,344 / 2^64) |

An outer step that fails cannot contain a trial with R = 0 of a beta* outcome. This is a necessary condition, so no
mass is lost and nothing is assumed: the mass per passing step is 2^9.81 times the average.

Real outer steps (real_filter_1M.txt; outer() is a transcription of ctr_gen.inc, cross-checked 300/300 against the team's
solve_order and against the real compression): 1,095 of 1,000,000 pass, 2^-9.835 +-3%. That is z = -0.5 against
the exact model value.

Other outcome sets (all exact):

| outcome set | mass | pass |
|---|---|---|
| top-2 betas | 119.1M | 2^-6.11 |
| top-3 betas | 169.9M | 2^-5.97 |
| top-4 betas | 183.1M | 2^-5.69 |
| the 14 rows of the Y4 cube 07ef8307/070c0307 | 76.16M | 2^-7.53 |

Cost of the check (DERIVED): two position-dependent byte-table automata. They have 61 states for (1) and 74 for (2),
4 lookups each, plus E and an AND of the two 7-bit patterns: about 35 operations. The outer step itself is 81 lines,
about 335 operations plus loads; VALUE.md's "under 400" is used.

## 2. The listed refinements, one by one (own gain on V0 = 84.96; stack_calc_out.txt)

### 2.1 Rule A designed for beta* only

- (a) More h1-bit conditions (DERIVED from a15 columns).
  - All seven beta* rows pass rule A (S8) in full.
  - The next condition (S9: h2 ^ h3 = 1) halves rows 175020a0, 275020a0 and 675020a0. The rate falls to 63,995,904
    (-0.081). It saves half of the stage-2 budget (+0.038). Net **-0.04**.
  - Removing stage 2 entirely is worth at most +0.077. So no h1-only rule can gain more than that.
- (b) **Rule G**: condition (1) with Y9 known, as the stage-A test in place of rule A.
  - It is exact, with no mass lost. Estimated about 36 units per 7-lane word against 41, with a negligible stage-2
    share. Gain **+0.26** (DERIVED; op count GUESS, not machine-counted).
  - It also lets a Y4 cube keep all its rows (2.2).
  - On V0, rule G is a weak form of L5. Its Y9-only part rejects 97% of outer steps after paying for them.
- Needs: a machine count with the filed Machine (copy halfsearch.py). No new premise.

### 2.2 Y4 subset chosen for beta*

Exact counts with the team's binary, beta* alone, 1 s per cube (scan_y4.txt, scan_y4_q01b2.txt, cube_*.out; about
400 cubes). This corrects VALUE.md:
- **Whole class: rate 71,698,432, but rule A keeps only 33,849,344: -1.000** (VALUE.md's +0.083 "rule A not
  recounted").
- The rate is flat in every single free bit of e1 except bit 2, plus one pair interaction:
  - e1 bit 21 = 0 with bit 26 = 1 (or 1 with 0): 75,698,176;
  - adding bit 2 = 1 (cube 07ef8307/070c0307, 65,536 members): **76,161,024 = +0.170**, 14 rows (the extra seven have
    tau x5060a0).
- Greedy descent below that found nothing further.
- Filed rule A keeps 67,698,688 in that cube, so **0** with rule A. With rule G or the E3 solve all 14 rows count:
  **+0.170** (COMPUTED rate).
- Under the outer filter it is a **loss**: its extra rows raise the pass rate from 2^-9.81 to 2^-7.53 for +0.17 of
  mass. V4q = 72.59 against V4's 70.99.
- Needs: nothing new (Y4 is an outer word; one cube or even one member is enough, as 2^224 outer steps remain).

### 2.3 The c1-split proofreading stage

- In the filed design, stage 2 split at the cheap c1 test (105/16,384 of c1 pass; END_OF_LINE item 2, about 0.16).
- In the counter arrangement every trial has c1 in the beta* cube, so the test always passes: **0** (DERIVED).
- The same idea moved to the listed-tau test is worth **+0.05**: 22 units first; the remaining 50 are entered at
  7 x 2^-10.7 per word. DERIVED from VALUE's part table. Capped at +0.077, since stage 2 is 5% of the cost.

### 2.4 Bitslicing

DERIVED op count, not machine-counted. The counter inner loop is a single word walked through a fixed table (RT), with
two subtractions of outer constants and two rotations. That is the ideal shape for 256 trials per 256-bit word: the
rotations become free relabelling.

Per 256 trials:
- 32 RT slice loads;
- two constant subtractions at about 6 operations per bit (generic) or about 2.5 (code specialised per outer step);
- Y6 slices stored and reloaded across the rotation (64);
- rule A on 13 slices, about 15;
- the passing lanes (one per batch on average) gathered for a scalar stage 2, about 0.23 per trial.

Result: about 2.5 per trial generic and 1.6 specialised, against 6.5. Gain **+1.38 / +2.02**.

The filed design's skeptics found only 0.02-0.15 there, because its lanes differed in X2 and in members from scattered
clusters. This design does not have that problem.

Needs: a machine count, and the judge accepting a 256-lane bitsliced machine (the same 1-op-per-256-bit-word
convention as the filed 7-lane machine). On V3 the inner loop is still 97% of the cost, so bitslicing carries over
(V3b/V3c). On V4 it is moot.

### 2.5 The outer-step filter

The filed design's version was S12: prefer rich outer steps, +8.4%, at most about 0.12, never run, with the judge's
F2-unbounded-nonuniform-selection risk.

The counter version (section 1) is **exact and bounded**:
- a fixed-cost test on every walked step;
- no selection by estimated richness;
- zero loss.

Own gain **+9.77 (75.19)**.

Premises:
- the filter lemma: proof, no premise;
- a pass budget over the run (H3 kind): exact 2^-9.813 under M_outer, measured 2^-9.835 on 10^6 real steps;
- H1' unchanged.

### 2.6 Clusters rebuilt on the new inner loop (variant D)

VALUE.md section 7 measures the inputs:
- rule A is carried with probability 0.81-0.95 per flipped free c1 bit (11-14, 20, 21);
- the 4-condition gate is carried with probability 1.000 for bits 11-14 and 28-31.

VALUE GUESSES +2 to +3; taken here as **about +2.5 (GUESS)**.

Its premises are exactly the three that made 64c075ac not_evaluable (aggregate.json reasons):
- **H4 (yield):** over a run, the neighbour trials found to satisfy rule A per representative, divided by 2^-8, are at
  least the measured mean. It is measured, not counted, and varies by outer step.
- **H5 (mass and clumping):** trials examined through an opened gate carry at least the average mass that rule A keeps,
  and good trials do not clump inside a cluster beyond H1'. The joint event at 2^-91 cannot be measured.
- **H6 (budgets):** gate openings, neighbour words through stage A and neighbour words into stage 2 each stay within
  1.2 times their measured means over a run.

On V3 clusters could still sit in the inner loop of passing steps (GUESS: about 2 to 3 more, about 73). On V4 there is
no inner loop, so the gain is 0.

### 2.7 Discount 1.4 against 2.0

-0.515 on every line (log2(2/1.4)). This is a convention, not a gain: the count is the same, and only the claimed share
of it changes. Disclose it if it is used.

## 3. The E3-first solve (e3solve.py, e3solve2.py)

How the prototype works, in a passing step and for each viable tau (1.23 per passing step):
1. Enumerate all f1 with (2), using a carry DFS pruned by an exact backward table.
2. Map each to g1 = ROL(f1,12) ^ y, then h1 = g1 - Y9.
3. Test (1), then run E3 on both messages to test (3).
4. Each survivor gives c1 by the inverse inner map (Sol Y 7.1). Test beta* and the E1 outcome.

The E3 solutions are rare: 2^-24.3 per walked step.

Results (COMPUTED):

| check | result |
|---|---|
| completeness and soundness, 300 planted real pairs (target = the pair's own differences) | 0 missed, 0 unsound |
| f1 solutions of (2) per passing step, 150 steps | 11,274 (median 8,192, max 61,440) |
| survivors of (1) per passing step | 87 |
| DFS nodes per passing step | 38,700 |

Op weights (DERIVED): 6 per node, 12 per f1, 40 per survivor, 1,024 per viable tau. That gives 2^18.51 per passing
step, or 414 per walked step.

A joint DFS on (1) and (2) together returned the same solution sets (0 mismatches on 120 steps), but with MORE nodes
(61,772). A better solver remains a GUESS: one that starts at g1 bit 12, or a meet in the middle.

Mass is the same as the cube enumeration: per walked step, 2^32 x 67,698,688 x 2^-128 over all 2^32 inner values (Sol
Y 7.2's bijection holds for every fixed c1). The beta* part needs no cube and no rule A.

## 4. Candidate variants (stack_calc_out.txt; each with its own score and premises)

| variant | what | time_log2 (2.0) | at 1.4 | premises | status |
|---|---|---|---|---|---|
| V0 | VALUE.md as valued | 84.96 | 84.45 | H1', H2', H3' | COMPUTED (team) |
| V0g | rule G + Y4 cube 07ef8307 (14 rows), enumeration | 84.53 | 84.02 | H1'-H3' | DERIVED, ops GUESS |
| V0b | bitsliced (generic) + tau split | 83.53 | 83.01 | H1'-H3'; machine model | DERIVED |
| V0c | clusters (variant D) | about 82.5 | about 81.9 | H1'-H3' + H4, H5, H6 | GUESS |
| **V3** | **exact outer filter + enumeration (rule A, sub-class)** | **75.19** | 74.67 | H1'; filter lemma (proof); pass budget (H3 kind); stage-2 budget (H3') and E1-test budget (H2') inside passing steps | P COMPUTED, cost DERIVED |
| V3b / V3c | V3 + bitsliced inner loop, generic / specialised | 73.87 / 73.28 | 73.36 / 72.77 | as V3; machine model | DERIVED |
| **V4** | **outer filter + E3-first solve (beta*, sub-class Y4)** | **70.99** | 70.48 | H1'' (the same rate per walked step, over all 2^32 inner values); filter lemma; solver completeness (exact, testable); pass budget (H3 kind); solve-work budget (H2 kind, mean 11,274 f1 per pass) | DERIVED (measured counts) |
| V4q | V4 on the cube 07ef8307 (14 targets) | 72.59 | 72.07 | as V4 | DERIVED: a loss |
| V4p | V4 + 7 outer steps per packed word (outer 65, check 16) | 70.21 | 69.70 | as V4 | GUESS (packing) |
| V4s | V4p + a solver at 2^15 per passing step | 68.14 | 67.62 | as V4 | GUESS (solver) |
| V4u | top-4 betas (mass x2.70, pass 2^-5.69), packed, solver 2^15 per viable tau | 70.22 | 69.71 | as V4 | GUESS |

Not combinable: clusters and bitslicing on V4 (no inner loop); the Y4 cube on any filtered variant (a loss).

## 5. Risks, limits, and what was not run

- No machine count of any new piece: the filter automata, the solve, rule G, bitslicing. The op weights are DERIVED
  estimates. The next step is the filed Machine (copy halfsearch.py) on the outer step + automata + solve.
- V4's figure is dominated by the outer step (400 of about 850 ops per walked step). That 400 is VALUE's bound, not a
  count.
- Shared with V0 and unchanged: model M_outer, the physical-sampler transfer (Sol Y: OPEN), and the second moment.
  - Clumping: successes per passing step are 2^9.8 more concentrated but still about 2^-60, so the bound is
    unaffected (DERIVED).
  - The evaluability gap of VERDICT 3c: no organizer experiment can see the CV half-collision.
- V4 changes what a "trial" is. The claim becomes a rate per walked outer step. A judge may want the filter lemma and
  the solver's completeness proved in proof.md; both are short and exact.
- Not run: an end-to-end check that the cube enumeration and the filter+solve find the same E3 events on real
  passing steps (C: a few hundred passing steps x 2^21, seconds). Also not run: the toy (W = 8) rebuilt with the
  filter, to confirm that each of its 305 real collisions lies in a passing step.
- Pure maths for Sol, if wanted: an exact expectation and variance of the solve work per passing step, and the second
  moment of successes per passing step.

## 6. Files (this folder) and commands

- e3cond.py -> e3cond_out.txt: the E3 identities, the carry counters, sampled (1)/(2) counts.
- outer_filter.py -> outer_filter_bstar.txt, outer_filter_top2/3/4.txt, outer_filter_q01b2.txt: exact pass rates.
  Run `python -B outer_filter.py bstar | top4 | cube_q01b2.out`.
- real_filter.py (with copied verify_ctr.py and cone4_E1b1_B10.txt):
  - real_filter_smoke.txt;
  - real_filter_1M.txt (`python -B real_filter.py 1000000 5 300`, about 2 minutes).
- e3solve.py -> e3solve_out.txt (`python -B e3solve.py 7 300 150`, 38 s); e3solve2.py -> e3solve2_out.txt (15 s).
- run_cube.sh, scan_y4.py:
  - beta_star.lst, cube_*.out, cube_runs.log, scan_y4.txt, scan_y4_q01b2.txt;
  - command: `wsl -d Ubuntu -- bash .../run_cube.sh NAME MASK VALUE`, about 1 s each.
- stack_calc.py -> stack_calc_out.txt: every lever and variant.
- Blocked: nothing. All processes I started have finished.
