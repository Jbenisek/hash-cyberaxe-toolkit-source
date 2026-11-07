# CARD U7 - the S-box x -> x^5 on Pallas (level card, learner U7)

Written 2026-10-12. Folder: `./research/poseidon/levels/U7`. Learning only: no attack scores anywhere. Labels: OBSERVED (a command was run, script named) / PROVED (short argument given) / DERIVED (follows, not fully written out) / GUESS. Every script is single-process, deterministic (seeds in the files), outputs saved next to it as `*_output.txt`. Run from this folder: `python <script>.py`. Used: `poseidon_ref.py` (validated implementation) as data, `common.py` (field helpers), `toy.py` (numpy toy copies: same round schedule, random Cauchy MDS, random constants, capacity 2^65 mod q).

| script | question | output |
|---|---|---|
| `q1_factor.py`, `q1b_orders.py`, `q1c_cycles.py` | Q1 factorisation, orders, cycle spectrum | `q1_factor_output.txt`, `q1b_orders_output.txt`, `q1c_cycles_output.txt` |
| `e2_spectrum.py` | Q2, Q3 differential spectrum, quartic as quadratic in y^2 | `e2_spectrum_output.txt` |
| `e4_symmetry.py` | Q4 symmetry pairs through R0 and beyond | `e4_symmetry_output.txt` |
| `e5_set.py` | Q5 the 125 triples, E4b | `e5_set_output.txt` |
| `e6_support.py`, `e6b_rule.py` | Q6 polynomial normal form / degree profile | `e6_support_output.txt`, `e6b_rule_output.txt` |
| `e7_cost.py` | Q7 cost of x^d vs x^5, forward vs backward | `e7_cost_output.txt` |
| `e8_hits.py` | Q8 zero/fixed-point hits, toys and aimed hits | `e8_hits_output.txt` |

## 0. The level in one paragraph

The S-box is x -> x^5 on F_p, applied to 3 lanes (full rounds) or lane 0 (partial rounds); 24 live evaluations for r=1, 25 for r=2 (R0 lane 2 acts on a constant). It is a bijection (gcd(5,p-1)=1), odd, homogeneous of degree 5, commutes with multiplication by the 4th roots of unity, has exactly 5 fixed points, derivative 5x^4 (zero only at 0), and differential uniformity 4. Forward it costs 3 multiplications; backward (5th root) about 310 multiplications (103x).

## 1. Q1 - the 212-bit cofactor, orders, cycle structure of x -> x^5

- OBSERVED (`q1_factor.py`, sympy ECM, 87 s, B1 up to 8000): **C = 539204044132271846773 x 8999194758858563409123804352480028797519453** (69-bit and 143-bit primes, both prime by gmpy2 50 rounds and sympy; product checked equal to C). So **p - 1 = 2^32 * 3 * 463 * q1 * q2 is now fully factored** (`q1b_orders_output.txt`: "p-1 == 2^32*3*463*q1*q2: True").
- OBSERVED (`q1b_orders.py`): q1 - 1 = 2^2 * 3^5 * 89 * 14923 * 417677162933; q2 - 1 = 2^2 * 3^4 * 11 * 1197907 * 2531 * 115603 * 22160661629 * 325086459374267 (both fully factored). **5 is a primitive root modulo q1 and modulo q2** (ord = q-1 for both).
- OBSERVED (`q1c_cycles.py`) orders of 5: mod 2^e: 1,1 (e=1,2), then 2^(e-2) (e>=3; e=32 gives 2^30); **mod 3: 2; mod 463: 462**. CORRECTION to the atlas line "order of 5 modulo 3 is 3, modulo 463 is 463": both are impossible (5 = 2 mod 3 has order 2; the group mod 463 has order 462). The atlas statement on 2^32 (2^30) is right.
- DERIVED (x -> x^5 is "multiply by 5" on the cyclic group Z/(p-1) after taking discrete logs; an element of order m lies on a cycle of length ord_m(5); there are phi(m) such elements). Computed over all 528 divisors m of p-1 (sum of phi(m) = p-1 checked):
  - 235 distinct cycle lengths; **15,683,600 cycles** on F_p^* plus the fixed point 0.
  - Short cycles (all that exist below length 1000): length 1: 4 elements (1,-1,i,-i), length 2: 20 elements, then lengths 4, 8, 16, 32, 64, 128, 256 each with 6 cycles (24, 48, 96, ... elements), length 462 (24 cycles), 512, 924. Number of x with x^(5^L) = x (incl. 0): L=1: 5, L=2: 25, L=3: 5, L=4: 49, L=8: 97, L=16: 193, L=32: 385.
  - Longest cycle length 28141659245774691079001654546646862068247397390777234750164557367345152 (about 2^235); **49.9% of all elements sit on cycles of that one length**.
  - Fraction of elements on a cycle of length <= 2^30: 1.2e-66. Nothing of interest is reachable by iterating the bare S-box; the constants and M break every cycle anyway (cycles matter only for a lane iterated alone, which never happens).
- Dull but recorded: the gcd trick gcd(5^L - 1, p - 1) counts points of period dividing L without knowing the factorisation.

## 2. Q2 / Q3 - differential spectrum and the quartic in y^2

Equation: (x+a)^5 - x^5 = b, a != 0.

- PROVED: with h = a/2 and y = x + h, (y+h)^5 - (y-h)^5 = 10h y^4 + 20 h^3 y^2 + 2 h^5. With z = y^2: **10h z^2 + 20 h^3 z + (2h^5 - b) = 0**. Its discriminant is 40h(8h^5 + b) = 5a(a^5 + 4b). Put **t = (b + 8h^5)/(10 h^5)**; roots are z = h^2 (-1 +- u) with u^2 = t. Number of solutions x:
  **N(b) = (1 + chi(u-1)) + (1 + chi(-u-1))** for u = sqrt(t) != 0 (chi the quadratic character, chi(0) = 0 so z = 0 gives the single solution y = 0), N = 0 if t is a non-residue, and N = 1 + chi(-1) = 2 if t = 0 (double root z = -h^2, y = +- i h; needs p = 1 mod 4).
- PROVED (consequence): for p = 1 mod 4 the condition for **4 solutions** is: t is a nonzero square, u = sqrt(t), and u - 1 and u + 1 are both non-zero squares (chi(-u-1) = chi(u+1)). **3 solutions** exactly at t = 1 (u = +-1, b = 2h^5 = a^5/16): z = 0 gives y = 0 and the other root z = -2h^2 is a square when p = 1 mod 8. **2 solutions** if exactly one of u-1, u+1 is a square, or t = 0 (b = -8h^5).
- OBSERVED (`e2_spectrum.py`): closed form agrees with an independent root count on 18,796 toy (a,b) pairs (0 mismatches) and on 1,500 random (a,b) on Pallas, where the root count is gcd(x^p - x, f) (0 mismatches). Special b on Pallas: b = a^5/16 gives 3 solutions, b = -8h^5 gives 2, b = 0 gives 0, b = a^5 gives 4 (x = 0 is a root). Homogeneity (spectrum for a is the spectrum for 1 with b scaled by a^5): 200/200.
- OBSERVED (`e2_spectrum.py`, exhaustive on 365 toy primes q < 3500 with gcd(5,q-1)=1, a = 1; fits made on the two smallest primes of each class and checked on all): with n_k the number of b with k solutions,

| q mod 8 | n0 | n1 | n2 | n3 | n4 | primes checked |
|---|---|---|---|---|---|---|
| 1 | 5(q-1)/8 | 0 | (q+3)/4 | 1 | (q-9)/8 | 91 |
| 3 | (5q+1)/8 | 0 | (q-3)/4 | 1 | (q-3)/8 | 93 |
| 5 | (5q-9)/8 | 1 | (q+3)/4 | 0 | (q-5)/8 | 91 |
| 7 | (5q-3)/8 | 1 | (q-3)/4 | 0 | (q+1)/8 | 90 |

  (n1 = 1 appears when q = 3 mod 4 loses y = +-ih or q = 5,7 mod 8 loses the 3: the single b with a double-root solution count.) The formulas are fits to data, not proofs, for all rows; they follow the character-sum pattern sum chi(u^2 - 1) = -1 (DERIVED, not written out).
- **Pallas (p = 1 mod 8), per fixed a != 0** (DERIVED from row 1, consistent with the sampled fractions 0.625 / 0.257 / 0.119 over 1,500 draws): n4 = (p-9)/8, n3 = 1, n2 = (p+3)/4, n0 = 5(p-1)/8. Exact values are printed in `e2_spectrum_output.txt` (E2e). So a uniformly random b gives 0 solutions with probability 5/8, 2 with 1/4, 4 with 1/8. Differential uniformity is 4 (not 2: x^5 is not APN).
- GUESS / open: a clean proof of the four counts via Jacobsthal sums; whether the "one b with 3" or the D = 0 b are useful anywhere (they are single points, one each per a).

## 3. Q4 - the symmetry S(ix) = iS(x) through R0 and beyond

- PROVED: S(lam x) = lam^5 S(x) for any lam; lam^5 = lam exactly for lam^4 = 1 (lam in {1,-1,i,-i}); then S, M and the whole constant-free map commute with multiplication by lam on the state. OBSERVED sanity (`e4_symmetry.py`, toy q = 257, 3000 inputs): with zero constants and zero capacity out(ix, iy) = i out(x,y) holds 3000/3000; with zero constants but capacity 5 (not scaled) it holds 11/3000 (= random level). **The symmetry is destroyed by the capacity word and by the constants.**
- Construction of related pairs: nk' = i(nk + c00) - c00, rho' = i(rho + c01) - c01, so the two states are i-related at R0.C in lanes 0 and 1.
- OBSERVED, defect d = s' - i s after every step, real field, 6 random inputs, r = 1 and r = 2 (`e4_symmetry_output.txt`):
  - R0.C, R0.S: d = (0, 0, *) is identical across inputs, lanes 0 and 1 exactly related (zero in 6/6).
  - **R0.M: d = (1 - i) K M[:,2]** (K = (2^65 + c02)^5), a constant vector independent of the input, nonzero in all three lanes (checked equal to the prediction). Reason: lane 2 is the constant K in both states, not i K.
  - R1.C: d = (1 - i)(K M[:,2] + c1), still input independent (checked equal to prediction). **R1.S: d depends on the input** and stays so, no zero lane entry at any later step (0 of 6 inputs per lane per step). Final lane-0 defect is nonzero. Same for r = 2 (R5 inserts no change in behaviour).
- OBSERVED (E4b, `e5_set.py`): the relation could be made to survive R1.C only if K*M[j,2] = -c1_j for all three lanes; checked for lam in {i, -i, -1}: false (it would be one field equality per lane; they are unrelated 250-bit values).
- OBSERVED toys (exhaustive q = 257, 769, 1009, r = 1 and 2): number of inputs with out(pair) = i^k out for k = 0..3 is 236..269 for q = 257 (expected 257), 711..806 for 769, 986..1079 for 1009: **no surviving output relation** (all within sampling noise, no excess for k = 0, i.e. no symmetry-induced collisions).
- Takeaway: the exact symmetry covers exactly one level (R0), as a constant-offset affine relation of the plane P0 to itself; it does not propagate. Using scalings with lam^4 != 1 gives S(lam x) = lam^5 S(x) (OBSERVED, true) but the factor changes every round, so it is not an invariant either.

## 4. Q5 - the 125 triples {0, +-1, +-i}^3

- PROVED + OBSERVED: S fixes every one of the 5 values (x^5 = x iff x = 0 or x^4 = 1), so S acts as the identity on all 125 triples (125/125 OBSERVED).
- OBSERVED (`e5_set.py`): M v for the 125 triples: **124 of 124 nonzero triples land with no lane in the set; only v = 0 maps to the set** (histogram of lanes-in-set: 0 lanes: 124, 3 lanes: 1). Same for M^-1 (checked M M^-1 = I with own adjugate inverse). M (t,0,0) for t in {1,-1,i,-i}: no lane in the set.
- OBSERVED toys (2000 random Cauchy matrices per q, q = 1 mod 4: 17, 29, 37, 97, 193, 257, 769): number of output lanes landing in the set matches Binomial(3, 5/q) (e.g. q = 97: 212696 / 33460 / 1824 / 20 observed vs 211592 / 34499 / 1875 / 34 expected; q = 769: 243456 / 4524 / 20 / 0 vs 243194 / 4775 / 31 / 0.1). M behaves like a random matrix with respect to this set; the small-q 3-lane counts are a little low (q = 17: 5264 vs 6310) which is a small-q effect of requiring MDS (GUESS).
- DERIVED consequence: the set is a closed island for S but M kicks every nonzero point out of it; a state can stay "special" only in the zero vector.

## 5. Q6 - polynomial normal form and degree profile of x^5 composed with M

(The binary ANF is meaningless over F_p; the polynomial normal form is what matters.) State x = (x0,x1,x2) as three free variables, real F_p, exact coefficients (`e6_support.py`):

- PROVED: S o M lane j = (M_j . x)^5 is a homogeneous quintic with all 21 monomials present (multinomial 5!/(a!b!c!) times powers of nonzero M entries). M o S lane i = sum_j M_ij x_j^5: **3 monomials, a polynomial in x^5 only**.
- OBSERVED, no constants: F^k (k full rounds) lane has C(5^(k-1)+2, 2) monomials, all exponents multiples of 5: **3, 21, 351 monomials for k = 1, 2, 3** (the full triangles would be 56, 3276, 341376); residue-class count mod 5 = 1. So the constant-free map lives in the lattice 5Z^3 (polynomial of degree 5^(k-1) in X = x^5).
- OBSERVED, with the real constants: one full round has 16 monomials (the univariate expansions of (x_j + c_j)^5); **F,F has 2076 monomials per lane of 3276, and 2076 is exactly the number of exponent vectors (a0,a1,a2) with sum_j ceil(a_j/5) <= 5** (`e6b_rule.py`), the three-variable form of the atlas rule X9 (OBSERVED + checked). Degree 25 lane degree in each lane, constants give 125 residue classes (all classes mod 5 occur).
- OBSERVED, partial rounds: P (R4) has 8 monomials per lane with constants, 3 without (nonlinear only in x0); P,P (R4,R5): 196 with constants, 24 without; F,P (R3,R4): 24 without, 2076 with; P,F (R4,R60): 21 without, 196 with; P,P,F (R4,R5,R60): 956 without, 14,976 with (of 341,376). Degree: 5 per S-layer in every case (all lanes degree 5^k after k rounds that include a nonlinear lane-0 S-box, because M mixes lane 0 into all lanes).
- Degree profile of the whole target: unchanged from atlas X8 (5^9 for r=1, 5^10 for r=2); this card adds that the intermediate supports are far below the dense triangle early (constants create the mixed terms) and the no-constant model is 5-lattice-valued.
- GUESS: the "gaps" (monomials absent in the constant version) are the structure a polynomial/Groebner method would exploit; nothing was tried.

## 6. Q7 - cost of x^d vs x^5, forward vs backward per level

- OBSERVED (`e7_cost.py`): d = 5^-1 mod (p-1) = `0x333333333333333333333333333333334e9ee0c9a10a60e2e0f0f3f0cccccccd`, 254 bits, **Hamming weight 125**. x^5 = 3 multiplications (x^2, x^4, x^4 x). x^d: 253 squarings + 124 multiplications = 377 with plain binary; sliding window w = 5: about 310. **Ratio x^d / x^5 about 103.** Timing (Python big-int, this machine): x^5 1.7 us vs x^d 262 us (gmpy2: 0.6 us vs 60 us); ratio in time about 100-160.
- Per-level cost model (field multiplications, additions ignored; M 3x3 = 9, R0 with the constant lane folded = 12, R63 uses row 0 only = 3):

| level (r=1) | forward | backward |
|---|---|---|
| L1 R0 | 12 | 629 |
| L2..L4 R1..R3 | 18 each | 939 each |
| L5 R4 (partial) | 12 | 319 |
| L6..L8 R60..R62 | 18 each | 939 each |
| L9 R63 | 12 | 939 |
| total | 144 | 7521 |

  For r = 2 the extra partial level R5 costs 12 forward, 319 backward (totals 156 / 7840). Backward partial rounds are cheap relative to full ones (only lane 0 needs a root): 319 vs 939.
- DERIVED: with the prefix computed forward and the suffix backward, the total at a split after level k (r=1) is 7521, 6904, 5983, 5062, 4141, 3834, 2913, 1992, 1071, 144 for k = 0..9. Every level moved from the backward side to the forward side saves 3 roots (about 930 mults) minus about 18.
- Dull: one forward hash in Python is 193 us; 24 inverse S-boxes 7.8 ms (40x).
- OBSERVED: backward from the output is not a single path: only lane 0 is known, so two lanes (or two T-values at R63) are free (atlas X7); the backward cost above is per chosen full state.

## 7. Q8 - how often is an S-box input 0 or a fixed point

- DERIVED: 24 (r=1) / 25 (r=2) live inputs, each in {0,1,-1,i,-i} with probability 5/p if uniform: n*5/p = 2^-247.1 (r=1), 2^-247.0 (r=2); zero only: 2^-249.4 / 2^-249.4.
- OBSERVED toys (`e8_hits.py`, q = 257, 769, 1009 exhaustive; 4099, 12289, 65537, 786433, 1000003 on 4,000,000 random inputs, r = 1 and r = 2, random constants/Cauchy MDS): P(any live input in the set) matches 1 - (1 - s/q)^n with s = 5 (q = 1 mod 4) or 3 (q = 3 mod 4: 4099, 1000003): e.g. q = 1009: 0.11185 observed vs 0.11239 predicted (r=1); q = 65537: 0.00185 vs 0.00183; q = 4099: 0.01741 vs 0.01742. P(any zero) matches too (q = 1009: 0.02334 vs 0.02352). Per-position hit rates are uniform to within noise (q = 1009: 0.00480..0.00505 vs s/q = 0.00496). Slight small-q excess at q = 257, r = 1 (0.3773 vs 0.3760), within sampling expectation of exhaustive correlation (GUESS).
- OBSERVED (real field): such a point is not found by luck but by aiming. In (A,B) coordinates (A = (nk+c00)^5, B = (rho+c01)^5), the R1 inputs are affine in (A,B): fixing B and solving one linear equation put the R1 S-box input of lane 0, 1 and 2 exactly at 0 (3/3, verified by the implementation path). For R2 and R3 inputs the equation is a univariate polynomial of degree 5 (R2) / 25 (R3) in B for fixed A, solved by Lagrange interpolation and sympy `gf_factor`: S-box inputs equal to 0, 1 and i hit at R2 lane 0, R2 lane 2 and R3 lane 1 (9/9 targets found in at most 3 tries, verified). Root counts for R2 lane 0 = 0 over 40 random A: 0 roots 10 times, 1: 15, 2: 11, 3: 3, 5: 1 (mean 1.275); R3 lane 0 = 0, degree 25, 12 random A: mean 0.92 roots. So the set where a given S-box input is zero is a curve with about p points; it is easy to land on (one root-find) but a random input never does.
- OBSERVED: at an aimed point with the R2 lane-0 S-box input = 0 (derivative 0 there) the Jacobian of the state w.r.t. (nk, rho) still has rank 2 after every round, and the hash gradient wrt (nk, rho) is nonzero: a single vanishing S-box derivative does not degenerate the map (the other two lanes carry the derivative).

## 8. Boring details that may matter later

- p = 1 mod 8: so 2, -1, -2 are squares, i exists, 8th roots exist (x^4 = -1 has 4 solutions); the 3-solution case needs chi(-2) = 1.
- 2-adicity 32 makes Tonelli-Shanks up to 32 loop steps; all the sampling above used it with 0 mismatches against the gcd count.
- Phi_5 is irreducible over F_p (atlas G1), so x^5 = 1 only at x = 1: x -> x^5 has no kernel; the preimage of x is unique, x^d.
- For q = 3 mod 4 (4099, 1000003) the fixed-point set is {0, 1, -1} only; toys with q = 1 mod 4 are better stand-ins for Pallas (p = 1 mod 4, 1 mod 8).
- The lane-2 S-box in R0 acts on the constant K = (2^65 + c02)^5; no freedom, but it is the only reason the i-symmetry breaks one level in.
- Atlas G1 line "order of 5 modulo 3 / 463" is wrong (see Q1); the atlas "C unfactored" is now settled.

## 9. What moves when it changes (S-box level summary)

Changing one lane input by e changes that lane's output by (x+e)^5 - x^5, a quartic in x of degree 4; the difference table has uniformity 4 (Q2). The derivative 5x^4 vanishes only at the single point x = 0. A change confined to lanes untouched by the S-box (lanes 1,2 in partial rounds) passes linearly. A 5th-root step costs about 100 forward S-boxes.

## 10. Questions this raised

1. The 1/8 of the b with 4 solutions: does the pair-structure (the two roots +-y and +-y') give a useful 2-to-4 branching in a backward walk, and how often do chains of such branchings stay possible across 3 consecutive rounds (a branching factor above 1 per round would matter for counting preimages)?
2. The 2076 = #{sum ceil(a_j/5) <= 5} law and the 5Z^3-lattice structure of the constant-free map: is there a coordinate change that makes the constants vanish only on a sublattice, i.e. does the gap between 351 (no constants) and the dense count correspond to something an elimination method could use?
3. The i-relation dies at R1.S because of the single constant lane K: is there any other "symmetry with a constant defect" (a pair whose defect is a fixed vector for 2 levels) when the pair is chosen at R1.C or deeper instead of R0.C, e.g. defects that lie in the kernel direction of (M^-1 .)_2?
4. All 24-25 S-box inputs can be steered to 0/1/-1/+-i one at a time by root-finding. Can two or more be steered simultaneously (two equations in two unknowns (A,B): how many solutions at levels L2/L3) and does that create a locally degenerate algebraic structure (e.g. the S-box acts as the identity on several lanes at once)?
5. Is 5 a primitive root modulo both big primes by design, and does the mixed lcm structure of cycle lengths (2^30 x 462-type parts) allow any short-period identity f^L = id of the round map on a sub-plane (cycles of the full round map rather than the bare S-box)? Untested: round-map cycles on the toys (exhaustive q = 257, r = 1) vs the bare S-box prediction.
6. Atlas X10 gives one degree-drop direction per lane after R0; the quartic structure of the S-box difference (n4 = (p-9)/8 branches) suggests counting how many (A,B) pairs give identical R1.S outputs in two lanes: not measured here.
