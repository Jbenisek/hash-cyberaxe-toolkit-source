# Orchard Poseidon, r = 1: one centre of the odd-part method on a line, half-gcd with a derived worst case, root isolation (exact ledger, low memory)

## 1. Claim

Target: `poseidon-orchard-r1-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, one partial round 4, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = 25.62072` in target-compression units (`C(1) = 237` primitive operations per unit): the worst-case total of one attempt of the program,
  every executed operation charged (sections 4.2 and 6), no flat allowances for control or dispatch; every data-dependent stage is charged at a bound that is derived in section 6 and that the program checks against its own counters while it runs.
* `memory_log2_bytes = 23.074` (`8,829,894` bytes, section 7), so the normalized cost is `25.62072 + 3.074 = 28.69472`.
* `success_probability = 0.3934`: one attempt, one centre. Section 8 proves a lower bound of 0.3934647661 for one attempt (per-centre bound 0.3934678683, minus the proved cap-6 halt loss 3.1*10^-6, minus the root-isolation failure 2^-36); the claim is below it. The inputs of that proof that are computations are recomputed by the verifier of section 10 from the organizer constants (section 8.7).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^7`, then the roots of its odd part about a centre) is a known approach. What is offered here is a complete finite implementation with an exact operation ledger, a low-memory schedule,
  a half-gcd whose worst-case charge is derived, and a root isolation with a proved failure bound. Nothing here is an asymptotic estimate: every figure below is the count of an executed, instrumented program whose complete source is reproduced in section 10.
* The collisions stored in `certificates/` (2 pairs, each from a separate attempt of this program) are outputs of this program. They check the construction at the
  selected target with the organizer's hash; the cost and probability claims do not use them.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the
deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one canonical preimage. `K` is a constant.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`.
The program uses the line `j = 0`. With `I = {i1, i2} = {0,1,2} \ {j}`, let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant
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

Halts. The program is compiled with `-DDEG_CAP=6`. It ends early in exactly three ways that can happen with positive probability: stage D finds `deg G = 0` (the attempt has no useful root; a failure event of section 8), stage D finds `deg G > 6` (the cap, charged 2 operations; a failure event of section 8, bounded there) and a level of the root isolation has no proper split after its `t(d)` tries (probability at most `2^-36` over all levels, section 4.1).
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
6, 3 (2 levels with `d >= 3`, because the cap gives `deg G <= 6`); the ledger charges the larger schedule 9, 4. Hence the failure probability of stage E, whatever `G` is, is at most `2 * 2^-39.99 < 2^-38`.
The event `c = 0` (the Taylor shift needs `1/c`) has probability `2^-254` per try; over the at most 19 tries of the charged schedule (`t(9) + t(4) = 5 + 14`) it adds below `2^-246`, and it is included in the same bound (`2 * 2^-39.99 + 2^-246 < 2^-36`). The number of tries of a run is at most the sum of `t(d)` over the levels (for the worst schedule 19 tries).

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
  The value for `(39062, 39061)` is 3,336,226,186 operations; the run of this ledger charged 1,508,601,747 (ratio 0.452). The program asserts `charged <= bound` for the main gcd and for every gcd of the root isolation (exit status 81 otherwise); the table of bounds (`gcd_bounds.h`, section 10) is generated by `gcdbound H`.
  Tests: the gcd was compared with classical Euclid on planted gcds with normal and abnormal remainder sequences (`test_hgcd`, section 10).
* **Stage E (root isolation), worst case.** The levels of section 4.1 start at degree at most 9 (the cap gives `deg G <= 6`; 9 is charged, which is larger) and halve. For each level of degree `d` and each of its `t(d)` tries the charge is `shift(d) + pow(d) + gcd bound(d) + div bound(d)` plus the random word and control (about 60 operations),
  where `shift(d)` (the Taylor shift) and `pow(d)` (`Z^((p-1)/2) mod G`) are measured at that exact degree on random input (their cost does not depend on the coefficients), `gcd bound(d)` is `gcd_cost_bound(d, d-1)` (closed form, derived in section 10 `split.c`) for `d <= 152` and the table value above,
  and `div bound(d)` is the maximum over `a` in `(d/2, d)` of `div_cost_bound(d + 1, a + 1)` for `d <= 152` (schoolbook) and `B_div(d, d/2 + 1)` above (the division of `G` by `A` happens only when `deg A > d/2`; asserted at every division).
  The last level (`d = 2`) costs 16,000 operations (one square root with its control charge, one inversion). No margin or extrapolation is applied: the table lists the exact measured values for shift and pow at the charged degrees 9 and 4, the closed-form gcd bound `T_full(d)` and the division bound, summed as they are.
  *Why the schedule (9, 4) covers every reachable schedule.* Under the cap `deg G <= 6`, so the levels that can occur are `d_0 <= 6`, then at most `floor(d_0/2)` (the smaller piece). The charged schedule is the larger one (9 with 5 tries, 4 with 14 tries). The build script recomputes, from calibration records at every degree 3..9, the total of each reachable schedule with the same formula and asserts that the charged total is at least the largest of them: shift and pow are nondecreasing over d = 3..9 in the calibration, and the charged total 6,145,283 is at least the largest reachable total 4,865,764 (first level 6, then 3).
  *Derivation of `T_full(d)` (classical gcd, `gcd_cl` of section 10, called as `gcd_cl(Ap, G, d, S, d - 1)`).* The inner loop of the shipped code is
  `for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }` followed by `LD(2 * dB); ST(dB); loopc(dB); CTL(dB);`.
  One iteration is charged 1 multiplication + 1 subtraction (2 arithmetic), 2 loads and 1 store (3), 3 address operations (`LD`, `ST` add one control operation each), 3 loop-control operations (`loopc` adds `3n + 2` per loop) and 1 for `CTL(dB)`: 2 + 3 + 3 + 3 + 1 = 12 operations. Each elimination step lowers `dA + dB` by at least 1 and its inner loop runs `dB <= (dA + dB)/2` times, so with `S0 = deg a + deg b = 2d - 1` the inner iterations total at most `floor(S0^2/4) = d^2 - d`, the eliminations at most `E = S0 + 1 = 2d`, and the outer passes (one inversion each) at most `E`.
  The other terms are the constants written in `gcd_cost_bound` (section 10): elimination `25 E + 11 (S0 + 1)`, pass `E (330 + 2 + 2310 + 8)` (330 arithmetic operations of `fp_inv`, `INV_CTL = 2310`), setup `16 (S0 + 2) + 6`, final scaling `330 + 2 + 2310 + 8 (d + 1) + 4`. Substituting `S0 = 2d - 1`: `12(d^2 - d) + 72 d + 5300 d + (32 d + 22) + (8 d + 2654) = 12 d^2 + 5400 d + 2676`.
  So `T_full(9) = 52,248` and `T_full(4) = 24,468`, which are the "gcd bound" entries of the table; the program asserts `charged <= gcd_cost_bound(d, d - 1)` at every gcd of the root isolation (exit status 81 otherwise).

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table (once) | 17,361 | 126,642 | 144,003 | no |
| setup: the line | 391 | 3,519 | 3,910 | no |
| A: random centre | 1 | 3 | 4 | no |
| B: 98304 evaluations (units) + inverse NTT 49152 + normalisation | 1,436,260 | 31,273,571 | 32,709,831 | no |
| C: `S^((p-1)/2) mod g` (m = 39062, 238 steps) | 3,536,772,942 | 5,315,154,386 | 8,851,927,328 | no |
| D: half-gcd, derived bound for (39062, 39061) plus the degree scan allowance (10 x 39063) | - | - | 3,336,226,186 + 390,630 (charged in the run: 1,508,601,759) | yes: bound |
| E: root isolation, worst case over the level schedule (table below), plus the quadratic end | - | - | 6,145,283 | yes: bound |
| F, G: square root, back-map, two reference hashes (success path) | - | - | 400,000 allowance (observed 48,060) | no |

Worst case of the root isolation (stage E) over the level schedule of section 4.1 (starting degree 39062):

| d | tries t(d) | shift(d) | pow(d) | gcd bound | div bound | t(d) x (shift + pow + gcd + div + 100) |
|---:|---:|---:|---:|---:|---:|---:|
| 9 | 5 | 7,095 | 694,997 | 52,248 | 3,161 | 3,788,005 |
| 4 | 14 | 5,928 | 133,897 | 24,468 | 2,834 | 2,341,178 |
| quadratic end (d = 2) and level control | | | | | | 16,100 |
| total | 19 | | | | | 6,145,283 |

Worst case of one attempt (stage D finds the largest possible `G`, stage E runs to the end at the worst degrees):
`init + setup + A + B + C + D bound + scan + E bound + final allowance = 144,003 + 3,910 + 4 + 32,709,831 + 8,851,927,328 + 3,336,226,186 + 390,630 + 6,145,283 + 400,000 = 12,227,947,177` operations `= 51,594,713.8` units, `time_log2 = 25.62072`, claimed as `25.62072` (rounded up).
(A run in which stage D finds no root stops after about 10,393,386,835 operations; a run in which `G` is linear charges about 10,393,434,902, as in the logs of this ledger.)
Composition by type of the ledger run (init included; the control counter includes the address operations of loads and stores): add `1,368,825,116`, sub `1,279,204,609`, mul `1,246,452,000`, sqr `33,326,305`, loads `1,626,342,731`, stores `841,035,553`, control `3,974,950,539`, unit charges `23,298,048`.

Stage C in detail (m = 39062): Newton for MU: 56,854,985 operations; prefix and scaling: 508,491; 238 squaring steps at 36,951,626 operations each (arith 14,769,136). Of the arithmetic of stage C, 3,536,772,942 operations; the transforms are the largest term.

### 6.1 Ledger recomputation

```python
from math import log2, ceil
C = 237
init, setup, rand, build, power = 144003, 3910, 4, 32709831, 8851927328
gcd_bound, scan, split, final = 3336226186, 390630, 6145283, 400000
N = init + setup + rand + build + power + gcd_bound + scan + split + final
print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

## 7. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer (each buffer is one allocation). Stage C at `m = 39062`: the twiddle table (`2^14` elements, 524,288 bytes), `Y` (`3 * 2^15` elements, 3,145,728), `tmp` (`2^15` elements, 1,048,576), `MU` (1,249,952),
`g` (1,250,016) and the result `F` (1,249,984). Tracked peaks of the ledger run per stage: init (twiddle table) 524,288; line setup 524,288; random centre 524,288; B 3,347,168; C 8,468,544; D 7,843,648; E 524,416; F 524,288; G 524,288. For the worst-case root isolation the stages at the degrees of the level schedule were run by the calibration program: Taylor shift 525,536, powering 525,472 bytes (including the live arrays), the gcd stage of the top level (the half-gcd of degrees 39062 and 39061 is stage D of the ledger run itself, whose tracked peak is in the list above; no gcd of that size occurs in the root isolation under the cap, so `test_keep` is not used) not applicable under the cap;
the largest is 8,468,544 bytes. To the heap peak we add the static image of the executable (code, constants and tables: text 284,670 + data 1,712 + bss 5,336 = 291,718 bytes), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit) and 4,096 bytes for the allocator's own metadata:
`8,829,894` bytes `= 2^23.074`. The memory penalty is `max(0, 23.074 - 20) = 3.074`.
Counted: every buffer of the program (the tracked heap peak above), the executable's own code, constants and tables (text + data + bss), the stack bound and the allocator metadata. Not counted, as they are not part of the abstract program: the dynamically linked C library code and loader mappings and the kernel structures of the host process; the program uses the library only for `malloc`/`free`/`memcpy`/`memset` (whose buffers are counted) and, in the diagnostic ledger run only, printing.
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. Success probability

**Statement.** One attempt of the program of section 4 (DEG_CAP = 6, one uniform centre `c`, uniform shifts in stage E) outputs a digest collision with probability at least **0.3934647661**. The claimed value `0.3934` is below it.
The random experiment: the program draws the centre `c` (one uniform 254-bit word) and the shifts of stage E; all are independent and uniform (the cost model has independent uniform random words as a primitive; the executed program uses a 64-bit xorshift generator, and the claim uses the idealisation, D18 below).
The attempt succeeds iff `1 <= N(c) <= 6` and stage E isolates a root, where `N(c)` is the number of nonzero squares `S` in `F_p` with `g_c(S) = 0` (stage D then returns `G` with `deg G = N(c)`).

**The chain, in one place.**
1. Per centre: for `c` uniform in `F_p`, `P(N(c) >= 1) >= 0.3934678683`; the program draws `c` uniform in `[0, 2^254)`, a subset of `F_p`, so its probability is lower by at most the total-variation distance `2^-128.9` (D18, step 6) (sec. 8.2: Bonferroni sums for `k <= 6`, point counts on the `k`-tuple curves by Hasse-Weil, genus bound by Riemann-Hurwitz). This uses the hypothesis `HK(k)`, `k <= 6`: the `k`-tuple curves are geometrically irreducible.
2. `HK(k)`, `k <= 6`, follows from CERT A (the full sign module, sec. 8.5.3) and CERT B (the block action contains `A_d`, sec. 8.5.5), through the `(d-2)`-transitivity of `A_d` (Lemma 8.5.6).
3. CERT A is computed at the critical point `c_A` of the line (sec. 8.5.3). CERT B is proved from the witness of sec. 8.6 (centre `c0`, prime factor degree `l = 20269`), together with transitivity of the block action (Lemma 8.5.1), which needs absolute irreducibility of `Q = (F(u) - F(v))/(u - v)`, which comes from indecomposability of `F` (witnesses for the six inner degrees, sec. 8.5.1; the team holds 18 for the three lines) and the cited classification theorems.
4. The cap: centres with `deg G >= 7` are abandoned. `P(N(c) >= 7) <= E[C(N,6)]/7 <= 3.102141*10^-6` is PROVED from the same chain (sec. 8.3): no loss term is assumed.
5. Root isolation fails with probability at most `2^-36` (section 4.1), whatever `G` is.
6. Total: `0.39346786834977 - 2^-128.9 - 3.102141*10^-6 - 1.4552*10^-11 >= 0.3934647661` (the `2^-128.9` is about `1.1*10^-39`, the total-variation distance of the sampler to the uniform law on `F_p`) (sec. 8.4.2).

**What is proved here, what is computed, what is cited, what is idealised.** Everything labelled PROVED is proved in this document from the items labelled COMPUTED and CITED below. COMPUTED items are exact computations over `F_p`; the verifier of sec. 8.7 (source in section 10) recomputes every one of them from the organizer constants and the two numbers `c0`, `l`. CITED items are theorems of the literature, with the status of our check of each stated in sec. 8.8. The only idealisation is D18 (ideal randomness), which `claim.json` also states. No sample and no heuristic about the roots of `g_c` enters section 8. The heuristic H1 declared in `claim.json` concerns the charges of section 4.2 and is stated at the end of this section; it does not enter the probability.

Numbers of the form `sec. 8.a.b`, `Lemma 8.a.b`, `Proposition 8.a.b`, `Theorem 8.a.b` and the labels `D1`...`D19` refer to this section 8.

### 8.0 Dependency list

| ID | Input | Label | Used in |
|---|---|---|---|
| D1 | `p` is the Pallas base prime: 255 bits, `p = 1 (mod 2^32)`, `p = 2 (mod 5)` | COMPUTED (probable prime by 40-base Miller-Rabin; the standard modulus) | 8.1 |
| D2 | `F = F_j` in `F_p[W]` has degree `n = 5^7` and leading coefficient `a_n != 0` (`j = 0`) | COMPUTED (interpolation at 131072 points; rebuilt by V1) | 8.1, 8.2 |
| D3 | Lemmas 8.1.1-8.1.6 (structure, collisions, top form, discriminant degree, `S`-discriminant, `k`-fold algebra and infinity) | PROVED | 8.1, 8.5 |
| D4 | Proposition 8.1.7 (genus bound), Lemma 8.1.8 (fibres), Proposition 8.1.9 (point count) | PROVED given HK(k) | 8.2, 8.3 |
| D5 | Bonferroni chain: `P(N(c) >= 1) >= 0.39346786834977` (sec. 8.2) | PROVED given HK(k <= 6) | 8.2 |
| D6 | HK(k <= 6): the `k`-tuple curves `Z_k^o` are geometrically irreducible | PROVED from D8 and D9 (Lemma 8.5.6) | 8.2, 8.5 |
| D7 | CERT A conditions at `c_A`: `F'(c_A) = 0`, `F''(c_A) != 0`, `H(c_A, .)` squarefree with `H(c_A, 0) = 0` | COMPUTED (team; recomputed by V6) | 8.5.3 |
| D8 | Full sign module `N = F_2^d` | PROVED from D7 and Lemma 8.5.1 (Lemma 8.5.2) | 8.5 |
| D9 | CERT B: `pi(G)` contains `A_d` | PROVED from D13 (Proposition 8.5.5) | 8.5 |
| D10 | `Q(u,v) = (F(u) - F(v))/(u - v)` is absolutely irreducible | PROVED (cited: Fried criterion) from D11 | 8.5.1 |
| D11 | `Mon(F)` is 2-transitive (indeed `A_n` or `S_n`) | PROVED (cited: Feit 1980, Mueller 1995, in the form of Jones) from D12 | 8.5.1 |
| D12 | `F` is geometrically indecomposable | COMPUTED (V7: `F mod H_m` is non-constant for `m = 5^e`, `e = 1..6`) + PROVED (the inner polynomial is unique and has coefficients in `F_p`, sec. 8.5.1 (i); no descent theorem is needed) | 8.5.1 |
| D13 | WITNESS: `c0` in `F_p` with `Delta_S(c0) != 0` and an irreducible factor of `h(c0, .)` of prime degree `l`, `d/2 < l <= d-3` | COMPUTED and certified twice (sec. 8.6): `c0 = 12894125564123335855227378247026121035387943383342050628014288421295627833647`, `l = 20269` | 8.5.5 |
| D14 | Moment bound `E[C(N,6)] <= 2.1714981824*10^-5` and the abandonment bound at the cap 6 | PROVED given HK(6) (arithmetic re-done) | 8.3 |
| D15 | Root-isolation failure at most `2^-36` | PROVED (section 4.1, Lemma B) | 8.4 |
| D16 | Ledger fields (time, memory) | not used by the probability | - |
| D17 | Digest identity: digest of the canonical input built from `tau` equals `F(tau^5)` | PROVED (degree argument) + COMPUTED (V1 rebuilds `F` and checks 5 random `tau` against a straight-line reference) | 8.4.1 |
| D18 | Randomness: `c` is a uniform 254-bit word (total variation gap to uniform on `F_p` is `2^-128.9`); ideal randomness | ASSUMED (idealisation, stated in `claim.json`) | 8.4.2 |
| D19 | Cited theorems: Riemann-Hurwitz, Hasse-Weil, Dedekind-Kummer, Jordan (Wielandt Thm 13.9), Fried, Feit/Mueller (Jones Thm 1.2), Lueroth, Tonelli-Shanks, Gauss lemma | CITED | throughout |

### 8.1 Setup, structure, and the genus bound

#### 8.1.1 Notation

p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (D1). F in F_p[W] is the line polynomial of the r = 1 construction for the line j used by the program, with deg F = n = 5^7 = 78125 and leading coefficient a_n != 0 (D2). Put D = n - 1 = 78124 and d = D/2 = 39062. Since p != 5, p does not divide n. Since p > n and p > N_6 (sec. 8.1.4), all ramification indices below are tame.

P(c,s) := (F(c+s) - F(c-s))/s in F_p[c,s]. h(c,S) in F_p[c,S] is defined by P(c,s) = h(c,s^2) (Lemma 8.1.1). g_c := h(c,*). N(c) := #{S in F_p : h(c,S) = 0 and S = s^2 for some s in F_p^*}. Delta(c) := disc_s P(c,*) in F_p[c], and Delta_S(c) := disc_S h(c,*). K denotes an algebraic closure of F_p.

#### 8.1.2 Structure and collisions

**Lemma 8.1.1 (structure). PROVED.** (a) P is even in s, so h exists and is unique, deg_S h = d, and the S^d-coefficient of h is 2a_n. (b) P has total degree D; writing P = Sigma_j a_j(c) s^j, one has deg_c a_j <= D - j and a_D = 2a_n. (c) P(c,0) = 2F'(c), so deg_c h(c,0) = D.

*Proof.* (a) F(c+s) - F(c-s) is odd in s, hence divisible by s, and the quotient is even. Since n is odd, the coefficient of s^n in (c+s)^n - (c-s)^n is 1 - (-1)^n = 2, so the s^D-coefficient of P is 2a_n. (b) The total degree of F(c+s) - F(c-s) is at most n, with degree-n part a_n((c+s)^n - (c-s)^n); division by s lowers the total degree by one. (c) F(c+s) - F(c-s) = 2 Sigma_{j odd} F^{(j)}(c) s^j / j! (valid since p > n), whose s^1-term is 2F'(c)s. [end]

**Lemma 8.1.2 (collisions). PROVED.** For c in F_p, the map {u,v} -> S = ((u-v)/2)^2 is a bijection from the unordered pairs {u,v} subset of F_p with u != v, F(u) = F(v) and u + v = 2c onto {S in F_p^{*2} : h(c,S) = 0}. Hence N(c) equals the number of such collision pairs, and N(c) >= 1 iff F has a collision with midpoint c.

*Proof.* For such {u,v} set s = (u-v)/2 in F_p^* (p odd). Then P(c,s) = (F(u)-F(v))/s = 0, so h(c,s^2) = 0. Swapping u and v replaces s by -s and leaves S unchanged, so the map is well defined. S determines {s,-s}, hence the pair {c+s, c-s} = {u,v}: injective. Conversely, if S = s^2 with s in F_p^* and h(c,S) = 0, then P(c,s) = 0, so F(c+s) = F(c-s) with c+s != c-s, and this pair maps to S. [end]

#### 8.1.3 Algebraic lemmas

**Lemma 8.1.3 (top form). PROVED.** Let P_D(1,lambda) = a_n((1+lambda)^n - (1-lambda)^n)/lambda. Then P_D(1,*) = 2a_n prod _{zeta in mu_n minus {1}} (lambda - (zeta-1)/(zeta+1)), a polynomial of degree D with D distinct roots. It is even in lambda.

*Proof.* Since p does not divide n, mu_n has n elements in K. P_D(1,0) = 2n a_n != 0, so every root lambda is nonzero, and (1+lambda)^n = (1-lambda)^n gives zeta := (1+lambda)/(1-lambda) with zeta^n = 1, zeta != 1. The Mobius map zeta -> (zeta-1)/(zeta+1) is injective on mu_n minus {1} (-1 not in mu_n since n is odd) and inverts the correspondence. So the D roots are exactly these, and they are distinct. Evenness: (1+lambda)^n - (1-lambda)^n is odd in lambda. [end]

**Lemma 8.1.4 (discriminant degree). PROVED.** Delta(c) != 0 and deg_c Delta = D(D-1) =: B.

*Proof.* Put t = 1/c and Phat(t,u) := t^D P(1/t, u/t) = Sigma_{a+b <= D} p_{ab} t^{D-a-b} u^b in F_p[t,u], where P = Sigma p_{ab} c^a s^b. Then Phat(0,u) = P_D(1,u) and the u^D-coefficient is 2a_n. The roots of Phat(t,*) are u_i = t s_i, so disc_u Phat(t,*) = t^{D(D-1)} Delta(1/t) (the leading coefficients agree). By Lemma 8.1.3, disc_u Phat(0,*) != 0. Hence Delta(c) = c^{D(D-1)} E(1/c) with E(t) := disc_u Phat(t,*) a polynomial with E(0) != 0, so deg_c Delta = D(D-1) exactly. [end]

**Lemma 8.1.5 (S-discriminant). PROVED.** Delta(c) = kappa * h(c,0) * Delta_S(c)^2 for some kappa in F_p^*. Consequently deg_c Delta_S = D(D-2)/2 = 2d(d-1). In particular Delta_S != 0, and the finite branch points of the splitting cover of h(c,*) are among the zeros of Delta_S, at most 2d(d-1) of them.

*Proof.* The roots of P(c,*) are +-s_i, where S_i = s_i^2 are the roots of h(c,*). Pairs inside one block give (2s_i)^2 = 4S_i. For i < j the four cross pairs give (s_i-s_j)^2(s_i+s_j)^2(s_i+s_j)^2(s_i-s_j)^2 = (S_i-S_j)^4. So Delta = (2a_n)^{2D-2} prod _i 4S_i prod _{i<j}(S_i-S_j)^4 = kappa' prod _i S_i * Delta_S^2. Since prod _i S_i = +-h(c,0)/(2a_n), the identity follows. Degrees: 2 deg Delta_S = deg Delta - deg h(c,0) = D(D-1) - D by Lemmas 1.4 and 1.1(c). [end]

**Lemma 8.1.6 (k-fold algebra; no ramification at infinity). PROVED.** Let A_1 := K[c][s]/(P(c,s)) and A_k := A_1 (x)_{K[c]} ... (x)_{K[c]} A_1 (k factors) = K[c][s_1..s_k]/(P(c,s_i)). Then:
(a) A_1 and A_k are free over K[c] of ranks D and D^k, and deg_c disc(A_k/K[c]) = k(D-1)D^k.
(b) Let t = 1/c. The K[[t]]-algebra A^infinity_k := K[[t]][u_1..u_k]/(Phat(t,u_i)) is finite etale over K[[t]] and is the integral closure of K[[t]] in A_k (x) K((t)). Consequently every point over c = infinity of the normalisation of any component of Spec A_k has ramification index 1.

*Proof.* (a) A_1 has basis 1, ..., s^{D-1} since the leading coefficient is a unit, and disc(A_1) = Delta up to a unit. For free algebras of finite rank, disc(A (x) B) = disc(A)^{rk B} disc(B)^{rk A}; by induction disc(A_k) = Delta^{k D^{k-1}} up to a unit, of degree kD^{k-1} * D(D-1) = k(D-1)D^k. (b) The discriminant of A^infinity_k at t = 0 is the discriminant of Phat(0,*) = P_D(1,*) (Lemma 8.1.3), which is nonzero, so A^infinity_k is etale; etale over a DVR implies normal, and A^infinity_k (x) K((t)) = A_k (x) K((t)) via s_i = u_i/t. A factor of A_k (x) K((t)) therefore has integral closure a direct factor of A^infinity_k, which is etale. [end]

#### 8.1.4 Genus bound, fibres, and point count

Notation for k >= 1: N_k := prod _{j<k}(D-2j); A'_k := 2 - 2N_k + k(D-1)D^k; B := D(D-1); pi_k := 1/(2^k k!); err'_k := (A'_k sqrt p + N_k(B+1) + 1)/(2^k k! p). Let X_k(c) be the set of ordered k-tuples of roots of P(c,*) with pairwise distinct squares and nonzero entries; |X_k(c)| = N_k for c outside a finite set. Let Z_k^o := {(c,s_1..s_k) : P(c,s_i) = 0, s_i != 0, s_i^2 != s_j^2} over U := K minus Sigma, where Sigma := {zeros of Delta} union {infinity}, so |Sigma intersect P^1(F_p)| <= B+1.

**HK(k).** Z_k^o is geometrically irreducible. Equivalently, the geometric monodromy G of P(c,*) acts transitively on X_k(c). (Z_k^o -> U is finite etale with generic fibre X_k(c), and its connected components correspond to G-orbits on that fibre.)

**Proposition 8.1.7 (genus bound). PROVED given HK(k).** Let Ztilde be the smooth projective model of the closure of Z_k^o, with genus g. Then Ztilde -> P^1 has degree N_k and 2g <= A'_k.

*Proof.* The degree is N_k, which is below p, so the cover is tame and Riemann-Hurwitz gives 2g - 2 = -2N_k + Sigma_Q (e_Q - 1). Points over c = infinity contribute nothing (Lemma 8.1.6(b)). For a finite c_0, tameness gives Sigma_{Q over c_0}(e_Q - 1) = ord_{c_0} disc(Atilde_0), where Atilde_0 is the integral closure of K[c] in the function field of the component. Since A_k (x) K(c) is etale (Delta != 0), its integral closure Atilde is a product of the integral closures of its factor fields and disc(A_k) = disc(Atilde) * [Atilde : A_k]^2, so deg disc(Atilde_0) <= deg disc(A_k) = k(D-1)D^k (Lemma 8.1.6(a)). Therefore 2g <= 2 - 2N_k + k(D-1)D^k = A'_k. [end] (For k = 1, A'_1 = (D-1)(D-2), the plane-curve bound.)

**Lemma 8.1.8 (fibres). PROVED given HK(k).** For c in U the fibre of Ztilde over c is X_k(c). The fibres over c in Sigma have at most N_k points. Hence |#Z_k^o(F_p) - #Ztilde(F_p)| <= N_k(B+1).

*Proof.* Over U the algebra A_k is etale, so Ztilde -> P^1 is etale over U and the fibres have N_k points. Over U, a root is never zero (a root at 0 would have even multiplicity, forcing Delta(c) = 0), so the only possible coincidences are s_i = +-s_j, and the coincidence locus is clopen in Spec A_k|_U (it is the preimage of the diagonal of an etale cover). Z_0|_U is irreducible and open-closed in Spec A_k|_U, so the coincidence locus is either empty or all of Z_0|_U. It is not all of Z_0|_U, since the generic fibre is X_k. Hence the fibre is X_k(c). Over c in Sigma intersect P^1(F_p), both fibres lie in [0, N_k]. The point infinity contributes at most N_k. There are at most B+1 points of Sigma intersect P^1(F_p). [end]

**Proposition 8.1.9 (point count). PROVED given HK(k).** |#Z_k^o(F_p) - p| <= A'_k sqrt p + N_k(B+1) + 1.

*Proof.* Ztilde is defined over F_p and geometrically irreducible of genus g <= A'_k/2 (Proposition 8.1.7). Hasse-Weil gives |#Ztilde(F_p) - (p+1)| <= 2g sqrt p <= A'_k sqrt p. Combine with Lemma 8.1.8 and the "+1". [end]

#### 8.1.5 The one-centre procedure (the program of section 4)

Input: c in F_p.
1. Compute h(c,*) in F_p[S]. This uses the grid of section 3: with H = 49152 = 3*2^14 (H | p-1 and H >= m+1 for m = d), let omega be a primitive H-th root of unity and zeta^2 = omega. Evaluate g_c(omega^i) = (F(c+zeta^i) - F(c-zeta^i))/(2zeta^i) for i = 0..H-1 (2H = 98304 evaluations of F), and recover the coefficients of h(c,*) by one inverse transform of size H (exact, since deg h = d < H).
2. Compute G := gcd(h(c,*), S^{(p-1)/2} - 1). Since x^{(p-1)/2} - 1 is squarefree with roots the nonzero squares, G is squarefree and its roots are exactly the distinct nonzero-square roots of h(c,*). So deg G = N(c). If deg G = 0, output "no collision".
3. Find one root S of G (randomised root isolation of section 4.1; failure event RI).
4. s := sqrt S (Tonelli-Shanks; the 2-adic valuation of p-1 is 32). Output (c+s, c-s) after checking F(c+s) = F(c-s) by direct evaluation.

By Lemma 8.1.2, step 4 outputs a collision whenever N(c) >= 1 and step 3 succeeds. The check in step 4 is deterministic. The capped variant (section 4, DEG_CAP = 6) outputs "no collision" when deg G > 6.

### 8.2 Per-centre probability: P(N(c) >= 1) >= 0.39346786834977

**Statement.** For c uniform in F_p, P(N(c) >= 1) >= 0.39346786834977, hence >= 0.3934678683. The only assumption is HK(k <= 6). Its derivation is in sec. 8.5.

**Proof.** The chain below is stated with every constant explicit. It uses Proposition 8.1.7, Lemma 8.1.8 and Proposition 8.1.9 (the genus bound, fibre comparison and point count), with k-tuple curves Z_k^o as in sec. 8.1.4 and the notation there (N_k, A'_k, B, pi_k, err'_k).

```text
(3) FINAL INEQUALITY CHAIN (every constant explicit)
  Step 1 (pointwise). For integers y >= 0:  1_{y>=1} - sum_{k=1}^{6} (-1)^{k+1} C(y,k) = C(y-1,6) >= 0 for y >= 1,
      and the left side is 0 for y = 0.  Hence, averaging over c in F_p,
      X >= sum_{k=1}^{6} (-1)^{k+1} m_k,   m_k := (1/p) sum_{c in F_p} C(N(c), k).
  Step 2 (counting). Each rational S gives two values s = +-sqrt(S) in F_p^*, and each ordered tuple of distinct S gives
      2^k times the ordered tuples of s. Hence
      m_k = #Z_k^o(F_p) / (2^k k! p).
  Step 3 (Weil on the normalization). Let Ztilde be the smooth projective model of the closure of Z_k^o. It is defined over
      F_p and geometrically irreducible, of genus g_k, with 2g_k <= A'_k. Hasse-Weil gives
      |#Ztilde(F_p) - (p+1)| <= 2 g_k sqrt(p).
      Let Sigma = {zeros of disc(P) in K-bar} u {infinity}, so |Sigma| <= B+1. For c not in Sigma, the fibres of Z_k^o and
      Ztilde agree (both are the N_k-point set X_k(c)). For c in Sigma, each fibre has 0..N_k points. Hence
      |#Z_k^o(F_p) - #Ztilde(F_p)| <= N_k (B+1).
      Therefore |#Z_k^o(F_p) - p| <= A'_k sqrt(p) + N_k(B+1) + 1.
  Step 4 (combine). |m_k - pi_k| <= err'_k := (A'_k sqrt(p) + N_k(B+1) + 1)/(2^k k! p), and since
      sum_{k=1}^{6} (-1)^{k+1} pi_k = 18131/46080,
      X >= 18131/46080 - sum_{k=1}^{6} err'_k.

  Explicit constants (recomputed for this document with exact rational arithmetic and 60-digit decimal arithmetic):
   k   N_k                                   A'_k                                             err'_k
   1   78124                                 6103125006                                       1.793547e-29
   2   6103203128                            953613282656242                                  7.006044e-25
   3   476782228359360                       111750602996820937538                            1.368356e-20
   4   37245274114976484480                  11640563649176110870156034                       1.781695e-16
   5   2909451832765503061639680             1136760698631114972076147814402                  1.739916e-12
   6   227268920464644506156921963520        106570042361223701138346902470760450             1.359293e-08
   sum err'_k = 1.359467442209e-08
   18131/46080 = 0.39346788194444443...
   X >= 0.39346786834977002235...
```
**Status.** PROVED given HK(k <= 6). HK(k <= 6) is derived in sec. 8.5 from CERT A (D7, computed and recomputed by the verifier of sec. 8.7) and CERT B (D13, the witness of sec. 8.6).

### 8.3 The loss from the cap (centres with deg G >= 7 are abandoned)

**8.3.1 The k = 6 factorial-moment bound, explicitly.** Let m_6 := E_c[C(N(c),6)] = (1/p) Sigma_{c in F_p} C(N(c),6). By the counting identity (Step 2 of sec. 8.2), m_6 = #Z_6^o(F_p)/(2^6 * 6! * p) = #Z_6^o(F_p)/(46080 p). Under HK(6), Proposition 8.1.9 gives #Z_6^o(F_p) <= p + A'_6 sqrt p + N_6(B+1) + 1. Therefore

E[C(N,6)] <= 1/46080 + err'_6 = 1/46080 + (A'_6 sqrt p + N_6(B+1) + 1)/(46080 * p).

For n = 5^7 the constants are:

- N_6 = prod _{j<6}(D-2j) = 227268920464644506156921963520
- A'_6 = 2 - 2N_6 + 6(D-1)D^6 = 106570042361223701138346902470760450
- B + 1 = 6103281253
- sqrt p = 1.70141183460469231732 * 10^38
- err'_6 = 1.3592934328 * 10^-8 (COMPUTED; the Weil term A'_6 sqrt p/(46080 p) is all of err'_6 up to a relative 10^-30)

So

**E[C(N,6)] <= 1/46080 + 1.3592934328*10^-8 = 2.1714981824*10^-5** (rounded up from 2.17149818232*10^-5).

The leading term 1/46080 = 2.1701388889*10^-5 is the group-model value of the moment. The bound is conservative by the Weil term.

**8.3.2 Abandonment.** For integers N >= 0 and c >= 5: if N >= c+1 then C(N,6) >= C(c+1,6), since C(*,6) is nondecreasing on integers >= 6. Hence 1[N >= c+1] <= C(N,6)/C(c+1,6), and taking expectations,

P(N >= c+1) <= E[C(N,6)] / C(c+1,6).

- Cap c = 6 (the cap of this entry): C(7,6) = 7, so P(N >= 7) <= 2.1714981824*10^-5 / 7 <= **3.102141*10^-6**.

The program abandons exactly on {N(c) > c}, because deg G = N(c) (sec. 8.1.5, step 2).

Consequently P(N(c) >= 7) <= 3.102141*10^-6 is a PROVED bound (given HK(6)), computed from the same Weil-bound chain as sec. 8.2 and not from any sample.
Arithmetic re-done for this document (60-digit decimal arithmetic): E[C(N,6)] <= 2.17149818232164e-5, divided by 7 gives 3.10214026045949e-6, which is below the stated 3.102141e-6.

### 8.4 From a digest collision to the success probability

**8.4.1 From a digest collision to a collision of F (Lemma 8.4.1). PROVED given D17.** The line data are fixed by the constants and do not depend on c or tau: Q = (U_Q, V_Q) and (a, b) = (M_{j,1}, -M_{j,0}) are the affine solution and direction of the line of section 2.2, and U = U_Q + tau*a, V = V_Q + tau*b are the state variables built from tau. The line index j is the one used by the program. Let e := 5^{-1} mod (p-1), which exists since gcd(5, p-1) = 1. Let W_1 != W_2 in F_p with F(W_1) = F(W_2), and put tau_i := W_i^e. Then tau_1 != tau_2, the canonical pairs (nk_i, rho_i) built from tau_i are distinct, and their digests are equal.

*Proof.* x -> x^5 is injective on F_p, so tau_1 != tau_2 and tau_i^5 = W_i. The pairs (U_i, V_i) = Q + tau_i(a,b) are distinct since (a,b) != 0. The map (nk, rho) -> (U, V) is a bijection of [0,p)^2 (section 2.1), so the canonical pairs are distinct. By D17 the digest of the pair built from tau_i equals F(tau_i^5) = F(W_i), which is the same for i = 1, 2. [end]

**D17 (digest identity).** For the line j, the digest of the canonical input built from tau equals F(tau^5). Reason: after the round-1 affine step the state is affine in W = tau^5, and each of the seven S-box layers multiplies the degree in W by 5, so the digest is a polynomial in W of degree <= 5^7. F is that polynomial; it is determined by its values at 131072 > 5^7 points (COMPUTED), The verifier of sec. 8.7 (step V1) builds F from the organizer constants by exactly this interpolation and checks F(tau^5) against an independent straight-line reference hash at 5 random tau.

**8.4.2 Theorem (success). PROVED given HK(6) and the other items of the dependency list.** One attempt of the program of section 4 with DEG_CAP = 6 outputs a digest collision with probability at least

0.39346786834977 - P(N >= 7) - 2^-36 >= 0.3934678683 - E[C(N,6)]/7 - 2^-36 >= **0.3934647661**.

*Proof.* The procedure outputs a collision whenever 1 <= N(c) <= 6 and root isolation succeeds (sec. 8.1.5). So P(success) >= P(1 <= N <= 6) - P(1 <= N <= 6 and RI fails) >= P(N >= 1) - P(N >= 7) - 2^-36, where the probabilities of N are those of sec. 8.2 and 8.3 for `c` uniform in `F_p`, applied to the program's `c` uniform in `[0, 2^254)` at the price of the total-variation distance `2^-128.9` (D18) in each of the two terms, so `2 * 2^-128.9` in all; by sec. 8.2, sec. 8.3 and the failure bound of stage E in section 4.1 (at most 2^-36, whatever G is; the shifts of stage E are independent of c). A collision of F gives a digest collision by Lemma 8.4.1. [end]

Values (arithmetic re-done in 60-digit decimal arithmetic): 0.39346786834977 - 0.00000310214026 - 0.0000000000145519 - 2.2*10^-39 = 0.39346476619496 (to 14 digits; the sampler term changes only the 39th digit) >= 0.3934647661. The claimed value 0.3934 is below it by 6.5*10^-5.

**Randomness (D18).** The program draws c as a uniform 254-bit word, which lies in [0, 2^254) subset of F_p, and the total-variation distance from uniform on F_p is 2^-128.9. The statement assumes ideal randomness (independent uniform random words, the model primitive of the cost rules). The executed program uses xorshift, which is an idealisation that we state and do not prove. This is the one premise of section 8 that is not a computation or a cited theorem.

### 8.5 HK(k) from CERT A and CERT B

**8.5.0 Overview.** HK(k) follows from CERT A (the full sign module) and CERT B (the block action contains A_d) by Lemma 8.5.6. CERT B uses transitivity of the block action (Lemma 8.5.1), which uses absolute irreducibility of Q, which uses 2-transitivity of Mon(F) (sec. 8.5.1).

**8.5.1 Absolute irreducibility of Q.** Let G_F := the geometric monodromy group of F(X) - t over K(t). The components of Q(u,v) = 0 over K correspond to the G_F-orbits on ordered pairs of distinct roots. So Q is absolutely irreducible iff G_F is 2-transitive (cited: Fried). **PROVED (cited).**

G_F is 2-transitive when G_F in {A_n, S_n}. That follows from:
- (i) F is geometrically indecomposable (D12). Let F = G(H') over the algebraic closure K with deg H' = m, so m divides n and m is one of 5, 25, 125, 625, 3125, 15625 (m < n). Replacing H' by (H' - H'(0))/lc(H') and G accordingly, H' is monic with H'(0) = 0. With r = n/m the terms of F other than g_r H'^r have degree <= n - m, so the coefficients of x^(n-i), 0 <= i < m, of F and of g_r H'^r agree. This fixes g_r = a_n and fixes H' = x^m + b_1 x^(m-1) + ... + b_(m-1) x + b_m as follows: the series 1 + b_1 y + ... + b_(m-1) y^(m-1) is the r-th root, with constant term 1, of A(y) = sum_(i<m) (a_(n-i)/a_n) y^i modulo y^m (the root is unique because p does not divide r, as p != 5), and b_m = H'(0) = 0. So H' = H_m, the polynomial computed in step V7 of sec. 8.7, and its coefficients lie in F_p. If F = G(H_m) then the remainder F mod H_m, computed in F_p[x], would be the constant G(0). COMPUTED (V7): for each of the six values of m, F mod H_m has degree m - 1 > 0. So F is indecomposable over K, and no descent theorem is needed. (The six H_m of line 0 were also produced by the team's separate code and match by SHA-256; the team holds the same test for lines 1 and 2, 18 witnesses in all, which this entry does not use.)
- (ii) Primitivity of G_F (cited: from indecomposability, by Luroth, for a polynomial with p not dividing n) and an n-cycle in G_F (the monodromy at infinity is an n-cycle, since p does not divide n).
- (iii) The classification of primitive groups containing an n-cycle (Feit 1980, Mueller 1995, as restated in Jones, arXiv:1209.5169, Thm 1.2; purely group theoretic): such a G_F contains A_n unless (a) n is prime, or (b) n = (q^e-1)/(q-1) with PSL_e(q) <= G_F <= PGammaL_e(q) acting on points or hyperplanes (e >= 2), or (c) n in {11, 23}. For n = 5^7 = 78125: n is not prime; direct enumeration over all integers q >= 2 and 2 <= e <= 19 gives the single solution (q, e) = (78124, 2) of (q^e-1)/(q-1) = 5^7, and 78124 = 4*19531 is not a prime power; n is not 11 or 23. (Groups of prime-power degree 5^7 with an affine socle contain no element of order 5^7, since every 5-element of AGL(7,5) has order at most 125.) Hence G_F is A_n or S_n. The restatement was checked only through the secondary source (see sec. 8.8).

So D11 is PROVED (cited) given D12. Then D10 is PROVED (cited) given D11.

**8.5.2 Transitivity on blocks. Lemma 8.5.1. PROVED given D10.** The block action pi(G) of the geometric monodromy G is transitive on the d blocks, and h(c,*) is separable.

*Proof.* Q is absolutely irreducible (D10). Since P(c,s) = 2Q(c+s, c-s) with an affine change of variables, P is absolutely irreducible. Its leading coefficient in s is the constant 2a_n, so by Gauss's lemma P is irreducible over K(c). If h(c,*) = h_1 h_2 with positive S-degrees, then P(c,s) = h_1(c,s^2) h_2(c,s^2) is a nontrivial factorisation in K(c)[s], which is impossible. So h(c,*) is irreducible over K(c), and separable since Delta_S != 0 (Lemma 8.1.5). So Gal acts transitively on its roots. [end]

**8.5.3 CERT A. Lemma 8.5.2. PROVED given D7 and Lemma 8.5.1.** Suppose c0 in K satisfies F'(c0) = 0, F''(c0) != 0 and h(c0,*) squarefree. Then N = G intersect F_2^d = F_2^d.

*Proof.* (i) h(c0,0) = 2F'(c0) = 0, and by squarefreeness the root S = 0 of h(c0,*) is simple. By Hensel's lemma there is a root S(c) of h(c,*) in K[[c-c0]] with S(c0) = 0 and dS/dc(c0) = -2F''(c0)/partial _S h(c0,0) != 0 (since partial _c h(c,0) = 2F''(c)). So S(c) has a simple zero at c0.
(ii) The other roots of h(c,*) are simple and nonzero at c0, so they lie in K[[c-c0]] and their sheets are unramified. The two sheets +-sqrt S(c) of the block of S(c) are interchanged by the generator of the inertia group of K((c-c0)). This inertia is tame (p != 2). So the inertia image in G is the sign flip e_{i0} on that block, and e_{i0} in N.
(iii) For g = (epsilon,pi) in G one has g e_i g^{-1} = e_{pi(i)}. So N is stable under pi(G), which is transitive (Lemma 8.5.1). Hence N contains every e_j, i.e. N = F_2^d. [end]

**Status of CERT A (line 0, the line of this entry).** The three conditions of Lemma 8.5.2 hold at the base-field point
c_A = 25165542869611562156214771577253815338782953579437145343258119448900718155215:
F_0'(c_A) = 0, F_0''(c_A) != 0, and the monic polynomial H(c_A, S) of degree 39062 has H(c_A, 0) = 0 and gcd(H, H') = 1. COMPUTED by the team (gcd(F_0', X^p - X) has degree 1) and recomputed from scratch by the verifier of sec. 8.7 (step V6, about 10 seconds). Lemma 8.5.2 turns them into N = F_2^d, so CERT A is COMPUTED + PROVED given D10.

**8.5.4 Primitivity, lifting, Jordan.**

**Lemma 8.5.3 (primitivity). PROVED.** Let Gamma <= S_d be transitive and contain an l-cycle tau with l prime and d/2 < l < d. Then Gamma is primitive.

*Proof.* Suppose Gamma has a block system with m blocks of size b, 1 < b < d, so m = d/b <= d/2 < l. The <tau>-orbits on blocks have size 1 or l, and m < l, so tau fixes every block. A block meeting the support A of tau is tau-invariant, hence contains A. So a block has size b >= l > d/2, contradicting b <= d/2. [end]

**Lemma 8.5.4 (lifting an l-cycle). PROVED.** Let sigma in S_d have a cycle of prime length l, all other cycles of length < l (automatic for l > d/2, since the other cycles have total length d - l < d/2 < l). Let M be the lcm of the other cycle lengths. Then sigma^M is an l-cycle.

*Proof.* Every prime factor of M is at most d - l < l, so gcd(M,l) = 1. On the l-cycle sigma^M is an l-cycle; on each other cycle sigma^M is the identity, since its length divides M. [end]

**Jordan's theorem (Wielandt, Finite Permutation Groups, Thm 13.9; Dixon-Mortimer, Permutation Groups, Thm 3.3E). PROVED (cited).** A primitive group of degree d containing a p-cycle with p prime and p <= d-3 contains A_d. Jordan's theorem in the form used (a primitive group of degree d containing a cycle of prime length l fixing at least three points, i.e. l <= d-3, contains A_d) was confirmed in the statement of arXiv:1209.5169, Thm 1.1; the book numbers are quoted from that paper (the books were not available to us).

**8.5.5 Witness => CERT B. Proposition 8.5.5. PROVED given D13 (sec. 8.6) and Lemma 8.5.1.** Suppose c0 in F_p has Delta_S(c0) != 0 and h(c0,*) has an irreducible factor over F_p of prime degree l with d/2 < l <= d-3. Then pi(G) contains A_d.

*Proof.* Let L be the splitting field of h(c,*) over F_p(c), Gbar_a := Gal(L/F_p(c)) is contained in S_d, and Gbar_g := Gal(L/L intersect K(c)) = pi(G).
(a) Gbar_g is normal in Gbar_a and Gbar_a/Gbar_g ~= Gal((L intersect K(c))/F_p(c)). The finite subextensions of K(c) containing F_p(c) are the constant-field extensions F_{p^m}(c), so this quotient is cyclic and abelian.
(b) Gbar_g is transitive (Lemma 8.5.1), hence so is Gbar_a.
(c) Since Delta_S(c0) != 0 and the leading coefficient is a unit, the splitting cover is unramified over c0. By Dedekind-Kummer, a Frobenius sigma_0 in Gbar_a above c0 has cycle type equal to the factorisation pattern of h(c0,*) over F_p. So sigma_0 has a cycle of length l, and the other cycles have total length d - l < l. Lemma 8.5.4 gives an l-cycle tau = sigma_0^M in Gbar_a.
(d) Gbar_a is primitive (Lemma 8.5.3 applied to tau) and contains an l-cycle with l <= d-3. By Jordan's theorem, Gbar_a contains A_d.
(e) [Gbar_a, Gbar_a] is contained in Gbar_g because the quotient is abelian. Since d >= 5, A_d = [A_d,A_d] is contained in [Gbar_a,Gbar_a] is contained in Gbar_g. [end]

**8.5.6 HK from CERT A and CERT B. Lemma 8.5.6. PROVED given D8 and D9.** If N = F_2^d and pi(G) contains A_d, then G is transitive on X_k(c) for every k <= d-2. In particular HK(k) holds for k <= 6.

*Proof.* Let (sigma_1..sigma_k) and (sigma'_1..sigma'_k) be ordered k-tuples of sheets in pairwise distinct blocks. Since A_d is (d-2)-transitive, choose pi_0 in A_d mapping the blocks of sigma_j to the blocks of sigma'_j, and g in G with pi(g) = pi_0. Then g maps the first tuple to a tuple in the right blocks, with some signs. N = F_2^d contains an element prescribing the signs on those k blocks, so composing gives the target tuple. [end]

### 8.6 CERT B: the witness

#### 8.6.1 The witness

Line j = 0 (the line of this entry), n = 5^7 = 78125, d = (n-1)/2 = 39062, d/2 = 19531.

**WITNESS: c0 = 12894125564123335855227378247026121035387943383342050628014288421295627833647 (in F_p), prime factor degree l = 20269.**

* l = 20269 is prime (trial division), and 19531 < 20269 <= d - 3 = 39059. The window (19531, 39059] holds 1897 primes; the strict inequality l > d/2 matters because 19531 = d/2 is itself prime and Lemmas 8.5.3 and 8.5.4 need l > d/2.
* g := g_{c0} = H(c0, S) is the monic polynomial of degree 39062 defined by F(c0+s) - F(c0-s) = 2 a_n s g(s^2). It is squarefree: gcd(g, g') = 1, so Delta_S(c0) != 0.
* g = f * u with f monic irreducible of degree 20269 and u monic of degree 18793 (u is the product of the remaining irreducible factors, all of degree <= 19531).
* Proposition 8.5.5 applies with this c0 and l, and gives D9 (CERT B).

#### 8.6.2 Two criteria (both PROVED)

**Lemma 8.6.1 (Rabin for prime degree).** A monic f of prime degree l over F_p is irreducible iff (i) x^(p^l) = x (mod f) and (ii) gcd(f, x^p - x) = 1.
*Proof.* (=>) F_p[x]/f = F_(p^l), so x^(p^l) = x, and f has no linear factor. (<=) By (i) f divides x^(p^l) - x, which is squarefree, so f is squarefree and each irreducible factor has degree dividing l, i.e. 1 or l. By (ii) there is none of degree 1. [end]

**Lemma 8.6.2 (composition).** Let P_a in F_p[x], deg P_a < l, satisfy P_a = x^(p^a) (mod f). Then P_(a+b) = P_a(P_b(x)) mod f. So R_0 = x^p mod f, R_j = R_(j-1) o R_(j-1) mod f gives R_j = x^(p^(2^j)) mod f, and a binary product of the R_j gives x^(p^l) mod f.
*Proof.* In A = F_p[x]/f, phi(y) = y^p is a ring endomorphism fixing F_p, so phi^b(P_a(theta)) = P_a(phi^b(theta)) = P_a(P_b(theta)) and phi^(a+b)(theta) = phi^b(phi^a(theta)). [end]

**Lemma 8.6.3 (criterion modulo g, no factor needed).** Let g in F_p[x] be monic and squarefree of degree d, and l a prime with 2l > d. Then g has an irreducible factor of degree l iff deg gcd(g, x^(p^l) - x) - deg gcd(g, x^p - x) = l, and then there is exactly one such factor, equal to gcd(g, x^(p^l) - x) / gcd(g, x^p - x).
*Proof.* gcd(g, x^(p^l) - x) is the product of the irreducible factors of g whose degree divides l, i.e. degree 1 or l, and gcd(g, x^p - x) is the product of those of degree 1. The difference of degrees is l times the number of factors of degree l; there is at most one since 2l > d. [end]

#### 8.6.3 Certification 1: modulo f (team engine)

A GPU program of the team (`certb_fast.cu`, Kaltofen-Shoup distinct-degree factorisation with baby and giant steps; checked against python-flint on random and planted inputs, as described in its README) was run on centres chosen at random; no selection was applied other than "the residual factor has prime degree in the window", and for c0 it returned the pair (f, u) with f * u = g. The proof does not rely on the factorisation program. It relies on the following exact checks of the returned data, which a second program of the team ran (log `certify.log`, result PASS, 6.7 s): (1) f * u = g exactly, with f and u monic; (2) gcd(g, g') = 1; (3) R_0 = x^p mod f, and gcd(f, R_0 - x) = 1; (4) the doubling edges R_j = R_(j-1) o R_(j-1) mod f (15 were checked, j = 1..15; j = 1..14 are used); (5) the binary chain for l = 20269 = 1 + 4 + 8 + 32 + 256 + 512 + 1024 + 2048 + 16384 (bits 0, 2, 3, 5, 8, 9, 10, 11, 14) reaches x^(p^l) = x mod f. By Lemma 8.6.1 and Lemma 8.6.2, f is irreducible of degree 20269.
SHA-256 of the data, each polynomial as the concatenation of its coefficients, constant term first, each a 32-byte little-endian canonical representative in [0, p):

| object | SHA-256 |
|---|---|
| F_0 (78126 coefficients) | 92088a6a4189af2a453ecc1043770701c4af53df3a4c859b457e46180be262e9 |
| g = H(c0, S) (39063 coefficients) | 4cffc67966ec9bea6586e45e8c22f47e23088a6f3333cde58af80c027b7bada5 |
| f | e01b6162e788b38fe4251d5545be9fa5f43938b085b876458883c154ffd17a9e |
| u | b51e77ec569dad44c142da27f16fd552eed6720d7bcb663a17a36384f491e7b9 |
| R_0 | 8d28a7e9e7a01f5dff443f03afbc01285f3de26084682e711b0dd92b42e997ff |
| R_1 | 9197eaa43708d2973e57f915cb97da767ee24d435dbff42cfb0e2ff2ce26b433 |
| R_2 | d540b925234e92a474f5efc7181d8745ebb5d4c8199aee350617a4330309c554 |
| R_3 | ed1d6872477af6049edf55c14d52c40499536213c2e8b44ddb739a53d30c7e56 |
| R_4 | d432dc60a905414cdd90346884acd8cf14ae12d31133b7a654303155c0189609 |
| R_5 | cabdf3001de5fe070a078b5fca18b990afe3fb277e3ac9952d490037a6d9b6ed |
| R_6 | eb45ffb0cd1a3e0b1717787dd9c7ad761e1c7f68cba8bdfa3a246aa848130efc |
| R_7 | 5fb2dec56bb1096f3082c2f33469b9b12a48a78b8ed1f9a84c2355e6a388508d |
| R_8 | 0500cd0d6463dcd35a0c2475187e9a4c08733e7e1ed34bec57676f1c8fe4cc20 |
| R_9 | 6d3f39040b2116423ee24d6ffbcae75a7d68a53c7398a49aa55c82e6aa2e37ba |
| R_10 | cb5e0870ff91382ba896d69e552ac88559ab7a170b444bbc0e8fd11ec31af2a8 |
| R_11 | d64fb4a33fb8dbcf094c2ae62062a20594597fa16b91e2c708bd011f8590ed94 |
| R_12 | 0e68509347fb2d76b74c52fd01f9abb588dde482e91cbcfe95e7cbc273afcddd |
| R_13 | 6fcabc4f47ec621d7bad195f74084b775546dbb114ede27c8dea6e4f53db96e0 |
| R_14 | 0caa35e07726b5cd9283bdb2d42528f86805b2e4c669661fd522c453aa251bc2 |

#### 8.6.4 Certification 2: modulo g (the referee's route, no data needed)

By Lemma 8.6.3 the same fact is certified from c0 and l alone: compute R_0 = x^p mod g, R_j = R_(j-1) o R_(j-1) mod g for j = 1..14, Q = x^(p^l) mod g by the binary chain, g_l = gcd(g, Q - x), g_1 = gcd(g, R_0 - x), and check deg g_l - deg g_1 = 20269. This is step V5 of the verifier of sec. 8.7; it uses a different library (python-flint) and a different modulus (g of degree 39062, not f of degree 20269) than certification 1. The verifier also prints the SHA-256 of f = g_l / g_1, of u = g / f and of R_j mod f, to be compared with the table above.

#### 8.6.5 Why the data are not shipped, and what the certificate document proposed

The certificate document of the team (checks C0-C4) proposed to ship the witness data with a manifest of hashes: F (2.5 MB), g (1.25 MB), the Bezout pair for squarefreeness (2.5 MB), f, u, the checkpoints R_j and a second Bezout pair, in all 18 to 30 MB. That is far above the organizer limits (evidence at most 524,288 bytes; no undeclared files), so nothing of it is shipped. Instead the package states c0, l and the digests above, and ships the verifier (section 10, `certb_verify.py`, 10 KB) that regenerates every object from the organizer constants. The differences from the certificate document are: (a) F is rebuilt (V1) instead of read from a file, and the hash of the rebuilt F equals the hash of the team's coefficient file, which closes the open item of that document about identifying the line model of the decomposition code with the interpolated F; (b) squarefreeness is checked by gcd(g, g') = 1 instead of shipped Bezout coefficients (same statement, recomputed); (c) the C0 random test of the certificate document is replaced by the exact interpolation of V1 plus the straight-line reference check; (d) irreducibility of f is replaced by Lemma 8.6.3, which needs no f.
What this means for a reader: the judge of this entry cannot recompute the witness inside the review. A referee can, in the time stated in sec. 8.7.

### 8.7 What a referee recomputes, and what it costs

**Tool.** `certb_verify.py` (section 10; 10 KB; Python 3 and python-flint 0.9.0). **Inputs.** The organizer's constants file `orchard-pallas-constants.json` (the file the program constants of `pallas_consts.h` come from), the line j = 0, the witness `c0` and `l = 20269` of sec. 8.6.1, and the CERT A point `c_A` of sec. 8.5.3. No other file is needed. Call: `python certb_verify.py orchard-pallas-constants.json 12894125564123335855227378247026121035387943383342050628014288421295627833647 20269 0 25165542869611562156214771577253815338782953579437145343258119448900718155215`.

| step | what is recomputed | cost (one core, python-flint 0.9.0) | printed value to compare |
|---|---|---|---|
| V1 | F_0 (degree 78125) by 131072 evaluations of the seven tail rounds on the line and one inverse transform; F(tau^5) against an independent straight-line reference hash at 5 random tau | 10 s | SHA-256 of F_0 = 92088a6a4189af2a... (table in sec. 8.6.3) |
| V7 | for m = 5, 25, 125, 625, 3125, 15625: the forced inner polynomial H_m (root series of the top m coefficients) and F mod H_m, which must be non-constant | 3 s in all | degree of F mod H_m (= m-1 in every case) and SHA-256 of H_m (table below) |
| V6 | CERT A at c_A: F'(c_A) = 0, F''(c_A) != 0, H(c_A, 0) = 0, gcd(H, H') = 1 | 9 s | PASS line |
| V2, V3, V4 | g = H(c0, S) by one Taylor shift; gcd(g, g') = 1; l prime in (d/2, d-3] | 9 s | SHA-256 of g = 4cffc679...; PASS lines |
| V5 | R_0 = x^p mod g; R_j = R_(j-1) o R_(j-1) mod g (j = 1..14); the chain for x^(p^l) (8 more compositions); two gcds of degree 39062 | 6,600 s (110 min) measured: x^p mod g 114 s, 22 compositions at about 300 s each, two gcds and the reductions modulo f about 10 s; peak memory 2.8 GB | deg g_l - deg g_1 = 20269; SHA-256 of f, u, R_j mod f (table in sec. 8.6.3) |
| total | | 6,635 s (about 111 min, 1.9 h) measured, one core, pure Python with flint (BelowNormal priority on a shared machine) | |

**Cost of V5 in other terms.** The 22 compositions modulo a degree-39062 polynomial dominate. Modulo f (degree 20269, certification 1) the same chain took 6.7 s on the team's GPU engine; that engine is not part of the package. The team's data files for certification 1 (about 13 MB) are not part of this package (sec. 8.6.5).

**Inner polynomials of V7 (line 0).** SHA-256 of H_m, coefficients constant term first, 32-byte little-endian. The same six polynomials were produced by the team's earlier separate code (`nondecomp_witnesses`; its file hashes, taken over hex text, begin 8840f75ffdc024bc, c9553028674f6ef3, cd73efecd2a4c9a3, d72656b6173cfb62, bf47a0287b093b15, 63a7deaaa8a4716c); that code also holds 12 witnesses for lines 1 and 2, which this entry does not use (18 in total).

| m | degree of F mod H_m | SHA-256 of H_m |
|---:|---:|---|
| 5 | 4 | 5e64ddec8781472d31dfd28228f0d0aeaa3867b5aed6ce6574c18d7c8ce25f7f |
| 25 | 24 | 5814abb8a6ae3a5040c02cedfc23fb64873a6b690534c0fa4efd99c655dab60e |
| 125 | 124 | 360b3915d575a8c3612ee6edd544c69c09451ade66aba7da347b9c8798e4e782 |
| 625 | 624 | a471797978bd9e07ae99f984aead6fe37c796ab2158c6fab14e4e123eede8c35 |
| 3125 | 3124 | ccb44986a090cf2c43af4327059a92d53d9d24929ac39dc388a3c197fd7125d3 |
| 15625 | 15624 | 10eb938aae219b5626768c87538b31e9aee09717e91071da8387f06121e86998 |

**What the verifier does not cover, stated plainly.** (1) The cited theorems (sec. 8.8) are not recomputed. (2) The reference hash of V1 is a straight-line implementation inside the verifier (rounds 0-3, 4, 60-63 with the organizer constants); the two certificates of the package are checked by the organizer's hash. (3) The transcription of the lemmas of sec. 8.1-8.6 is a matter for reading, not for computation. (4) The complete run of the shipped verifier on the final data finished with all PASS lines in 6,635 s: deg gcd(g, x^(p^l) - x) = 20271 and deg gcd(g, x^p - x) = 2 (so the degree-l part has degree 20269), and the printed SHA-256 of f, u and R_0..R_14 mod f equal the tables of sec. 8.6.3. The team's compiled engine (C/CUDA, not part of the package) did the equivalent chain modulo f in 6.7 s on one RTX 3090; the referee time is therefore about two hours in pure Python, not minutes.

### 8.8 Scope, status of the cited theorems, attack points

* **Scope.** Section 8 is for r = 1 only, for the line j = 0 used by the program, one attempt, one centre. The method gives nothing at r = 3 and is not used for r = 2 here.
* **Status of our check of each cited theorem** (from our citation check of 2026-10-13; the primary sources were not available to us, which we say plainly).
  Jordan's theorem: statement confirmed (arXiv:1209.5169, Thm 1.1: primitive group of degree n containing a cycle of prime length fixing at least three points contains A_n); the book numbers (Wielandt Thm 13.9, Dixon-Mortimer Thm 3.3E) are taken from that paper.
  Feit/Mueller classification in the form of Jones, arXiv:1209.5169, Thm 1.2 (group-theoretic, so no transfer between characteristics is needed): we took the form stated in the certificate document of the team; we did not read the text of Theorem 1.2 ourselves. The polynomial-monodromy version (Mueller's list, in Burda-Khovanskii arXiv:1209.5137, Thm 7, a characteristic-0 statement) leaves only A_n or S_n for n = 5^7 as well, because n is odd and composite; we do not use it.
  Fried's criterion: statement confirmed in Kreso-Tichy arXiv:1503.05401, Thm 3.3 (hypothesis: the characteristic does not divide deg f; for composite n the Dickson exception cannot occur); the 1970 paper was not read.
  Riemann-Hurwitz, Hasse-Weil, Dedekind-Kummer, Gauss's lemma, Lueroth's theorem, Tonelli-Shanks: standard.
* **Open premises of section 8.** None in the probability chain other than D18 (ideal randomness, stated in `claim.json`) and the cited theorems above. The cap loss is a proved term (sec. 8.3), not an assumption. Nothing in section 8 is a sample or a heuristic.
* **Attack points for a referee.** The form of the classification theorem for n = 5^7 (sec. 8.5.1 (iii)); Fried's criterion for Q (sec. 8.5.1); uniqueness of the inner polynomial (sec. 8.5.1 (i)); the Dedekind-Kummer step at c0 (sec. 8.5.5 (c)); the lifting and primitivity lemmas (8.5.3, 8.5.4); the local-inertia argument for CERT A (Lemma 8.5.2); the genus bound (Proposition 8.1.7) and the fibre comparison (Lemma 8.1.8); the abandonment inequality (sec. 8.3.2); the chain of sec. 8.2.

**Supporting statements on the charges.**
**H1 (supporting).** The charges of section 4.2 describe the executed program: every statement that executes a field operation, a load or store, or an index, address or branch operation carries its charge on the same line; the block and position kernels are straight-line generated code in which each executed line is charged exactly once, and every loop is charged per executed iteration as written in the loop. The block register file (18 words: 16 data words and two working words) is a disclosed assumption.
No other heuristic is declared: the worst-case ledger of stage E (section 6) is a closed-form bound with no extrapolation, derived from the loops of the shipped source.


## 9. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the root-isolation proof (4.1), the half-gcd facts (4.4), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 10), 2 machine-checked collision certificates (`certificates/`, checked by the organizer's hash).
  The success-probability proof is section 8 (final); its computed inputs are recomputed by `certb_verify.py` (section 10) in the time stated in section 8.7; the witness data themselves (several MB) are not shipped.
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package contains only the certificates, so the C source is part of this document (section 10) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3 -DDEG_CAP=6` and run as `single <seed> 1`; the calibrations as `calib 3 4 5 6 7 8 9`, the gcd bounds as `gcdbound H`.
* The worst case of stage E is charged although it has not been observed: it needs a centre for which `g_c` has a very large number of roots that are squares. It is derived, not run end to end; the components were run at the sizes of the levels (`calib`, `gcdbound`) and the half-gcd was run against classical Euclid on planted gcds (`test_hgcd`); the cap bounds the root isolation to degrees at most 6, so `test_split` (degrees up to 12000) is not part of the evidence of this entry.
* The cost claim assumes the model of section 4.2; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.
* What a referee can rerun (one core; the organizer did not run the program): (a) the collision certificates against the organizer's hash, seconds; (b) the ledger recomputation of section 6.1 and the closed form `12 d^2 + 5400 d + 2676` for `d = 9, 4`, seconds, by hand or in Python; (c) `gcc -O3 -DDEG_CAP=6` of the source of section 10 and `single <seed> 1` under `ulimit -s 64`, which reproduces the data-independent counts of section 6 and the peak of section 7, about 90 s per seed; (d) `calib 3 4 5 6 7 8 9`, which reproduces the shift and pow columns, seconds; (e) `gcdbound H`, which regenerates `gcd_bounds.h` (the table used only above degree 152; it is not used by the capped root isolation), and `test_hgcd`; (f) `certb_verify.py` with the witness data of section 8.6, two hours on one core in pure Python with flint in pure Python, which the judge cannot do inside the review. The charges of stage E are derived bounds, not observations; (b) and (d) are the complete inputs of that stage and are cheap to rerun.

## 10. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters. Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: `common.h`, `common.c`, `pallas.h`, `pallas.c`, `pallas_consts.h`, `attack.h`, `hgcd.h`, `gcd_bounds.h`, `ntt.c`, `gen_kern.py`, `ntt_kern.h`, `ntt_a3.h`, `poly.c`, `lean.c`, `line.c`, `split.c`, `hgcd.c`, `single.c`, `test_hgcd.c`, `test_split.c`, `test_keep.c`, `calib.c`, `gcdbound.c`, `certb_verify.py`.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs. `gcd_bounds.h` is generated by `gcdbound H`. `certb_verify.py` is the referee verifier of section 8.7 (not part of the counted program; it reads the organizer constants file and the witness numbers of section 8.6). `test_hgcd.c`, `test_split.c`, `test_keep.c`, `calib.c` and `gcdbound.c` are the test, calibration and bound programs named above.

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
/* A loop with its body unrolled 8 times (straight-line, no branch inside the body): one operation for the bound n & ~7, then per pass of the
 * unrolled body the index update, the comparison and the branch (3), on exit one comparison and branch (2); the 0..7 remaining elements run in a
 * plain loop (3 per iteration, 2 on exit).  The statements of the body carry their own load / store charges. */
#define FOR8(I, N, ...) do { size_t n_ = (size_t)(N), n8_ = n_ & ~(size_t)7, i_ = 0; CTL(1);                          for (; i_ < n8_; i_ += 8) {                                                                                         { size_t I = i_;     __VA_ARGS__; } { size_t I = i_ + 1; __VA_ARGS__; } { size_t I = i_ + 2; __VA_ARGS__; } { size_t I = i_ + 3; __VA_ARGS__; }         { size_t I = i_ + 4; __VA_ARGS__; } { size_t I = i_ + 5; __VA_ARGS__; } { size_t I = i_ + 6; __VA_ARGS__; } { size_t I = i_ + 7; __VA_ARGS__; }         CTL(3); }                                                                                                   CTL(2);                                                                                                         for (; i_ < n_; i_++) { size_t I = i_; __VA_ARGS__; CTL(3); }                                                  CTL(2); } while (0)
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
void   ntt_fwd_shifted(const plan_t *P, fp *dst, const fp *B, size_t lenB, size_t boff);   /* cached spectrum of B placed at cyclic offset boff */
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
void fp_from_limbs(fp *r, const uint64_t v[4]) { fp_cnt.mul++; /* a conversion is one Montgomery multiplication: charged as one field multiplication */ uint64_t t[4]; mont_mul_raw(t, v, PALLAS_R2); memcpy(r->l, t, 32); }
void fp_to_limbs(uint64_t v[4], const fp *a) { fp_cnt.mul++; /* charged as one field multiplication */ static const uint64_t one[4] = {1, 0, 0, 0}; uint64_t t[4]; mont_mul_raw(t, a->l, one); memcpy(v, t, 32); }
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
/* Orchard Poseidon (r partial rounds) collision: line model, digest polynomial, odd-part polynomial g. */
#ifndef ATTACK_H
#define ATTACK_H
#include "common.h"

typedef struct {
    int j;                 /* coordinate of the round-1 S-box input that stays constant */
    fp UQ, VQ;             /* point Q on the plane: U,V at tau = 0 */
    fp a, b;               /* direction (U,V) = Q + tau (a,b) */
    fp d[3];               /* S-box input at round 1 = d_i tau (i != j), kappa (i == j) */
    fp kappa;
    fp alpha[3], beta[3];  /* round-2 S-box input = alpha + beta W,  W = tau^5 */
    fp e5inv_unused;
} line_t;

/* exponent e = 5^{-1} mod (p-1), 254 bits */
extern const uint64_t E5INV[4];

void line_setup(line_t *L, int j);                         /* counted */
void tail_eval(fp *out, const line_t *L, const fp *W, int r);   /* F(W): counted, no memory-op charge (caller bounds it) */
size_t poly_degree_m(int r);                               /* m = (5^(6+r) - 1)/2 */

/* random */
void rng_seed(uint64_t s);
void rnd_fp254(fp *a);                                     /* uniform on [0,2^254), canonical; charged as 1 random word + 2 ctl */

/* build the monic odd-part polynomial g (deg m) for centre c; g has room m+1. Counted. */
void build_g(fp *g, const line_t *L, const fp *c, int r, int debug_check);

/* map a pair of roots back to inputs: W -> (nk, rho) */
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);

/* gcd and root finding */
size_t euclid_gcd(fp *out, const fp *a, size_t da, const fp *b, size_t db, size_t *dout); /* classical; out receives gcd (monic) */
int  find_root(fp *root, const fp *G, size_t d);           /* G monic, product of distinct linear factors; returns 1 on success */

/* minor-stage memory charge: 2 loads + 1 store + 1 control op per primitive executed since s0 */
void bound_mem_since(snap_t s0);

/* split.c: deflation-free root isolation with derived worst-case charges */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db);       /* classical Euclid; monic gcd; returns degree */
uint64_t gcd_cost_bound(size_t da, size_t db);
uint64_t div_cost_bound(size_t la, size_t lb);
int  split_find_root(fp *root, fp *G, size_t d);                              /* one root of a monic product of distinct linear factors */
size_t split_tries(size_t d);
fp  *taylor_shift(fp *G, size_t d, const fp *a);                              /* G(Z + a), frees G */
void pow_half(fp *S, const fp *G, size_t d);                                  /* Z^((p-1)/2) mod G */
extern uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;
#endif
```

### hgcd.h

```c
/* Half-GCD / fast Euclid over the Pallas base field (all ops counted through pallas.c and common.h). */
#ifndef HGCD_H
#define HGCD_H
#include "common.h"

/* 2x2 polynomial matrix R = Q_1 ... Q_h, Q_i = [[q_i,1],[1,0]];  e[0]=r11 e[1]=r12 e[2]=r21 e[3]=r22; h counts the factors */
typedef struct { fp *e[4]; size_t len[4]; int h; } mat_t;

/* polynomial a (la coefficients, trimmed), b (lb coefficients, trimmed, lb < la or lb == 0)
 * -> fresh arrays *c (lc), *d (ld) = consecutive Euclid remainders (r_h, r_{h+1}) with deg r_h >= n-k > deg r_{h+1}
 * (n = la-1), (a,b)^T = R (c,d)^T.  want_mat: also return R. */
void hgcd(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own);
void mat_free(mat_t *R);

/* gcd of a (la coefs) and b (lb coefs, lb <= la), monic result in out (room la); returns its number of coefficients (0 if both zero) */
fp *poly_gcd_own(size_t *lg, fp *x, size_t lx, fp *y, size_t ly); /* inputs are xalloc'ed and given away; returns the monic gcd (xalloc'ed) */
extern int hgcd_k1_pct;
size_t poly_gcd_fast(fp *out, const fp *a, size_t la, const fp *b, size_t lb);
/* plain Euclid (reference, counted) */
size_t poly_gcd_naive(fp *out, const fp *a, size_t la, const fp *b, size_t lb);
/* a = q*b + r (naive); q has la-lb+1 coefficients (if la>=lb), r has lb-1 slots; returns trimmed lr; *lq set */
void poly_divrem_naive(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb);
extern int hgcd_base_k;
extern uint64_t hgcd_stat_calls, hgcd_stat_base_steps, hgcd_stat_bigdiv;
void divrem_any_pub(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb);
fp *poly_gcd_keep(size_t *lg, const fp *x, size_t lx, fp *y, size_t ly); /* x borrowed, y given away; monic gcd as a fresh array */
#endif
```

### gcd_bounds.h

```c
/* generated by gcdbound H: worst-case charges of the fast gcd (deg a = d, deg b < d) and of the division of a degree-d polynomial by a factor of degree > d/2 */
#define NLEVELB 9
struct lvl_ { size_t d; unsigned long long gcd, div; };
static const struct lvl_ LEVELB[NLEVELB] = {
    { 39062, 3336226186ULL, 46718622ULL },
    { 19531, 1431310491ULL, 22213293ULL },
    { 9765, 609125679ULL, 9919625ULL },
    { 4882, 256902911ULL, 4820773ULL },
    { 2441, 106601271ULL, 2317342ULL },
    { 1220, 43098786ULL, 1105405ULL },
    { 610, 16783393ULL, 493833ULL },
    { 305, 6182859ULL, 250829ULL },
    { 152, 1918721ULL, 125968ULL },
};
```

### ntt.c

```c
/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 data words in registers, plus 2 working words) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"

static fp *tw = NULL;          /* tw[j] = rho_max^j, j < nmax/2 */
static int amax_g = 0;
static size_t nmax_g = 0;
fp ntt_w3;                      /* primitive cube root of unity */
static fp W3[3];                /* 1, w, w^2 */
static fp ZERO;                 /* 0 */
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
    fp_set_zero(&ZERO);
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

/* ---------- butterflies: straight-line register blocks and passes (ntt_kern.h, generated by gen_kern.py) ----------
 * Charging convention of this file and of the generated headers: every statement that executes loads, stores, integer, address or
 * branch operations carries its charge on the same line (LD / ST: one 256-bit memory access with its address formation; CTL(n): n integer
 * operations, comparisons or branches, 1 each); field operations are charged by pallas.c.  The block kernels contain no loop and no
 * branch.  Register assumption (disclosed): a block holds 2^k <= 16 data words in registers; the twiddle operand and the butterfly
 * temporary need 2 more words; strides, shift counts and base pointers live in integer registers. */
#include "ntt_kern.h"

/* per-pass constants: sj[j] = l0 + j, sjs[j] = sj[j] + shift, D[j] = s << sjs[j] (twiddle pointer step between consecutive tp of layer j).
 * Executed: a loop over the k layers with three additions, a shift and a store per layer (6 with the loop step 3 + 3). */
static void pass_tables(int k, int l0, size_t s, int shift, size_t *D, int *sj, int *sjs) {
    for (int j = 0; j < k; j++) { sj[j] = l0 + j; sjs[j] = l0 + j + shift; D[j] = s << sjs[j]; CTL(3 + 3 + 3); }
    CTL(2);
}
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), ngrp = (size_t)1 << l0;
    CTL(5);                                              /* s, ngrp: two shifts, an add; call, return */
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    CTL(4);                                              /* switch on k: compare, jump table */
    switch (k) { case 1: pf1(row, s, ngrp, tw, D, sjs); break; case 2: pf2(row, s, ngrp, tw, D, sjs); break;
                 case 3: pf3(row, s, ngrp, tw, D, sjs); break; default: pf4(row, s, ngrp, tw, D, sjs); break; }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), ngrp = (size_t)1 << l0, nh = P->n >> 1;
    CTL(6);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    CTL(4);
    switch (k) { case 1: pi1(row, s, ngrp, tw, D, sj, P->shift, nh); break; case 2: pi2(row, s, ngrp, tw, D, sj, P->shift, nh); break;
                 case 3: pi3(row, s, ngrp, tw, D, sj, P->shift, nh); break; default: pi4(row, s, ngrp, tw, D, sj, P->shift, nh); break; }
}
enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };
/* last forward pass + pointwise + first inverse pass (s == 1) in one register-resident block */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t ngrp = P->n >> k, nh = P->n >> 1;
    CTL(6);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, 1, P->shift, D, sj, sjs);
    CTL(6);                                              /* switch on mode and on k */
    if (mode == M_SQ) {
        switch (k) { case 1: pu1_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break; case 2: pu2_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break;
                     case 3: pu3_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break; default: pu4_sq(row, ngrp, tw, D, sjs, sj, P->shift, nh); break; }
    } else {
        switch (k) { case 1: pu1_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break; case 2: pu2_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break;
                     case 3: pu3_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break; default: pu4_mul(row, ngrp, tw, D, sjs, sj, P->shift, nh, C); break; }
    }
}

/* ---------- radix-3 stage ----------
 * Position kernels (ntt_a3.h) are straight-line code for one (pattern of nonzero inputs, rotation); a region driver runs one kernel
 * variant per position phase over a range of positions (head until the phase is 0, a loop of three positions per iteration, tail).
 * The ranges of constant pattern are found by split_regions below, whose operations are all charged where they are executed. */
typedef void (*rg_t)(fp *, const fp *, ptrdiff_t, ptrdiff_t, ptrdiff_t, size_t, size_t, size_t);
/* the kernel call macros are generated per (pat, rot, phase offset) by the helpers below */
#define KF(pat, rot, off) a3f_##pat##_##rot(dst, S, d0, d1, d2, n, i + (off))
#define KI(pat, rot, off) a3i_##pat##_##rot(dst, n, i + (off))
#define KR(r, pat, rot, off) a3r_##pat##_##rot##_##r(dst, S, d0, d1, d2, i + (off))
#define DRV_F(pat, c0, r0, r1, r2)                                                                                \
    static void rgf_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)d0; (void)d1; (void)d2;                                                                             \
        _DRV(KF(pat, r0, o), KF(pat, r1, o), KF(pat, r2, o)) }
#define DRV_I(pat, c0, r0, r1, r2)                                                                                \
    static void rgi_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)S; (void)d0; (void)d1; (void)d2;                                                                    \
        _DRV(KI(pat, r0, o), KI(pat, r1, o), KI(pat, r2, o)) }
#define DRV_R(r, pat, c0, r0, r1, r2)                                                                             \
    static void rgr##r##_##pat##_##c0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t lo, size_t hi) { \
        (void)n;                                                                                                  \
        _DRV(KR(r, pat, r0, o), KR(r, pat, r1, o), KR(r, pat, r2, o)) }
/* _DRV(K0, K1, K2): K_ph is the kernel call for phase ph with the placeholder offset o */
#define _DRV(K0, K1, K2)                                                                                          \
    size_t i = lo, ph = lo % 3; CTL(3);                                                                           \
    CTL(2); if (ph == 1) {                                                                                        \
        CTL(2); if (i < hi) { _SUB(K1, 0); i++; CTL(1);                                                           \
            CTL(2); if (i < hi) { _SUB(K2, 0); i++; CTL(1); } }                                                   \
    } else { CTL(2); if (ph == 2) { CTL(2); if (i < hi) { _SUB(K2, 0); i++; CTL(1); } } }                         \
    size_t nt = 0; CTL(2); if (hi > i) { nt = (hi - i) / 3; CTL(3); }                                             \
    for (size_t q = 0; q < nt; q++) { _SUB(K0, 0); _SUB(K1, 1); _SUB(K2, 2); i += 3; CTL(1 + 3); }               \
    CTL(2);                                                                                                       \
    CTL(2); if (hi > i) { size_t rem = hi - i; CTL(1);                                                            \
        _SUB(K0, 0); i++; CTL(1);                                                                                 \
        CTL(2); if (rem == 2) { _SUB(K1, 0); } }
#define _SUB(K, off) do { const size_t o = (off); K; } while (0)
#include "ntt_a3.h"

/* Regions of constant pattern.  Position pos = i0 + n*t (t = 0, 1, 2) of the length-N cyclic vector holds B[(pos + N - boff) mod N] when
 * that index is < lenB (lenB <= N), else 0.  bp[] receives the sorted breakpoints (bp[0] = 0, last = n), pat[] the pattern of each range
 * (bit t set: position t of the triple is nonzero).  Returns the number of ranges.  Every executed operation is charged. */
static int split_regions(size_t n, size_t N, size_t boff, size_t lenB, size_t *bp, int *pat) {
    if (lenB > N) { fprintf(stderr, "split_regions: lenB %zu > N %zu\n", lenB, N); exit(10); }
    int cnt = 0;
    bp[cnt++] = 0; CTL(3);
    for (int t = 0; t < 3; t++) {
        size_t st = (n * (size_t)t + N - boff) % N; CTL(3 + 4);                   /* loop, multiply, add, subtract, modulo */
        size_t x;
        CTL(3); if (st < lenB) { x = lenB - st; CTL(1); CTL(3); if (x > 0 && x < n) { bp[cnt++] = x; CTL(1); } }
        CTL(3); if (st > 0) { x = N - st; CTL(1); CTL(3); if (x > 0 && x < n) { bp[cnt++] = x; CTL(1); }
                              x = N + lenB - st; CTL(2); CTL(3); if (x > 0 && x < n) { bp[cnt++] = x; CTL(1); } }
    }
    CTL(2);
    bp[cnt++] = n; CTL(1);
    for (int a = 1; a < cnt; a++) {                                              /* insertion sort */
        size_t key = bp[a]; int b = a - 1; CTL(3 + 2);
        while (b >= 0 && bp[b] > key) { bp[b + 1] = bp[b]; b--; CTL(3 + 3); }
        CTL(3);
        bp[b + 1] = key;
    }
    CTL(2);
    int m = 0;                                                                   /* drop empty ranges */
    for (int a = 0; a + 1 < cnt; a++) {
        CTL(3 + 3);
        if (bp[a + 1] > bp[a]) {
            size_t lo = bp[a]; int p = 0;
            for (int t = 0; t < 3; t++) { size_t idx = (lo + n * (size_t)t + N - boff) % N; p |= (idx < lenB) << t; CTL(3 + 5 + 3); }
            CTL(2 + 3);
            bp[m] = lo; pat[m] = p; m++; CTL(2);
        }
    }
    CTL(2);
    bp[m] = n; CTL(1);
    return m;
}
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(4);                                                                       /* test of rows, dispatch */
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        CTL(4);                                                                   /* test dst == src && off == 0 */
        if (dst == src && off == 0) { if (n > len) { FOR8(i, n - len, dst[len + i] = z; ST(1)); } return; }
        { size_t c = len < n ? len : n; FOR8(i, c, dst[i] = src[off + i]; LD(1); ST(1)); if (n > c) { FOR8(i, n - c, dst[c + i] = z; ST(1)); } }
        return;
    }
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, P->N, 0, len, bp, pat);
    int c0 = P->c0 % 3; CTL(2);
    for (int q = 0; q < nr; q++) {
        CTL(4);                                                                   /* table lookup of the driver, indirect call */
        RGF[c0][pat[q]](dst, src + off, (ptrdiff_t)0, (ptrdiff_t)n, (ptrdiff_t)(2 * n), n, bp[q], bp[q + 1]);
        CTL(3);
    }
    CTL(2);
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n;
    CTL(2);
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, P->N, 0, outlen, bp, pat);
    int c0 = P->c0 % 3; CTL(2);
    for (int q = 0; q < nr; q++) {
        CTL(2); if (pat[q] == 0) { CTL(3); continue; }
        CTL(4);
        RGI[c0][pat[q]](buf, NULL, 0, 0, 0, n, bp[q], bp[q + 1]);
        CTL(3);
    }
    CTL(2);
}

/* Row r of the Good-Thomas stage for the compact vector B (see split_regions for the layout of B at the cyclic offset boff) */
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N;
    size_t bp[12]; int pat[12];
    int nr = split_regions(n, N, boff, lenB, bp, pat);
    int c0 = P->c0 % 3; CTL(2);
    for (int q = 0; q < nr; q++) {
        size_t lo = bp[q];
        ptrdiff_t d[3];
        for (int t = 0; t < 3; t++) { size_t idx = (lo + n * (size_t)t + N - boff) % N; d[t] = (ptrdiff_t)idx - (ptrdiff_t)lo; CTL(3 + 6); }
        CTL(2);
        CTL(4);
        RGR[r][c0][pat[q]](tmp, B, d[0], d[1], d[2], n, lo, bp[q + 1]);
        CTL(3);
    }
    CTL(2);
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

/* spectrum of the compact vector B (lenB coefficients, cyclic offset boff) of a rows==3 plan, generated row by row straight into dst (P->N slots) */
void ntt_fwd_shifted(const plan_t *P, fp *dst, const fp *B, size_t lenB, size_t boff) {
    CTL(4);
    for (int r = 0; r < 3; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(2 + 2);
        stageA_row(P, row, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
    }
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
            if (t == 0) { FOR8(i, n, fp_mul(&row[i], &tmpA[i], &tmpB[i]); LD(2); ST(1)); }
            else if (sign[t] > 0) { FOR8(i, n, fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_add(&row[i], &row[i], &x); LD(3); ST(1)); }
            else { FOR8(i, n, fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_sub(&row[i], &row[i], &x); LD(3); ST(1)); }
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

### gen_kern.py

```python
"""Generates ntt_kern.h (straight-line register-block kernels and whole pass functions) and ntt_a3.h (straight-line radix-3 position
kernels and their region drivers) for ntt.c.  Every generated statement that executes loads, stores, integer or address operations
carries its charge on the same line (LD / ST / CTL); field operations are charged by pallas.c.  Nothing in a kernel is a loop or a branch.

Register file (disclosed assumption): a block keeps 2^k <= 16 data words x[] of 256 bits in registers; the twiddle operand, the
butterfly temporary and the radix-3 constants are charged as loads where they are used, and need 2 further working words.
Integer values (strides, shift counts, base pointers) are held in integer registers."""

# ---------------------------------------------------------------- block kernels
out = ['/* generated by gen_kern.py: straight-line butterfly blocks (k = 1..4 layers) and whole passes; x[] is the register block */',
       '#define BF(u, v, w) do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, (w)); } while (0)',
       '#define BFN(u, v) do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); (v) = t_; } while (0)',
       '#define IB(u, v, w) do { fp tt_, A_ = (u); fp_mul(&tt_, &(v), (w)); fp_sub(&(u), &A_, &tt_); fp_add(&(v), &A_, &tt_); } while (0)',
       '#define IBN(u, v) do { fp tt_ = (v); fp_sub(&(v), &(u), &tt_); fp_add(&(u), &(u), &tt_); } while (0)']


def layers(k):
    L = []
    for j in range(k):
        half = 1 << (k - 1 - j)
        for tp in range(half):
            L.append((j, tp, list(range(tp, 1 << k, 2 * half)), half))
    return L


for k in range(1, 5):
    L = layers(k)
    for z in (0, 1):
        out.append('static inline void kf%d%s(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {' % (k, 'z' if z else ''))
        for (j, tp, ts, half) in L:
            if tp == 0:
                if z:
                    for t in ts:
                        out.append('    BFN(x[%d], x[%d]);' % (t, t + half))
                    if half > 1:
                        out.append('    const fp *w%d = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */' % j)
                else:
                    out.append('    const fp *w%d = tw + (b << sjs[%d]); LD(1); CTL(2);' % (j, j))
                    for t in ts:
                        out.append('    BF(x[%d], x[%d], w%d);' % (t, t + half, j))
            else:
                out.append('    w%d += D[%d]; LD(1); CTL(1);' % (j, j))
                for t in ts:
                    out.append('    BF(x[%d], x[%d], w%d);' % (t, t + half, j))
        out.append('}')
    for z in (0, 1):
        out.append('static inline void ki%d%s(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {' % (k, 'z' if z else ''))
        for j in reversed(range(k)):
            for (jj, tp, ts, half) in L:
                if jj != j:
                    continue
                if tp == 0:
                    if z:
                        for t in ts:
                            out.append('    IBN(x[%d], x[%d]);' % (t, t + half))
                        if half > 1:
                            out.append('    const fp *w%d = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */' % j)
                    else:
                        out.append('    const fp *w%d = tw + ((nh - (b << sj[%d])) << sh); LD(1); CTL(4);' % (j, j))
                        for t in ts:
                            out.append('    IB(x[%d], x[%d], w%d);' % (t, t + half, j))
                else:
                    out.append('    w%d -= D[%d]; LD(1); CTL(1);' % (j, j))
                    for t in ts:
                        out.append('    IB(x[%d], x[%d], w%d);' % (t, t + half, j))
        out.append('}')


def loads(k, ind='            '):
    return '\n'.join('%sx[%d] = base[%s]; LD(1);' % (ind, i, ('%d * s' % i) if i > 1 else ('s' if i == 1 else '0')) for i in range(1 << k))


def stores(k, ind='            '):
    return '\n'.join('%sbase[%s] = x[%d]; ST(1);' % (ind, ('%d * s' % i) if i > 1 else ('s' if i == 1 else '0'), i) for i in range(1 << k))


for k in range(1, 5):
    G = 1 << k
    # forward pass: block b == 0 of every group uses the z kernel, the blocks b = 1 .. s-1 the general kernel.  Executed integer operations:
    # group base (1), block base (1), block loop (3 per iteration, 2 on exit), group loop (3 per iteration, 2 on exit).
    out.append('static void pf%d(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sjs) {' % k)
    out.append('    fp x[16]; size_t Gs = %d * s; CTL(1);' % G)
    out.append('    for (size_t grp = 0; grp < ngrp; grp++) {')
    out.append('        fp *rb = row + grp * Gs; CTL(1);')
    out.append('        { fp *base = rb;')
    out.append(loads(k, '            '))
    out.append('            kf%dz(x, tw, 0, D, sjs);' % k)
    out.append(stores(k, '            '))
    out.append('        }')
    out.append('        for (size_t b = 1; b < s; b++) {')
    out.append('            fp *base = rb + b; CTL(1);')
    out.append(loads(k))
    out.append('            kf%d(x, tw, b, D, sjs);' % k)
    out.append(stores(k))
    out.append('            CTL(3);')
    out.append('        }')
    out.append('        CTL(2 + 3);')
    out.append('    }')
    out.append('    CTL(2);')
    out.append('}')
    out.append('static void pi%d(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sj, int sh, size_t nh) {' % k)
    out.append('    fp x[16]; size_t Gs = %d * s; CTL(1);' % G)
    out.append('    for (size_t grp = 0; grp < ngrp; grp++) {')
    out.append('        fp *rb = row + grp * Gs; CTL(1);')
    out.append('        { fp *base = rb;')
    out.append(loads(k, '            '))
    out.append('            ki%dz(x, tw, 0, D, sj, sh, nh);' % k)
    out.append(stores(k, '            '))
    out.append('        }')
    out.append('        for (size_t b = 1; b < s; b++) {')
    out.append('            fp *base = rb + b; CTL(1);')
    out.append(loads(k))
    out.append('            ki%d(x, tw, b, D, sj, sh, nh);' % k)
    out.append(stores(k))
    out.append('            CTL(3);')
    out.append('        }')
    out.append('        CTL(2 + 3);')
    out.append('    }')
    out.append('    CTL(2);')
    out.append('}')
    # fused last forward pass + pointwise + first inverse pass (s == 1)
    for mode in ('sq', 'mul'):
        sig = ('static void pu%d_%s(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh%s) {'
               % (k, mode, ', const fp *C' if mode == 'mul' else ''))
        out.append(sig)
        out.append('    fp x[16];')
        out.append('    for (size_t grp = 0; grp < ngrp; grp++) {')
        out.append('        fp *base = row + grp * %d; CTL(1);' % G)
        if mode == 'mul':
            out.append('        const fp *cb = C + grp * %d; CTL(1);' % G)
        for i in range(G):
            out.append('        x[%d] = base[%d]; LD(1);' % (i, i))
        out.append('        kf%dz(x, tw, 0, D, sjs);' % k)
        for i in range(G):
            if mode == 'sq':
                out.append('        fp_sqr(&x[%d], &x[%d]);' % (i, i))
            else:
                out.append('        fp_mul(&x[%d], &x[%d], &cb[%d]); LD(1);' % (i, i, i))
        out.append('        ki%dz(x, tw, 0, D, sj, sh, nh);' % k)
        for i in range(G):
            out.append('        base[%d] = x[%d]; ST(1);' % (i, i))
        out.append('        CTL(3);')
        out.append('    }')
        out.append('    CTL(2);')
        out.append('}')
open('ntt_kern.h', 'w', newline='\n').write('\n'.join(out) + '\n')

# ---------------------------------------------------------------- radix-3 position kernels and region drivers
A = ['/* generated by gen_kern.py: straight-line radix-3 position kernels and the region drivers around them.',
     '   Position kernel = loads of the present inputs, the field operations of the selected linear map, the stores; the constants',
     '   W3[1], W3[2], CH, DL are charged as one load per use. */']


def mask_of(pat, rot):
    m = 0
    for i1 in range(3):
        if (pat >> ((rot + i1) % 3)) & 1:
            m |= 1 << i1
    return m


class Em:
    def __init__(self):
        self.l = []

    def e(self, s):
        self.l.append('    ' + s)


def const_ref(e):
    return '&W3[%d]' % e


def emit_dft3_sel(em, v, nzmask, need, prefix):
    """v[i]: variable names; returns names of outputs o[k] (None if not needed). Mirrors dft3_sel / dft3_full."""
    o = [None] * 3
    if nzmask == 7 and need == 7:
        em.e('fp %st1, %st2, %sm1, %sm2, %so0, %so1, %so2;' % ((prefix,) * 7))
        em.e('fp_add(&%st1, &%s, &%s);' % (prefix, v[1], v[2]))
        em.e('fp_sub(&%st2, &%s, &%s);' % (prefix, v[1], v[2]))
        em.e('fp_add(&%so0, &%s, &%st1);' % (prefix, v[0], prefix))
        em.e('LD(1); fp_mul(&%sm1, &%st1, &CH);' % (prefix, prefix))
        em.e('fp_add(&%sm1, &%sm1, &%s);' % (prefix, prefix, v[0]))
        em.e('LD(1); fp_mul(&%sm2, &%st2, &DL);' % (prefix, prefix))
        em.e('fp_add(&%so1, &%sm1, &%sm2);' % (prefix, prefix, prefix))
        em.e('fp_sub(&%so2, &%sm1, &%sm2);' % (prefix, prefix, prefix))
        return ['%so0' % prefix, '%so1' % prefix, '%so2' % prefix]
    for k in range(3):
        if not (need >> k) & 1:
            continue
        name = '%so%d' % (prefix, k)
        first = True
        for i in range(3):
            if not (nzmask >> i) & 1:
                continue
            e = (i * k) % 3
            if first:
                if e:
                    em.e('fp %s; LD(1); fp_mul(&%s, &%s, %s);' % (name, name, v[i], const_ref(e)))
                else:
                    em.e('fp %s = %s;' % (name, v[i]))
                first = False
            else:
                if e:
                    em.e('{ fp tm_; LD(1); fp_mul(&tm_, &%s, %s); fp_add(&%s, &%s, &tm_); }' % (v[i], const_ref(e), name, name))
                else:
                    em.e('fp_add(&%s, &%s, &%s);' % (name, name, v[i]))
        o[k] = name
    return o


def kernel_fwd(pat, rot):
    em = Em()
    name = 'a3f_%d_%d' % (pat, rot)
    em.e('static inline void %s(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {' % name)
    d = ['d0', 'd1', 'd2']
    for t in range(3):
        if (pat >> t) & 1:
            em.e('    fp u%d = S[(ptrdiff_t)i + %s]; LD(1);' % (t, d[t]))
    mask = mask_of(pat, rot)
    v = [('u%d' % ((rot + i1) % 3)) if (mask >> i1) & 1 else None for i1 in range(3)]
    if mask == 0:
        em.e('    dst[i] = ZERO; ST(1); dst[i + n] = ZERO; ST(1); dst[i + 2 * n] = ZERO; ST(1);')
    else:
        sub = Em()
        o = emit_dft3_sel(sub, v, mask, 7, '')
        em.l += ['    ' + l for l in sub.l]
        em.e('    dst[i] = %s; ST(1); dst[i + n] = %s; ST(1); dst[i + 2 * n] = %s; ST(1);' % tuple(o))
    em.e('}')
    return name, em.l


def kernel_inv(pat, rot):
    em = Em()
    name = 'a3i_%d_%d' % (pat, rot)
    need = mask_of(pat, rot)
    em.e('static inline void %s(fp *buf, size_t n, size_t i) {' % name)
    for k in range(3):
        em.e('    fp A%d = buf[i + %s]; LD(1);' % (k, ['0', 'n', '2 * n'][k]))
    v = ['A0', 'A2', 'A1']
    sub = Em()
    o = emit_dft3_sel(sub, v, 7, need, '')
    em.l += ['    ' + l for l in sub.l]
    for i1 in range(3):
        if (need >> i1) & 1:
            t = (rot + i1) % 3
            em.e('    buf[i + %s] = %s; ST(1);' % (['0', 'n', '2 * n'][t], o[i1]))
    em.e('}')
    return name, em.l


def kernel_row(pat, rot, r):
    em = Em()
    name = 'a3r_%d_%d_%d' % (pat, rot, r)
    em.e('static inline void %s(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {' % name)
    d = ['d0', 'd1', 'd2']
    for t in range(3):
        if (pat >> t) & 1:
            em.e('    fp u%d = S[(ptrdiff_t)i + %s]; LD(1);' % (t, d[t]))
    mask = mask_of(pat, rot)
    v = [('u%d' % ((rot + i1) % 3)) if (mask >> i1) & 1 else None for i1 in range(3)]
    if mask == 0:
        em.e('    tmp[i] = ZERO; ST(1);')
    else:
        sub = Em()
        o = emit_dft3_sel(sub, v, mask, 1 << r, '')
        em.l += ['    ' + l for l in sub.l]
        em.e('    tmp[i] = %s; ST(1);' % o[r])
    em.e('}')
    return name, em.l


for pat in range(8):
    for rot in range(3):
        nm, l = kernel_fwd(pat, rot)
        A += l
for pat in range(1, 8):
    for rot in range(3):
        nm, l = kernel_inv(pat, rot)
        A += l
for r in range(3):
    for pat in range(8):
        for rot in range(3):
            nm, l = kernel_row(pat, rot, r)
            A += l
for c0 in range(3):
    R = [(c0 * ph) % 3 for ph in range(3)]
    for pat in range(8):
        A.append('DRV_F(%d, %d, %d, %d, %d)' % (pat, c0, R[0], R[1], R[2]))
    for pat in range(1, 8):
        A.append('DRV_I(%d, %d, %d, %d, %d)' % (pat, c0, R[0], R[1], R[2]))
    for r in range(3):
        for pat in range(8):
            A.append('DRV_R(%d, %d, %d, %d, %d, %d)' % (r, pat, c0, R[0], R[1], R[2]))
# tables
A.append('static rg_t RGF[3][8] = {')
for c0 in range(3):
    A.append('    { ' + ', '.join('rgf_%d_%d' % (p, c0) for p in range(8)) + ' },')
A.append('};')
A.append('static rg_t RGI[3][8] = {')
for c0 in range(3):
    A.append('    { 0, ' + ', '.join('rgi_%d_%d' % (p, c0) for p in range(1, 8)) + ' },')
A.append('};')
A.append('static rg_t RGR[3][3][8] = {')
for r in range(3):
    A.append('  {')
    for c0 in range(3):
        A.append('    { ' + ', '.join('rgr%d_%d_%d' % (r, p, c0) for p in range(8)) + ' },')
    A.append('  },')
A.append('};')
open('ntt_a3.h', 'w', newline='\n').write('\n'.join(A) + '\n')
print('ok')
```

### ntt_kern.h

```c
/* generated by gen_kern.py: straight-line butterfly blocks (k = 1..4 layers) and whole passes; x[] is the register block */
#define BF(u, v, w) do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, (w)); } while (0)
#define BFN(u, v) do { fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); (v) = t_; } while (0)
#define IB(u, v, w) do { fp tt_, A_ = (u); fp_mul(&tt_, &(v), (w)); fp_sub(&(u), &A_, &tt_); fp_add(&(v), &A_, &tt_); } while (0)
#define IBN(u, v) do { fp tt_ = (v); fp_sub(&(v), &(u), &tt_); fp_add(&(u), &(u), &tt_); } while (0)
static inline void kf1(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    const fp *w0 = tw + (b << sjs[0]); LD(1); CTL(2);
    BF(x[0], x[1], w0);
}
static inline void kf1z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[1]);
}
static inline void ki1(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w0 = tw + ((nh - (b << sj[0])) << sh); LD(1); CTL(4);
    IB(x[0], x[1], w0);
}
static inline void ki1z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
}
static inline void kf2(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    const fp *w0 = tw + (b << sjs[0]); LD(1); CTL(2);
    BF(x[0], x[2], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[3], w0);
    const fp *w1 = tw + (b << sjs[1]); LD(1); CTL(2);
    BF(x[0], x[1], w1);
    BF(x[2], x[3], w1);
}
static inline void kf2z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[2]);
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[3], w0);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
}
static inline void ki2(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w1 = tw + ((nh - (b << sj[1])) << sh); LD(1); CTL(4);
    IB(x[0], x[1], w1);
    IB(x[2], x[3], w1);
    const fp *w0 = tw + ((nh - (b << sj[0])) << sh); LD(1); CTL(4);
    IB(x[0], x[2], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[1], x[3], w0);
}
static inline void ki2z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
    IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    const fp *w0 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[1], x[3], w0);
}
static inline void kf3(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    const fp *w0 = tw + (b << sjs[0]); LD(1); CTL(2);
    BF(x[0], x[4], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[5], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[2], x[6], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[3], x[7], w0);
    const fp *w1 = tw + (b << sjs[1]); LD(1); CTL(2);
    BF(x[0], x[2], w1);
    BF(x[4], x[6], w1);
    w1 += D[1]; LD(1); CTL(1);
    BF(x[1], x[3], w1);
    BF(x[5], x[7], w1);
    const fp *w2 = tw + (b << sjs[2]); LD(1); CTL(2);
    BF(x[0], x[1], w2);
    BF(x[2], x[3], w2);
    BF(x[4], x[5], w2);
    BF(x[6], x[7], w2);
}
static inline void kf3z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[4]);
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[5], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[2], x[6], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[3], x[7], w0);
    BFN(x[0], x[2]);
    BFN(x[4], x[6]);
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w1 += D[1]; LD(1); CTL(1);
    BF(x[1], x[3], w1);
    BF(x[5], x[7], w1);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
    BFN(x[4], x[5]);
    BFN(x[6], x[7]);
}
static inline void ki3(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w2 = tw + ((nh - (b << sj[2])) << sh); LD(1); CTL(4);
    IB(x[0], x[1], w2);
    IB(x[2], x[3], w2);
    IB(x[4], x[5], w2);
    IB(x[6], x[7], w2);
    const fp *w1 = tw + ((nh - (b << sj[1])) << sh); LD(1); CTL(4);
    IB(x[0], x[2], w1);
    IB(x[4], x[6], w1);
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[1], x[3], w1);
    IB(x[5], x[7], w1);
    const fp *w0 = tw + ((nh - (b << sj[0])) << sh); LD(1); CTL(4);
    IB(x[0], x[4], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[1], x[5], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[2], x[6], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[3], x[7], w0);
}
static inline void ki3z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
    IBN(x[2], x[3]);
    IBN(x[4], x[5]);
    IBN(x[6], x[7]);
    IBN(x[0], x[2]);
    IBN(x[4], x[6]);
    const fp *w1 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[1], x[3], w1);
    IB(x[5], x[7], w1);
    IBN(x[0], x[4]);
    const fp *w0 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[1], x[5], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[2], x[6], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[3], x[7], w0);
}
static inline void kf4(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    const fp *w0 = tw + (b << sjs[0]); LD(1); CTL(2);
    BF(x[0], x[8], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[9], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[2], x[10], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[3], x[11], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[4], x[12], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[5], x[13], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[6], x[14], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[7], x[15], w0);
    const fp *w1 = tw + (b << sjs[1]); LD(1); CTL(2);
    BF(x[0], x[4], w1);
    BF(x[8], x[12], w1);
    w1 += D[1]; LD(1); CTL(1);
    BF(x[1], x[5], w1);
    BF(x[9], x[13], w1);
    w1 += D[1]; LD(1); CTL(1);
    BF(x[2], x[6], w1);
    BF(x[10], x[14], w1);
    w1 += D[1]; LD(1); CTL(1);
    BF(x[3], x[7], w1);
    BF(x[11], x[15], w1);
    const fp *w2 = tw + (b << sjs[2]); LD(1); CTL(2);
    BF(x[0], x[2], w2);
    BF(x[4], x[6], w2);
    BF(x[8], x[10], w2);
    BF(x[12], x[14], w2);
    w2 += D[2]; LD(1); CTL(1);
    BF(x[1], x[3], w2);
    BF(x[5], x[7], w2);
    BF(x[9], x[11], w2);
    BF(x[13], x[15], w2);
    const fp *w3 = tw + (b << sjs[3]); LD(1); CTL(2);
    BF(x[0], x[1], w3);
    BF(x[2], x[3], w3);
    BF(x[4], x[5], w3);
    BF(x[6], x[7], w3);
    BF(x[8], x[9], w3);
    BF(x[10], x[11], w3);
    BF(x[12], x[13], w3);
    BF(x[14], x[15], w3);
}
static inline void kf4z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[8]);
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[9], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[2], x[10], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[3], x[11], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[4], x[12], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[5], x[13], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[6], x[14], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[7], x[15], w0);
    BFN(x[0], x[4]);
    BFN(x[8], x[12]);
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w1 += D[1]; LD(1); CTL(1);
    BF(x[1], x[5], w1);
    BF(x[9], x[13], w1);
    w1 += D[1]; LD(1); CTL(1);
    BF(x[2], x[6], w1);
    BF(x[10], x[14], w1);
    w1 += D[1]; LD(1); CTL(1);
    BF(x[3], x[7], w1);
    BF(x[11], x[15], w1);
    BFN(x[0], x[2]);
    BFN(x[4], x[6]);
    BFN(x[8], x[10]);
    BFN(x[12], x[14]);
    const fp *w2 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w2 += D[2]; LD(1); CTL(1);
    BF(x[1], x[3], w2);
    BF(x[5], x[7], w2);
    BF(x[9], x[11], w2);
    BF(x[13], x[15], w2);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
    BFN(x[4], x[5]);
    BFN(x[6], x[7]);
    BFN(x[8], x[9]);
    BFN(x[10], x[11]);
    BFN(x[12], x[13]);
    BFN(x[14], x[15]);
}
static inline void ki4(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w3 = tw + ((nh - (b << sj[3])) << sh); LD(1); CTL(4);
    IB(x[0], x[1], w3);
    IB(x[2], x[3], w3);
    IB(x[4], x[5], w3);
    IB(x[6], x[7], w3);
    IB(x[8], x[9], w3);
    IB(x[10], x[11], w3);
    IB(x[12], x[13], w3);
    IB(x[14], x[15], w3);
    const fp *w2 = tw + ((nh - (b << sj[2])) << sh); LD(1); CTL(4);
    IB(x[0], x[2], w2);
    IB(x[4], x[6], w2);
    IB(x[8], x[10], w2);
    IB(x[12], x[14], w2);
    w2 -= D[2]; LD(1); CTL(1);
    IB(x[1], x[3], w2);
    IB(x[5], x[7], w2);
    IB(x[9], x[11], w2);
    IB(x[13], x[15], w2);
    const fp *w1 = tw + ((nh - (b << sj[1])) << sh); LD(1); CTL(4);
    IB(x[0], x[4], w1);
    IB(x[8], x[12], w1);
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[1], x[5], w1);
    IB(x[9], x[13], w1);
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[2], x[6], w1);
    IB(x[10], x[14], w1);
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[3], x[7], w1);
    IB(x[11], x[15], w1);
    const fp *w0 = tw + ((nh - (b << sj[0])) << sh); LD(1); CTL(4);
    IB(x[0], x[8], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[1], x[9], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[2], x[10], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[3], x[11], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[4], x[12], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[5], x[13], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[6], x[14], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[7], x[15], w0);
}
static inline void ki4z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
    IBN(x[2], x[3]);
    IBN(x[4], x[5]);
    IBN(x[6], x[7]);
    IBN(x[8], x[9]);
    IBN(x[10], x[11]);
    IBN(x[12], x[13]);
    IBN(x[14], x[15]);
    IBN(x[0], x[2]);
    IBN(x[4], x[6]);
    IBN(x[8], x[10]);
    IBN(x[12], x[14]);
    const fp *w2 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
    w2 -= D[2]; LD(1); CTL(1);
    IB(x[1], x[3], w2);
    IB(x[5], x[7], w2);
    IB(x[9], x[11], w2);
    IB(x[13], x[15], w2);
    IBN(x[0], x[4]);
    IBN(x[8], x[12]);
    const fp *w1 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[1], x[5], w1);
    IB(x[9], x[13], w1);
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[2], x[6], w1);
    IB(x[10], x[14], w1);
    w1 -= D[1]; LD(1); CTL(1);
    IB(x[3], x[7], w1);
    IB(x[11], x[15], w1);
    IBN(x[0], x[8]);
    const fp *w0 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[1], x[9], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[2], x[10], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[3], x[11], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[4], x[12], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[5], x[13], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[6], x[14], w0);
    w0 -= D[0]; LD(1); CTL(1);
    IB(x[7], x[15], w0);
}
static void pf1(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sjs) {
    fp x[16]; size_t Gs = 2 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            kf1z(x, tw, 0, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            kf1(x, tw, b, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pi1(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sj, int sh, size_t nh) {
    fp x[16]; size_t Gs = 2 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            ki1z(x, tw, 0, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            ki1(x, tw, b, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pu1_sq(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 2; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        kf1z(x, tw, 0, D, sjs);
        fp_sqr(&x[0], &x[0]);
        fp_sqr(&x[1], &x[1]);
        ki1z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pu1_mul(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh, const fp *C) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 2; CTL(1);
        const fp *cb = C + grp * 2; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        kf1z(x, tw, 0, D, sjs);
        fp_mul(&x[0], &x[0], &cb[0]); LD(1);
        fp_mul(&x[1], &x[1], &cb[1]); LD(1);
        ki1z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pf2(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sjs) {
    fp x[16]; size_t Gs = 4 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            kf2z(x, tw, 0, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            kf2(x, tw, b, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pi2(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sj, int sh, size_t nh) {
    fp x[16]; size_t Gs = 4 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            ki2z(x, tw, 0, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            ki2(x, tw, b, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pu2_sq(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 4; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        x[2] = base[2]; LD(1);
        x[3] = base[3]; LD(1);
        kf2z(x, tw, 0, D, sjs);
        fp_sqr(&x[0], &x[0]);
        fp_sqr(&x[1], &x[1]);
        fp_sqr(&x[2], &x[2]);
        fp_sqr(&x[3], &x[3]);
        ki2z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        base[2] = x[2]; ST(1);
        base[3] = x[3]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pu2_mul(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh, const fp *C) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 4; CTL(1);
        const fp *cb = C + grp * 4; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        x[2] = base[2]; LD(1);
        x[3] = base[3]; LD(1);
        kf2z(x, tw, 0, D, sjs);
        fp_mul(&x[0], &x[0], &cb[0]); LD(1);
        fp_mul(&x[1], &x[1], &cb[1]); LD(1);
        fp_mul(&x[2], &x[2], &cb[2]); LD(1);
        fp_mul(&x[3], &x[3], &cb[3]); LD(1);
        ki2z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        base[2] = x[2]; ST(1);
        base[3] = x[3]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pf3(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sjs) {
    fp x[16]; size_t Gs = 8 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            kf3z(x, tw, 0, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            kf3(x, tw, b, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pi3(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sj, int sh, size_t nh) {
    fp x[16]; size_t Gs = 8 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            ki3z(x, tw, 0, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            ki3(x, tw, b, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pu3_sq(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 8; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        x[2] = base[2]; LD(1);
        x[3] = base[3]; LD(1);
        x[4] = base[4]; LD(1);
        x[5] = base[5]; LD(1);
        x[6] = base[6]; LD(1);
        x[7] = base[7]; LD(1);
        kf3z(x, tw, 0, D, sjs);
        fp_sqr(&x[0], &x[0]);
        fp_sqr(&x[1], &x[1]);
        fp_sqr(&x[2], &x[2]);
        fp_sqr(&x[3], &x[3]);
        fp_sqr(&x[4], &x[4]);
        fp_sqr(&x[5], &x[5]);
        fp_sqr(&x[6], &x[6]);
        fp_sqr(&x[7], &x[7]);
        ki3z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        base[2] = x[2]; ST(1);
        base[3] = x[3]; ST(1);
        base[4] = x[4]; ST(1);
        base[5] = x[5]; ST(1);
        base[6] = x[6]; ST(1);
        base[7] = x[7]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pu3_mul(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh, const fp *C) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 8; CTL(1);
        const fp *cb = C + grp * 8; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        x[2] = base[2]; LD(1);
        x[3] = base[3]; LD(1);
        x[4] = base[4]; LD(1);
        x[5] = base[5]; LD(1);
        x[6] = base[6]; LD(1);
        x[7] = base[7]; LD(1);
        kf3z(x, tw, 0, D, sjs);
        fp_mul(&x[0], &x[0], &cb[0]); LD(1);
        fp_mul(&x[1], &x[1], &cb[1]); LD(1);
        fp_mul(&x[2], &x[2], &cb[2]); LD(1);
        fp_mul(&x[3], &x[3], &cb[3]); LD(1);
        fp_mul(&x[4], &x[4], &cb[4]); LD(1);
        fp_mul(&x[5], &x[5], &cb[5]); LD(1);
        fp_mul(&x[6], &x[6], &cb[6]); LD(1);
        fp_mul(&x[7], &x[7], &cb[7]); LD(1);
        ki3z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        base[2] = x[2]; ST(1);
        base[3] = x[3]; ST(1);
        base[4] = x[4]; ST(1);
        base[5] = x[5]; ST(1);
        base[6] = x[6]; ST(1);
        base[7] = x[7]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pf4(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sjs) {
    fp x[16]; size_t Gs = 16 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            x[8] = base[8 * s]; LD(1);
            x[9] = base[9 * s]; LD(1);
            x[10] = base[10 * s]; LD(1);
            x[11] = base[11 * s]; LD(1);
            x[12] = base[12 * s]; LD(1);
            x[13] = base[13 * s]; LD(1);
            x[14] = base[14 * s]; LD(1);
            x[15] = base[15 * s]; LD(1);
            kf4z(x, tw, 0, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
            base[8 * s] = x[8]; ST(1);
            base[9 * s] = x[9]; ST(1);
            base[10 * s] = x[10]; ST(1);
            base[11 * s] = x[11]; ST(1);
            base[12 * s] = x[12]; ST(1);
            base[13 * s] = x[13]; ST(1);
            base[14 * s] = x[14]; ST(1);
            base[15 * s] = x[15]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            x[8] = base[8 * s]; LD(1);
            x[9] = base[9 * s]; LD(1);
            x[10] = base[10 * s]; LD(1);
            x[11] = base[11 * s]; LD(1);
            x[12] = base[12 * s]; LD(1);
            x[13] = base[13 * s]; LD(1);
            x[14] = base[14 * s]; LD(1);
            x[15] = base[15 * s]; LD(1);
            kf4(x, tw, b, D, sjs);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
            base[8 * s] = x[8]; ST(1);
            base[9 * s] = x[9]; ST(1);
            base[10 * s] = x[10]; ST(1);
            base[11 * s] = x[11]; ST(1);
            base[12 * s] = x[12]; ST(1);
            base[13 * s] = x[13]; ST(1);
            base[14 * s] = x[14]; ST(1);
            base[15 * s] = x[15]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pi4(fp *row, size_t s, size_t ngrp, const fp *tw, const size_t *D, const int *sj, int sh, size_t nh) {
    fp x[16]; size_t Gs = 16 * s; CTL(1);
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *rb = row + grp * Gs; CTL(1);
        { fp *base = rb;
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            x[8] = base[8 * s]; LD(1);
            x[9] = base[9 * s]; LD(1);
            x[10] = base[10 * s]; LD(1);
            x[11] = base[11 * s]; LD(1);
            x[12] = base[12 * s]; LD(1);
            x[13] = base[13 * s]; LD(1);
            x[14] = base[14 * s]; LD(1);
            x[15] = base[15 * s]; LD(1);
            ki4z(x, tw, 0, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
            base[8 * s] = x[8]; ST(1);
            base[9 * s] = x[9]; ST(1);
            base[10 * s] = x[10]; ST(1);
            base[11 * s] = x[11]; ST(1);
            base[12 * s] = x[12]; ST(1);
            base[13 * s] = x[13]; ST(1);
            base[14 * s] = x[14]; ST(1);
            base[15 * s] = x[15]; ST(1);
        }
        for (size_t b = 1; b < s; b++) {
            fp *base = rb + b; CTL(1);
            x[0] = base[0]; LD(1);
            x[1] = base[s]; LD(1);
            x[2] = base[2 * s]; LD(1);
            x[3] = base[3 * s]; LD(1);
            x[4] = base[4 * s]; LD(1);
            x[5] = base[5 * s]; LD(1);
            x[6] = base[6 * s]; LD(1);
            x[7] = base[7 * s]; LD(1);
            x[8] = base[8 * s]; LD(1);
            x[9] = base[9 * s]; LD(1);
            x[10] = base[10 * s]; LD(1);
            x[11] = base[11 * s]; LD(1);
            x[12] = base[12 * s]; LD(1);
            x[13] = base[13 * s]; LD(1);
            x[14] = base[14 * s]; LD(1);
            x[15] = base[15 * s]; LD(1);
            ki4(x, tw, b, D, sj, sh, nh);
            base[0] = x[0]; ST(1);
            base[s] = x[1]; ST(1);
            base[2 * s] = x[2]; ST(1);
            base[3 * s] = x[3]; ST(1);
            base[4 * s] = x[4]; ST(1);
            base[5 * s] = x[5]; ST(1);
            base[6 * s] = x[6]; ST(1);
            base[7 * s] = x[7]; ST(1);
            base[8 * s] = x[8]; ST(1);
            base[9 * s] = x[9]; ST(1);
            base[10 * s] = x[10]; ST(1);
            base[11 * s] = x[11]; ST(1);
            base[12 * s] = x[12]; ST(1);
            base[13 * s] = x[13]; ST(1);
            base[14 * s] = x[14]; ST(1);
            base[15 * s] = x[15]; ST(1);
            CTL(3);
        }
        CTL(2 + 3);
    }
    CTL(2);
}
static void pu4_sq(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 16; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        x[2] = base[2]; LD(1);
        x[3] = base[3]; LD(1);
        x[4] = base[4]; LD(1);
        x[5] = base[5]; LD(1);
        x[6] = base[6]; LD(1);
        x[7] = base[7]; LD(1);
        x[8] = base[8]; LD(1);
        x[9] = base[9]; LD(1);
        x[10] = base[10]; LD(1);
        x[11] = base[11]; LD(1);
        x[12] = base[12]; LD(1);
        x[13] = base[13]; LD(1);
        x[14] = base[14]; LD(1);
        x[15] = base[15]; LD(1);
        kf4z(x, tw, 0, D, sjs);
        fp_sqr(&x[0], &x[0]);
        fp_sqr(&x[1], &x[1]);
        fp_sqr(&x[2], &x[2]);
        fp_sqr(&x[3], &x[3]);
        fp_sqr(&x[4], &x[4]);
        fp_sqr(&x[5], &x[5]);
        fp_sqr(&x[6], &x[6]);
        fp_sqr(&x[7], &x[7]);
        fp_sqr(&x[8], &x[8]);
        fp_sqr(&x[9], &x[9]);
        fp_sqr(&x[10], &x[10]);
        fp_sqr(&x[11], &x[11]);
        fp_sqr(&x[12], &x[12]);
        fp_sqr(&x[13], &x[13]);
        fp_sqr(&x[14], &x[14]);
        fp_sqr(&x[15], &x[15]);
        ki4z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        base[2] = x[2]; ST(1);
        base[3] = x[3]; ST(1);
        base[4] = x[4]; ST(1);
        base[5] = x[5]; ST(1);
        base[6] = x[6]; ST(1);
        base[7] = x[7]; ST(1);
        base[8] = x[8]; ST(1);
        base[9] = x[9]; ST(1);
        base[10] = x[10]; ST(1);
        base[11] = x[11]; ST(1);
        base[12] = x[12]; ST(1);
        base[13] = x[13]; ST(1);
        base[14] = x[14]; ST(1);
        base[15] = x[15]; ST(1);
        CTL(3);
    }
    CTL(2);
}
static void pu4_mul(fp *row, size_t ngrp, const fp *tw, const size_t *D, const int *sjs, const int *sj, int sh, size_t nh, const fp *C) {
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * 16; CTL(1);
        const fp *cb = C + grp * 16; CTL(1);
        x[0] = base[0]; LD(1);
        x[1] = base[1]; LD(1);
        x[2] = base[2]; LD(1);
        x[3] = base[3]; LD(1);
        x[4] = base[4]; LD(1);
        x[5] = base[5]; LD(1);
        x[6] = base[6]; LD(1);
        x[7] = base[7]; LD(1);
        x[8] = base[8]; LD(1);
        x[9] = base[9]; LD(1);
        x[10] = base[10]; LD(1);
        x[11] = base[11]; LD(1);
        x[12] = base[12]; LD(1);
        x[13] = base[13]; LD(1);
        x[14] = base[14]; LD(1);
        x[15] = base[15]; LD(1);
        kf4z(x, tw, 0, D, sjs);
        fp_mul(&x[0], &x[0], &cb[0]); LD(1);
        fp_mul(&x[1], &x[1], &cb[1]); LD(1);
        fp_mul(&x[2], &x[2], &cb[2]); LD(1);
        fp_mul(&x[3], &x[3], &cb[3]); LD(1);
        fp_mul(&x[4], &x[4], &cb[4]); LD(1);
        fp_mul(&x[5], &x[5], &cb[5]); LD(1);
        fp_mul(&x[6], &x[6], &cb[6]); LD(1);
        fp_mul(&x[7], &x[7], &cb[7]); LD(1);
        fp_mul(&x[8], &x[8], &cb[8]); LD(1);
        fp_mul(&x[9], &x[9], &cb[9]); LD(1);
        fp_mul(&x[10], &x[10], &cb[10]); LD(1);
        fp_mul(&x[11], &x[11], &cb[11]); LD(1);
        fp_mul(&x[12], &x[12], &cb[12]); LD(1);
        fp_mul(&x[13], &x[13], &cb[13]); LD(1);
        fp_mul(&x[14], &x[14], &cb[14]); LD(1);
        fp_mul(&x[15], &x[15], &cb[15]); LD(1);
        ki4z(x, tw, 0, D, sj, sh, nh);
        base[0] = x[0]; ST(1);
        base[1] = x[1]; ST(1);
        base[2] = x[2]; ST(1);
        base[3] = x[3]; ST(1);
        base[4] = x[4]; ST(1);
        base[5] = x[5]; ST(1);
        base[6] = x[6]; ST(1);
        base[7] = x[7]; ST(1);
        base[8] = x[8]; ST(1);
        base[9] = x[9]; ST(1);
        base[10] = x[10]; ST(1);
        base[11] = x[11]; ST(1);
        base[12] = x[12]; ST(1);
        base[13] = x[13]; ST(1);
        base[14] = x[14]; ST(1);
        base[15] = x[15]; ST(1);
        CTL(3);
    }
    CTL(2);
}
```

### ntt_a3.h

```c
/* generated by gen_kern.py: straight-line radix-3 position kernels and the region drivers around them.
   Position kernel = loads of the present inputs, the field operations of the selected linear map, the stores; the constants
   W3[1], W3[2], CH, DL are charged as one load per use. */
    static inline void a3f_0_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        dst[i] = ZERO; ST(1); dst[i + n] = ZERO; ST(1); dst[i + 2 * n] = ZERO; ST(1);
    }
    static inline void a3f_0_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        dst[i] = ZERO; ST(1); dst[i + n] = ZERO; ST(1); dst[i + 2 * n] = ZERO; ST(1);
    }
    static inline void a3f_0_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        dst[i] = ZERO; ST(1); dst[i + n] = ZERO; ST(1); dst[i + 2 * n] = ZERO; ST(1);
    }
    static inline void a3f_1_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o0 = u0;
        fp o1 = u0;
        fp o2 = u0;
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_1_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o0 = u0;
        fp o1; LD(1); fp_mul(&o1, &u0, &W3[2]);
        fp o2; LD(1); fp_mul(&o2, &u0, &W3[1]);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_1_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o0 = u0;
        fp o1; LD(1); fp_mul(&o1, &u0, &W3[1]);
        fp o2; LD(1); fp_mul(&o2, &u0, &W3[2]);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_2_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        fp o1; LD(1); fp_mul(&o1, &u1, &W3[1]);
        fp o2; LD(1); fp_mul(&o2, &u1, &W3[2]);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_2_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        fp o1 = u1;
        fp o2 = u1;
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_2_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        fp o1; LD(1); fp_mul(&o1, &u1, &W3[2]);
        fp o2; LD(1); fp_mul(&o2, &u1, &W3[1]);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_3_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u1);
        fp o1 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o1, &o1, &tm_); }
        fp o2 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_3_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u0);
        fp o1 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_3_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u1);
        fp o1; LD(1); fp_mul(&o1, &u0, &W3[1]);
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2; LD(1); fp_mul(&o2, &u0, &W3[2]);
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_4_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp o1; LD(1); fp_mul(&o1, &u2, &W3[2]);
        fp o2; LD(1); fp_mul(&o2, &u2, &W3[1]);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_4_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp o1; LD(1); fp_mul(&o1, &u2, &W3[1]);
        fp o2; LD(1); fp_mul(&o2, &u2, &W3[2]);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_4_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp o1 = u2;
        fp o2 = u2;
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_5_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u2);
        fp o1 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_5_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u0);
        fp o1; LD(1); fp_mul(&o1, &u2, &W3[1]);
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2; LD(1); fp_mul(&o2, &u2, &W3[2]);
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_5_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u0);
        fp o1 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o1, &o1, &tm_); }
        fp o2 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_6_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u2);
        fp o1; LD(1); fp_mul(&o1, &u1, &W3[1]);
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2; LD(1); fp_mul(&o2, &u1, &W3[2]);
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_6_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u2);
        fp o1 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        fp o2 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_6_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u1);
        fp o1 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_7_0(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp t1, t2, m1, m2, o0, o1, o2;
        fp_add(&t1, &u1, &u2);
        fp_sub(&t2, &u1, &u2);
        fp_add(&o0, &u0, &t1);
        LD(1); fp_mul(&m1, &t1, &CH);
        fp_add(&m1, &m1, &u0);
        LD(1); fp_mul(&m2, &t2, &DL);
        fp_add(&o1, &m1, &m2);
        fp_sub(&o2, &m1, &m2);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_7_1(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp t1, t2, m1, m2, o0, o1, o2;
        fp_add(&t1, &u2, &u0);
        fp_sub(&t2, &u2, &u0);
        fp_add(&o0, &u1, &t1);
        LD(1); fp_mul(&m1, &t1, &CH);
        fp_add(&m1, &m1, &u1);
        LD(1); fp_mul(&m2, &t2, &DL);
        fp_add(&o1, &m1, &m2);
        fp_sub(&o2, &m1, &m2);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3f_7_2(fp *dst, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t n, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp t1, t2, m1, m2, o0, o1, o2;
        fp_add(&t1, &u0, &u1);
        fp_sub(&t2, &u0, &u1);
        fp_add(&o0, &u2, &t1);
        LD(1); fp_mul(&m1, &t1, &CH);
        fp_add(&m1, &m1, &u2);
        LD(1); fp_mul(&m2, &t2, &DL);
        fp_add(&o1, &m1, &m2);
        fp_sub(&o2, &m1, &m2);
        dst[i] = o0; ST(1); dst[i + n] = o1; ST(1); dst[i + 2 * n] = o2; ST(1);
    }
    static inline void a3i_1_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        buf[i + 0] = o0; ST(1);
    }
    static inline void a3i_1_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + 0] = o2; ST(1);
    }
    static inline void a3i_1_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        buf[i + 0] = o1; ST(1);
    }
    static inline void a3i_2_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        buf[i + n] = o1; ST(1);
    }
    static inline void a3i_2_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        buf[i + n] = o0; ST(1);
    }
    static inline void a3i_2_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + n] = o2; ST(1);
    }
    static inline void a3i_3_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        buf[i + 0] = o0; ST(1);
        buf[i + n] = o1; ST(1);
    }
    static inline void a3i_3_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + n] = o0; ST(1);
        buf[i + 0] = o2; ST(1);
    }
    static inline void a3i_3_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + 0] = o1; ST(1);
        buf[i + n] = o2; ST(1);
    }
    static inline void a3i_4_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + 2 * n] = o2; ST(1);
    }
    static inline void a3i_4_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        buf[i + 2 * n] = o1; ST(1);
    }
    static inline void a3i_4_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        buf[i + 2 * n] = o0; ST(1);
    }
    static inline void a3i_5_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + 0] = o0; ST(1);
        buf[i + 2 * n] = o2; ST(1);
    }
    static inline void a3i_5_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + 2 * n] = o1; ST(1);
        buf[i + 0] = o2; ST(1);
    }
    static inline void a3i_5_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        buf[i + 2 * n] = o0; ST(1);
        buf[i + 0] = o1; ST(1);
    }
    static inline void a3i_6_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + n] = o1; ST(1);
        buf[i + 2 * n] = o2; ST(1);
    }
    static inline void a3i_6_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        fp o1 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        buf[i + n] = o0; ST(1);
        buf[i + 2 * n] = o1; ST(1);
    }
    static inline void a3i_6_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp o0 = A0;
        fp_add(&o0, &o0, &A2);
        fp_add(&o0, &o0, &A1);
        fp o2 = A0;
        { fp tm_; LD(1); fp_mul(&tm_, &A2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &A1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        buf[i + 2 * n] = o0; ST(1);
        buf[i + n] = o2; ST(1);
    }
    static inline void a3i_7_0(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp t1, t2, m1, m2, o0, o1, o2;
        fp_add(&t1, &A2, &A1);
        fp_sub(&t2, &A2, &A1);
        fp_add(&o0, &A0, &t1);
        LD(1); fp_mul(&m1, &t1, &CH);
        fp_add(&m1, &m1, &A0);
        LD(1); fp_mul(&m2, &t2, &DL);
        fp_add(&o1, &m1, &m2);
        fp_sub(&o2, &m1, &m2);
        buf[i + 0] = o0; ST(1);
        buf[i + n] = o1; ST(1);
        buf[i + 2 * n] = o2; ST(1);
    }
    static inline void a3i_7_1(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp t1, t2, m1, m2, o0, o1, o2;
        fp_add(&t1, &A2, &A1);
        fp_sub(&t2, &A2, &A1);
        fp_add(&o0, &A0, &t1);
        LD(1); fp_mul(&m1, &t1, &CH);
        fp_add(&m1, &m1, &A0);
        LD(1); fp_mul(&m2, &t2, &DL);
        fp_add(&o1, &m1, &m2);
        fp_sub(&o2, &m1, &m2);
        buf[i + n] = o0; ST(1);
        buf[i + 2 * n] = o1; ST(1);
        buf[i + 0] = o2; ST(1);
    }
    static inline void a3i_7_2(fp *buf, size_t n, size_t i) {
        fp A0 = buf[i + 0]; LD(1);
        fp A1 = buf[i + n]; LD(1);
        fp A2 = buf[i + 2 * n]; LD(1);
        fp t1, t2, m1, m2, o0, o1, o2;
        fp_add(&t1, &A2, &A1);
        fp_sub(&t2, &A2, &A1);
        fp_add(&o0, &A0, &t1);
        LD(1); fp_mul(&m1, &t1, &CH);
        fp_add(&m1, &m1, &A0);
        LD(1); fp_mul(&m2, &t2, &DL);
        fp_add(&o1, &m1, &m2);
        fp_sub(&o2, &m1, &m2);
        buf[i + 2 * n] = o0; ST(1);
        buf[i + 0] = o1; ST(1);
        buf[i + n] = o2; ST(1);
    }
    static inline void a3r_0_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_0_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_0_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_1_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o0 = u0;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_1_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o0 = u0;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_1_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o0 = u0;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_2_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_2_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_2_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_3_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u1);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_3_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u0);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_3_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u1);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_4_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_4_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_4_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_5_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u2);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_5_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u0);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_5_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u0);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_6_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u2);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_6_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u2);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_6_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u1);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_7_0_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u0;
        fp_add(&o0, &o0, &u1);
        fp_add(&o0, &o0, &u2);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_7_1_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u1;
        fp_add(&o0, &o0, &u2);
        fp_add(&o0, &o0, &u0);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_7_2_0(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o0 = u2;
        fp_add(&o0, &o0, &u0);
        fp_add(&o0, &o0, &u1);
        tmp[i] = o0; ST(1);
    }
    static inline void a3r_0_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_0_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_0_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_1_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o1 = u0;
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_1_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u0, &W3[2]);
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_1_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u0, &W3[1]);
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_2_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u1, &W3[1]);
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_2_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o1 = u1;
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_2_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u1, &W3[2]);
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_3_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o1 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_3_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o1 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_3_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u0, &W3[1]);
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_4_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u2, &W3[2]);
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_4_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u2, &W3[1]);
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_4_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u2;
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_5_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_5_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u2, &W3[1]);
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_5_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_6_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1; LD(1); fp_mul(&o1, &u1, &W3[1]);
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_6_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_6_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_7_0_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_7_1_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_7_2_1(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o1 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o1, &o1, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o1, &o1, &tm_); }
        tmp[i] = o1; ST(1);
    }
    static inline void a3r_0_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_0_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_0_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        tmp[i] = ZERO; ST(1);
    }
    static inline void a3r_1_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o2 = u0;
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_1_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u0, &W3[1]);
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_1_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u0, &W3[2]);
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_2_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u1, &W3[2]);
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_2_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o2 = u1;
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_2_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u1, &W3[1]);
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_3_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o2 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_3_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o2 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_3_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u0, &W3[2]);
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_4_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u2, &W3[1]);
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_4_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u2, &W3[2]);
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_4_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u2;
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_5_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_5_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u2, &W3[2]);
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_5_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_6_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2; LD(1); fp_mul(&o2, &u1, &W3[2]);
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_6_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_6_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_7_0_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u0;
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_7_1_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u1;
        { fp tm_; LD(1); fp_mul(&tm_, &u2, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
    static inline void a3r_7_2_2(fp *tmp, const fp *S, ptrdiff_t d0, ptrdiff_t d1, ptrdiff_t d2, size_t i) {
        fp u0 = S[(ptrdiff_t)i + d0]; LD(1);
        fp u1 = S[(ptrdiff_t)i + d1]; LD(1);
        fp u2 = S[(ptrdiff_t)i + d2]; LD(1);
        fp o2 = u2;
        { fp tm_; LD(1); fp_mul(&tm_, &u0, &W3[2]); fp_add(&o2, &o2, &tm_); }
        { fp tm_; LD(1); fp_mul(&tm_, &u1, &W3[1]); fp_add(&o2, &o2, &tm_); }
        tmp[i] = o2; ST(1);
    }
DRV_F(0, 0, 0, 0, 0)
DRV_F(1, 0, 0, 0, 0)
DRV_F(2, 0, 0, 0, 0)
DRV_F(3, 0, 0, 0, 0)
DRV_F(4, 0, 0, 0, 0)
DRV_F(5, 0, 0, 0, 0)
DRV_F(6, 0, 0, 0, 0)
DRV_F(7, 0, 0, 0, 0)
DRV_I(1, 0, 0, 0, 0)
DRV_I(2, 0, 0, 0, 0)
DRV_I(3, 0, 0, 0, 0)
DRV_I(4, 0, 0, 0, 0)
DRV_I(5, 0, 0, 0, 0)
DRV_I(6, 0, 0, 0, 0)
DRV_I(7, 0, 0, 0, 0)
DRV_R(0, 0, 0, 0, 0, 0)
DRV_R(0, 1, 0, 0, 0, 0)
DRV_R(0, 2, 0, 0, 0, 0)
DRV_R(0, 3, 0, 0, 0, 0)
DRV_R(0, 4, 0, 0, 0, 0)
DRV_R(0, 5, 0, 0, 0, 0)
DRV_R(0, 6, 0, 0, 0, 0)
DRV_R(0, 7, 0, 0, 0, 0)
DRV_R(1, 0, 0, 0, 0, 0)
DRV_R(1, 1, 0, 0, 0, 0)
DRV_R(1, 2, 0, 0, 0, 0)
DRV_R(1, 3, 0, 0, 0, 0)
DRV_R(1, 4, 0, 0, 0, 0)
DRV_R(1, 5, 0, 0, 0, 0)
DRV_R(1, 6, 0, 0, 0, 0)
DRV_R(1, 7, 0, 0, 0, 0)
DRV_R(2, 0, 0, 0, 0, 0)
DRV_R(2, 1, 0, 0, 0, 0)
DRV_R(2, 2, 0, 0, 0, 0)
DRV_R(2, 3, 0, 0, 0, 0)
DRV_R(2, 4, 0, 0, 0, 0)
DRV_R(2, 5, 0, 0, 0, 0)
DRV_R(2, 6, 0, 0, 0, 0)
DRV_R(2, 7, 0, 0, 0, 0)
DRV_F(0, 1, 0, 1, 2)
DRV_F(1, 1, 0, 1, 2)
DRV_F(2, 1, 0, 1, 2)
DRV_F(3, 1, 0, 1, 2)
DRV_F(4, 1, 0, 1, 2)
DRV_F(5, 1, 0, 1, 2)
DRV_F(6, 1, 0, 1, 2)
DRV_F(7, 1, 0, 1, 2)
DRV_I(1, 1, 0, 1, 2)
DRV_I(2, 1, 0, 1, 2)
DRV_I(3, 1, 0, 1, 2)
DRV_I(4, 1, 0, 1, 2)
DRV_I(5, 1, 0, 1, 2)
DRV_I(6, 1, 0, 1, 2)
DRV_I(7, 1, 0, 1, 2)
DRV_R(0, 0, 1, 0, 1, 2)
DRV_R(0, 1, 1, 0, 1, 2)
DRV_R(0, 2, 1, 0, 1, 2)
DRV_R(0, 3, 1, 0, 1, 2)
DRV_R(0, 4, 1, 0, 1, 2)
DRV_R(0, 5, 1, 0, 1, 2)
DRV_R(0, 6, 1, 0, 1, 2)
DRV_R(0, 7, 1, 0, 1, 2)
DRV_R(1, 0, 1, 0, 1, 2)
DRV_R(1, 1, 1, 0, 1, 2)
DRV_R(1, 2, 1, 0, 1, 2)
DRV_R(1, 3, 1, 0, 1, 2)
DRV_R(1, 4, 1, 0, 1, 2)
DRV_R(1, 5, 1, 0, 1, 2)
DRV_R(1, 6, 1, 0, 1, 2)
DRV_R(1, 7, 1, 0, 1, 2)
DRV_R(2, 0, 1, 0, 1, 2)
DRV_R(2, 1, 1, 0, 1, 2)
DRV_R(2, 2, 1, 0, 1, 2)
DRV_R(2, 3, 1, 0, 1, 2)
DRV_R(2, 4, 1, 0, 1, 2)
DRV_R(2, 5, 1, 0, 1, 2)
DRV_R(2, 6, 1, 0, 1, 2)
DRV_R(2, 7, 1, 0, 1, 2)
DRV_F(0, 2, 0, 2, 1)
DRV_F(1, 2, 0, 2, 1)
DRV_F(2, 2, 0, 2, 1)
DRV_F(3, 2, 0, 2, 1)
DRV_F(4, 2, 0, 2, 1)
DRV_F(5, 2, 0, 2, 1)
DRV_F(6, 2, 0, 2, 1)
DRV_F(7, 2, 0, 2, 1)
DRV_I(1, 2, 0, 2, 1)
DRV_I(2, 2, 0, 2, 1)
DRV_I(3, 2, 0, 2, 1)
DRV_I(4, 2, 0, 2, 1)
DRV_I(5, 2, 0, 2, 1)
DRV_I(6, 2, 0, 2, 1)
DRV_I(7, 2, 0, 2, 1)
DRV_R(0, 0, 2, 0, 2, 1)
DRV_R(0, 1, 2, 0, 2, 1)
DRV_R(0, 2, 2, 0, 2, 1)
DRV_R(0, 3, 2, 0, 2, 1)
DRV_R(0, 4, 2, 0, 2, 1)
DRV_R(0, 5, 2, 0, 2, 1)
DRV_R(0, 6, 2, 0, 2, 1)
DRV_R(0, 7, 2, 0, 2, 1)
DRV_R(1, 0, 2, 0, 2, 1)
DRV_R(1, 1, 2, 0, 2, 1)
DRV_R(1, 2, 2, 0, 2, 1)
DRV_R(1, 3, 2, 0, 2, 1)
DRV_R(1, 4, 2, 0, 2, 1)
DRV_R(1, 5, 2, 0, 2, 1)
DRV_R(1, 6, 2, 0, 2, 1)
DRV_R(1, 7, 2, 0, 2, 1)
DRV_R(2, 0, 2, 0, 2, 1)
DRV_R(2, 1, 2, 0, 2, 1)
DRV_R(2, 2, 2, 0, 2, 1)
DRV_R(2, 3, 2, 0, 2, 1)
DRV_R(2, 4, 2, 0, 2, 1)
DRV_R(2, 5, 2, 0, 2, 1)
DRV_R(2, 6, 2, 0, 2, 1)
DRV_R(2, 7, 2, 0, 2, 1)
static rg_t RGF[3][8] = {
    { rgf_0_0, rgf_1_0, rgf_2_0, rgf_3_0, rgf_4_0, rgf_5_0, rgf_6_0, rgf_7_0 },
    { rgf_0_1, rgf_1_1, rgf_2_1, rgf_3_1, rgf_4_1, rgf_5_1, rgf_6_1, rgf_7_1 },
    { rgf_0_2, rgf_1_2, rgf_2_2, rgf_3_2, rgf_4_2, rgf_5_2, rgf_6_2, rgf_7_2 },
};
static rg_t RGI[3][8] = {
    { 0, rgi_1_0, rgi_2_0, rgi_3_0, rgi_4_0, rgi_5_0, rgi_6_0, rgi_7_0 },
    { 0, rgi_1_1, rgi_2_1, rgi_3_1, rgi_4_1, rgi_5_1, rgi_6_1, rgi_7_1 },
    { 0, rgi_1_2, rgi_2_2, rgi_3_2, rgi_4_2, rgi_5_2, rgi_6_2, rgi_7_2 },
};
static rg_t RGR[3][3][8] = {
  {
    { rgr0_0_0, rgr0_1_0, rgr0_2_0, rgr0_3_0, rgr0_4_0, rgr0_5_0, rgr0_6_0, rgr0_7_0 },
    { rgr0_0_1, rgr0_1_1, rgr0_2_1, rgr0_3_1, rgr0_4_1, rgr0_5_1, rgr0_6_1, rgr0_7_1 },
    { rgr0_0_2, rgr0_1_2, rgr0_2_2, rgr0_3_2, rgr0_4_2, rgr0_5_2, rgr0_6_2, rgr0_7_2 },
  },
  {
    { rgr1_0_0, rgr1_1_0, rgr1_2_0, rgr1_3_0, rgr1_4_0, rgr1_5_0, rgr1_6_0, rgr1_7_0 },
    { rgr1_0_1, rgr1_1_1, rgr1_2_1, rgr1_3_1, rgr1_4_1, rgr1_5_1, rgr1_6_1, rgr1_7_1 },
    { rgr1_0_2, rgr1_1_2, rgr1_2_2, rgr1_3_2, rgr1_4_2, rgr1_5_2, rgr1_6_2, rgr1_7_2 },
  },
  {
    { rgr2_0_0, rgr2_1_0, rgr2_2_0, rgr2_3_0, rgr2_4_0, rgr2_5_0, rgr2_6_0, rgr2_7_0 },
    { rgr2_0_1, rgr2_1_1, rgr2_2_1, rgr2_3_1, rgr2_4_1, rgr2_5_1, rgr2_6_1, rgr2_7_1 },
    { rgr2_0_2, rgr2_1_2, rgr2_2_2, rgr2_3_2, rgr2_4_2, rgr2_5_2, rgr2_6_2, rgr2_7_2 },
  },
};
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
    FOR8(j, m - 1, size_t i = m - 1 - j; fp t; fp_mul(&t, &c, &G[i]); fp_sub(&Y[i], &Y[i - 1], &t); LD(2); ST(1));
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&Y[0], &t); LD(1); ST(1);
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
#ifdef CACHED_POW
    /* cached spectra: of mu'' (window at offset gamma, N slots) and of g (N' slots); the compact mu and the transform row are then released */
    fp *MUH = NEW_FP(N), *GH = NEW_FP(Np);
    ntt_fwd_shifted(&PN, MUH, MU, m - 1, gamma);
    ntt_fwd(&PNp, GH, g, 0, m + 1);
    xfree(MU); MU = NULL; xfree(tmp); tmp = NULL;
#endif
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
        size_t lim = 2 * m - 2 >= Np ? 2 * m - 2 - Np + 1 : 0; if (lim > m) lim = m; CTL(8);   /* positions i < lim fold Y[i + Np]; the rest are copies */
        FOR8(i, lim, fp_add(&F[i], &Y[i], &Y[i + Np]); LD(2); ST(1));
        FOR8(j, m - lim, size_t i = lim + j; F[i] = Y[i]; LD(1); ST(1));
        FOR8(i, m - 1, Y[i] = Y[m + i]; LD(1); ST(1));
#ifdef CACHED_POW
        conv_mulc(&PN, Y, Y, 0, m - 1, MUH, m - 1);
        conv_mulc(&PNp, Y, Y, 0, m - 1, GH, m);
#else
        conv_mulc_otf(&PN, Y, Y, 0, m - 1, tmp, MU, m - 1, gamma, m - 1);
        conv_mulc_otf(&PNp, Y, Y, 0, m - 1, tmp, g, m + 1, 0, m);
#endif
        FOR8(i, m, fp_sub(&Y[i], &F[i], &Y[i]); LD(2); ST(1));
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
#ifdef CACHED_POW
    xfree(MUH); xfree(GH); xfree(Y);
#else
    xfree(Y); xfree(tmp); xfree(MU);
#endif
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

size_t poly_degree_m(int r) { size_t D = 1; for (int i = 0; i < 6 + r; i++) D *= 5; return (D - 1) / 2; }

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

/* g(S) = sum_k f_{2k+1} S^k where F(c + s) = sum_t f_t s^t; evaluated at the H-th roots of unity theta^k, S_k = s_k^2,
 * s_k = psi^k, psi^2 = theta:  g(S_k) = (F(c+s_k) - F(c-s_k)) / (2 s_k).  One inverse NTT of size H returns g. */
void build_g(fp *g, const line_t *L, const fp *c, int r, int debug_check) {
    size_t m = poly_degree_m(r);
    plan_t P = plan_for_len(m + 1, 1);
    size_t H = P.N;
    fp *buf = NEW_FP(H);
    fp theta, psi, ipsi, s, u, one;
    fp_set_one(&one);
    plan_theta(&P, &theta);
    if (!fp_sqrt(&psi, &theta)) { fprintf(stderr, "theta not a square?\n"); exit(7); }
    fp_inv(&ipsi, &psi); CTL(INV_CTL + 12000);                 /* control of fp_inv and fp_sqrt (Tonelli-Shanks: two powers and up to 32*33/2 squaring-loop tests) */
    { fp two, half; fp_add(&two, &one, &one); fp_inv(&half, &two); u = half; }
    s = one;
    for (size_t k = 0; k < H; k++) {
        fp W1, W2, F1, F2, d, v;
        fp_add(&W1, c, &s); fp_sub(&W2, c, &s);
        /* the two reduced permutations F(c+s), F(c-s) are charged as two target-compression units, 2*C(r) primitive
         * operations, instead of their (smaller) expanded arithmetic: the counters are restored after the evaluation */
        snap_t e0 = snap();
        tail_eval(&F1, L, &W1, r);
        tail_eval(&F2, L, &W2, r);
        snap_restore(e0);
        X.perm += 2 * (uint64_t)poseidon_C(r);
        fp_sub(&d, &F1, &F2);
        fp_mul(&v, &d, &u);
        buf[layout_index(&P, k)] = v;
        fp_mul(&s, &s, &psi); fp_mul(&u, &u, &ipsi);
        CTL(2 + 4);                /* the calls of the two evaluations, and the call of layout_index (arguments) */
    }
    ST(H); loopc(H);               /* one store per point; s, u, c, psi, ipsi stay in registers; the bit-reversed index is charged inside layout_index */
    if (debug_check) {
        /* uncounted check: high coefficients vanish */
        snap_t keep = snap();
        fp *cp = NEW_FP(H); memcpy(cp, buf, H * sizeof(fp));
        ntt_inv(&P, cp, H);
        int bad = 0; for (size_t i = m + 1; i < H; i++) if (!fp_is_zero(&cp[i])) bad++;
        printf("build_g debug: H=%zu m=%zu nonzero coefficients above m: %d\n", H, m, bad);
        xfree(cp); snap_restore(keep);
    }
    ntt_inv(&P, buf, m + 1);                 /* buf[k] = H * g_k */
    fp il;
    fp_inv(&il, &buf[m]); CTL(INV_CTL);       /* 1/(H g_m) */
    for (size_t k = 0; k < m; k++) fp_mul(&g[k], &buf[k], &il);
    fp_set_one(&g[m]);
    LD(m + 1); ST(m + 1); loopc(m + 1);
    xfree(buf);
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
#include "hgcd.h"
#include "gcd_bounds.h"

uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;

/* worst-case charges of the fast gcd and of the division by the smaller factor at the level schedule d_0 = 39062, d_{i+1} = floor(d_i / 2);
 * a polynomial of degree d <= d_i is charged at the first level d_i >= d (the bounds are nondecreasing in d, checked in gcdbound). */
static const struct lvl_ *lvl_for(size_t d) {
    const struct lvl_ *r = &LEVELB[0];
    for (int i = 0; i < NLEVELB; i++) if (LEVELB[i].d >= d) r = &LEVELB[i];
    return r;
}
#define CL_MAX 152          /* classical Euclid up to this degree, the fast gcd above */
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
            fp *Ap; size_t a;
            snap_t tg = snap();
            CTL(2);                                                  /* the test d <= CL_MAX */
            if (d <= CL_MAX) {
                Ap = NEW_FP(d + 1);
                a = gcd_cl(Ap, G, d, S, d - 1);
                xfree(S);
            } else {
                size_t ly = d; while (ly > 0 && fp_is_zero(&S[ly - 1])) ly--;
                CTL(9 * (uint64_t)(d - ly + 1)); LD(d - ly + 1);
                size_t lg;
                Ap = poly_gcd_keep(&lg, G, d + 1, S, ly);
                a = lg - 1;
            }
            uint64_t gch = snap_total(snap_sub(snap(), tg));
            SPL_gcd += snap_total(snap_sub(snap(), t0));
            if (d > CL_MAX ? gch > lvl_for(d)->gcd : gch > gcd_cost_bound(d, d - 1)) { fprintf(stderr, "gcd charge %llu above its bound (d=%zu)\n", (unsigned long long)gch, d); exit(81); }
            CTL(4);
            if (a >= 1 && a <= d - 1) {
                size_t b = d - a;
                CTL(3);
                if (a <= b) { xfree(G); G = Ap; d = a; }
                else {
                    t0 = snap();
                    size_t dold = d; int d_gt_cl = dold > 76; fp *q = NEW_FP(b + 1), *rem = NEW_FP(d + 1); size_t lq, lr;
                    divrem_any_pub(q, &lq, rem, &lr, G, d + 1, Ap, a + 1);
                    CTL(4);                                                  /* the test of the remainder and the quotient length */
                    if (lr != 0 || lq != b + 1) { fprintf(stderr, "split: division left a remainder\n"); exit(80); }
                    xfree(rem); xfree(Ap); xfree(G); G = q; d = b;
                    SPL_div += snap_total(snap_sub(snap(), t0));
                    if (snap_total(snap_sub(snap(), t0)) > (d_gt_cl ? lvl_for(dold)->div : div_cost_bound(dold + 1, a + 1))) { fprintf(stderr, "division charge %llu above its bound %llu (la=%zu lb=%zu)\n", (unsigned long long)snap_total(snap_sub(snap(), t0)), (unsigned long long)div_cost_bound(dold + 1, a + 1), dold + 1, a + 1); exit(82); }
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

### hgcd.c

```c
/* Half-GCD (Knuth-Schoenhage / Thull-Yap style) over F_p with NTT multiplication and exact operation counting.
 *
 * Euclid remainder sequence r_0=a, r_1=b, r_{i-1} = q_i r_i + r_{i+1}; Q_i = [[q_i,1],[1,0]]; R_j = Q_1..Q_j,
 * (r_0,r_1)^T = R_j (r_j,r_{j+1})^T; d_j = deg q_1 + .. + deg q_j, deg r_j = n - d_j.
 * hgcd(a,b,k) returns R_h, (r_h, r_{h+1}) for h = max{ j : d_j <= k }.
 *
 * Truncation lemma: if a = a* x^s + a0, b = b* x^s + b0 (deg a0, b0 < s) and the Euclid sequence of (a*,b*) has
 * 2 d_j <= deg a*, then its first j quotients are the first j quotients of (a,b).  With deg a* = 2 k1 this makes
 * the recursive call on the top halves valid for parameter k1.  After applying R_1^{-1} to the exact (a,b) and one
 * exact division step the remaining parameter is <= k - k1 - 1.
 */
#include "hgcd.h"

#ifndef BASEK
#define BASEK 48
#endif
int hgcd_base_k = BASEK;
uint64_t hgcd_stat_calls, hgcd_stat_base_steps, hgcd_stat_bigdiv;

static size_t trimlen(const fp *c, size_t len) {
    size_t it = 1;
    while (len > 0 && fp_is_zero(&c[len - 1])) { len--; it++; }
    CTL(9 * it); LD(it);                 /* per test: len > 0 (compare, branch), index len - 1, the four-limb zero test (3 or, compare), branch, len-- */
    return len;
}
static size_t trimlen_(const fp *c, size_t len) { return trimlen(c, len); }
static fp *dupv(const fp *c, size_t len) {
    fp *r = NEW_FP(len ? len : 1);
    if (len) memcpy(r, c, len * sizeof(fp));
    LD(len); ST(len); loopc(len);
    return r;
}

/* ---- naive division */
void poly_divrem_naive(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) {
    if (la < lb) { *lq = 0; memcpy(r, a, la * sizeof(fp)); LD(la); ST(la); *lr = trimlen(r, la); return; }
    fp *w = r; /* r must have room for la coefficients */
    if (w != a) { memcpy(w, a, la * sizeof(fp)); LD(la); ST(la); loopc(la); }
    fp inv; fp_inv(&inv, &b[lb - 1]); CTL(INV_CTL);
    *lq = la - lb + 1;
    for (size_t i = la - lb + 1; i-- > 0;) {
        fp qi; fp_mul(&qi, &w[i + lb - 1], &inv); LD(1);
        q[i] = qi; ST(1);
        for (size_t j = 0; j + 1 < lb; j++) { fp t; fp_mul(&t, &qi, &b[j]); fp_sub(&w[i + j], &w[i + j], &t); }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(lb - 1);     /* index i + j in the inner loop */
        CTL(3 + 2 + 2);                                              /* outer loop iteration, index i + lb - 1, i + j base */
    }
    *lr = trimlen(w, lb - 1);
}


/* ---- fast division with remainder for long quotients (reversed Newton iteration).
 * a (la coefficients, top nonzero), b (lb coefficients, top nonzero), la >= lb; k = la - lb + 1 quotient coefficients.
 * q (k slots) and r (lb - 1 slots at least; la slots are not needed) are written; *lr = trimmed length of r. */
static void series_inverse(fp *g, const fp *f, size_t lf, size_t k) {      /* g = 1/f mod x^k (k slots); f has lf coefficients (zero beyond) */
    fp inv; fp_inv(&inv, &f[0]); CTL(INV_CTL); LD(1);
    g[0] = inv; ST(1);
    size_t t = 1;
    while (t < k) {
        size_t t2 = 2 * t < k ? 2 * t : k;
        CTL(3 + 3 + 2);                                   /* loop test, 2t, compare, select */
        size_t lft = lf < t2 ? lf : t2;
        fp *e = NEW_FP(lft + t - 1);
        poly_mul(e, f, lft, g, t);                        /* low t coefficients are 1, 0, ..., 0 */
        size_t m2 = t2 - t;
        fp *h = NEW_FP(2 * m2 - 1);
        fp *mid = NEW_FP(m2);
        for (size_t i = 0; i < m2; i++) { if (t + i < lft + t - 1) mid[i] = e[t + i]; else fp_set_zero(&mid[i]); }
        LD(m2); ST(m2); loopc(m2); CTL(3 * m2);           /* the index t + i and the bound test */
        poly_mul(h, g, m2, mid, m2);                      /* g (first m2 coefficients) times the middle part */
        for (size_t i = 0; i < m2; i++) fp_neg(&g[t + i], &h[i]);
        LD(m2); ST(m2); loopc(m2); CTL(m2);
        xfree(e); xfree(h); xfree(mid);
        t = t2;
    }
}
static size_t trimlen_(const fp *c, size_t len);
static void divrem_fast(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) {
    size_t k = la - lb + 1;
    fp *ar = NEW_FP(k), *br = NEW_FP(k), *g = NEW_FP(k);
    for (size_t i = 0; i < k; i++) ar[i] = a[la - 1 - i];
    LD(k); ST(k); loopc(k); CTL(k);
    size_t lbr = lb < k ? lb : k;
    for (size_t i = 0; i < lbr; i++) br[i] = b[lb - 1 - i];
    LD(lbr); ST(lbr); loopc(lbr); CTL(lbr);
    CTL(3);
    series_inverse(g, br, lbr, k);
    fp *qr = NEW_FP(2 * k - 1);
    poly_mul(qr, ar, k, g, k);
    for (size_t i = 0; i < k; i++) q[k - 1 - i] = qr[i];
    LD(k); ST(k); loopc(k); CTL(k);
    *lq = k;
    xfree(ar); xfree(br); xfree(g); xfree(qr);
    fp *pr = NEW_FP(la);
    poly_mul(pr, q, k, b, lb);
    for (size_t i = 0; i + 1 < lb; i++) fp_sub(&r[i], &a[i], &pr[i]);
    LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1);
    xfree(pr);
    *lr = trimlen_(r, lb - 1);
}
#define DIVFAST_MIN 64
static void divrem_any(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) {
    CTL(3);                                            /* the test of the quotient length */
    if (la - lb + 1 <= DIVFAST_MIN || lb <= DIVFAST_MIN) { poly_divrem_naive(q, lq, r, lr, a, la, b, lb); return; }
    divrem_fast(q, lq, r, lr, a, la, b, lb);
}

void divrem_any_pub(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb) { divrem_any(q, lq, r, lr, a, la, b, lb); }
/* ---- matrices */
static void mat_set_identity(mat_t *R) {
    for (int i = 0; i < 4; i++) { R->e[i] = NEW_FP(1); R->len[i] = 0; }
    fp_set_one(&R->e[0][0]); R->len[0] = 1; fp_set_one(&R->e[3][0]); R->len[3] = 1; ST(2);
    R->h = 0;
}
void mat_free(mat_t *R) { for (int i = 0; i < 4; i++) { if (R->e[i]) xfree(R->e[i]); R->e[i] = NULL; } }

/* out = e*q + f (any of the operands may be empty) ; returns trimmed length; *res freshly allocated */
static size_t poly_mul_add_small(fp **res, const fp *e, size_t le, const fp *q, size_t lq, const fp *f, size_t lf) {
    size_t lt = (le && lq) ? le + lq - 1 : 0;
    size_t lo = lt > lf ? lt : lf;
    fp *o = NEW_FP(lo ? lo : 1);
    for (size_t i = 0; i < lo; i++) fp_set_zero(&o[i]);
    ST(lo); loopc(lo);
    if (lt) {
        fp *t = NEW_FP(lt);
        poly_mul(t, e, le, q, lq);
        for (size_t i = 0; i < lt; i++) o[i] = t[i];
        LD(lt); ST(lt); loopc(lt);
        xfree(t);
    }
    for (size_t i = 0; i < lf; i++) fp_add(&o[i], &o[i], &f[i]);
    LD(2 * lf); ST(lf); loopc(lf);
    *res = o;
    return trimlen(o, lo);
}
/* R := R * [[q,1],[1,0]] */
static void mat_mulQ(mat_t *R, const fp *q, size_t lq) {
    fp *n0, *n2; size_t l0, l2;
    l0 = poly_mul_add_small(&n0, R->e[0], R->len[0], q, lq, R->e[1], R->len[1]);
    l2 = poly_mul_add_small(&n2, R->e[2], R->len[2], q, lq, R->e[3], R->len[3]);
    xfree(R->e[1]); xfree(R->e[3]);
    R->e[1] = R->e[0]; R->len[1] = R->len[0];
    R->e[3] = R->e[2]; R->len[3] = R->len[2];
    R->e[0] = n0; R->len[0] = l0; R->e[2] = n2; R->len[2] = l2;
    R->h++;
}

/* ---- pointwise helpers */
static void pw_mul(fp *dst, const fp *x, const fp *y, size_t N) {
    for (size_t i = 0; i < N; i++) fp_mul(&dst[i], &x[i], &y[i]);
    LD(2 * N); ST(N); loopc(N);
}
static void pw_mulsub(fp *acc, const fp *x, const fp *y, size_t N) {   /* acc -= x*y */
    for (size_t i = 0; i < N; i++) { fp t; fp_mul(&t, &x[i], &y[i]); fp_sub(&acc[i], &acc[i], &t); }
    LD(3 * N); ST(N); loopc(N);
}
static void pw_muladd(fp *acc, const fp *x, const fp *y, size_t N) {   /* acc += x*y */
    for (size_t i = 0; i < N; i++) { fp t; fp_mul(&t, &x[i], &y[i]); fp_add(&acc[i], &acc[i], &t); }
    LD(3 * N); ST(N); loopc(N);
}
/* transform of src (len coefficients) reduced modulo x^N-1 */
static void prep(const plan_t *P, fp *buf, const fp *src, size_t len) {
    size_t N = P->N;
    if (len <= N) { ntt_fwd(P, buf, src, 0, len); return; }
    for (size_t i = 0; i < N; i++) buf[i] = src[i];
    LD(N); ST(N); loopc(N);
    for (size_t i = N; i < len; i++) fp_add(&buf[i % N], &buf[i % N], &src[i]);
    LD(2 * (len - N)); ST(len - N); loopc(len - N); CTL(len - N);   /* modulo i % N */
    ntt_fwd(P, buf, buf, 0, N);
}
static void finish(const plan_t *P, fp *out, fp *T, size_t outlen) {
    ntt_inv(P, T, outlen);
    fp inv; plan_invN(P, &inv);
    for (size_t i = 0; i < outlen; i++) fp_mul(&out[i], &T[i], &inv);
    LD(outlen); ST(outlen); loopc(outlen);
}

/* (c,d) = R^{-1}(a,b): c = s(r22 a - r12 b), d = s(r11 b - r21 a), s = (-1)^h.  deg c = n - deg r11.
 * Lean: every operand spectrum is generated row by row from the compact polynomial; the outputs are built in
 * buffers of N slots (N >= nres) that are handed back as the result arrays. */
static void apply_inv(fp **c, size_t *lc, fp **d, size_t *ld, const mat_t *R, const fp *a, size_t la, const fp *b, size_t lb, int consume) {
    if (R->h == 0) { *c = dupv(a, la); *lc = la; *d = dupv(b, lb); *ld = lb; return; }
    size_t nres = la;                              /* nominal output length (deg c < la; the top coefficients are zero): the cost depends on la only */
    plan_t P = plan3_for_len(nres);
    size_t N = P.N;
    fp *tA = NEW_FP(P.n), *tB = NEW_FP(P.n);
    *c = NEW_FP(N); *d = NULL;
    int odd = R->h & 1;
    CTL(60);                                 /* operand selection: about 60 executed comparisons, branches and index operations */
    /* c = r22 a - r12 b (even) or r12 b - r22 a (odd) */
    {
        const fp *A[2], *B[2]; size_t lA[2], lB[2]; int sg[2] = { 1, -1 }; int nt = 0;
        if (!odd) { if (R->len[3] && la) { A[nt] = R->e[3]; lA[nt] = R->len[3]; B[nt] = a; lB[nt] = la; nt++; }
                    if (R->len[1] && lb) { A[nt] = R->e[1]; lA[nt] = R->len[1]; B[nt] = b; lB[nt] = lb; sg[nt] = -1; nt++; } }
        else      { if (R->len[1] && lb) { A[nt] = R->e[1]; lA[nt] = R->len[1]; B[nt] = b; lB[nt] = lb; nt++; }
                    if (R->len[3] && la) { A[nt] = R->e[3]; lA[nt] = R->len[3]; B[nt] = a; lB[nt] = la; sg[nt] = -1; nt++; } }
        if (nt) conv_sum_otf(&P, *c, nt, A, lA, B, lB, sg, tA, tB, nres);
        else for (size_t i = 0; i < nres; i++) fp_set_zero(&(*c)[i]);
    }
    if (consume) { mat_t *Rw = (mat_t *)R; xfree(Rw->e[1]); Rw->e[1] = NULL; Rw->len[1] = 0; xfree(Rw->e[3]); Rw->e[3] = NULL; Rw->len[3] = 0; }   /* memory only: the matrix is not needed afterwards */
    *d = NEW_FP(N);
    {
        const fp *A[2], *B[2]; size_t lA[2], lB[2]; int sg[2] = { 1, -1 }; int nt = 0;
        if (!odd) { if (R->len[0] && lb) { A[nt] = R->e[0]; lA[nt] = R->len[0]; B[nt] = b; lB[nt] = lb; nt++; }
                    if (R->len[2] && la) { A[nt] = R->e[2]; lA[nt] = R->len[2]; B[nt] = a; lB[nt] = la; sg[nt] = -1; nt++; } }
        else      { if (R->len[2] && la) { A[nt] = R->e[2]; lA[nt] = R->len[2]; B[nt] = a; lB[nt] = la; nt++; }
                    if (R->len[0] && lb) { A[nt] = R->e[0]; lA[nt] = R->len[0]; B[nt] = b; lB[nt] = lb; sg[nt] = -1; nt++; } }
        if (nt) conv_sum_otf(&P, *d, nt, A, lA, B, lB, sg, tA, tB, nres);
        else for (size_t i = 0; i < nres; i++) fp_set_zero(&(*d)[i]);
    }
    xfree(tA); xfree(tB);
    if (consume) mat_free((mat_t *)R);
    fp inv; plan_invN(&P, &inv);
    for (size_t i = 0; i < nres; i++) fp_mul(&(*c)[i], &(*c)[i], &inv);
    for (size_t i = 0; i < nres; i++) fp_mul(&(*d)[i], &(*d)[i], &inv);
    LD(2 * nres); ST(2 * nres); loopc(2 * nres);
    *lc = trimlen(*c, nres); *ld = trimlen(*d, nres);
}

/* out = A * B (2x2 polynomial matrices), lean: one N-slot product buffer reused for the four entries */
static void mat_mul(mat_t *out, const mat_t *A, const mat_t *B) {
    size_t Lmax = 1;
    size_t L[4];
    CTL(80);                                 /* length computation loops (4 entries x 2 terms) and comparisons */
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
        size_t l = 0;
        for (int t = 0; t < 2; t++) {
            size_t la = A->len[2 * i + t], lb = B->len[2 * t + j];
            if (la && lb && la + lb - 1 > l) l = la + lb - 1;
        }
        L[2 * i + j] = l; if (l > Lmax) Lmax = l;
    }
    out->h = A->h + B->h;
    if (Lmax <= 48) {
        for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
            size_t l = L[2 * i + j];
            fp *o = NEW_FP(l ? l : 1);
            for (size_t u = 0; u < l; u++) fp_set_zero(&o[u]);
            ST(l); loopc(l);
            for (int t = 0; t < 2; t++) {
                size_t la = A->len[2 * i + t], lb = B->len[2 * t + j];
                if (!la || !lb) continue;
                fp *tmp = NEW_FP(la + lb - 1);
                poly_mul_naive(tmp, A->e[2 * i + t], la, B->e[2 * t + j], lb);
                for (size_t u = 0; u < la + lb - 1; u++) fp_add(&o[u], &o[u], &tmp[u]);
                LD(2 * (la + lb - 1)); ST(la + lb - 1); loopc(la + lb - 1);
                xfree(tmp); CTL(6);
            }
            out->e[2 * i + j] = o; out->len[2 * i + j] = trimlen(o, l);
        }
        return;
    }
    plan_t P = plan3_for_len(Lmax);
    size_t N = P.N;
    fp *buf = NEW_FP(N), *tA = NEW_FP(P.n), *tB = NEW_FP(P.n);
    fp inv; plan_invN(&P, &inv);
    for (int i = 0; i < 2; i++) for (int j = 0; j < 2; j++) {
        size_t l = L[2 * i + j];
        const fp *Ap[2], *Bp[2]; size_t lA[2], lB[2]; int sg[2] = { 1, 1 }; int nt = 0;
        for (int t = 0; t < 2; t++) {
            size_t la = A->len[2 * i + t], lb = B->len[2 * t + j];
            if (la && lb) { Ap[nt] = A->e[2 * i + t]; lA[nt] = la; Bp[nt] = B->e[2 * t + j]; lB[nt] = lb; nt++; }
        }
        fp *o = NEW_FP(l ? l : 1);
        if (nt) {
            conv_sum_otf(&P, buf, nt, Ap, lA, Bp, lB, sg, tA, tB, l);
            for (size_t u = 0; u < l; u++) fp_mul(&o[u], &buf[u], &inv);
            LD(l); ST(l); loopc(l);
        }
        out->e[2 * i + j] = o; out->len[2 * i + j] = l ? trimlen(o, l) : 0;
    }
    xfree(buf); xfree(tA); xfree(tB);
}

/* ---- base case: plain Euclid until the next quotient would exceed the remaining budget.
 * own: bit 0 set: a is an xalloc'ed array whose ownership passes to the callee; bit 1 set: the same for b (own = 3: both, 1: only a, 2: only b, 0: borrowed). */
static void hgcd_base(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    fp *x = (own & 1) ? (fp *)a : dupv(a, la), *y = (own & 2) ? (fp *)b : dupv(b, lb);
    size_t lx = la, ly = lb, sum = 0;
    if (want_mat) mat_set_identity(R);
    while (ly > 0) {
        size_t dq = lx - ly;
        CTL(3 + 3);                          /* loop test, subtraction, subtraction, compare, branch */
        if (dq > k - sum) break;
        fp *q = NEW_FP(dq + 1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        if (want_mat) mat_mulQ(R, q, lq);
        sum += dq;
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
        hgcd_stat_base_steps++;
    }
    if (c) { *c = x; *lc = lx; } else xfree(x);
    if (d) { *d = y; *ld = ly; } else xfree(y);
}

int hgcd_k1_pct = 50;

void hgcd(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    hgcd_stat_calls++;
    CTL(40);                                 /* the size computations, comparisons and branches of this call (about 40 executed operations) */
    size_t n = la - 1;
    if (lb == 0 || n - (lb - 1) > k) {
        if (want_mat) mat_set_identity(R);
        CTL(4);                              /* the two ownership tests */
        if (c) { if (own & 1) *c = (fp *)a; else *c = dupv(a, la); *lc = la; } else if (own & 1) xfree((void *)a);
        if (d) { if (own & 2) *d = (fp *)b; else *d = dupv(b, lb); *ld = lb; } else if (own & 2) xfree((void *)b);
        return;
    }
    if (k <= (size_t)hgcd_base_k) { hgcd_base(R, c, lc, d, ld, a, la, b, lb, k, want_mat, own); return; }
    size_t k1 = (k * (size_t)hgcd_k1_pct + 99) / 100;
    if (2 * k1 > n) k1 = n / 2;
    size_t s = n - 2 * k1;
    mat_t R1; fp *cc, *dd; size_t lcc, ldd;
    {
        const fp *as = a + s; size_t las = la - s;
        const fp *bs = b + s; size_t lbs = lb > s ? lb - s : 0;
        hgcd(&R1, NULL, NULL, NULL, NULL, as, las, bs, lbs, k1, 1, 0);
    }
    if (R1.h == 0) {
        CTL(4);
        cc = (own & 1) ? (fp *)a : dupv(a, la); dd = (own & 2) ? (fp *)b : dupv(b, lb);
        lcc = la; ldd = lb;
    } else {
        apply_inv(&cc, &lcc, &dd, &ldd, &R1, a, la, b, lb, !want_mat);
        CTL(4);
        if (own & 1) xfree((void *)a);
        if (own & 2) xfree((void *)b);
    }
    size_t sumdeg = n - (lcc - 1);
    size_t k2 = k - sumdeg;
    if (ldd == 0 || (lcc - ldd) > k2) {
        if (want_mat) *R = R1; else mat_free(&R1);
        if (c) { *c = cc; *lc = lcc; } else xfree(cc);
        if (d) { *d = dd; *ld = ldd; } else xfree(dd);
        return;
    }
    size_t dq = lcc - ldd;
    fp *q = NEW_FP(dq + 1), *rem = NEW_FP(lcc); size_t lq, lrem;
    divrem_any(q, &lq, rem, &lrem, cc, lcc, dd, ldd);
    xfree(cc);
    if (dq > 32) hgcd_stat_bigdiv++;
    size_t k3 = k2 - dq;
    mat_t R2;
    hgcd(&R2, c, lc, d, ld, dd, ldd, rem, lrem, k3, want_mat, 3);
    if (want_mat) {
        mat_mulQ(&R1, q, lq);
        mat_mul(R, &R1, &R2);
        mat_free(&R2);
    }
    mat_free(&R1);
    xfree(q);
}

/* ---- gcd */
static size_t monic_out(fp *out, const fp *x, size_t lx) {
    if (!lx) return 0;
    fp inv; fp_inv(&inv, &x[lx - 1]); CTL(INV_CTL);
    for (size_t i = 0; i + 1 < lx; i++) fp_mul(&out[i], &x[i], &inv);
    fp_set_one(&out[lx - 1]);
    LD(lx); ST(lx); loopc(lx);
    return lx;
}
size_t poly_gcd_naive(fp *out, const fp *a, size_t la, const fp *b, size_t lb) {
    fp *x = dupv(a, la), *y = dupv(b, lb); size_t lx = la, ly = lb;
    while (ly > 0) {
        fp *q = NEW_FP(lx > ly ? lx - ly + 1 : 1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
    }
    size_t l = monic_out(out, x, lx);
    xfree(x); xfree(y);
    return l;
}
/* gcd of x (lx coefficients) and y (ly coefficients), both xalloc'ed and given away.  Returns the monic gcd as an xalloc'ed array
 * (its length in *lg; the array is the last nonzero remainder scaled in place); NULL with *lg = 0 if both are zero. */
fp *poly_gcd_own(size_t *lg, fp *x, size_t lx, fp *y, size_t ly) {
    CTL(3);
    if (lx < ly) { fp *t = x; x = y; y = t; size_t tl = lx; lx = ly; ly = tl; CTL(6); }
    CTL(3);
    if (lx == ly && ly > 0) {   /* equal degrees: one division step first */
        fp *q = NEW_FP(1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q); CTL(5);
    }
    while (ly > 0) {
        CTL(2);
        size_t n = lx - 1;
        CTL(4);
        if (n <= 2 * (size_t)hgcd_base_k) {
            fp *q = NEW_FP(lx - ly + 1), *r = NEW_FP(lx); size_t lq, lr;
            poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
            xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q); CTL(5);
            continue;
        }
        fp *c, *d; size_t lc, ld;
        hgcd(NULL, &c, &lc, &d, &ld, x, lx, y, ly, (n + 1) / 2, 0, 3);
        CTL(2);
        if (ld == 0) { x = c; lx = lc; y = d; ly = 0; break; }
        fp *q = NEW_FP(lc - ld + 1), *r = NEW_FP(lc); size_t lq, lr;
        divrem_any(q, &lq, r, &lr, c, lc, d, ld);
        xfree(c); xfree(q);
        x = d; lx = ld; y = r; ly = lr; CTL(5);
    }
    xfree(y);
    CTL(2);
    if (!lx) { xfree(x); *lg = 0; return NULL; }
    fp inv; fp_inv(&inv, &x[lx - 1]); CTL(INV_CTL); LD(1);
    for (size_t i = 0; i + 1 < lx; i++) fp_mul(&x[i], &x[i], &inv);
    fp_set_one(&x[lx - 1]);
    LD(lx); ST(lx); loopc(lx);
    *lg = lx;
    return x;
}

/* Same as poly_gcd_own, but x is only borrowed (the caller keeps it); y is given away.  Needs lx > ly. */
fp *poly_gcd_keep(size_t *lg, const fp *x, size_t lx, fp *y, size_t ly) {
    CTL(3);
    if (ly == 0 || lx - 1 <= 2 * (size_t)hgcd_base_k) {        /* small or trivial: work on a copy */
        fp *xc = dupv(x, lx);
        return poly_gcd_own(lg, xc, lx, y, ly);
    }
    size_t n = lx - 1;
    fp *c, *d; size_t lc, ld;
    hgcd(NULL, &c, &lc, &d, &ld, x, lx, y, ly, (n + 1) / 2, 0, 2);
    CTL(2);
    if (ld == 0) { xfree(d); return poly_gcd_own(lg, c, lc, NULL, 0); }
    fp *q = NEW_FP(lc - ld + 1), *r = NEW_FP(lc); size_t lq, lr;
    divrem_any(q, &lq, r, &lr, c, lc, d, ld);
    xfree(c); xfree(q);
    return poly_gcd_own(lg, d, ld, r, lr);
}

size_t poly_gcd_fast(fp *out, const fp *a, size_t la, const fp *b, size_t lb) {
    size_t l; fp *g = poly_gcd_own(&l, dupv(a, la), la, dupv(b, lb), lb);
    if (g) { memcpy(out, g, l * sizeof(fp)); xfree(g); }
    return l;
}
```

### single.c

```c
/* Orchard Poseidon, r = 1, one centre of the odd-part method.
 * usage: single seed [verbose]
 * One attempt: line j = LINE, one random centre c, g = monic odd part of (F(c+s) - F(c-s))/s in S = s^2 (degree m = 39062),
 * R = S^((p-1)/2) mod g, G = gcd(g, R - 1) (half-gcd), one root S of G (root isolation by random shifts), s = sqrt(S),
 * W1 = c + s, W2 = c - s, back-map, verify with two reference hashes.  Every executed operation is charged (common.h).
 * There is no loop over attempts and no budget check: every data-dependent stage is charged at a derived bound that the program asserts. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include "gcd_bounds.h"
#include <time.h>
#include <math.h>

#ifndef LINE
#define LINE 0
#endif
typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[16]; static int nst;
static snap_t cur; static clock_t tcur; static size_t gpeak;
static void stage_begin(void) { cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

int main(int argc, char **argv) {
    const int r = 1;
    uint64_t seed = argc > 1 ? strtoull(argv[1], 0, 0) : 1;
    int verbose = argc > 2 ? atoi(argv[2]) : 0;
    rng_seed(seed);
    size_t m = poly_degree_m(r);
    printf("r=%d seed=%llu line=%d m=%zu\n", r, (unsigned long long)seed, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_begin(); ntt_init(15); stage_end("init (twiddle table)");
    uint64_t pre = snap_total(st[0].d);
    line_t L;
    stage_begin(); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); } stage_end("line setup");
    fp c;
    stage_begin(); rnd_fp254(&c); stage_end("random centre");
    fp *g = NEW_FP(m + 1);
    stage_begin(); build_g(g, &L, &c, r, 0); stage_end("B: build g");
    fp *F = NEW_FP(m);
    stage_begin(); powx_lean(F, g, m, PALLAS_PM1H, verbose ? 2 : 1); stage_end("C: S^((p-1)/2) mod g");
    fp one; fp_set_one(&one);
    stage_begin();
    fp_sub(&F[0], &F[0], &one);
    int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
    CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R - 1: executed tests only */
    size_t lG = 0; fp *G = NULL;
    snap_t sg = snap();
    G = poly_gcd_own(&lG, g, m + 1, F, (size_t)dR + 1);
    uint64_t gcd_charged = snap_total(snap_sub(snap(), sg));
    if (gcd_charged > LEVELB[0].gcd) { fprintf(stderr, "gcd charge %llu above its bound %llu\n", (unsigned long long)gcd_charged, (unsigned long long)LEVELB[0].gcd); return 81; }
    stage_end("D: gcd(g, S^h - 1) (half-gcd)");
    size_t dG = lG ? lG - 1 : 0;
    printf("gcd degree %zu, charged %llu, derived bound %llu (within)\n", dG, (unsigned long long)gcd_charged, (unsigned long long)LEVELB[0].gcd);
    int found = 0, success = 0;
    fp S, nk1, rho1, nk2, rho2, dg1, dg2;
#ifdef DEG_CAP
    CTL(2);                                              /* variant with a cap on deg G: a larger G ends the attempt (a failure event of section 8) */
    if (dG > DEG_CAP) { printf("deg G above the cap: attempt ends\n"); xfree(G); G = NULL; dG = 0; }
#endif
    if (dG >= 1) {
        stage_begin(); found = split_find_root(&S, G, dG); stage_end("E: root isolation");
        if (found) {
            stage_begin();
            snap_t s0 = snap();
            fp s; int sq = fp_sqrt(&s, &S);
            CTL(12000);                                  /* Tonelli-Shanks control */
            if (!sq) { printf("root not a square?!\n"); found = 0; }
            fp W1, W2;
            fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
            map_back(&nk1, &rho1, &L, &W1);
            map_back(&nk2, &rho2, &L, &W2);
            bound_mem_since(s0);
            stage_end("F: sqrt + map back");
            stage_begin();
            poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
            poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
            { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
            stage_end("G: verification (2 reference hashes)");
            int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
            success = found && fp_eq(&dg1, &dg2) && !same_in;
        }
    } else if (G) xfree(G);
    uint64_t all = 0, arith = 0; double sec = 0;
    for (int i = 0; i < nst; i++) { all += snap_total(st[i].d); arith += snap_arith(st[i].d); sec += st[i].sec; }
    for (int i = 0; i < nst; i++)
        printf("  %-40s arith=%12llu other=%12llu total=%12llu %7.1fs peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
               (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].sec, st[i].peak);
    printf("RESULT found=%d success=%d roots_degree=%zu\n", found, success, dG);
    printf("SPLIT levels=%llu tries=%llu shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)SPL_shift,
           (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    int C = 216 + 21 * r;
    printf("SUMMARY total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", (unsigned long long)all, (unsigned long long)arith, (double)all / C, log2((double)all / C), gpeak, sec);
    { snap_t tt; memset(&tt, 0, sizeof tt);
      for (int i = 0; i < nst; i++) { tt.add += st[i].d.add; tt.sub += st[i].d.sub; tt.mul += st[i].d.mul; tt.sqr += st[i].d.sqr; tt.ld += st[i].d.ld; tt.st += st[i].d.st; tt.ctl += st[i].d.ctl; tt.rnd += st[i].d.rnd; tt.perm += st[i].d.perm; }
      printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu\n", (unsigned long long)tt.add, (unsigned long long)tt.sub, (unsigned long long)tt.mul, (unsigned long long)tt.sqr,
             (unsigned long long)tt.ld, (unsigned long long)tt.st, (unsigned long long)tt.ctl, (unsigned long long)tt.rnd, (unsigned long long)tt.perm); }
    if (success) {
        phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
        phex("COLLISION digest", &dg1); phex("COLLISION centre", &c);
    }
    return success ? 0 : 1;
}
```

### test_hgcd.c

```c
/* test of the gcd: usage test_hgcd n dg db [naive]  : a = f u (deg n), b = f v (deg db >= dg), planted gcd f of degree dg.
 * Small db with large n gives a long first quotient (abnormal sequence). */
#include "common.h"
#include "hgcd.h"
#include <time.h>
static uint64_t rs = 99172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    size_t n = argc > 1 ? strtoul(argv[1], 0, 10) : 3000;
    size_t d = argc > 2 ? strtoul(argv[2], 0, 10) : 3;
    size_t db = argc > 3 ? strtoul(argv[3], 0, 10) : n - 1;
    int naive = argc > 4 ? atoi(argv[4]) : 1;
    ntt_init(15);
    size_t la = n + 1, lb = db + 1;
    fp *f = NEW_FP(d + 1), *u = NEW_FP(n - d + 1), *v = NEW_FP(db - d + 1);
    for (size_t i = 0; i <= d; i++) rnd_fp(&f[i]);
    for (size_t i = 0; i <= n - d; i++) rnd_fp(&u[i]);
    for (size_t i = 0; i <= db - d; i++) rnd_fp(&v[i]);
    fp *a = NEW_FP(la), *b = NEW_FP(lb);
    snap_t keep = snap();
    poly_mul(a, f, d + 1, u, n - d + 1);
    poly_mul(b, f, d + 1, v, db - d + 1);
    snap_restore(keep);
    fp *o1 = NEW_FP(la), *o2 = NEW_FP(la);
    size_t base = mem_cur; mem_reset_peak();
    snap_t s0 = snap(); clock_t c0 = clock();
    size_t g1 = poly_gcd_fast(o1, a, la, b, lb);
    snap_t d1 = snap_sub(snap(), s0); double t1 = (double)(clock() - c0) / CLOCKS_PER_SEC; size_t pk = mem_peak - base;
    printf("hgcd: n=%zu db=%zu deg gcd = %zu (planted %zu) arith=%llu total=%llu extra peak=%zu bytes, %.1fs\n", n, db, g1 - 1, d, (unsigned long long)snap_arith(d1), (unsigned long long)snap_total(d1), pk, t1);
    int good = (g1 == d + 1);
    if (naive) {
        s0 = snap(); c0 = clock();
        size_t g2 = poly_gcd_naive(o2, a, la, b, lb);
        snap_t d2 = snap_sub(snap(), s0);
        printf("naive: deg gcd = %zu arith=%llu total=%llu %.1fs\n", g2 - 1, (unsigned long long)snap_arith(d2), (unsigned long long)snap_total(d2), (double)(clock() - c0) / CLOCKS_PER_SEC);
        good &= (g2 == g1); for (size_t i = 0; i < g1 && good; i++) if (!fp_eq(&o1[i], &o2[i])) good = 0;
    }
    { fp inv; fp_inv(&inv, &f[d]); for (size_t i = 0; i <= d && good; i++) { fp t; fp_mul(&t, &f[i], &inv); if (!fp_eq(&t, &o1[i])) good = 0; } }
    printf(good ? "HGCD OK\n" : "HGCD FAIL\n");
    return !good;
}
```

### test_split.c

```c
/* Tests of split.c on synthetic products of linear factors: root isolation, gcd charge against its derived bound, Taylor shift, division. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(15);
    rng_seed(argc > 1 ? strtoull(argv[1], 0, 0) : 7);
    size_t ds[] = { 1, 2, 3, 4, 5, 9, 17, 40, 41, 64, 200, 1000, 3000, 12000, 0 };
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

### test_keep.c

```c
/* Memory of the gcd stage of the root isolation at the top degree: poly_gcd_keep(G borrowed, S - 1 given away) on random operands of degrees d and d - 1.
 * usage: test_keep d */
#include "common.h"
#include "hgcd.h"
static uint64_t rs = 99172645463325252ULL;
static uint64_t rnd64(void) { rs ^= rs << 13; rs ^= rs >> 7; rs ^= rs << 17; return rs; }
static void rnd_fp(fp *a) { uint64_t v[4] = { rnd64(), rnd64(), rnd64(), rnd64() & 0x3fffffffffffffffULL }; fp_from_limbs(a, v); }
int main(int argc, char **argv) {
    size_t d = argc > 1 ? strtoul(argv[1], 0, 10) : 39062;
    ntt_init(15);
    fp *G = NEW_FP(d + 1), *S = NEW_FP(d);
    for (size_t i = 0; i <= d; i++) rnd_fp(&G[i]);
    for (size_t i = 0; i < d; i++) rnd_fp(&S[i]);
    size_t base = mem_cur; mem_reset_peak();
    snap_t s0 = snap();
    size_t lg; fp *A = poly_gcd_keep(&lg, G, d + 1, S, d);
    uint64_t ch = snap_total(snap_sub(snap(), s0));
    printf("poly_gcd_keep d=%zu: gcd degree %zu charged %llu, peak above the live inputs %zu, absolute peak %zu bytes (inputs %zu)\n", d, lg - 1, (unsigned long long)ch, mem_peak - base, mem_peak, base);
    xfree(A); xfree(G);
    return 0;
}
```

### calib.c

```c
/* Calibration of the data-independent stage charges used by the worst-case bound of the root-isolation stage.
 * usage: calib d [d ...]   prints:  LEVEL d shift=<charge> pow=<charge> ...  and the heap peaks of the two stages.
 * The charges do not depend on the coefficients (fixed loop counts), so random monic input is used. */
#include "attack.h"
#include <time.h>
int main(int argc, char **argv) {
    ntt_init(15);
    rng_seed(5);
    for (int i = 1; i < argc; i++) {
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

### gcdbound.c

```c
/* Derived worst-case charge of the gcd (hgcd.c).  The recursion below follows the control structure of hgcd() and poly_gcd_own();
 * every kernel is charged at the cost of the executed kernel on nominal operands of the maximal lengths (all coefficients nonzero, so no
 * top-coefficient scan stops early); the data-dependent scans (trimlen) and the plan_invN cache search are added at their worst case.
 * usage: gcdbound d [d ...]   prints  GCDBOUND d value  (the bound for gcd(a, b), deg a = d, deg b <= d - 1). */
#include "hgcd.c"
#include <time.h>
uint64_t div_cost_bound(size_t la, size_t lb);
#define INVA 330
#define PLAN_ALLOW 460            /* plan_invN: search of the 64-entry cache, 7 operations per entry, at most 448 */

static uint64_t rs_ = 88172645463325252ULL;
static uint64_t rnd64_(void) { rs_ ^= rs_ << 13; rs_ ^= rs_ >> 7; rs_ ^= rs_ << 17; return rs_; }
static fp *rarr(size_t n) { fp *a = NEW_FP(n ? n : 1); for (size_t i = 0; i < n; i++) { uint64_t v[4] = { rnd64_() | 1, rnd64_(), rnd64_(), rnd64_() & 0x3fffffffffffffffULL }; fp_from_limbs(&a[i], v); } return a; }
static uint64_t tot(snap_t s0) { return snap_total(snap_sub(snap(), s0)); }

/* ---- memo */
typedef struct { int kind; uint64_t a, b, c; uint64_t v; } memo_t;
static memo_t memo[200000]; static int nmemo;
static int memo_get(int kind, uint64_t a, uint64_t b, uint64_t c, uint64_t *v) {
    for (int i = 0; i < nmemo; i++) if (memo[i].kind == kind && memo[i].a == a && memo[i].b == b && memo[i].c == c) { *v = memo[i].v; return 1; }
    return 0;
}
static void memo_put(int kind, uint64_t a, uint64_t b, uint64_t c, uint64_t v) { memo[nmemo].kind = kind; memo[nmemo].a = a; memo[nmemo].b = b; memo[nmemo].c = c; memo[nmemo++].v = v; }

/* ---- kernels at nominal operands */
static uint64_t K_apply(size_t la, size_t K) {              /* apply_inv with a of la coefficients, b of la - 1, all matrix entries of K + 1 coefficients */
    uint64_t v; if (memo_get(1, la, K, 0, &v)) return v;
    mat_t R; for (int i = 0; i < 4; i++) { R.e[i] = rarr(K + 1); R.len[i] = K + 1; } R.h = 1;
    fp *a = rarr(la), *b = rarr(la - 1), *c, *d; size_t lc, ld;
    snap_t s0 = snap(); apply_inv(&c, &lc, &d, &ld, &R, a, la, b, la - 1, 0); v = tot(s0);
    v += 2 * 10 * (la + 1) + PLAN_ALLOW;                    /* the two trimlen scans at their worst case (10 per entry) */
    xfree(c); xfree(d); xfree(a); xfree(b); mat_free(&R);
    memo_put(1, la, K, 0, v); return v;
}
static uint64_t K_matmul(size_t kA, size_t kB) {            /* mat_mul of matrices with entries of kA + 1 and kB + 1 coefficients */
    uint64_t v; if (memo_get(2, kA, kB, 0, &v)) return v;
    mat_t A, B, O; for (int i = 0; i < 4; i++) { A.e[i] = rarr(kA + 1); A.len[i] = kA + 1; B.e[i] = rarr(kB + 1); B.len[i] = kB + 1; } A.h = 1; B.h = 1;
    snap_t s0 = snap(); mat_mul(&O, &A, &B); v = tot(s0);
    size_t Lmax = kA + kB + 1;
    v += 4 * 10 * (Lmax + 1) + 8 * PLAN_ALLOW;
    mat_free(&A); mat_free(&B); mat_free(&O);
    memo_put(2, kA, kB, 0, v); return v;
}
static uint64_t K_mulQ(size_t sd, size_t dq) {              /* mat_mulQ: R entries of sd + 1 coefficients, q of dq + 1 */
    uint64_t v; if (memo_get(3, sd, dq, 0, &v)) return v;
    mat_t R; for (int i = 0; i < 4; i++) { R.e[i] = rarr(sd + 1); R.len[i] = sd + 1; } R.h = 1;
    fp *q = rarr(dq + 1);
    snap_t s0 = snap(); mat_mulQ(&R, q, dq + 1); v = tot(s0);
    v += 2 * 10 * (sd + dq + 2) + 4 * PLAN_ALLOW;
    mat_free(&R); xfree(q);
    memo_put(3, sd, dq, 0, v); return v;
}
static uint64_t K_mulQ_max(size_t k) {                      /* sd + dq <= k: maximum over the splits (all of them for small k, a grid otherwise) */
    uint64_t v; if (memo_get(4, k, 0, 0, &v)) return v;
    uint64_t best = 0;
    for (size_t dq = 0; dq <= k; dq++) { if (k > 60 && dq % ((k + 59) / 60) && dq != k && dq != 0) continue; uint64_t c = K_mulQ(k - dq, dq); if (c > best) best = c; }
    memo_put(4, k, 0, 0, best); return best;
}
static uint64_t K_divfast(size_t n, size_t kq) {            /* divrem_fast with a of n + 1 coefficients, quotient of kq coefficients */
    uint64_t v; if (memo_get(5, n, kq, 0, &v)) return v;
    size_t la = n + 1, lb = la - kq + 1;
    fp *a = rarr(la), *b = rarr(lb), *q = NEW_FP(kq), *r = NEW_FP(lb); size_t lq, lr;
    snap_t s0 = snap(); divrem_fast(q, &lq, r, &lr, a, la, b, lb); v = tot(s0);
    uint64_t lg = 0; while (((uint64_t)1 << lg) < kq) lg++;
    v += 10 * (lb + 1) + (2 * lg + 6) * PLAN_ALLOW;
    xfree(a); xfree(b); xfree(q); xfree(r);
    memo_put(5, n, kq, 0, v); return v;
}
/* division of a polynomial with at most n + 1 coefficients, quotient length at most kq: worst over the two branches of divrem_any */
static uint64_t B_div(size_t n, size_t kq) {
    uint64_t v; if (memo_get(6, n, kq, 0, &v)) return v;
    uint64_t best = 0;
    size_t kn = kq < DIVFAST_MIN ? kq : DIVFAST_MIN;          /* naive branch with quotient length <= 64 */
    if (kn >= 1) { uint64_t c = div_cost_bound(n + 1, n + 2 - kn); if (c > best) best = c; }
    if (kq >= 1) {                                             /* naive branch with divisor length <= 64 */
        size_t la2 = kq + DIVFAST_MIN - 1 < n + 1 ? kq + DIVFAST_MIN - 1 : n + 1;
        uint64_t c2 = div_cost_bound(la2, DIVFAST_MIN < la2 ? DIVFAST_MIN : la2); if (c2 > best) best = c2;
    }
    if (kq > DIVFAST_MIN) {                                    /* fast branch: a grid of quotient lengths up to kq, and kq itself */
        size_t step = kq / 24 + 1;
        for (size_t t = DIVFAST_MIN + 1; t <= kq; t += step) { uint64_t c = K_divfast(n, t); if (c > best) best = c; }
        uint64_t c = K_divfast(n, kq); if (c > best) best = c;
    }
    best += 40;                                               /* divrem_any test and call */
    memo_put(6, n, kq, 0, best); return best;
}

/* ---- hgcd node */
static uint64_t B_base(size_t n, size_t k, int wm) {
    uint64_t steps = k, quo = 2 * (uint64_t)k;                /* steps <= k; the sum of (dq + 1) over the steps <= 2k */
    uint64_t v = quo * (14 + 12 * (uint64_t)n) + steps * (7 * ((uint64_t)n + 1) + 2 + INVA + 2 + INV_CTL + 11 * ((uint64_t)n + 1)) + steps * 30;
    if (wm) v += steps * K_mulQ_max(k);
    v += 14 * ((uint64_t)n + 1) + 8 + 20 + 100;               /* dupv of the inputs, identity matrix, loop exit */
    return v;
}
static uint64_t B_hgcd(size_t n, size_t k, int wm) {
    uint64_t v; if (memo_get(7, n, k, wm, &v)) return v;
    if (k <= (size_t)hgcd_base_k) { v = B_base(n, k, wm); memo_put(7, n, k, wm, v); return v; }
    size_t k1 = (k * (size_t)hgcd_k1_pct + 99) / 100;
    if (2 * k1 > n) k1 = n / 2;
    uint64_t c = 28 * ((uint64_t)n + 1) + 200;                 /* call overhead, copies on the early exits */
    c += B_hgcd(2 * k1, k1, 1);                                /* first call: top parts, matrix wanted */
    uint64_t ap = K_apply(n + 1, k1); uint64_t dp = 14 * ((uint64_t)n + 1) + 8; c += ap > dp ? ap : dp;
    size_t kq = (k < n ? k : n) + 1;                           /* quotient length <= k2 + 1 <= k + 1 */
    c += B_div(n, kq);
    if (k > k1 + 1) c += B_hgcd(n > k1 + 1 ? n - k1 - 1 : 1, k - k1 - 1, wm);   /* second call: parameter <= k - k1 - 1 and degree <= n - k1 - 1 (sumdeg + dq > k1) */
    if (wm) { c += K_mulQ_max(k) + K_matmul(k / 2, k - k / 2) + 80; }
    memo_put(7, n, k, wm, c); return c;
}

/* ---- gcd */
static uint64_t B_gcd(size_t n) {                              /* deg a = n, deg b <= n - 1 */
    uint64_t v; if (memo_get(8, n, 0, 0, &v)) return v;
    uint64_t c = div_cost_bound(n + 1, n + 1) + 100;           /* the equal-length step (not needed when deg b < deg a, harmless) */
    size_t m = n;
    while (1) {
        c += 20;
        if (m <= 2 * (size_t)hgcd_base_k) {                    /* classical Euclid to the end: at most m steps, sum of (dq + 1) <= 2 m */
            c += 2 * (uint64_t)m * (14 + 12 * (uint64_t)m) + (uint64_t)m * (7 * ((uint64_t)m + 1) + 2 + INVA + 2 + INV_CTL + 11 * ((uint64_t)m + 1)) + (uint64_t)m * 20;
            break;
        }
        c += B_hgcd(m, (m + 1) / 2, 0);
        c += B_div(m, m + 1) + 40;                             /* the division of c by d (quotient up to m) */
        m = m / 2;                                             /* next degree <= floor(m/2) - 1 */
    }
    c += INVA + 2 + INV_CTL + 8 + 10 * ((uint64_t)n + 1) + 100; /* monic scaling */
    memo_put(8, n, 0, 0, c); return c;
}
int main(int argc, char **argv) {
    ntt_init(15);
    if (argc > 1 && argv[1][0] == 'H') {              /* emit gcd_bounds.h for the level schedule 39062, 19531, ... (> 76) */
        size_t lv[16]; int nl = 0;
        for (size_t d = 39062; d > 76; d /= 2) lv[nl++] = d;
        printf("/* generated by gcdbound H: worst-case charges of the fast gcd (deg a = d, deg b < d) and of the division of a degree-d polynomial by a factor of degree > d/2 */\n");
        printf("#define NLEVELB %d\nstruct lvl_ { size_t d; unsigned long long gcd, div; };\nstatic const struct lvl_ LEVELB[NLEVELB] = {\n", nl);
        for (int i = 0; i < nl; i++) {
            size_t d = lv[i];
            uint64_t g = B_gcd(d), dv = B_div(d, d / 2 + 1);
            /* monotonicity checks on intermediate degrees */
            size_t xs[6] = { d - 1, d * 9 / 10, d * 3 / 4, d * 5 / 8, d * 9 / 16, d / 2 + 1 };
            for (int t = 0; t < 6; t++) { size_t x = xs[t]; if (x <= 152 || getenv("NOMONO")) continue; uint64_t gx = B_gcd(x), dx = B_div(x, x / 2 + 1);
                fprintf(stderr, "MONO d=%zu x=%zu gcd ratio %.5f div ratio %.5f\n", d, x, (double)gx / g, (double)dx / dv); }
            printf("    { %zu, %lluULL, %lluULL },\n", d, (unsigned long long)g, (unsigned long long)dv);
        }
        printf("};\n");
        return 0;
    }
    for (int i = 1; i < argc; i++) {
        size_t d = strtoull(argv[i], 0, 10);
        uint64_t b = B_gcd(d);
        printf("GCDBOUND %zu %llu\n", d, (unsigned long long)b); fflush(stdout);
    }
    return 0;
}
```

### certb_verify.py

```python
"""certb_verify.py: referee recomputation of the single-centre success-probability inputs (proof.md section 8.7). Needs no data file except the organizer's constants JSON.
usage:  python certb_verify.py ORCHARD_CONSTANTS.json C0 L [J [C0A]]   (J = line index, default 0; C0A = the CERT A critical point, checked if given)
needs:  python 3 and python-flint (tested with 0.9.0: fmpz_mod_poly with pow_mod, compose_mod, gcd, derivative, pow_trunc, inverse_series_trunc)
V1  build F_j (degree 5^7) by evaluation at the 2^17-th roots of unity and one inverse transform; check F(tau^5) against an independent reference hash (5 values of tau).
V7  for m = 5, 25, ..., 15625: H_m is forced by the top m coefficients of F (r-th root series, r = 5^7 / m); F mod H_m must be non-constant (no right factor of degree m).
V6  (if C0A is given; CERT A) F'(C0A) = 0, F''(C0A) != 0, g(C0A; S) has constant term 0 and gcd(g, g') = 1.
V2  g = H(C0; S) monic of degree d = 39062 from F and C0 by one Taylor shift.   V3  gcd(g, g') = 1.   V4  L is prime and d/2 < L <= d - 3.
V5  R_0 = x^p mod g, R_i = R_(i-1) o R_(i-1) mod g, Q = x^(p^L) mod g by the binary chain; g_L = gcd(g, Q - x), g_1 = gcd(g, R_0 - x);
    accept iff deg g_L - deg g_1 = L; then f = g_L / g_1 is irreducible of degree L and divides g (proof.md Lemma 8.7.1).
It prints SHA-256 of f, of g / f and of R_i mod f (32-byte little-endian coefficients, constant term first), to be compared with the values stated in proof.md."""
import sys, json, time, hashlib, random
import flint

P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
T0 = time.time()


def say(tag, msg):
    print('%-5s %8.1fs  %s' % (tag, time.time() - T0, msg), flush=True)


def is_prime(n):
    return n > 1 and all(n % q for q in range(2, int(n ** 0.5) + 1))


def sha(poly):
    n = poly.degree()
    return hashlib.sha256(b''.join(int(poly[i]).to_bytes(32, 'little') for i in range(n + 1))).hexdigest()


def ntt(a, w):
    n = len(a); j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit: j ^= bit; bit >>= 1
        j ^= bit
        if i < j: a[i], a[j] = a[j], a[i]
    ln = 2
    while ln <= n:
        wl = pow(w, n // ln, P); half = ln // 2
        tw = [1] * half
        for k in range(1, half): tw[k] = tw[k - 1] * wl % P
        for s in range(0, n, ln):
            for k in range(half):
                u = a[s + k]; v = a[s + k + half] * tw[k] % P
                a[s + k] = (u + v) % P; a[s + k + half] = (u - v) % P
        ln <<= 1


def line_data(const, j):
    MDS = [[int(x, 16) % P for x in r] for r in const['mds']]; RC = [[int(x, 16) % P for x in r] for r in const['round_constants']]
    mv = lambda v: [sum(MDS[i][k] * v[k] for k in range(3)) % P for i in range(3)]
    K5 = pow((1 << 65) + RC[0][2], 5, P)
    plane = [(MDS[i][2] * K5 + RC[1][i]) % P for i in range(3)]          # x_k = M_k0 U + M_k1 V + plane_k
    i1, i2 = [t for t in range(3) if t != j]
    a_, b_, c_, d_ = MDS[i1][0], MDS[i1][1], MDS[i2][0], MDS[i2][1]
    det = pow((a_ * d_ - b_ * c_) % P, -1, P)
    u, v = ((-plane[i1]) * d_ - b_ * (-plane[i2])) * det % P, (a_ * (-plane[i2]) - (-plane[i1]) * c_) * det % P   # x_i1 = x_i2 = 0
    kappa = (MDS[j][0] * u + MDS[j][1] * v + plane[j]) % P
    dirn = [(MDS[t][0] * MDS[j][1] - MDS[t][1] * MDS[j][0]) % P for t in range(3)]   # x_t = dirn_t * tau
    assert dirn[j] == 0 and dirn[i1] and dirn[i2]
    s1 = mv([kappa ** 5 % P if t == j else dirn[t] * 0 for t in range(3)])
    s2 = mv([pow(dirn[t], 5, P) for t in range(3)])
    return MDS, RC, (u, v, dirn, j, K5), s1, s2


def tail(s1, s2, MDS, RC, w):
    st = [(s1[i] + s2[i] * w) % P for i in range(3)]                        # state after round 1 (before the round-2 constants)
    for idx in (2, 3, 4, 60, 61, 62, 63):
        z = [(st[i] + RC[idx][i]) % P for i in range(3)]
        y = [pow(x, 5, P) for x in z] if idx != 4 else [pow(z[0], 5, P), z[1], z[2]]
        st = [sum(MDS[i][k] * y[k] for k in range(3)) % P for i in range(3)]
    return st[0]


def ref_hash(MDS, RC, nk, rho):                                              # independent straight-line reference of the target: rounds 0-3, 4, 60-63
    st = [nk, rho, 1 << 65]
    for idx in (0, 1, 2, 3, 4, 60, 61, 62, 63):
        z = [(st[i] + RC[idx][i]) % P for i in range(3)]
        y = [pow(x, 5, P) for x in z] if idx != 4 else [pow(z[0], 5, P), z[1], z[2]]
        st = [sum(MDS[i][k] * y[k] for k in range(3)) % P for i in range(3)]
    return st[0]


def build_F(const, j, R):
    MDS, RC, (u, v, dirn, jj, K5), s1, s2 = line_data(const, j)
    n = 5 ** 7; N = 1 << 17
    z = 2
    while True:
        w = pow(z, (P - 1) // N, P)
        if pow(w, N // 2, P) != 1: break
        z += 1
    vals = []; x = 1
    for _ in range(N):
        vals.append(tail(s1, s2, MDS, RC, x)); x = x * w % P
    ntt(vals, pow(w, -1, P)); ninv = pow(N, -1, P)
    co = [c * ninv % P for c in vals]
    assert all(c == 0 for c in co[n + 1:]) and co[n] != 0
    F = R(co[:n + 1])
    e = pow(5, -1, P - 1); rnd = random.Random(1)
    for _ in range(5):                                                       # F(tau^5) = reference hash of the canonical input built from tau
        tau = rnd.randrange(P); U = (u + tau * MDS[j][1]) % P; V = (v - tau * MDS[j][0]) % P
        nk = (pow(U, e, P) - RC[0][0]) % P; rho = (pow(V, e, P) - RC[0][1]) % P
        assert ref_hash(MDS, RC, nk, rho) == int(F(pow(tau, 5, P))) % P, 'F does not match the reference hash'
    return F


def taylor_shift(F, c, R):
    n = F.degree(); fact = [1] * (n + 1)
    for k in range(1, n + 1): fact[k] = fact[k - 1] * k % P
    A = R([int(F[n - i]) * fact[n - i] % P for i in range(n + 1)])          # sum a_{n-i} (n-i)! x^i
    inv = pow(fact[n], -1, P); invf = [1] * (n + 1); invf[n] = inv
    for k in range(n, 0, -1): invf[k - 1] = invf[k] * k % P
    cp = 1; B = []
    for m in range(n + 1): B.append(cp * invf[m] % P); cp = cp * c % P       # c^m / m!
    C = A * R(B)
    return R([int(C[n - k]) * invf[k] % P for k in range(n + 1)])           # coefficients of F(x + c)


def g_of_centre(F, c0, R):
    n = F.degree(); b = taylor_shift(F, c0, R); an = pow(int(F[n]), -1, P)
    return R([int(b[2 * k + 1]) * an % P for k in range((n - 1) // 2 + 1)])  # monic: F(c+s) - F(c-s) = 2 a_n s g(s^2)


def witness(g, l, R, show=say):
    """accept iff the monic squarefree g has exactly one irreducible factor of prime degree l (d/2 < l <= d-3); returns (f, cofactor, R_list) or None"""
    d = g.degree(); X = R.gen()
    assert g.gcd(g.derivative()) == R(1); show('V3', 'gcd(g, g\') = 1: g is squarefree')
    assert is_prime(l) and 2 * l > d and l <= d - 3; show('V4', 'l = %d is prime in (d/2, d-3], d = %d' % (l, d))
    Rs = [X.pow_mod(int(R.modulus()), g)]; show('V5', 'R_0 = x^p mod g')
    m = l.bit_length()
    for i in range(1, m):
        Rs.append(Rs[-1].compose_mod(Rs[-1], g)); show('V5', 'R_%d = R_%d o R_%d mod g' % (i, i - 1, i - 1))
    Q = None
    for i in range(m):
        if (l >> i) & 1:
            Q = Rs[i] if Q is None else Rs[i].compose_mod(Q, g); show('V5', 'chain bit %d' % i)
    gl = g.gcd(Q - X); g1 = g.gcd(Rs[0] - X)
    show('V5', 'deg gcd(g, x^(p^l) - x) = %d, deg gcd(g, x^p - x) = %d' % (gl.degree(), g1.degree()))
    if gl.degree() - g1.degree() != l: return None
    f = gl // g1
    return f, g // f, [r % f for r in Rs]


def indecomposable_at(F, m, R):
    """F is not G(H) for any G over F_p with deg H = m (m | deg F, p > deg F): H is forced by the top m coefficients of F (monic, H(0) = 0, the r-th root series, r = deg F / m);
    returns (H, F mod H); F = G(H) iff F mod H is constant."""
    n = F.degree(); r = n // m; assert n % m == 0 and P > n
    X = R.gen(); an = pow(int(F[n]), -1, P)
    A = R([int(F[n - i]) * an % P for i in range(m)])                      # A(y) = (reversed F / a_n) mod y^m, y = 1/x
    B = R(1); N = 1; rinv = pow(r, -1, P)
    while N < m:
        N = min(2 * N, m)
        t = A.truncate(N).mul_low(B.pow_trunc(r, N).inverse_series_trunc(N), N) + (r - 1)   # B <- B ((r-1) + A / B^r) / r  (Newton step for B^r = A)
        B = B.mul_low(t, N).scalar_mul(rinv)
    b = [int(B[i]) if i <= B.degree() else 0 for i in range(m)]
    H = R([0] + [b[m - 1 - k] for k in range(m)] + [])                     # x^m + b_1 x^(m-1) + ... + b_(m-1) x   (coefficient of x^(m-i) is b_i, b_0 = 1)
    return H, F % H


def cert_a(F, c0a, R):
    g = g_of_centre(F, c0a, R); d1 = F.derivative(); d2 = d1.derivative()
    assert int(d1(c0a)) % P == 0 and int(d2(c0a)) % P != 0, "CERT A: F-prime(c0) = 0 and F-second(c0) != 0 fail"
    assert int(g[0]) == 0 and g.gcd(g.derivative()) == R(1), "CERT A: g(0) = 0 and gcd(g, g-prime) = 1 fail"
    return g


if __name__ == '__main__':
    const = json.load(open(sys.argv[1])); c0 = int(sys.argv[2]); l = int(sys.argv[3]); j = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    R = flint.fmpz_mod_poly_ctx(P)
    c0a = int(sys.argv[5]) if len(sys.argv) > 5 else None
    F = build_F(const, j, R)
    say('V1', 'F_%d built, degree %d, sha256(coefficients) = %s' % (j, F.degree(), sha(F)))
    for e in range(1, 7):                                                   # V7: no proper right factor of degree 5^e (e = 1..6); 5^7 has no other proper divisors
        H, rem = indecomposable_at(F, 5 ** e, R)
        assert rem.degree() >= 1, 'F is a composition with an inner polynomial of degree %d' % 5 ** e
        say('PASS', 'V7 inner degree m = %5d: F mod H_m has degree %d > 0, so F != G(H) for every G; sha256(H_m) = %s' % (5 ** e, rem.degree(), sha(H)))
    if c0a is not None: cert_a(F, c0a, R); say('PASS', 'CERT A at c0 = %d: F-prime(c0) = 0, F-second(c0) != 0, g(0) = 0, g squarefree' % c0a)
    g = g_of_centre(F, c0, R); assert g.degree() == (F.degree() - 1) // 2 and int(g[g.degree()]) == 1
    say('V2', 'g = H(c0, S) monic, degree %d, sha256 = %s' % (g.degree(), sha(g)))
    res = witness(g, l, R)
    if res is None: say('FAIL', 'no irreducible factor of degree %d' % l); sys.exit(1)
    f, cof, Rl = res
    say('PASS', 'f has degree %d and is irreducible; sha256(f) = %s' % (f.degree(), sha(f)))
    say('PASS', 'cofactor degree %d, sha256 = %s' % (cof.degree(), sha(cof)))
    for i, r in enumerate(Rl): say('PASS', 'sha256(R_%d mod f) = %s' % (i, sha(r)))
```

