# U11 CARD - What a collision means here (bijection + truncation)

Written 2026-10-12 by learner U11. Folder `./research/poseidon/levels/U11`. Learning only: no attack score is estimated anywhere. Labels: **OBSERVED** (measured; script named), **PROVED** (short argument), **DERIVED** (follows, not fully written), **GUESS**. Real target = `orchard\impl\poseidon_ref.py` (validated 11/11). Toys = same structure over F_q, gcd(5,q-1)=1, random Cauchy MDS (all minors nonzero), random constants, init [nk, rho, 2^65 mod q], all q^2 inputs enumerated.

| script (this folder) | what | output |
|---|---|---|
| `toy_u11.py q seed r` | full-state injectivity, fibres, pairs equal in lane 0 at every level, joint with the final level | `toy_u11_output.txt` (q=257 r=1,2; 769 r=1; 1009 r=1,2) |
| `toy_pairs.py q seed r R3` | every pair equal in lane 0 after R3.M followed through later levels: weights, direction, agreement | stdout in section 5 (q=257 r=1,2) |
| `toy_chain.py` | pairs equal at R3, R3&R4, R3&R4&R5 (&R6), then with R63; 5 (q,seed) x r=1,2,3 | stdout in section 4 |
| `toy_gcd5.py` | what X1 needs: toys with gcd(5,q-1)=5 | `toy_gcd5_output.txt` |
| `real_diff.py` | real field: weight facts, line degrees of difference polynomials, a real R3-equal pair, structural reductions | `real_diff_output.txt` |
| `free_boundaries.py r max trials` | real field: force lane 0 equal at level L by one univariate root-finding (python-flint) | `free_boundaries_r1_deep*_output.txt`, numbers in section 6 |
| `trail_check.py` | r=2 trail vector, second image | `trail_check_output.txt` |

## 1. The exact definition (question 1)

- [PROVED] A collision of the reduced target (r = 1 or 2) is a pair of **distinct canonical** inputs (nk, rho) != (nk', rho'), all four values in [0,p), whose 32-byte outputs are equal; the output is lane 0 of the final state, canonical little-endian, so equal bytes <=> equal lane-0 integers.
- [PROVED, X1] The whole 3-lane map Pi (init -> R_last.M) is a bijection of F^3 (translation, lanewise x^5 with gcd(5,p-1)=1, invertible M). The init set {s_2 = 2^65} is a plane, so Pi restricted to it is injective: **equal full final state is impossible** for distinct inputs. Also impossible at every intermediate level: the state difference is never the zero vector (zero in all three lanes).
- Required: the two final states agree in lane 0 and differ in (lane 1, lane 2) - differ in at least one of the two lanes, not necessarily both. [OBSERVED toy q=257 r=1] 32814 pairs agree in lanes 0 and 1 (and so differ in lane 2 only), 33126 agree in lanes 0 and 2, 0 pairs agree in all three (random expectation for each 2-lane coincidence 33024). So one of the two other lanes may coincide, never both.
- Lanes 1,2 of the final state are produced by the dead rows 1,2 of the last M (X7); "differing in lanes 1,2" is a statement about states that nobody reads. The live statement is about the three S-box outputs T = S(state after R62.M + c63): the collision is `M_00 dT_0 + M_01 dT_1 + M_02 dT_2 = 0` with dT != 0 [PROVED; dT != 0 because S is lanewise bijective and the pair differs before R63.S].
- [OBSERVED, `toy_gcd5.py`] The exponent condition is what makes X1 true: toys with gcd(5,q-1)=5 lose it at once. q=11: 5 distinct full outputs of 121 (r=1), q=31: 25 of 961, q=41: 61 of 1681, q=211: 1704 of 44521, q=251: 2427 of 63001, while q=257 (gcd 1) has 66049 of 66049. So with the wrong exponent a collision could be a *full-state* collision; on Pallas it cannot.

## 2. Toy fibres (question 2)

- [OBSERVED `toy_u11_output.txt`] q=257 (r=1 and 2, seed 1), q=769 (r=1), q=1009 (r=1 seeds 1,2; r=2): number of distinct 3-lane outputs = q^2 in every run (66049, 591361, 1018081). Distinct elements of one lane-0 fibre therefore always differ in (lane 1, lane 2) jointly. Pairs equal in lanes 0,1,2 = 0 in all runs. Pairs equal in lane 0 and lane 1: 32814 / 296220 / 507352 / 509626, expectation if independent 33024 / 295680 / 509040: random-like.
- [OBSERVED] Fibre sizes (lane 0 over all q^2 inputs): q=257 r=1: min 206 max 304 mean 257 var/mean 1.001; r=2: 202..293, var/mean 0.887 (seed-to-seed spread 0.82-1.17 in the atlas); q=1009: 896..1133 (r=1), 918..1114 (r=2). No empty fibre. Nothing that is not a random function at fibre level (as the atlas already said).
- [PROVED] Level R0.M is exactly flat: every lane-0 value after R0.M has a fibre of size q (a line in (A,B): M00 A + M01 B = const). [OBSERVED] min = max = q for q=257, 769, 1009. Consequence: pairs equal in lane 0 after R0.M number q * C(q,2) = q^2(q-1)/2 versus the random value q(q^2-1)/2, ratio q/(q+1) (observed 0.99612, 0.99870, 0.99901 for 257, 769, 1009 = q/(q+1) exactly). This is the first level that is *not* a random function: the ratio at R1 is 0.99950 (q=257), at R2 0.99994, then 1.000 +- 0.001.

## 3. Pair differences: which can be zero, what it does (question 3)

Let d = state difference of two inputs at a given step.

- [PROVED] **Zero pattern is preserved by C and by S**: C is a translation (d unchanged), S is a bijection on each lane it acts on, so a lane of d is zero before S iff it is zero after S (in full and in partial rounds; in a partial round the untouched lanes keep d by definition). M is the only step that changes the pattern, and obeys the branch number: wt(d) + wt(Md) >= 4 (wt = number of nonzero lanes) [PROVED from all 9 entries and all 2x2 minors nonzero, G3].
- [OBSERVED real, `real_diff_output.txt`] 300 random input pairs, r=1 and r=2: weight of d is 2 at init (lane 2 is the fixed capacity), 3 at every later level, no exception. Pairs differing only in nk or only in rho: weight 1 at init, 3 after R0.M and at every later level.
- Lane-0 difference may be zero as follows [PROVED unless stated]:
  - init and R0.C, R0.S: d_0 = 0 iff nk = nk' (then the pair differs in rho only). Weight at init is 1, so after R0.M the weight is 3 (branch number) - lane 0 is not equal after R0.M for such pairs (d_0 after M = M_01 dB != 0).
  - After R0.M: d = M (dA, dB, 0). Lane 0 equal iff M_00 dA + M_01 dB = 0. Then d_1, d_2 are both nonzero (weight exactly 2, because wt(in)=2 and branch number gives >= 2; weight 1 would need two zero lanes of M(dA,dB,0), i.e. a column of M with a zero entry, none). This is a **line** in the (A,B) plane, i.e. q points per start point and exact.
  - After R1..R3 and later: a hypersurface condition, probability 1/q per random pair [OBSERVED section 5: 0.00389-0.00391 vs 1/q = 0.003891 at q=257].
- What a zero lane-0 difference does to the next S-box:
  - Full round: S acts lanewise; lane 0 passes difference 0 and lanes 1,2 still carry the S-box nonlinearity. Nothing is removed. [OBSERVED real, line degrees: a difference line with d_0 = 0 entering R60 gives lane degrees [5,5,5] after R60.M, not [1,1,1].]
  - Partial round (R4, R5): S acts on lane 0 only. If d_0 = 0 at the round input then w = (s_0 + c)^5 is common to both states, the output difference is the **linear** M (0, d_1, d_2): no nonlinearity at all. [OBSERVED real: difference line s + t d with d_0 = 0 entering R4 has lane degrees [1,1,1] after R4.M, versus [5,5,5] for generic d.]
  - It removes the nonlinearity only in partial rounds, and only for the *input* difference to that round. [PROVED] Whether the lane-0 difference after the round's M is again 0 is a separate linear condition on (d_1,d_2) (next item).
- **Trail vectors** (X6, now with the structure measured): from a lane-0 equal pair at M-output of level k (partial round next), lane-0 equal again after the next M iff (d_1,d_2) is on the direction u = (M_02, -M_01) [PROVED]. [OBSERVED toy q=257 r=1] of the 8485572 pairs equal in lane 0 after R3.M: 33124 are on u, 33124 agree in lane 0 after R4.M, and the two sets coincide (33124 of 33124). The direction (d_2/d_1) of those pairs is uniform: 258 directions, 32440..33406 pairs each, mean 32890.
- [PROVED + OBSERVED, real] Equality in lane 0 at **three consecutive** partial-round outputs is impossible for the actual M: with d_0 = 0 and (d_1,d_2) on u, the next difference is t * M(0,u), which is not along u, and (M M u)_0 = `0x3141e9b5...5747` != 0 (`trail_check_output.txt`). [OBSERVED toy] chain R3&R4&R5 = 0 pairs in all 15 runs (q=257 seeds 1,2,3; q=769; q=1009; r=2 and 3) while R3&R4 stays 33124 / 32777 / 32906 / 295378 / 508881 (expected 33024 / 295680 / 509040). Two consecutive equalities are available, a third is not. For r=2 this means: lane-0 equality at R3.M, R4.M and R5.M cannot all hold. (Equality at R4.M and R5.M without R3.M, or R3.M and R5.M, is not excluded.)

## 4. Pairs agreeing in lane 0 after R3.M versus q^2/q (question 4)

- [OBSERVED] Number of unordered pairs equal in lane 0 after R3.M (rounds R0..R3 are identical for r=1,2,3, so one number per (q,seed)): q=257 seed 1: 8485572 (random expectation N(N-1)/(2q) = 8487168, ratio 0.99981), seed 2: 8481969, seed 3: 8494143; q=769: 227354843 (exp 227377920); q=1009: 513643032 (exp 513621360). All within 0.1% of the random-function value.
- Per level, q=257 (seed 1), ratio against the random expectation: R0 0.99612, R1 0.99950, R2 0.99994, R3 0.99981, R4 1.00086, then 1.0007, 1.0001, 1.0001, 1.0000 (r=1) and R5 0.99981, R60 1.0003, ... R63 0.99958 (r=2). For r=1 versus r=2 the levels R0..R4 are literally the same numbers (same seed, same rounds); afterwards the two targets differ. q=769 r=1: R0 0.99870, R3 0.99990, R4 0.99997, R63 1.00016. q=1009: R0 0.99901, R3 1.00004 (r=2), 0.99998 (r=1).
- [OBSERVED] Joint events (equal at level k and equal at the final level) are independent: q=257 r=1 joint counts 32703 (R0), 32659, 32863, 33069 (R3), 33081 (R4), 32771, 33129, 33269 versus 33024 expected; r=2 32485..33163. q=769: 295900..296098 vs 295680. q=1009: 507955..509518 vs 509040. No level leaves a footprint in the final agreement count.
- Chain R3 & R4 & ... & R63 (equal at all listed levels): r=1: 33124 -> 115 (q=257 seed 1; expectation 128), 32777 -> 146 (seed 2), 32906 -> 125 (seed 3), 295378 -> 357 (q=769, exp 384), 508881 -> 514 (q=1009, exp 504). r=2,3: chain R3&R4&R5 = 0, so the longer chains are empty (section 3).
- [DERIVED] The pairs of inputs form a 4-dimensional space; one equation (lane 0 equal after R3.M) leaves a 3-dimensional set, about q^3/2 unordered pairs: 257^3/2 = 8.49e6, matching the observed 8.49e6.

## 5. A toy pair with equal lane 0 followed through the tail (question 5)

[OBSERVED `toy_pairs.py`, q=257 seed 1, all 8485572 pairs equal after R3.M, r=1 and r=2 identical through R4]:

| level | pairs still equal in lane 0 | fraction (1/q = 0.00389) | weight histogram of d (pairs with 1 / 2 / 3 nonzero lanes) |
|---|---|---|---|
| R3 | 8485572 | 1 | 1: 65836, 2: 8419736 (lane 0 is zero in every one) |
| R4 | 33124 | 0.00390 | 2: 98918, 3: 8386654 (no weight 1: branch number) |
| r=1: R60 | 33102 | 0.00390 | 1: 386, 2: 98744, 3: 8386442 |
| R61 | 33005 | 0.00389 | 1: 388, 2: 98028, 3: 8387156 |
| R62 | 32859 | 0.00387 | 1: 387, 2: 98204, 3: 8386981 |
| R63 | 33069 | 0.00390 | 1: 363, 2: 98656, 3: 8386553 |
| r=2: R5 | 32754 | 0.00386 | 1: 367, 2: 97612, 3: 8387593 |
| R60..R63 | 33050 / 33078 / 33177 / 33163 | 0.00389-0.00391 | weight 1: 364-407 |

- [OBSERVED] After R4 every pair has weight >= 2 (as branch number demands: weight 1 at R3 is possible only when lanes 0 and one other lane agree, weight 2 at R3 gives >= 2 at R4). Weight 3 is the generic case, weight 1 reappears after R60 at about 3 * pairs / q^2 = 385 (observed 363-407): a lane pair coincidence at random rate, nothing structural. Fraction of pairs still equal in lane 0 after each later level = 1/q, i.e. **no conditional memory**: the equal-lane-0 property of R3 gives no head start at R63 (this is the same observation as the independence of the joint counts in section 4).
- [PROVED, real] The set of differences does not stay small: the difference polynomial of a line s + t d grows by x5 per full round (all measured degrees in `real_diff_output.txt`, from the state entering R4.C, one random state, one random direction of each type):

| direction | r=1 degrees (lane0,1,2) after R4, R60, R61, R62, R63 | r=2 after R4, R5, R60, R61, R62, R63 |
|---|---|---|
| generic d | 5, 25, 125, 625, 3125 | 5, 25, 125, 625, 3125, 15625 |
| d_0 = 0, generic | 1, 5, 25, 125, 625 | 1, 5, 25, 125, 625, 3125 |
| d_0 = 0 on trail u | R4 lane 0 degree 0, lanes 1,2 degree 1; then 5, 25, 125, 625 | R4 [0,1,1], R5 [1,1,1] (lane 0 now degree 1: R5's S-box sees nothing), then 5, 25, 125, 625 |

  So a lane-0-equal start removes exactly one factor 5 per transparent partial round (r=1: one, d_0 = 0; r=2 on u: two) from the final degree. A real pair equal after R3.M (found by root finding, section 6) follows the d_0 = 0 row exactly: degrees 1, 5, 25, 125, 625 (r=1) and 1, 5, 25, 125, 625, 3125 (r=2); zero lanes of its difference: lane 2 at init, none at R0, R1, R2, lane 0 at R3, none at R4..R63; final lane 0 differs.

## 6. Structural reductions and level boundaries (question 6)

Reductions that need no attack computation (each re-verified, 200 random real inputs, 0 mismatches, `real_diff_output.txt`):

| id | reduction | status |
|---|---|---|
| X2 | start at M*(A,B,K) instead of R0: hash(nk,rho) = H(A,B), (A,B) = ((nk+c00)^5,(rho+c01)^5) bijective | OBSERVED 200/200 |
| X5 | partial-round constants of lanes 1,2 carried into the next round: effective R60 constants (r=1) listed in output | OBSERVED 200/200 |
| X7 | output = row 0 of the last M applied to three fifth powers; rows 1,2 dead | OBSERVED 200/200 |
| R0 lane 2 | S-box output is the constant K | OBSERVED 200/200 |
| X1 | all rounds bijective | PROVED + toy |

Which level boundaries are **free**, i.e. can be forced to have equal lane 0 by a single root-finding and no search:

- [PROVED] boundary after R0.M: a line (linear equation in (A,B), fifth roots to return to (nk,rho)).
- [OBSERVED real, `free_boundaries.py`, r=1] For a fixed first input and a free A' = (nk'+c00)^5, the lane-0 value after level L is a polynomial in t = B' = (rho'+c01)^5 of degree 5^L (R1: 5, R2: 25, R3: 125, R4: 625, then 3125 at R60). Equal lane 0 at that level <=> t is a root of poly - target. Number of roots found by gcd(t^p - t, poly): R1 over 20 trials [3,1,1,1,1,0,1,0,1,0,0,3,0,1,1,0,0,1,2,0] (mean 0.9), R2 over 20 trials mean 1.1, R3 over 10 trials mean 0.8, R4 [0,0,1], R60 [1,0,0], R61 (degree 15625) [1,0]. All found roots were turned back into (nk',rho') and the lane 0 after the level checked equal with the first input (and the pair distinct): every root verified. Time per trial: R1-R2 < 0.1 s, R3 0.18 s, R4 1.13 s, R60 13.6 s (degree 3125), R61 64.4 s (degree 15625). So lane-0-equal pairs at R1, R2, R3, R4, R60 are "free" in the sense of one root-finding with a number of roots Poisson(about 1)-like. R62 (degree 78125) was started as one trial; see the addendum at the end of this card.
- Not free: demanding equality at a level *and* at the next (probability 1/q per level for random pairs); equal at R3&R4 needs the trail direction (section 3); equal at three consecutive partial rounds is impossible.
- Backward side [PROVED, X7]: at the output y is a linear equation in (T_0,T_1,T_2) with M_00,M_01,M_02 all nonzero; the final-boundary "collision" reduces to two T-triples with M_0 . dT = 0. Entry from the end costs fifth roots, not a search.
- What is *not* a reduction: the dense block R1..R3 and the 4-round tail have no cancellation (dense MDS, no weight loss measured), only the partial block is transparent to d_0 = 0.

## 7. The five most surprising / useful observations

1. A pair with equal lane 0 at level L can be built exactly by a single univariate root-finding of degree 5^L in the variable B' (A' free), and the real-field runs found roots at R1, R2, R3, R4, R60, R61 (R60: degree 3125 in 14 s per trial; R61: degree 15625 in 64 s); the number of roots is about 1 on average, as for a random polynomial. This means "equal lane 0 at level L" is a cheap boundary all the way to R60 and, as a statement about levels, the whole target is a single polynomial in one variable of degree 5^8 (r=1) / 5^9 (r=2) after fixing A' (DERIVED); how far the root-finding stays practical is the open question (time against degree: 625 -> 1.13 s, 3125 -> 13.6 s, 15625 -> 64.4 s, i.e. local slope about 1.5 then 1.0; 1-3 trials each).
2. The partial-round transparency has a hard limit: equal lane 0 after R3.M, R4.M and R5.M cannot hold together (0 pairs in 15 toy runs; PROVED for the real M since (M M u)_0 != 0), while two in a row are available on the single direction u; the direction of R3-equal pairs is uniform.
3. The zero pattern of a difference is exactly preserved by C and S, so the only place where "which lanes agree" can change is M, with the branch number 4: weight-1 and weight-2 differences are very constrained and weight 3 is generic. For a lane-0 collision the weight before R63.S must be >= 2 (PROVED) - at most one of three S-boxes of R63 may be inactive.
4. Equal lane 0 at one level gives no head start at later levels: conditional agreement rate = 1/q at every later level, joint counts with the final level are independent (levels carry no memory), except the exact relation R3&R4 on the trail direction. The only exact non-random level is R0 (fibre size exactly q, ratio q/(q+1)).
5. The exponent condition matters: with gcd(5,q-1)=5 the full state itself collides massively (q=211: 1704 distinct of 44521), with gcd 1 never; and even with gcd 1 the pair (lane 0, lane 1) collides at the random rate (32814 pairs at q=257), only the triple never.

## 8. Questions this raised

- How large is the degree range over which the root-finding of item 1 stays practical, and how does time scale (flint gcd(t^p - t, f) is quasi-linear in degree times log p; measure R61, R62 and r=2 R5, R60)? Which of these facts is already known to the team?
- Given a root-finding per level, what is the structure of the *set of roots over varying A'*: is the root count really Poisson(1) (R1 x100 trials, a distribution test) or does the symmetry of the Cauchy-structured polynomial change it?
- Can the "two consecutive equalities" (R3&R4) be combined with the free boundary (R4 equality needs only a trail-direction condition after R3.M): count the real solutions by solving the two equations jointly (two curves intersect in finitely many points)?
- For r=2: equality at R4.M and R5.M (without R3.M) needs d' on u, i.e. a codim-2 condition at R4: does an exact parametrisation exist?
- Does the weight >= 2 requirement at R63.S (and branch-number accounting for R60..R62) give a lower bound on the number of active S-boxes in the tail that is useful as a level map (analogue of SHA-256 active-row counts)? A tabulation of minimal active S-boxes per round for the four full rounds ending in a lane-0 zero is cheap and has not been done.
- Toy gap: the full-triangle supports and the exact line-degree statements are real-field only; for q=1000003 (gcd ok) no sampling run was made in this unit.

## 9. Dull things and null results (kept on purpose)

- `toy_u11.py` prints `-1` in the cumulative-chain column after the fifth level: the chain code is limited to the first five levels (int64 safety); it is not a result. Use `toy_chain.py` for chains.
- No toy run found a pair equal in lane 0,1,2 at the end (all runs listed in `toy_u11_output.txt` and `toy_chain.py`).
- Weight 1 never occurs for pairs equal at R3 after R4 (observed 0 in 8.5M pairs); weight 0 never occurs at any level in any run.
- Fibre variance/mean for r=2 q=257 seed 1 is 0.887 (lower than the atlas spread 0.93-1.08 for other seeds): seed-to-seed noise, not read as structure.
- The trail vector u and (M M u)_0 are in `trail_check_output.txt`; the nine weight-2-stays-weight-2 directions of M (3 supports x 3 output lanes) are in `real_diff_output.txt` section 1.
- q=4099 and 12289 toys were not run in this unit (memory for 16.8M x 10 levels); q=1000003 not sampled.
- No collision of the real hash is reported here; pairs found are equal only at the named intermediate level, never at the final output (final lane 0 verified different).

## Addendum - R62 not finished

The r=1 run at R62 (degree 78125, one trial) was started and had not returned when this card was closed; the process was stopped by its owner (U11). No R62, R63 or r=2 root-finding result exists. Measured: R60 and R61 only (section 6). Re-run `python free_boundaries.py 1 63 62:1,0:0,1:0,2:0,3:0,4:0,60:0,61:0,63:0` (expected several minutes at the 64 s per 15625 degree seen at R61) and `python free_boundaries.py 2 63 5:3,60:2` for r=2.
