# Orchard Poseidon, r = @@R@@: two free rounds on a line, odd-part polynomial, root finding (exact ledger, low memory)

## 1. Claim

Target: `poseidon-orchard-r@@R@@-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, @@PARTIAL_WORDS@@, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = @@TIME_LOG2@@` in target-compression units (`C(@@R@@) = @@C@@` primitive operations per unit): the charged work of a run of at most @@NCEN@@ centres in which no centre
  finds a root, every operation of the program charged and every data-dependent stage charged at its halt budget (section 6). A single centre costs `@@TIME_LOG2_ONE@@`.
* `memory_log2_bytes = @@MEM_LOG2@@` (`@@MEM_BYTES@@` bytes, section 7), so the normalized cost is `@@TIME_LOG2@@ + @@MEM_PEN@@ = @@SCORE@@`.
* `success_probability = @@PCLAIM@@`: @@NCEN@@ independent centres, each succeeding with probability at least @@PMIN@@ (@@PMIN_WORDS@@), so the run succeeds with probability at least `1 - (1 - @@PMIN@@)^@@NCEN@@ = @@PRUN@@`. Every halt of the program is counted as a failure inside the measured per-line rates.
* The method (two free rounds on a special line, then the roots of a univariate polynomial) is a known approach. What is offered
  here is a complete finite implementation with an exact operation ledger, a low-memory schedule and the complete source (section 10). Every figure below is the count of an executed,
  instrumented program; no omega = 2.8 substitution and no asymptotic estimate is used.
* The collisions stored in `certificates/` (@@N_CERT@@ pairs from @@N_CERT@@ different centres) are outputs of this program. They check the construction at the
  selected target with the organizer's hash; they are not part of the cost claim.

## 2. Two free rounds: a line in the input plane

Notation. `p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001`, `p mod 5 = 2`, so `gcd(5, p-1) = 1` and `x -> x^5` is a
bijection of `F_p` with inverse `x -> x^e`, `e = (4(p-1)+1)/5` (254 bits, 125 one bits). `M` is the deployed 3x3 MDS, `c_{i,k}` the
deployed round constant `k` of round `i` (read from the organizer constants; never regenerated).

2.1 Round 0. With `U = (nk + c_{0,0})^5`, `V = (rho + c_{0,1})^5`, `K = (2^65 + c_{0,2})^5` the state after round 0 is `M (U, V, K)^T`.
`(nk, rho) -> (U, V)` is a bijection of `[0,p)^2` (inverse `nk = U^e - c_{0,0}`, `rho = V^e - c_{0,1}`), so every `(U, V)` has exactly one
canonical preimage.

2.2 Round 1. The S-box input is `x_k = M_{k0} U + M_{k1} V + b_k`, `b_k = M_{k2} K + c_{1,k}`, affine in `(U, V)`.
Fix `j in {0,1,2}`, `I = {i1, i2} = {0,1,2} \ {j}`. Let `Q = (U_Q, V_Q)` be the solution of `x_{i1} = x_{i2} = 0` (the 2x2 determinant
`M_{i1,0} M_{i2,1} - M_{i1,1} M_{i2,0}` is a minor of the MDS; it is nonzero for all three `j`, checked on the deployed constants). Let
`(a, b) = (M_{j,1}, -M_{j,0})` and `(U, V) = Q + tau (a, b)`. Then `x_j = kappa` is constant and `x_i = d_i tau` for `i in I`, where
`d_i = M_{i0} a + M_{i1} b` (`d_j = 0`). With `W = tau^5` the round-1 S-box output is `v0 + W v1`, `v0 = kappa^5 e_j`, `v1 = sum_{i in I} d_i^5 e_i`.
After the round-1 MDS and the round-2 constants the state is `alpha + beta W` with `alpha = M v0 + c_2`, `beta = M v1`, affine in `W`.

2.3 Digest polynomial. Rounds 2, 3 (full), @@PARTIAL_LIST@@ (partial, r = @@R@@), 60, 61, 62, 63 (full) put @@LAYERS@@ S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F_j(W)` with `deg F_j <= 5^@@EXPO@@ = D = @@DEG@@`. The leading coefficient is obtained by
propagating leading coefficients through the @@LAYERS@@ layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for each `j`:
`f_D(0) = @@FD0@@`,
`f_D(1) = @@FD1@@`,
`f_D(2) = @@FD2@@`
(computed; so `deg F_j = D` exactly). For random `tau`, `F_j(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau` for each `j`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F_j(W1) = F_j(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F_j(c + s) - F_j(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = @@M@@`, `g_c` has degree exactly `m` and
leading coefficient `2 f_D(j)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)`. (Roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives
`s = 0` and `W1 = W2`.)

Construction of `g_c` by evaluation. `H = @@H@@ = 3 * 2^@@HA@@` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F_j(c + zeta^i) - F_j(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = @@H2@@` evaluations of `F_j` are each charged as
one target-compression unit (`C(@@R@@) = @@C@@` operations), although a line evaluation (affine start, six more rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store,
four control operations for the bit-reversed index) is charged on top.

## 4. The program (per centre; at most @@NCEN@@ centres)

```
centre k = 0 .. @@NCEN@@-1 (@@LINE_EXPR@@):
  A  c := uniform 254-bit word (one random word + 2 control ops)
  B  g := monic g_c, by section 3 (@@H2@@ evaluations + one inverse NTT of size @@H@@ + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; @@STEPS@@ modular squarings, a subset of the steps also multiplying by S by a streaming shift)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products; classical quotient steps when the parameter is at most 48) ; if deg G = 0 the centre fails;
                                       if deg G > @@DEGCAP@@ the centre fails
  E  S := a root of G                 (Cantor-Zassenhaus: random shift a, gcd(G, (x+a)^((p-1)/2) - 1); at most 40 shifts per centre)
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (@@C@@ operations each) are equal and the pairs differ -> output, stop.
```

Implemented halts (all enforced in the executed program; a check adds 2 control operations to the ledger). Each halt ends the centre or the run without an output, and every execution used for the
success rates of section 8 ran with all of them active, so a halt is a failure inside the measured rate and no probability for a halt is assumed anywhere:
* at most @@NCEN@@ centres; `deg G <= @@DEGCAP@@` (otherwise the centre fails);
* stage D stops the program as soon as the work charged since the stage began exceeds `@@BUDGET_GCD@@` operations. The budget is the derived normal-case cost of section 4.4 plus 10 percent; the check is made at every entry of the
  half-gcd recursion, after every matrix application and matrix product, in every quotient step of the classical base case and inside the products between rows; the largest work between two checks is bounded by `@@GAP_GCD_BOUND@@` operations (section 4.4);
* stage E (all shifts of the whole run together) is checked before every shift (at most 40 shifts per centre) and stops the program when more than `@@BUDGET_ROOT@@` operations have been charged; one shift costs at most `@@W_SHIFT@@` operations (section 4.4).

### 4.1 Machine model and charging rules

The program of section 10 is the program that was executed; its counters are part of its source. Every item below is counted by that code as it runs; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications; `x^e`: 253 squarings, 124 multiplications; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each (`LD`, `ST`). A 16-element register block is the only register assumption: a pass of up to four butterfly layers loads its block, works on the block, and stores it.
* integer and control operations (`CTL(n)`): every executed comparison, conditional branch, loop-index update, shift, addition, subtraction, multiplication, modular reduction and address calculation on indices and pointers is charged 1, and the charge is written next to the statement that executes it, in the source of section 10.
  Straight loops (`loopc`) are charged 8 per element (increment, comparison, branch and up to three pointer updates). In the transform kernels the twiddle pointer of a layer is computed with 2 operations for the first position of the layer (shift, address) and 1 addition for each further position; a load or store of a block element at stride `s > 1` costs 1 address update, at stride 1 it is a constant displacement; each block costs 6 operations of loop, base and zero-index test.
  The radix-3 stage is charged per element for the loop, the rotation update, the mask lookup, the address of each loaded position, the dispatch and the destination addresses; the Good-Thomas rotation of each element is maintained incrementally.
* the reduced permutation evaluations of stage B: @@C@@ each (section 3). Nothing else is charged as a unit.
* small-degree work in stages E and F is charged generously: 2 loads, 1 store and 1 control operation on top of every arithmetic operation.
Not charged (declared): conversion of constants to the internal Montgomery representation (constants of the program text), formatting and printing, and register-to-register moves of 256-bit values.

### 4.2 Stage C: the powering schedule (in place, no stored spectra)

`N = @@NN@@ = 3 * 2^@@NA@@ >= 2m - 1` and `N' = @@NP@@ = 3 * 2^@@NPA@@ >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; `p - 1` is divisible by `3 * 2^32`) followed by three independent
rows of radix-2 transforms of length `2^a`, run as passes of at most four layers (16-element register blocks). The state is `s = a / N` so no scaling is needed in the loop.
One step maps the residue `a` (m coefficients, stored in the buffer `Y` of `N` elements) to `a^2 mod g`:
```
Y := conv_sq(Y)                       square: forward transform, pointwise square fused with the first inverse pass, inverse transform
F[i] := Y[i] + Y[i+N'] (i < m)       fold of the low part modulo x^N' - 1 (saved in the buffer F of m elements)
Y[0..m-2] := Y[m..2m-2]               high part T1 of the square
Y := conv(Y, MU)                      quotient q (Barrett): MU = x^(N-m+2) * floor(x^(2m-2)/g) / (N N') stored compactly (m-1 elements)
Y := conv_N'(Y, g)                    (q * g) mod (x^N' - 1)
Y[i] := F[i] - Y[i] (i < m)           new residue; if the exponent bit is 1: shift by x and subtract lead * g (streaming)
```
The spectra of `MU` and of `g` are not stored: for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp` of `2^@@NA@@` elements,
immediately multiplied into the corresponding row of `Y`, and discarded. (About 1.5 transform equivalents per step more than with cached spectra; this is what the ledger below pays for the memory saved.)
`MU` is computed once per centre from `g` by Newton iteration with the same row-wise products. The first exponent bits after the leading one are absorbed by starting from the monomial `S^v` (`v < m`, @@VBITS@@ bits).

### 4.3 Stage D: half-gcd

Half-gcd of Knuth-Schoenhage / Thull-Yap type with parameter `k1 = k/2`; products by the same row-wise NTT products (operands generated one row at a time, outputs accumulated in a single buffer), classical Euclid below parameter 48,
ownership of inputs passed down the recursion so that no input is kept after its last use. The ledger counts every operation of the executed recursion (planted-gcd tests against classical Euclid on the same input: identical gcd).

### 4.4 Derivation of the stage budgets

Stage D. The half-gcd recursion `hgcd(n, k)` of the source (`hgcd.c`) with `k1 = ceil(k/2)` calls itself on the top halves (`hgcd(2 k1, k1)`), applies the inverse matrix of degree `k1` to the operands of degree `n` and `n-1`, performs one division step, and calls `hgcd(n - k1 - 1, k - k1 - 1)`;
below `k = 48` it runs the classical Euclid base case. The driver calls `hgcd(n, (n+1)/2)` and then one division step, so `n` becomes `n - ceil((n+1)/2) - 1`, repeatedly until `n <= 96`, followed by the classical gcd.
`bound_gcd.c` (section 10) enumerates this tree for `n = m = @@M@@` and executes the shipped node procedures (`apply_inv`, `mat_mulQ`, `mat_mul`, `poly_divrem_naive`, `hgcd_base`) on operands of exactly the sizes of each node,
memoising nodes by `(n, k, matrix flag)`. Its output is `@@DERIVED_D@@` operations for the tree, `@@EXTRA_D@@` for the scan of the degree of `R - 1` (5 per position) and a fixed allowance of 100,000. The stage D budget is this sum plus 10 percent, rounded up: `@@BUDGET_GCD@@`.
The budget is a halt, so no path of the program can exceed it by more than the work between two checks. That work is the largest of the shipped node procedures run on the largest node, as measured by `bound_gcd` with all checks of the source active: `@@MAXGAP_D@@` operations; the figure used is `@@GAP_GCD_BOUND@@`.

Stage E. A shift costs the powering `x -> (x+a)^((p-1)/2) mod G` with `d <= @@DEGCAP@@` (253 squarings and at most 125 multiplications by `x + a` modulo `G`) and one gcd; the cost is monotone in `d`. `bound_root.c` executes one shift of `find_root` on a polynomial of degree @@DEGCAP@@ with no roots: `@@W_SHIFT@@` operations.
The budget for the run is `@@NCEN@@ x 40 x @@W_SHIFT@@ = @@BUDGET_ROOT@@` operations, so it is never reached before the cap of 40 shifts per centre; one shift is also the largest work between two checks.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F_j(c+s) = F_j(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes
and compares them; the output is only emitted if they are equal and the pairs differ. Independent of the program, the pairs in `certificates/` are checked by the organizer's hash implementation.

## 6. Ledger (primitive operations; `C(@@R@@) = @@C@@`)

Counts are the exact totals of the instrumented executions (`arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the @@C@@-operation unit charges).
The last column marks the stages whose cost depends on the data; every other stage costs exactly the same in every execution.

@@LEDGER_TABLE@@

Worst case for @@NCEN@@ centres (every centre but the last fails or stops after stage D and the last runs up to stage G; every data-dependent stage is charged at its halt budget plus the largest work between two checks):
`@@WORST_FORMULA@@ = @@WORST_TOTAL@@` operations `= @@WORST_UNITS@@` units, `time_log2 = @@TIME_LOG2_EXACT@@`, claimed as `@@TIME_LOG2@@` (rounded up). One centre: budget `@@ONE_TOTAL@@` operations, `@@TIME_LOG2_ONE@@`.
Composition by type of the ledger run (init included, @@LEDGER_CENTRES@@ centre(s) executed): add `@@T_ADD@@`, sub `@@T_SUB@@`, mul `@@T_MUL@@`, sqr `@@T_SQR@@`, loads `@@T_LD@@`, stores `@@T_ST@@`, control `@@T_CTL@@`, random words `@@T_RND@@`, unit charges `@@T_PERM@@`.

Stage C in detail (m = @@M@@): Newton for MU: @@NEWTON@@ operations; prefix and scaling: @@PREFIX@@; @@STEPS@@ squaring steps at @@PER_STEP@@ operations each (arith @@PER_STEP_ARITH@@).
A step is one forward and one inverse transform of size @@NN@@ for the square, a forward transform, a row-wise generated operand transform and an inverse transform of size @@NN@@ for the quotient, the same at size @@NP@@ for `q g`,
plus the fold, shift and subtraction loops over `m` elements.

### 6.1 Ledger recomputation

The worst-case sum above, recomputed from the table entries:

```python
@@LEDGER_PY@@
```

## 7. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer (each buffer below is one allocation), at the moment of stage C:

| item | elements | bytes |
|---|---:|---:|
@@MEM_TABLE@@
| scalars, line constants, plans | | @@SCALAR_BYTES@@ |
| tracked heap peak | | @@HEAP_PEAK@@ |

Tracked peak per stage of the first centre (bytes, the allocator's high-water mark inside the stage, twiddle table included): @@STAGE_PEAKS@@. The allocator's global peak over the whole run is `@@HEAP_PEAK@@`. To the heap peak we add the static image of the executable (code, constants and tables:
@@STATIC_DESC@@), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit and finished normally) and 4,096 bytes for the allocator's own metadata:
`@@MEM_BYTES@@` bytes `= 2^@@MEM_LOG2@@`. The memory penalty is `max(0, @@MEM_LOG2@@ - 20) = @@MEM_PEN@@`.
Not counted, as they are not part of the abstract program: the dynamic C library and loader mappings and kernel structures of the host process (the program uses `memcpy`, `printf` and an allocator only for I/O and buffer management).
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. Success probability

The random experiment: the program draws `c_k` (one random word per centre) and the root-finder shifts, all independent and uniform; @@LINE_RULE@@; the run stops with an output at the first centre whose stage E returns a root and whose
verification passes, and fails after centre @@NCEN_M1@@ or at any halt of section 4.
For a line `j` let `q_j` be the probability that one centre on line `j`, with `c` uniform in `[0, 2^254)`, ends with a verified output without a halt. The claim uses no model of how many roots `g_c` has; it uses measured values of `q_j`.

**H1 (score-critical).** `q_j >= L_j` for each line used, where `L_j` is the Wilson lower confidence limit (one-sided 99.5 percent, `z = 2.576`) of the success fraction of the executions of the program with that line; and the centres of a run are independent.
@@SAMPLE_DESC@@

@@PERLINE_TABLE@@

The smallest lower limit is `@@PMIN@@` (line @@PMIN_LINE@@; @@LINES_USED@@). With `@@NCEN@@` independent centres every one of which succeeds with probability at least `@@PMIN@@`, the run succeeds with probability at least `1 - (1 - @@PMIN@@)^@@NCEN@@ = @@PRUN@@`, and the claim is `@@PCLAIM@@`.
The sample is the only support of H1: the confidence statement is statistical, each line's limit holds with confidence 99.5 percent, and nothing else (no root-count model, no extrapolation from smaller instances) enters the success probability or any budget.
Every halt of section 4 was active in every counted execution, so halted executions are failures in the fractions.
Parts that are not heuristics: the algebra of sections 2-3 (the digest polynomial, its exact degree and leading coefficient) and the exactness of the interpolation (checked by the executed program: collisions produced, section 5).
**Randomness.** The executed program draws `c` and the shifts from a 64-bit xorshift generator seeded by the run's seed argument; the cost model has independent uniform random 256-bit words as a primitive (charged: 1 + 2 control per word) and the claim uses that idealisation.

**H2 (supporting).** The charges of section 4.1 describe the executed program: the instrumentation counts each executed field operation, each element load/store and the stated control operations. The 16-element register block is the one structural assumption.
**H3 (supporting).** The halt budgets of section 4.4 are the only bounds on stages D and E; a halted execution is a failure counted in H1. No bound on the cost of stage D or E depends on a property of the data.

## 9. What is and is not provided

* The package contains the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7), the complete source of the executed program (section 10, every file verbatim, including the generated kernel header and its generator), and @@N_CERT@@ collision certificates (`certificates/`) checked by the organizer's hash.
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The dominant term is the @@STEPS@@ squaring steps of stage C at @@PER_STEP@@ operations each.
* Build. One build produced the ledger runs and the executions of section 8. The transform sizes go up to 3 * 2^@@NA@@ and the twiddle table has @@TWN@@ entries. The line-evaluation debug check of the source (`debug_check`) is off in every ledger and sample run. Conversions of runtime values into the internal representation (`c`, `N`) are conversions of program constants and are not charged.
* The cost claim uses the model of section 4.1; cache and bandwidth effects are outside that model.

## 10. Source of the executed program

Counters: `LD(n)`, `ST(n)`, `CTL(n)` add `n` to the load, store and control counters; `loopc(n)` adds 8 per element; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters;
`budget_check()` adds 2 control operations and stops the program when the charged work since the last `budget_arm()` exceeds the armed limit. Buffers are obtained from the tracked allocator (`NEW_FP`).
Build: `build.sh lean_attack` (`gcc -O3 -march=native` over the files below); budgets: `bound.sh @@R@@` (`bound_gcd`, `bound_root`); run: `lean_attack @@R@@ <centres> <seed> <first line> <verbose>`.

@@APPENDIX@@
