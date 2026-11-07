# split_e3: fix E3 by construction, then search E1 (2026-10-09)

**Question:** does fixing E3's inputs by construction (Y4, Y9, Y14, w8; Y3 and column 3 are already pins) and then moving free words to search E1 beat 63.6027?
**Verdict: DOES NOT BEAT.** The best version we could build prices at about 84.6. Even if each candidate cost one operation, it would still be 79.2, about 15.6 bits worse than 63.6. Confidence is high inside the word model. One lever is not ruled out: a non-exhaustive solver for one fully coupled 32-bit ARX loop of 21 equations. It would have to cost under 2^16.4 operations per solve to change the verdict.

Scripts and outputs are all in this folder. COMPUTED = run here. DERIVED = arithmetic on computed or ledger numbers. GUESS = not established.

## 1. Pair table and today's 63.6
**Probabilities (COMPUTED, pairsum.py).**
- Sum over pairs of W15: **2^-54.592**. This is Pr[side 3 (E3) lands on ANY of the 317 contributing (t,s)].
- Sum of P1avg over the 453 pairs: **2^-40.152**. This is Pr[side 1 (E1) lands on ANY of the 453 (t,s)].
- Joint, the sum of W*P1avg: **2^-100.534** for C15 and 2^-100.726 for C13.
- The product of the two marginals would be 2^-94.74. The joint is smaller because both sides must land on the SAME pair.

**What fixing E3 changes (COMPUTED from the table, DERIVED via R1 of REPORT.md).**
- Once E3 is fixed, its (t*,s*) is fixed, and the per-trial E1 probability is P1(t*,s*).
- That is **at most 2^-44.00**, at the best pair 189060a0/6e203e55 with beta* = 18b1a098. The P3-weighted mean is 2^-45.94.
- So the claim's 2^-40.2 overstates the per-trial E1 probability of this design by at least 3.8 bits.

**How 63.6 arises (DERIVED, from the CK2/CM ledgers that sol_answer_STACK.md points to).**
- Members: K = 2^50.117 contexts × 2^19 class members (Y4 walks C13) = 2^69.117. Work N = 2^72.351 units, 9.41 units per member, and N/430 = 2^63.603.
- Success needs λ = 0.497, so 2^-70.13 per member.
- Each member is one outer step whose h1 (Y14 ↔ w0 ↔ T0) is swept over all 2^32 values by the direct tables. At the C13 joint rate, that is 2^32 × 2^-100.73 = 2^-68.73 per member. The ledger needs 2^-70.13, so 1.40 bits are slack or losses. GUESS on where those 1.40 bits go.
- Class concentration: the 2^-100.7 is already conditional on e1 in the class, and the class costs nothing because Y4 is a basis word that is walked.
- Net effect: the front line pays about **2^27.4 units per E1 trial**, where an E1 trial is a point with E3 satisfied. Every one of those trials sees the P3-weighted E1 rate of 2^-46.0.
- **Bar for this design (DERIVED):** with the best pair (2^-44, about 2^42.98 trials for success 0.39), an E1 trial must cost under **2^29.37 ops** to beat 63.6027.

## 2. k when E3 is fixed (census word model, peeling as in DIRECT/MITM)
**Counter 1, T1 = 0, as in the front line (COMPUTED, kmin.py, kseq.py).**
- Outer system with F = {Y4,Y9,w8}, and full system with F = {Y4,Y9,w8,Y14}: least **k = 2**.
- Over 2,922 + 66 + 3 distinct minimal guess sets (k = 2/3/4), none can be solved one word at a time. Every check needs both solved words, so each step is a coupled 64-bit system.
- Cross-check: with F = {Y4,Y9} or {Y4,w8} alone, k = 1 and a one-word order exists, matching DIRECT.md.

**Counter 2, T1 = v13 free (COMPUTED, kmin2.py, loopw.py, design.py).**
- k = 1 with a one-word order: 881 sets and 3,234 designs.
- T1 depends on the solved word in every design, so it can only be filtered after the solve. P(T1 in [1,2^19)) = 2^-12.95 (V13E1, measured).
- Keeping T1 fixed brings back k = 2 with no one-word order.
- The shortest cyclic loop has 21 equations (g = C0.b1, check Y9 = C1.c1 + Y13), costing 43 ops per candidate with native rotations.

**Can the solve be avoided or cut down? No (COMPUTED).**
- **Loop words:** in all 3,234 designs, the check reads every one of the 6 free words and g. No word can move without a re-solve (loopw.py).
- **Bit moves:** 0 of 19,200 single-bit flips and 0 of 19,200 adjacent-pair flips of free words keep the check (bitmoves.py, 100 real points).
- **List match:** the check never splits into two groups (sep.py). In all 19,404 (design, u) combinations, the separate closures from g and from u leave at least 30 linking equations (mitm2.py).
- **Bit-serial solving:** every one of the 32 check bits reads all 32 bits of g (cone.py, BITS.md method). A guess-and-determine solver therefore cannot prune before all 32 bits are fixed, which means 2^32 leaves.

**Solving on real steps (COMPUTED; GPU exhaustive solve, gen.py, solve.cu, check.py, check_2_out.txt).**
- **Setup:** 8 E3 tuples (Y4, Y9, w8, Y14) taken from real points × 2,048 fresh draws of the 6 free words. Every draw is a full 2^32 sweep of g.
- **Roots per target:** mean 1.006, P(0) = 0.368, histogram 6026/5977/3053/997/269/50/9/3. This is Poisson(1).
- **Control:** the generating g was among the roots in 8 of 8 control instances.
- **Verification:** all 16,475 roots were rebuilt and verified on the real 2-round compression (compress2, counter T0 + 2^32·T1, flags 3). E3 inputs equal the forced ones, digest words 0/2/5/7 are zero, Y3/Y11 are the pins, the e1 class and eta hold. 0 failures.
- **T1 filter:** 5 roots have T1 in [1,2^19). Those are 5 real E3-fixed steps with a valid counter (expected 2.1 at 2^-12.95; T1 is uniform: below 2^28 = 2^-3.96, below 2^24 = 2^-7.74).
- **Cost per solve:** 2^32 × 43 = 2^37.43 ops, about 0.021 s on the 3090 (344.9 s for 16,392 sweeps).

## 3. Free moves and the E1 key with E3 held
**Degrees of freedom (COMPUTED).**
- Counter 1: 9 words, so 5 remain after E3 (160 bits). Counter 2: 10 words, so 6 remain, and T1 then costs 13 bits.
- The claimed ~267 free bits do not appear.
- E0/E2 inputs are not independent variables. Digest words 0, 2, 5 and 7 stay zero on every verified root.
- T0 is fixed by Y14, so it cannot absorb anything.
- Moves that keep E3 without a re-solve: **0** (section 2).

**E1 variation (COMPUTED, e1stat.py, e1stat_2_out.txt).**
- All 16,475 E3-held roots have distinct E1 tuples.
- Side-1 event rates match uniform E1 inputs (2^24 samples) within |z| <= 1.4:
  - beta = beta*: 10 observed against 8.2 expected;
  - beta in the 453-pair set: 75 against 76.1;
  - s low 8 bits: 207 against 188;
  - t low 12 bits: 275 against 264.
- Pooled bit chi2/dof is 1.39. This is explained by roots of one draw sharing w5 and w12, which do not depend on g, so the samples are not independent.
- **Conclusion:** no bias was detected, so the per-move probability is the table's P1(t*,s*) <= 2^-44, not 2^-40.2.

## 4. Agreement with MITM.md section 3 and DIRECT.md
**What they already showed.**
- MITM section 3 ("fixing only E3's triple: no closure with 4 extra words"; deps5 "E3 fixed + 5 basis -> NOT solved") already shows there is no triangular way to hold E3. This is the failure point.
- DIRECT covers {Y4,Y9} and {Y4,w8} (k = 1 each) and T1 as a filter. It never covers the triple {Y4,Y9,w8}, and it never solved or priced a cyclic equation ("no solver for the cyclic equation", V13E1 item 8).

**What this note adds.**
- k = 2 with no one-word order (counter 1), or k = 1 with a 21-equation loop plus the T1 filter (counter 2).
- No loop word, no list match and a full bit cone, so each E1 trial needs at least one exhaustive 2^32 solve times 2^12.95.

## 5. Price of the best buildable design (DERIVED)
**Design: counter 2, construct E3 once, then per E1 trial:**
- draw the 6 free words;
- solve the 21-equation loop over 2^32 g (about 1 root per draw);
- keep the root if T1 is in [1,2^19) (2^-12.95);
- test E1.

**Price.**
- Trials: 2^42.98 at P1 = 2^-44, giving success 0.39.
- Per trial: 2^12.95 × 2^32 × 43 = 2^50.38 ops.
- Total: 2^93.36 ops, which is **84.61** in log2(compressions). At an impossible 1 op per candidate it is 79.19.
- One-time E3 construction: a bit-serial DP solve of one G for (t*,s*), negligible (DERIVED). Even 2^60 G evaluations would be 2^55.6, still negligible.
- Counter 1 is worse: at least 2^64 candidates per trial.
- **Needed to beat 63.6:** a solve under 2^16.4 ops for a 21-step fully coupled 32-bit loop, which no tested method gives.

## Not done
- No SAT or algebraic solver timing for the 32-bit loop. BITS.md saw SAT fail on the 128-bit version.
- No exact count in the ctr_count machine (rotation = 5 units would make it worse).
- Other Δe1 classes outside C13/C15 were not searched for a larger P1. GUESS: this would not recover 15 bits.
