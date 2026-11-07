# CONSTANTS_REOPT: would a different record (six constants, eta, beta, S) make the current construction cheaper?

Date 2026-10-09. Local, read-only, no yukon. Ledger: pkgCA proof.md Section 11 (per outer step = (context, member)),
with 9.1, 10.1, 12 and 17. Scripts are in the session scratchpad (sreopt.py, union.py, plus inline runs). Labels:
PROVED, MEASURED (exact computation run today), DERIVED (arithmetic or reading from stated sources), GUESS.

## 1. Answer
- **Six constants (top level): no.** Among the 65 SAT-prefix instances, the best other one (run 39, 13,107,200) is at
  least +1.41 bit worse even with zero filter and solver cost. A fresh search needs a listed part of at least 42.9M.
  DERIVED.
- **S under beta* alone: no.** Over all 16,383 subsets of the 14 outcomes, the best is 005b (drop 275), -0.005 bit.
  MEASURED.
- **Middle level, a second beta under the pinned constants: YES, about -0.4 bit.** Beta 18d0e098 has eps 6e61be55,
  which differs from ours in one bit. Its exact whole-class part is 54,005,760 (MEASURED). Its outcomes reuse our
  filter almost for free: the shares are exact automaton counts. Listing S = 5f plus six of its outcomes gives:
  - dT -0.61 bit with the credit held fixed;
  - -0.42 with the credit scaled by pass share;
  - -0.40 with a row-by-row cap model (GUESS caps);
  - -0.21 at 1.5x and -0.02 at 2x the scaled credit.
  From about 64.87 that is about 64.47. The construction, the caps and H1' for a second cube are not checked
  (GUESS); see 7.
- pkg12 10.1 ruled out unions ("no union beats beta*") on a per-trial cost. On today's per-outer-step ledger that
  argument does not hold: the 51.5% batch floor and the filter are shared. This is the "tried before, not where we
  are now" case.

## 2. Price terms that depend on the record (search part per outer step = Section 11 rows / 2^69.465 steps)
| term | units/step (share) | depends on | exact tool | GPU |
| --- | ---: | --- | --- | --- |
| rate C = 2^11 x part_S (10.1) | divides | Y3, Y3', Y11, Y11' (the six constants), eta, beta, S | pkg17/count/count_class.py `--beta` (Sec. 17; 9-356 s); pair_calc_sub (C, <= 320 s) | none: 2^-91 per trial |
| batch 67 per 7 + context 600/2^19 | 9.5726 (51.52%) | none: immediates. The class size only moves the context share (0.006%) | Sec. 11 | n/a |
| Q path 67 x 17/16 x p_E | 3.8737 (20.85%) | tau set, eps, D3, S | price.py e_count; scouts2/constants word_hist (any tau, eps, D3) | impl/memberloop/member.cu |
| passing lane 450 x 17/16 x pi | 0.4740 (2.55%) | as above plus eta | price.py ACTIVE; constants.py active_sets (2^64 AND-convolution) | same |
| credit 17/16 x 1.06 x cbar | 4.6588 (25.08%) | caps C(T): Sol G7 trees exist for beta*'s rows only; n_A; VMASK | price.py ledger_cap(G7) | none; caps need Sol |
| success (H1' FACTOR = 5/7 C, H4', H5') | via C and shares | stated per record (10.3) | none | pkg17/gpu, this record only |
| preprocessing P = 2^70 (+0.108) | none | Sec. 12 bound covers further search on the listed machines inside the window | n/a | n/a |
MEASURED: price.py data reproduce E_COUNT 233,715,456, SHARE 18,289,159,183,466,496, CBAR 582,173,006,981,436 (G7),
cbar 4.13659 through the AND-convolution, part 67,633,152, and 18.5792 units per step.
**Objective.** DERIVED from Section 11's one-line time formula, since RUN_STEPS is proportional to 1/C:
dT = log2(c'/18.5792) - log2(R'/R0), where c' = 9.5726 + 71.1875 p_E + 478.125 pi + 1.12625 cbar and
R = the sum of the listed parts. Trials in disjoint cubes add; k cancels per cube.
**Gate for a 0.3-bit win with one beta.** DERIVED. c' cannot fall below 9.5726, so R' must be at least 0.634 x
67.6M, about 42.9M. At today's filter and solver cost R' must be about 83.3M.

## 3. Runs made for this note
(a) The S scan, as in Section 1. On the pkgCB variant (Q path 64, credit x 76/97) 005b gives -0.001. No subset with a
    NEW row (tau ...5060a0) is in the top 15. MEASURED.
(b) The prefix instances (PREFIX.md exact recount). Ours is 71,698,432 and run 39 is 13,107,200, so the bound is
    log2(67.6M/13.1M) - 0.957 = +1.41. scouts2/constants (10-08, old 640 ledger) reached the same verdict. DERIVED.
(c) Beta 18b1a098 (eps 6e203e55): 16 outcomes, part 25,692,160. Every single outcome added to S loses, from +0.085
    up to +0.50 even with the credit fixed, because p_E rises to 0.07-0.19. Closed. MEASURED.
(d) Beta 18d0e098 (cube 0e09818d/02008001, k 11; disjoint from Q*, since bit 0 is fixed to 1 there and to 0 in Q*):
    count_class.py --beta gives 19 outcomes, part 216,023,040/2^81 = 54,005,760 on 2^83 (356 s). MEASURED, exact.
    Greedy best-first additions to 5f with exact shares (credit scaled by pi) in order: 285020a0 -0.221,
    17d020a0 -0.320, 385020a0 -0.351, 185020a0 -0.407, 685020a0 -0.420, 175020a0 -0.4225. The union ends with
    part 114,294,784, p_E 0.0787 (ours 0.0544) and pi 2^-9.293 (ours 2^-9.978). Two other credit models: with a
    separate joint solver per beta, each beta-2 row using the tree shape of the beta* row with the same tau
    (17d -> 175) and the pre-check keeping nu 3 and 4, cbar is 6.967 and dT is -0.401. Over 5b in place of 5f the
    result is -0.43. Alone, as a replacement for beta*, 18d0e098 loses (+0.13 even at zero credit). MEASURED for the parts and
    shares, GUESS for the caps.
(e) Eta classes of D3 fdb77cfd: the carry DP gives at most 96,121 patterns x: 4 of weight 8, 995 of weight 8-12 and
    1,208 of weight 13 like ours. None was scored. DERIVED.

## 4. Constraints any new record must keep (3.1, 3.2, 6.1, 12)
- Fact P: C3 gives equal d and b outputs for W4 and W4' = ((K + W4) XOR 8) - K, with K = 5bf2cd1d. The 8 is
  55 XOR 63 (Lemma L). The top byte of W13 is 0 and w14 = w15 = 0. A beta union keeps all of this unchanged.
- The class of eta is nonempty (Lemma Q). Each listed beta has its own cube (Theorem C analogue) and one eps; the
  cubes must be disjoint so that the trials add.
- A T2 or T1 entry stays one word: the union uses 12 outcome bits.
- The advice grows by about 22 bytes (beta2, its cube, eps2, tau 17d020a0, S2) to about 115 bytes, still under
  2^7. DERIVED.
- Reduction of the top level, DERIVED today from the G equations and checked on ours:
  - D11 = Y11' - Y11 = d1' - d1 = 0a08818b.
  - D3 = (a1' - a1) + (b1' - b1) = 8 + fdb77cf5.
  - The XOR difference of a1 is a carry run from bit 3 (fffffff8).
  - The count reads the record only through (Y3, Y3', Y11, Y11'), eta and beta.

## 5. Search space by level
- L1, S over 14 outcomes: 16,383 subsets. Done.
- L2, betas under the pinned constants: 46 with a part (h8/subcube). The union subsets of 18d0e098 are done
  greedily; 2^19 of them would be exhaustive. 18d1a098 (13.2M sub-class), 18b3e098 and 18d3e098 (k 13) are not
  counted yet (6 min each). Eta: at most 96,121 classes.
- L3, the six constants: about 2^120 tuples (GUESS), but the price sees only (D3, D11, eta, beta): up to 58 carry
  runs, up to 2^(m+1) signings of D11, and the D3 values allowed by the two XOR-consistency conditions. The prefix
  sampled 65 of these points.

## 6. First GPU test (one 3090, under 60 min): the beta-2 union on real outer steps
1. Build T1 and T2 for the 12-outcome union: the automata of 5f plus the six outcomes of 18d0e098 with eps 6e61be55
   (scouts2/constants word_hist logic). Regenerate impl/memberloop tables_generated.cuh. Positive control: the
   5f-only tables must reproduce the current figures.
2. Run member.cu on about 2^36 uniform outer steps (real step-CO lines, omega-first batch). Count E-positive lanes,
   passing lanes, and the 12-bit mask of each pass. Compare with the exact model figures: p_E 0.07867, pi 2^-9.293,
   and the mask histogram that gives cbar 6.967 under the cap model of 3(d). Within 3 sigma is a pass.
3. From the measured shares, compute dT with the credit bracket (scaled, cap model, 1.5x). **Go** if dT <= -0.3 at
   the cap model and below -0.15 at 1.5x. Then send Sol the analogue of Theorem C for cube Q2, the joint-solver rows
   for eps 6e61be55 with (G7) trees and caps, and the pre-check for these rows.
4. CPU, same hour: count 18d1a098, 18b3e098 and 18d3e098 with count_class.py, and run the exhaustive or local subset
   search over the union (2^19 x seconds, so greedy plus one-swap).
The top-level census (GPU enumeration of feasible (D3, D11) pairs, then pair_calc_sub on the best 200) waits on this:
it needs 42.9M or more per beta and was 1 in 65 last time.

## 7. Not tested, and limits
- Whether the omega-first construction of a second cube really shares the batch and the filter. This note assumes
  it from the shape of the T1 and T2 tests, which carry only (tau, eps) per outcome (GUESS). Sections 8 and 9.8
  need a line-by-line check, and Sol needs to confirm Theorem C (iv) for Q2.
- The caps of beta-2 rows are borrowed from beta* rows with the same tau (GUESS). H1', H4' and H5' need new evidence
  for the union. The 2^26 automaton allowance must cover 12 outcomes.
- Not run: the GPU test above, the eta-class scores, the three further betas, and the sub-class or rule variants.
