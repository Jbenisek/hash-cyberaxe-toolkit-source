# VALUE: net effect of the chunk-counter lever on the 55/63 path (folder counter\value)

Written 2026-10-08. Research only: no yukon, nothing submitted or posted, trace untouched, nothing written outside
this folder. Tags: COMPUTED = run here (file named); DERIVED = follows from a named source or an argument given
here; GUESS = judgement, not checked.

## 0. Answer

1. NET (same conventions as the filed 64c075ac: margin 2.0, success floor 0.39, cost /430, no clusters in the new
   arrangement): **time_log2 84.96 against the filed 92.53, a gain of 7.57 bits** (value_calc_out.txt).
   Against the filed arrangement WITHOUT clusters (94.75, the same premise set H1-H3) the gain is 9.79 bits.
   Status: the ledger is COMPUTED from three inputs: an exact count (DERIVED from the team's two independent
   counters), a machine count of the new batch (COMPUTED), and real-arithmetic rates of the new trial (COMPUTED,
   32 bits, 2^45.6 real and 2^44.6 model trials on the GPU, 2^38 on the CPU). Uncertainty of the difference:
   about +-0.4 bit (section 6).
   The board convention (margin 1.4) would read 84.45.
2. Where the 7.57 bits come from (COMPUTED in value_calc_out.txt):
   - rate per trial x 747.92 = 2^9.547 (sub-class): 2^11 x 67,698,688 (part of beta* = 18b0e098 in the sub-class,
     all of it kept by rule A and kept for H1) / 185,377,197.55. The earlier "905x" is the same figure for the
     whole class: 2^11 x 71,698,432 / 162,266,763.66 = 904.92 = 2^9.822 (re-derived here).
   - word operations per trial x 0.844 = 2^-0.244 (machine count: stage A 41 units per 7-lane word against 47;
     stage 2 72 per entered word against 135; budgeted 6.180 per trial against 7.318; charged 6.5 against 7.7).
   - minus the cluster lever of the filed entry (2.222 bits), which the new figure does NOT use.
   9.547 + 0.244 - 2.222 = 7.569.
3. The two scouts measured different things and both are right (DERIVED, section 5): scout_cross measured a
   CONSTANT counter inside the filed arrangement (no gain; t = 0 best; its X2 co-pass and x30/x31 figures belong
   to the filed cluster design). scout_recent's lever is a counter SOLVED PER TRIAL (it absorbs w0), which adds a
   free 32-bit word and lets E1.d1 be prescribed next to Y4. In that arrangement X2 and Y4 are outer-step words, so
   the filed cluster moves (e1 bits, X2 bits) are not available and the X2 co-pass does not enter; t_hi = 0.
4. Real arithmetic (COMPUTED, out\g_*.txt, out\r_*.txt; GPU 2^45 + 2^44 real, 2^44 + 2^43 model; CPU 4 x 2^36):
   every counter trial has beta = 18b0e098 (0 exceptions in 2^45.6); listed E1 outcomes 15,139 against 15,264
   exact (-0.8% +- 0.8%; per-tau chi-square 15.8 on 14 cells); listed tau 2^-10.696 against 2^-10.696; rule A
   2^-8.000; E1 outcome AND rule A 55 against 59.6; listed partial E3 events whole class 3,626 against 3,569
   exact; real against the seven-word model (beta* forced) agrees on every counter, the largest departure being
   sub-class partial E3 events at 1.057 (+2.8 Poisson sd, events cluster by outer step; whole class 0.971).
   Filed arrangement, same events (exact): T1 2^-11, listed E1 outcome of beta* 2^-42.69 per trial. So the
   E1 side of the counter trial carries exactly the 2^11 the count predicts, and the E3 side is unchanged.
5. Evaluability: without clusters the counter figure needs only premises of the kinds H1-H3, which the
   organizers rated "plausible" for 64c075ac (its not_evaluable came from H4-H6, the cluster premises). The one
   premise that can only be supported as an internal-state rate is H1': "a trial whose E1.c1 is forced into the
   cube of beta* has R = 0 at the model's conditional rate 2^11 x 67,698,688 x 2^-128 (factor taken at half)".
   Real messages reach only its internal proxies (listed tau, listed E1 outcome, partial E3 events, E1 outcome
   with rule A); the joint event is at 2^-92, and its only end-to-end support can come from a reduced-width run
   (counter\toy). Section 4.

## 1. The two arrangements (pin H8, lengths 55/63, sub-class bits 21, 26 of e1 zero, rule A of 8 conditions)

| | filed (pkg10, 64c075ac) | counter (scout_recent cone4_E1b1_B10.txt) |
|---|---|---|
| colliding compression | root, counter 0, flags 11 | last chunk of P||B, counter v12 = t solved per trial, v13 = 0, flags 3 |
| free words | 8 (6 outer, X2 middle, Y4 member) | 9 (8 per outer step incl. Y4; inner word E1.d1) |
| per-trial words | D0, C2 to h1 (11 equations), member table | a1, Y6, Y10, Y14, h1 (5 equations); ROL(d1,16) from a run-wide table |
| T1 = c1 in the beta* cube | probability 2^-11 | 1 (by construction) |
| rate per trial (count) | 185,377,197.55 x 2^-128 | 2^11 x 67,698,688 x 2^-128 = 2^-90.99 |
| H1 factor (half the count) | 92,675,904 = 2^26.466 | 69,323,456,512 = 2^36.013 |
| trials for success 0.39 | 2^100.534 (trial-equivalents) | 2^90.987 |
| cluster lever | yes (H4-H6), 1.65 per trial-equivalent | not used (could exist, section 7) |

Checks of the counter construction at 32 bits (COMPUTED): check_ctr_out.txt, 3,000 of 3,000 trials of the C
program (ctr_rates.c, code generated from the order by gen_ctr.py) equal the real compression of a non-root last
chunk (counter T0, flags 3) word for word (107 words), digest words 0, 2, 5, 7 of the 55- and 63-byte blocks
agree, c1 in the cube and beta = 18b0e098, tail bytes zero. The tree claim (last-chunk CV collision = full
collision) is the scouts' and counter\structure's (organizer verifier, t up to 1025 and 2^32 + 5).

## 2. Rates per trial at 32 bits (real arithmetic) - filed against counter

| event | filed arrangement (exact; real 2^45.49 in research\h8\reports\r1_gpu.txt) | counter arrangement, real trials (this folder) |
|---|---|---|
| T1 (beta = 18b0e098) | 2^-11 | 1 (2^45 of 2^45; GPU) |
| listed tau (E1.a2 difference listed for beta) | beta*: 2^-21.70; any listed beta: 2^-18.88 | 2^-10.696 (GPU 2^45; exact 2^-10.696) |
| listed E1 outcome (beta, tau, eps) | any beta 2^-40.15 (real 47 vs 40.48); beta*: 2^-42.69 (real 8 vs 6.99) | 2^-31.694: 10,129 vs 10,176.0 exact |
| rule A on h1 (E3.h1 test) | 2^-8 | 2^-8.000 |
| E1 outcome AND rule A | 2^-48.15 | 55 vs 59.6 exact (GPU, both classes) |
| listed partial E3 event | whole class 2^-32.20 | whole class GPU 3,626 vs 3,569 exact; sub-class 2^-31.93 (model 2^-32.01) |
| eta condition (Lemma E, E1 only) | 2^-31.39 (r1_gpu, whole class) | 2^-26.02 |
| X2 co-pass (filed cluster design, H4) | 0.2585 mean at t = 0 (scout_cross) | not applicable: X2 is an outer-step word |
| d1-direction co-pass of rule-A trials | - | bit 11: 0.953, 12: 0.922, 20: 0.896, 13: 0.875 (rule A carried) |

Per-outer-step overdispersion (CPU runs, 2^20 outer steps x 2^16 inner): rule A variance/mean 572, listed tau 247;
with that variance the CPU deviations from exact are z = -0.12, +1.67, +0.57 (rule A) and -1.28, +1.11, +0.01
(listed tau). E3 partial events cluster by outer step in the sub-class (58 and 7 in two 2^36 runs): they depend on
(Y4, Y9, w8), which are fixed per outer step; only their average enters the rate (DERIVED; section 6).

### 2a. Real against model (GPU; analyze_gpu.txt)

Same program, same counters: "real" = the counter arrangement (outer words random, 2^12 consecutive cube values
per outer step), "model" = the seven-word model with E1.c1 in the same cube and a1, Y6, w5, Y4, Y9, Y14, w8 drawn
independently per trial. Sub-class, real 2^45 trials, model 2^44 (COMPUTED; errors Poisson only):

| event | real / model per trial |
|---|---|
| listed E1 outcome (beta*) | 1.009 +- 0.017 |
| listed tau | 1.0001 |
| rule A, gate H4 | 1.0000, 1.0000 |
| early word 0 (Lemma E, joint E1/E3) | 1.0007 +- 0.0004 |
| eta condition | 0.9998 +- 0.0024 |
| E1 outcome AND rule A | 0.90 +- 0.25 |
| listed tau AND rule A | 0.9999 +- 0.0002 |
| listed partial E3 event | 1.057 +- 0.020 (Poisson; the real events cluster by outer step, so the true error is larger) |
| residual words 0, 1, 2, 3 zero | 1.019, 1.009, 0.984, 0.990 (each +- 0.006 to 0.021) |

Whole eta class (real 2^44, model 2^43), against the exact figures of h8_deep_expected.txt (COMPUTED):
listed E1 outcome real 5,010 vs 5,088.0 exact (z -1.09); listed partial E3 real 3,626 vs 3,569.1 exact (z +0.95),
eps 6e21be55 894 vs 920.0 (z -0.86); E1 outcome AND rule A 19 vs 19.9; real/model: E1 outcome 0.989 +- 0.024,
partial E3 0.971 +- 0.028, early word 1.0004, eta condition 1.0014, residual words zero 0.99-1.03.
Pooled over both classes: listed E1 outcome 15,139 against 15,264 exact (-0.8% +- 0.8%); E1 outcome AND rule A
55 against 59.6 (0.92 +- 0.13). The largest departure is the sub-class partial-E3 ratio 1.057 (+2.8 Poisson
sd; its true error is larger because those events cluster by outer step, and its sign is favourable); the
whole-class one is 0.971. Every other counter is within 2 Poisson sd of the model.

## 3. Word operations per trial (count_ctr_out.txt; machine of halfsearch.py)

COMPUTED with the filed program's own counting machine (seven 36-bit lanes per 256-bit word, rotation 5
operations, one unit per operation, load and store, at most 16 registers), validated lane by lane on 2,100 lanes
against a scalar reference that solves the whole order (rule-A flag, E1-test word and beta: 2,100 of 2,100):

| piece | counter | filed (halfsearch.py TABLES) |
|---|---|---|
| stage A per 7-lane word | 31 operations + 10 loads = 41 | 37 + 10 = 47 |
| stage 2 per entered word | 50 + 22 = 72 | 135 |
| register peak | 16 (7 resident) | 16 (9 kept) |
| entry share (budget) | 1/32 (0.0270 = 1-(1-2^-8)^7 from the measured lane rate 2^-8.000) | 1/32 (measured 0.0262) |
| budgeted per trial | 6.180 | 7.318 |
| charged per trial | 6.5 (x1.04, up to 0.1) | 7.7 |

What makes stage A cheaper: Y11 is pinned, so ROL(E1.d1, 16) of every cube member is one table word for the
whole run (2^21 members, built once); Y4 is fixed per outer step, so rule A's right side is a constant (no list
word V[j]); C1 and the member side of C0/D1 are outer-step words. What costs: z = ROL(Y14, 8) (5 operations) to
reuse the filed rule-A plan. Not counted (negligible, DERIVED): the outer step (about 81 lines, under 400 units)
per 2^21 / 7 = 299,593 words, 0.001 per word; the table build, once per run.

## 4. Premises and the organizers' evaluability problem

- H1' (rate): R = 0 at 2^11 x 67,698,688 x 2^-128 per counter trial; claimed at half. Under the seven-word model
  this is exact (the part of beta* divided by P(beta*) = 2^-11). It is a rate CONDITIONAL ON AN INTERNAL WORD
  (E1.c1 in the cube), and this is the premise that can only be supported as an internal-state rate. Evidence:
  E1 side on real messages at 32 bits (listed outcome rate 2^-31.69 exact, measured -0.8% +- 0.8%); E1-E3
  coupling only through E1 outcome AND rule A (55 vs 59.6), listed tau AND rule A (0.9999 of the model) and the
  Lemma-E early word (1.0004-1.0007 of the model); E3 side by its partial events. No 32-bit
  experiment reaches the joint event. A reduced-width end-to-end run is the only direct test (counter\toy).
  Clumping (DERIVED): one outer step holds 2^21 trials with expected 2^-71 successes; E3 events do cluster by
  outer step, but a second success in the same outer step needs a second E1 outcome there (about 2^-10.7 times an
  overdispersion of about 250 for E1-side events, measured for listed tau) and then a second E3 hit, so the clump
  size stays 1 + o(2^-10); the success bound 1 - exp(-lambda) is unaffected.
- H2', H3' (E1 test passes, stage-2 entries within budget 1/32): the same kind as the filed H2, H3; entry
  share 0.0270 from the measured lane rate; per-outer-step overdispersion (variance/mean 572 for rule A) means the budget is a
  statement about the run average, as in the filed text.
- No H4-H6: the counter figure uses no clusters. 64c075ac was not_evaluable ONLY for H4-H6
  (dossiers\64c075ac\aggregate.json: reasons H4-cluster-yield, H5-cluster-mass, H6-neighbour-budgets; H1, H2,
  H3 "plausible"). GUESS: a counter package without clusters is evaluable at the same level as H1-H3 were.
- New risks that are not rate premises (GUESS on how a judge reacts): messages of 1024 t + 55/63 bytes with t up
  to 2^32 (mean about 2 TiB, inside the 2^64-bit domain); a non-root colliding compression (needs the tree lemma);
  hashing the final pair costs about 2^37 compressions (negligible in the cost model, not runnable by a judge).

## 5. Why the counter-claim does not cancel the gain (DERIVED)

scout_cross section 2 measured (1b) toy rates of the length-sibling pair for several CONSTANT counters and (1c)
the filed trial model with q2 = t_lo, k2 = t_hi as constants: no gain, t = 0 best, large t lowers the X2 co-pass,
t_hi != 0 lowers x30/x31. All of that is correct and is the statement "a constant re-instancing buys nothing"
(round 0 is a bijection for every constant). The lever is different: t is SOLVED PER TRIAL (T0 = ROL(K0.d1, 16)
XOR K0.a1), so it adds one free word to the system, and the system then has a basis with Y4 and E1.d1 both
prescribed (scout_recent, counter\structure). In the counter arrangement:
- t_lo varies per trial, t_hi = 0: the x30/x31 effect (t_hi != 0) does not arise;
- X2 and Y4 are outer-step words; the filed cluster moves (flip e1 bits 14, 30, 31 and X2 bits 14, 30, 31) would
  need a new outer step each, so the X2 co-pass is not a quantity of the counter figure;
- the H1 rate model is unchanged (the counter enters no word that E1 or E3 reads; flags 3 enter K3 only, which
  the order solves): checked by 3,000 / 3,000 real trials and by the rate table of section 2.

## 6. Uncertainty of the net figure

- Rate factor 2^9.547: exact under the model (two counters agree); its counter-specific risk is the E1-E3
  independence under forcing and the outer-step averaging of E3. Measured proxies agree within their errors
  (E1 outcome -0.8% +- 0.8%; E1 outcome AND rule A -8% +- 13%; partial E3 +5.7% sub-class, -2.9% whole class).
  GUESS: +-0.3 bit for what the proxies cannot see (the joint E1-E3 event).
- Cost ratio 2^-0.244: machine counted; the 1.04 allowance and 0.1 rounding move it by about +-0.05 bit.
- Shared with the filed figure (cancels in the difference): the seven-word model itself, margin 2.0.
- Upside not counted: a Y4 set chosen for beta* (the whole class already gives +0.083 bit, rule A not recounted
  there), a rule built for beta* only, the board's margin 1.4 (+0.515), clusters (section 7).
Total for the difference: about +-0.4 bit (GUESS on the composition; components COMPUTED where stated).

## 7. Clusters in the counter arrangement (not counted; would bring back H4-H6-type premises)

In the inner direction the rule itself is carried (COMPUTED, 2^28 rule-A trials per CPU run, three runs agree):
flipping free bit 11 / 12 / 13 / 14 / 20 / 21 of c1 (the trial stays in the cube) keeps all eight conditions of
rule A with probability 0.953 / 0.922 / 0.875 / 0.813 / 0.896 / 0.823, and the four of H4 with 1.000 for bits
11-14 and 28-31. The filed design worked with co-pass 0.54-0.87 under a 4-condition gate. A cluster design here
would likely be worth 2 to 3 bits more (GUESS, by the filed formula K = a(1 + n p0)/(1 + S) + s p0 discounted by
the 1.7 seen when the filed design was machine-counted), but it re-imports the yield, mass and budget premises
that made 64c075ac not_evaluable.

## 8. Files and commands (all in this folder)

- gen_ctr.py: compiles the order cone4_E1b1_B10.txt (copied from scout_recent) into C (ctr_gen.inc) or CUDA
  (ctr_gen.cuh); uses verify_ctr.py (copied from scout_recent) for the relations.
- ctr_rates.c (CPU): `check` mode -> check_out.txt, checked by check_ctr.py -> check_ctr_out.txt; `rates` mode ->
  out\r_sub_cube_s11.txt, r_sub_cube_s12.txt (sub-class), r_all_cube_s13.txt (whole class), r_all_free_s14.txt
  (control: c1 uniform); smoke_rates.txt. Analysis: analyze_cpu.txt.
- ctr_gpu.cu (GPU): out\g_real_sub45.txt, g_model_sub44.txt, g_real_all44.txt, g_model_all43.txt; run log
  out\gpu_runs.log. Analysis: analyze_gpu.txt.
- count_ctr.py -> count_ctr_out.txt: the machine count (imports research\pkg10\pkg\blake3-r2\experiments\
  halfsearch.py read only).
- value_calc.py -> value_calc_out.txt: the ledger.
- analyze.py: rates against exact and real against model.
- Scripts: build.sh, build_gpu.sh, run_main.sh, run_gpu.sh, wait_cpu.sh, wait_gpu.sh; my_pids.txt (PIDs of my
  background runs; all finished).
Commands (PowerShell): `wsl -d Ubuntu -- bash ./research/newpaths/counter/value/build.sh`
(gcc build, 3,000-trial check, smoke run); `... /run_main.sh` (four CPU runs, about 20 min); `... /build_gpu.sh`,
`... /run_gpu.sh` (about 50 min on the 3090); `python -B check_ctr.py check_out.txt`; `python -B count_ctr.py 300 9 7`;
`python -B analyze.py`; `python -B value_calc.py`.
