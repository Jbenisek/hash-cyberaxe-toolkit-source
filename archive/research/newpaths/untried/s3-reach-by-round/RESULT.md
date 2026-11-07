# SHA3-256 reach-by-round: which technique opens at which round, and its cost (2026-10-10)

Scope: SHA3-256 with prefix rounds 0..r-1 in every permutation (organizer `verifier/keccak.py:sha3_256(msg, rounds=r)`).
For each technique on our grid, the deepest round it still works and its cost at r = 3,4,5,6,7. Cost unit per the
owner's convention: organizer unit where a track exists (r5 = 1355 ops/perm, r6 = 1626); word operations (log2 N) otherwise.
A "natural unit" column divides by one r-round permutation (271*r ops) so the depths are comparable.
Labels: COMPUTED (run here), DERIVED (arithmetic from cited figures), GUESS. Nothing filed or submitted; our own research.

## 0. Headline
- **The low-degree (FES on W40) route opens exactly at r = 6.** COMPUTED 123.18242 in r6 units, re-validated to D19's
  exact numerator `19621183271953275558043014167496083929897`. It beats the board 124.04565 by 0.863 bit. No r6
  submission uses finite differences (RULES.md), so this depth is the untried door.
- **It is birthday-level, not sub-birthday.** At r = 3,4,5 FES still works (tested end-to-end here) but only scores
  ~123.2-123.8 natural units = a 2^128-candidate birthday with cheap steps. At r = 5 the internal differential (2^105)
  beats it by ~18 bits, so FES opens no NEW door below r = 6.
- **r = 7 is newly tested and priced.** chi7-input degree is exactly 16 (COMPUTED, nonzero at dim 16, zero at dim 17).
  The degree-16 FES setup costs 2^136 word ops (naive init is 3^40; D19's Moebius init is P_16 ~ 2^37 evals/coset),
  giving 125.85 natural units: still ~2 bits under generic birthday, but 2.7 bits worse than the r6 sweet spot and there
  is no r7 track. Obstruction named with a number.

## 1. Reach-by-round grid (deepest working round + cost)

| technique | r=3 | r=4 | r=5 (/1355) | r=6 (/1626) | r=7 | deepest useful |
|---|---|---|---|---|---|---|
| **low-degree W40 FES** | 123.758 u | 123.412 u | **123.217 u** | **123.182 u (beats 124.046)** | 125.851 u | **r=6** |
| 2-round linear structure | ~128 | ~128 | ~128 | 132.074 u standalone / +0.013 as leader patch | ~128 | r=6 (worse than FES) |
| 3-round structure | dead | dead | dead | dead | dead | r=2 (never reaches chi3) |
| internal differential | <=2^105 | <=2^105 | **2^105 (SUB-BIRTHDAY)** | 2^172 (169.5 best) | worse | **r=5** |
| connector + trail | - | - | open | 2^206 (2^197 abort) | - | none for SHA3-256 |
| generic birthday | ~128 u | ~128 u | ~128 u | 124.046 board / 124.27 promoted | ~128 u | all (floor) |

"u" = log2 of (word-ops / 271*r), i.e. the score in one-r-round-permutation units. For r5/r6 that IS the organizer
track unit (1355/1626). Full exact word-op numerators are in `out_ledger.txt` and the low-degree rows of `reach.csv`.

## 2. Low-degree route: exact per-round ledger (COMPUTED, `ledger_by_round.py`)
D19-style counting generalized to r rounds. Only these change with r: chi_r-input degree D = 2^(r-3); the uncached FES
chain sum sum_p C(40,p)*min(D,p); the degree constants P_D, J_D, V_D (D19 Section 2 closed forms); the per-point
evaluation schedule (r-1 full rounds + 1 linear step); the two-permutation verification charge. The 175-plane cone,
the 4656 chi/transpose, n = 40, and the 256-bit / 140-bit-key birthday (G, Q, R129, R140, B = 2^129) are r-independent.
**Validation: r = 6 reproduces D19's N_v exactly and time_log2 = 123.18242 (D19 rounds up to 123.18243).**

| r | D | N (word ops, exact) | log2 N (word ops) | natural unit /271r | dominant term |
|---|---|---|---|---|---|
| 3 | 1 | 14621473351299012435222369944513055392888 | 133.42521 | 123.75810 | G*chi/transpose (132.18) |
| 4 | 2 | 15338181635711633652706252131973109651835 | 133.49425 | 123.41210 | G*chi/transpose |
| 5 | 4 | 16749368921849664548484950053263599886167 | 133.62123 | 123.21715 | G*chi/transpose |
| 6 | 8 | 19621183271953275558043014167496083929897 | 133.84953 | 123.18242 | G*chi/transpose |
| 7 | 16 | 145520963694473729600761241428652183975707 | 136.74027 | 125.85077 | **setup Sv (136.47)** |

Why the natural-unit score falls r3->r6 then jumps at r7: the numerator N grows only mildly r3->r6 (the FES term grows
with D) while the unit 271*r grows faster, so N/271r falls to a 123.18 minimum at r6; at r7 the degree-16 setup Sv
explodes past every birthday term (2^136) and dominates, so the score jumps 2.7 bits. The route's useful ceiling is r6.

## 3. End-to-end tests at each depth (COMPUTED, `test_fes_by_round.py`, `out_test_fes.txt`)
Reusing the certified W40 embedding (`research/sha3r6/lowdegree/cube_degree.py`): one block, 135-byte message, byte 135 =
0x86, zero capacity; organizer round function. For each r, the chi_r-input f_t = rounds 0..r-2 full + theta/rho/pi of
round r-1 (row 0, 320 bits). The route works iff the Gray FES chain at degree D reproduces direct evaluation (0 plane-word
mismatches) and the explicit chi_r + iota of the FES planes equals `sha3_256(msg, rounds=r)`.

| r | D | n | FES@D mismatches | control FES@(D-1) | end-to-end digests | result |
|---|---|---|---|---|---|---|
| 3 | 1 | 12 | 0 of 1,310,400 | (D-1=0, n/a) | 384/384 equal | WORKS |
| 4 | 2 | 12 | 0 of 1,310,400 | 1,309,758 fail | 384/384 equal | WORKS, degree tight |
| 5 | 4 | 13 | 0 of 2,621,120 | 2,612,800 fail | 384/384 equal | WORKS, degree tight |
| 6 | 8 | 13 | 0 of 2,621,120 | 1,942,080 fail | 384/384 equal | WORKS, degree tight |

Degree of the chi_r-input via vectorized cubes (nonzero at dim D, zero at D+1 => degree exactly D):
- r = 6: dim7 40/40, dim8 40/40, dim9 0/40  => degree exactly 8 (COMPUTED).
- r = 7: dim15 40/40, dim16 40/40, dim17 0/40 => **degree exactly 16 (COMPUTED; never run before per lowdegree/RESULT.md)**.

The r3,r4,r5 end-to-end digest matches are new (lowdegree/RESULT.md ran only D=8 and a D=4 FES self-check, not full
digest equality at r=3,4,5). The degree-tightness controls confirm D = 2^(r-3) is exact, not just an upper bound.

## 4. Other techniques (DERIVED/cited from SHA3R6_MAP.md sections 3-4; not re-run here)
- **2-round linear structure (W40 / SOLCLOUD_16).** Parent of the FES route (same field, affine after 2 rounds).
  Standalone birthday with a cheap Gray step: 132.0744 at r6 (full-record sorting ledger); as a replacement for the
  leader's chi2/theta3 patch only +0.013 bit (MAP 3.4). Affine property holds at every r; the FES route supersedes it.
- **3-round structure (linstruct3).** DEAD at every r >= 3: extending the affine region through chi3 gives rank <= 2
  (10,000 rank-2 checks, 0 fails; 0 triangles so no rank 3). Obstruction: theta3 spreads each direction's chi2 bits to
  56-88 chi3-input bits; best-case saving <= 0.18 bit, likely 0 (MAP 3.5/3.7). Reaches round 2 only.
- **Internal differential (ZHL2023 period-32).** The only SUB-BIRTHDAY technique we have: 2^105 at r = 5. Dies at r = 6:
  2^172 (169.5 best branch), the 4th chi's 16-bit branching becomes a 2^-16 filter and 120 of 160 S-boxes are impossible
  for the reduced first block; min k5 = 141, pre-6th-chi rank 118 (MAP 3.1/3.2). Deepest useful round = 5.
- **Connector + trail (Guo-Liu-Song-Tu, SHAKE route).** On SHA3-256 only a 2-round connector fits (5 DF vs 27), opening
  38+116+52 = 206 conditions -> 2^206 (2^197 with 8.8-bit early abort); a 3-round connector is short >= 33 DF; best
  4-round trail floors ~2^132 (MAP 3.3). Not competitive with the birthday at r = 6; r <= 5 not computed for SHA3-256.
- **Generic birthday.** 256-bit output -> ~2^128 r-round permutations + table overhead, ~128 natural units at every r.
  The board 124.046 (and promoted 124.27) are already cheap-step birthdays (the leader's route), which the FES route beats.

## 5. What the grid reveals (the owner's "door at round 3 or 4" question)
- There is **no new sub-birthday door at r = 3 or 4** from our techniques. FES works there (tested) but is birthday-level
  (~123.4-123.8 natural units = 2^128 candidates with cheap steps); it cannot drop below the birthday because the
  low-degree property cuts the per-candidate COST, not the NUMBER of candidates. At r <= 5 the internal differential
  (2^105) already beats it, using structure to collide below the birthday.
- The **one open door is r = 6**, and it is the FES route (untried by all 84 submissions). The grid confirms r6 is its
  unique sweet spot: r <= 5 is dominated by the internal differential, r7 is killed by the degree-16 setup (2^136).
- The real frontier the grid exposes (NOT tested here; out of this budget): a **sub-birthday technique at r = 6**. The
  internal differential's sub-birthday mechanism stops at r = 5; the FES route only ties the birthday at r = 6. MAP
  section 4's open lead -- a 3-round structure with NON-IDENTITY chi1/chi2 transitions carrying a sparse 6-bit pattern
  into the theta3 kernel -- is the untried candidate to push sub-birthday reach to r = 6. It needs a SAT/subspace search.

## 6. Verdict
**ALIVE.** The low-degree FES route is a concrete, tested route with exact numbers that beats a known cost: 123.18242 in
r6 units vs board 124.04565 (COMPUTED, re-validated to D19's exact numerator). The reach-by-round table is now priced and
tested at every depth r = 3..7: FES confirmed end-to-end at r = 3,4,5,6 (0 mismatches, all digests match, degree tight),
degree-16 confirmed at r = 7 for the first time, and every competing technique placed with a number. The route's door is
specifically r = 6; r <= 5 is dominated by the internal differential (2^105 at r5) and r = 7 by the degree-16 setup (2^136).

## Files
- `reach.csv` -- the table (technique, round, works, cost, label, source).
- `ledger_by_round.py` / `out_ledger.txt` -- exact per-round D19-style ledger, validated against D19 r6.
- `test_fes_by_round.py` / `out_test_fes.txt` -- per-round end-to-end FES tests and degree confirmations.
- `gen_csv.py` -- emits reach.csv.

## Not done / risks
- Other-technique r3/r4 costs are GUESS (<= their r5 line); only r5/r6 have cited numbers in the MAP.
- The FES route inherits D19's open H_coset premise (whole-coset enumeration treated as IID 256-bit) and the 140-bit
  stand-in key; memory is 2^136 bytes (free in the model, declared).
- r7 FES was priced with D19's Moebius init (P_16 evals); the naive 3^40 init is infeasible and was not run.
- No r5/r7 board numbers were in the named files, so "beats generic ~128" at those depths is vs the generic baseline,
  not vs a known submission.
