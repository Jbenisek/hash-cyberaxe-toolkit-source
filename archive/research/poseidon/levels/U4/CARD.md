# CARD U4 - rounds 60-63 and the output (the "tail", 4 full rounds + lane-0 read)

Learner U4, 2026-10-12. Learning only; no attack scores. Labels: OBSERVED (command given) / PROVED / DERIVED / GUESS.
Scripts (single process, exact big-int, constants read as data, `orchard\impl\poseidon_ref.py` imported):
- `u4_facts.py` -> `u4_facts_output.txt` (Q1-Q8, real target; ~1 min). Re-run: `python u4_facts.py`.
- `u4_q5_fix_output.txt` (Q5 corrected chi-square; the first Q5 line in `u4_facts_output.txt` bins `y>>250` wrongly into 64 bins, ignore its chi2 value, use the corrected file).
- `u4_toy_output.txt` (toy copies q = 103 and 257, exhaustive, own inline script, see section T).

## 0. What the tail is
Tail = one function Tail: F^3 -> F, y = row0(M) . S( M S( M S( M S(s + c60) + c61 ... ) ) ). Four full rounds R60..R63, then lane 0 of R63.M. Same object for r=1 and r=2 (Q6). Only row 0 of the final M is used.

## 1. Answers to the eight questions
1. **X7 holds.** OBSERVED, Q1: y = sum_j M0j * T_j, T = S(state after R62.M + c63): 0 mismatches in 1000 inputs for r=1 and 1000 for r=2 (real hash).
2. **Backward map works.** OBSERVED, Q2: pick (T0,T1) free, T2 = (y - M00 T0 - M01 T1)/M02, t = T^d (d = 5^-1 mod p-1), state after R62.M = t - c63; forward R63 returns y in 1000/1000. Continuing backward through R62, R61, R60 (apply M^-1, 5th roots, subtract constants) and running the 4 rounds forward returns y in 1000/1000. Cost: **3 fifth-root exponentiations per full round, 12 for the whole tail** (counter in the script). A partial round costs 1 (DERIVED: only lane 0 has an S-box). Whole backward chain to the R0 input: r=1 12+1+12 = 25 roots, r=2 26 (DERIVED); the lane-2 root at R0 is not free: the value must equal the constant K, an extra equation.
3. **Degree 625.** OBSERVED, Q3 (finite differences on exact lines in R60-entry space, 640 points): y has degree exactly 625 on 2 random lines. Intermediate lane combinations after R60.M, R61.M, R62.M: degree 5, 25, 125 (as predicted). New: **degree drops exist** - the leading coefficient of y on direction u is G(u)_0 where G = 4 rounds of (S then M) with the constants deleted (homogeneous of degree 625, OBSERVED). Building u by running the constant-free map backward from (0,a,b) gives G(u)_0 = 0 and y has degree **624** on that line (OBSERVED). So a whole curve of directions (one equation on P^2) drops the degree by at least 1; how far it can drop (e.g. to 623 or lower on special directions) is not yet looked at.
4. **Special lane values at R63.S.** OBSERVED, Q4. Writing t = state after R62.M + c63:
   - If two of the three t_j are 0, y = M0j * t_j^5 for the third (3 cases checked): y depends on ONE fifth power. That is a 1-dim line of states after R62.M for each pair (PROVED: set two coordinates of t, solve the third free).
   - If any t_j is 0, y depends on two fifth powers; this is a 2-dim surface per lane, count 3q^2-3q+1 states in the toy (exact match q=103, 257).
   - If t_j in {0, 1, -1, i, -i} (the 5 fixed points of x^5) the S-box acts as the identity on that lane; all 125 combinations give y = M0 . t, a purely LINEAR function (125/125 OBSERVED, toy q=257: exactly 125 states, q=103: 27 = 3^3). Each of the 125 points was pulled back through R62, R61, R60 (9 roots) to a state at R60 entry and forward-checked (OBSERVED, hex of the t=(0,0,0) case in the output file). These are 125 points of the R60-entry space where R63 is linear. Whether they sit near anything on the front side is not yet looked at.
5. **Top byte.** OBSERVED, Q5: 10^5 random inputs, r=1: top byte (byte 31 of the LE encoding, = y>>248) ranged 0..63 (0x3f), every one of the 64 values occurred, byte 0x40 never, bits 255 and 254 never set; chi-square of the 64-bin top byte vs uniform = 61.2 (63 df): uniform. r=2, 3x10^4 inputs: same range, chi2 = 80.9 (63 df, p ~ 0.06, unremarkable). PROVED: prob(y >= 2^254) = (p - 2^254)/p = 1.6e-39, so the top two bits are 00 in practice and the 0x40 byte is unreachable by sampling. The top two bits carry no information; effective output length is 254 bits minus ~1.6e-39, i.e. the top byte has only 64 values, the next 6 bits are uniform.
6. **R60..R63 are the same functions for r=1 and r=2.** OBSERVED, Q6: schedule tails equal; on 1000 inputs one common Tail applied to the partial-block output reproduces the hash for both r. The hashes of the same input differ between r (as expected). PROVED from the code: they use the same original constants.
7. **Dead / constant computations.** OBSERVED, Q7 (all 3 steps x 3 lanes of every round, r=1: 81 values, r=2: 90 values): changing the value by +1 leaves y unchanged only for **R63.M lanes 1 and 2** (2 values, both r). Values independent of (nk,rho): **R0.C lane 2 and R0.S lane 2** (both r). Nothing else is dead or constant. The constants of R0 lanes 0,1 and partial-round lanes 1,2 are redundant by re-labelling (atlas X2, X5), but they are not "dead values" and the value-level test cannot see that (not tested here).
8. **Reverse-mode influence.** OBSERVED, Q8, 100 points per r: the adjoint (exact derivative of y wrt each lane after every step) was nonzero everywhere except R63.M lanes 1 and 2 (zero in 100 of 100 points, both r). Closed form PROVED: gradient wrt lane j after R62.M = M0j * 5 * t_j^4, zero only at t_j = 0 (probability ~1/p per lane per point, never seen in 100 points).

## 2. Row cards (what moves what)
| step | reads | writes | linear | fact |
|---|---|---|---|---|
| R60.C..R62.C | 3 lanes | 3 lanes | translation | constants unrelated (atlas G4) |
| R60.S..R62.S | each lane alone | each lane alone | no | bijection, fixed points 0,1,-1,i,-i, derivative 5x^4 zero only at 0 |
| R60.M..R62.M | 3 lanes | 3 lanes | linear | dense, MDS; 3 lanes all influence y |
| R63.C, R63.S | as above | as above | no | t_j = special values give reduced dependence (Q4) |
| R63.M | 3 lanes | lane 0 only used | linear | rows 1,2 dead (Q7,Q8), y = M0.T |

## 3. Interactions between levels
- The degree of Tail is 5^4 = 625 as a function of ANY state at R60 entry; the full-hash degree 5^9 = 1953125 (r=1) is a product of 5^5 (front) and 5^4. OBSERVED consistent with atlas X8.
- The backward map from y is a 2-parameter family (T0,T1 free) that lands on a 2-dim surface at R60 entry; every hop costs 3 roots. The forward front reaches the same space on another 2-dim surface. DERIVED, not intersected here.
- The linear points (fixed-point t) and the single-power lines (two t_j = 0) are the only places where the tail loses its nonlinearity; they are fixed points of the geometry, independent of nk, rho, r (PROVED).

## 4. Toy copies (section T)
`u4_toy_output.txt` (q=103 and 257, Cauchy MDS, random constants, tail only, all q^3 states): the tail on states is a bijection (1092727/1092727 and 16974593/16974593 distinct final states); every y has exactly q^2 preimage states at R60 entry (X7 consequence, min = max); the 3q^2-3q+1 zero count and the 125 / 27 fixed-point counts match the real-structure predictions. q=103 has only 3 fixed points of x^5 (103 = 3 mod 4), q=257 has 5. OBSERVED.

## 5. Five most useful/surprising observations
1. The tail's nonlinearity vanishes entirely at 125 explicit states (all t_j in {0,1,-1,i,-i}); we can compute them (9 roots each) and they are the same for r=1,2.
2. Exactly 12 fifth roots take y back to the R60 entry; 3 per round. A full backward to the input is 25 (r=1) / 26 (r=2).
3. Degree-drop directions exist in the tail itself: constructing u with G(u)_0 = 0 (constant-free 4-round map run backward) gives degree 624 on a line. The leading coefficient is controlled by the constants-free round function.
4. Only 2 dead values (R63.M lanes 1,2) and 2 constant values (R0 lane 2) in the whole pipeline, same for r=1 and 2.
5. Output top byte takes exactly the 64 values 0..63 and is uniform (chi2 61.2); the top two bits are 00 with probability 1 - 1.6e-39.

## 6. Questions this raised (not answered)
- How low can the degree of Tail go along special lines or curves (624 reached; is 623, 5^k-ish, possible)? Is there a plane where the leading coefficient AND the next ones vanish?
- Where do the 125 linear R60-entry points sit relative to the image of the front (R0..R4 surface)? Is the distance zero for some (nk,rho)?
- What do the "two t_j = 0" lines (1-dim in R62.M space) look like pulled back to R60 entry: curves of what degree?
- For r=2 the front changes; do the mid-state images for r=1 and r=2 ever overlap, i.e. is the same R60-entry state reachable under both?
- Does the dead R63.M row structure change the backward count if we also drop M^-1 rows (we use all 9 entries of M^-1 in the backward step - minor).
- The finite-difference degree test needs only 640 evaluations; use it as a standard probe at each level boundary.
