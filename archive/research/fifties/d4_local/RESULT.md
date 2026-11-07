# D4 local section 7: implementation and measurement (full 32-bit)

2026-10-09. Source: research\sol_answer_D4_local.md section 7. Organizer code: hash-smash\verifier\blake3.py (rounds=2).
Labels: COMPUTED = measured by code here; DERIVED = algebra from the construction; GUESS = unverified.

STATUS (19:35): FINAL for this pass. Everything below is done; no completed construction was obtained by any method.

SUMMARY
- The solving order is coded exactly (d4c.c); every cycle root comes from an exact carry automaton (validated against full 2^32 scans).
- COMPUTED: the eight "one-word cycles" are not generic equations. Each FIRST has a root with probability 2^-9.5 (but then thousands of roots); a diagonal (FIRST+SECOND) is solvable with probability 1.6e-5 = 2^-15.9, the same in all three arms and all four diagonals. 0 of 24,000,000 random free choices completed all eight; projected rate 2^-63.7.
- COMPUTED: the keeper search below (exact invariances that keep diagonals 0 and 1 while re-randomising 2 and 3) ran 2^34.7 stage-C tries plus 7.7e9 other tries in 6 x 25 min and found 0 completions; the stage-C tries are strongly clumped (joint FIRST2 and FIRST3 never seen).
- COMPUTED with organizer code: on all 1,577 solved diagonals the two boundary b,c words are equal and S_k = 0 (0 failures). The full ten-check test on a completed construction and the D0-D3 rates could not be measured, because no completed construction exists.
- DERIVED: D_j holds iff X_(j+12),A XOR X_(j+12),B = T_j XOR (T_j - Delta y_j). Diagonal k feeds D_(k-1), D_k, D_(k+1) and never D_(k+2); no disjoint grouping; no late word can solve any D_j; only root choice keeps the ten checks, and root choice barely moves low bits.

## Keeper search (new, to get completed constructions at all)

Same construction; only the free inputs are chosen adaptively, using the two exact keepers found below:
- A: random free inputs until diagonal 1 has a pair (about 2^16 tries).
- B: resample A.m3 with h re-chosen (Pi_1 exactly invariant) until diagonal 0 has a pair (about 2^17 tries).
- C: take U5_A from {U : (U + c) XOR U = K0} (c = U5_B - U5_A fixed by P0), m3_A = BPIN(U5_A), h re-chosen: Pi_0 and Pi_1 both exactly invariant (0 violations in 3e8 checks), diagonals 2 and 3 re-randomised. |set| = 2^(1 + number of zero bits of K0 below bit 31), mean log2 = 15.2.
- On all four diagonals having a pair, construct() is run from scratch with those free inputs (order 7.1-7.3 exactly as written).
- Fast solvability test: the same 16-state automaton as a bitmask forward pass (32 table lookups); 300,000-instance self-test vs the exact counter: 0 disagreements.
- Single-core 60 s test (none): 3.2e8 tries (0.18 us each), 337 A-rounds, 1,351 C-entries, 0 found (expected 0.03 at P = 2^-31.8 per C try).
- Full run (COMPUTED), 6 processes x 1,500 s (2 per arm): 12,659 A-rounds (777M A-tries), 6.6e9 B-tries, 99,124 C-entries (mean log2|S| 15.6-17.3), 2.82e10 = 2^34.7 C-tries, invariance violations 0, completed constructions 0 (none 0/6.3e9 C-tries, len 0/12.2e9, flags 0/9.7e9). If C-tries were independent at 2^-31.8, about 7.4 completions were expected.
- Diagnostic (COMPUTED, 3 x 240 s with counting): inside the C-sets FIRST of diagonal 2 passed at 1.5e-5..1.1e-4 and FIRST of diagonal 3 at 4e-4..5e-2 (clumped by entry), both together 0 times in 1.06e9 C-tries, and a full diagonal-2 pair 24 times, a diagonal-3 pair 0 times. DERIVED reason: across a C-set the U9 pair keeps its XOR difference exactly (U9_A^U9_B = beta-terms ^ L7(K0)), so diagonal 3's instance is only partly re-randomised; the set members are not independent trials.
- Cost conclusion: the keeper search did not make a completion cheap. Measured lower bound: more than 2^34.7 stage-C tries (each about 0.18 us, i.e. about 2.6 two-round-compression equivalents) without a completion.

## Setup (choices made here)

- Chaining value = IV. Side A metadata (v12,v13,v14,v15) = (0,0,64,11) = single block, CHUNK_START|CHUNK_END|ROOT.
- Arms: none = side B same as A; len = side B v14 = 63; flags = side B v15 = 3 (ROOT bit removed).
- Free inputs drawn uniformly: common m1,m5; A's m0,m2,m3,m4,m6,m7; B's m0,m4,m6; alpha_1 high 31 bits; h; root choice uniform among roots.
- Code: d4c.c (C, gcc -O3). Order exactly as 7.1-7.3: columns 0,2, col3 first half, col1 side A; alpha_1B bit0 pin; m2_B; P0 by BPIN -> m3_B; P2 by BPIN -> m7_B; d13, R, d10; then for each diagonal FIRST (over x) then SECOND (over y).
- Cycle solver: exact carry graph. FIRST/SECOND are both of the form (P_A + ROR_r(Q_A ^ z)) ^ (P_B + ROR_r(Q_B ^ (z+delta))) = K (r=16, K = B_A^B_B for FIRST; r=8, K=0 for SECOND). A 16-state carry automaton (guessed carry into bit r, carry of z+delta, the two addition carries) counts all roots exactly by backward DP (1,024 transitions) and returns the i-th root. No 2^32 scans in the construction.
- If SECOND has no root for the chosen FIRST root, the other FIRST roots are tried ("retry").

## Solver validation (COMPUTED)

- Full 2^32 scans vs DP root count: 8 equation-level instances (r=16 from constructions, r=8 random; counts 0,0,0,0,64,256,600,640) all equal. G-level scans (b1_A(x) vs b1_B(x+dx), c2_A(y) vs c2_B(y+dy), organizer G formulas): 10 FIRST instances (counts 0..2048) and 6 SECOND instances all equal.
- Planted-root test: 200,000 random instances with a planted root: count >= 1 every time, planted root enumerated in all 176,779 enumerated cases, every enumerated root verifies.
- Every root used in the construction is re-checked by forward G evaluation (b1 common after FIRST; b2,c2 common after SECOND); 0 failures.

## (2) Cycle success rates, 8,000,000 random free choices per arm (24M total) (COMPUTED)

| | none | len | flags |
|---|---|---|---|
| FIRST zero-root rate, per diagonal | 0.99864-0.99869 | 0.99863-0.99868 | 0.99865-0.99869 |
| FIRST mean root count | 0.92-1.06 | 0.91-1.00 | 0.93-1.05 |
| FIRST max root count seen | 122,880 | 221,184 | 147,456 |
| SECOND zero-root rate (random FIRST root) | D0,D3: 1.0000 (0 of ~10,700); D1,D2: 0.9989-0.9998 | 0.9991-0.9998 | 0.9992-0.9996 |
| P(diagonal has some (x,y) pair, all FIRST roots tried) | 1.4e-5 .. 2.0e-5 | 1.6e-5 .. 1.9e-5 | 1.2e-5 .. 1.8e-5 |
| mean (x,y) pairs per diagonal (all samples) | 0.50-2.20 | 0.44-1.35 | 0.35-1.41 |
| all eight cycles solved | 0 / 8M | 0 / 8M | 0 / 8M |
| two diagonals solved together | 0 / 8M | 0 / 8M | 0 / 8M |

- COMPUTED: a FIRST equation has a root with probability 1.34e-3 = 2^-9.5, but then has many roots (mean count is still about 1: the roots come in large clusters). Given a FIRST root, a SECOND root exists for 2^-11..2^-13 of FIRST roots; over all FIRST roots of a solvable FIRST, 1.2% of FIRST-solvable diagonals become solvable. Net P(diagonal solvable) = 1.6e-5 = 2^-15.9, the same in all three arms and all four diagonals.
- DERIVED (why): in both equations the output bit i depends on z only through carries: bit i of the XOR of the two sides equals P_A^P_B^Q_A^Q_B^delta at the matching positions XOR the three carries, and z's own bit cancels. So each equation is an XOR-differential condition through modular additions, not a generic 32-bit equation; most instances have no root.
- DERIVED projection (independence assumed, no joint success seen to test it): P(all eight cycles) = (1.6e-5)^4 = 2^-63.7 per random free choice. Sol's "ten checks met by construction" therefore costs about 2^63.7 random free choices per completed construction.
- Cost (COMPUTED): 18.8 us per free choice with all four diagonals solved exhaustively = 274 word ops + 7.9 DP solves (8,400 carry-graph transitions); one organizer-equivalent 2-round compression in the same C = 68 ns. With the bitmask solvability test and abort at the first unsolvable diagonal, one free choice costs about 0.18 us = 2.6 compression equivalents (columns ~130 word ops + one 32-lookup test; measured in the keeper runs). Per completed construction at random: 2^63.7 free choices x 2.6 = about 2^65 two-round-compression equivalents (DERIVED from the measured rates and timing; no completion observed).

## (3) Organizer-code verification (COMPUTED)

- No completed construction exists in 24M samples, so the full ten-check verification could not be run on a completed one.
- Every sample with a solved diagonal was dumped (1,577 records, no sample had two). With the organizer _g (rounds=2 trace, cross-checked against organizer _compress output for every record): the two boundary b,c words of the solved diagonal are equal in all 1,577 (3,154 words), its absorption sum S_k = 0 in all 1,577, J words common in all. 0 failures. The algebra of 7.2/7.3 (b1 common gives Delta X_k = Delta U_a + Delta U_b + dx + dy; S_k by P0/P2/d10/d13) is confirmed on every solved diagonal.
- 7.3 sufficiency (common incoming b,c + S_j + D_j => round-1 column outputs equal): 100,000 random trials with organizer _g, 0 failures.

## (4) D0-D3 rates (not measurable on real constructions)

- No completed construction, so D0-D3 cannot be sampled. Each D_j needs three solved diagonals (P about 2^-47.7).
- DERIVED exact form: given S_j, D_j holds iff X_(j+12),A XOR X_(j+12),B = T_j XOR (T_j - Delta y_j), with T_j = X_j,A + X_(j+4) + x_j,A and Delta y_j = Delta m6, d10, Delta m0, d13 for j = 0..3. So each D_j is again an XOR-differential condition (the XOR difference that subtracting the fixed modular difference Delta y_j produces), not a uniform 32-bit equality.

## Root multiplicity inside a solvable diagonal (COMPUTED, 240 solvable diagonals, all pairs enumerated)

- Mean (x,y) pairs per solvable diagonal: none 56,633; len 34,528; flags 57,835 (about 2^15.6; by diagonal D0 41,818, D1 47,799, D2 86,758, D3 26,886).
- These pairs move the diagonal's outputs very little in the low bits: across ~5e4 pairs, distinct X_a,A values 17k-27k, but only 13-15 distinct low-8-bit values; distinct X_b 31k-55k, low 8 bits 27 values; the d-word XOR difference X_d,A^X_d,B takes only 130-152 distinct values in total and about 3 distinct low-8-bit values.
- DERIVED consequence: root choice is the only freedom that keeps the ten checks, and it barely moves the low bits of the D checks. The low bits of D0-D3 are essentially fixed by the column state.

## Which free inputs change which diagonal's cycle instance (COMPUTED, 20,000 random samples per arm, all three arms agree)

DERIVED first: diagonal k's root set (in z) and its outputs depend only on Pi_k = (U_c pair, U_d pair, delta_k = Delta U_a + Delta U_b + dx_k, K_k = U_b,A ^ U_b,B, dy_k). If Pi_k is unchanged, the diagonal stays solvable with the same roots and the same X outputs (except X_b when U_b's values move); only its first message word shifts.

P(Pi_k unchanged) after one perturbation (none arm; len and flags identical to 4 decimals in the rows shown):

| perturbation | Pi_0 | Pi_1 | Pi_2 | Pi_3 |
|---|---|---|---|---|
| resample m1, A.m0, A.m2, A.m4, A.m6, A.m7, B.m0, B.m4, B.m6, alpha_1 high bits | 0 | 0 | 0 | 0 |
| resample m5 | 0 | 0 | 0.59 | 0 |
| resample m5, keeping U6_A^U6_B bit 0 (alpha pin bit) | 0 | 0 | 1.0000 | 0 |
| resample A.m3 | 0.0001 | 0.56 | 0 | 0 |
| resample A.m3, h re-chosen | 0.0001 | 1.0000 | 0 | 0 |
| flip h | 1 | 0 | 1 | 1 |
| flip bit 31 of A.m3 | 0.34 | 1.0 | 0 | 0 |
| flip bit 31 of m5 | 0 | 0.14 | 1.0 | 0 |
| flip bit 31 of m1 | 0.24 | 0 | 0 | 0.14 |
| flip bit 31 of A.m7 | 0 | 0 | 0.14 | 0.24 |

- DERIVED reasons: A.m3 moves only column 1; P0 re-pins U5_B = U5_A + const; delta_1 = (Delta alpha_1 + Delta beta_1 + Delta U6)/2 (+2^31 h) does not contain Delta m3, so with h re-chosen Pi_1 is exactly invariant. m5 is common and is column 2's second word, so Delta U2 = Delta a1 + Delta b1 of column 2 is unchanged and Pi_2 only sees Delta U2.
- No single free input keeps all four Pi_k; nothing but root choice keeps the ten checks.
- Keep-solvable test on 150 bases per arm with one solved diagonal (COMPUTED): a full resample of any column word other than m5 and A.m3 kept the solved diagonal solvable 0-1 times in 150; m5 8-20%, A.m3 9-18% (the 1/4 of bases where that word's keeper diagonal was the solved one); bit-31 flips of m5/A.m3 kept it 47-63%.

## (5) Structure (DERIVED)

Exact dependency of the four residual checks on the round-0 diagonals:

| check | diag giving a-word | diag giving b-word | diag giving d-word | round-1 x | Delta y |
|---|---|---|---|---|---|
| D0 | diag0 (X0) | diag3 (X4) | diag1 (X12) | m2 | Delta m6 |
| D1 | diag1 (X1) | diag0 (X5) | diag2 (X13) | m3 | d10 |
| D2 | diag2 (X2) | diag1 (X6) | diag3 (X14) | m7 | Delta m0 |
| D3 | diag3 (X3) | diag2 (X7) | diag0 (X15) | m4 | d13 |

- diag k feeds D_k, D_(k+1), D_(k-1); it never touches D_(k+2). The c-words X8..X11 enter no D check.
- Every column word (m1, m5, A's six, B's three, alpha_1 high bits) changes all four column outputs and so all four diagonals' inputs: it moves all four D_j. Measured above: no free input keeps all four cycle instances; A.m3 (h re-chosen) keeps only diagonal 1, m5 (pin bit kept) only diagonal 2, a restricted A.m3 set keeps diagonals 0 and 1.
- h changes only diag1 (dx = d10) and Delta y_1: moves D0, D1, D2, not D3.
- No disjoint split: every pair of checks shares at least two diagonals. The only partial decoupling: diag2 roots leave D0 fixed, diag0 roots leave D2 fixed, diag3 roots leave D1 fixed, diag1 roots leave D3 fixed.
- No late free word: after the eight cycles all 16 words of both sides are assigned (m10_B, m13_B by d10, d13). The only freedom that keeps the ten checks is the discrete root choice inside a solved diagonal (about 2^15.6 pairs, but only about 14-27 distinct low-8-bit output values and about 3 distinct low-8-bit d-word XOR differences). h changes diag1's instance. No D_j can be solved directly as an 11th constructed check in this order.
- GUESS (lever for a later pass, untested): D0 and D2 have Delta y = Delta m6 and Delta m0, which are free (side B's m6, m0). With Delta m6 = 0, D0 becomes X12_A = X12_B; with Delta m0 = 0, D2 becomes X14_A = X14_B. Whether that helps depends on cycle solvability in that sub-family, not measured.

## Files

d4c.c (all modes: stats, plant, brute, gbrute, roots, keep, pi, seq, bench), verify_organizer.py (organizer-code checks), stats_<arm>_<seed>.txt (8M per arm), dump_<arm>_<seed>.bin (1,577 solved-diagonal records), brute_flags.txt, gbrute_*.txt, roots_*.txt, keep_*.txt, pi_*.txt, seq_<arm>_<seed>.txt (keeper search), seqdiag_*.txt.
