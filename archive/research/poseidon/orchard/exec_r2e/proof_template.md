# Orchard Poseidon, r = @@R@@: one deterministic run on the fixed target, executed operation count (two free rounds on a line, odd part about a fixed centre, half-gcd)

## 1. Claim

Target: `poseidon-orchard-r@@R@@-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, @@PARTIAL@@, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `success_probability = 1`: the procedure is deterministic (centres `c_i = i` in the fixed order `i = 1, 2, 3, ...`, section 4) and it was executed once, from the start, on the fixed target, where it stopped with the collision at trial @@TRIALS@@ (`c = @@LASTC@@`); every executed trial, failed ones included, is charged. There is no probability statement and no worst-case bound anywhere in this document.
* `time_log2 = @@TIME_LOG2@@` in target-compression units (`C(@@R@@) = @@C@@` primitive operations per unit): the executed operation count of that one run, all @@TRIALS@@ trials, `N = @@N@@` operations (section 6), `log2(N / @@C@@) = @@TIME_LOG2_EXACT@@`, rounded up at five decimals. The twiddle table is built inside the run and is part of `N`, so `preprocessing_log2 = 0`.
* `memory_log2_bytes = @@MEM_LOG2@@` (`@@MEM_BYTES@@` bytes, section 7): the peak allocator footprint of the executed run (maximum over the trials, measured, headers included) plus the whole statically linked executable image and a stack bound. The normalized cost is `@@TIME_LOG2@@ + @@MEM_PEN@@ = @@SCORE@@`.
* No selection: no centre was chosen or screened beforehand. The run began at `c_1 = 1`, every trial it executed is in the count `N`, and the table of section 6 lists them all. `memory` is the maximum over the trials (the buffers of a trial are released before the next).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^@@DEXP@@`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is a known approach. What is offered here is a complete finite implementation with an executed operation ledger and a low-memory schedule. No heuristic premise is used.
* The collision stored in `certificates/` is the output of this program. It is checked at the selected target with the organizer's hash.

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

2.3 Digest polynomial. Rounds 2, 3 (full), @@PARTIALRS@@ (partial), 60, 61, 62, 63 (full) put @@LAYERS@@ S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^@@DEXP@@ = D = @@D@@`. The leading coefficient is obtained by
propagating leading coefficients through the @@LAYERS@@ layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = @@FD0@@`
(computed; so `deg F = D` exactly). The program reaches the same value from the other side: the inverse transform of stage B returns `H g_m = @@LEAD@@` (`H = @@H@@`), and `(H g_m) / H = f_D(0)`; stage B tests that coefficient for zero with a counted test before it inverts it. For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = @@M@@`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = @@H@@ = 3 * 2^@@HEXP@@` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = @@N2@@` evaluations of `F` are each charged as
one target-compression unit (`C(@@R@@) = @@C@@` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store,
the loop control and the incremental update of the layout position of the point (row counter and bit-reversed counter), all charged by `CTL` next to the statements that execute them) is charged on top.


## 4. The program (one deterministic run)

```
init:   twiddle table
setup:  the line (line_setup)
A  c := c_i = i (the integer i as a field element; one conversion, 3 control ops)
B  g := monic g_c, by section 3 (@@N2@@ evaluations + one inverse NTT of size @@H@@ + the counted test that the leading coefficient is nonzero + normalisation by the leading coefficient)
C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; @@STEPS@@ modular squarings, 45 of the steps also multiply by S by a streaming shift)
D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
E  S := a root of G                 (only if deg G >= 1: root isolation, for degree 1 S = -G_0; otherwise the trial ends and the next centre is tried)
F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
G  verify: the two reference hashes (@@C@@ operations each) are equal and the pairs differ -> stop the search; otherwise the next trial
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each (section 4.2)
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the @@VEXP@@ bits after the leading one are zero, so the program starts from the monomial `S^v` with `v = 2^@@VEXP@@ < m` (this absorbs @@VEXP@@ of the 253 squarings, @@VEXP@@ + @@STEPS@@ = 253), and the squaring loop of stage C has @@STEPS@@ steps, of which 45 also multiply by `S` (a streaming shift).

Determinism. The program takes no input and reads no file. It executes init and setup once, then trials `i = 1, 2, 3, ...` (stages A to D, and E to G when `deg G >= 1`), and, at the first trial whose two reference hashes agree with distinct pairs, runs stage H and returns exit status 0. The program draws no random word: the shifts of the root isolation (made only in a trial with `deg G >= 2`) are `a = 1, 2, 3, ...`; a trial with `deg G = 1` makes none. If the leading coefficient of `g` were zero for a centre (it is not: it does not depend on the centre, section 3), the centre would be skipped: the trial ends after stage B and the next centre is tried. Every trial, failed or not, is executed to its end and counted by the same counters; the stages form a chain without a gap (`stage_open` in `exec_attack.c` closes the previous stage as it opens the next, so every charged operation, the control of the trial loop included, belongs to exactly one stage and one trial); and the buffers of a failed trial are released before the next trial begins. In the executed run the trials are listed in section 6; the last trial is the one that produced the certificate.

### 4.2 Machine model and charging rules
Every item below is counted by the executing code at the statement that executes it; none is estimated. The complete source is in section 9. The rules for loop control, address work and loads and stores follow the price list of the public r = 2 entries (quoted from section 4.1 of the revision of tanctl that reuses the kernels of entry 186052af: "A radix-2 butterfly is charged 9/2 units: the twiddle update multiplication, the twiddle product, one addition, one subtraction and one half unit of loop/address work ... Loop control: a radix-8 pass processes eight elements, twelve butterflies, per loop iteration (one index update, one comparison, one branch: 3 units per 12 butterflies), so 1/2 unit per butterfly is conservative; every other per-element loop (pointwise steps, padding, copies, folds, remainders, shifts) is unrolled eight elements per iteration and charged 1/2 unit per element."). We adopt exactly those two statements: 1/2 unit per butterfly and 1/2 unit per element of an unrolled loop.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly), and the control of their bit loops is charged inside `fp_pow` and `fp_sqrt` (`ctl_add` in `pallas.c`).
* load or store of a 256-bit element of an array: 1 each (`LD(n)`, `ST(n)`); no separate address-formation operation is charged: the register-block kernels use constant displacements from a block base, as in the public entries. The loads of twiddles and of the constants of the radix-3 stage are charged as loads (`LD(1)` per use).
* loop and address work in half units (counter `hc`; macro `HC(n)` adds `n` half units): one half unit per butterfly (`BF`, `BFN`, `IB`, `IBN` in `ntt_kern.h`), one half unit per element of every pointwise step fused into the transform, three half units (one per element) per position of the radix-3 Good-Thomas stage, and `loopc(n)` = `n` half units after every other loop of `n` elements (copy, fold, pad, subtraction, scaling, schoolbook inner loops: these are unrolled eight elements per pass in the rule above). The radix-3 stage is executed by three-position unrolled kernels (the rotation of the Good-Thomas index repeats every three positions, so the choice of the constant permutation and of the input pattern is resolved at the unrolled kernel, not per element); the per-region setup of that stage is charged as the constants 25 and 30 in `ntt.c`. The half units of each stage visit are added up and rounded up to a whole operation when the visit ends (`snap_total` in `common.c`: `(hc + 1) / 2`); that rounded figure is what every stage row, every trial row and the total contain.
* per-call constants of a transform pass (`CTLK` in `ntt.c`): computing the pass tables and the call and return: `18 + 6k` (forward), `19 + 6k` (inverse and fused pass) operations for a pass of `k` layers.
* every other executed index or control operation outside the transform kernels, one each: shift, mask, or, addition, subtraction, multiplication, modulo, comparison, conditional branch. They are added with `CTL(k)` next to the statement that executes them (the gcd, the divisions, the root isolation, the line setup, the bit-reversed index of stage B, the control of the trial loop), and data-dependent tests are charged per executed test.
* transform kernels are generated, straight-line code (`gen_kern.py` is part of the source of section 9; its output `ntt_kern.h` is listed there). A block kernel for `k` layers (1 to 4; 2^k data words `x[]`) has no loop and no branch: each butterfly is the literal statements `fp_sub`, `fp_add`, `fp_mul` (three field operations, none for the multiplication when the twiddle is 1 at `b = 0`) plus its half unit, and every twiddle load is a literal `LD(1)`.
* working registers (disclosed assumption): a block keeps its 2^k <= 16 data words `x[]` in registers; the twiddle operand and the butterfly temporary need two further words, so the kernels assume a register file of 18 words of 256 bits. Strides, shift counts, base pointers and loop indices are held in integer registers (not charged as memory accesses). The real cost of a machine with fewer registers would be higher; this is the one structural assumption of the model.
* the centre `c_i = i`: one conversion (one multiplication) and the three control operations of the trial loop; the shifts `a = 1, 2, 3, ...` of the root isolation are drawn the same way (no random words are used anywhere).
* the reduced permutation evaluations of stage B: @@C@@ each (`C(@@R@@)`), instead of their (smaller) expanded arithmetic (`X.perm`). Nothing else is charged as a unit.
* small-degree work in the line setup and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 1 control operation.
* Montgomery conversions: every conversion of an integer to or from the internal representation (`fp_from_limbs`, `fp_to_limbs`, `fp_from_u64`, `fp_from_hex`; for example the centre `c_i` of stage A, the constants of the twiddle setup, the factor `N` of the powering, the inputs of the reference hashes, and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication: `pallas.c` increments the multiplication counter in `fp_from_limbs` and `fp_to_limbs`, and every other conversion function calls them. The constants of `pallas_consts.h` are stored in Montgomery form and need no conversion.
* output (stage H): the program converts `nk1`, `rho1`, `nk2`, `rho2`, the digest and the centre out of the Montgomery representation (6 charged multiplications) and encodes each as 64 hexadecimal digits in `enc_hex` of `exec_attack.c`, 12 operations per digit (loop update, comparison and branch; `pos = 63 - i`; word index; mask; scaling of the shift count; shift; mask; table load; byte store) and 5 more per call; stage H is inside the total `N`. The standard-library call that writes the encoded text to the output descriptor and the program's report of its own counters (the stage table, the trial rows, `printf` of the statistics) are not operations of the computation and are not counted; every byte of the output is formed and stored by the counted code.
* the leading coefficient of `g` (stage B): one four-limb zero test and one branch (5 control operations) on the coefficient `H g_m` before it is inverted; if it were zero the centre would be skipped (the trial ends and the next centre is tried). Every inversion, including that one, is counted in full.
* the program contains no budget, no halt, no random draw and no self-check: everything it executes between the start of `main` and the end of stage H is charged, except the increments of the instrumentation's own statistics (`inv_calls`, `pow_calls`, `sqrt_calls` in `pallas.c`, `hgcd_stat_calls`, `hgcd_stat_base_steps`, `hgcd_stat_bigdiv` in `hgcd.c`), which are bookkeeping of the report and not operations of the computation.
* allocator: `xalloc` and `xfree` call `posix_memalign` and `free`; their instruction counts are not charged as time (the model's primitive operations do not include allocation, and the working state of the computation is a set of arrays); the memory they use is counted in full in section 7.
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

`hgcd(a, b, k)` (`deg a = n`) in `hgcd.c` returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})`. The code: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`, schoolbook division, one inversion per division) while the next quotient degree fits the remaining parameter; a division with a two-coefficient quotient (the normal case) is one pass over the remainder, and `R := R Q` for it is one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each matrix entry are transformed once and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`poly_divrem_naive`); (5) `R2, (c', d') = hgcd(d, e, k - d_1 - deg q)`; return `R1 Q R2` (matrix products only if the matrix is wanted: `mat_mulQ` for `Q`, and `mat_mul` for the product of two 2 x 2 matrices, schoolbook for entries of length at most 48 and otherwise by shared-transform NTT products with `conv_bilin_otf`).
The outer function `poly_gcd_fast_own` repeats, while `deg b > 0`: if `n = deg a <= 192`, one classical division step; otherwise `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` (`poly_divrem_naive`) and `(a, b) := (d, e)`; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications). If that gcd has more than 17 coefficients the trial ends without a root (it would be charged in full); in the executed run `deg G = 1`.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes
and compares them; the program returns success only if they are equal and the pairs differ. Independent of the program, the pair in `certificates/` is checked by the organizer's hash, and the digest `@@DIGEST@@` is printed by the run.

## 6. Ledger: the executed run (primitive operations; `C(@@R@@) = @@C@@`)

The count is the instrumented total of one execution of the shipped source (`gcc -O3 -march=native -static`, run as `exec_attack 1` under `ulimit -s 64`; the argument only turns on printing of the powering breakdown for the first trial). `arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control (half units of loop and address work rounded up per stage visit, section 4.2), random words, and the @@C@@-operation unit charges. Nothing is bounded, extrapolated or taken from another run: every figure below is a counter of the same execution. The program prints one total: the sum of the stage rows, the sum of the trial rows and the counters of the whole run are computed separately and printed in the line `RECONCILE`, which reads `ok=1` only if the three are equal (@@RECONCILE@@) and if every counter of the whole run (additions, subtractions, multiplications, squarings, loads, stores, control operations, unit charges, half units) equals the sum of that counter over the stage visits. Half units are rounded up to a whole operation at the end of each stage visit (section 4.2); the stage rows, the trial rows and the counters all use that one rounding, so there is no separate rounding row. The table below and the table of trials are two groupings of the same counters.

@@LEDGER_TABLE@@

@@TRIAL_TABLE@@

Total `N = @@N@@` operations (stage rows, trial rows plus the row outside the trials, and the counters of the run, all equal) `= @@UNITS@@` units, `log2(N / @@C@@) = @@TIME_LOG2_EXACT@@`, claimed as `@@TIME_LOG2@@` (rounded up).
The half-gcd of stage D charged @@GCD_OBS@@ operations in this run (summed over all trials; the modulus has degree @@M@@). Composition by type of the run (init included; half units of loop and address work in all: @@T_HC@@, rounded up per stage visit): add `@@T_ADD@@`, sub `@@T_SUB@@`, mul `@@T_MUL@@`, sqr `@@T_SQR@@`, loads `@@T_LD@@`, stores `@@T_ST@@`, control `@@T_CTL@@`, unit charges `@@T_PERM@@`.

Stage C in detail (m = @@M@@): Newton for MU: @@NEWTON@@ operations; prefix and scaling: @@PREFIX@@; @@STEPS@@ squaring steps at @@PER_STEP@@ operations each (arith @@PER_STEP_ARITH@@). Of the arithmetic of stage C, @@POW_ARITH@@ operations; the transforms are the largest term.

### 6.1 Ledger recomputation

```python
@@LEDGER_PY@@
```

## 7. Memory

The executable is linked statically (`gcc -O3 -march=native -static`): the C library routines it uses (`malloc`, `memcpy`, `memset`, `printf`, start-up code) are part of its own image and there is no loader and no shared library. Three terms are counted.
(a) The whole executable image: every loadable segment, text + data + bss as printed by `size` for the linked program: @@STATIC_DESC@@. This includes the library code and the library's own static state (the allocator's arena descriptor, the stdio tables).
(b) The footprint of the allocator at its peak. Every buffer of the program is served by `xalloc`, which places a 64-byte header (it holds the payload size and keeps the payload 64-byte aligned) in front of the payload. The program reads the allocator's footprint with `mallinfo2()` right after every allocation (`arena` + `hblkhd`: the bytes the allocator holds from the system, the heap and the separately mapped blocks) and keeps the maximum (per stage in the list below, overall in the figure used). This footprint contains the payloads, the 64-byte headers, the allocator's own chunk headers and alignment padding, page rounding of mapped blocks, and heap memory the allocator has not yet returned. At the peak (in stage @@PEAK_STAGE@@) there were @@PEAK_LIVE@@ live allocations holding @@PEAK_PAY@@ bytes of payload; their @@PEAK_LIVE@@ headers of 64 bytes (@@HDR@@ bytes) are inside the footprint. The largest buffers (stage C at `m = @@M@@`) are the twiddle table (`2^@@TWEXP@@` elements, @@TWB@@ bytes), `Y` (`3 * 2^@@AEXP@@` elements, @@YB@@), `tmp` (`2^@@AEXP@@` elements, @@TMPB@@), `MU` (@@MUB@@), `g` (@@GB@@) and the result `F` (@@FB@@). Footprint peaks per stage (maximum over the trials): @@STAGE_PEAKS@@. The largest is @@HEAP_PEAK@@ bytes.
(c) A stack bound of 65,536 bytes: the complete run was executed under `ulimit -s 64`.
Total: `@@MEM_BYTES@@` bytes `= 2^@@MEM_LOG2@@` (rounded up at three decimals). The memory penalty is `max(0, @@MEM_LOG2@@ - 20) = @@MEM_PEN@@`.
Not counted: the pages the kernel maps for a process outside its executable image (the vdso and vvar mappings, page tables) and the buffers of the program's report of its counters (`printf` output). As a cross-check, the run was measured with GNU `time -v`: its maximum resident set was @@RSS@@ bytes, below the total counted here.
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 9), one machine-checked collision certificate (`certificates/`, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package contains only the certificate, so the C source is part of this document (section 9) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3 -march=native -static` and run as `exec_attack 1`.
* The cost is the executed count of one run of the fixed procedure from its first centre, every trial charged. It says nothing about how many trials another sequence of centres would need.
* The cost claim assumes the model of section 4.2; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it. The organizer did not run the program, so the counts rest on the shipped source.
* Reproduction on one core: (a) the collision certificate against the organizer's hash, seconds; (b) the ledger recomputation of section 6.1, seconds; (c) `gcc -O3 -march=native -static` of the source of section 9 and `exec_attack 1` under `ulimit -s 64`, which reproduces every count of section 6 and prints the collision (about @@SECS@@ s; the footprint of section 7 depends on the allocator of the C library it is linked with).

## 9. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter, `CTL(n)` adds `n` to the control counter, `HC(n)` and `loopc(n)` add `n` half units; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()` reads all counters; `snap_restore()` restores them where a block is charged by a stated unit instead of its expansion (the line evaluations of stage B, charged `X.perm += @@C@@` each). Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: @@FILE_ORDER@@.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs. The root isolation of `euclid.c` for `deg G >= 2` is not executed by this run (the run has `deg G = 1`).

@@APPENDIX@@
