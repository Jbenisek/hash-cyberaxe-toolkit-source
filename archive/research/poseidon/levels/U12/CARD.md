# CARD U12 - r=1 versus r=2, and how the levels hand over to each other

Learner U12, 2026-10-12. Folder `./research/poseidon/levels/U12`. Learning only; no attack score is estimated anywhere. Labels: OBSERVED (a command was run, named), PROVED (short argument written out), DERIVED (follows from labelled facts, check before relying), GUESS (nothing run).

Scripts (single process each, exact arithmetic, implementation `orchard\impl\poseidon_ref.py`, constants as data):

| script | what | output |
|---|---|---|
| `u12_real.py` | questions 1-5 on the real field p (about 6 s) | `u12_real_output.txt` |
| `u12_toy.py` | toy fields, exhaustive: injectivity, plane, trail pairs, Jacobian rank, collision overlap, drop directions | `u12_toy_output.txt` |
| `u12_balance.py` | fibre balance of 1..4 partial rounds (toy exhaustive) and the same condition on the real field | `u12_balance_output.txt` |
| `u12_fdbig.py` | exact output degree by finite differences (r=1: 5^8 in (A,B) line, r=2: 5^9 in (A,B) line) | `u12_fdbig_output.txt` |

Toys: q in {11,31,41 (gcd(5,q-1)=5, the control), 23,29,37,103,257}, Cauchy MDS and constants drawn at random with recorded seeds, capacity 2^65 mod q, same schedule shape (R0-R3 full, r partial, R60-R63 full). `gcd(5,q-1)=1` holds for 23,29,37,103,257 (q-1 = 22,28,36,102,256). q=1,000,003 also satisfies it (1000002 = 2*3*166667, not divisible by 5) but was not needed here.

## 1. What r=2 is, exactly

- [OBSERVED `u12_real.py` section 1] Schedules: r=1 `[0,1,2,3,4,60,61,62,63]`, r=2 `[0,1,2,3,4,5,60,61,62,63]`. With Phi = R0..R4 and Psi = R60..R63 (full 3-lane maps): hash_r=1 = lane0 of Psi(Phi(x)); hash_r=2 = lane0 of Psi(R5(Phi(x))). 300 random inputs, 0 failures for both. R0..R4 and R60..R63 are literally the same functions in both targets (prefix and suffix of the schedules are equal; the constants are the same table rows).
- [OBSERVED, 600 checks, 0 failures] On full 3-lane states: **G2 = Psi o R5 o Psi^-1 o G1**. So r=2 is r=1 with the partial round R5 *conjugated by the tail*. [PROVED] since Psi is a bijection (every round is). Used as a view: the r=2 target is the r=1 target followed by a bijection that acts non-linearly on one linear combination of the three final lanes.
- [OBSERVED `u12_toy.py` T5, q=103, 3 seeds] Lane-0 collision pairs of r=1 and r=2 (about 546,000 each of 56,206,000 pairs): in both = 5319 / 5381 / 5145 against independent-random expectation 5322 / 5293 / 5315. **The two targets' collision sets are statistically independent**; also the pairs that already collide in lane 0 after R4.M show no enrichment at either output (5330, 5147, 5350 for r=1; 5353, 5236, 5222 for r=2; expectation about 5310). Adding R5 re-randomises *which* pairs collide, it does not just move a few.
- Null result recorded: no relation between the two hash values at one input was looked for beyond this (they differ at random inputs: OBSERVED).

## 2. Degrees: 5^9 versus 5^10 (question 2)

- [OBSERVED `u12_real.py` section 2] Leading-form tracker (exact, evaluates the top homogeneous part of every lane along nk = a + u t, rho = b + v t; no cancellation reported for 32 directions per r including both axes u=0 and v=0). Lane degrees after each round, all three lanes equal from R0.M on: r=1: 5, 25, 125, 625, 3125 (after R4), 15625 (R60), 78125, 390625, 1953125 = 5^9 (R63). r=2: 5, 25, 125, 625, 3125 (R4), 15625 (R5), 78125 (R60), 390625, 1953125, 9765625 = 5^10 (R63). Ratio r=2 / r=1 at R60, R61, R62, R63 = 5, 5, 5, 5; ratio R5 / R4 = 5 within r=2. The ratio is exactly the one extra lane-0 S-box and nothing else. Because the tracker evaluates the top form exactly, a nonzero value at one point **proves** the degree (PROVED for these lines: the leading coefficient of the output along the line is a nonzero field element, so the total degree is at least, hence equal to, 5^9 / 5^10).
- [PROVED] Every other round already multiplies the degree by 5 (full) or by 5 for the lane-0 S-box and then through the dense M to all three lanes (partial); an extra partial round is therefore exactly x5. So the output degree is 5^(8+r) in (nk,rho) (4 full + r partial + 4 full rounds, one factor 5 each, lane-0 S-box per partial round); the tracker confirms r=1,2 only (r>=3 DERIVED).
- [OBSERVED, exact, independent of the tracker] Finite-difference degrees on an (A,B)-line (A = a0 + alpha t, B = b0 + beta t, with nk,rho obtained by 5th roots) give the exact degree in t of all three lanes after each prefix: R0: 1, R0-R1: 5, R0-R2: 25, R0-R3: 125, R0-R4: 625, R0-R4+R60: 3125, R0-R5: 3125; in every case Delta^(d+1) = 0 for all three lanes and Delta^d is nonzero for all three lanes. This is the "one level lower" degree of X2 and shows R4 (partial) and R5 (partial) each cost exactly x5. For the final outputs see section 9 (finite differences up to 5^8 / 5^9).
- [OBSERVED] Drop directions (X10) on the real field: for lane i the line with (u/v)^5 = -M_i1/M_i0 loses the top degree after R0 (the tracker reports the cancellation at (R0, lane i)); the *final* degree on that line is still 5^9 / 5^10 for all three lanes and r=1,2 (note: the tracker discards the lower terms of the cancelled lane, which can only matter if every term of a later sum cancelled - none did). [PROVED] consequence: the drop is transient (matches X10).

## 3. Difference trails: dimension 2, 1, 0 (question 3)

Setting: two states entering R4 that agree in lane 0 (d = (0, d1, d2)).

- [PROVED] A partial round with equal lane-0 input has equal w, so the output difference is M(0, d1, d2) (X5, X6). For the *next* partial round to see no difference the output difference must again have lane 0 zero: (M d)_0 = 0, i.e. M01 d1 + M02 d2 = 0. In general d survives k partial rounds unseen iff (M^j d)_0 = 0 for j = 0..k-1: **dimension 3 - k** for k = 1, 2 (here 2, 1) and 0 for k = 3 because det[e0; e0 M; e0 M^2] != 0.
- [OBSERVED real field] Trail vector d = (0, M02, -M01) = `(0, 0x7c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d, 0xe6e99d71a75a544d6c0f0f2779386abfe394e7f49d9a1e50a62db56166954a3)`; (M d)_0 = 0 exactly, (M^2 d)_0 = `0x3141e9b5462006d0906f3d691c47ce59002af987df7adb19c151022db9175747` (nonzero). The determinant printed by `u12_real.py` as "observability det" is, by its code, det[e0 M; e0 M^2; e0 M^3] = `0x1875f9a272a44c8bbdb211e0729fc02ce6cc5f7133f30688f4237a303c9c8bb5` (nonzero; mislabelled in the script output, see section 7 item A); the atlas value for det[e0; e0 M; e0 M^2] is `0xebe164ab9dff92f6f90c296e3b831a7221b9f7429d21e01d7dc2ebf46e8a8ba`, re-derived in section 4. 200 random pairs with equal lane 0 entering R4: output difference == M(0,d1,d2) in 200/200; 200 pairs along t*d: lane 0 equal after R4.M in 200/200; difference after R5.M == M^2 (t d) in 200/200, whose lane 0 is nonzero, so the pair separates in lane 0 at the second partial round's output.
- [OBSERVED toy, exhaustive over **all** q^3 states, q = 23 and 29, 3 seeds each] Ordered pairs of distinct states with equal entry lane 0 **and** equal lane 0 after R4.M: exactly q^3 (q-1) (267,674 for q=23; 682,892 for q=29), matching the algebra (one nonzero multiple of the trail vector per state). Pairs with equal entry lane 0 that are equal after R4 *and* R5: **0**. Generic expectation for pairs of arbitrary entry lane 0 equal after one round: about N^2/q (6.4M for q=23): the trail pairs are a tiny, exactly-countable subset.
- [OBSERVED, new, see section 4] Equal lane 0 after R5 alone for equal-entry pairs is also exactly q^3 (q-1), and for R6 it is not: this is a *balance* phenomenon, not a trail.
- Difference at the entry of R60: r=1: M(0, d1, d2) (a 2-dim subspace); r=2: spanned by M^2 d (`0x3141e9...5747, 0x1978ec4716cec311ad9acbc6bba0b7615ea4860a9a776948c171e57fb91d120e, 0x167d4c4f956a21d64338f74067d8926fd9f9cbba50d43feefa2efa1ce737389f`); [PROVED] since (M d)_0 = 0 the S-box of R5 passes the difference unchanged and (M^2 t d) is the output difference. What the tail does with it was not followed.
- All of this needs the *entry* states to agree in lane 0 at R4; how many (nk,rho) pairs make the R3 outputs agree in lane 0 is a curve-of-pairs question left open (it is the real interface between the dense block and the partial block).

## 4. Balance of the partial block (new, not in the atlas)

- [OBSERVED `u12_balance.py`, toy exhaustive q = 23, 29, 37, 103, 3 seeds each, entry lane 0 in {0, 1, 5}] Fix the entry lane 0 and let (s1, s2) range over all q^2 values. After **one** partial round the lane 0 output takes every value exactly q times ("balanced"); after **two** partial rounds also exactly q times (all 36 cases); after **three** it is not balanced (fibres between about 0.4q and 1.9q at q=103) and after four neither.
- [PROVED + OBSERVED real field] Reason: lane 0 after the 2nd partial round = M00 (y0 + c)^5 + L(s1, s2) with y0 the lane 0 after the first; (y0, L) are two linear forms in (s1, s2) and the map (s1,s2) -> (y0, L) is a linear bijection iff the 2x2 minor of their coefficients is nonzero. That minor is `0xebe164ab9dff92f6f90c296e3b831a7221b9f7429d21e01d7dc2ebf46e8a8ba` on the real field and **equals** the observability determinant det[e0; e0 M; e0 M^2] of the atlas (X6) (OBSERVED equal, script `u12_balance.py`; the 3x3 determinant with the e0 row is that 2x2 minor). The decomposition formula was checked on 200 real states (0 failures).
- So one number controls two things: (i) no trail survives 3 partial rounds, and (ii) lane 0 after r <= 2 partial rounds is a uniform function of the free pair (s1, s2) for each fixed s0. [DERIVED] with r=3 a third S-box acts on a lane 0 that is now a non-linear function of (s1,s2), and balance is lost. This is exactly where r=1 and r=2 are "linear-ish" and r>=3 is not; it holds only when (s1, s2) are free, which they are not in the real hash (they lie on the 2-dim surface after R3). Whether the surface inherits any of it is not looked at.

## 5. The hand-off ladder, each arrow with a command (question 4)

| arrow | statement | label and command |
|---|---|---|
| init -> R0.C,S | plane {s2 = 2^65}, 2 free dims; lane 0 only nk, lane 1 only rho | PROVED by definition |
| R0.S -> R0.M = P0 | state = M (A, B, K)^T, (A,B) free; (M^-1 s)_2 = K | OBSERVED 200 real inputs 0 failures (`u12_real.py` s4); OBSERVED **all** q^2 inputs for q = 23, 29, 103, 257 (plane holds for q^2 of q^2, (A,B) distinct for q^2 of q^2, H(A,B) == hash for r=1,2) (`u12_toy.py` T2) |
| P0 -> R1 -> R2 -> R3 | 2-dim surface; (A,B)-line degree 1 -> 5 -> 25 -> 125 | OBSERVED exact by finite differences, `u12_real.py` s4 |
| R3 -> R4 | state = M (w, s1 + c, s2 + c); w = (s0 + c)^5; degree 625 -> 3125 | OBSERVED 1000 real states 0 failures; degree exact |
| R4 -> R5 (r=2) | same form; extra x5 | OBSERVED exact degree 3125 after R0-R5 |
| tail | R60..R63 bijections; y = sum_j M0j T_j | OBSERVED 1000 real inputs 0 failures |
| bijection check | all rounds invertible; inversion needs 5th roots only on S | OBSERVED full-state inversion returns the input 20/20, r=1 and r=2 |

## 6. Which levels invert cheaply, and the 5th-root count (question 5)

- [PROVED] C (translation) and M (matrix, M^-1 is 9 multiplications and 6 additions) are cheap; S (x -> x^5) inverts by x -> x^d, d = 5^-1 mod p-1 (254 bits).
- [OBSERVED] d has 254 bits, Hamming weight 125: plain square-and-multiply = 253 squarings + 124 multiplications. Timing in this Python: one 5th root `pow(x,d,p)` 110 us, one forward hash r=1 89 us (about 25 S-boxes, three multiplications each): **one backward S-box costs about 120 forward S-boxes**; walking back through the whole map costs about 25 x 120 = 3000 forward-S-box-equivalents per state, which is the whole difference in scale between the two directions.
- [OBSERVED, `u12_real.py` s5] 5th roots when inverting round by round (a partial round needs 1, a full round 3): r=1: R0 3 (of which lane 2 is a constant), R1 3, R2 3, R3 3, R4 1, R60..R63 3 each = **25 in total, 22 to get back to the state after R0.M, 24 to reach (nk, rho)** (2 roots for the lanes with variable input, the third root of R0 is wasted on the constant). r=2: **26 in total, 23 to the state after R0.M, 25 to reach (nk,rho)**. The extra root is exactly the extra partial S-box. The same counts hold when starting from the output y with T0, T1 free (T2 solved from the linear form of X7): 22 / 23 roots, forward re-evaluation returns y (OBSERVED, both r).
- [OBSERVED] A random choice of (T0, T1) does not land on a valid hash input: the state obtained after R0.M violates the plane condition (M^-1 s)_2 = K (residual nonzero). [PROVED] the preimage of y is exactly the set of (T0,T1) for which the residual vanishes, one equation on two free parameters (a curve). The backward walk is cheap per point but the final plane condition is the only place where the front block (R0 plane) constrains the search; each probe of it costs the full 22 / 23 roots.
- Forward direction needs no roots: all roots are in the backward direction. The cost of the *meeting point* (forward to R3 or R4, backward from y) was not studied.

## 7. Audit: OBSERVED-on-samples statements upgraded (question 6)

| atlas statement | original label | now |
|---|---|---|
| X1 (full-state bijection, collisions only via the truncation) | PROVED + toy q=257 | OBSERVED exhaustively for q=23, 29, 37, 103, 257 (r=1,2): q^2 distinct 3-lane outputs in every case. Control: for gcd(5,q-1)=5 (q = 11, 31, 41) the map collapses: 4 / 3 distinct outputs at q=11, 31 / 29 at q=31, 55 / 56 at q=41 for r=1/2 (OBSERVED `u12_toy.py` T1): the exponent condition is what makes it a bijection |
| X2 (round 0 is a reparametrisation) | 20 inputs | PROVED and OBSERVED exhaustively on toys (above) |
| X5 (partial round = M(w, s1+c, s2+c)) | 40 inputs | PROVED (algebra), OBSERVED 1000 real states |
| X7 (linear form of three 5th powers) | PROVED | OBSERVED 1000 real inputs |
| X8 (degrees 5^9 / 5^10) | 2 random lines per r | tracker: 32 directions per r incl. axes, 0 cancellations; leading form nonzero => PROVED degree for those lines; finite differences exact up to the sizes in section 9 |
| X10 (one drop direction per lane) | OBSERVED | PROVED: M_i0 u^5 + M_i1 v^5 = 0 has exactly one solution (u:v) because x -> x^5 is bijective on F_p; OBSERVED exhaustively on toys q = 23,29,37,103,257: exactly 1 direction per lane out of q+1; control q = 11, 31 (gcd 5): 0 directions for all three lanes (u^5 takes only the 5th-power values) |
| X4 "Jacobian of (nk,rho) has rank 2 at every point" (sampled) | OBSERVED on 28-31 random points | **FALSE as an every-point statement**: exhaustive q=103: rank < 2 at 205 inputs after R0 (exactly 2q-1: a = 0 or b = 0, PROVED: column of nk is multiplied by 5 a^4 = 0) and growing to 246 after R63 (r=1) / 256 (r=2) (OBSERVED, `u12_toy.py` T4). The rank-drop set only grows. On the real field the points nk = -c0,0 or rho = -c0,1 have rank <= 1 at every level (PROVED) |
| X6 "r >= 3 no trail" | det != 0 | PROVED/OBSERVED, plus the balance statement (section 4) |

Two corrections of the atlas found while auditing:
- A. Label slip in MY script, not in the atlas: `u12_real.py` prints "observability det[e0; e0 M; e0 M^2]" but its rows are e0 M, e0 M^2, e0 M^3 (`0x1875f9...8bb5`, nonzero, i.e. det[M e0, M^2 e0, M^3 e0]-type quantity up to transpose). The atlas value `0xebe164...a8ba` for det[e0; e0 M; e0 M^2] is **confirmed** independently (section 4: equal to the 2x2 minor and to `det3([[1,0,0], M[0], M2[0]])`). Both determinants are nonzero.
- B. X4 / "Jacobian rank 2 at every one of the recorded points": true at the recorded random points, not everywhere (above).

## 8. Interaction summary

- [PROVED] The three blocks interact through exactly three narrow interfaces: front->partial: a 2-dim surface in F^3 (R3.M output); partial->tail: the map (w, s1, s2) -> M(w, s1+c, s2+c) (one scalar nonlinearity) and, for r=2, applied twice; tail->output: one linear form of three 5th powers (rank-1 read of three coordinates).
- [OBSERVED] The partial block is the only place where (a) degrees stop being multiplied by 5 per lane (only lane 0 gets the S-box) and (b) differences can pass without non-linearity; both die at r=3 (section 3) and both are controlled by the same determinant (section 4).
- [OBSERVED] r=1 -> r=2 changes: +1 S-box (26 vs 25, 25 vs 24 non-constant), +1 MDS, degree x5, trail dim 2 -> 1, collision sets independent, inversion +1 root. It changes nothing in R0..R4 or R60..R63.

## 9. Exact output degree (finite differences)

- [OBSERVED `u12_fdbig.py`, lane 0 of the final output along an (A,B)-line, exact] r=1: Delta^390626 = 0 and Delta^390625 != 0, so the exact degree of the output in t is **5^8 = 390625** (166 s). r=2: Delta^1953126 = 0 and Delta^1953125 != 0, exact degree **5^9 = 1953125** (885 s). By X2 ((nk,rho) -> (A,B) is 5th powers) these are the (A,B) degrees; the (nk,rho) degrees 5^9 / 5^10 are the tracker's (PROVED on the tested lines), and the finite differences confirm the tracker independently, including the extra factor 5 for r=2, on the real output. Not run: exact finite differences in (nk,rho) coordinates (5^9 / 5^10 points, too many).

## 10. Boring details worth keeping

- The tracker silently turns a cancelled lane into "zero" and loses its lower terms: harmless for the top-form of later lanes but do not read its post-cancellation lane degrees as true.
- `hash_reduced` includes input range checks, 89 us per call; the stand-alone 5th root costs 110 us.
- Python 3.14 `pow(x,-1,p)` is used for the binomial recurrence in finite differences; k < p, so k! is invertible and Delta^k f = k! * (coefficient): a vanishing Delta^(d+1) with nonzero Delta^d is an exact degree statement.
- In `u12_toy.py` T3 the equality "pairs equal after R5 = q^3 (q-1)" caught me out: my first prediction (zero) was for the *chained* event; both numbers are in the output (section 3 and 4).
- A script copy of the finite-difference run was started twice by mistake and one used the wrong degree formula (5^(8+r) for the (A,B)-line, which is one power too high); the stray processes were killed by PID and the formula corrected before any result was recorded.

## 11. Questions this raised

1. The balance (section 4) holds for free (s1, s2). On the real hash, (s1, s2) after R3 lie on a 2-dim surface; is lane 0 after R5 still uniform over the surface at fixed s0? On toys: restrict the exhaustive q^2 inputs to those with equal lane 0 after R3 and test the balance of the lane-0 value after R4 and R5.
2. How many (nk, rho) pairs have equal lane 0 after R3.M (the curve of pairs)? Toy count versus q^2 (q^2 - 1) / (2q), and the same for the pairs among those whose differences have the trail form.
3. Is G2 = Psi R5 Psi^-1 G1 useful as a recursion (r partial rounds = r conjugates)? What is the algebraic degree of Psi R5 Psi^-1 as a map on F^3 (5^8 or 5^4 per coordinate? the tracker would say)?
4. The determinant `0xebe164...` appears in two roles; is there a third (e.g. the quantity that decides surjectivity of the front surface onto the tail's input plane)?
5. The 5th-root cost ratio (about 120 forward S-boxes per backward one): is there an addition chain for d much shorter than 253 + 124 (d is a structured number of Hamming weight 125; its low part `...0cccccccd` is regular)?
