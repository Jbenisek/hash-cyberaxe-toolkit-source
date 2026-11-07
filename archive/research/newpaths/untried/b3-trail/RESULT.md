# b3-trail: counter and flag difference trails on 2-round BLAKE3 (scout, 2026-10-10)

Our own team's research. Nothing filed or submitted. Labels: COMPUTED (I ran it), DERIVED
(arithmetic or a hand proof from computed or cited facts), GUESS.

## 0. Answer

- **Legal cells.** A flag difference with equal chaining values exists only as flags 11 vs 12
  at the root (one 64-byte chunk vs a two-chunk parent) or 3 vs 4 at a right child, and the
  right child brings the counter difference t (any even t; t = 2^31 is MSB-only). A counter
  difference alone needs different tree shapes (generic 2^128 match). Section 1.
- **Best characteristic found (flags, root):** probability **2^-382** (LM), 2^-376 per trial
  after prepaying the round-0 absorption on cv_L: cost about 2^377.6, about **315 bits short**
  of beating 2^62.79. Counter routes found only heavier characteristics: counter + flags
  (t = 2^31) 2^-451 (about 384 bits short); counter only (generic) 2^-757.
- **Proved floor (flags, case Z = differences cancelled inside round 0, which covers every
  trail whose round-0 state difference is zero):** round-1 weight >= **67** in the LM
  single-characteristic model, so cost >= 2^64.1 (optimistic per-pair cost) to 2^68.6 (plain):
  no such characteristic beats 62.79. **The same floor (>= 67) is proved for the counter + flag
  route for every legal even counter t < 2^32** (section 6). For the counter-only generic cell
  (illegal as a route) no floor above 21 was proved.
- **Obstruction:** the absorbing message word re-enters a round-1 column call, so the last
  step holds two active matched pairs (G4/G6 on digest words 0,2,5,7 and G5/G7 on words
  1,3,4,6) that must emit swapped-equal 128-bit differences; one matched pair costs >= 26
  (rows a,c) / >= 21 (rows b,d) proved, 79 / 99 at best found; columns + G4/G6 jointly >= 46.
- **Not closed:** case NZ (nonzero state after round 0): the full model stayed undecided even
  at W <= 30 within 4 minutes. Clustering (summing characteristics) was not measured.

## 1. Which counter / flag differences are legal (DERIVED from verifier\blake3.py tree logic)

The two compressions of a colliding pair must have equal chaining values, or a 256-bit CV
difference enters (closed elsewhere: SOLCLOUD_13, C8). With CV = IV on both sides, the only
legal ways to get a counter or flag difference are:

- **F (root, flags only).** M = one 64-byte chunk: root call (IV, m, counter 0, len 64, flags
  CHUNK_START|CHUNK_END|ROOT = 11). M' = two chunks: root call (IV, cv0||cv1, 0, 64,
  PARENT|ROOT = 12). Input difference: dv15 = 11 xor 12 = 7, nothing else.
- **CF_t (right child, counter + flags).** M has t+1 chunks, its last chunk is one 64-byte
  block at index t: (IV, m, counter t, 64, flags 3). M' has t+2 chunks; the same tree node is
  a parent: (IV, cv_t||cv_t+1, 0, 64, flags 4). The first t chunks are shared, so the hashes
  collide iff these two CVs collide. Legal for every even t >= 2 (t < 2^51 so data < 2^61
  bytes). Input difference: dv12/dv13 = t, dv15 = 3 xor 4 = 7. Lightest counters: t = 2^k
  (k = 1..31); t = 2^31 is an MSB-only difference (messages of about 2 TiB; the shared prefix
  costs about 2^35 compressions once, negligible).
- **Counter only** (chunk vs chunk at different indices): the prefixes then differ in size,
  so a generic 2^128 subtree match is needed (EDGES_FIBRE item 2). Searched here only for the
  number (the generic "free ctr x trail" cell), not as a route.
- Other flag pairs (CHUNK_START vs none, END vs none, multi-block roots) carry a chained CV
  on one side and IV (or another chained CV) on the other: a full 256-bit CV difference.

In both legal routes the parent side's message is a pair of chunk CVs (random: 1 compression
for the last chunk, 16 for a full chunk) and the chunk side is free, so each pair is fixed by
the parent message. Conditions on cv_L words only (m0..m7) can be prepaid by choosing cv_L;
every other condition costs trials.

## 2. Model and tool checks

- b3trail.py writes a CNF whose models are XOR-differential characteristics of the 2-round
  compression (16 G calls): fixed input difference (or a solver-chosen counter difference),
  free message differences (the same XOR difference in both rounds), output condition
  dv[i] = dv[i+8] for i < 8 (output words are v[i] ^ v[i+8], no feed-forward there).
- Every 2-input modular addition is priced by Lipmaa-Moriai (validity, weight
  HW(~eq & 0x7fffffff)). A 3-input addition a+b+x is two LM additions and the solver may pick
  any of the three pairings, so lower bounds hold for every evaluation order.
- Total (or selected) weight <= W by a sequential counter; kissat 4.0.3 in WSL with --time;
  each model is decoded and every active addition re-priced by an independent LM routine
  (decode.py; all decoded models in this report: 0 invalid transitions).
- **Checks (COMPUTED).** LM formula vs brute force on 5-bit words, all 32,768 triples: 0
  mismatches; CNF addition encoding vs LM, all triples: 0 mismatches (test_lm.py). 1-round
  sanity: flags-only difference gives a weight-7 collision characteristic (dm6 = 7, dm7 = 1,
  absorbed inside G3 of round 0), the known 1-round absorption.

## 3. Structure (PROVED by hand from the G steps; exact statements, no probability)

G(a,b,c,d,x,y): a+=b+x; d=(d^a)>>>16; c+=d; b=(b^c)>>>12; a+=b+y; d=(d^a)>>>8; c+=d; b=(b^c)>>>7.

- **L1 (zero output).** If a G call has zero output difference, its input difference lies only
  in rows a and d (invert G step by step). A difference in row b or c is never absorbed by one
  call.
- **L2 (message only).** A G call with zero input difference and a nonzero message difference
  outputs a nonzero difference in row b or c (x differs: a1, d1, c1, b1 all differ, and c2 = 0
  would force b2 = b1>>>7 != 0; only y differs: a2, d2, c2, b2 all differ).
- **L3 (b,c clean in).** If rows b and c of the input carry no difference and the output rows
  b and c carry none either, the whole output carries none.
- **Split.** S1 = state difference after round 0. Case Z: S1 = 0. Then every round-0 diagonal
  call outputs zero, so (L1) its b,c inputs are clean, so (L3) every round-0 column call outputs
  zero, so (L2) only the calls holding the input difference may use message differences:
  flags -> dm6, dm7 only (G3 absorbs dv15 = 7); counter -> dm0, dm1 (G0 absorbs dv12).
  Case NZ: S1 != 0.
- **Case Z forces an active, matched last step.** Each absorption needs an x-word difference
  (round-0 a,b are IV constants), and those words (m0, m2, m4, m6) all re-enter round-1 column
  calls; by L2 that call leaves a b/c-row difference, which by L1 makes a last-step diagonal
  call active. For the flags: dm6 is y of round-1 G0, so v0, v4, v8, v12 all differ and v4, v8
  make G7 and G6 active. The output condition pairs the last-step calls: G4 with G6 (digest
  words 0,2,5,7) and G5 with G7 (words 1,3,4,6), with out(G4) = (c,d,a,b) of out(G6), likewise
  G5/G7. So a trail must make two independent G calls produce swapped-equal 128-bit output
  differences, twice. This is the differential form of OPUS_1's four-checks theorem, and the
  two pairs are exactly the front line's pinned words (0,2,5,7) and residual words (1,3,4,6).
- In the flag route's case Z the G4/G6 inputs differ only in rows a,c and G5/G7 only in rows
  b,d (round-1 G1 and G3 are inactive), with no message difference in their words.
- **LM floor before the last step:** round-0 flag absorption >= 6 (DERIVED: bits 0-2 of dm6 and
  dm7 are not-equal positions in both additions); round-1 columns G0 + G2 = exactly 11
  (COMPUTED, run 11; the optimum is the hand trail dm6 = dm7 = 1, G0 2 + G2 9).
- **A matched pair is cheap when all four input rows may differ (DERIVED by hand, each step
  checked with the LM rule).** Input (a,b,c,d) = (0x81000800, 0x01000800, 0x01000001,
  0x80010000), no message difference: weights 2 + 2 + 0 + 1 = 5 to the self-symmetric output
  (0, 2^24, 0, 2^24); two copies are a matched pair of weight 10. So any useful bound must use
  the row restriction above.

## 4. How a weight compares with 62.79 (DERIVED, per the cost model)

- Prepaid: the round-0 absorption conditions sit on cv_L words (m6, m7 for the flags; m0, m1
  for the counter), so they are met once by choosing cv_L. What must be paid per trial is the
  round-1 weight w_r1.
- Plain count: one fresh cv_R (1 compression) and two 2-round compressions per pair, about
  2^1.6 units, so cost about 2^(w_r1 + 1.6); beating 62.79 needs w_r1 <= 61.
- Optimistic count: lists cv_L x cv_R; round-0 columns precomputed per cv_L; in case Z both
  sides share the round-0 diagonal step (about 48 word ops per pair), then early abort after a
  few ops; about 58 ops = 2^-2.9 units per pair, cost about 2^(w_r1 - 2.9); beating 62.79 needs
  w_r1 <= 65 (GUESS for the op count, DERIVED otherwise).
- So a case-Z trail is out of the race once w_r1 >= 66 is proved. Clustering over
  characteristics with the same message difference could give the attacker a few more bits
  (GUESS, not measured).

## 5. Runs and numbers (COMPUTED unless marked)

Solver outcomes: SAT (a characteristic within the bound was found and re-priced), UNSAT
(none exists: a proof), UNKNOWN (time limit hit). Times are kissat --time limits.

| # | case | model | bound | run | outcome |
|---|---|---|---|---|---|
| 1 | 1 round, flags | full | W<=20 | 60 s | SAT, weight 7 (sanity) |
| 2 | 2 rounds, flags F | full, all 16 dm free | W<=62 | 540 s | UNKNOWN |
| 3 | F | full | W<=30 | 240 s, --unsat | UNKNOWN |
| 4 | F | dm6, dm7 only | W<=200 | 240 s, --sat | UNKNOWN (nothing found) |
| 5 | F | dm6, dm7 only | W<=62 | 240 s, --unsat | UNKNOWN |
| 6 | F case Z, cheapest columns (dm6 = dm7 = 1, weight 17 before the last step, by hand) | last step only | bisection | 120 s steps | SAT at 365 (G4 78, G6 110, G5 89, G7 88); 293, 362, 397 UNKNOWN |
| 7 | counter only, t = 2^31, cheapest columns (weight 1 before the last step) | last step only | none | 1 s | **UNSAT at any weight** |
| 8 | one matched pair, rows a,c, no message difference | pair | bisection | 120 s steps | SAT at 79 (34 + 45); 39, 59 UNKNOWN |
| 9 | same | pair | W<=30 / W<=25 | 120 s each, --unsat | UNKNOWN / **UNSAT: pair >= 26** |
| 10 | one matched pair, rows b,d, no message difference | pair | none / W<=30 / W<=25 / W<=20 | 0 s / 120 s / 120 s / 120 s, --unsat | SAT at 99 (64 + 35) / UNKNOWN / UNKNOWN / **UNSAT (96 s): pair >= 21** |
| 11 | F case Z: the two round-1 column calls alone (no output condition) | full, counted r1c0+r1c2 | bisection | 60 s steps | **exact minimum 11** (W<=10 UNSAT in 4 s; 11 found) |
| 12 | F case Z: columns + G4/G6 jointly (words 0,2,5,7 required; G5/G7 unconstrained) | full, counted r1c0+r1c2+r1d0+r1d2 | W<=45 | 31 s, --unsat | **UNSAT: SubA >= 46** |
| 13 | rows b,d pair with the WLOG cut w(P) <= W/2 | pair | W<=29 / W<=27 / W<=25 | 150 s each, --unsat | UNKNOWN / UNKNOWN / UNKNOWN (pairBD stays >= 21) |
| 14 | CF_t, t = 2^31 (counter + flags 3 vs 4), case Z, columns free | full | bisection | 100 s steps | SAT at 920 (unbounded first model; counter absorbed at weight 0 by dm0 = dm1 = 2^31); 460, 690, 805 UNKNOWN |
| 15 | counter only, any nonzero t in v12, case Z, columns free | full | bisection | 100 s steps | SAT at 757 (unbounded first model, t = 0xffffffff); 378, 568, 663 UNKNOWN |
| 16 | CF_t, every legal even t < 2^32 with flags 3 vs 4, case Z: columns + G4/G6 jointly | full, counted r1c0+r1c2+r1d0+r1d2 | W<=45 | 73 s, --unsat | **UNSAT: SubA_CF >= 46** |
| 17 | counter only, any nonzero t < 2^32, case Z: columns + G4/G6 jointly | full, counted | W<=45 / W<=40 | 150 s each, --unsat | UNKNOWN / UNKNOWN (no floor proved for this generic cell) |
| 18 | CF_t, t = 2^31, case Z, hand columns (round 0: 6 + 0; columns G0 2 + G2 10 = 12) | last step only | bisection | 100 s steps | SAT at 433 (G4 159, G6 75, G5 121, G7 78); 307, 370, 402 UNKNOWN; full trail 6 + 12 + 433 = 451 |
| 19 | hand trails sampled on the real G (verify.py, 2^22 samples per call, real round-0 constants) | sampling | - | seconds | flag absorption (r0 G3) 2^-3.00 (LM 2^-6); counter 2^31 absorption (r0 G0) 1.00 (LM 0); round-1 G0 2^-2.00 (LM 2); round-1 G2 2^-7.98 (LM 9) for flags, 2^-9.04 (LM 10) with the counter; counter-only round-1 G2 2^-1.00 (LM 1) |

## 6. Obstruction, distance to 62.79

**The obstruction: two matched pairs in the last step.** Every route that cancels the counter
or flag difference inside round 0 (case Z) re-injects its absorbing x-word difference into a
round-1 column call, which (L2) leaves a row-b/c difference, so (L1) the last step has two
active pairs that must emit swapped-equal 128-bit output differences from independent
inputs: G4/G6 (digest words 0,2,5,7) and G5/G7 (words 1,3,4,6). Each matched pair is the
expensive part of every characteristic found.

**Numbers for the flag route F (root, flags 11 vs 12), case Z, LM single characteristic:**

- Proved lower bound (DERIVED from the COMPUTED UNSAT results 9, 10, 12 and the hand lemmas):
  w_r1 = w(columns) + w(G4,G6) + w(G5,G7) >= SubA + pairBD >= 46 + 21 = **67**; with the round-0
  absorption (>= 6, prepaid) the whole characteristic has weight >= 73.
  Plain cost >= 2^(67+1.6) = 2^68.6, that is >= 5.8 bits above 62.79. Optimistic cost
  >= 2^(67-2.9) = 2^64.1, >= 1.3 bits above. (Other proved pieces: columns exactly 11, any
  a,c-row matched pair >= 26, any b,d-row matched pair >= 21.)
- Best characteristic found: weight 382 = 6 (round 0) + 11 (columns: G0 2, G2 9) + 365 (last
  step: G4 78, G6 110, G5 89, G7 88), probability 2^-382; per trial 2^-376 after prepaying
  round 0, cost about 2^377.6, about **315 bits above 62.79**.
- The truth lies between 67 and 376 for w_r1; the solver could neither find a last step below
  365 for the cheapest columns nor refute 362 in 120 s.
- Within this budget the margin under the optimistic count (1.3 bits) is thinner than the
  plausible clustering gain (GUESS: a few bits), so the claim is "no single characteristic
  of case Z can beat 62.79", not "no differential can".

**Numbers for the counter routes (case Z):**

- The counter alone is absorbed for free when t = 2^31: dm0 = dm1 = 2^31 cancel it in round-0
  G0 with LM weight 0, and exactly (probability 1 with the real constants; MSB differences
  pass additions unchanged). So the counter costs nothing in round 0; the cost moves to the
  last step, where dm0 (round-1 G2, y) again forces the two matched pairs.
- Counter only, t = 2^31, cheapest columns (weight 1 before the last step): no last step
  exists at any weight (run 7, UNSAT in 1 s). With columns free and any nonzero t in v12 the
  best found is weight 757 (run 15; the solver picked t = 0xffffffff; round 0 93, round 1
  664), probability 2^-757, per trial 2^-664 after prepaying round 0: about 600 bits short;
  nothing below 757 was found in 100-s steps. This cell needs the generic 2^128 tree match
  anyway (section 1).
- Counter + flags (legal right-child route), t = 2^31: best found weight **451** = 6 (flags,
  round 0) + 0 (counter, round 0) + 12 (columns: G0 2, G2 10) + 433 (last step, run 18),
  probability 2^-451, per trial 2^-445 after prepaying round 0, cost about 2^446.6, about
  **384 bits short**. With the columns left free the full case-Z model found only 920 (run 14).
- Floor, counter + flags (DERIVED from runs 16 and 10): in case Z of this route round-1 G1 and G3
  stay inactive and G5/G7 carry no message difference, so G5/G7 is again a b,d-row matched pair
  (>= 21) and w_r1 >= SubA_CF + 21 >= **67** for every legal even t < 2^32: cost >= 2^64.1
  (optimistic) to 2^68.6 (plain), the same floor as the flags-only route.
- Floor, counter only (generic cell, illegal as a route): not proved; SubA for this cell stayed
  undecided at 45 and 40 (run 17). The pair bound still gives w_r1 >= 21 (G5/G7 b,d pair).

## 7. Limits, what was not tested

- **Case NZ is not closed by proof.** The full model (all 16 message words free) stayed
  undecided: W = 62 in 540 s (kissat default) and even W = 30 in 240 s (--unsat). A dedicated
  case-NZ search (S1 != 0 forced) was prepared (b3trail.py --s1 nonzero) but not run in this
  budget. OPUS_1's word-level count (13 conditions for nonzero-state routes, round-0 stages
  not free) is the only other evidence; I did not re-check it.
- All numbers are single-characteristic LM weights (independent additions). The real
  collision probability for a fixed message difference sums many characteristics; that sum
  was not bounded. With the real round-0 constants the flag absorption is 2^-3 (measured
  2^-3.00, run 19), not the LM 2^-6; it is prepaid on cv_L either way.
- XOR differences only; modular-difference trails were not modelled.
- Counter in the high word (t >= 2^32, messages >= 4 TiB) makes round-1 G1 active, so the
  row-restricted pair bounds do not cover it; not searched.
- Flags combined with a shorter chunk-side block (length difference too) not searched: the
  zero padding fixes chunk-side bytes while the parent side is random (8 bits per padded byte).
- Chaining-value differences not searched (closed elsewhere: SOLCLOUD_13, no score below 63.6).
- base ctr x trail (t as a value, not a difference) unchanged: GAPS row 6 stands (the exact
  counter already sums every E1/E3 characteristic; a trail only adds conditions).
- Every solver run was capped under 10 minutes and one process ran at a time; stronger bounds
  need longer SAT runs or a dedicated pair-matching search.

## 8. Tool calls that were blocked or stopped

- One wait written as `Start-Sleep` was blocked by the harness (it asks for a monitor instead).
  I did not retry it; waits used background monitors on my own job's PID or log.
- I stopped four of my own background jobs with TaskStop: a waiter whose `pgrep -f` pattern
  matched its own command line (it would never have started anything), a linear-descent run
  replaced by bisection, and two queue tails replaced by reordered queues (each stopped
  between solver runs or at the start of one); plus three of my own log monitors. No other
  process was touched; no pkill, no kill by name; I checked afterwards that none of my solver
  processes was left running.
- One 1-second generator self-test wrote two temporary files to %TEMP% and deleted them at
  once; everything else was written in this folder.

## 9. Files (all in this folder)

- b3trail.py (full model), diag_match.py (last step for fixed column trails), pair_free.py
  (one matched pair, free inputs), decode.py (decoder and independent LM re-pricing),
  test_lm.py (brute-force checks), verify.py (sampling on the real G), make_hand_dec.py (hand
  column trails), run.sh / run2.sh / runone.sh / bisect.sh / lbsearch.sh / minimize.sh /
  batch.sh / queue*.sh (drivers; one kissat at a time, kissat --time, no wrappers).
- runs/LOG.txt (every solver outcome), runs/*.dec.txt (decoded characteristics),
  runs/*.sol.txt (solver status lines), runs/*.gen.txt (CNF sizes), runs/verify_hand.txt
  (sampling, run 19), runs/hand_checks.txt (hand-trail LM weights). CNF files were deleted
  after each solve; every CNF is rebuilt in seconds by the generator line in runs/LOG.txt.
- Key characteristics: runs/diagF11_W414.dec.txt (flags last step, 365), runs/zCOLS_W13.dec.txt
  (optimal columns, 11), runs/diagCF31_W461.dec.txt (counter + flags last step, 433),
  runs/pairAC_W82.dec.txt and runs/pairBD_W-1.dec.txt (matched pairs 79 and 99).
