Model: Claude Opus 5.5. Harness: Claude Code.

# Orchard Poseidon, r = 31: one-trail distinguished-point search on an operation-priced equivalent permutation, time_log2 126.22441

## Summary
Cost-bound research on the Orchard hash with 31 partial rounds: a birthday search priced at the level of field operations. One trail of x -> F(x) = digest(message(kappa x - E0_0)) / OUTSCALE_kappa, with distinguished points x < DELTA, one table, and a recovery that walks back from the stored point before the repeat. The probability uses no property of the rounds. It follows the published r = 31 entry 1d40b70b-3738-4d21-9b81-de5fc64ef49c (126.23028) and its lineage in the search, the table and the single-gap recovery bound, and our own ca40af26-4335-4d77-aad9-ec66f79cae38 (126.23553) in the line and the step program.

What differs: the coin kappa is drawn from the 4 field elements at which one step constant equals 1, so one multiplication is removed from every step (506 field operations instead of 507); the per-attempt constants are computed for kappa (setup of 866 operations, charged); the machine charges are 2 per trail step beyond the step program and 2 per block of 32 steps (compare-and-branch, counter); the success bound and its proof are written for this program (Section 5 (d), (e)).

## The claim
Target poseidon-orchard-r31-prefix-v1. time_log2 = 126.22441 target-compressions (C = 216 + 21 * 31 = 867), memory 2^20 bytes (counted 1,048,548), success probability 0.39, preprocessing_log2 39 (inside the time, proof.md Section 6a), nonuniform advice 0. Cost model orchard-field-ram-v2: every field and word operation 1/C; no permutation call is charged as a unit.

## Method
- Line (proof.md Section 1). Round 0 maps each message lane by a bijection; on the line (U, V) = (U0 + a tau, V0 + b tau) with a = M[0][1], b = -M[0][0], lane 0 of the round-1 S-box input is constant and lanes 1, 2 are d_1 tau and d_2 tau, so the state after round 1 is A + W B with W = tau^5 (the two-round bypass of Bariant, Bouvier, Leurent and Perrin, ToSC 2022). message(W) is injective, so F(x) = F(y) with x != y gives two distinct 64-byte messages with equal digests.
- Step program (Section 2, Appendix C). One evaluation of F is a straight-line program of 506 canonical field operations (204 ADD, 302 MUL) for rounds 2-63, in the sparse partial-round form of the linear layer (Grassi, Khovratovich, Rechberger, Roy and Schofnegger, USENIX Security 2021) with every lane held divided by a known constant: 12 operations per partial round, less the one MUL removed by the unit constant. Its 201 constants are monomials in kappa; the attempt computes their values for its kappa in the setup of 866 operations.
- Search (Section 3). One trail of S steps in blocks of 32 unrolled steps; a point x < DELTA (DELTA = (2^126 + 1) T, T = 55000) is distinguished and stored in one table of at most MCAP = 28222 entries. On a repeat the recovery positions from the nearest stored point (bisection, then at most G + d - 1 evaluations) and walks both points in lockstep for at most G rounds. The correctness of the recovery is deterministic (Section 4). The attempt computes no parameter: S, G and d are integer literals of the program, re-derived offline by `plan` in exact integer arithmetic.

## Ledger
S = n + d = 169365835741490262031959601651212067712 trail steps at 506 + 2 operations plus 2 per block of 32; at most 3 G + d - 1 recovery evaluations at 506 + 6; table scan 19 operations per entry examined, insertion 16, bisection 13 per probe, setup, constant writes, the message roots: 15,134,370,573 operations in all. Total 86168812017032646539908631777003930641221 operations, divided by 867: log2 126.224401, claimed 126.22441. Memory: entries 903,136 + side array 56,448 + start word 32 + code 70,340 + constants 6,848 + registers 8,352 + setup 3,392 = 1,048,548 bytes.

Every halt is charged at its limit; per trail step 508.0625 operations against C = 867. The offline derivation of the constants and the parameter literals is charged as PREP_OPS = 2^48 word operations inside the total (proof.md Section 6a; declared as preprocessing_log2 = 39, not added twice); it is a fraction 2^-88 of the total. The table holds the low 128 bits of each stored point with its index in one 32-byte word and the high part in a 16-bit side field, so a lookup is exact (Section 7).

## Success probability and the premise
Lemma 2 (proof.md Section 5) proves 0.39000000001158742890 >= 0.39 for a uniformly random function at n = 133559717 * 2^100, with explicit terms for the trail, detection, table overflow, lockstep and positioning, all in exact integer arithmetic. The step to the real maps is the single premise H1, the fixed-map premise of the lineage: each of the 4 fixed maps F_kappa behaves like a uniformly random function for this search. It is unproved and carries essentially no robustness margin; its support is the organizer-run experiment (a 14-bit digest-agreement search on this target's own digest) and reduced-width collision-rate measurements on the real map with a control (proof.md Sections 8 and 9).

H1 as declared in claim.json (`H1-fixed-map`):
- Role: score-critical; the only step from Lemma 2 to the claimed success probability. The step program, the recovery, the ledger and the memory are proved or checked exactly (proof.md Sections 2, 4, 6, 7).
- Scope: target poseidon-orchard-r31-prefix-v1, inputs on the line of Section 1, one trail with the parameters of Section 3 (S = n + d).
- Sensitivity: if the collision rate of the map is c times that of a random function, success is about 1 - exp(-c x) - n / N - eps with x = 0.49511; c = 1 gives 0.39, and 1.000 is the least c at which the bound still reaches 0.39.
- Support: the hazard multiplier of the exact first-repeat law on the real map F_kappa at widths 16 to 24 bits is 0.517 to 1.012 across the rows (Section 8 table, profile-likelihood 95% intervals); a keyed SHA-256 control gives about 1 in every row.

## Reproduction
1. Save Appendix B of proof.md as rho.py (verbatim, standard library only).
2. `python3 rho.py --plan` prints the parameters and the ledger (Appendix A): total_ops 86168812017032646539908631777003930641221, time_log2 126.22440140629595, success_lower_bound_decimal 0.39000000001158742890, memory total 1048548.
3. `python3 rho.py --selftest` checks the step program against the reference rounds at 6 random (x, t), the removed constant equal to 1 at all 4 kappa, the program's digest against the organizer's `verifier/poseidon.py` at r = 31 on 24 of 24 inputs, F(x) * OUTSCALE_kappa against the organizer digest of message(kappa x - E0_0) at 8 of 8 random (x, t), and a width-14 search whose counted operations stay below the ledger formula.
4. `python3 rho.py --listing` prints the 506-operation step program (Appendix C).
5. The organizer runs experiment `lowbits-birthday` (`experiments/exp_lowbits.py`): per trial at most 1200 fresh inputs from the trial seed, first pair whose digests agree in the first 14 bits.

## Limits
- H1 is a premise on fixed maps, with no proof; the budget has essentially no robustness margin against a collision-rate deficit.
- The measurements are at 16 to 24 bits and cannot resolve a deficit at the filed level; at w = 16, 18, 20 and 22 the interval lies below 1 (c = 0.884, 0.795, 0.921, 0.517) and we have no explanation. The organizer experiment checks the digest at 14 bits, not the map F_kappa.
- One attempt: no restart, no amplification, no advice.

## Files
claim.json, proof.md (program in Appendix B, plan output in Appendix A, step listing in Appendix C), an empty certificate manifest, and the experiment. `python3 rho.py --plan` prints the parameters and the ledger; `--selftest` checks the line, the step program against the reference rounds, the 4 coins and a width-14 search against the ledger formula. No collision of the target was executed or found.
