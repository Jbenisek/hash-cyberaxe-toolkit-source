# Orchard Poseidon r=1,2 : verification of the "skip round 1, odd-part collision" attack

Folder: `./research/poseidon/orchard/math`  (all code, logs and raw outputs are here).
Date of runs: 2026-10-12.  Field p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
(p mod 5 = 2, so gcd(5, p-1) = 1; 2-adicity of p-1 is exactly 32).

Labels: PROVED = paper argument, no experiment needed. COMPUTED = I ran it on the real constants (big ints, exact).
DERIVED = argued, depends on a stated assumption. GUESS = not tested at target size.

## 0. Answers in one table

| Item | Verdict | Label |
|---|---|---|
| Step 1: round 0 only enters through U=(nk+c0)^5, V=(rho+c1)^5 (bijective), round-1 S-box input is an affine plane P in (U,V) | correct | PROVED + COMPUTED |
| Step 2: for each j in {0,1,2} a line Q + tau d in P on which the round-1 S-box output is v0 + W v1, W = tau^5 | correct for all three j; exact equality on 20 random tau per j (60 total), nk,rho canonical | COMPUTED |
| Hash = F_j(W) end to end (genuine reference hash of (nk,rho) from the line equals the line model) | holds for r = 0,1,2, 60/60 tau | COMPUTED |
| Step 3: deg F_j = 5^(6+r) exactly | 15625 (r=0), 78125 (r=1), 390625 (r=2), for all three j; all D+1 coefficients nonzero | COMPUTED (upper bound PROVED) |
| Third round skippable? | No. Complete classification below: the 3 lines are the only curves in the (nk,rho) plane that skip round 1; their image line at round 2 has dim span = 4, not 2 | PROVED (modulo a genus argument) + COMPUTED |
| Success heuristic (Poisson roots of g, half of them squares) | supported: 0.3937 +- 0.001 over 600,000 centres at D=125, 0.3938 at D=625, consistent at D=3125, 15625; real Pallas r=0,1 runs found verified collisions | COMPUTED (small analogues) / DERIVED (extrapolation) |
| End to end on real constants | verified collisions found on the real constants for r=0 (36 of 90 centres), r=1 (7 of 12), r=2 (1 of 2); pairs in section 6 | COMPUTED |

## 1. Reference check

`pos.py` is my own implementation (add constants of the ORIGINAL round index, S-box on all coordinates for full rounds and coordinate 0 for partial, dense MDS, digest = coordinate 0, init [nk, rho, 2^65], rounds 0..3, 4..4+r-1, 60..63).
Validated against `tests/orchard-upstream-vectors.json`: 11/11 full-permutation vectors (56 partial rounds) and 11/11 ConstantLength<2> hash vectors match. So round function, constants, MDS and byte order are right.
Then `digest(nk, rho, r)` is the same code with the reduced schedule.

Facts used: 5^-1 mod (p-1) = e = (4(p-1)+1)/5 (254 bits, Hamming weight 125), so x -> x^5 is a bijection of F_p with inverse x -> x^e. (PROVED/COMPUTED)

## 2. Steps 1-2 (verify1.py, output verify1_out.txt)

Notation: c0_k = RC[0][k], c1_k = RC[1][k], M the MDS, K = (2^65 + c0_2)^5 (a constant:
`K = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c`).

Round 0 gives (U, V, K) with U = (nk+c0_0)^5, V = (rho+c0_1)^5. Since x->x^5 is a bijection, (nk,rho) in [0,p)^2 <-> (U,V) in F_p^2 bijectively, so every (U,V) has exactly one canonical preimage: nk = U^e - c0_0 mod p, rho = V^e - c0_1 mod p. (PROVED)

Round-1 S-box input: x_k = M_k0 U + M_k1 V + b_k, b_k = M_k2 K + c1_k  (affine plane P). (PROVED)

For a chosen constant coordinate j with others I = {i1, i2}:
* Q = (U_Q, V_Q): solution of x_i1 = x_i2 = 0 (2x2 system; its determinant M_i1,0 M_i2,1 - M_i1,1 M_i2,0 is nonzero for all three j: COMPUTED).
* direction (a, b) = (M_j1, -M_j0), so d_k = M_k0 M_j1 - M_k1 M_j0, d_j = 0 and d_i != 0 for i != j (COMPUTED; these are 2x2 minors of an MDS matrix).
* Line (U,V) = (U_Q + tau a, V_Q + tau b). Then x_i = d_i tau (i != j), x_j = kappa_j = x_j(Q) != 0 constant.
* S-box output = v0 + W v1 with W = tau^5, v0 = kappa_j^5 e_j, v1 = sum_{i != j} d_i^5 e_i. (PROVED)
* tau -> W = tau^5 is a bijection, so distinct W give distinct tau, distinct (U,V) (since (a,b) != 0), distinct canonical (nk,rho). (PROVED)

COMPUTED, for each j in {0,1,2} and 20 random tau (seeded, `verify1.py`): genuine round 0 from (nk,rho), genuine round-1 constant addition, then
(i) x_j equals kappa_j and x_i equals d_i tau, exactly;
(ii) the S-box output equals v0 + W v1, exactly;
(iii) (nk+c0_0)^5 = U, (rho+c0_1)^5 = V, nk,rho < p;
(iv) the genuine reference digest(nk, rho, r) equals the line model F_j(tau^5, r) for r = 0, 1 and 2.
Result 20/20 for every j. Per-j numbers (Q, a, b, d, x(Q)) are in the appendix.

Observation: all three j work, and give three different polynomials F_0, F_1, F_2 (different leading coefficients, section 3). They can serve as independent trials for amplification at the same cost as new centres.

## 3. Step 3: degree of F_j (degree.py; logs degree_r0.txt, degree_r1.txt, degree_r2.txt)

Upper bound (PROVED): after the round-1 MDS the state is affine in W. Rounds 2, 3, the r partial rounds and rounds 60..63 each multiply the degree by at most 5 (a partial round puts x^5 on coordinate 0 only, but the dense MDS has no zero entry, so every coordinate has degree 5x afterwards). The digest is row 0 of the last MDS applied to the S-box outputs. So deg F <= 5^(6+r).

Exactness (COMPUTED): evaluate F_j at the N = 2^k powers of a primitive N-th root of unity w (N > D), inverse NTT (pure Python), read the coefficients; N > D makes this exact interpolation, and I checked a fresh random point by Horner against the direct model (excludes aliasing).

| r | D = 5^(6+r) | log2 D | N | found degree | nonzero coeffs above D | zero coeffs below D | fresh-point check |
|---|---|---|---|---|---|---|---|
| 0 | 15625 | 13.93 | 2^14 | 15625 (j=0,1,2) | 0 | 0 | pass (3 points each) |
| 1 | 78125 | 16.25 | 2^17 | 78125 (j=0,1,2) | 0 | 0 | pass |
| 2 | 390625 | 18.57 | 2^19 | 390625 (j=0,1,2) | 0 | 0 | pass |

So the digest polynomial is dense (no sparsity to exploit), the leading coefficient is nonzero, and the degree is exactly 5^(6+r). Derived sizes for the odd-part trick: g has degree m = (D-1)/2 = 7812 (r=0), 39062 (r=1), 195312 (r=2) (confirmed deg g = 7812 on the real field).

## 4. Can a third round be skipped?

Answer: no. I could not find any remaining freedom, and I can show there is none.

Setup. A "skip" of a round means: along the one-parameter family, the three S-box outputs lie in span{1, w} for a single polynomial w, so the state after the S-box is affine in w and the next round costs no degree. Let A = span{1, x_0^5, x_1^5, x_2^5} as polynomials in the family parameter. A skip works iff dim A <= 2.

Lemma (PROVED, characteristic > 5). Along a line x_k = alpha_k + beta_k t, the polynomial x_k^5 is a constant if beta_k = 0, otherwise a quintic with a single 5-fold root t_k = -alpha_k/beta_k; (t-a)^5 - (t-b)^5 has t^4 coefficient 5(b-a) != 0 for a != b. Hence dim A <= 2 iff all coordinates with beta_k != 0 vanish at one common t. This gives exactly three kinds of lines:
 (a) a line through the origin x = 0 of the S-box input space;
 (b) a line meeting a coordinate axis e_j (so the other two coordinates vanish at one point) and constant in coordinate j;
 (c) a line parallel to an axis e_k.
Curves other than lines: if x_a, x_b are both non-constant and x_a^5, x_b^5 are affine-dependent, x_a^5 - lambda x_b^5 = mu. For mu != 0 this is the smooth plane quintic X^5 - lambda Y^5 = mu of genus 6, which has no non-constant rational (hence no polynomial) parametrization; for mu = 0, x_a is proportional to x_b. So every rational or polynomial curve that skips has the same shape (non-constant coordinates proportional, i.e. a line traversed by a reparametrization). (DERIVED from standard genus facts; I did not machine-check it.)

Round 1 (the plane P). (a) needs the origin on P: this is one condition on (U,V,K) and is false (COMPUTED: third component of -M^-1 RC1 is `0x28a26c8f...95d`, K is `0x1bb8b655...08c`, they differ). (c) needs e_k in the direction space of P, i.e. a 2x2 minor of M (rows != k, columns 0,1) to vanish: all three nonzero (COMPUTED). (b): for each j, P meets the axis in exactly one point Q_j, and the lines through Q_j in P form a pencil with d_j = 0 fixing a unique direction. So the only skipping lines in P are the three lines of section 2 (dim A = 2 for all three: COMPUTED). The "second free choice of which coordinate vanishes" does not exist: j determines everything; the two vanishing coordinates are forced. The nk/rho asymmetry gives nothing either: U and V enter symmetrically as the two columns of M; the capacity word K is a fixed constant.

Round 2. The round-2 S-box input along the chosen line is l_k(W) = alpha_k + beta_k W with alpha = M v0 + RC[2], beta = M v1. COMPUTED for all three j: all beta_k nonzero (so (a) or (b-with-3-nonconstant) is the only way), the three roots -alpha_k/beta_k are pairwise distinct, and the rank of {1, l_0^5, l_1^5, l_2^5} is 4 (not <= 2). So round 2 cannot be skipped on any of the three lines. Since the three lines are the only rational curves in the (nk,rho) plane that skip round 1 (above), and round 2 skip would need one of them to also satisfy (a)/(b)/(c) at round 2, a third skip is impossible. (PROVED given the classification, COMPUTED for the constants.)

Parameter count (DERIVED): the family has 3 continuous parameters (Q: 2, direction: 1) and the round-1 skip uses all 3 (x_i1(Q)=x_i2(Q)=0, d_j=0). A round-2 skip would need two more independent conditions (beta_k = 0 for one k plus a common root of the other two, or common roots of all three), i.e. probability about 1/p per (j, k) choice, about 2^-251 in total, and the data show none holds.

Not covered: attacks that are not a one-parameter polynomial family (bivariate systems, or non-rational curves of genus > 0, or backward/meet-in-the-middle formulations). I did not analyze them. The last round gives no skip either: the digest is row 0 of M applied to the S-box output, which is the degree-5 map itself.

## 5. Is the success-probability heuristic supported?

Heuristic: for a random centre c, g(S) (deg m) is "generic", so its number of roots in F_p is about Poisson(1) and each root is a nonzero square with probability 1/2, independently, so P(at least one usable root) = 1 - e^(-1/2) = 0.393469. Alternative F(W) - F(W0): Poisson(1) roots, P = 1 - e^-1 = 0.632121 at degree D (twice the degree of g, no square condition).

Experiments (exact: root counts via gcd(g, S^((p-1)/2) -+ 1) in FLINT; every success extracted a root, took its square root, got W = c +- s, tau = W^e, canonical (nk,rho), and checked equal genuine hashes and distinct inputs):

A. Same construction on a mini-Poseidon over a small prime with the same 2-adicity pattern: p = 43*2^32+1 = 184683593729 (38 bits, p-1 has 2-adicity 32, gcd(5,p-1)=1), random round constants and Cauchy MDS, same line construction (all three j), same round structure truncated to rounds 0, 1 + the last q of the tail (so deg F = 5^q) and the full r=0 structure (D = 5^6).

| D = deg F | centres | successes | rate | Wilson 95% | verified collisions | alt F(W)-F(W0) rate |
|---|---|---|---|---|---|---|
| 125 | 600,000 | 236,216 | 0.3937 | [0.392, 0.395] | 236,216 / 236,216 | 0.6281 (60,000 tries) |
| 625 | 60,000 | 23,630 | 0.3938 | [0.390, 0.398] | 23,630 / 23,630 | 0.6288 (6,000) |
| 3125 | 1,800 | 728 | 0.4044 | [0.382, 0.427] | 728 / 728 | - |
| 15625 (full r=0 structure) | 1,500 | 580 | 0.3867 | [0.362, 0.412] | 580 / 580 | 0.6507 (375) |

Root-count histograms: D=125, 600k centres, square-root count chi^2 = 7.76 (4 dof, 5% critical 9.49), non-square 3.99, means 0.5014 and 0.5010 (theory 0.5). D=625: chi^2 0.92 and 6.02, means 0.5005 and 0.4997. D=15625: chi^2 9.96 (just above critical, square-root mean 0.471 vs non-square mean 0.525; combined 0.995, so I take it as a fluctuation, n=1500) and 2.64. The alternative (F(W)-F(W0)) rate is 0.628 to 0.629 at D=125 and 625, about 2 sigma under 0.632 (60,000 tries: sigma 0.002); its root-count chi^2 is 9.76 at D=125 (borderline) and 3.34 at D=625. I do not read this as a real effect but did not investigate further.

B. Real Pallas field, real constants, real Orchard tail, FLINT (python-flint 0.9.0, fmpz_mod_poly), F built by exact polynomial arithmetic, g from a Taylor shift, root counting by gcd(g, S^((p-1)/2) -+ 1), collision extraction and the genuine `digest()` check:

* r = 0 (D = 15625, deg g = 7812), 90 random centres (j cycles 0,1,2): 36 successes (0.400, Wilson [0.305, 0.503]); 36/36 extracted pairs are genuine collisions of the reference digest (distinct canonical inputs, equal digest). Square-root-count chi^2 = 1.41, non-square 7.32 (n = 90). One verified r=0 collision is in section 6.
* r = 1: 12 centres, 7 verified collisions; r = 2: 1 verified collision in 2 centres (section 6).

Reading (DERIVED / GUESS): the model "g behaves like a random polynomial" predicts exactly 1 - e^(-1/2) up to O(m/p) = 2^-240 corrections and 1/m! tails, and it matches within statistical error at every degree we could test, with the best precision (+-0.001) at D = 125 and +-0.004 at D = 625. At the target size (D = 15625..390625, 255-bit field) the real-field test has only 90 centres (+-0.1), the toy at D=15625 has 1500 (+-0.012). So:
 - the model is solid but its decisive number is 0.3935 against a bar of 0.39: a margin of 0.0035 that NO experiment at target size can resolve. The experiments say "no visible structural deviation larger than about 0.01 at D <= 15625, none larger than 0.004 at D <= 625".
 - If the filing needs success >= 0.39 with a real margin, the safe options are: two centres (or two different j) before declaring failure (success 1-(1-0.3935)^2 = 0.632, twice the cost, +1 bit), or the F(W)-F(W0) variant (0.632 per attempt but degree D, roughly 2 to 2.2 times the cost of one g attempt, +1.1 bits). A single g attempt gives 0.3935 and relies on the model.
 - Note for the cost argument: the probability is per centre; on failure draw a new centre c (or switch j); failed trials are charged.

## 6. Things I found while checking that matter for costing

1. Coefficients of g without symbolic polynomial arithmetic (COMPUTED, `gcoef.py`, r=0, real field): h(s) = F(c+s) - F(c-s) = 2 s g(s^2). Evaluate h/(2s) at s_i = w_N^i, i < H = N/2 (w_N a primitive N-th root of unity, N = 2H > ... such that H >= m+1), so S_i = s_i^2 runs over the H-th roots of unity, then one inverse NTT of size H returns all m+1 coefficients of g (the rest vanish). Matches the Taylor-shift coefficients exactly. Number of evaluations of F (each = line-affine map + (6+r) rounds + 1 MDS): 2H = 2^14, 2^17, 2^19 and NTT size H = 2^13, 2^16, 2^18 for r = 0, 1, 2. Mind that each F evaluation is a truncated hash, (6+r) rounds from round 2 on.
2. Square-root-only test: n_sq = deg gcd(g, S^((p-1)/2) - 1) is the number of usable roots. In my runs one powmod gave both square and non-square counts (gcd with X^h -+ 1 for X^h mod g). Observed: S = 0 never was a root (g(0) = 2F'(c) != 0 in all runs).
3. Mapping back costs per pair: 1 square root, then for each of the two members W -> tau = W^e, nk = U^e - c0_0, rho = V^e - c0_1, i.e. 6 exponentiations by e (254 bits, weight 125; about 254 squarings and 124 multiplications each by plain square and multiply) plus the sqrt.
4. FLINT wall time (not the contest cost model): at the real prime, deg g = 7812: building F 0.25 s, Taylor shift 0.3 s, S^((p-1)/2) mod g 19 s, gcds 2 s; about 24 s per centre inside the 90-centre run.
5. The deployed p has 2-adicity 32, so power-of-two NTTs up to 2^32 exist natively. A product of two degree-m polynomials has degree 2m = 15624, 78124, 390624 for r = 0, 1, 2, which pads to NTT sizes 2^14, 2^17, 2^19 (r=1 and r=2 waste 40% and 25% of the transform length to padding; r=0 about 5%).

Real-field end-to-end collisions (genuine reference digest equal, distinct canonical inputs):

* r = 0, line j = 2, one verified pair:
  nk1  = 0x1f45997635204814935d0fd2a6c5244127a974f354c3220ee30cc5b6c14550cb
  rho1 = 0x18c06e2e05f096f42e8b0ad31e3314050aa411d8ffff7105a63f3a0b26276268
  nk2  = 0x2bde542219556a6cdc271e3a01b12e2c4eeac1ab0e37130110ff141f89ee2e09
  rho2 = 0x12be8e3a587ca21c2f4a88f7461413c12b92df689bcdb0d090c1d069e178b2b8
  digest(r=0) = 0x200b1d43f5ff82dfc01f40195ce6fd45c3887152cd440e6b9aa74749167d4ec0 for both. (r=0 is outside the admitted tracks; shown as a check of the pipeline.)

* r = 1 (D = 78125, deg g = 39062), 12 random centres: 7 successes (0.583, Wilson [0.32, 0.81]; n too small to test the rate), 7/7 extracted pairs are genuine collisions of the reference digest. About 130 s per centre with FLINT. One verified pair, line j = 0:
  nk1  = 0x157f965904b92f0ecd2aeb46f277d150fc9affc3c5769cadaea24c7e7db3bafb
  rho1 = 0x057be42c44dcfb32e048f25c01f5e0867cbd95c74d3d4da93b80f94ba3b45f5a
  nk2  = 0x03eb03de5c4dc31b4760764f5fc0ba6ef2ae670fbb2dbba5a7b3cea1aee8b897
  rho2 = 0x1984596a7d7108ff9a992c58e0d917abc6951895ab987827a887b29c820cf3f2
  digest(r=1) = 0x233a5d608ad6a8938e961398e686d4c07d732ae787c4e9dd3238156cc1b2cd38 for both.
* r = 2 (D = 390625, deg g = 195312): 2 centres run (about 690 s each), 1 success (j = 1), verified genuine collision (the run was stopped after that):
  nk1  = 0x20ab639af0a1c6bdcaac19e4f9381e49484cf452713a41e822c847743e576330
  rho1 = 0x1bd5b81f6d248b3bf978a39a07c11e7f70ec14f62ddf83118bd54c4499ed76fd
  nk2  = 0x2976cceaffd982b6a10be7e12658ab0e6da773899f73f628f24e930089a0ba5f
  rho2 = 0x0552dcc47c31202951b1971b3a161df0123c7f2f1f7b2f59b162a1d0b0808132
  digest(r=2) = 0x2b56d57c79ffcfdea5e12fe52a0c5ff6eef95579f418ab13292b24b283348476 for both.
  Check was `pos.digest` (validated on the 22 upstream vectors); canonical (all < p), pairs distinct. I did not cross-check with the organizer verifier (not present in the read-only clone).
So the attack is demonstrated end to end on the real Orchard constants for r = 1 and r = 2 (and r = 0). Raw: exp_real_r0.json, exp_real_r1.json, exp_real_r2.json.

## 7. Limitations and what was not done

* Cost is not computed here; I give degrees and operation structure only.
* The Poisson/half-square heuristic was tested at target size only with 90 (real field) centres; larger-degree evidence is from a 38-bit-prime analogue with random constants (the real constants could differ in structure, but the real-field runs showed no deviation).
* The classification of skippable curves relies on the genus-6 argument for X^5 - lambda Y^5 = mu (standard, not machine-checked), and on exhaustively checking the three lines for round 2.
* Attacks outside one-parameter polynomial families (multivariate, genus > 0 curves, backward or two-sided) were not examined.
* r=2 real-field run is only 2 centres (one success); it demonstrates feasibility, not the rate.

## Files

pos.py (reference + vector check via t0.py), attack.py (Line model), verify1.py / verify1_out.txt, verify2.py / verify2_out.txt (third-round tests), degree.py + degree_r*.txt, fpoly.py + exp_real.py (+ exp_real_r*.json/.txt), toy.py, toy_small.py, toy_small2.py + toy_*.json/.txt, gcoef.py, analyze.py.

## Appendix: per-j numbers (from verify1_out.txt)

```
p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
K = (2^65+c0[2])^5 = 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c
j 0 2x2 minor rows [1, 2] cols 0,1 nonzero: True
j 1 2x2 minor rows [0, 2] cols 0,1 nonzero: True
j 2 2x2 minor rows [0, 1] cols 0,1 nonzero: True
--- j = 0 I = [1, 2]
 Q=(U,V) 0x2de17246e844b000296eefaaf2116b9705e3af63806d80541c7d6b4be442036c 0x2622542e119aef1f7c021664aae329063a3e73651cd62e02756427f9437fdd96
 direction (a,b) 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e 0x354a1a478b5972184c2a60423736152b8a6ef850e5c7edc566ee0c66281ee49e
 d = ['0x0', '0x2b1cf2a34b2b6723837c31d51d5c91d12d1a715784a437124e3daf150a8d2b15', '0x194af15c17a9f125b198b4fcacb6f6a0d7525c1960573b90b20d8c6a16f61d57']  d_j==0: True  other d nonzero: True
 x(Q) = ['0x2a78890d8503b228bfa6bd9b312401c7af4e02a6376ceebb003ef1138f67c72c', '0x0', '0x0']  x_i(Q)==0 for i!=j: True  x_j(Q) nonzero True
 random tau checked (exact equality, canonical nk,rho, digest r=0,1,2 = F(tau^5)): 20 / 20
 round-2 S-box input l_k(W)=alpha_k+beta_k*W; beta_k nonzero: [True, True, True]
 zero of l_k pairwise equal?  [False, False, False]
--- j = 1 I = [0, 2]
 Q=(U,V) 0x3c80d88605267033c2acc6e39978ff96d087a8e77d92f7c14652fc91b04c8f83 0x1f430622884d4c88c3767dfd251d039a0114a4032402ba9f73e7a14f77073e2e
 direction (a,b) 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e 0x1cce9d9cf1406128071db0997dd3d260e83c52bbc08f8210c8e363242f7ae985
 d = ['0x14e30d5cb4d498dc7c83ce2ae2a36e2ef52c27a484a8c2094aef81d7f572d4ec', '0x0', '0x29ff5d012f09098bd15bbf637fb69b9102e1567bbf433f63d5987016a23d1cc2']  d_j==0: True  other d nonzero: True
 x(Q) = ['0x0', '0x56ca88352495e3b531f6639906f2a46f1123cf5ea8ca2ead4467a8cc69282fa', '0x0']  x_i(Q)==0 for i!=j: True  x_j(Q) nonzero True
 random tau checked (exact equality, canonical nk,rho, digest r=0,1,2 = F(tau^5)): 20 / 20
 round-2 S-box input l_k(W)=alpha_k+beta_k*W; beta_k nonzero: [True, True, True]
 zero of l_k pairwise equal?  [False, False, False]
--- j = 2 I = [0, 1]
 Q=(U,V) 0x3a6b4715e36197c96a9a6f3872a4228ff76b2e677bc2daee281769346513ae75 0x165d64bda0c30365e498649bf11808b860bc6a7b495927fd0ba21062a3e476bb
 direction (a,b) 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664 0x11d622a639b4efc80ccc556e3c7ccb9c00de8a5043e137bd9a458758b07b241d
 d = ['0x26b50ea3e8560eda4e674b035349095f4af43ce2a8f5bd8ae71fa482e909e2aa', '0x1600a2fed0f6f6742ea4409c8049646f1f6542804a09b9b7c394c0d65dc2e33f', '0x0']  d_j==0: True  other d nonzero: True
 x(Q) = ['0x0', '0x0', '0x9b2d7e67acf680114704863d53135870423bf02a5b6414ddd79da0955bb7210']  x_i(Q)==0 for i!=j: True  x_j(Q) nonzero True
 random tau checked (exact equality, canonical nk,rho, digest r=0,1,2 = F(tau^5)): 20 / 20
 round-2 S-box input l_k(W)=alpha_k+beta_k*W; beta_k nonzero: [True, True, True]
 zero of l_k pairwise equal?  [False, False, False]
```

Third-round tests (verify2_out.txt):

```
origin of round-1 S-box input space lies on plane P only if 3rd comp of -M^-1 RC1 equals K: False
  (3rd comp, K) = 0x28a26c8f4a241f2f3e28a633fe1763f03d0f1f3f2f26baf797bb9d5db4fe95d 0x1bb8b6550fd0a299151ec6e764ce7a0e7639053ef68202d771242177f32f108c
e_0 in direction space of P? False
e_1 in direction space of P? False
e_2 in direction space of P? False
j 0 dim span{1,x_k(tau)^5} (round 1) = 2 (<=2 means round-1 skip works)
j 0 dim span{1,l_k(W)^5} (round 2) = 4 (<=2 would allow a round-2 skip)
j 1 dim span{1,x_k(tau)^5} (round 1) = 2 (<=2 means round-1 skip works)
j 1 dim span{1,l_k(W)^5} (round 2) = 4 (<=2 would allow a round-2 skip)
j 2 dim span{1,x_k(tau)^5} (round 1) = 2 (<=2 means round-1 skip works)
j 2 dim span{1,l_k(W)^5} (round 2) = 4 (<=2 would allow a round-2 skip)
```

