# Orchard Poseidon, r = 2: two input families, a counting argument for the success probability, root isolation (exact ledger)

## 1. Claim

Target: `poseidon-orchard-r2-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, two partial rounds 4 and 5, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = @@TIME_LOG2@@` in target-compression units (`C(2) = 258` primitive operations per unit): the worst-case total of one attempt of the program,
  every executed operation charged (sections 6 and 7); every data-dependent stage is charged at a bound that is derived in section 7 and that the program checks while it runs.
* `memory_log2_bytes = @@MEM_LOG2@@` (`@@MEM_BYTES@@` bytes, section 8), so the normalized cost is `@@TIME_LOG2@@ + @@MEM_PEN@@ = @@SCORE@@`.
* `success_probability = @@PCLAIM@@`: one attempt. The probability is a theorem of section 9 and does not rest on a sample, a model of the digest polynomial or a heuristic about it:
  a counting (pigeonhole) argument shows that a uniformly drawn point of a set of `2p - 1` inputs has a partner with the same digest with probability at least `p/(2p - 1) > 1/2`;
  the program then finds a partner with certainty except for a bounded failure probability of the root-isolation step, at most `2^-35`, and of the sampler, at most `2^-128`.
* The method (two free rounds on a line, so that the digest is a univariate polynomial of degree `5^8`) is a known approach. What is new here is only the use of two such lines and the resulting probability argument.
* The collisions stored in `certificates/` (@@N_CERT@@ pairs, each from a separate attempt; section 10 says how they were produced) are outputs of the stage functions of this program. They check the construction at the
  selected target with the organizer's hash; the cost and probability claims do not use them.

## 2. Two families of inputs on which the digest is a polynomial of degree 5^8

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5`. `M` is the deployed 3x3 MDS, `c_{i,k}` the deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`): every `(U, V)` is the image of exactly one canonical input. `K` is a constant.

2.2 The plane. The input of the round-1 S-box layer is `x = M (U, V, K)^T + c_1`. For the legal inputs it ranges over the plane `n . x = B` (`n = e_2^T M^-1`, `B = K + n . c_1`),
which is the description by `y = M^-1 (x - c_1)` with third coordinate `K`.

2.3 Family `j` (`j = 0, 1`). Let `I = {i1, i2} = {0,1,2} \ {j}` and let `Q = (U_Q, V_Q)` solve `x_{i1} = x_{i2} = 0` (a 2x2 system whose determinant is a minor of the MDS, nonzero on the deployed constants).
With `(a, b) = (M_{j,1}, -M_{j,0})` set `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant on the family (`kappa = B / n_j`) and `x_i = d_i tau` for `i in I`, `d_i = M_{i0} a + M_{i1} b`.
Hence the supports of the "slope" `(d_i tau)` and of the constant `(kappa e_j)` are disjoint, and with `W = tau^5` the round-1 S-box output is `kappa^5 e_j + W sum_{i in I} d_i^5 e_i`, affine in `W`.
After the round-1 MDS and the round-2 constants the state is `alpha + beta W`, `alpha = M kappa^5 e_j + c_2`, `beta = M sum_i d_i^5 e_i`.
Family `C_j` is the set of canonical inputs `(nk, rho)` obtained from `tau in F_p`. The map `tau -> (U,V) -> (nk, rho)` is injective, `W = tau^5` is a bijection, so `|C_j| = p` and every `W in F_p` gives exactly one input of `C_j`
(`tau = W^e`, `(U, V) = Q + tau (a, b)`, `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`; function `map_back` in section 11).

2.4 The digest polynomial. Rounds 2, 3 (full), 4, 5 (partial), 60, 61, 62, 63 (full) put eight S-box layers on top of the affine map `W -> alpha + beta W`; the digest is row 0 of the last MDS. So the digest of the input of `C_j` with parameter `W` is
`f_j(W)` with `deg f_j <= 5^8 = D = 390625`. (In the program, `tail_eval` computes `f_j(W)`.) The leading coefficient of `f_j` is nonzero on the deployed constants; the program computes it at every attempt and halts if it is zero (it never was). So `deg f_j = D` exactly.
Interpolation is exact: `D + 1 <= N = 393216 = 3 * 2^17` evaluations at the `N`-th roots of unity determine `f_j` (a transform of size `N` divides `p - 1 = 2^32 * 3 * q`).

2.5 The two families meet in exactly one input. `C_0` and `C_1` are lines in the `(U, V)` plane with directions `(a_0, b_0)`, `(a_1, b_1)`; the determinant `a_1 b_0 - a_0 b_1` is nonzero (a minor of the MDS), so the lines meet in exactly one point `I`.
The program computes the two parameters `W0*`, `W1*` of `I` (stage "two line setups + intersection"); the self-test of the source (`twofam selftest`) checks that both give the same canonical input and that `f_0(W0*) = f_1(W1*)` equals the reference hash of that input.
Hence `|C_0 u C_1| = 2p - 1`.

## 3. Lemma A (counting)

Let `H` be the digest map from `U = C_0 u C_1` (`|U| = 2p - 1`) to `F_p`. Call `u in U` isolated if no other `u' in U` has `H(u') = H(u)`. If `s` is the number of isolated points, then `s <= p - 1`.
Proof. The `s` isolated points have `s` distinct digests, so `s <= p`. If `s = p`, every element of `F_p` is the digest of an isolated point, so each of the remaining `(2p - 1) - p = p - 1 >= 1` points of `U` would have a digest that is already the digest of an isolated point (no other digest value is available), which contradicts that point being isolated. Hence `U` has no further point, `|U| = p`, contradicting `|U| = 2p - 1 > p`. So `s <= p - 1`. Therefore a uniformly drawn `x in U` has a partner
(a different `x' in U` with `H(x') = H(x)`) with probability at least `(2p - 1 - (p - 1)) / (2p - 1) = p / (2p - 1) > 1/2`. No assumption on `f_0, f_1` is used. `x'` differs from `x` as an input pair, because `U` is a set of distinct inputs.

## 4. The program (one attempt)

```
init:   twiddle table
setup:  the two families (line_setup), the parameters W0*, W1* of their common input I
A  x  := uniform point of U:  w := uniform 256-bit word, repeated until w < 2p - 1 (at most 128 words);
          w < p            : family 0, W = w
          p <= w < 2p - 1  : family 1, W = (w - p) + [w - p >= W1*]            (skips W1*, so I is counted once)
   y  := H(x) = f_h(W)   (one target-compression unit)
for h = 0, 1 (stop as soon as a root has been isolated):
  B  F := (f_h - y) / lead, monic of degree D: 393216 evaluations of the family (units) + one inverse NTT of size 393216
  C  R := W^p mod F, then R := R - W        (lean NTT schedule of section 6.2; exponent p)
  D  G := gcd(F, R) (classical Euclid), R = W^p - W mod F;   G = gcd(F, W^p - W) = the product of (W - root) over the distinct roots of F in F_p
  E  remove from G the roots that are x itself: W (if h is the family of x) and, if x = I, also W1* (family 1)       [exact division by W - root]
  F  if deg G >= 1: isolate one root W' of G (section 4.1), and stop
output: x' := map_back(h, W'); verify that the two reference hashes of x and x' agree and that x' != x
```
Halts. The program ends early in exactly two ways that can happen with positive probability: the sampler uses up its 128 words (probability at most `2^-128`, section 9) and a level of the root isolation has no proper split after its `t(d)` tries (probability at most `2^-35` over all levels, section 4.1). Every other test that ends the program
(the leading coefficient of `f_h` is zero, a charged gcd or division exceeds its derived bound, a division leaves a remainder, a deflation root is not a root) cannot fire: the first is a fixed property of the constants and was checked, and the others are comparisons against bounds that are derived in section 7 as a calculation (maximum number of levels x maximum tries per level x maximum work of a try, each term a closed form or a measured data-independent charge),
so their probability is 0 by proof. There is one attempt, no loop over attempts, and no budget check whose failure could stop a later attempt.

### 4.1 Root isolation (stage F)

Input: monic `G`, degree `d >= 1`, a product of `d` distinct linear factors over `F_p`. Output: a root.
`d = 1`: the root is `-G_0`. `d = 2`: the root is `(s - G_1) / 2` with `s = sqrt(G_1^2 - 4 G_0)` (Tonelli-Shanks; the discriminant is a square since both roots are in `F_p`).
`d >= 3`: repeat for at most `t(d)` tries, `t(d) = ceil(40 / (d - 1))` for `d <= 40` and `t(d) = 1` for `d > 40`:
draw `c` uniform in `[0, 2^254)`; replace `G(Z)` by `G(Z - c)` (Taylor shift; the roots become `r + c`); `S := Z^((p-1)/2) mod G`; `A := gcd(G, S - 1)` (monic, classical Euclid).
`A` is the product of the factors whose root `r + c` is a nonzero square. If `1 <= deg A <= d - 1` the try is proper: continue with `A` if `deg A <= d - deg A`, otherwise with `G / A` (exact division); in both cases the new degree is at most `floor(d/2)`.
If no try of a level is proper, the attempt fails (halt). At the end the root of the final linear or quadratic factor is shifted back by the sum of the `c` used.
The roots of the final polynomial are roots of `G`: each piece divides the previous one.

**Lemma B.** Let `G` be a monic product of `d >= 3` distinct linear factors over `F_p`, `d <= 2^19`, and `c` uniform in `[0, 2^254)`. The probability that `deg gcd(G(Z - c), Z^((p-1)/2) - 1) in {0, d}` is at most `2^(1-d) + 2^-100`.
Proof. Let `r_1..r_d` be the roots, `chi` the quadratic character (`chi(0) = 0`), `E = {-r_i}`. The degree of the gcd is `#{i : chi(r_i + c) = 1}`. For `c not in E`,
`[chi(r_i + c) = 1 for all i] = prod_i (1 + chi(r_i + c))/2 = 2^-d sum_{S} chi(prod_{i in S} (r_i + c))` and `[chi(r_i + c) = -1 for all i] = 2^-d sum_S (-1)^|S| chi(prod_{i in S} (r_i + c))`.
For `S` nonempty, `prod_{i in S}(Z + r_i)` is squarefree of degree `|S|`, so by Weil's bound `|sum_{c in F_p} chi(prod_{i in S}(c + r_i))| <= (|S| - 1) sqrt(p)` (the sum is 0 for `|S| = 1`). Summing over `c not in E` costs at most `d` more per term.
So the number of `c in F_p` with all `chi = 1`, and likewise with all `chi = -1`, is at most `p/2^d + (d-1) sqrt(p) + d`, and the `c in E` add at most `d`. Dividing by `2^254 >= p (1 - 2^-128)` (the draw is uniform on a subset of `F_p`, so counts of bad values over `F_p` bound the counts over the subset):
probability `<= 2^(1-d) (1 + 2^-127) + 2 (d-1) 2^-127 + 3d 2^-254 <= 2^(1-d) + 2^-100`. QED.

Consequence. A level of degree `d` fails with probability at most `(2^(1-d) + 2^-100)^t(d) < 2^-39.99`: for `d > 40` take `t = 1` and `2^(1-d) <= 2^-40`; for `3 <= d <= 40`, `t(d) (d - 1) >= 40` gives at most `2^-40 (1 + 2^-61)^t`. Degrees halve, so a polynomial of degree at most `D = 390625` passes through at most 17 levels with `d >= 3`
(390625, 195312, 97656, 48828, 24414, 12207, 6103, 3051, 1525, 762, 381, 190, 95, 47, 23, 11, 5). Over all levels the failure probability is below `17 * 2^-39.99 < 2^-35`, and a shift `c = 0` (Taylor shift needs `1/c`), probability `2^-254` per try, is absorbed (fewer than 100 tries in all). The number of tries of a run is at most the sum of `t(d)` over these levels (@@TRIES_SUM@@).

## 5. Why the output is a collision

By section 2 every root `W'` of `F_h` in `F_p` is the parameter of an input `x'` of `C_h` with `H(x') = y = H(x)`. The roots removed in stage E are exactly the parameters of `x` (and, when `x = I`, the parameter of `I` in the other family), so `x'` differs from `x`:
within one family distinct parameters are distinct inputs; across families the only common input is `I`. The program recomputes both reference hashes and emits the pair only if they are equal and the pairs differ. Independent of the program, the pairs in `certificates/` are checked by the organizer's hash.

## 6. Machine model and charging rules

Every item below is counted by the executing code at the statement that executes it; none is estimated. The complete source is in section 11.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation): `LD(n)` adds `n` to the load counter and `n` to the control counter, `ST(n)` likewise.
* every loop, whatever its body: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). The code is not unrolled; `loopc(n)` adds exactly this.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, multiplication, modulo, comparison, conditional branch, and the selection of an element of the 16-word register block by a computed index. They are added with `CTL(k)` next to the statement that executes them, and data-dependent tests are charged per executed test.
* one iteration of the innermost butterfly loop of a transform block: 9 control operations, counted as `CTL(9 * nb + 2)` after the loop that executed `nb` butterflies. The loops over `j`, `tp`, the elements of a block and the blocks of a pass are charged with `loopc` and the statements `idx = (b + tp * s) << (l0 + j)` (4), `half = 1 << (k-1-j)` (3), the test `if (idx)` (2) and the twiddle address (1 or 2) are charged where they are written (section 11, `blk_fwd`, `pass_fwd`).
* working registers: the 16-word array `x` of a block is the register file. Its 16 words are loaded once and stored once per pass block (each with its address operation), and a selection of an element of `x` by a computed index is charged as above. This is the only register assumption.
* a random word: 1 plus 2 control operations for a 254-bit word (`rnd_fp254`), 1 for a 256-bit word (`rnd_u256`).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B and the evaluation of `y`: 258 each (`C(2)`), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* dispatch and selection: the source contains no `switch`, function pointer or branch table (searched in all files of section 11). Every other selection (`if`, `?:`, `while` tests, the test of the mode in `pass_fused`, the tests of `P->rows`, the choice of the operand pointer in `conv_core`, the validity tests) is charged by a `CTL` next to the statement, as the comments show.
* every executed statement of the new stages (`gcd_cl`, `deflate`, `taylor_shift`, `split_find_root`, the sampler) is charged where it is written, including the compare, branch and subtraction of every loop test, as the comments of section 11 show.
Not charged (declared): conversion of constants to the internal Montgomery representation (constants of the program text, the 256-bit constant `2p - 1`, and the conversion of a loop counter `j` into a field element in `taylor_shift`, once per use), the bookkeeping of the allocator (`xalloc`, `xfree`: memory is accounted in section 8), formatting and printing.

### 6.1 Stage C: the powering schedule (in place, no stored spectra)

For the exponent `E` (here `p`, and `(p-1)/2` in section 4.1), `m` the degree of the modulus, `N = 3 * 2^a >= 2m - 1` and `N' = 3 * 2^b >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most four layers (16-element register blocks). The state is `s = a / N` so no scaling is needed in the loop.
One step maps the residue `a` (`m` coefficients, stored in the buffer `Y` of `N` elements) to `a^2 mod g`:
```
Y := conv_sq(Y)                       square: forward transform, pointwise square fused with the first inverse pass, inverse transform
F[i] := Y[i] + Y[i+N'] (i < m)       fold of the low part modulo x^N' - 1 (saved in the buffer F of m elements)
Y[0..m-2] := Y[m..2m-2]               high part T1 of the square
Y := conv(Y, MU)                      quotient q (Barrett): MU = x^(N-m+2) * floor(x^(2m-2)/g) / (N N') stored compactly (m-1 elements)
Y := conv_N'(Y, g)                    (q * g) mod (x^N' - 1)
Y[i] := F[i] - Y[i] (i < m)           new residue; if the exponent bit is 1: shift by x and subtract lead * g (streaming)
```
The spectra of `MU` and of `g` are not stored: for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp`, immediately multiplied into the corresponding row of `Y`, and discarded.
`MU` is computed once from `g` by Newton iteration with the same row-wise products. The leading exponent bits are absorbed by starting from the monomial `W^v` with `v < m`.
All charges of this stage depend only on `m` and the exponent, not on the coefficients.

## 7. Ledger (primitive operations; `C(2) = 258`)

The counts of the data-independent stages are the exact totals of the instrumented execution (`arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 258-operation unit charges).
Every term of the worst case is either such a total, or an exact enumeration of the control operations written next to the statements of the source (sampler, driver, quadratic end), or a bound that is derived below and that the program checks while it runs. There is no allowance in the ledger.

* **Stage A (sampler and `y = H(x)`).** The sampler loop runs at most 128 times; one iteration charges 1 random word plus `3 + 2 + 30 + 1 = 36` control operations (loop, test of `got`, the comparison of four limbs with `2p - 1`, branch). After the loop: 4 (exit, test) and 31 (comparison with `p`, branch);
  family 1 adds the subtraction `w - p` (38), the copy of `W1*` (14), the comparison with `W1*` (31), the increment (31) and the copy of the result (15); family 0 a copy (15); the test `x = I` costs 12, and `y = H(x)` one unit (258). The worst case, 128 iterations and family 1, is @@SAMPLE@@ operations
  (`128 x 37 + 4 + 31 + 38 + 14 + 31 + 31 + 15 + 12 + 258`); the logged runs charge @@SAMPLE_OBS@@.
* **Driver.** Per family: the loop head (7), the calls of `build_F`, `powx_lean`, `gcd_cl` (6), the call of the bound (4), `d = dg` (1), the two root tests (2 + 3) each with the call of a deflation (3), the test `d >= 1` (2): 31 operations; the family that runs the isolation adds the call (5) and the assignment (1); once after the loops: the loop head (7) and the test of `found` (2).
  The program prints the operations it charges outside its named stages in the line `DRIVER`; for a run that succeeds in family 0 the line reports 72 = 7 + 6 + 4 + 2 + 7 + 2 + 44, the last term being the combination of the four comparisons of the success test.
* **Stage D (gcd).** `gcd_cl(da, db)` with `da = D`, `db = D - 1`. Let `S0 = da + db`. Every elimination step of the program lowers `dA + dB` by at least 1 and its inner loop runs `dB <= (dA + dB)/2` times, so the inner iterations total at most `floor(S0^2/4)`;
  the eliminations number at most `S0 + 1`, the passes (one inversion each) at most `S0 + 1`, and the degree scans lower `dA` by `S0 + 1` in total. An inner iteration is charged 12 (2 arithmetic, 2 loads, 1 store, 7 control), an elimination 25 + 11 (`dA - nd`), a pass 330 + 1 + 2310 + 8 plus the loads, setup and final normalisation (function `gcd_cost_bound`, section 11).
  The leading term is the cost of the worst degree chain `D, D-1, D-2, ..., 0` (two eliminations of about `b` inner iterations for each remainder of degree `b`, so about `D^2` inner iterations in all; a gap in the chain between `a > c` removes inner iterations, because inserting a degree `b` with `a > b > c` adds the work `(a - b)(b - c) + b`).
  The program asserts `charged <= bound` at every gcd it runs (the root isolation and the main stage); the bound is @@GCD_BOUND@@ operations for `(D, D-1)`, against @@GCD_OBS@@ charged in the runs of this ledger (the ratio of charge to bound is 0.56 at `d = 17`, 0.85 at `d = 1000`, 0.94 at `d = 3000` in the tests, because the bound is the cost of a normal remainder sequence).
* **Stage E.** At most `d + 1` coefficients are copied and at most two roots deflated: @@RM_D@@ operations at `d = D` (measured at that size; the cost is linear in `d` and independent of the data).
* **Stage F (root isolation), worst case.** The level `j` of section 4.1 works on a polynomial of degree `d_j <= k_j = floor(D / 2^j)` (the program continues with the factor of smaller degree, which has degree at most half): `k_j = 390625, 195312, ..., 11, 5` for `j = 0..16`.
  A try on a polynomial of degree `d` charges exactly `shift(d) + pow(d) + gcd(d) + 13`, where `shift` is the Taylor shift, `pow` is `Z^((p-1)/2) mod G`, `gcd(d) <= gcd_bound(d, d - 1)`, and 13 is the control of the try (loop test 5, random word 3, negation 1, the test of the split 4).
  A level charges `t(d)` tries, 17 operations of level control, and once (only the successful try of a level divides) `div_bound(d) = max_a div_cost_bound(d + 1, a + 1)`, the closed form of the division by the monic factor, asserted at every division (section 11).
  The constants 13 and 17 are checked by the test program: `test_split` prints the difference between the charged total of a root isolation and its four stage charges, which equals `17 L + 13 T + 7` in the seven runs of the log that end in a linear factor (`d = 3, 4, 9, 17, 40, 1000, 3000`; `L` levels, `T` tries).
  The end of the schedule, a quadratic factor, charges at most @@QUAD@@ operations: the square root of the discriminant is charged by the rule "2 loads, 1 store, 6 control operations per arithmetic operation, twice" and 2 x 2310 for the bit loops of its two exponentiations, and its arithmetic is
  at most `A_q + A_qp1h + sum_(m = 1)^32 (m + 2) = @@SQRT_ARITH@@` operations (the exponentiations by `q` and `(q+1)/2` cost @@A_Q@@ and @@A_QP1H@@; the Tonelli-Shanks loop lowers `m` strictly from 32 and its pass with parameter `m` costs `m + 2`; over 4,000 random squares the largest observed arithmetic was @@SQRT_MAX_OBS@@).
  `shift(d)` and `pow(d)` depend on the degree and not on the coefficients (fixed loop counts). They are measured at the exact degree `k_j` (table below) and bounded for every `d <= k_j` by the structure of the code:
  (i) every term of the charge of a step (the plan sizes `N = 3 * 2^a` of the transforms, the lengths of the linear passes) is a nondecreasing function of `d`, and a degree `d <= k/2^i` has plan sizes at most `1/2^i` of those at `k` (the plan is the smallest `3 * 2^a >= 2d - 1`), so one loop step at degree `d <= k/2^i` charges at most `1/2^i` of a step at `k`;
  (ii) the number of loop steps of the powering is `s(d) = 254 - L(d)` where `L(d)`, the number of exponent bits absorbed into the starting monomial, is `floor(log2 d)` or `floor(log2 d) + 1`; so a degree in `(k/2, k]` has at most `s(k) + 2` steps and a degree in `(k/2^(i+1), k/2^i]` at most `s(k) + i + 2`.
  The bound used is `pow_B(k) = pow(k) + 2 P + (s + 2 - u) X`, where `s` is the number of steps, `u` the number of steps with exponent bit 1, `X` the charge of the multiplication by `x` (the extra of a bit-1 step, measured) and `P = (loop charge - u X)/s` bounds the charge of any other step;
  the extra `X` is charged in all `s + 2` steps. For `d <= 47` the Taylor shift (`n <= 48`) and, for `d <= 40`, the powering are schoolbook variants whose charges are increasing in `d`: the levels with `k_j <= 47` are charged by the maximum over all degrees `3 <= d <= k_j` of
  `t(d) (shift(d) + pow(d) + gcd_bound(d, d-1) + 13) + 17 + div_bound(d)` with the calibrated charge of that exact degree, and a level with `k_j > 47` is charged the larger of its own value and the same maximum over `3 <= d <= 47` (a polynomial of that level can be small).
  The Taylor shift at `k_j >= 95` is bounded by its measured charge (nondecreasing in `d`; it exceeds the schoolbook charge at `d = 47`).

@@LEDGER_TABLE@@

Worst case of one attempt: both families are run to the end of stage D (family 0 yields nothing), family 1 runs stage F at the worst degrees.
`@@WORST_FORMULA@@ = @@WORST_TOTAL@@` operations `= @@WORST_UNITS@@` units, `time_log2 = @@TIME_LOG2_EXACT@@`, claimed as `@@TIME_LOG2@@` (rounded up).
(A run that isolates a root in the first family stops there and charges about @@TYPFIRST@@ operations, summing the stage charges of the logs; a run that goes through both families and finds no partner charges about @@TYPICAL@@ operations. Both are below the worst case because the root isolation stage is small when the number of roots is small.)

@@LEDGER_PY@@

## 8. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer. The largest live set is in the powering stage (stage C, and the same schedule inside stage F) at `m = D = 390625`:
`Y` (`3 * 2^18` elements, 25,165,824 bytes), `tmp` (`2^18` elements, 8,388,608), `MU` (390,624 elements, 12,499,968), the modulus `g` and the result (2 x 12,500,000 bytes), the twiddle table (`2^17` elements, 4,194,304). Tracked peaks: main run @@PEAK_MAIN@@ bytes;
the stages of the worst-case root isolation at `d = D` (calibration, `calib`): Taylor shift @@PEAK_SHIFT@@, powering @@PEAK_POW@@ bytes (absolute peak), the gcd stage (two inputs, two working copies, one output) @@PEAK_GCD@@; the largest is @@HEAP_PEAK@@ bytes.
To the heap peak we add the static image of the executable (code, constants and tables: @@STATIC_DESC@@), a stack bound of 65,536 bytes and 4,096 bytes for the allocator's own metadata:
`@@MEM_BYTES@@` bytes `= 2^@@MEM_LOG2@@`. The memory penalty is `max(0, @@MEM_LOG2@@ - 20) = @@MEM_PEN@@`.
Not counted, as they are not part of the abstract program: the dynamic C library and loader mappings and kernel structures of the host process.
The program has no stored advice and no precomputed data beyond what it computes itself.

## 9. Success probability

The random experiment: the program draws the words of the sampler and the shifts `c` of stage F; all are independent and uniform (the cost model has independent uniform random 256-bit words as a primitive; the executed program uses a 64-bit xorshift generator, and the claim uses the idealisation).

**Theorem.** One attempt outputs a verified collision with probability at least `(p/(2p-1) - 2^-128)(1 - 2^-35) > 0.4999999999`.
Proof. (1) Sampling. The words `w` are uniform on `[0, 2^256)`; conditioned on `w < 2p - 1` the word is uniform on `[0, 2p-1)`. Each word is accepted with probability `(2p-1)/2^256 >= 1/2`, so 128 words fail with probability at most `2^-128`.
The map `w -> (family, W)` of stage A is a bijection of `[0, 2p-1)` onto `U` (`w < p`: `W = w` in `C_0`; `w >= p`: `W` runs over `F_p \ {W1*}` in `C_1`; `C_0 u C_1` with `I` counted once as the member of `C_0`). So `x` is uniform on `U`.
(2) Lemma A: with probability at least `p/(2p-1)` the point `x` has a partner in `U`. For such `x`, the partner is the input of a root of `F_0` or `F_1` that is not removed in stage E (section 5). Stage D computes the product `G` of all distinct roots exactly (deterministic, with no assumption).
So for the first family `h` whose `G` has a root left, stage F is run on a polynomial of degree between 1 and `D` that is a product of distinct linear factors, and for the other branch the stage is not needed. (3) Lemma B and its consequence: given `G`, stage F fails with probability at most `17 * 2^-39.99 < 2^-35` (the zero shifts counted in section 4.1 included)
over the shifts, whatever `G` is. The randomness of stage F is independent of `x`. So `P(success) >= (p/(2p-1) - 2^-128)(1 - 2^-35) > 0.4999999999`, because `p/(2p-1) > 1/2`, so the product exceeds `0.5 (1 - 2^-35) - 2^-128 > 0.4999999999`, which is the claim `0.4999999999`. QED

What the theorem uses and does not use. It uses only: the algebra of section 2 (the families, their sizes, the single common input, the degree bound that makes interpolation exact), the counting lemma, Weil's bound for multiplicative character sums, and independent uniform random words.
It uses no measurement and no assumption about the polynomials `f_0, f_1`, their roots, or the number of preimages of any value. Every halt of the program belongs to the failure events counted above; none of the cost bounds of section 7 can be exceeded.

**H1 (supporting).** The charges of section 6 describe the executed program: the instrumentation counts each executed field operation, each element load/store with its address operation, every loop iteration and the stated index and control operations. The 16-element register block is the one structural assumption.
**H2 (supporting).** Structure of the charge of the Taylor shift and of the powering (section 7, stage F): each term of the charge of one step is a nondecreasing function of the degree, halving the degree at least halves the charge of a step (the transform plans halve), and the number of steps of the powering varies by at most 1 with
`floor(log2 d)` (and at most 2 beyond the measured degree of a level). This is a statement about the code, checked at the calibrated degrees (the measured per-step charges roughly double with each doubling of the degree), and it enters only the worst-case time ledger of a branch that is needed with probability below `2^-35` beyond a level of degree 3,
and not the probability.

## 10. What is and is not provided

* Provided: the algebraic derivation (section 2), the counting and character-sum proofs (sections 3, 4.1, 9), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 11), @@N_CERT@@ machine-checked collision certificates (`certificates/`, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* How the certificates were produced. The machine on which the long runs were made (24 threads, no error-correcting memory) produced intermittent arithmetic faults in the memory-bound classical gcd and, less often, in the powering: runs of `twofam` on a sampled `x` of family 0 returned a gcd of degree 0, which is impossible because `x` itself is a root, and a re-check of the same data
  found a state of the Euclid sequence that did not vanish at the known root. The certificates were therefore produced by `certrun.c` (section 11), which calls the same stage functions of `twofam.c` and differs in three ways, none of which is part of the charged program: it processes the family of `x` first; for that family, where the root of `x` is known,
  it checks after the build, after the powering and every 1000 eliminations of the gcd that the polynomials vanish at that root, and repeats or rolls back to the last checkpoint when they do not (the rollbacks are printed in its logs); its charges are not used in any ledger. A fault cannot produce a wrong certificate, because every certificate is two inputs whose digests are compared by the organizer's hash.
  The ledger numbers of the data-independent stages come from runs of `twofam` itself (the logs agree to the last digit across all runs). The same source was also run end to end at `r = 1` (D = 78125) as a check of the small case.
* The package contains only the certificates, so the C source is part of this document (section 11) as text, and the program reads no input file. The counts of section 7 are the output of that source compiled with `gcc -O3` and run as `twofam 2 <seed>`; the calibrations as `calib <d>...`.
* The worst case of stage F is charged although it has not been observed: it would need a value `y` with a very large number of preimages in the sampled family. It is derived, not run end to end; the components were run at the sizes of the levels (`calib`) and the compositions were run on synthetic inputs up to degree 3000 (`test_split`). The same source at `r = 1` was run end to end as a check of the small case.
* The cost claim assumes the model of section 6; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.

## 11. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters. Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: @@FILE_ORDER@@.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs. `test_split.c` and `calib.c` are the test and calibration programs named above; `certrun.c` is the driver used to produce the certificates (section 10).

@@APPENDIX@@
