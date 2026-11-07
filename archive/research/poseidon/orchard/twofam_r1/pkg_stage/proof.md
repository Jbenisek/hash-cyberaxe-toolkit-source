# Orchard Poseidon, r = 1: two input families, a counting argument for the success probability, root isolation (exact ledger)

## 1. Claim

Target: `poseidon-orchard-r1-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, one partial round 4, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = 31.331` in target-compression units (`C(1) = 237` primitive operations per unit): the worst-case total of one attempt of the program,
  every executed operation charged (sections 6 and 7); every data-dependent stage is charged at a bound that is derived in section 7 and that the program checks while it runs.
* `memory_log2_bytes = 24.028` (`17,097,311` bytes, section 8), so the normalized cost is `31.331 + 4.028 = 35.359`.
* `success_probability = 0.4999999999`: one attempt. The probability is a theorem of section 9 and does not rest on a sample, a model of the digest polynomial or a heuristic about it:
  a counting (pigeonhole) argument shows that a uniformly drawn point of a set of `2p - 1` inputs has a partner with the same digest with probability at least `p/(2p - 1) > 1/2`;
  the program then finds a partner with certainty except for a bounded failure probability of the root-isolation step, at most `2^-36`, and of the sampler, at most `2^-127`.
* The method (two free rounds on a line, so that the digest is a univariate polynomial of degree `5^7`) is a known approach. What is new here is only the use of two such lines and the resulting probability argument.
* The collisions stored in `certificates/` (4 pairs, each from a separate attempt of this program) are outputs of this program. They check the construction at the
  selected target with the organizer's hash; the cost and probability claims do not use them.

## 2. Two families of inputs on which the digest is a polynomial of degree 5^7

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

2.4 The digest polynomial. Rounds 2, 3 (full), 4 (partial), 60, 61, 62, 63 (full) put seven S-box layers on top of the affine map `W -> alpha + beta W`; the digest is row 0 of the last MDS. So the digest of the input of `C_j` with parameter `W` is
`f_j(W)` with `deg f_j <= 5^7 = D = 78125`. (In the program, `tail_eval` computes `f_j(W)`.) The leading coefficient of `f_j` is nonzero on the deployed constants; the program computes it at every attempt and halts if it is zero (it never was). So `deg f_j = D` exactly.
Interpolation is exact: `D + 1 <= N = 98304 = 3 * 2^15` evaluations at the `N`-th roots of unity determine `f_j` (a transform of size `N` divides `p - 1 = 2^32 * 3 * q`).

2.5 The two families meet in exactly one input. `C_0` and `C_1` are lines in the `(U, V)` plane with directions `(a_0, b_0)`, `(a_1, b_1)`; the determinant `a_1 b_0 - a_0 b_1` is nonzero (a minor of the MDS), so the lines meet in exactly one point `I`.
The program computes the two parameters `W0*`, `W1*` of `I` (stage "two line setups + intersection"); the self-test of the source (`twofam selftest`) checks that both give the same canonical input and that `f_0(W0*) = f_1(W1*)` equals the reference hash of that input.
Hence `|C_0 u C_1| = 2p - 1`.

## 3. Lemma A (counting)

Let `H` be the digest map from `U = C_0 u C_1` (`|U| = 2p - 1`) to `F_p`. Call `u in U` isolated if no other `u' in U` has `H(u') = H(u)`. If `s` is the number of isolated points, then `s <= p - 1`.
Proof. The `s` isolated points have `s` distinct digests, so `s <= p`. If `s = p`, every element of `F_p` is the digest of an isolated point, so no other point of `U` exists, and `|U| = p`, contradicting `|U| = 2p - 1 > p`. So `s <= p - 1`. Therefore a uniformly drawn `x in U` has a partner
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
  B  F := (f_h - y) / lead, monic of degree D: 98304 evaluations of the family (units) + one inverse NTT of size 98304
  C  R := W^p mod F, then R := R - W        (lean NTT schedule of section 6.2; exponent p)
  D  G := gcd(F, R) (classical Euclid), R = W^p - W mod F;   G = gcd(F, W^p - W) = the product of (W - root) over the distinct roots of F in F_p
  E  remove from G the roots that are x itself: W (if h is the family of x) and, if x = I, also W1* (family 1)       [exact division by W - root]
  F  if deg G >= 1: isolate one root W' of G (section 4.1), and stop
output: x' := map_back(h, W'); verify that the two reference hashes of x and x' agree and that x' != x
```
Halts. The program ends early in exactly two ways that can happen with positive probability: the sampler uses up its 128 words (probability at most `2^-128`, section 9) and a level of the root isolation has no proper split after its `t(d)` tries (probability at most `2^-36` over all levels, section 4.1). Every other test that ends the program
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

**Lemma B.** Let `G` be a monic product of `d >= 3` distinct linear factors over `F_p`, `d <= 2^17`, and `c` uniform in `[0, 2^254)`. The probability that `deg gcd(G(Z - c), Z^((p-1)/2) - 1) in {0, d}` is at most `2^(1-d) + 2^-100`.
Proof. Let `r_1..r_d` be the roots, `chi` the quadratic character (`chi(0) = 0`), `E = {-r_i}`. The degree of the gcd is `#{i : chi(r_i + c) = 1}`. For `c not in E`,
`[chi(r_i + c) = 1 for all i] = prod_i (1 + chi(r_i + c))/2 = 2^-d sum_{S} chi(prod_{i in S} (r_i + c))` and `[chi(r_i + c) = -1 for all i] = 2^-d sum_S (-1)^|S| chi(prod_{i in S} (r_i + c))`.
For `S` nonempty, `prod_{i in S}(Z + r_i)` is squarefree of degree `|S|`, so by Weil's bound `|sum_{c in F_p} chi(prod_{i in S}(c + r_i))| <= (|S| - 1) sqrt(p)` (the sum is 0 for `|S| = 1`). Summing over `c not in E` costs at most `d` more per term.
So the number of `c in F_p` with all `chi = 1`, and likewise with all `chi = -1`, is at most `p/2^d + (d-1) sqrt(p) + d`, and the `c in E` add at most `d`. Dividing by `2^254 >= p (1 - 2^-128)` (the draw is uniform on a subset of `F_p`, so counts of bad values over `F_p` bound the counts over the subset):
probability `<= 2^(1-d) (1 + 2^-127) + 2 (d-1) 2^-127 + 3d 2^-254 <= 2^(1-d) + 2^-100`. QED.

Consequence. A level of degree `d` fails with probability at most `(2^(1-d) + 2^-100)^t(d) < 2^-39.99`: for `d > 40` take `t = 1` and `2^(1-d) <= 2^-40`; for `3 <= d <= 40`, `t(d) (d - 1) >= 40` gives at most `2^-40 (1 + 2^-61)^t`. Degrees halve, so a polynomial of degree at most `D = 78125` passes through at most 15 levels with `d >= 3`
(78125, 39062, 19531, 9765, 4882, 2441, 1220, 610, 305, 152, 76, 38, 19, 9, 4). Over all levels the failure probability is below `15 * 2^-39.99 < 2^-36`, and a shift `c = 0` (Taylor shift needs `1/c`), probability `2^-254` per try, is absorbed (fewer than 100 tries in all). The number of tries of a run is at most the sum of `t(d)` over these levels (for the worst schedule 35 tries).

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
* the reduced permutation evaluations of stage B and the evaluation of `y`: 237 each (`C(1)`), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
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

## 7. Ledger (primitive operations; `C(1) = 237`)

The counts of the data-independent stages are the exact totals of the instrumented execution (`arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 237-operation unit charges).
The three stages whose cost depends on the data are charged at derived bounds, which are not observations:

* **Stage D (gcd).** `gcd_cl(da, db)` with `da = D`, `db = D - 1`. Let `S0 = da + db`. Every elimination step of the program lowers `dA + dB` by at least 1 and its inner loop runs `dB <= (dA + dB)/2` times, so the inner iterations total at most `floor(S0^2/4)`;
  the eliminations number at most `S0 + 1`, the passes (one inversion each) at most `S0 + 1`, and the degree scans lower `dA` by `S0 + 1` in total. An inner iteration is charged 12 (2 arithmetic, 2 loads, 1 store, 7 control), an elimination 25 + 11 (`dA - nd`), a pass 330 + 1 + 2310 + 8 plus the loads, setup and final normalisation (function `gcd_cost_bound`, section 11).
  The program asserts `charged <= bound` at every gcd it runs (the root isolation and the main stage); the bound is 73,664,065,176 operations for `(D, D-1)`, against 73,454,999,982 charged in the runs of this ledger. The ratio of charge to bound grows toward 1 with the degree (0.54 at `d = 17`, 0.85 at `d = 1000`, 0.93 at `d = 3000` in the tests), because the bound is the cost of a normal remainder sequence.
* **Stage E.** At most `d + 1` coefficients are copied and at most two roots deflated: 2,265,633 operations at `d = D` (measured at that size; the cost is linear in `d` and independent of the data).
* **Stage F (root isolation), worst case.** The levels of section 4.1 start at degree at most `D` and halve. For each level of degree `d` and each of its `t(d)` tries the charge is `shift(d) + pow(d) + gcd_bound(d, d-1) + div_bound(d)` plus the random word and control (about 60 operations),
  where `shift(d)` (the Taylor shift) and `pow(d)` (`Z^((p-1)/2) mod G`) are measured at that exact degree on random input (their cost does not depend on the coefficients), `gcd_bound` is the bound above, and `div_bound(d)` is the maximum over `a` in `(d/2, d)` of `div_cost_bound(d + 1, a + 1)`
  (the division of `G` by `A` happens only when `deg A > d/2`; function `div_cost_bound`, derived in section 11 and asserted at every division). The last level (`d = 2`) costs 16,000 operations (one square root with its control charge, one inversion).
  The cost of a level is nondecreasing in `d` up to the exponent length, which varies by one step per power of two (0.4 %): every measured value is therefore multiplied by 1.02 (the table lists the measured values; the 1.02 factor is applied in its last column).

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table (once) | 33,742 | 241,330 | 275,072 | no |
| setup: two lines, the common input I | 1,131 | 12,489 | 13,620 | no |
| A: sampler (at most 128 words) and `y = H(x)` | - | - | 1,900 allowance (observed 279-291) | derived: 128 x 12 + 42 + 237 |
| B (per family): 98304 evaluations (units) + inverse NTT 98304 + normalisation | 2,525,873 | 61,471,246 | 63,997,119 | no |
| C (per family): `W^p mod F` (m = 78125, 238 steps) | 7,533,028,466 | 85,123,176,368 | 92,656,204,834 | no |
| D (per family): classical gcd, derived bound for (78125, 78124) | - | - | 73,664,065,176 (charged in the run: 73,454,999,982) | yes: bound |
| E (per family): copy of G and two deflations at d = 78125 | - | - | 2,265,633 | linear in d |
| F: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | 307,364,430,728 | yes: bound |
| map back and two reference hashes (success path) | - | - | 200,000 allowance (observed 27,480) | no |

Worst case of the root isolation (stage F) over the level schedule of section 4.1 (starting degree 78125):

| d | tries t(d) | shift(d) | pow(d) | gcd bound | div bound | t(d) x (1.02 (shift + pow) + gcd + div + 100) |
|---:|---:|---:|---:|---:|---:|---:|
| 78,125 | 1 | 205,854,187 | 92,268,713,832 | 73,664,065,176 | 18,312,541,751 | 186,300,666,407 |
| 39,062 | 1 | 101,431,198 | 45,566,840,428 | 18,521,015,604 | 4,578,518,297 | 69,681,171,060 |
| 19,531 | 1 | 50,014,440 | 22,481,193,667 | 4,682,989,608 | 1,144,880,612 | 28,809,702,590 |
| 9,765 | 1 | 24,572,201 | 10,767,609,193 | 1,196,996,376 | 286,317,371 | 12,491,338,869 |
| 4,882 | 1 | 10,869,940 | 4,809,106,672 | 312,372,564 | 71,628,947 | 5,300,377,756 |
| 2,441 | 1 | 5,345,826 | 2,366,250,900 | 84,685,848 | 17,940,377 | 2,521,654,986 |
| 1,220 | 1 | 2,633,333 | 1,162,898,377 | 24,451,476 | 4,498,994 | 1,217,792,915 |
| 610 | 1 | 1,293,839 | 550,923,249 | 7,761,876 | 1,134,539 | 572,157,945 |
| 305 | 1 | 562,631 | 238,724,294 | 2,765,976 | 289,541 | 247,128,281 |
| 152 | 1 | 279,902 | 116,896,951 | 1,100,724 | 75,872 | 120,697,087 |
| 76 | 1 | 141,754 | 57,207,270 | 482,388 | 21,950 | 59,000,443 |
| 38 | 2 | 74,440 | 12,680,407 | 225,204 | 7,985 | 26,486,466 |
| 19 | 3 | 11,225 | 3,145,447 | 109,608 | 4,256 | 10,001,310 |
| 9 | 5 | 7,093 | 694,997 | 52,248 | 3,161 | 3,858,205 |
| 4 | 14 | 5,926 | 133,897 | 24,468 | 2,834 | 2,380,308 |
| quadratic end (d = 2) and level control | | | | | | 16,100 |
| total | 35 | | | | | 307,364,430,728 |

Worst case of one attempt: both families are run to the end of stage D (family 0 yields nothing), family 1 runs stage F at the worst degrees.
`init + setup + sampler allowance + 2 x (B + C + D bound + E) + F bound + final allowance = 275,072 + 13,620 + 1,900 + 2 x (63,997,119 + 92,656,204,834 + 73,664,065,176 + 2,265,633) + 307,364,430,728 + 200,000 = 640,137,986,844` operations `= 2,701,004,163.9` units, `time_log2 = 31.33085`, claimed as `31.331` (rounded up).
(A run that isolates a root in family 0 stops there and charges about 166,175,528,585 operations in the logs; a run that goes through both families and finds no partner charges about 332,350,650,229 operations. Both are below the worst case because the root isolation stage is small when the number of roots is small.)

```python
from math import log2
C = 237
init, setup, sampler, final = 275072, 13620, 1900, 200000
build, power, gcd_bound, remove = 63997119, 92656204834, 73664065176, 2265633
split = 307364430728
N = init + setup + sampler + 2 * (build + power + gcd_bound + remove) + split + final
print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % log2(N / C))
```


## 8. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer. The largest live set is in the powering stage (stage C, and the same schedule inside stage F) at `m = D = 78125`:
`Y` (`3 * 2^16` elements, 6,291,456 bytes), `tmp` (`2^16` elements, 2,097,152), `MU` (1,249,952 x 2 = 2,499,904), the modulus `g` and the result (2 x 2,500,000 bytes), the twiddle table (`2^15` elements, 1,048,576). Tracked peaks: main run 16,937,184 bytes;
the stages of the worst-case root isolation at `d = D` (calibration, `calib`): Taylor shift 16,534,400, powering 16,937,184 bytes above the live arrays, the gcd stage (two inputs, two working copies, one output) 13,548,736; the largest is 16,937,184 bytes.
To the heap peak we add the static image of the executable (code, constants and tables: text 82,967 + data 752 + bss 6,776 = 90,495 bytes), a stack bound of 65,536 bytes and 4,096 bytes for the allocator's own metadata:
`17,097,311` bytes `= 2^24.028`. The memory penalty is `max(0, 24.028 - 20) = 4.028`.
Not counted, as they are not part of the abstract program: the dynamic C library and loader mappings and kernel structures of the host process.
The program has no stored advice and no precomputed data beyond what it computes itself.

## 9. Success probability

The random experiment: the program draws the words of the sampler and the shifts `c` of stage F; all are independent and uniform (the cost model has independent uniform random 256-bit words as a primitive; the executed program uses a 64-bit xorshift generator, and the claim uses the idealisation).

**Theorem.** One attempt outputs a verified collision with probability at least `p/(2p-1) (1 - 2^-36) - 2^-127 > 0.4999999999`.
Proof. (1) Sampling. The words `w` are uniform on `[0, 2^256)`; conditioned on `w < 2p - 1` the word is uniform on `[0, 2p-1)`. Each word is accepted with probability `(2p-1)/2^256 >= 1/2`, so 128 words fail with probability at most `2^-128`.
The map `w -> (family, W)` of stage A is a bijection of `[0, 2p-1)` onto `U` (`w < p`: `W = w` in `C_0`; `w >= p`: `W` runs over `F_p \ {W1*}` in `C_1`; `C_0 u C_1` with `I` counted once as the member of `C_0`). So `x` is uniform on `U`.
(2) Lemma A: with probability at least `p/(2p-1)` the point `x` has a partner in `U`. For such `x`, the partner is the input of a root of `F_0` or `F_1` that is not removed in stage E (section 5). Stage D computes the product `G` of all distinct roots exactly (deterministic, with no assumption).
So for the first family `h` whose `G` has a root left, stage F is run on a polynomial of degree between 1 and `D` that is a product of distinct linear factors, and for the other branch the stage is not needed. (3) Lemma B and its consequence: given `G`, stage F fails with probability at most `15 * 2^-39.99 + 2^-247 < 2^-36`
over the shifts, whatever `G` is. The randomness of stage F is independent of `x`. So `P(success) >= (p/(2p-1) - 2^-128)(1 - 2^-36) >= 0.5 (1 - 2^-36) - 2^-127`, which exceeds `0.4999999999`. QED

What the theorem uses and does not use. It uses only: the algebra of section 2 (the families, their sizes, the single common input, the degree bound that makes interpolation exact), the counting lemma, Weil's bound for multiplicative character sums, and independent uniform random words.
It uses no measurement and no assumption about the polynomials `f_0, f_1`, their roots, or the number of preimages of any value. Every halt of the program belongs to the failure events counted above; none of the cost bounds of section 7 can be exceeded.

**H1 (supporting).** The charges of section 6 describe the executed program: the instrumentation counts each executed field operation, each element load/store with its address operation, every loop iteration and the stated index and control operations. The 16-element register block is the one structural assumption.
**H2 (supporting).** For the levels of stage F other than the first, the charge of a level is bounded by the measured cost at the maximum degree of that level (2 % margin, section 7). This enters only the worst-case ledger of a branch that has probability below `2^-36` of being needed beyond a level of degree 3,
and not the probability.

## 10. What is and is not provided

* Provided: the algebraic derivation (section 2), the counting and character-sum proofs (sections 3, 4.1, 9), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 11), 4 machine-checked collision certificates (`certificates/`, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package contains only the certificates, so the C source is part of this document (section 11) as text, and the program reads no input file. The counts of section 7 are the output of that source compiled with `gcc -O3` and run as `twofam 1 <seed>`; the calibrations as `calib <d>...`.
* The worst case of stage F is charged although it has not been observed: it would need a value `y` with a very large number of preimages in the sampled family. It is derived, not run end to end; the components were run at the sizes of the levels (`calib`) and the compositions were run on synthetic inputs up to degree 3000 (`test_split`).
* The cost claim assumes the model of section 6; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.

## 11. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters. Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: `common.h`, `common.c`, `pallas.h`, `pallas.c`, `pallas_consts.h`, `attack.h`, `ntt.c`, `poly.c`, `lean.c`, `line.c`, `split.c`, `twofam.c`, `test_split.c`, `calib.c`.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs. `test_split.c` and `calib.c` are the test and calibration programs named above.

### common.h

```c
/* Shared definitions for the Orchard odd-part root finder.  All field arithmetic goes through pallas.c
 * (counted: add, sub, mul, sqr).  Additional charged primitives are counted here: 256-bit loads (ld), stores (st),
 * loop-control / index operations (ctl) and random words (rnd).  See SOLVE.md for the machine model. */
#ifndef COMMON_H
#define COMMON_H
#include "pallas.h"
#include <stdint.h>
#include <stddef.h>
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

typedef struct { uint64_t ld, st, ctl, rnd, perm; } xcnt_t;   /* perm: reduced permutation evaluations charged as C(r) primitive operations each */
extern xcnt_t X;
/* Counting rule: every executed operation of the code below is charged where it is written.
 *  - LD(n)/ST(n): n element loads/stores; each is charged together with one address-formation operation (counted as control).
 *  - a loop that runs n iterations: 3n+2 control operations (per iteration the index update, the bound comparison and the
 *    conditional branch; on exit one more comparison and branch).  loopc(n) charges exactly this.
 *  - every other executed shift, mask, add, multiply, modulo, comparison or branch of index and control code: 1 each via CTL(). */
#define LD(n)  do { X.ld  += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
#define ST(n)  do { X.st  += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
#define CTL(n) (X.ctl += (uint64_t)(n))
static inline void loopc(size_t nel) { X.ctl += 3 * (uint64_t)nel + 2; }
#define INV_CTL 2310     /* control of fp_inv outside the per-operation stages: 253 iterations x 9 (index update, compare, branch, word and bit selection, bit test) + 3 x 8 for the search of the top bit */

typedef struct { uint64_t add, sub, mul, sqr, ld, st, ctl, rnd, perm; } snap_t;
snap_t snap(void);
snap_t snap_sub(snap_t a, snap_t b);
uint64_t snap_arith(snap_t s);           /* add+sub+mul+sqr */
uint64_t snap_total(snap_t s);           /* everything charged */
void snap_restore(snap_t s);             /* restore counters (used to exclude test/debug-only work) */

/* ---- memory accounting (every buffer goes through xalloc) */
void *xalloc(size_t bytes);
void  xfree(void *p);
extern size_t mem_cur, mem_peak;
void  mem_reset_peak(void);

/* ---- field helpers */
#define NEW_FP(n) ((fp *)xalloc((size_t)(n) * sizeof(fp)))

/* ---- NTT engine (ntt.c) */
typedef struct {
    int rows;          /* 1: plain 2^a transform; 3: Good-Thomas radix-3 x 2^a */
    int a;             /* log2 of row length */
    size_t n, N;       /* row length, total length */
    int shift;         /* amax - a (twiddle table stride shift) */
    int npass, kk[8];  /* layers per pass; last pass is the one fused with pointwise ops */
    int c0;            /* radix-3 rotation constant (rows==3) */
} plan_t;

void   ntt_init(int amax);               /* roots of unity + twiddle table (counted) */
void   ntt_free(void);
plan_t make_plan(int rows, int a);
plan_t plan_for_len(size_t len, int allow3); /* smallest {2^a, 3*2^a} >= len */
size_t ntt_table_bytes(void);

/* forward transform: src[off .. off+len) (zero beyond) -> dst (layout order); dst may equal src when off==0 */
void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len);
/* inverse (unnormalised: result = N * coefficients), in place; only positions < outlen are produced */
void ntt_inv(const plan_t *P, fp *buf, size_t outlen);
/* fused convolution kernels (unnormalised cyclic convolution of length N, result = N * (x*y mod x^N-1)) */
void conv_sq (const plan_t *P, fp *buf, size_t len, size_t outlen);
void conv_mulc(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, const fp *C, size_t outlen);
/* point of layout position (row, pos) i.e. exponent k -> index in dst */
size_t layout_index(const plan_t *P, size_t k);
void   plan_theta(const plan_t *P, fp *theta);      /* theta such that the transform evaluates at theta^k (counted-free, uses table) */

extern fp ntt_w3, ntt_invN_cache;
/* lean variant: second operand B (compact, lenB coefficients, cyclic offset boff) transformed row by row into tmp (P->n entries) */
void   conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                     const fp *B, size_t lenB, size_t boff, size_t outlen);
void   conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                    const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen);
plan_t plan3_for_len(size_t len);                    /* smallest 3*2^a >= len */

/* ---- polynomial tools (poly.c) */
typedef struct { fp *c; size_t len; } pv;   /* view: len coefficients, len==0 -> zero polynomial; c[len-1] != 0 when normalised */
void poly_mul(fp *r, const fp *a, size_t la, const fp *b, size_t lb);  /* r has la+lb-1 entries, counted */
void poly_mul_naive(fp *r, const fp *a, size_t la, const fp *b, size_t lb);
void plan_invN(const plan_t *P, fp *out);              /* 1/N as a field element (cached, counted once) */

/* ---- modular exponentiation x^E mod g (lean.c) */
void powx_lean(fp *F, const fp *g, size_t m, const uint64_t E[4], int quiet);


#endif
```

### common.c

```c
#include "common.h"
xcnt_t X;
size_t mem_cur = 0, mem_peak = 0;

snap_t snap(void) {
    snap_t s; s.add = fp_cnt.add; s.sub = fp_cnt.sub; s.mul = fp_cnt.mul; s.sqr = fp_cnt.sqr;
    s.ld = X.ld; s.st = X.st; s.ctl = X.ctl; s.rnd = X.rnd; s.perm = X.perm; return s;
}
snap_t snap_sub(snap_t a, snap_t b) {
    snap_t s; s.add = a.add - b.add; s.sub = a.sub - b.sub; s.mul = a.mul - b.mul; s.sqr = a.sqr - b.sqr;
    s.ld = a.ld - b.ld; s.st = a.st - b.st; s.ctl = a.ctl - b.ctl; s.rnd = a.rnd - b.rnd; s.perm = a.perm - b.perm; return s;
}
uint64_t snap_arith(snap_t s) { return s.add + s.sub + s.mul + s.sqr; }
uint64_t snap_total(snap_t s) { return snap_arith(s) + s.ld + s.st + s.ctl + s.rnd + s.perm; }
void snap_restore(snap_t s) {
    fp_cnt.add = s.add; fp_cnt.sub = s.sub; fp_cnt.mul = s.mul; fp_cnt.sqr = s.sqr;
    X.ld = s.ld; X.st = s.st; X.ctl = s.ctl; X.rnd = s.rnd; X.perm = s.perm;
}

/* tracked allocation: a 64-byte header holds the size */
void *xalloc(size_t bytes) {
    void *p = NULL;
    if (posix_memalign(&p, 64, bytes + 64)) { fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    *(size_t *)p = bytes;
    mem_cur += bytes; if (mem_cur > mem_peak) mem_peak = mem_cur;
    return (char *)p + 64;
}
void xfree(void *q) {
    if (!q) return;
    void *p = (char *)q - 64; mem_cur -= *(size_t *)p; free(p);
}
void mem_reset_peak(void) { mem_peak = mem_cur; }
```

### pallas.h

```c
/* Pallas base field (p = 0x4000...224698fc094cf91b992d30ed00000001), 4x64-bit Montgomery representation,
 * exact operation counters, and the Orchard P128Pow5T3 reduced hash. Not constant time. */
#ifndef PALLAS_H
#define PALLAS_H
#include <stdint.h>
#include <stddef.h>

typedef struct { uint64_t l[4]; } fp;          /* Montgomery form, always fully reduced (< p), little-endian limbs */

/* ---- exact counters (global, single-threaded). Charged primitives = add + sub + mul + sqr.
 * inv/pow/sqrt "calls" are informational ONLY: their constituent ops are already counted in add/sub/mul/sqr. */
typedef struct {
    uint64_t add, sub, mul, sqr;               /* primitive field operations actually executed */
    uint64_t inv_calls, pow_calls, sqrt_calls; /* informational, not charged separately */
} fp_counters;
extern fp_counters fp_cnt;
void     fp_counters_reset(void);
uint64_t fp_prim_total(void);                  /* add+sub+mul+sqr  (each = 1/C(r) target-compression units) */

/* ---- conversions (I/O encodings; NOT counted: a program may store constants/inputs in Montgomery form) */
void fp_from_limbs(fp *r, const uint64_t v[4]);    /* canonical integer limbs (< p) -> Montgomery */
void fp_to_limbs(uint64_t v[4], const fp *a);      /* Montgomery -> canonical integer limbs */
int  fp_limbs_canonical(const uint64_t v[4]);      /* 1 iff v < p */
void fp_from_u64(fp *r, uint64_t x);
int  fp_from_hex(fp *r, const char *hex64);        /* 64 hex digits big-endian; returns 0 ok, -1 bad/noncanonical */
void fp_to_hex(char out[65], const fp *a);

/* ---- field operations (each counted) */
void fp_add(fp *r, const fp *a, const fp *b);
void fp_sub(fp *r, const fp *a, const fp *b);
void fp_neg(fp *r, const fp *a);                   /* counted as one sub (0 - a) */
void fp_dbl(fp *r, const fp *a);                   /* counted as one add */
void fp_mul(fp *r, const fp *a, const fp *b);
void fp_sqr(fp *r, const fp *a);                   /* counted as one sqr (a primitive multiplication) */
void fp_pow5(fp *r, const fp *a);                  /* sqr, sqr, mul = 3 primitives */
void fp_pow(fp *r, const fp *a, const uint64_t e[4]); /* left-to-right square-and-multiply, exact count (no op on zero-bit multiplies) */
void fp_inv(fp *r, const fp *a);                   /* a^(p-2); inv(0)=0. Expands to its sqr/mul ops. */
int  fp_sqrt(fp *r, const fp *a);                  /* Tonelli-Shanks (2-adicity 32); 1 and a root if a is a square (0 -> 0), else 0 */
int  fp_legendre(const fp *a);                     /* 0, 1, -1 via a^((p-1)/2); counted */

/* ---- uncounted helpers (comparisons are NOT charged here; charge them yourself if your algorithm needs them) */
int  fp_eq(const fp *a, const fp *b);
int  fp_is_zero(const fp *a);
void fp_set_zero(fp *r);
void fp_set_one(fp *r);

/* ---- Orchard P128Pow5T3, reduced to full rounds 0..3, r partial rounds 4..4+r-1, full rounds 60..63 (0<=r<=56) */
int  poseidon_C(int r);                            /* 216 + 21 r */
void poseidon_perm_r(fp s[3], int r);              /* faithful reference arithmetic: 27*8 + 21*r primitives */
int  poseidon_hash_r(const uint64_t nk[4], const uint64_t rho[4], int r, uint64_t out[4]); /* canonical limbs; 0 ok, -1 invalid */
void poseidon_hash_r_fp(fp *out, const fp *nk, const fp *rho, int r); /* state [nk, rho, 2^65], returns state[0] */
#endif
```

### pallas.c

```c
#include "pallas.h"
#include "pallas_consts.h"
#include <string.h>
#include <stdio.h>

typedef unsigned __int128 u128;
fp_counters fp_cnt;
void fp_counters_reset(void) { memset(&fp_cnt, 0, sizeof fp_cnt); }
uint64_t fp_prim_total(void) { return fp_cnt.add + fp_cnt.sub + fp_cnt.mul + fp_cnt.sqr; }

/* ---------- raw (uncounted) limb helpers ---------- */
static int geq_p(const uint64_t a[4]) {
    for (int i = 3; i >= 0; i--) { if (a[i] > PALLAS_P[i]) return 1; if (a[i] < PALLAS_P[i]) return 0; }
    return 1;
}
static void sub_p(uint64_t a[4]) {
    uint64_t b = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a[i] - PALLAS_P[i] - b; a[i] = (uint64_t)d; b = (uint64_t)(d >> 64) & 1; }
}
static void mont_mul_raw(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) {
    uint64_t t[6] = {0, 0, 0, 0, 0, 0};
    for (int i = 0; i < 4; i++) {
        uint64_t carry = 0;
        for (int j = 0; j < 4; j++) { u128 s = (u128)a[i] * b[j] + t[j] + carry; t[j] = (uint64_t)s; carry = (uint64_t)(s >> 64); }
        u128 s = (u128)t[4] + carry; t[4] = (uint64_t)s; t[5] = (uint64_t)(s >> 64);
        uint64_t m = t[0] * PALLAS_INV;
        s = (u128)m * PALLAS_P[0] + t[0]; carry = (uint64_t)(s >> 64);
        for (int j = 1; j < 4; j++) { s = (u128)m * PALLAS_P[j] + t[j] + carry; t[j - 1] = (uint64_t)s; carry = (uint64_t)(s >> 64); }
        s = (u128)t[4] + carry; t[3] = (uint64_t)s; carry = (uint64_t)(s >> 64);
        t[4] = t[5] + carry;
    }
    /* t < 2p here; t[4] is 0 because p < 2^255 */
    r[0] = t[0]; r[1] = t[1]; r[2] = t[2]; r[3] = t[3];
    if (t[4] || geq_p(r)) sub_p(r);
}

/* ---------- conversions ---------- */
int fp_limbs_canonical(const uint64_t v[4]) { return !geq_p(v); }
void fp_from_limbs(fp *r, const uint64_t v[4]) { uint64_t t[4]; mont_mul_raw(t, v, PALLAS_R2); memcpy(r->l, t, 32); }
void fp_to_limbs(uint64_t v[4], const fp *a) { static const uint64_t one[4] = {1, 0, 0, 0}; uint64_t t[4]; mont_mul_raw(t, a->l, one); memcpy(v, t, 32); }
void fp_from_u64(fp *r, uint64_t x) { uint64_t v[4] = {x, 0, 0, 0}; fp_from_limbs(r, v); }
int fp_from_hex(fp *r, const char *hex) {
    uint64_t v[4] = {0, 0, 0, 0};
    for (int i = 0; i < 64; i++) {
        char c = hex[i]; int d;
        if (c >= '0' && c <= '9') d = c - '0'; else if (c >= 'a' && c <= 'f') d = c - 'a' + 10; else if (c >= 'A' && c <= 'F') d = c - 'A' + 10; else return -1;
        int pos = 63 - i;                       /* nibble index from least significant */
        v[pos / 16] |= (uint64_t)d << (4 * (pos % 16));
    }
    if (!fp_limbs_canonical(v)) return -1;
    fp_from_limbs(r, v); return 0;
}
void fp_to_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    snprintf(out, 65, "%016llx%016llx%016llx%016llx", (unsigned long long)v[3], (unsigned long long)v[2], (unsigned long long)v[1], (unsigned long long)v[0]);
}

/* ---------- counted field ops ---------- */
void fp_add(fp *r, const fp *a, const fp *b) {
    fp_cnt.add++;
    uint64_t t[4], c = 0;
    for (int i = 0; i < 4; i++) { u128 s = (u128)a->l[i] + b->l[i] + c; t[i] = (uint64_t)s; c = (uint64_t)(s >> 64); }
    if (c || geq_p(t)) sub_p(t);
    memcpy(r->l, t, 32);
}
void fp_dbl(fp *r, const fp *a) { fp_add(r, a, a); }
void fp_sub(fp *r, const fp *a, const fp *b) {
    fp_cnt.sub++;
    uint64_t t[4], br = 0;
    for (int i = 0; i < 4; i++) { u128 d = (u128)a->l[i] - b->l[i] - br; t[i] = (uint64_t)d; br = (uint64_t)(d >> 64) & 1; }
    if (br) { uint64_t c = 0; for (int i = 0; i < 4; i++) { u128 s = (u128)t[i] + PALLAS_P[i] + c; t[i] = (uint64_t)s; c = (uint64_t)(s >> 64); } }
    memcpy(r->l, t, 32);
}
void fp_neg(fp *r, const fp *a) { fp z; fp_set_zero(&z); fp_sub(r, &z, a); }
void fp_mul(fp *r, const fp *a, const fp *b) { fp_cnt.mul++; uint64_t t[4]; mont_mul_raw(t, a->l, b->l); memcpy(r->l, t, 32); }
void fp_sqr(fp *r, const fp *a) { fp_cnt.sqr++; uint64_t t[4]; mont_mul_raw(t, a->l, a->l); memcpy(r->l, t, 32); }
void fp_pow5(fp *r, const fp *a) { fp t; fp_sqr(&t, a); fp_sqr(&t, &t); fp_mul(r, &t, a); }

void fp_set_zero(fp *r) { memset(r, 0, sizeof *r); }
void fp_set_one(fp *r) { memcpy(r->l, PALLAS_ONE_M, 32); }
int fp_eq(const fp *a, const fp *b) { return memcmp(a->l, b->l, 32) == 0; }
int fp_is_zero(const fp *a) { return (a->l[0] | a->l[1] | a->l[2] | a->l[3]) == 0; }

void fp_pow(fp *r, const fp *a, const uint64_t e[4]) {
    fp_cnt.pow_calls++;
    int top = -1;
    for (int i = 255; i >= 0; i--) if ((e[i / 64] >> (i % 64)) & 1) { top = i; break; }
    if (top < 0) { fp_set_one(r); return; }
    fp base = *a, acc = *a;                    /* leading 1 bit: acc = a, no operation */
    for (int i = top - 1; i >= 0; i--) {
        fp_sqr(&acc, &acc);
        if ((e[i / 64] >> (i % 64)) & 1) fp_mul(&acc, &acc, &base);
    }
    *r = acc;
}
void fp_inv(fp *r, const fp *a) { fp_cnt.inv_calls++; fp_pow(r, a, PALLAS_PM2); }
int fp_legendre(const fp *a) {
    if (fp_is_zero(a)) return 0;
    fp t, one; fp_pow(&t, a, PALLAS_PM1H); fp_set_one(&one);
    return fp_eq(&t, &one) ? 1 : -1;
}
/* Tonelli-Shanks with p-1 = 2^32 * q. Invariant: x^2 = a*t, z has order 2^m, t has order dividing 2^(m-1) iff a is a square. */
int fp_sqrt(fp *r, const fp *a) {
    fp_cnt.sqrt_calls++;
    if (fp_is_zero(a)) { fp_set_zero(r); return 1; }
    fp one; fp_set_one(&one);
    fp z, t, x, b;
    memcpy(z.l, PALLAS_Z_M, 32);                /* z = 5^q, order 2^32 */
    fp_pow(&t, a, PALLAS_Q);                    /* t = a^q   */
    fp_pow(&x, a, PALLAS_QP1H);                 /* x = a^((q+1)/2) */
    unsigned m = 32;
    while (!fp_eq(&t, &one)) {
        unsigned i = 0; fp u = t;
        while (!fp_eq(&u, &one)) { fp_sqr(&u, &u); i++; if (i >= m) return 0; }   /* i == m: t has order 2^m => non-residue */
        b = z;
        for (unsigned k = 0; k + i + 1 < m; k++) fp_sqr(&b, &b);                  /* b = z^(2^(m-i-1)) */
        fp_mul(&x, &x, &b);
        fp_sqr(&z, &b);
        fp_mul(&t, &t, &z);
        m = i;
    }
    *r = x; return 1;
}

/* ---------- Poseidon ---------- */
int poseidon_C(int r) { return 216 + 21 * r; }
static void mds_mul(fp s[3]) {
    fp o[3], t;
    for (int i = 0; i < 3; i++) {
        fp_mul(&o[i], &POSEIDON_MDS_M[i][0], &s[0]);
        fp_mul(&t, &POSEIDON_MDS_M[i][1], &s[1]); fp_add(&o[i], &o[i], &t);
        fp_mul(&t, &POSEIDON_MDS_M[i][2], &s[2]); fp_add(&o[i], &o[i], &t);
    }
    s[0] = o[0]; s[1] = o[1]; s[2] = o[2];
}
static void round_fn(fp s[3], int idx, int full) {
    for (int i = 0; i < 3; i++) fp_add(&s[i], &s[i], &POSEIDON_RC_M[idx][i]);
    if (full) for (int i = 0; i < 3; i++) fp_pow5(&s[i], &s[i]); else fp_pow5(&s[0], &s[0]);
    mds_mul(s);
}
void poseidon_perm_r(fp s[3], int r) {
    for (int i = 0; i < 4; i++) round_fn(s, i, 1);
    for (int i = 0; i < r; i++) round_fn(s, 4 + i, 0);
    for (int i = 60; i < 64; i++) round_fn(s, i, 1);
}
void poseidon_hash_r_fp(fp *out, const fp *nk, const fp *rho, int r) {
    fp s[3]; s[0] = *nk; s[1] = *rho; memcpy(s[2].l, POSEIDON_CAP_M, 32);
    poseidon_perm_r(s, r);
    *out = s[0];
}
int poseidon_hash_r(const uint64_t nk[4], const uint64_t rho[4], int r, uint64_t out[4]) {
    if (r < 0 || r > 56 || !fp_limbs_canonical(nk) || !fp_limbs_canonical(rho)) return -1;
    fp a, b, o; fp_from_limbs(&a, nk); fp_from_limbs(&b, rho);
    poseidon_hash_r_fp(&o, &a, &b, r); fp_to_limbs(out, &o); return 0;
}
```

### pallas_consts.h

```c
/* GENERATED by gen_c_consts.py from the organizer JSON; limbs little-endian, values in Montgomery form */
#ifndef PALLAS_CONSTS_H
#define PALLAS_CONSTS_H
#define PALLAS_INV 0x992d30ecffffffffULL /* -p^{-1} mod 2^64 */
static const uint64_t PALLAS_P[4] = {0x992d30ed00000001ULL,0x224698fc094cf91bULL,0x0000000000000000ULL,0x4000000000000000ULL};
static const uint64_t PALLAS_R2[4] = {0x8c78ecb30000000fULL,0xd7d30dbd8b0de0e7ULL,0x7797a99bc3c95d18ULL,0x096d41af7b9cb714ULL};
static const uint64_t PALLAS_ONE_M[4] = {0x34786d38fffffffdULL,0x992c350be41914adULL,0xffffffffffffffffULL,0x3fffffffffffffffULL};
/* q = (p-1)/2^32, odd */
static const uint64_t PALLAS_Q[4] = {0x094cf91b992d30edULL,0x00000000224698fcULL,0x0000000000000000ULL,0x0000000040000000ULL};
/* (q+1)/2 */
static const uint64_t PALLAS_QP1H[4] = {0x04a67c8dcc969877ULL,0x0000000011234c7eULL,0x0000000000000000ULL,0x0000000020000000ULL};
/* (p-1)/2 */
static const uint64_t PALLAS_PM1H[4] = {0xcc96987680000000ULL,0x11234c7e04a67c8dULL,0x0000000000000000ULL,0x2000000000000000ULL};
/* p-2 */
static const uint64_t PALLAS_PM2[4] = {0x992d30ecffffffffULL,0x224698fc094cf91bULL,0x0000000000000000ULL,0x4000000000000000ULL};
/* Z = 5^q, primitive 2^32-th root of unity (Montgomery form) */
static const uint64_t PALLAS_Z_M[4] = {0xa28db849bad6dbf0ULL,0x9083cd03d3b539dfULL,0xfba6b9ca9dc8448eULL,0x3ec928747b89c6daULL};
static const uint64_t POSEIDON_CAP_M[4] = {0x992d30ed00000001ULL,0x58dd1194094cf913ULL,0xedcb381fb5983723ULL,0x3ffffffffffffffeULL}; /* 2^65 */
static const fp POSEIDON_RC_M[64][3] = {
  {{{0x2d6110568f8fb1cdULL,0xe436f09787ae5fc6ULL,0x51ea32d50f7be93fULL,0x3ee3b205efa6ab5dULL}},{{0x5564975171925a88ULL,0x4ccc244f2b4cee87ULL,0xa473a9e22140ab94ULL,0x293983c6cd66b132ULL}},{{0x1650a1e8d6eb3b9dULL,0xe1d084ae973c80a4ULL,0xc6b0e48a821b7324ULL,0x26f40bdecf47ed19ULL}}},
  {{{0xc6687b9c41161a23ULL,0x7132cacb8362ca7aULL,0xd85a41c272c6bbb5ULL,0x201e196e95c1d5a7ULL}},{{0xfac81e29844529d7ULL,0x55cd21dd6e3519aaULL,0xdac6e75068b2d6e6ULL,0x1db160cfe68f1791ULL}},{{0xd0380768fd7d233eULL,0x1e9be9783f636613ULL,0x072a39e85b32c9c0ULL,0x12451bc216857272ULL}}},
  {{{0x28238cb2f9610a03ULL,0xa5bf3dbbb71c1a95ULL,0xcfa2634c3dcdc1cfULL,0x30d475d91c9d2660ULL}},{{0xe54edcbe9506d50dULL,0x6336d456820cd730ULL,0x62f946f09a61cd4cULL,0x3dbf6a7660d1c1f2ULL}},{{0xa1f0f09ab6b52ec7ULL,0xa0256009a9a655c0ULL,0x02d87cd8131e6863ULL,0x1d82928e0581f03dULL}}},
  {{{0xd40988e46aa0d84aULL,0xcb83b98a6c3311b6ULL,0x1faecd3d4f5ba6feULL,0x21816a2ace1e6ceeULL}},{{0x12966345b9eb55e6ULL,0xe7207d68cede2273ULL,0xc5e2cfe134e17a59ULL,0x3b77812fa31cbea0ULL}},{{0x7c6cf91aa5ec91b8ULL,0x788439799fc5e819ULL,0x420b62303e699297ULL,0x03cf4743b88562d7ULL}}},
  {{{0x62a23ec7246945beULL,0xf0ce22ea72865fbdULL,0x656887c5d7179774ULL,0x0387c6accf862ddbULL}},{{0x3a8498acade3e889ULL,0x11837e2c04524a39ULL,0x1d734b9714471abcULL,0x123cb78b6fa1e7f0ULL}},{{0xd9e655459801f98aULL,0xfc579cc290c7c6f9ULL,0x2027d70ac2d2c545ULL,0x347d84f327297c50ULL}}},
  {{{0x0c514cbe25cd5dceULL,0xecce789089b36388ULL,0xe8ae18e6cf5c2d28ULL,0x09508b80b79c153cULL}},{{0xf1c79b4f210c1577ULL,0x39d1fa61fe64ebd8ULL,0xb8d92fd604863955ULL,0x16356b23d117fcf8ULL}},{{0x075b151491dd1191ULL,0x61dc8c496394e6dbULL,0x3db07ac8572c1d58ULL,0x0cd7d3fd2c41152eULL}}},
  {{{0xf2f6633139c4b05eULL,0x01dbcb2916c3253dULL,0xf1172b5fa58201e9ULL,0x16ce288f5de472a7ULL}},{{0x74b411041f0f061bULL,0x119ca91c82f60867ULL,0x88a45446cea98b5fULL,0x3f947ecf9f672579ULL}},{{0x9bc2a35b9de62d46ULL,0x040c50a583d292a1ULL,0x1f62387715c339a0ULL,0x2b0e1ed4a55c9b51ULL}}},
  {{{0x0988c91b9e85fef9ULL,0xe8ad133faa5d1bcdULL,0xd8df562e7b09d6efULL,0x0ce401a7279eeb38ULL}},{{0xc4dfd87b16cb67c7ULL,0x63d16458323b64bcULL,0xc8c653cf8e63bcccULL,0x11242b4450a3daa4ULL}},{{0x6768a64cd32ee7f7ULL,0xc2e49f96bbd21fb0ULL,0x97aae974ebac14cbULL,0x01d1a1069ea732f8ULL}}},
  {{{0xd11a4d50cdf5c831ULL,0xf0141a1730a04151ULL,0x4839556e137af540ULL,0x337fc238de198aacULL}},{{0x65126e84b58b3ba7ULL,0xc8d56c47b3b29eeeULL,0x8f7755c67ad08f38ULL,0x032b374daf0f5daeULL}},{{0x03c37d36570461bdULL,0xf7af83659d08e8f8ULL,0x5ab5a972d3ed3a2cULL,0x3ea0dc7d347f4499ULL}}},
  {{{0x6c9388c1bf9426b6ULL,0x6ef2023f27f48878ULL,0x4858081b3f9d5fc7ULL,0x022a53a4a03a61b2ULL}},{{0x8d8bbf6d29f2c488ULL,0xf1fb6efb14f6c308ULL,0x12566c68cdf47685ULL,0x2874c6e0c2f51250ULL}},{{0x0cbd4d8959832848ULL,0x0be4c3aaeae1eec8ULL,0x8ff6a34de0e0041bULL,0x35a497e0ae1c0c6fULL}}},
  {{{0xf265123421944696ULL,0x58c83e93fd718498ULL,0xf5d679bbfa9b691dULL,0x16394bccd2d2fddaULL}},{{0x6b0b7673c8d01fe1ULL,0x43d92fddf33b2e84ULL,0xc2c2fb35e711d5baULL,0x3310e80bcf0c079cULL}},{{0xba2001a87d410461ULL,0x92db1732f98ac5bfULL,0x46b53d2f258b21a0ULL,0x2431dc11acaf9487ULL}}},
  {{{0x4e5eac0c7809dac9ULL,0x88d278a88757b06dULL,0xb1caa105e8cfd525ULL,0x38c5e465b0998789ULL}},{{0x8d582cd16028d0b6ULL,0x02f5f6f2049341fbULL,0x14da884cd65b6d4cULL,0x175b5e71ccbd92ccULL}},{{0x7a4f279b84faae3fULL,0xdc9cf712aa7020eaULL,0xd282adb6f153c7ceULL,0x3dc87f51bee14157ULL}}},
  {{{0x54cf83685b98d9ecULL,0xf982055b2e3f539fULL,0xa9150eebebecca51ULL,0x101de276dcdc3feaULL}},{{0x07ff3281e556dffaULL,0x8e411f5f9f08c47aULL,0x901151014e2336c7ULL,0x051670efbebe0450ULL}},{{0x9e49643f069395b7ULL,0x28bf9db3e38928cdULL,0x8c02c832008df673ULL,0x079d4a1265f1f9b8ULL}}},
  {{{0x174d2c5549935069ULL,0xf449d64ba7afd980ULL,0x17489be3cbeb8217ULL,0x3dde70f1a49ecc6cULL}},{{0x7dfd80ab7fad4deeULL,0x8f7d70f1057b7365ULL,0x432c8e8ae0ea2f2dULL,0x21a4f21cbad39e96ULL}},{{0x97383a22729d1abaULL,0x4120a9e5df48c0aeULL,0x0ac4c5efc2eedad4ULL,0x1b96fd1670bdf887ULL}}},
  {{{0x663798be9e2ca816ULL,0x74a1d330e5c2746dULL,0xaf106b2043e0b1cdULL,0x1d3b129ea32c0690ULL}},{{0x623d1657253b3822ULL,0xde6cd3acc6c1e3daULL,0x1bbcb5725404e77dULL,0x1555343383b9e912ULL}},{{0x5e942b15b6542262ULL,0x99c8b631c5e985c4ULL,0x22cd0b12f24838eaULL,0x342e25680ac0f457ULL}}},
  {{{0xacee1be8258f1974ULL,0x330f1daa7a0a82d3ULL,0x30cf05803e57f42fULL,0x05af97ff16360de2ULL}},{{0xf60d13bc70fb7261ULL,0x89323aa335da65e0ULL,0xa230cf39306ada27ULL,0x37ec8d60f94c0e00ULL}},{{0x77cb61b22f0fef36ULL,0x97b9c176aa4f29dcULL,0x753951ba534b64ccULL,0x39d864f4db0d66e5ULL}}},
  {{{0x1c93a280de7e6390ULL,0x89bbe99192d5942bULL,0xd298630838ac97b4ULL,0x1fdee9515ec23733ULL}},{{0x1b1500ea3ea52e7cULL,0xab66b5200e504be8ULL,0xf2ca2fc2dd1238ceULL,0x2e99ac0058887a8eULL}},{{0x797a75c017355c08ULL,0x95753d5fbfe4b639ULL,0x99d90146a1022ee1ULL,0x18c6c282437c0106ULL}}},
  {{{0x28c41cb0f6a427aaULL,0x7a6274209547e747ULL,0x409958bab0ce8004ULL,0x0f5c9a21669c3561ULL}},{{0x4f458041d5a49e9aULL,0x70bf9be212724995ULL,0x16bb868a425b1357ULL,0x11bbfdbd72e6c273ULL}},{{0x840d988bb266eb39ULL,0x32ee4645ac430194ULL,0xdf94525d6b695073ULL,0x26f7032e169d741eULL}}},
  {{{0xed032a7242155f1cULL,0xd3bf87a6d0fc1c34ULL,0x6e6b7f2bba883e7aULL,0x03bee947acf8d869ULL}},{{0x54124791da75f84cULL,0xdea3fdd86d09154cULL,0xa8b1b78ee689124bULL,0x08cc569a704f8ae7ULL}},{{0x16e420feed279927ULL,0xd4e9f90a2430cadeULL,0xbda76f8c724ed3c4ULL,0x26f0c2eb7941a2edULL}}},
  {{{0xfa8bcd50c49a6dc1ULL,0x1b75bef3f3b40443ULL,0x16306d7f83e6e86fULL,0x2cb265185a682f74ULL}},{{0x816198532054502fULL,0xa53e572f12c3401fULL,0xe9a8f617740903c3ULL,0x2c9ba61ca6f41275ULL}},{{0xf5b6a307021d72c4ULL,0xf9b09e3b204957faULL,0x1ef85c62ca5473eeULL,0x0efc66dcec9a30aeULL}}},
  {{{0x005b369d1ddec201ULL,0x1a842b0d7196bbe6ULL,0x737adf896a50cea4ULL,0x236df79cb9f4188bULL}},{{0xea5b61d7bd606ab0ULL,0xccb039d4615a540eULL,0x1408af70b00d1a59ULL,0x225863cd3b10bb9dULL}},{{0x6cb2f4bcc26de564ULL,0xbb358e5aee7406abULL,0xf08ffcbb81863becULL,0x00f144f53402205fULL}}},
  {{{0x47dac6922bd0e686ULL,0x7d618f7ba9d32c8eULL,0x6118919ff121628cULL,0x074faa94927b7786ULL}},{{0x3af193a3ff7b9d4dULL,0x5b4be86fcf9052b0ULL,0xa9433b495aa64416ULL,0x041c30de6dcc571eULL}},{{0x3d90f898029f92e2ULL,0xfcbb9e4743c48e1dULL,0x20bc4ddedcf505afULL,0x0ce8a49fa10949e7ULL}}},
  {{{0x6bb524c3db961189ULL,0xe93f7a4d2c5cd069ULL,0xc7c572085a58c1f2ULL,0x157be04d9af4f4b7ULL}},{{0xcce74e4ac292398dULL,0xaed371d912fb1d56ULL,0x356e0c2dbf7bc066ULL,0x3514dcf22466a19fULL}},{{0xfd1e5928b50de13cULL,0x00f1d7fb3cb6d5ffULL,0xfe3bd8a8f595d931ULL,0x2aef30e01461acebULL}}},
  {{{0xa86cd7f133554ebbULL,0x094a97d9d8908309ULL,0x3de9cf716c0e5531ULL,0x2a215295d3b86a1cULL}},{{0xd53c009bb1e61c5cULL,0xfb9b2a40c066fa76ULL,0xfc69157a958ea7d9ULL,0x2a396665f94e134fULL}},{{0xf86e48d38ebb1402ULL,0x06e4f55e6bfb3e89ULL,0x16bf492bbf874eb3ULL,0x335d71a30027eccdULL}}},
  {{{0x1e4bb73ffb93a6d1ULL,0x9ef465a03f553915ULL,0xa986466f8cb39340ULL,0x344b522709d83fd6ULL}},{{0x54d1385a73cedc14ULL,0x554f9d50f1aa4237ULL,0x6c40c2c46e70eb08ULL,0x08d14481b53d311cULL}},{{0x1424438d34dfc1daULL,0x2409171b46a1ca37ULL,0x1a1c4cfb701efcc3ULL,0x3238d087fe0f487bULL}}},
  {{{0xe4e41151ef95cfa8ULL,0x5ac9a18bf328f9a7ULL,0xa74bc957b4f0312fULL,0x2a7229e81bd17e27ULL}},{{0x128b64e508a63bd9ULL,0xbc72e63f546c4584ULL,0x88cf7accb6e0e0eeULL,0x113c3d59a596d700ULL}},{{0xf4d7b2de93df79c1ULL,0xd48511fd9b630fa2ULL,0x66d2195a8ed94ca5ULL,0x1c0c0ca45eee2c44ULL}}},
  {{{0x466d86d03c2466caULL,0x8227a59ab7462664ULL,0xd2fd28964ffc5f0eULL,0x047b0867cd0bb8bcULL}},{{0xd789d21c1d4ea83cULL,0x7401f29ebae79841ULL,0xe0abd0eb46b46cb8ULL,0x28e0786cd4de5a8fULL}},{{0x7402eeab3141e20fULL,0xd768b71e6068c79bULL,0x3db2195fe3a15590ULL,0x2ae0bdb635468021ULL}}},
  {{{0xc16e17aec4c8c257ULL,0xcbe2e0daf07542ffULL,0xbfe62521350c02fbULL,0x1228614aa1224324ULL}},{{0x75e7f93077ae107aULL,0x4393dd80790be351ULL,0xdff377ea2fa44416ULL,0x1e8508e864d3a7c5ULL}},{{0xb1ec20078a1957fdULL,0x763ab46a70baa519ULL,0x7738685a419fd1cbULL,0x2a5e0a5a9db64745ULL}}},
  {{{0xc22212c67483d82eULL,0xa75cc24295d6ff8dULL,0x7992eb54a6a2ed5dULL,0x07404560d0b2cbd5ULL}},{{0x2a285911ee339ba5ULL,0x8893e0badb13c939ULL,0xd83525d7431b9b62ULL,0x25f63b980e96e6dbULL}},{{0xa15a39ed0b3d0589ULL,0xd368b459a4b900e0ULL,0x4efa56d549364219ULL,0x0b5ca2beedd7dd3eULL}}},
  {{{0xeb7ba4127d2e6354ULL,0x6986145a2941fb14ULL,0x0e3e7c6c97a14312ULL,0x1ed53f1aa1bf808fULL}},{{0xaf8ab4c0d2b2669dULL,0x7e7a7326eb971e3fULL,0xa2d3848e9ce2fc69ULL,0x29ea52e7093a43d4ULL}},{{0x1e72622bdb4569a9ULL,0x874356996d93fcdeULL,0x5c7c464758b32bc2ULL,0x105fe2acbcc84897ULL}}},
  {{{0x0653a67e86f62c0fULL,0xda058f0b6767498aULL,0xa49ef164a0280442ULL,0x348a3f44e29a1db3ULL}},{{0x4ebc09df098dddf4ULL,0x7953e2582fc1806cULL,0x4c7c4749054887c8ULL,0x0ea7f29878781fb8ULL}},{{0x9e9e28ff373a00a1ULL,0x59d68a2c32f0aeaeULL,0x030aa50eb0d116f4ULL,0x265063100e234ee0ULL}}},
  {{{0xc65436d24cba466aULL,0x461c6791d1c4df7bULL,0x44a880f485ffa101ULL,0x3fbc3cf75118c62eULL}},{{0xd77ac655ca67b1c2ULL,0x76d88fda6b1d115cULL,0x089c758c1ba6ef20ULL,0x0964db39bd4b200bULL}},{{0xbd5667e04c034a11ULL,0x5d4c63fffa29c3a1ULL,0xf6831d76df36eaa1ULL,0x255644c108880d6dULL}}},
  {{{0xafa80ea9d8392946ULL,0xb374fe3c3d852b90ULL,0x6ac7be0421200289ULL,0x20e4c096c4dd72e6ULL}},{{0x7896f449e943831eULL,0x1ce40ea3c4383e92ULL,0xb49ab8f65a18dfb3ULL,0x022f6ae3e0d1f236ULL}},{{0x3befcfdbe8dd042cULL,0x1f23c41b8459e28cULL,0x9d3df3e0c372ff8aULL,0x18dc26fa862b191eULL}}},
  {{{0x56dd436505fd7a95ULL,0xde6df28980a2b7d9ULL,0x0363df341e40f38bULL,0x07e2bca200e16abaULL}},{{0xd411d472d8dc23daULL,0xf50cfab4071be3cfULL,0x3c259a5e3e76eb62ULL,0x0ac0b7df209f51acULL}},{{0x5ed3556cb6eccdaaULL,0x5a77f234139d70b3ULL,0xfcb189da416e3bcaULL,0x0cafd03316e3da67ULL}}},
  {{{0x3ded6d76360a45beULL,0x6c429cb169faa590ULL,0x2fb017c34a83a077ULL,0x31f542859f15f500ULL}},{{0x3429130c2c719a28ULL,0x2c9ef140b71e34edULL,0x483fc18d0a310a87ULL,0x1495571d0705997cULL}},{{0x3af7365d394648aeULL,0x5cf1b21e24262136ULL,0xc0fc62acf9bb6f72ULL,0x1115c26a2fa746d9ULL}}},
  {{{0x8099beda71efd72fULL,0xd36c358a6cb42b28ULL,0xeec3d42dc5d22579ULL,0x22193d634f4398d4ULL}},{{0x69fa4c8431c72241ULL,0x3d493a2870de9ecaULL,0xfa85379fa7f96e96ULL,0x06ed1793aac4bac5ULL}},{{0x469e500151fe112eULL,0xf15b462bf229e21fULL,0xf700e5a684cc210eULL,0x208c794ee061495bULL}}},
  {{{0x42e1de787c5ac045ULL,0xdaf7f483c5ac2542ULL,0x3a179e90ac57dc06ULL,0x3ccede2a70073e55ULL}},{{0x9907bebdd515efcdULL,0x5c5759cc9d41d88aULL,0x3674aac584e9815eULL,0x256eccb4ae6815a8ULL}},{{0xfbecb087cd94ed86ULL,0xe2c856bd76367ef6ULL,0x4eb80ed90b2de128ULL,0x259f3b2f4d72a341ULL}}},
  {{{0x8aee7138a3e493efULL,0xc097e3916e39d301ULL,0x3f4edaab5fade903ULL,0x26341785bebb55d1ULL}},{{0x81743dbd685bfc78ULL,0x51e1df5405018bb4ULL,0x5e7f09f43fab73dcULL,0x300dc575584e1165ULL}},{{0xcf5e72012088079fULL,0x5ee47f6039ea45b0ULL,0x1376a4ad287da55cULL,0x15c592ab8709a775ULL}}},
  {{{0xd1ba83ae61ab349cULL,0x54c4ebfa46c6c5ddULL,0x6811f417646c4a9bULL,0x0304e5f3b22fd1e6ULL}},{{0x96b0a28615104eebULL,0xddc28384fa498de1ULL,0x2e588de186363997ULL,0x35279da4cf2bc018ULL}},{{0xd0533b7b914aa30eULL,0xf91091f7f642e389ULL,0xe768cc728d9ffd9fULL,0x3512143a077d0fa6ULL}}},
  {{{0xa64b6584aa7777b6ULL,0xa9ecd008c97413bdULL,0x42db693e89469246ULL,0x000f9bd1021c5922ULL}},{{0x0208b8d66e15fe3bULL,0xeb7cb55bbc327ae8ULL,0x63a2418e20a3ba6cULL,0x38a5ea6f82db3d5dULL}},{{0x9a649745f40e953eULL,0x9d6406d52cb622f5ULL,0x200a4cbd0f1f267cULL,0x3db51a34b6e9fe06ULL}}},
  {{{0x17c83056e2c382a1ULL,0x2f4c8b882d658eb4ULL,0x96acd13fcc26bf82ULL,0x000c6a1b1bf90012ULL}},{{0xf616d545a5d3e939ULL,0x2af7464619d365cbULL,0xf097308d468c947dULL,0x291ffc707a48e2ccULL}},{{0xd3b637e65a834971ULL,0x8fa7365afde54fe7ULL,0x118cc5ff60f24404ULL,0x1430b62cbd021f4aULL}}},
  {{{0xab3d6c0df3ce0ca0ULL,0x08144b4c79d86499ULL,0xf91d2462d75a2286ULL,0x2bf52870c017cf4eULL}},{{0xe5e5488d5162898eULL,0xe83c6c0ca21e9962ULL,0x66f17a5cce9bd5eeULL,0x0faa86932fc9ec52ULL}},{{0x6a601060296db14dULL,0xecf3cf47c1dc4442ULL,0x6a950536b5584542ULL,0x313de4b333fc8118ULL}}},
  {{{0xc2bb2bdb161c0d43ULL,0xe42240232ae44172ULL,0x305435bec7528b04ULL,0x2da4e7173aee4d48ULL}},{{0x923370757c286129ULL,0xbf9fcef7fa21e1f3ULL,0x0e1971e6add36a32ULL,0x05f07747dffb6336ULL}},{{0xb63765a7f3c491d9ULL,0xc6da1f9e3e9828c7ULL,0xde242a4e2279090dULL,0x2cca495816249692ULL}}},
  {{{0x1ff64be92cab7091ULL,0x3d79404b46d72eb9ULL,0x1710f1c5af14541aULL,0x0ebaf248a381fe31ULL}},{{0xa40aa7f2f4be8e45ULL,0x135a66ac8749ce1cULL,0xd8d76ea87865c570ULL,0x044ec20c80c90b04ULL}},{{0x4a9da72cba665450ULL,0xd5295d8e27bb7bfbULL,0x3626ca8c336dd990ULL,0x022408a1fb0b3800ULL}}},
  {{{0x8446ea40f76089b3ULL,0xdbfa50f0a581e128ULL,0xd7685cd42f8f7c21ULL,0x398f3c2662df6e9aULL}},{{0x37d44d6ed12e5836ULL,0xdd62ee99a8b6cc55ULL,0xaf6d348d1857a659ULL,0x1f9c9041980969afULL}},{{0xf749702efd480758ULL,0x323710fe973ef206ULL,0xddb2efafff6e26bfULL,0x3281013f35baa4d1ULL}}},
  {{{0x36f8bf09755e3fd1ULL,0x5d77e2be7cd25b26ULL,0xb3f18051ec66d481ULL,0x228b840f19b7f6edULL}},{{0x1e20bd7e9007dc99ULL,0x7f9c083ce884876dULL,0xb113ce50640f20f6ULL,0x2bf716d6b3cd9a18ULL}},{{0xe0f986df949e09f8ULL,0x32d8dd9249948d2eULL,0x9ae905c32961e96fULL,0x30553eb90e4d277aULL}}},
  {{{0x2acddfb558ce6fd8ULL,0xc70f8fcddfdb34a1ULL,0xfa66e72c6937e86fULL,0x385df4d2ddcdcaa5ULL}},{{0x3e7465e402206318ULL,0xf6ead3f9d9e048b3ULL,0x619112a188adb41eULL,0x2c34febcf9def460ULL}},{{0xe8a7c82fa2625b3fULL,0xaebb23cc8147e2bdULL,0xf587afa348f34bf0ULL,0x07ccc87a97eee0b3ULL}}},
  {{{0xd679b84eef1994b9ULL,0x7def28d56667062cULL,0xac3068742ec64b40ULL,0x14479d04a6999fefULL}},{{0x1bf627000bfe0e4aULL,0x1c54cb5d1844ccffULL,0x76ba72dfe568a18aULL,0x1eb61f5d4af67fbdULL}},{{0x48f5e53e337b002aULL,0xa2cd1072d615602fULL,0x6bb93f9dad34bed7ULL,0x320e9200e22d4464ULL}}},
  {{{0x5aa93dae91a2e4b9ULL,0xfaacb53728337d8aULL,0x1081dbb00247523bULL,0x397bf21666510308ULL}},{{0x8f7f76f47d9ff019ULL,0x24de8ffa0fad4008ULL,0x2018e79b576a6bc7ULL,0x158acea556828e27ULL}},{{0xe905f10b227bbf42ULL,0xc2edbfc5a426c09fULL,0xd95d18ff73154263ULL,0x040333330a351778ULL}}},
  {{{0x91a0adc20b096a81ULL,0x8ed3f92a943f4990ULL,0x09dca1eb774a58aaULL,0x3190de39a08e30d0ULL}},{{0xa186477461610158ULL,0x49dcf00c9a3f4cdcULL,0xc24bd4292b6300a8ULL,0x2353ebbae73e6b0bULL}},{{0xd86fe6c3fd5d72d6ULL,0xcb092c676b2faf59ULL,0x41de6a751b2ab6b8ULL,0x36d1c42ec123b236ULL}}},
  {{{0x6eeb8c14a580493fULL,0xa63fafe1762d0433ULL,0x2535874ab3d5feb7ULL,0x3f9fd0c9caf16f44ULL}},{{0x097b1331d5d5fdcdULL,0xb69a099bd2707e4bULL,0xa00d654aab61139bULL,0x04a51f72fbc8f91eULL}},{{0xec1ba969b57bc21aULL,0x757b333a7ffa3b3dULL,0x0e597273fe4ac666ULL,0x114d73316180d61bULL}}},
  {{{0x042ec88c94422adfULL,0x84669dfab8f97048ULL,0xdcc347c19ad69842ULL,0x293316fbfcb11e39ULL}},{{0x63d9ab3880316efeULL,0xd06d752adf2b43fcULL,0xa236c0995704aa60ULL,0x286ce110716c2974ULL}},{{0x25fd65694898efb4ULL,0x99cb620dfc63fbcdULL,0xf3a0a1e1aedec074ULL,0x097462528778299bULL}}},
  {{{0x418c3f6d880e3244ULL,0x20a933100425e4d5ULL,0x5366e37bd79dd77dULL,0x1c5640c60b10f088ULL}},{{0x062556e677ce1aeeULL,0x551bb969a99a27d8ULL,0xbd64e65f6d50ce56ULL,0x3670f79b1ebd37eaULL}},{{0x6340a6e40b2cb449ULL,0x75a66980082192d0ULL,0xf26997d2e59968b8ULL,0x1ba8ef4ddba030a2ULL}}},
  {{{0x9e81ed6bcca99ca8ULL,0xe283e6741c1c8c1aULL,0x4dcbab4c903e7d6cULL,0x144287df706d7d35ULL}},{{0xf307d19656785140ULL,0xf2359f3af40af740ULL,0x073120eaab4c104dULL,0x372a560cedb19147ULL}},{{0x0917ef782f366a32ULL,0x118e0d62997e0761ULL,0x85a794632bd1186eULL,0x3fd8af8f75a55735ULL}}},
  {{{0x45f1327d29d5bb47ULL,0x1d267c203c076406ULL,0x54568d3ebb89dbacULL,0x050c1e7fd4e0840aULL}},{{0x8918a0f53d47ef87ULL,0xd801c477ffe38754ULL,0x6f614c3c03eab522ULL,0x3e22c9f862e9d961ULL}},{{0x0a6c3b558ff7fb9dULL,0x916c06f103a297bfULL,0xfe331bfa4f477e45ULL,0x02fda085e0882d39ULL}}},
  {{{0xe00d560c1922bd80ULL,0xbe5fb99f7823e7ceULL,0x9b8ab20ee58d07d2ULL,0x3cf282a530973229ULL}},{{0x61f5e4a62789d305ULL,0xe79e5db989d235c2ULL,0x779fd5723b0e4c8cULL,0x1fb84c68e272aacdULL}},{{0x9f8bc8af370f0e1fULL,0x628b777da9608e7aULL,0x56f3fce27af86d3dULL,0x3ed0ea844bce3f7cULL}}},
  {{{0xa81ca9ad3596718eULL,0xa2e243ebc26d8786ULL,0xbdd0c75e49311133ULL,0x0491f56bad943b95ULL}},{{0x662a89747f07eb48ULL,0xbfd2949f2198be29ULL,0x61faee803ba6ad21ULL,0x0d92b19df57965e5ULL}},{{0x74c0170dcb26b9a3ULL,0x6e043841ae89ad9cULL,0x9c21986513bb6c95ULL,0x32c850785ef8c550ULL}}},
  {{{0xed4d002f16bc787fULL,0x06ebf8cb07196aa9ULL,0x14eb45e365573e2bULL,0x25032cef4a7000efULL}},{{0x3b118891deafe0c1ULL,0x13f9c32f82aa94f5ULL,0xa02a82d122209fb7ULL,0x1ce89d10d60cb6f5ULL}},{{0xf371d6ce33fea695ULL,0x5505eca4ffdb4f3aULL,0x2c1c430f4a00cc14ULL,0x18679130f2053d1bULL}}},
  {{{0x8f93a25b2e5c3ac9ULL,0xf65309c16f7c2122ULL,0x448ec71a1bb9c43fULL,0x1c9901bfdaead7bbULL}},{{0xce3903ea34b01eb4ULL,0x3743ef7a61a75b0dULL,0xc4b3b804343ab52cULL,0x21525c6921c10348ULL}},{{0x3e58ceccf33d9fd6ULL,0x0a4405f0f3f9ecddULL,0x5e439182f7d467e3ULL,0x2fdbb7666a8d4e93ULL}}},
  {{{0xd95c47374d92d769ULL,0x6e7a4d28152762eeULL,0x70aca0ccc8b1e64cULL,0x00224355557620cdULL}},{{0xd546a4caccd86c58ULL,0x94e61f808ca9e38fULL,0xd4dcc0ca96cc3b32ULL,0x19e80175f12ee906ULL}},{{0xdd1c43055a2df184ULL,0x21ea7e74be932b7bULL,0xeb9bd9f6301efde3ULL,0x204f1be7c3153361ULL}}},
  {{{0x669a1bfa4452e5b9ULL,0xb50119f9ba5913e4ULL,0x376e862381f50e26ULL,0x2fb4218313d636abULL}},{{0x79c6708a2d8292c2ULL,0x2684a5342d6e29c4ULL,0x77efae4ea0f85e94ULL,0x26a86c00b42234b5ULL}},{{0xacb8a62ec21f1790ULL,0xa532d1c96fd777b0ULL,0xbce6beb99cd715c5ULL,0x2205f95b96860426ULL}}},
  {{{0xeea18d332c6ba201ULL,0x7e49750fe17b0c48ULL,0x84b958e355658851ULL,0x1af476c6c11beb7cULL}},{{0xac7444171b9ed2a4ULL,0xb13b491258203302ULL,0x7bbd82c67d980d63ULL,0x288fef4833b6612bULL}},{{0xdb2f5426a3ce3a28ULL,0xe35f66b7b35fd095ULL,0xc2911efe8acaa8d3ULL,0x20adef5e2b2bc83fULL}}},
  {{{0x668c5c60dc165271ULL,0xa20833455f8c9082ULL,0x7ea98ee735477650ULL,0x3742df583c401d58ULL}},{{0x76bb56ba0777dd32ULL,0x57ae5691adfd5bb6ULL,0xc25cd5eaaad89961ULL,0x0ba64c73d78f268aULL}},{{0x77f195a810966117ULL,0x5a4fa67cbe740274ULL,0xc195daea12525beaULL,0x116979774227425cULL}}},
  {{{0x5d58cfd09c2210bbULL,0x4ba345d05d37c73aULL,0x6e8d9dd33f2a5189ULL,0x1a0e98c3ef88d4cfULL}},{{0x561643bef1c2f375ULL,0xd28ed380885331acULL,0xba76d3ad613a46f5ULL,0x3ef76bf14ed05706ULL}},{{0x0fe0d46abf50f962ULL,0xb8c8c797af9d04b6ULL,0xd19d4f33430a128fULL,0x11ffb1bc451c07d1ULL}}},
};
static const fp POSEIDON_MDS_M[3][3] = {
  {{{0x7c1a669d208e8b4dULL,0x5f51868647bdf2a3ULL,0x00fcf9354819f613ULL,0x3103a7de3b678ebdULL}},{{0xd02c6b7336d40cfaULL,0x3a1a0851864fb4a7ULL,0x2282de236a32af60ULL,0x0e799762bd549615ULL}},{{0xb3624a21289b4249ULL,0xca6c5877b9c3c7c5ULL,0xb02a2a0100ebb202ULL,0x117cb780c908530aULL}}},
  {{{0xe3ff3f5c313a6a34ULL,0x51c6f61bd721544dULL,0x8ed31b47cae66704ULL,0x02087f41039c75bbULL}},{{0xd2f9d522444ac1a0ULL,0xe69ac4d3b9d1c5a0ULL,0x6edec07987aaee83ULL,0x1e43c65722df71bdULL}},{{0x10a0d86e38d77e7bULL,0xf0b93da384af65e0ULL,0x62ed3679f9a91794ULL,0x2345494383dd3fb8ULL}}},
  {{{0x1ff15b66b7bbe66dULL,0x75ecdd64110a734fULL,0x78f0280d37007108ULL,0x376408280c7418bcULL}},{{0x934d00845da6461dULL,0x930aa4624cdae4b4ULL,0xdcd1ebac0098612dULL,0x2de64334636be38dULL}},{{0x0f957fede68e9322ULL,0x14ac4b874d7324dbULL,0x4007b97b032e6d5dULL,0x22011675ded37456ULL}}},
};
#endif
```

### attack.h

```c
/* Orchard Poseidon (r partial rounds) two-family collision: line model, digest polynomial, helpers. */
#ifndef ATTACK_H
#define ATTACK_H
#include "common.h"

typedef struct {
    int j;                 /* coordinate of the round-1 S-box input that stays constant on this family */
    fp UQ, VQ;             /* point Q of the family: (U,V) at tau = 0 */
    fp a, b;               /* direction: (U,V) = Q + tau (a,b) */
    fp d[3];               /* round-1 S-box input = d_i tau (i != j), kappa (i == j) */
    fp kappa;
    fp alpha[3], beta[3];  /* round-2 S-box input = alpha + beta W,  W = tau^5 */
    fp e5inv_unused;
} line_t;

extern const uint64_t E5INV[4];                            /* 5^{-1} mod (p-1) */
void line_setup(line_t *L, int j);                         /* counted */
void tail_eval(fp *out, const line_t *L, const fp *W, int r);   /* H on the family at W: counted, no memory-op charge */
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);   /* W -> canonical input (nk, rho) */
void rng_seed(uint64_t s);
void rnd_fp254(fp *a);                                     /* 254-bit random word: 1 random word + 2 ctl */
void rnd_u256(uint64_t w[4]);                              /* 256-bit random word: 1 random word */
void bound_mem_since(snap_t s0);                           /* 2 loads + 1 store + 6 control ops per primitive since s0 */

/* split.c */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db);       /* classical Euclid; monic gcd; returns degree */
uint64_t gcd_cost_bound(size_t da, size_t db);
uint64_t div_cost_bound(size_t la, size_t lb);                                /* derived worst-case charge of gcd_cl */
fp  *deflate(fp *G, size_t d, const fp *r);                                   /* G / (Z - r), frees G; exits if r is not a root */
int  split_find_root(fp *root, fp *G, size_t d);                              /* one root of a monic product of distinct linear factors */
size_t split_tries(size_t d);
fp  *taylor_shift(fp *G, size_t d, const fp *a);                              /* G(Z + a), frees G */
void pow_half(fp *S, const fp *G, size_t d);                                  /* Z^((p-1)/2) mod G */
extern uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;
#endif
```

### ntt.c

```c
/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 words in registers) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"

static fp *tw = NULL;          /* tw[j] = rho_max^j, j < nmax/2 */
static int amax_g = 0;
static size_t nmax_g = 0;
fp ntt_w3;                      /* primitive cube root of unity */
static fp W3[3];                /* 1, w, w^2 */
static fp CH, DL;               /* -1/2, (w - w^2)/2 */

static void limbs_sub1(uint64_t r[4], const uint64_t a[4]) {      /* r = a - 1 */
    for (int i = 0; i < 4; i++) r[i] = a[i];
    for (int i = 0; i < 4; i++) { if (r[i]) { r[i]--; break; } r[i] = ~(uint64_t)0; }
}
static void limbs_shr(uint64_t r[4], const uint64_t a[4], int s) {
    int ws = s / 64, bs = s % 64;
    for (int i = 0; i < 4; i++) {
        uint64_t v = 0;
        if (i + ws < 4) v = a[i + ws] >> bs;
        if (bs && i + ws + 1 < 4) v |= a[i + ws + 1] << (64 - bs);
        r[i] = v;
    }
}
static void limbs_div3(uint64_t r[4], const uint64_t a[4]) {
    unsigned __int128 rem = 0;
    for (int i = 3; i >= 0; i--) { unsigned __int128 cur = (rem << 64) | a[i]; r[i] = (uint64_t)(cur / 3); rem = cur % 3; }
}

void ntt_init(int amax) {
    if (tw) ntt_free();
    CTL(2);                                        /* the test of tw */
    amax_g = amax; nmax_g = (size_t)1 << amax;
    uint64_t pm1[4], e[4]; limbs_sub1(pm1, PALLAS_P);
    fp five; fp_from_u64(&five, 5);
    /* rho_max = 5^((p-1)/2^amax) (5 is a non-residue so this has exact order 2^amax) */
    limbs_shr(e, pm1, amax);
    fp rho; fp_pow(&rho, &five, e);
    /* w = 5^((p-1)/3) */
    limbs_div3(e, pm1); fp_pow(&ntt_w3, &five, e);
    CTL(400);               /* limbs_sub1, limbs_shr, limbs_div3: at most 4 iterations of about 20 operations each per call, three calls */
    CTL(2);                 /* the test ntt_w3 == 1 */
    fp one; fp_set_one(&one);
    if (fp_eq(&ntt_w3, &one)) { fprintf(stderr, "5 is a cube?\n"); exit(3); }
    tw = NEW_FP(nmax_g / 2);
    tw[0] = one; ST(1);
    for (size_t j = 1; j < nmax_g / 2; j++) { fp_mul(&tw[j], &tw[j - 1], &rho); LD(1); ST(1); }
    loopc(nmax_g / 2);
    CTL(5 * INV_CTL);       /* control of the bit loops of fp_pow (x2) and fp_inv (x1): at most INV_CTL each; the other setup is a few dozen straight-line operations */
    W3[0] = one; W3[1] = ntt_w3; fp_sqr(&W3[2], &ntt_w3);
    fp two, half; fp_from_u64(&two, 2); fp_inv(&half, &two);
    fp s; fp_add(&s, &W3[1], &W3[2]); fp_mul(&CH, &s, &half);          /* (w+w^2)/2 = -1/2 */
    fp d; fp_sub(&d, &W3[1], &W3[2]); fp_mul(&DL, &d, &half);
}
void ntt_free(void) { if (tw) xfree(tw); tw = NULL; }
size_t ntt_table_bytes(void) { return (nmax_g / 2) * sizeof(fp); }

plan_t make_plan(int rows, int a) {
    plan_t P; memset(&P, 0, sizeof P);
    if (a < 2 || a > amax_g || (rows != 1 && rows != 3)) { fprintf(stderr, "bad plan rows=%d a=%d (amax=%d)\n", rows, a, amax_g); exit(4); }
    P.rows = rows; P.a = a; P.n = (size_t)1 << a; P.N = P.n * rows; P.shift = amax_g - a;
    CTL(16);                                       /* validity tests (4 compares, 4 branches) and the assignments above (shift, multiply, subtraction) */
    int np = (a + 3) / 4; P.npass = np;
    int rem = a;
    CTL(3);
    /* last pass gets 4 layers; earlier passes take the rest, first pass smallest */
    for (int i = np - 1; i >= 0; i--) { int k = rem >= 4 ? 4 : rem; P.kk[i] = k; rem -= k; }
    loopc(np); CTL(4 * np);                        /* per pass: compare, select, subtract, store index */
    CTL(2);                                        /* test of rows */
    if (rows == 3) {
        size_t n = P.n, beta = 0, it = 0;
        for (size_t b = 1; b < n; b += 2) { it++; if ((3 * b) % n == 1) { beta = b; break; } }
        loopc(it); CTL(4 * it);                    /* per iteration: multiply, modulo, compare, branch */
        P.c0 = (int)((3 * beta - 1) / n);
        CTL(4);
    }
    return P;
}
plan_t plan_for_len(size_t len, int allow3) {
    for (int a = 2; a <= amax_g; a++) {
        CTL(3 + 1 + 2 + (allow3 ? 3 : 0));         /* loop (3), shift, compare + branch, [multiply, compare, branch] */
        if (((size_t)1 << a) >= len) return make_plan(1, a);
        if (allow3 && 3 * ((size_t)1 << a) >= len) return make_plan(3, a);
    }
    fprintf(stderr, "length %zu too large for amax=%d\n", len, amax_g); exit(5);
}
static size_t brv(size_t x, int a) {
    size_t r = 0;
    for (int i = 0; i < a; i++) { r = (r << 1) | (x & 1); x >>= 1; }
    CTL(4 * (uint64_t)a);                          /* per iteration: shift, mask, or, shift */
    loopc(a);
    return r;
}
size_t layout_index(const plan_t *P, size_t k) {
    CTL(8);                                        /* call, rows test (compare, branch), k % 3, k % n, row * n, addition */
    size_t row = P->rows == 3 ? k % 3 : 0;
    return row * P->n + brv(k % P->n, P->a);
}
void plan_theta(const plan_t *P, fp *theta) {
    fp rho = tw[(size_t)1 << P->shift]; LD(1); CTL(1);
    CTL(2);                                        /* test of rows */
    if (P->rows == 1) { *theta = rho; return; }
    int e = (3 - P->c0 % 3) % 3;              /* omega3^(-c0) */
    CTL(10);
    fp_mul(theta, &rho, &W3[e]);
}

/* ---------- butterflies ---------- */
static inline void bf_fwd(fp *u, fp *v, const fp *w) {
    fp t; fp_sub(&t, u, v); fp_add(u, u, v);
    if (w) fp_mul(v, &t, w); else *v = t;
}
/* Charged per executed operation.  A loop of n iterations costs 3n + 2 (index update, bound comparison, branch per iteration;
 * comparison and branch on exit).  A butterfly iteration of the inner loop costs 9: t += 2*half (shift, add), compare, branch,
 * t + half, the addresses of x[t] and x[t+half], and the test of the twiddle pointer (compare, branch).
 * x[16] is the register file of the block. */
static inline void blk_fwd(fp *x, int k, int l0, size_t b, size_t s, int shift) {
    size_t K = (size_t)1 << k; CTL(1);
    for (int j = 0; j < k; j++) {
        size_t half = (size_t)1 << (k - 1 - j); CTL(3);               /* two subtractions, one shift */
        for (size_t tp = 0; tp < half; tp++) {
            size_t idx = (b + tp * s) << (l0 + j); CTL(4);            /* multiply, add, add, shift */
            const fp *w = NULL;
            CTL(2);                                                    /* test idx != 0: compare, branch */
            if (idx) { w = &tw[idx << shift]; LD(1); CTL(1); }         /* shift; the table load */
            uint64_t nb = 0;
            for (size_t t = tp; t < K; t += 2 * half) { bf_fwd(&x[t], &x[t + half], w); nb++; }
            CTL(9 * nb + 2);                                           /* butterfly iterations and the failing loop test */
        }
        loopc(half);
    }
    loopc(k);
}
/* inverse of the forward butterfly (u,v)->(u+v,(u-v)w), unnormalised: (A,B) -> (A + B w^-1, A - B w^-1),
 * w^-1 = -tw[n/2-idx]  =>  (A - B*wp, A + B*wp) */
static inline void blk_inv(fp *x, int k, int l0, size_t b, size_t s, int shift, size_t nh) {
    size_t K = (size_t)1 << k; CTL(1);
    for (int j = k - 1; j >= 0; j--) {
        size_t half = (size_t)1 << (k - 1 - j); CTL(3);
        for (size_t tp = 0; tp < half; tp++) {
            size_t idx = (b + tp * s) << (l0 + j); CTL(4);
            const fp *wp = NULL;
            CTL(2);
            if (idx) { wp = &tw[(nh - idx) << shift]; LD(1); CTL(2); }  /* subtraction, shift; the table load */
            uint64_t nb = 0;
            for (size_t t = tp; t < K; t += 2 * half) {
                fp *u = &x[t], *v = &x[t + half];
                if (!wp) { fp tt = *v; fp_sub(v, u, &tt); fp_add(u, u, &tt); }
                else { fp tt, A = *u; fp_mul(&tt, v, wp); fp_sub(u, &A, &tt); fp_add(v, &A, &tt); }
                nb++;
            }
            CTL(9 * nb + 2);
        }
        loopc(half);
    }
    loopc(k);
}

enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };

/* Per pass: 7 operations of setup (n >> (l0+k): add, shift; 1 << k; G*s; 1 << l0; call, return).
 * Per block (grp, b): base = row + grp*Gs + b (3), the call of the block (2), the load loop and the store loop of G iterations each
 * (loopc(G); per element one multiplication t*s and one register-slot selection: 2G), and the iteration of the b loop (loopc(s)). */
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    fp x[16];
    CTL(7);
    for (size_t grp = 0; grp < ngrp; grp++) {
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b; CTL(3);
            for (size_t t = 0; t < G; t++) x[t] = base[t * s];
            LD(G); loopc(G); CTL(2 * G);
            CTL(2);
            blk_fwd(x, k, l0, b, s, P->shift);
            for (size_t t = 0; t < G; t++) base[t * s] = x[t];
            ST(G); loopc(G); CTL(2 * G);
        }
        loopc(s);
    }
    loopc(ngrp);
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    fp x[16];
    CTL(7);
    for (size_t grp = 0; grp < ngrp; grp++) {
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b; CTL(3);
            for (size_t t = 0; t < G; t++) x[t] = base[t * s];
            LD(G); loopc(G); CTL(2 * G);
            CTL(2);
            blk_inv(x, k, l0, b, s, P->shift, P->n >> 1);
            for (size_t t = 0; t < G; t++) base[t * s] = x[t];
            ST(G); loopc(G); CTL(2 * G);
        }
        loopc(s);
    }
    loopc(ngrp);
}
/* last forward pass + pointwise + first inverse pass (s == 1) in one register-resident block.
 * Per block: base = row + grp*G (2), two calls (4), load loop, pointwise loop and store loop (G iterations each, one slot selection per element),
 * for M_MULC also cb = C + grp*G (2) and the load addresses of C. */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t G = (size_t)1 << k, ngrp = P->n >> k;
    fp x[16];
    CTL(5);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * G; CTL(2);
        for (size_t t = 0; t < G; t++) x[t] = base[t];
        LD(G); loopc(G); CTL(G);
        CTL(2);
        blk_fwd(x, k, l0, 0, 1, P->shift);
        CTL(2);                                    /* dispatch on the mode */
        if (mode == M_SQ) { for (size_t t = 0; t < G; t++) fp_sqr(&x[t], &x[t]); loopc(G); CTL(G); }
        else { const fp *cb = C + grp * G; CTL(2); for (size_t t = 0; t < G; t++) fp_mul(&x[t], &x[t], &cb[t]); LD(G); loopc(G); CTL(G); }
        CTL(2);
        blk_inv(x, k, l0, 0, 1, P->shift, P->n >> 1);
        for (size_t t = 0; t < G; t++) base[t] = x[t];
        ST(G); loopc(G); CTL(G);
    }
    loopc(ngrp);
}

/* ---------- radix-3 stage ---------- */
static void dft3_full(const fp *v, fp *o) {
    fp t1, t2, m1, m2;
    CTL(2 + 6);                                    /* call, return; six register-slot selections */
    fp_add(&t1, &v[1], &v[2]); fp_sub(&t2, &v[1], &v[2]);
    fp_add(&o[0], &v[0], &t1);
    fp_mul(&m1, &t1, &CH); fp_add(&m1, &m1, &v[0]);
    fp_mul(&m2, &t2, &DL);
    fp_add(&o[1], &m1, &m2); fp_sub(&o[2], &m1, &m2);
}
/* o[k] = sum over inputs flagged in nzmask of v[i] w^(ik); only outputs flagged in need are produced */
static void dft3_sel(const fp *v, int nzmask, int need, fp *o) {
    CTL(2 + 4);                                    /* call, return; test nzmask == 7 && need == 7 (two compares, two branches) */
    if (nzmask == 7 && need == 7) { dft3_full(v, o); return; }
    for (int k = 0; k < 3; k++) {
        CTL(4);                                    /* test of bit k of need: shift, mask, compare, branch */
        if (!((need >> k) & 1)) continue;
        int first = 1; fp acc; fp_set_zero(&acc);
        for (int i = 0; i < 3; i++) {
            CTL(4);                                /* test of bit i of nzmask */
            if (!((nzmask >> i) & 1)) continue;
            fp term = v[i]; int e = (i * k) % 3;
            CTL(1 + 2 + 2 + 2);                    /* slot selection, i*k % 3 (multiply, modulo), if (e), if (first) */
            if (e) { fp_mul(&term, &v[i], &W3[e]); CTL(2); }
            if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
        }
        loopc(3);
        o[k] = acc; CTL(1);
    }
    loopc(3);
}
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(2);                                        /* test of rows */
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        CTL(4);                                    /* test dst == src && off == 0 */
        if (dst == src && off == 0) { for (size_t i = len; i < n; i++) dst[i] = z; if (n > len) { ST(n - len); loopc(n - len); } CTL(2); return; }
        for (size_t i = 0; i < n; i++) { if (i < len) { dst[i] = src[off + i]; LD(1); CTL(1); } else dst[i] = z; }
        ST(n); loopc(n); CTL(2 * n); return;      /* per element: compare and branch of i < len; the add off + i is charged when the branch is taken */
    }
    int c0 = P->c0 % 3;
    CTL(1);
    for (size_t i0 = 0; i0 < n; i0++) {
        int rot = (int)((c0 * (i0 % 3)) % 3);
        CTL(3);                                    /* modulo, multiply, modulo */
        fp u[3], v[3], o[3]; int nz[3];
        for (int t = 0; t < 3; t++) {
            size_t pos = i0 + n * (size_t)t;
            nz[t] = pos < len;
            CTL(3 + 2 + 1);                        /* pos (multiply, add), comparison, if (nz[t]) */
            if (nz[t]) { u[t] = src[off + pos]; LD(1); CTL(2); }   /* add off + pos, slot selection */
        }
        loopc(3);
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) {
            int t = (rot + i1) % 3; CTL(2 + 2);    /* add, modulo; if (nz[t]) */
            if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; CTL(1 + 1 + 2); }   /* slot copy, shift, or, slot selections */
        }
        loopc(3);
        CTL(2);                                    /* if (mask == 0) */
        if (mask == 0) { fp_set_zero(&o[0]); o[1] = o[0]; o[2] = o[0]; }
        else dft3_sel(v, mask, 7, o);
        dst[i0] = o[0]; dst[i0 + n] = o[1]; dst[i0 + 2 * n] = o[2];
        ST(3); CTL(3);                             /* i0 + n, 2 * n, i0 + 2 * n */
    }
    loopc(n);
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    CTL(2);                                        /* test of rows */
    if (P->rows == 1) return;
    size_t n = P->n; int c0 = P->c0 % 3;
    CTL(1);
    for (size_t i0 = 0; i0 < n; i0++) {
        int rot = (int)((c0 * (i0 % 3)) % 3);
        CTL(3);
        int need = 0;
        for (int i1 = 0; i1 < 3; i1++) {
            size_t pos = i0 + n * (size_t)((rot + i1) % 3); if (pos < outlen) need |= 1 << i1;
            CTL(4 + 2 + 2);                        /* pos (add, modulo, multiply, add), comparison and branch, shift and or when taken */
        }
        loopc(3);
        CTL(2);                                    /* if (!need) */
        if (!need) continue;
        fp A[3], B[3], v[3];
        for (int k = 0; k < 3; k++) A[k] = buf[i0 + n * (size_t)k];
        LD(3); loopc(3); CTL(3 * 2 + 3);           /* addresses i0 + n*k (multiply, add) and the slot selections */
        B[0] = A[0]; B[1] = A[2]; B[2] = A[1]; CTL(3);
        dft3_sel(B, 7, need, v);
        for (int i1 = 0; i1 < 3; i1++) {
            CTL(4);                                /* test of bit i1 of need */
            if ((need >> i1) & 1) { buf[i0 + n * (size_t)((rot + i1) % 3)] = v[i1]; ST(1); CTL(4 + 1); }   /* address (add, modulo, multiply, add), slot */
        }
        loopc(3);
    }
    loopc(n);
}

void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    stageA_fwd(P, dst, src, off, len);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(3);
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(2);
    }
    CTL(2);
}
void ntt_inv(const plan_t *P, fp *buf, size_t outlen) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = P->a;
        CTL(3);
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(2);
    }
    CTL(2);
    stageA_inv(P, buf, outlen);
}
static void conv_core(const plan_t *P, fp *buf, int mode, const fp *C) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = 0;
        CTL(3 + 5);
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(4);                                    /* C ? ... : NULL: compare, branch, multiply, add */
        pass_fused(row, P, l0, P->kk[P->npass - 1], mode, C ? C + (size_t)r * P->n : NULL);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(4);
    }
    CTL(2);
}
void conv_sq(const plan_t *P, fp *buf, size_t len, size_t outlen) {
    stageA_fwd(P, buf, buf, 0, len);
    conv_core(P, buf, M_SQ, NULL);
    stageA_inv(P, buf, outlen);
}
void conv_mulc(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, const fp *C, size_t outlen) {
    stageA_fwd(P, dst, src, off, len);
    conv_core(P, dst, M_MULC, C);
    stageA_inv(P, dst, outlen);
}

/* ---------- lean variant: the spectrum of the second operand is generated one row at a time (rows==3 plans only) ----------
 * Row r of the Good-Thomas stage for the compact vector B: position pos (0 <= pos < N) holds B[(pos + N - boff) % N] if that
 * index is < lenB, else 0.  The row is then transformed with the forward passes, giving exactly row r of ntt_fwd(B). */
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N; int c0 = P->c0 % 3;
    CTL(3);
    for (size_t i0 = 0; i0 < n; i0++) {
        int rot = (int)((c0 * (i0 % 3)) % 3);
        CTL(3);                                    /* modulo, multiply, modulo */
        fp u[3], v[3], o[3]; int nz[3];
        for (int t = 0; t < 3; t++) {
            size_t pos = i0 + n * (size_t)t, idx = (pos + N - boff) % N;
            CTL(2 + 3);                            /* pos (multiply, add); idx (add, subtract, modulo) */
            int any = 0; fp acc; uint64_t nit = 0;
            for (; idx < lenB; idx += N) {            /* fold modulo x^N - 1 when lenB > N */
                if (!any) { acc = B[idx]; any = 1; } else fp_add(&acc, &acc, &B[idx]);
                LD(1); nit++;
            }
            loopc(nit); CTL(2 * nit);              /* loop; if (!any): compare and branch per iteration */
            nz[t] = any; if (any) u[t] = acc;
            CTL(1 + 2 + 1);                        /* nz[t] = any, if (any), slot selection */
        }
        loopc(3);
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) {
            int t = (rot + i1) % 3; CTL(2 + 2);    /* add, modulo; if (nz[t]) */
            if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; CTL(1 + 1 + 2); }
        }
        loopc(3);
        CTL(2 + 1);                                /* if (mask == 0); the shift 1 << r */
        if (mask == 0) fp_set_zero(&o[r]);
        else dft3_sel(v, mask, 1 << r, o);
        tmp[i0] = o[r]; ST(1); CTL(1);
    }
    loopc(n);
}
void conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                   const fp *B, size_t lenB, size_t boff, size_t outlen) {
    CTL(2);                                        /* validity test of rows */
    if (P->rows != 3) { fprintf(stderr, "conv_mulc_otf needs a rows==3 plan\n"); exit(9); }
    stageA_fwd(P, dst, src, off, len);
    CTL(4);
    for (int r = 0; r < 3; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(2 + 2 + 2 + 5);
        stageA_row(P, tmp, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmp, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        CTL(2);
        l0 = 0;
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
        pass_fused(row, P, l0, P->kk[P->npass - 1], M_MULC, tmp);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(4);
    }
    CTL(2);
    stageA_inv(P, dst, outlen);
}
plan_t plan3_for_len(size_t len) {
    for (int a = 2; a <= amax_g; a++) { CTL(3 + 1 + 1 + 2); if (3 * ((size_t)1 << a) >= len) return make_plan(3, a); }   /* loop, shift, multiply, compare, branch */
    fprintf(stderr, "plan3: length %zu too large\n", len); exit(5);
}

/* out (P->N slots) = sum_t sign[t] * (A_t * B_t mod x^N - 1) * N, all operands compact (folded modulo x^N-1 if longer than N);
 * the first term must have sign +1.  tmpA, tmpB: P->n slots each.  Only positions < outlen of out are produced. */
void conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                  const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen) {
    CTL(2);                                        /* validity test of rows */
    if (P->rows != 3) { fprintf(stderr, "conv_sum_otf needs a rows==3 plan\n"); exit(9); }
    size_t n = P->n;
    CTL(2);
    for (int r = 0; r < 3; r++) {
        fp *row = out + (size_t)r * n; CTL(2 + 2);
        for (int t = 0; t < nt; t++) {
            int l0 = 0; CTL(3 + 6);                /* loop; the array selections A[t], lenA[t], B[t], lenB[t] and the argument setups */
            stageA_row(P, tmpA, r, A[t], lenA[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpA, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
            CTL(2);
            l0 = 0;
            stageA_row(P, tmpB, r, B[t], lenB[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpB, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
            CTL(2 + 4);                            /* loop exit; the tests t == 0 and sign[t] > 0 */
            if (t == 0) { for (size_t i = 0; i < n; i++) fp_mul(&row[i], &tmpA[i], &tmpB[i]); LD(2 * n); ST(n); }
            else if (sign[t] > 0) { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_add(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            else { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_sub(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            loopc(n);
        }
        CTL(2);
        int l0 = P->a;
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        CTL(2);
    }
    CTL(2);
    stageA_inv(P, out, outlen);
}
```

### poly.c

```c
/* Generic polynomial multiplication (NTT based, counted), Newton reciprocal for Barrett reduction. */
#include "common.h"

/* cache of 1/N per plan size */
static struct { size_t N; fp inv; int used; } invcache[64];
void plan_invN(const plan_t *P, fp *out) {
    for (int i = 0; i < 64; i++) { CTL(3 + 4); if (invcache[i].used && invcache[i].N == P->N) { *out = invcache[i].inv; return; } }   /* loop, two compares, two branches */
    fp Nf; uint64_t v[4] = { P->N, 0, 0, 0 }; fp_from_limbs(&Nf, v);
    fp inv; fp_inv(&inv, &Nf); CTL(INV_CTL);
    for (int i = 0; i < 64; i++) if (!invcache[i].used) { invcache[i].used = 1; invcache[i].N = P->N; invcache[i].inv = inv; break; }
    *out = inv;
}

void poly_mul_naive(fp *r, const fp *a, size_t la, const fp *b, size_t lb) {
    if (!la || !lb) return;
    for (size_t k = 0; k < la + lb - 1; k++) {
        size_t lo = k >= lb ? k - lb + 1 : 0, hi = k < la ? k : la - 1;
        fp acc; fp_set_zero(&acc); int first = 1;
        for (size_t i = lo; i <= hi; i++) {
            fp t; fp_mul(&t, &a[i], &b[k - i]);
            if (first) { acc = t; first = 0; } else fp_add(&acc, &acc, &t);
            LD(2); CTL(1 + 2 + 3);          /* index k - i, if (first), inner loop iteration */
        }
        r[k] = acc; ST(1); CTL(2 + 4 + 3);  /* inner loop exit, lo and hi (compare, subtract, select), outer iteration */
    }
    CTL(2);
}

void poly_mul(fp *r, const fp *a, size_t la, const fp *b, size_t lb) {
    if (!la || !lb) return;
    size_t len = la + lb - 1;
    if (la <= 24 || lb <= 24) { poly_mul_naive(r, a, la, b, lb); return; }
    plan_t P = plan3_for_len(len);
    fp *out = NEW_FP(P.N), *tA = NEW_FP(P.n), *tB = NEW_FP(P.n);
    const fp *As[1] = { a }, *Bs[1] = { b }; size_t lA[1] = { la }, lB[1] = { lb }; int sg[1] = { 1 };
    conv_sum_otf(&P, out, 1, As, lA, Bs, lB, sg, tA, tB, len);
    fp inv; plan_invN(&P, &inv);
    for (size_t i = 0; i < len; i++) fp_mul(&r[i], &out[i], &inv);
    LD(len); ST(len); loopc(len);
    xfree(out); xfree(tA); xfree(tB);
}
```

### lean.c

```c
/* Low-memory x^E mod g (g monic, degree m): one transform buffer Y (3*2^a slots), one transform row, g, mu and a fold buffer.
 * No stored spectra: the spectra of mu' and g are regenerated row by row for every multiplication (conv_mulc_otf).
 * State s = a/N as in loop.c (N = size of the big plan), so no scaling of the state is ever needed.
 *   Y := conv_sq(s)                      = T/N                  (T = a^2)
 *   F := T/N folded modulo x^N'-1 (first m coefficients)        saved
 *   Y := T1/N = coefficients m..2m-2 of T/N moved to 0..m-2
 *   Y := conv(T1/N, mu'')                = q/(N N')             mu'' = x^(N-m+2) mu /(N N') (cyclic, window at 0..m-2)
 *   Y := conv_N'(q/(N N'), g)            = (q g mod x^N'-1)/N
 *   Y := F - Y                           = a_new/N              (N' >= m) */
#include "common.h"

static int ebit(const uint64_t E[4], int i) { return (int)((E[i / 64] >> (i % 64)) & 1); }

static void mulx_(fp *Y, const fp *G, size_t m) {
    fp c = Y[m - 1]; LD(1);
    for (size_t i = m - 1; i >= 1; i--) { fp t; fp_mul(&t, &c, &G[i]); fp_sub(&Y[i], &Y[i - 1], &t); }
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&Y[0], &t);
    LD(2 * m); ST(m); loopc(m); CTL(m);          /* index i - 1 */
}

/* MU[0..m-2] = floor(x^(2m-2)/g); GR (>= m-1 slots) and Y, tmp are scratch */
static void newton_lean(fp *MU, const fp *g, size_t m, fp *GR, fp *Y, fp *tmp) {
    size_t L = m - 1;
    for (size_t i = 0; i < L; i++) GR[i] = g[m - i];
    LD(L); ST(L); loopc(L); CTL(L);              /* index m - i */
    fp one; fp_set_one(&one);
    CTL(4);                                      /* fp_eq: compare, branch; setup */
    if (!fp_eq(&GR[0], &one)) { fprintf(stderr, "newton: g not monic\n"); exit(6); }
    MU[0] = one; ST(1);
    size_t l = 1;
    while (l < L) {
        size_t l2 = 2 * l < L ? 2 * l : L;
        CTL(3 + 3 + 2);                          /* loop test, 2*l, compare, select */
        plan_t P1 = plan3_for_len(l2 + l - 1);
        conv_mulc_otf(&P1, Y, MU, 0, l, tmp, GR, l2, 0, l2);
        fp inv1; plan_invN(&P1, &inv1);
        for (size_t i = 0; i < l2 - l; i++) fp_mul(&Y[i], &Y[l + i], &inv1);
        LD(l2 - l); ST(l2 - l); loopc(l2 - l); CTL(l2 - l);          /* index l + i */
        plan_t P2 = plan3_for_len(l2 - 1);
        conv_mulc_otf(&P2, Y, Y, 0, l2 - l, tmp, MU, l, 0, l2 - l);
        fp inv2; plan_invN(&P2, &inv2);
        for (size_t i = 0; i < l2 - l; i++) { fp t; fp_mul(&t, &Y[i], &inv2); fp_neg(&MU[l + i], &t); }
        LD(l2 - l); ST(l2 - l); loopc(l2 - l); CTL(l2 - l);          /* index l + i */
        l = l2;
    }
    for (size_t i = 0; i < L / 2; i++) { fp t = MU[i]; MU[i] = MU[L - 1 - i]; MU[L - 1 - i] = t; }
    LD(L); ST(L); loopc(L / 2); CTL(2 * (L / 2));       /* L/2 iterations; index L - 1 - i twice (two operations each) */
}

/* F (m slots, caller-owned) receives x^E mod g; it is also used as scratch.  Allocates Y, tmp, MU through xalloc. */
void powx_lean(fp *F, const fp *g, size_t m, const uint64_t E[4], int quiet) {
    plan_t PN = plan3_for_len(2 * m - 1), PNp = plan3_for_len(m + 1);
    size_t N = PN.N, Np = PNp.N;
    fp *Y = NEW_FP(N), *tmp = NEW_FP(PN.n), *MU = NEW_FP(m - 1);
    snap_t sA = snap();
    newton_lean(MU, g, m, F, Y, tmp);
    snap_t sB = snap();
    {
        fp i1, i2, sc; plan_invN(&PN, &i1); plan_invN(&PNp, &i2); fp_mul(&sc, &i1, &i2);
        for (size_t i = 0; i < m - 1; i++) fp_mul(&MU[i], &MU[i], &sc);
        LD(m - 1); ST(m - 1); loopc(m - 1);
    }
    size_t gamma = N - (m - 2);
    int top = 255; while (top > 0 && !ebit(E, top)) { top--; CTL(3 + 7 + 2); }      /* loop, ebit (7: divide, modulo, index, shift, mask, ...), test */
    size_t v = 1; int bit = top;
    while (bit >= 1 && ((v << 1) | (size_t)ebit(E, bit - 1)) < m) { v = (v << 1) | (size_t)ebit(E, bit - 1); bit--; CTL(3 + 2 * 7 + 2 + 2 + 3 + 1); }   /* loop, ebit twice, two shifts/ors, compare with m, branch, bit-- */
    for (size_t i = 0; i < m; i++) fp_set_zero(&Y[i]);
    ST(m); loopc(m);
    { fp invN; plan_invN(&PN, &invN); Y[v] = invN; ST(1); }
    snap_t sC = snap();
    int steps = 0;
    for (int b = bit - 1; b >= 0; b--) {
        conv_sq(&PN, Y, m, 2 * m - 1);
        for (size_t i = 0; i < m; i++) {
            if (i + Np <= 2 * m - 2) { fp_add(&F[i], &Y[i], &Y[i + Np]); LD(2); CTL(1); } else { F[i] = Y[i]; LD(1); }
            CTL(2 + 2 + 2);                  /* i + Np, 2*m - 2 (shift, subtract), compare, branch */
        }
        ST(m); loopc(m);
        for (size_t i = 0; i + 1 < m; i++) Y[i] = Y[m + i];
        LD(m - 1); ST(m - 1); loopc(m - 1); CTL(2 * (m - 1));       /* i + 1 in the loop test, index m + i */
        conv_mulc_otf(&PN, Y, Y, 0, m - 1, tmp, MU, m - 1, gamma, m - 1);
        conv_mulc_otf(&PNp, Y, Y, 0, m - 1, tmp, g, m + 1, 0, m);
        for (size_t i = 0; i < m; i++) fp_sub(&Y[i], &F[i], &Y[i]);
        LD(2 * m); ST(m); loopc(m);
        if (ebit(E, b)) mulx_(Y, g, m);
        CTL(3 + 7 + 2 + 2);                  /* loop, ebit (7), if, steps++ and the quiet/modulo test */
        steps++;
        CTL(6);
        if (!quiet && steps % 32 == 0) fprintf(stderr, "  lean step %d/%d\n", steps, bit);
    }
    { fp Nf; uint64_t vv[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, vv);
      for (size_t i = 0; i < m; i++) fp_mul(&F[i], &Y[i], &Nf);
      LD(m); ST(m); loopc(m); }
    CTL(2);                                      /* test of quiet */
    if (quiet == 2) {
        snap_t n_ = snap_sub(sB, sA), l_ = snap_sub(snap(), sC), p_ = snap_sub(sC, sB);
        printf("lean-pow breakdown: newton total=%llu arith=%llu | prefix+scale total=%llu | loop steps=%d total=%llu arith=%llu per-step total=%llu arith=%llu",
               (unsigned long long)snap_total(n_), (unsigned long long)snap_arith(n_), (unsigned long long)snap_total(p_), steps,
               (unsigned long long)snap_total(l_), (unsigned long long)snap_arith(l_),
               (unsigned long long)(snap_total(l_) / (steps ? steps : 1)), (unsigned long long)(snap_arith(l_) / (steps ? steps : 1)));
        putchar(10);
    }
    xfree(Y); xfree(tmp); xfree(MU);
}
```

### line.c

```c
/* Line model of the Orchard hash with r partial rounds, the digest polynomial F(W), the odd-part polynomial g,
 * and the map back from W to canonical inputs.  All field arithmetic goes through pallas.c (counted). */
#include "attack.h"
#include "pallas_consts.h"

/* e = 5^{-1} mod (p-1) = (4(p-1)+1)/5; 254 bits, Hamming weight 125 */
const uint64_t E5INV[4] = { 0xe0f0f3f0cccccccdULL, 0x4e9ee0c9a10a60e2ULL, 0x3333333333333333ULL, 0x3333333333333333ULL };

static uint64_t rs_state = 0x9e3779b97f4a7c15ULL;
void rng_seed(uint64_t s) { rs_state = s ? s : 0x9e3779b97f4a7c15ULL; }
static uint64_t rnd64(void) { rs_state ^= rs_state << 13; rs_state ^= rs_state >> 7; rs_state ^= rs_state << 17; return rs_state; }
void rnd_fp254(fp *a) {
    uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL };
    fp_from_limbs(a, v);
    X.rnd += 1; X.ctl += 2;      /* one random 256-bit word; the 254-bit mask: one AND, one assignment */
}


void rnd_u256(uint64_t w[4]) { for (int i = 0; i < 4; i++) w[i] = rnd64(); X.rnd += 1; }

void bound_mem_since(snap_t s0) {
    snap_t d = snap_sub(snap(), s0);
    uint64_t ops = snap_arith(d);
    X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops;      /* per field operation: two operand loads, one result store, six control/index operations (loop: 3, index selections, bit tests) */
}

static void mds_apply(fp s[3]) {
    fp o[3], t;
    for (int i = 0; i < 3; i++) {
        fp_mul(&o[i], &POSEIDON_MDS_M[i][0], &s[0]);
        fp_mul(&t, &POSEIDON_MDS_M[i][1], &s[1]); fp_add(&o[i], &o[i], &t);
        fp_mul(&t, &POSEIDON_MDS_M[i][2], &s[2]); fp_add(&o[i], &o[i], &t);
    }
    s[0] = o[0]; s[1] = o[1]; s[2] = o[2];
}

/* Round 0 maps (nk, rho, 2^65) to M (U, V, K), U = (nk + c0_0)^5, V = (rho + c0_1)^5, K = (2^65 + c0_2)^5.
 * Round-1 S-box input x = M (U, V, K) + RC1 = M[:,0] U + M[:,1] V + base,  base_k = M[k][2] K + RC1[k].
 * For the constant coordinate j (others I = {i1, i2}): Q solves x_i1 = x_i2 = 0; direction (a, b) = (M[j][1], -M[j][0])
 * gives d_j = 0.  On (U, V) = Q + tau (a, b): x_i = d_i tau (i in I), x_j = kappa.  Round-1 S-box output = v0 + W v1 with
 * W = tau^5, v0 = kappa^5 e_j, v1 = sum_{i in I} d_i^5 e_i.  After the round-1 MDS: A + W B with A = M v0, B = M v1;
 * the round-2 S-box input (constants of round 2 added) is alpha + beta W, alpha = A + RC2, beta = B. */
void line_setup(line_t *L, int j) {
    const fp (*M)[3] = POSEIDON_MDS_M;
    L->j = j;
    int i1 = j == 0 ? 1 : 0, i2 = j == 2 ? 1 : 2;
    fp cap, K, base[3], t, u;
    memcpy(cap.l, POSEIDON_CAP_M, 32);
    fp_add(&t, &cap, &POSEIDON_RC_M[0][2]);
    fp_pow5(&K, &t);
    for (int k = 0; k < 3; k++) { fp_mul(&t, &M[k][2], &K); fp_add(&base[k], &t, &POSEIDON_RC_M[1][k]); }
    /* 2x2 system  M[i1][0] U + M[i1][1] V = -base[i1],  M[i2][0] U + M[i2][1] V = -base[i2] */
    fp det, idet, e1, e2, n1, n2;
    fp_mul(&t, &M[i1][0], &M[i2][1]); fp_mul(&u, &M[i1][1], &M[i2][0]); fp_sub(&det, &t, &u);
    fp_inv(&idet, &det);
    fp_neg(&n1, &base[i1]); fp_neg(&n2, &base[i2]);
    /* U = (n1 M[i2][1] - M[i1][1] n2)/det ; V = (M[i1][0] n2 - n1 M[i2][0])/det */
    fp_mul(&t, &n1, &M[i2][1]); fp_mul(&u, &M[i1][1], &n2); fp_sub(&e1, &t, &u); fp_mul(&L->UQ, &e1, &idet);
    fp_mul(&t, &M[i1][0], &n2); fp_mul(&u, &n1, &M[i2][0]); fp_sub(&e2, &t, &u); fp_mul(&L->VQ, &e2, &idet);
    L->a = M[j][1]; fp_neg(&L->b, &M[j][0]);
    for (int k = 0; k < 3; k++) { fp_mul(&t, &M[k][0], &L->a); fp_mul(&u, &M[k][1], &L->b); fp_add(&L->d[k], &t, &u); }
    fp_mul(&t, &M[j][0], &L->UQ); fp_mul(&u, &M[j][1], &L->VQ); fp_add(&t, &t, &u); fp_add(&L->kappa, &t, &base[j]);
    fp v0j, v1[3];
    fp_pow5(&v0j, &L->kappa);
    for (int k = 0; k < 3; k++) { if (k == j) fp_set_zero(&v1[k]); else fp_pow5(&v1[k], &L->d[k]); }
    for (int k = 0; k < 3; k++) {
        fp_mul(&t, &M[k][j], &v0j); fp_add(&L->alpha[k], &t, &POSEIDON_RC_M[2][k]);
        fp acc; fp_set_zero(&acc); int first = 1;
        for (int i = 0; i < 3; i++) if (i != j) {
            fp_mul(&t, &M[k][i], &v1[i]);
            if (first) { acc = t; first = 0; } else fp_add(&acc, &acc, &t);
        }
        L->beta[k] = acc;
    }
}

/* F(W): rounds 2 (S-box on alpha + beta W), MDS, 3, r partial rounds, 60..63, digest = row 0 of the last MDS */
void tail_eval(fp *out, const line_t *L, const fp *W, int r) {
    fp x[3], t;
    for (int k = 0; k < 3; k++) { fp_mul(&t, &L->beta[k], W); fp_add(&x[k], &L->alpha[k], &t); }
    for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
    mds_apply(x);
    for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], &POSEIDON_RC_M[3][k]);
    for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
    mds_apply(x);
    for (int i = 0; i < r; i++) {
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], &POSEIDON_RC_M[4 + i][k]);
        fp_pow5(&x[0], &x[0]);
        mds_apply(x);
    }
    for (int idx = 60; idx < 64; idx++) {
        for (int k = 0; k < 3; k++) fp_add(&x[k], &x[k], &POSEIDON_RC_M[idx][k]);
        for (int k = 0; k < 3; k++) fp_pow5(&x[k], &x[k]);
        if (idx < 63) mds_apply(x);
        else {
            fp o;
            fp_mul(&o, &POSEIDON_MDS_M[0][0], &x[0]);
            fp_mul(&t, &POSEIDON_MDS_M[0][1], &x[1]); fp_add(&o, &o, &t);
            fp_mul(&t, &POSEIDON_MDS_M[0][2], &x[2]); fp_add(&o, &o, &t);
            *out = o;
        }
    }
}

void map_back(fp *nk, fp *rho, const line_t *L, const fp *W) {
    fp tau, tt, U, V, t;
    fp_pow(&tau, W, E5INV);
    fp_mul(&t, &tau, &L->a); fp_add(&U, &L->UQ, &t);
    fp_mul(&t, &tau, &L->b); fp_add(&V, &L->VQ, &t);
    fp_pow(&tt, &U, E5INV); fp_sub(nk, &tt, &POSEIDON_RC_M[0][0]);
    fp_pow(&tt, &V, E5INV); fp_sub(rho, &tt, &POSEIDON_RC_M[0][1]);
}
```

### split.c

```c
/* Stage tools of the two-family attack: classical Euclid gcd with a derived worst-case charge, deflation by a known root,
 * Taylor shift, Z^((p-1)/2) mod G, and the isolation of one root of a monic product of distinct linear factors.
 * Every executed operation is charged as in common.h. */
#include "attack.h"
#include "pallas_consts.h"

uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;

static int deg_of(const fp *a, int top) { while (top >= 0 && fp_is_zero(&a[top])) top--; return top; }

/* ---------- classical Euclid.  da, db are degree upper bounds (arrays hold da+1 and db+1 coefficients, not all zero).
 * Writes the monic gcd to out (room max(da,db)+1) and returns its degree. */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db) {
    size_t cap = (da > db ? da : db) + 1;
    fp *A = NEW_FP(cap), *B = NEW_FP(cap);
    memcpy(A, a, (da + 1) * sizeof(fp)); memcpy(B, b, (db + 1) * sizeof(fp));
    LD(da + db + 2); ST(da + db + 2); loopc(da + db + 2);
    int dA = deg_of(A, (int)da), dB = deg_of(B, (int)db);
    CTL(9 * ((uint64_t)((int)da - dA) + (uint64_t)((int)db - dB) + 2) + 4);   /* degree scans: per test index, four-limb zero test, branch, decrement; the comparison and swap below */
    if (dA < dB) { fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td; }
    while (dB >= 0) {
        CTL(2);                                                  /* outer loop test */
        fp ilc; fp_inv(&ilc, &B[dB]); LD(1); CTL(INV_CTL);
        while (dA >= dB) {
            CTL(3);                                              /* loop test, shift sh = dA - dB */
            fp q; fp_mul(&q, &A[dA], &ilc); LD(1);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            LD(2 * (size_t)dB); ST(dB); loopc(dB); CTL(dB);       /* index sh + i */
            fp_set_zero(&A[dA]); ST(1);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            CTL(9 * (uint64_t)(dA - nd + 1) + 6); LD(dA - nd);
            dA = nd;
            if (dA < 0) break;
        }
        CTL(6);                                                  /* swap of the two arrays and degrees */
        fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td;
    }
    CTL(2);
    int dg = dA;
    if (dg < 0) { fprintf(stderr, "gcd of zero polynomials\n"); exit(8); }
    fp il; fp_inv(&il, &A[dg]); LD(1); CTL(INV_CTL);
    for (int i = 0; i <= dg; i++) fp_mul(&out[i], &A[i], &il);
    LD(dg + 1); ST(dg + 1); loopc(dg + 1);
    xfree(A); xfree(B);
    return (size_t)dg;
}

/* Derived worst-case charge of gcd_cl(da, db).  Let S0 = da + db.  Each elimination step lowers dA + dB by at least 1 and its inner loop
 * runs dB <= (dA + dB)/2 times, so the inner iterations total at most floor(S0^2/4); eliminations E <= S0 + 1; passes <= E; the
 * degree scans lower dA by S0 + 1 in total.  Constants: inner iteration 2 arith + 2 ld + 1 st + 7 ctl = 12; elimination 25 + 11 (dA - nd);
 * pass: one inversion (330) + 1 ld + 1 address + INV_CTL + 8 ctl.  INVA is the arithmetic of fp_inv (254 squarings + 76 multiplications for the exponent p - 2). */
#define INVA 330
uint64_t gcd_cost_bound(size_t da, size_t db) {
    uint64_t S0 = da + db, cap = (da > db ? da : db) + 1;
    uint64_t inner = (S0 * S0) / 4, E = S0 + 1;
    uint64_t setup = 5 * (S0 + 2) + 2 + 2 * (S0 + 2) + 9 * (S0 + 2) + 4;
    uint64_t elim = 25 * E + 11 * (S0 + 1);
    uint64_t pass = E * (INVA + 2 + INV_CTL + 8);
    uint64_t fin = INVA + 2 + INV_CTL + 8 * cap + 4;
    return 12 * inner + elim + pass + setup + fin;
}

/* ---------- quotient and remainder by naive division ---------- */
static size_t trimlen(const fp *c, size_t len) {
    size_t it = 1;
    while (len > 0 && fp_is_zero(&c[len - 1])) { len--; it++; }
    CTL(9 * it); LD(it);
    return len;
}
void divrem(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) {
    memcpy(r, a, la * sizeof(fp)); LD(la); ST(la); loopc(la);
    fp inv; fp_inv(&inv, &b[lb - 1]); CTL(INV_CTL); LD(1);
    *lq = la - lb + 1;
    for (size_t i = la - lb + 1; i-- > 0;) {
        fp qi; fp_mul(&qi, &r[i + lb - 1], &inv); LD(1);
        q[i] = qi; ST(1);
        for (size_t j = 0; j + 1 < lb; j++) { fp t; fp_mul(&t, &qi, &b[j]); fp_sub(&r[i + j], &r[i + j], &t); }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(lb - 1);
        CTL(3 + 2 + 2);
    }
    *lr = trimlen(r, lb - 1);
}

/* Derived worst-case charge of divrem(la, lb): per quotient coefficient 14 + 12 (lb - 1) operations (1 + 2(lb-1) arithmetic, 1 + 2(lb-1) loads,
 * 1 + (lb-1) stores, 11 + 7(lb-1) control), plus the copy of the dividend (7 la + 2), one inversion, and the trimming of the remainder (11 per test). */
uint64_t div_cost_bound(size_t la, size_t lb) {
    return (uint64_t)(la - lb + 1) * (14 + 12 * (uint64_t)(lb - 1)) + 7 * (uint64_t)la + 2 + INVA + 2 + INV_CTL + 11 * ((uint64_t)lb + 1);
}

/* ---------- deflation: G / (Z - r) for a root r of the monic G (d+1 coefficients); returns d coefficients, frees G */
fp *deflate(fp *G, size_t d, const fp *r) {
    fp *Q = NEW_FP(d);
    fp b = G[d];
    Q[d - 1] = b;
    for (size_t k = d - 1; k >= 1; k--) { fp t; fp_mul(&t, r, &b); fp_add(&b, &G[k], &t); Q[k - 1] = b; }
    fp t; fp_mul(&t, r, &b); fp_add(&t, &G[0], &t);
    LD(d + 1); ST(d); loopc(d - 1); CTL(2 * d);
    CTL(4);
    if (!fp_is_zero(&t)) { fprintf(stderr, "deflate: not a root\n"); exit(79); }
    xfree(G);
    return Q;
}

/* ---------- Taylor shift: returns G(Z + a), frees G (monic, d+1 coefficients).
 * out_k = (1/k!) sum_i (i! g_i) (a^(i-k)/(i-k)!): one convolution of A'_(d-i) = i! g_i with B_j = a^j/j!. */
fp *taylor_shift(fp *G, size_t d, const fp *a) {
    size_t n = d + 1;
    fp one; fp_set_one(&one);
    fp *A = NEW_FP(n), *B = NEW_FP(n);
    fp fct = one, ii; fp_set_zero(&ii);
    for (size_t i = 0; i < n; i++) {
        if (i) { fp_add(&ii, &ii, &one); fp_mul(&fct, &fct, &ii); }
        fp_mul(&A[d - i], &G[i], &fct);
    }
    LD(n); ST(n); loopc(n); CTL(2 * n + 1);                         /* the branch i != 0, index d - i */
    xfree(G);
    fp ifd, ainv, pw, inf, jj;
    fp_inv(&ifd, &fct); CTL(INV_CTL);
    uint64_t ev[4] = { (uint64_t)d, 0, 0, 0 };
    fp_pow(&pw, a, ev); CTL(80);                                    /* a^d: bit tests */
    fp_inv(&ainv, a); CTL(INV_CTL);
    inf = ifd; fp_from_limbs(&jj, ev);
    for (size_t j = n; j-- > 0;) {
        fp_mul(&B[j], &pw, &inf);
        fp_mul(&inf, &inf, &jj); fp_sub(&jj, &jj, &one);
        fp_mul(&pw, &pw, &ainv);
    }
    ST(n); loopc(n); CTL(n);
    fp *res = A;                                                     /* the result goes into A once the product is formed */
    CTL(2);                                                          /* the test n <= 48 */
    if (n <= 48) {
        fp *C = NEW_FP(2 * n - 1);
        poly_mul(C, A, n, B, n);
        inf = ifd; fp_from_limbs(&jj, ev);
        for (size_t k = n; k-- > 0;) {
            fp_mul(&res[k], &C[d - k], &inf);
            fp_mul(&inf, &inf, &jj); fp_sub(&jj, &jj, &one);
        }
        LD(n); ST(n); loopc(n); CTL(n);
        xfree(C); xfree(B);
        return res;
    }
    plan_t P = plan3_for_len(2 * n - 1);
    fp *out = NEW_FP(P.N), *tA = NEW_FP(P.n), *tB = NEW_FP(P.n);
    const fp *As[1] = { A }, *Bs[1] = { B }; size_t lA[1] = { n }, lB[1] = { n }; int sg[1] = { 1 };
    conv_sum_otf(&P, out, 1, As, lA, Bs, lB, sg, tA, tB, n);
    fp invN; plan_invN(&P, &invN);
    inf = ifd; fp_mul(&inf, &inf, &invN); fp_from_limbs(&jj, ev);
    for (size_t k = n; k-- > 0;) {
        fp_mul(&res[k], &out[d - k], &inf);
        fp_mul(&inf, &inf, &jj); fp_sub(&jj, &jj, &one);
    }
    LD(n); ST(n); loopc(n); CTL(2 * n);
    xfree(out); xfree(tA); xfree(tB); xfree(B);
    return res;
}

/* ---------- Z^((p-1)/2) mod G.  d <= 40: schoolbook square-and-multiply; otherwise the lean NTT schedule ---------- */
static void sqr_mod(fp *r, const fp *a, const fp *G, size_t d) {
    fp *t = NEW_FP(2 * d);
    for (size_t i = 0; i < 2 * d; i++) fp_set_zero(&t[i]);
    for (size_t i = 0; i < d; i++) {
        fp x; fp_sqr(&x, &a[i]); fp_add(&t[2 * i], &t[2 * i], &x);
        for (size_t j = i + 1; j < d; j++) { fp y; fp_mul(&y, &a[i], &a[j]); fp_add(&y, &y, &y); fp_add(&t[i + j], &t[i + j], &y); }
    }
    for (size_t i = 2 * d - 1; i-- > d;) {
        fp c = t[i];
        for (size_t j = 0; j < d; j++) { fp u; fp_mul(&u, &c, &G[j]); fp_sub(&t[i - d + j], &t[i - d + j], &u); }
        fp_set_zero(&t[i]);
    }
    for (size_t i = 0; i < d; i++) r[i] = t[i];
    xfree(t);
}
static void mulx_mod(fp *r, const fp *G, size_t d) {         /* r := Z r mod G */
    fp c = r[d - 1];
    for (size_t i = d - 1; i >= 1; i--) { fp t; fp_mul(&t, &c, &G[i]); fp_sub(&r[i], &r[i - 1], &t); }
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&r[0], &t);
}
void pow_half(fp *S, const fp *G, size_t d) {
    CTL(2);                                                          /* the test d > 40 */
    if (d > 40) { powx_lean(S, G, d, PALLAS_PM1H, 1); return; }
    snap_t s0 = snap();
    for (size_t i = 0; i < d; i++) fp_set_zero(&S[i]);
    fp_set_one(&S[1]);
    int top = 253; while (top >= 0 && !((PALLAS_PM1H[top / 64] >> (top % 64)) & 1)) { top--; CTL(12); }
    for (int bit = top - 1; bit >= 0; bit--) {
        sqr_mod(S, S, G, d);
        if ((PALLAS_PM1H[bit / 64] >> (bit % 64)) & 1) mulx_mod(S, G, d);
        CTL(3 + 7 + 2 + 3);
    }
    bound_mem_since(s0);
}

/* ---------- number of tries per level: ceil(40/(d-1)) for d <= 40, one try above ---------- */
size_t split_tries(size_t d) { return d > 40 ? 1 : (40 + d - 2) / (d - 1); }

/* Root isolation.  G: monic, d >= 1, product of d distinct linear factors over F_p, d+1 coefficients (consumed).
 * Level: shift by a random c (G(Z - c), roots r + c), S = Z^((p-1)/2) mod G, A = gcd(G, S - 1) = the roots whose shifted value is a
 * nonzero square; the split is proper if 1 <= deg A <= d - 1; continue with the piece of smaller degree (A, or G / A).
 * Returns 0 if a level has no proper split after split_tries(d) tries. */
int split_find_root(fp *root, fp *G, size_t d) {
    fp shift; fp_set_zero(&shift);
    snap_t t0;
    while (d >= 3) {
        size_t t = split_tries(d); int proper = 0;
        CTL(3 + 3 + 6);                                              /* loop test, call of split_tries (two compares, branch, subtract, add, divide) */
        SPL_levels++;
        for (size_t tr = 0; tr < t && !proper; tr++) {
            CTL(3 + 2);
            SPL_tries++;
            fp c, mc; rnd_fp254(&c); fp_neg(&mc, &c);
            t0 = snap();
            G = taylor_shift(G, d, &mc);
            fp_add(&shift, &shift, &c);
            SPL_shift += snap_total(snap_sub(snap(), t0));
            t0 = snap();
            fp *S = NEW_FP(d);
            pow_half(S, G, d);
            SPL_pow += snap_total(snap_sub(snap(), t0));
            t0 = snap();
            fp one; fp_set_one(&one); fp_sub(&S[0], &S[0], &one); LD(1); ST(1);
            fp *Ap = NEW_FP(d + 1);
            snap_t tg = snap();
            size_t a = gcd_cl(Ap, G, d, S, d - 1);
            uint64_t gch = snap_total(snap_sub(snap(), tg));
            xfree(S);
            SPL_gcd += snap_total(snap_sub(snap(), t0));
            if (gch > gcd_cost_bound(d, d - 1)) { fprintf(stderr, "gcd charge above its bound\n"); exit(81); }
            CTL(4);
            if (a >= 1 && a <= d - 1) {
                size_t b = d - a;
                CTL(3);
                if (a <= b) { xfree(G); G = Ap; d = a; }
                else {
                    t0 = snap();
                    size_t dold = d; fp *q = NEW_FP(b + 1), *rem = NEW_FP(d + 1); size_t lq, lr;
                    divrem(q, &lq, rem, &lr, G, d + 1, Ap, a + 1);
                    CTL(4);                                                  /* the test of the remainder and the quotient length */
                    if (lr != 0 || lq != b + 1) { fprintf(stderr, "split: division left a remainder\n"); exit(80); }
                    xfree(rem); xfree(Ap); xfree(G); G = q; d = b;
                    SPL_div += snap_total(snap_sub(snap(), t0));
                    if (snap_total(snap_sub(snap(), t0)) > div_cost_bound(dold + 1, a + 1)) { fprintf(stderr, "division charge %llu above its bound %llu (la=%zu lb=%zu)\n", (unsigned long long)snap_total(snap_sub(snap(), t0)), (unsigned long long)div_cost_bound(dold + 1, a + 1), dold + 1, a + 1); exit(82); }
                }
                proper = 1;
            } else xfree(Ap);
        }
        if (!proper) { xfree(G); return 0; }
    }
    fp r;
    CTL(3);
    if (d == 2) {
        fp b2, disc, four, s, two, itwo, nb;
        fp_sqr(&b2, &G[1]); fp_add(&four, &G[0], &G[0]); fp_add(&four, &four, &four); fp_sub(&disc, &b2, &four);
        LD(2);
        CTL(2);
        if (!fp_sqrt(&s, &disc)) { xfree(G); return 0; }
        CTL(12000);
        fp one; fp_set_one(&one); fp_add(&two, &one, &one); fp_inv(&itwo, &two); CTL(INV_CTL);
        fp_sub(&nb, &s, &G[1]); fp_mul(&r, &nb, &itwo);
    } else {
        fp_neg(&r, &G[0]); LD(1);
    }
    fp_sub(root, &r, &shift);
    xfree(G);
    return 1;
}
```

### twofam.c

```c
/* Orchard Poseidon, r partial rounds: two-family collision attack with a proved success probability.
 * usage: twofam r seed [family wordhex]     (the optional pair forces the sampled point x, for tests)
 *        twofam selftest
 * One attempt: sample x uniformly from C_0 u C_1 (2p-1 inputs), y = H(x); for h = 0, 1: F_h(W) = f_h(W) - y (degree 5^(6+r)),
 * R = W^p mod F_h, G = gcd(F_h, R - W) = product of the distinct roots in F_p, remove the roots that are x itself, and
 * isolate one remaining root (split.c).  Every field operation, load, store, loop-control op and random word is counted. */
#include "attack.h"
#include "pallas_consts.h"
#include <time.h>
#include <math.h>

typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[32]; static int nst;
static snap_t cur; static clock_t tcur;
static size_t gpeak;
static void stage_begin(void) { cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
    printf("  %-44s arith=%14llu other=%14llu total=%14llu %7.1fs peak=%zu\n", name, (unsigned long long)snap_arith(s->d),
           (unsigned long long)(snap_total(s->d) - snap_arith(s->d)), (unsigned long long)snap_total(s->d), s->sec, s->peak);
    fflush(stdout);
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

static size_t degD(int r) { size_t D = 1; for (int i = 0; i < 6 + r; i++) D *= 5; return D; }

/* F = (f_h - y) / lead, monic of degree D, from D+1 .. N evaluations of the digest on the family at W = theta^k (k < N, N = 3 * 2^a >= D + 1) */
static void build_F(fp *F, const line_t *L, const fp *y, int r) {
    size_t D = degD(r);
    plan_t P = plan_for_len(D + 1, 1);
    size_t H = P.N;
    fp *buf = NEW_FP(H);
    fp theta, s, one;
    fp_set_one(&one);
    plan_theta(&P, &theta);
    s = one;
    for (size_t k = 0; k < H; k++) {
        fp F1;
        snap_t e0 = snap();
        tail_eval(&F1, L, &s, r);
        snap_restore(e0);
        X.perm += (uint64_t)poseidon_C(r);               /* one target-compression unit per evaluation of H */
        buf[layout_index(&P, k)] = F1;
        fp_mul(&s, &s, &theta);
        CTL(2 + 4);
    }
    ST(H); loopc(H);
    ntt_inv(&P, buf, D + 1);                              /* buf[k] = N f_k */
    fp invN, lead, il, sc, t;
    plan_invN(&P, &invN);
    fp_mul(&lead, &buf[D], &invN);                        /* leading coefficient of f_h */
    if (fp_is_zero(&lead)) { printf("leading coefficient is zero\n"); exit(78); }
    CTL(3);
    fp_inv(&il, &lead); CTL(INV_CTL);
    fp_mul(&sc, &invN, &il);
    for (size_t k = 0; k < D; k++) fp_mul(&F[k], &buf[k], &sc);
    fp_mul(&t, y, &il); fp_sub(&F[0], &F[0], &t);
    fp_set_one(&F[D]);
    LD(D + 1); ST(D + 1); loopc(D + 1);
    xfree(buf);
}

/* ---- 256-bit helpers (constants of the program: N = 2p - 1) */
static int lt256(const uint64_t a[4], const uint64_t b[4]) { for (int i = 3; i >= 0; i--) { if (a[i] != b[i]) return a[i] < b[i]; } return 0; }
static void sub256(uint64_t r[4], const uint64_t a[4], const uint64_t b[4]) { unsigned __int128 br = 0; for (int i = 0; i < 4; i++) { unsigned __int128 d = (unsigned __int128)a[i] - b[i] - (uint64_t)br; r[i] = (uint64_t)d; br = (d >> 64) & 1; } }
static void add1_256(uint64_t r[4], const uint64_t a[4]) { unsigned __int128 c = 1; for (int i = 0; i < 4; i++) { unsigned __int128 s = (unsigned __int128)a[i] + (uint64_t)c; r[i] = (uint64_t)s; c = s >> 64; } }

int main(int argc, char **argv) {
    int r = argc > 1 && strcmp(argv[1], "selftest") ? atoi(argv[1]) : 1;
    int selftest = argc > 1 && !strcmp(argv[1], "selftest");
    uint64_t seed = argc > 2 ? strtoull(argv[2], 0, 0) : 1;
    int force_h = argc > 3 ? atoi(argv[3]) : -1;
    rng_seed(seed);
    size_t D = degD(r);
    printf("r=%d seed=%llu D=%zu\n", r, (unsigned long long)seed, D);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    uint64_t total_all = 0;
    nst = 0;
    stage_begin(); ntt_init(16); stage_end("init (twiddle table)");
    line_t L[2]; fp W0s, W1s;
    stage_begin();
    {
        snap_t s0 = snap();
        line_setup(&L[0], 0); line_setup(&L[1], 1);
        /* intersection of the two families: Q0 + t0 (a0,b0) = Q1 + t1 (a1,b1) */
        fp dU, dV, det, idet, t, u, t0, t1, ta, tb;
        fp_sub(&dU, &L[1].UQ, &L[0].UQ); fp_sub(&dV, &L[1].VQ, &L[0].VQ);
        fp_mul(&t, &L[1].a, &L[0].b); fp_mul(&u, &L[0].a, &L[1].b); fp_sub(&det, &t, &u);        /* a1 b0 - a0 b1 */
        fp_inv(&idet, &det);
        fp_mul(&t, &L[1].a, &dV); fp_mul(&u, &dU, &L[1].b); fp_sub(&ta, &t, &u); fp_mul(&t0, &ta, &idet);   /* (a1 dV - b1 dU)/det */
        fp_mul(&t, &L[0].a, &dV); fp_mul(&u, &L[0].b, &dU); fp_sub(&tb, &t, &u); fp_mul(&t1, &tb, &idet);   /* (a0 dV - b0 dU)/det */
        fp_pow5(&W0s, &t0); fp_pow5(&W1s, &t1);
        bound_mem_since(s0); CTL(INV_CTL);
    }
    stage_end("two line setups + intersection");
    if (selftest) {
        /* uncounted checks */
        snap_t keep = snap();
        fp n1, r1, n2, r2;
        map_back(&n1, &r1, &L[0], &W0s); map_back(&n2, &r2, &L[1], &W1s);
        printf("intersection consistent: %d\n", fp_eq(&n1, &n2) && fp_eq(&r1, &r2));
        fp d0, d1;
        tail_eval(&d0, &L[0], &W0s, r); tail_eval(&d1, &L[1], &W1s, r);
        fp h0; poseidon_hash_r_fp(&h0, &n1, &r1, r);
        printf("digest on both families equals the reference hash: %d\n", fp_eq(&d0, &h0) && fp_eq(&d1, &h0));
        fp zero; fp_set_zero(&zero);
        fp y; rnd_fp254(&y);
        fp *F = NEW_FP(D + 1);
        build_F(F, &L[1], &zero, r);
        fp w, acc; rnd_fp254(&w); fp_set_zero(&acc);
        for (size_t k = D + 1; k-- > 0;) { fp_mul(&acc, &acc, &w); fp_add(&acc, &acc, &F[k]); }
        fp ev, lead_ev; tail_eval(&ev, &L[1], &w, r);
        /* F is monic scaled: compare F(w) * lead with f(w): recover lead from tail_eval at two points is awkward; compare ratios */
        fp w2; rnd_fp254(&w2); fp acc2; fp_set_zero(&acc2);
        for (size_t k = D + 1; k-- > 0;) { fp_mul(&acc2, &acc2, &w2); fp_add(&acc2, &acc2, &F[k]); }
        fp ev2; tail_eval(&ev2, &L[1], &w2, r);
        fp lhs, rhs; fp_mul(&lhs, &acc, &ev2); fp_mul(&rhs, &acc2, &ev);
        printf("interpolated polynomial matches the digest at 2 random points (ratio test): %d\n", fp_eq(&lhs, &rhs));
        (void)lead_ev; (void)y;
        xfree(F);
        snap_restore(keep);
        return 0;
    }
    /* ---- sample x uniformly from the union ---- */
    stage_begin();
    uint64_t Nlim[4], w[4], Plim[4], W1l[4];
    {   /* N = 2p - 1 */
        unsigned __int128 c = 0;
        for (int i = 0; i < 4; i++) { unsigned __int128 s = (unsigned __int128)PALLAS_P[i] * 2 + (uint64_t)c; Nlim[i] = (uint64_t)s; c = s >> 64; }
        uint64_t one4[4] = { 1, 0, 0, 0 }; sub256(Nlim, Nlim, one4);
        memcpy(Plim, PALLAS_P, 32);
    }
    int hx; fp Wx;
    if (force_h >= 0) {
        hx = force_h; fp_from_hex(&Wx, argv[4]);
        CTL(10);
    } else {
        int got = 0;
        for (int tr = 0; tr < 128 && !got; tr++) {
            rnd_u256(w); CTL(3 + 8);                                  /* loop, comparison with N */
            if (lt256(w, Nlim)) got = 1;
        }
        if (!got) { printf("sampling halt\n"); return 3; }
        CTL(8);
        if (lt256(w, Plim)) { hx = 0; fp_from_limbs(&Wx, w); }
        else {
            uint64_t v[4]; sub256(v, w, Plim); CTL(8);
            fp_to_limbs(W1l, &W1s); CTL(8);
            if (!lt256(v, W1l)) { add1_256(v, v); CTL(8); }
            hx = 1; fp_from_limbs(&Wx, v);
        }
    }
    CTL(6 + 40);                                                     /* family test and the control of the driver (calls, tests of found and failed) */
    int x_is_I = (hx == 0 && fp_eq(&Wx, &W0s)); CTL(4);
    fp y;
    {
        snap_t e0 = snap();
        tail_eval(&y, &L[hx], &Wx, r);
        snap_restore(e0);
        X.perm += (uint64_t)poseidon_C(r);
    }
    stage_end("sample x, y = H(x)");
    printf("x: family %d%s\n", hx, x_is_I ? " (intersection point)" : "");
    fp Wr; int found = 0, hr = -1; int failed_split = 0;
    for (int h = 0; h < 2 && !found && !failed_split; h++) {
        fp *F = NEW_FP(D + 1);
        char nm[64];
        stage_begin(); build_F(F, &L[h], &y, r); snprintf(nm, sizeof nm, "family %d: build F (evaluations + NTT)", h); stage_end(nm);
        fp *R = NEW_FP(D);
        stage_begin(); powx_lean(R, F, D, PALLAS_P, 1);
        { fp one; fp_set_one(&one); fp_sub(&R[1], &R[1], &one); LD(1); ST(1); }
        snprintf(nm, sizeof nm, "family %d: W^p mod F", h); stage_end(nm);
        fp *Gb = NEW_FP(D + 1);
        stage_begin();
        size_t dg = gcd_cl(Gb, F, D, R, D - 1);
        xfree(F); xfree(R);
        snprintf(nm, sizeof nm, "family %d: gcd(F, W^p - W)", h); stage_end(nm);
        uint64_t bound = gcd_cost_bound(D, D - 1), got = snap_total(st[nst - 1].d);
        printf("    gcd degree %zu, charged %llu, derived bound %llu (%s)\n", dg, (unsigned long long)got, (unsigned long long)bound, got <= bound ? "within" : "EXCEEDED"); fflush(stdout);
        CTL(2); if (got > bound) return 4;
        stage_begin();
        fp *G = NEW_FP(dg + 1); memcpy(G, Gb, (dg + 1) * sizeof(fp)); LD(dg + 1); ST(dg + 1); loopc(dg + 1);
        xfree(Gb);
        size_t d = dg;
        if (h == hx) { G = deflate(G, d, &Wx); d--; }
        if (h == 1 && x_is_I) { G = deflate(G, d, &W1s); d--; }
        CTL(8 + 40);                                                 /* the two tests above and the control of the driver loop over the families */
        snprintf(nm, sizeof nm, "family %d: remove the roots of x", h); stage_end(nm);
        printf("    remaining roots: %zu\n", d);
        if (d >= 1) {
            stage_begin();
            if (split_find_root(&Wr, G, d)) { found = 1; hr = h; } else failed_split = 1;
            snprintf(nm, sizeof nm, "family %d: isolate one root", h); stage_end(nm);
        } else xfree(G);
    }
    int success = 0;
    fp nk1, rho1, nk2, rho2, dg1, dg2;
    if (found) {
        stage_begin();
        snap_t s0 = snap();
        map_back(&nk1, &rho1, &L[hx], &Wx);
        map_back(&nk2, &rho2, &L[hr], &Wr);
        bound_mem_since(s0);
        stage_end("map back (two inputs)");
        stage_begin();
        poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
        poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
        { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
        stage_end("verification (2 reference hashes)");
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
        success = fp_eq(&dg1, &dg2) && !same_in;
    }
    for (int i = 0; i < nst; i++) total_all += snap_total(st[i].d);
    printf("RESULT found=%d success=%d split_levels=%llu split_tries=%llu\n", found, success, (unsigned long long)SPL_levels, (unsigned long long)SPL_tries);
    if (success) {
        phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
        phex("COLLISION digest", &dg1);
    }
    printf("SUMMARY total_all=%llu units=%.1f log2_units=%.4f heap_peak=%zu\n", (unsigned long long)total_all, (double)total_all / poseidon_C(r), log2((double)total_all / poseidon_C(r)), gpeak);
    printf("SPLIT shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_shift, (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    return success ? 0 : 1;
}
```

### test_split.c

```c
/* Tests of split.c on synthetic products of linear factors: root isolation, gcd charge against its derived bound, Taylor shift, division. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(16);
    rng_seed(argc > 1 ? strtoull(argv[1], 0, 0) : 7);
    size_t ds[] = { 1, 2, 3, 4, 5, 9, 17, 40, 41, 64, 200, 1000, 3000, 0 };
    int ok = 1;
    for (int t = 0; ds[t]; t++) {
        size_t d = ds[t];
        fp *roots = NEW_FP(d), *G = NEW_FP(d + 1);
        for (size_t i = 0; i < d; i++) rnd_fp254(&roots[i]);
        fp_set_one(&G[0]);
        size_t deg = 0;
        for (size_t i = 0; i < d; i++) {          /* multiply by (Z - r_i) */
            fp nr; fp_neg(&nr, &roots[i]);
            G[deg + 1] = G[deg];
            for (size_t k = deg; k >= 1; k--) { fp tm; fp_mul(&tm, &G[k], &nr); fp_add(&G[k], &G[k - 1], &tm); }
            fp tm; fp_mul(&tm, &G[0], &nr); G[0] = tm;
            deg++;
        }
        fp *Gc = NEW_FP(d + 1); memcpy(Gc, G, (d + 1) * sizeof(fp));
        snap_t s0 = snap(); clock_t c0 = clock();
        SPL_levels = SPL_tries = 0;
        fp root; int res = split_find_root(&root, Gc, d);
        snap_t dd = snap_sub(snap(), s0);
        int isroot = 0;
        if (res) for (size_t i = 0; i < d; i++) if (fp_eq(&roots[i], &root)) isroot = 1;
        printf("d=%zu: found=%d is_root=%d levels=%llu tries=%llu charged=%llu %.1fs\n", d, res, isroot, (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)snap_total(dd), (double)(clock() - c0) / CLOCKS_PER_SEC);
        ok &= res && isroot;
        /* taylor shift check: (G shifted by a)(z) == G(z + a) */
        fp a, z, e1, e2; rnd_fp254(&a); rnd_fp254(&z);
        fp *Gs = NEW_FP(d + 1); memcpy(Gs, G, (d + 1) * sizeof(fp));
        Gs = taylor_shift(Gs, d, &a);
        fp_set_zero(&e1); for (size_t k = d + 1; k-- > 0;) { fp_mul(&e1, &e1, &z); fp_add(&e1, &e1, &Gs[k]); }
        fp za; fp_add(&za, &z, &a); fp_set_zero(&e2); for (size_t k = d + 1; k-- > 0;) { fp_mul(&e2, &e2, &za); fp_add(&e2, &e2, &G[k]); }
        printf("   taylor shift ok: %d\n", fp_eq(&e1, &e2)); ok &= fp_eq(&e1, &e2);
        /* gcd charge vs bound: gcd(G, G') style random pair of degrees d, d-1 */
        if (d >= 2) {
            fp *B = NEW_FP(d); for (size_t i = 0; i < d; i++) rnd_fp254(&B[i]);
            fp *out = NEW_FP(d + 1);
            snap_t g0 = snap(); size_t dg = gcd_cl(out, G, d, B, d - 1); uint64_t ch = snap_total(snap_sub(snap(), g0));
            uint64_t bd = gcd_cost_bound(d, d - 1);
            printf("   gcd degree %zu charged %llu bound %llu ratio %.4f %s\n", dg, (unsigned long long)ch, (unsigned long long)bd, (double)ch / bd, ch <= bd ? "ok" : "EXCEEDED");
            ok &= ch <= bd;
            /* gcd with a known factor */
            fp *Hh = NEW_FP(d); fp_set_zero(&Hh[0]);
            xfree(B); xfree(out); xfree(Hh);
        }
        xfree(Gs); xfree(G); xfree(roots);
    }
    printf(ok ? "ALL OK\n" : "FAILURES\n");
    return !ok;
}
```

### calib.c

```c
/* Calibration of the data-independent stage charges used by the worst-case bound of the root-isolation stage.
 * usage: calib d [reps]   prints: LEVEL d shift_charge pow_charge  and the heap peaks of the two stages.
 * The charges do not depend on the coefficients (fixed loop counts), so random monic input is used. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(16);
    rng_seed(5);
    for (int i = 1; i < argc; i++) {
        if (argv[i][0] == 'r') {           /* "rD": the stage that copies a gcd of degree D and removes two roots of x (worst case) */
            size_t d = strtoull(argv[i] + 1, 0, 10);
            fp *G = NEW_FP(d + 1), *Gb = NEW_FP(d + 1); fp rt; rnd_fp254(&rt);
            fp_set_one(&G[d]); for (size_t k = 0; k < d; k++) fp_set_zero(&G[k]);
            /* G = (Z - rt) * Z^(d-1) so that rt is a root of G and of the deflated polynomial (rt is a root only of the first factor): use Z^(d-1) (Z - rt) and root 0 */
            fp_neg(&G[d - 1], &rt);
            fp zero; fp_set_zero(&zero);
            snap_t s0 = snap();
            memcpy(Gb, G, (d + 1) * sizeof(fp)); LD(d + 1); ST(d + 1); loopc(d + 1);
            fp *H = deflate(Gb, d, &zero); fp *H2 = deflate(H, d - 1, &zero);
            printf("REMOVE d=%zu charged=%llu\n", d, (unsigned long long)snap_total(snap_sub(snap(), s0)));
            xfree(H2); xfree(G);
            continue;
        }
        size_t d = strtoull(argv[i], 0, 10);
        fp *G = NEW_FP(d + 1);
        for (size_t k = 0; k < d; k++) rnd_fp254(&G[k]);
        fp_set_one(&G[d]);
        fp a; rnd_fp254(&a);
        size_t base = mem_cur; mem_reset_peak();
        snap_t s0 = snap(); clock_t c0 = clock();
        G = taylor_shift(G, d, &a);
        uint64_t sh = snap_total(snap_sub(snap(), s0)); size_t pk1 = mem_peak; double t1 = (double)(clock() - c0) / CLOCKS_PER_SEC;
        fp *S = NEW_FP(d);
        base = mem_cur; mem_reset_peak();
        s0 = snap(); c0 = clock();
        pow_half(S, G, d);
        uint64_t pw = snap_total(snap_sub(snap(), s0)); size_t pk2 = mem_peak; double t2 = (double)(clock() - c0) / CLOCKS_PER_SEC;
        printf("LEVEL d=%zu shift=%llu pow=%llu shift_abs_peak=%zu pow_abs_peak=%zu live_before=%zu secs %.1f %.1f\n", d, (unsigned long long)sh, (unsigned long long)pw, pk1, pk2, mem_cur, t1, t2);
        fflush(stdout);
        xfree(S); xfree(G);
    }
    return 0;
}
```

