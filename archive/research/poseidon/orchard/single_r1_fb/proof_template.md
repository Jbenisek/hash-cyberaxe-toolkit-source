# Orchard Poseidon, r = 1: one centre of the odd-part method on a line, half-gcd with a derived worst case, root isolation (exact ledger, low memory)

## 1. Claim

Target: `poseidon-orchard-r1-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, one partial round 4, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = @@TIME_LOG2@@` in target-compression units (`C(1) = 237` primitive operations per unit): the worst-case total of one attempt of the program,
  every executed operation charged (sections 4.2 and 6), no flat allowances for control or dispatch; every data-dependent stage is charged at a bound that is derived in section 6 and that the program checks against its own counters while it runs.
* `memory_log2_bytes = @@MEM_LOG2@@` (`@@MEM_BYTES@@` bytes, section 7), so the normalized cost is `@@TIME_LOG2@@ + @@MEM_PEN@@ = @@SCORE@@`.
* `success_probability = @@PCLAIM@@`: one attempt, one centre. Section 8 proves a lower bound of 0.3934647661 for one attempt (per-centre bound 0.3934678683, minus the proved cap-6 halt loss 3.1*10^-6, minus the root-isolation failure 2^-36); the claim is below it. The inputs of that proof that are computations are recomputed by the verifier of section 10 from the organizer constants (section 8.7).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^7`, then the roots of its odd part about a centre) is a known approach. What is offered here is a complete finite implementation with an exact operation ledger, a low-memory schedule,
  a half-gcd whose worst-case charge is derived, and a root isolation with a proved failure bound. Nothing here is an asymptotic estimate: every figure below is the count of an executed, instrumented program whose complete source is reproduced in section 10.
* The collisions stored in `certificates/` (@@N_CERT@@ pairs, each from a separate attempt of this program) are outputs of this program. They check the construction at the
  selected target with the organizer's hash; the cost and probability claims do not use them.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the
deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`.
The program uses the line `j = @@LINE@@`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant
`M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS, nonzero on the deployed constants, checked). Let
`(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, where
`d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i`
(the supports are disjoint). After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), 4 (partial, r = 1), 60, 61, 62, 63 (full) put seven S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^7 = D = 78125`. The leading coefficient is obtained by
propagating leading coefficients through the seven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x1c66a426cd2d5ec686ea41cae3a27d49c8724fffa0bc4f305029be8b2cce93c3`
(computed; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 39062`, `g_c` has degree exactly `m` and
leading coefficient `2 f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 49152 = 3 * 2^14` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 98304` evaluations of `F` are each charged as
one target-compression unit (`C(1) = 237` operations), although a line evaluation (affine start, six more rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, and the executed shifts, masks, ors, modulo operations and loop control of the bit-reversed index `layout_index`, which are counted inside that function) is charged on top.

## 4. The program (one attempt)

```
init:   twiddle table
setup:  the line (line_setup)
A  c := uniform 254-bit word (one random word + 2 control ops)
B  g := monic g_c, by section 3 (98304 evaluations + one inverse NTT of size 49152 + normalisation by the leading coefficient)
C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; 238 modular squarings, 45 of the steps also multiply by S by a streaming shift)
D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4);   if deg G = 0 the attempt fails (no root)
E  S := a root of G                 (root isolation, section 4.1)
F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
G  verify: the two reference hashes (237 operations each) are equal and the pairs differ -> output
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 15 bits after the leading one are zero, so the program starts from the monomial `S^v` with `v = 2^15 < m` (this absorbs 15 of the 253 squarings, 15 + 238 = 253), and the squaring loop of stage C has 238 steps, of which 45 also multiply by `S` (a streaming shift).
The ledger below counts what the program executes; no figure in this document assumes another weight.

Halts. The program is compiled with `-DDEG_CAP=@@CAP@@`. It ends early in exactly three ways that can happen with positive probability: stage D finds `deg G = 0` (the attempt has no useful root; a failure event of section 8), stage D finds `deg G > @@CAP@@` (the cap, charged 2 operations; a failure event of section 8, bounded there) and a level of the root isolation has no proper split after its `t(d)` tries (probability at most `2^-36` over all levels, section 4.1).
Every other test that ends the program (a charged gcd or division exceeds its derived bound, a division leaves a remainder, the leading coefficient of `g_c` is zero) cannot fire: the first two are comparisons against bounds that are derived in section 6 as a calculation (kernel charges at the maximal operand lengths, maximum number of nodes, levels and tries),
the last is a fixed property of the constants and was checked. There is one attempt, no loop over attempts, and no budget check whose failure could stop a later stage.

### 4.1 Root isolation (stage E)

Input: monic `G`, degree `d >= 1`, a product of `d` distinct linear factors over `F_p`. Output: a root.
`d = 1`: the root is `-G_0`. `d = 2`: the root is `(s - G_1) / 2` with `s = sqrt(G_1^2 - 4 G_0)` (Tonelli-Shanks; the discriminant is a square since both roots are in `F_p`).
`d >= 3`: repeat for at most `t(d)` tries, `t(d) = ceil(40 / (d - 1))` for `d <= 40` and `t(d) = 1` for `d > 40`:
draw `c` uniform in `[0, 2^254)`; replace `G(Z)` by `G(Z - c)` (Taylor shift; the roots become `r + c`); `S := Z^((p-1)/2) mod G`; `A := gcd(G, S - 1)` (monic; classical Euclid for `d <= 152`, the half-gcd of section 4.4 above).
`A` is the product of the factors whose root `r + c` is a nonzero square. If `1 <= deg A <= d - 1` the try is proper: continue with `A` if `deg A <= d - deg A`, otherwise with `G / A` (exact division, section 4.5); in both cases the new degree is at most `floor(d/2)`.
If no try of a level is proper, the attempt fails (halt). At the end the root of the final linear or quadratic factor is shifted back by the sum of the `c` used.
The roots of the final polynomial are roots of `G`: each piece divides the previous one.

**Lemma B.** Let `G` be a monic product of `d >= 3` distinct linear factors over `F_p`, `d <= 2^17`, and `c` uniform in `[0, 2^254)`. The probability that `deg gcd(G(Z - c), Z^((p-1)/2) - 1) in {0, d}` is at most `2^(1-d) + 2^-100`.
Proof. Let `r_1..r_d` be the roots, `chi` the quadratic character (`chi(0) = 0`), `E = {-r_i}`. The degree of the gcd is `#{i : chi(r_i + c) = 1}`. For `c not in E`,
`[chi(r_i + c) = 1 for all i] = prod_i (1 + chi(r_i + c))/2 = 2^-d sum_{S} chi(prod_{i in S} (r_i + c))` and `[chi(r_i + c) = -1 for all i] = 2^-d sum_S (-1)^|S| chi(prod_{i in S} (r_i + c))`.
For `S` nonempty, `prod_{i in S}(Z + r_i)` is squarefree of degree `|S|`, so by Weil's bound `|sum_{c in F_p} chi(prod_{i in S}(c + r_i))| <= (|S| - 1) sqrt(p)` (the sum is 0 for `|S| = 1`). Summing over `c not in E` costs at most `d` more per term.
So the number of `c in F_p` with all `chi = 1`, and likewise with all `chi = -1`, is at most `p/2^d + (d-1) sqrt(p) + d`, and the `c in E` add at most `d`. Dividing by `2^254 >= p (1 - 2^-128)` (the draw is uniform on a subset of `F_p`, so counts of bad values over `F_p` bound the counts over the subset):
probability `<= 2^(1-d) (1 + 2^-127) + 2 (d-1) 2^-127 + 3d 2^-254 <= 2^(1-d) + 2^-100`. QED.

**Failure bound of stage E (stated once).** Let `eps(d) = (2^(1-d) + 2^-100)^t(d)` be the failure probability of a level of degree `d`. For `d > 40`, `t = 1` and `2^(1-d) <= 2^-40`, so `eps(d) <= 2^-40 (1 + 2^-60)`.
For `3 <= d <= 40`, `t(d) (d - 1) >= 40` gives `eps(d) <= 2^-40 (1 + 2^-60)^t`. In all cases `eps(d) < 2^-39.99`. The degree at least halves at every level, and `deg G <= m = 39062`, so the levels have degrees at most
@@CAP@@, 3 (2 levels with `d >= 3`, because the cap gives `deg G <= @@CAP@@`); the ledger charges the larger schedule 9, 4. Hence the failure probability of stage E, whatever `G` is, is at most `2 * 2^-39.99 < 2^-38`.
The event `c = 0` (the Taylor shift needs `1/c`) has probability `2^-254` per try; over the at most 19 tries of the charged schedule (`t(9) + t(4) = 5 + 14`) it adds below `2^-246`, and it is included in the same bound (`2 * 2^-39.99 + 2^-246 < 2^-36`). The number of tries of a run is at most the sum of `t(d)` over the levels (@@TRIES_SUM@@).

### 4.2 Machine model and charging rules

Every item below is counted by the executing code at the statement that executes it; none is estimated. The complete source is in section 10.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation): `LD(n)` adds `n` to the load counter and `n` to the control counter, `ST(n)` likewise.
* every loop that is not unrolled: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left); `loopc(n)` adds exactly this after such a loop of `n` iterations. Loops that are unrolled (macro `FOR8` in `common.h`: the pointwise, copy, fold and subtraction loops of the powering and of the products) execute their body 8 times per pass without any branch inside the body; the macro itself adds 1 operation for the bound `n & ~7`, 3 operations at the end of every pass of 8 (index update, comparison, branch), 2 when the main loop is left, and then runs the remaining 0 to 7 elements in a plain loop (3 per iteration, 2 on exit). The loads and stores of the body are charged inside the body, per element.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, multiplication, modulo, comparison, conditional branch, and the selection of an element of the register block (16 data words) by a computed index. They are added with `CTL(k)` next to the statement that executes them, and data-dependent tests are charged per executed test.
* transform kernels are generated, straight-line code (`gen_kern.py` is part of the source of section 10; its output `ntt_kern.h` and `ntt_a3.h` are listed there). A block kernel for `k` layers (1 to 4; 2^k data words `x[]`) has no loop and no branch: each butterfly is the literal statements `fp_sub`, `fp_add`, `fp_mul` (three field operations, none for the multiplication when the twiddle is 1 at `b = 0`), and every twiddle load is a literal statement carrying its own charge on the same line: the first twiddle of a layer `tw + (b << sjs[j])`: shift and addition (2 operations), the load and its address formation (`LD(1)`); every further twiddle of the layer: one addition of the stride `D[j]` and `LD(1)`. In the inverse kernel the first twiddle address `tw + ((nh - (b << sj[j])) << sh)` costs 4 operations. The kernel for `b = 0` is a second generated variant that omits the twiddle of `tp = 0` (it is 1) and its multiplication. A pass function (`pf1..4`, `pi1..4`, `pu1..4_sq/_mul` in `ntt_kern.h`) contains the group loop and the block loop around the kernel: group base address (1), block base address (1), 3 operations per loop iteration and 2 on loop exit as written in the generated code, the loads and stores of the 2^k words of the block each with `LD(1)` / `ST(1)` (one address formation each); the block `b = 0` of a group is peeled so that no per-block test of `b` is executed. The wrapper (`pass_fwd`, `pass_inv`, `pass_fused`) charges the computation of the pass constants (a loop over the layers) and the `switch` on `k` (and on the mode) once per pass.
* working registers (disclosed assumption): a block keeps its 2^k <= 16 data words `x[]` in registers; the twiddle operand and the butterfly temporary need two further words, so the kernels assume a register file of 18 words of 256 bits. Strides, shift counts, base pointers and loop indices are held in integer registers (not charged as memory accesses). The 256-bit constants of the radix-3 kernels (`W3[1]`, `W3[2]`, `CH`, `DL`) are not assumed to be in registers: every use is charged as one load (`LD(1)` in the generated statement). The real cost of a machine with fewer registers would be higher; this is the one structural assumption of the model.
* a random word: 1 plus 2 control operations for a 254-bit word (`rnd_fp254`).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 237 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* dispatch and selection: the source contains `switch` statements (on `k` and on the mode, once per pass) and three tables of function pointers (`RGF`, `RGI`, `RGR`: the region driver of the radix-3 stage chosen by the pattern of nonzero inputs and the class of `c0`, once per region); each is charged by `CTL` next to the statement (4 operations for a table lookup and indirect call, 4 for the `switch` on `k`). Every other selection (`if`, `?:`, `while` tests, the test of the mode in `pass_fused`, the tests of `P->rows`, the choice of the operand pointer in `conv_core`, the validity tests, the choice between the schoolbook and the fast division, the tests of the recursion in `hgcd`) is charged by a `CTL` next to the statement, as the comments show.
* radix-3 stage (generated in `ntt_a3.h`): the positions `i0` of a row are processed by straight-line position kernels, one per (pattern of nonzero inputs, rotation): `LD(1)` per nonzero input, the field operations of the selected linear map written out (each multiplication by a constant preceded by the `LD(1)` of the constant), `ST(1)` per output. A region driver runs the kernels of the three phases of `i0 mod 3` over a range of positions: head (positions until the phase is 0), a loop of three positions per iteration (`i += 3`, comparison, branch: 4 operations per iteration), tail; every test of the head, loop bound and tail is charged next to its statement. The ranges of constant pattern are computed by `split_regions` (breakpoints, insertion sort, patterns), each of whose operations is charged next to its statement; one call costs a few hundred operations.
* every executed statement of the stages (`poly_gcd_own`, `hgcd`, `divrem_fast`, `gcd_cl`, `taylor_shift`, `split_find_root`) is charged where it is written, including the compare, branch and subtraction of every loop test, as the comments of section 10 show.
* Montgomery conversions: every conversion of an integer to or from the internal representation (`fp_from_limbs`, `fp_to_limbs`, `fp_from_u64`, `fp_from_hex`; for example the loop counter and the random words in `taylor_shift` and `rnd_fp254`, the constants of the twiddle setup, the inputs and output of the two reference hashes) is one Montgomery multiplication and is charged as one field multiplication in `pallas.c`, so it is inside every count of section 6 (the instrumented totals, the calibration records and the ledger run). The constants of `pallas_consts.h` are stored in Montgomery form and need no conversion.
* Not charged, and why: (a) the bookkeeping of the allocator (`xalloc`, `xfree`: a header word, a running sum for the peak): the abstract machine of the cost rules has no allocator, its working state is a set of arrays at fixed addresses, which is exactly what the memory figure of section 7 measures; the model's primitive operations (field addition and multiplication, 256-bit load and store, logic, shift, comparison, branch, random word) do not include allocation; (b) formatting and printing: they occur only under the verbose flag of the ledger run and are not part of the submitted computation, whose output is the two inputs (already in memory) of the collision.

### 4.3 Stage C: the powering schedule (in place, no stored spectra)

For the exponent `E` (here `(p-1)/2`), `m` the degree of the modulus, `N = 3 * 2^a >= 2m - 1` and `N' = 3 * 2^b >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; each radix-3 leaf costs 8 operations) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most four layers (blocks of at most 16 data words in registers; with the two working words the register file is 18 words of 256 bits, see section 4.2). The state is `s = a / N` so no scaling is needed in the loop.
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
`MU` is computed once from `g` by Newton iteration with the same row-wise products. The leading exponent bits are absorbed by starting from the monomial `S^v` with `v < m`.
All charges of this stage depend only on `m` and the exponent, not on the coefficients.

### 4.4 Stage D: the half-gcd

Notation: a polynomial is stored as its coefficient array with the top coefficient nonzero (length = degree + 1). Euclid sequence of `(a, b)`, `deg a > deg b`: `r_0 = a`, `r_1 = b`, `r_{i-1} = q_i r_i + r_{i+1}`; `d_j = deg q_1 + ... + deg q_j`, so `deg r_j = deg a - d_j`;
`R_j = Q_1 ... Q_j` with `Q_i = [[q_i, 1], [1, 0]]` (entries of degree at most `d_j`; the first-row entries of degree exactly `d_j` for `r11`), and `(r_0, r_1)^T = R_j (r_j, r_{j+1})^T`.

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})`. The code: if `b = 0` or `n - deg b > k` return the identity. If `k <= 48`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter.
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`); (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `R2, (c', d') = hgcd(d, e, k - d_1 - deg q)`; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 96`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; below 96 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications).

**Fact 1 (truncation).** Let `a = a* x^s + a0`, `b = b* x^s + b0`, `deg a0, deg b0 < s`, `deg a* = 2 k1 > deg b*`, and let `h` be such that `d*_h <= k1` for the Euclid sequence of `(a*, b*)` (starred quantities). Then the first `h` quotients of `(a, b)` equal those of `(a*, b*)`, and
`(r_h, r_{h+1}) = (x^s r*_h + e_h, x^s r*_{h+1} + e_{h+1})` with `deg e_h, deg e_{h+1} < s + d_h`.
Proof. The entries of `R_i^{-1}` are polynomials of degree at most `d_i`, so `(r_i, r_{i+1}) = R_i^{-1}(a, b) = x^s R_i^{-1}(a*, b*) + R_i^{-1}(a0, b0)` has errors `e_i, e_{i+1}` of degree `< s + d_i`. Induction on `i < h`: with `q*` the next quotient of the top parts,
`r_i - q* r_{i+1} = x^s r*_{i+2} + (e_i - q* e_{i+1})`, where `deg (x^s r*_{i+2}) < s + deg r*_{i+1}` and `deg (e_i - q* e_{i+1}) <= s + d_i + deg q* - 1 = s + d_{i+1} - 1 < s + deg r*_{i+1}`, because `deg r*_{i+1} = 2 k1 - d*_{i+1} >= k1 >= d_{i+1}`.
So the remainder of `r_i` by `r_{i+1}` has degree below `deg r_{i+1} = s + deg r*_{i+1}`: `q*` is the true quotient. QED.

**Fact 2 (progress of the second call).** In a node with parameter `k > 48` for which step (4) is executed, `d_1 + deg q >= k1 + 1` (`d_1 = deg R1`). Consequently the parameter of the second call is `k' = k - d_1 - deg q <= k - k1 - 1` and the first polynomial `d` of the second call has degree at most `n - k1 - 1`.
Proof. If `R1` is the identity, the first quotient of the top parts has degree `> k1` and equals `deg a* - deg b* = n - deg b` (the true first quotient degree), so `deg q > k1`, `d_1 = 0`, and `deg d = deg b < n - k1`. Otherwise, with `h >= 1` the number of quotients of `R1`, maximality of `h` gives `d*_{h+1} > k1`, so `deg r*_{h+1} = 2 k1 - d*_{h+1} <= k1 - 1`;
by Fact 1 `deg r_{h+1} <= max(s + k1 - 1, s + d_h - 1) = s + k1 - 1`, while `deg r_h = n - d_h = s + 2 k1 - d_h`. Hence `deg q = deg r_h - deg r_{h+1} >= k1 + 1 - d_h`, and `deg d = deg r_{h+1} <= s + k1 - 1 = n - k1 - 1`. QED.

**Fact 3 (outer loop).** After `hgcd(a, b, k)` with `k = floor((n+1)/2)`, `deg d < n - k`, so the next outer degree is at most `floor(n/2) - 1`.

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

### 4.5 Exact division in stage E

When `deg A > d/2`, `G / A` is computed with `divrem_any(G, A)`; the remainder is checked to be zero (it is, as `A | G`).

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes
and compares them; the output is only emitted if they are equal and the pairs differ. Independent of the program, the pairs in `certificates/` are checked by the organizer's hash.

## 6. Ledger (primitive operations; `C(1) = 237`)

The counts of the data-independent stages are the exact totals of the instrumented execution (`arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 237-operation unit charges).
The stages whose cost depends on the data are charged at derived bounds, which are not observations:

* **Stage D (gcd), `deg g = m = 39062`, `deg (R - 1) <= m - 1`.** The bound `B_gcd(d)` is the evaluation of the following recursion (program `gcdbound`, section 10), in which every kernel is charged at the cost of the executed kernel on operands of the maximal length.
  `B_hgcd(n, k)` for `k <= 48`: at most `k` division steps with `sum (deg q_i + 1) <= 2k`, each at the schoolbook bound `div_cost_bound` at length `n + 1`, plus `k` matrix updates at the maximum over the splits `d_1 + deg q <= k`.
  For `k > 48`: `B_hgcd(2 k1, k1)` (first call) `+ max(K_apply(n+1, k1), copy) + B_div(n, min(k,n) + 1) + B_hgcd(n - k1 - 1, k - k1 - 1)` (second call, Fact 2) `+ K_mulQ + K_matmul` (matrix wanted) `+ 28 (n + 1) + 200`.
  `B_gcd(n) = sum over the outer iterations m_0 = n, m_{i+1} = floor(m_i / 2) [ B_hgcd(m_i, floor((m_i + 1)/2)) + B_div(m_i, m_i + 1) ] + classical end + monic scaling`.
  `K_apply(l, K)`, `K_matmul`, `K_mulQ` and `K_divfast` are the charges of the executed kernels (`apply_inv`, `mat_mul`, `mat_mulQ`, `divrem_fast`) on operands whose coefficients are all nonzero, of the maximal lengths (for `apply_inv` the output length is fixed to `l = la`, so its charge depends on `la` and `K` only);
  the data-dependent scans (`trimlen`, 10 per entry) and the search of the 64-entry cache in `plan_invN` (at most 448 per call) are added at their worst case. Every charge of a kernel is a nondecreasing function of its operand lengths (all its loops run over the lengths and its plan is the smallest `3 * 2^a` covering the output length), so the charge at the maximal lengths bounds every execution.
  The value for `(39062, 39061)` is @@GCD_BOUND@@ operations; the run of this ledger charged @@GCD_OBS@@ (ratio @@GCD_RATIO@@). The program asserts `charged <= bound` for the main gcd and for every gcd of the root isolation (exit status 81 otherwise); the table of bounds (`gcd_bounds.h`, section 10) is generated by `gcdbound H`.
  Tests: the gcd was compared with classical Euclid on planted gcds with normal and abnormal remainder sequences (`test_hgcd`, section 10).
* **Stage E (root isolation), worst case.** The levels of section 4.1 start at degree at most 9 (the cap gives `deg G <= @@CAP@@`; 9 is charged, which is larger) and halve. For each level of degree `d` and each of its `t(d)` tries the charge is `shift(d) + pow(d) + gcd bound(d) + div bound(d)` plus the random word and control (about 60 operations),
  where `shift(d)` (the Taylor shift) and `pow(d)` (`Z^((p-1)/2) mod G`) are measured at that exact degree on random input (their cost does not depend on the coefficients), `gcd bound(d)` is `gcd_cost_bound(d, d-1)` (closed form, derived in section 10 `split.c`) for `d <= 152` and the table value above,
  and `div bound(d)` is the maximum over `a` in `(d/2, d)` of `div_cost_bound(d + 1, a + 1)` for `d <= 152` (schoolbook) and `B_div(d, d/2 + 1)` above (the division of `G` by `A` happens only when `deg A > d/2`; asserted at every division).
  The last level (`d = 2`) costs @@QUAD@@ operations (one square root with its control charge, one inversion). No margin or extrapolation is applied: the table lists the exact measured values for shift and pow at the charged degrees 9 and 4, the closed-form gcd bound `T_full(d)` and the division bound, summed as they are.
  *Why the schedule (9, 4) covers every reachable schedule.* Under the cap `deg G <= @@CAP@@`, so the levels that can occur are `d_0 <= @@CAP@@`, then at most `floor(d_0/2)` (the smaller piece). The charged schedule is the larger one (9 with 5 tries, 4 with 14 tries). The build script recomputes, from calibration records at every degree 3..9, the total of each reachable schedule with the same formula and asserts that the charged total is at least the largest of them: @@DOM_NOTE@@.
  *Derivation of `T_full(d)` (classical gcd, `gcd_cl` of section 10, called as `gcd_cl(Ap, G, d, S, d - 1)`).* The inner loop of the shipped code is
  `for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }` followed by `LD(2 * dB); ST(dB); loopc(dB); CTL(dB);`.
  One iteration is charged 1 multiplication + 1 subtraction (2 arithmetic), 2 loads and 1 store (3), 3 address operations (`LD`, `ST` add one control operation each), 3 loop-control operations (`loopc` adds `3n + 2` per loop) and 1 for `CTL(dB)`: 2 + 3 + 3 + 3 + 1 = 12 operations. Each elimination step lowers `dA + dB` by at least 1 and its inner loop runs `dB <= (dA + dB)/2` times, so with `S0 = deg a + deg b = 2d - 1` the inner iterations total at most `floor(S0^2/4) = d^2 - d`, the eliminations at most `E = S0 + 1 = 2d`, and the outer passes (one inversion each) at most `E`.
  The other terms are the constants written in `gcd_cost_bound` (section 10): elimination `25 E + 11 (S0 + 1)`, pass `E (330 + 2 + 2310 + 8)` (330 arithmetic operations of `fp_inv`, `INV_CTL = 2310`), setup `16 (S0 + 2) + 6`, final scaling `330 + 2 + 2310 + 8 (d + 1) + 4`. Substituting `S0 = 2d - 1`: `12(d^2 - d) + 72 d + 5300 d + (32 d + 22) + (8 d + 2654) = 12 d^2 + 5400 d + 2676`.
  So `T_full(9) = 52,248` and `T_full(4) = 24,468`, which are the "gcd bound" entries of the table; the program asserts `charged <= gcd_cost_bound(d, d - 1)` at every gcd of the root isolation (exit status 81 otherwise).

@@LEDGER_TABLE@@

Worst case of one attempt (stage D finds the largest possible `G`, stage E runs to the end at the worst degrees):
`@@WORST_FORMULA@@ = @@WORST_TOTAL@@` operations `= @@WORST_UNITS@@` units, `time_log2 = @@TIME_LOG2_EXACT@@`, claimed as `@@TIME_LOG2@@` (rounded up).
(A run in which stage D finds no root stops after about @@TYP_NOROOT@@ operations; a run in which `G` is linear charges about @@TYP_ROOT@@, as in the logs of this ledger.)
Composition by type of the ledger run (init included; the control counter includes the address operations of loads and stores): add `@@T_ADD@@`, sub `@@T_SUB@@`, mul `@@T_MUL@@`, sqr `@@T_SQR@@`, loads `@@T_LD@@`, stores `@@T_ST@@`, control `@@T_CTL@@`, unit charges `@@T_PERM@@`.

Stage C in detail (m = 39062): Newton for MU: @@NEWTON@@ operations; prefix and scaling: @@PREFIX@@; 238 squaring steps at @@PER_STEP@@ operations each (arith @@PER_STEP_ARITH@@). Of the arithmetic of stage C, @@POW_ARITH@@ operations; the transforms are the largest term.

### 6.1 Ledger recomputation

```python
@@LEDGER_PY@@
```

## 7. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer (each buffer is one allocation). Stage C at `m = 39062`: the twiddle table (`2^14` elements, 524,288 bytes), `Y` (`3 * 2^15` elements, 3,145,728), `tmp` (`2^15` elements, 1,048,576), `MU` (1,249,952),
`g` (1,250,016) and the result `F` (1,249,984). Tracked peaks of the ledger run per stage: @@STAGE_PEAKS@@. For the worst-case root isolation the stages at the degrees of the level schedule were run by the calibration program: Taylor shift @@PEAK_SHIFT@@, powering @@PEAK_POW@@ bytes (including the live arrays), the gcd stage of the top level (the half-gcd of degrees 39062 and 39061 is stage D of the ledger run itself, whose tracked peak is in the list above; no gcd of that size occurs in the root isolation under the cap, so `test_keep` is not used) @@PEAK_GCD@@;
the largest is @@HEAP_PEAK@@ bytes. To the heap peak we add the static image of the executable (code, constants and tables: @@STATIC_DESC@@), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit) and 4,096 bytes for the allocator's own metadata:
`@@MEM_BYTES@@` bytes `= 2^@@MEM_LOG2@@`. The memory penalty is `max(0, @@MEM_LOG2@@ - 20) = @@MEM_PEN@@`.
Counted: every buffer of the program (the tracked heap peak above), the executable's own code, constants and tables (text + data + bss), the stack bound and the allocator metadata. Not counted, as they are not part of the abstract program: the dynamically linked C library code and loader mappings and the kernel structures of the host process; the program uses the library only for `malloc`/`free`/`memcpy`/`memset` (whose buffers are counted) and, in the diagnostic ledger run only, printing.
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

@@SECTION8@@

## 9. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the root-isolation proof (4.1), the half-gcd facts (4.4), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 10), @@N_CERT@@ machine-checked collision certificates (`certificates/`, checked by the organizer's hash).
  The success-probability proof is section 8 (final); its computed inputs are recomputed by `certb_verify.py` (section 10) in the time stated in section 8.7; the witness data themselves (several MB) are not shipped.
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package contains only the certificates, so the C source is part of this document (section 10) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3 -DDEG_CAP=@@CAP@@` and run as `single <seed> 1`; the calibrations as `calib 3 4 5 6 7 8 9`, the gcd bounds as `gcdbound H`.
* The worst case of stage E is charged although it has not been observed: it needs a centre for which `g_c` has a very large number of roots that are squares. It is derived, not run end to end; the components were run at the sizes of the levels (`calib`, `gcdbound`) and the half-gcd was run against classical Euclid on planted gcds (`test_hgcd`); the cap bounds the root isolation to degrees at most @@CAP@@, so `test_split` (degrees up to 12000) is not part of the evidence of this entry.
* The cost claim assumes the model of section 4.2; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.
* What a referee can rerun (one core; the organizer did not run the program): (a) the collision certificates against the organizer's hash, seconds; (b) the ledger recomputation of section 6.1 and the closed form `12 d^2 + 5400 d + 2676` for `d = 9, 4`, seconds, by hand or in Python; (c) `gcc -O3 -DDEG_CAP=@@CAP@@` of the source of section 10 and `single <seed> 1` under `ulimit -s 64`, which reproduces the data-independent counts of section 6 and the peak of section 7, about 90 s per seed; (d) `calib 3 4 5 6 7 8 9`, which reproduces the shift and pow columns, seconds; (e) `gcdbound H`, which regenerates `gcd_bounds.h` (the table used only above degree 152; it is not used by the capped root isolation), and `test_hgcd`; (f) `certb_verify.py` with the witness data of section 8.6, @@VERIFY_SHORT@@ in pure Python, which the judge cannot do inside the review. The charges of stage E are derived bounds, not observations; (b) and (d) are the complete inputs of that stage and are cheap to rerun.

## 10. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters. Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: @@FILE_ORDER@@.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs. `gcd_bounds.h` is generated by `gcdbound H`. `certb_verify.py` is the referee verifier of section 8.7 (not part of the counted program; it reads the organizer constants file and the witness numbers of section 8.6). `test_hgcd.c`, `test_split.c`, `test_keep.c`, `calib.c` and `gcdbound.c` are the test, calibration and bound programs named above.

@@APPENDIX@@
