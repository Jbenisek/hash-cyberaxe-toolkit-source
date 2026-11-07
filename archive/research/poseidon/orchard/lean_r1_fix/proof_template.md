# Orchard Poseidon, r = 1: two free rounds on a line, odd-part polynomial, root finding (exact ledger, low memory)

## 1. Claim

Target: `poseidon-orchard-r1-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, one partial round 4, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = @@TIME_LOG2@@` in target-compression units (`C(1) = 237` primitive operations per unit): a worst-case budget for at most two
  independent centres, every executed operation of the program charged (section 6). A single centre costs `@@TIME_LOG2_ONE@@`.
* `memory_log2_bytes = @@MEM_LOG2@@` (`@@MEM_BYTES@@` bytes, section 7), so the normalized cost is `@@TIME_LOG2@@ + @@MEM_PEN@@ = @@SCORE@@`.
* `success_probability = 0.53`: two independent centres. The per-centre success rate measured on the target is @@N_SUCC@@ of @@N_CENTRES@@ complete executions; its Wilson 95% lower bound is @@WLO@@.
  With that lower bound for both centres the run succeeds with probability at least `1 - (1 - @@WLO@@)^2 = @@P2@@`, claimed as 0.53 (section 8). The Poisson root-count model (per centre `1 - exp(-1/2) = 0.3935`) is context only and is not used for the claim.
* The method (two free rounds on a special line, then the roots of a univariate polynomial) is a known approach. What is offered
  here is a complete finite implementation with an exact operation ledger and a low-memory schedule. Nothing here is an asymptotic estimate:
  every figure below is the count of an executed, instrumented program whose complete source is reproduced in section 10 (no omega = 2.8 substitution is used).
* The collisions stored in `certificates/` (@@N_CERT@@ pairs from @@N_CERT@@ different centres) are outputs of this program. They check the construction at the
  selected target with the organizer's hash; they are not part of the cost claim and the cost claim does not use them.

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

2.3 Digest polynomial. Rounds 2, 3 (full), 4 (partial, r = 1), 60, 61, 62, 63 (full) put seven S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F_j(W)` with `deg F_j <= 5^7 = D = 78125`. The leading coefficient is obtained by
propagating leading coefficients through the seven layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for each `j`:
`f_D(0) = 0x1c66a426cd2d5ec686ea41cae3a27d49c8724fffa0bc4f305029be8b2cce93c3`,
`f_D(1) = 0x23f4f4090b603b7edbc59c1e6873df7a90d68316f73ac9517f55080764cf3905`,
`f_D(2) = 0x191734549b1df57af01548d1bb07d507b21fdd533a2ab8e07e0dc05e02cd900e`
(computed; so `deg F_j = D` exactly). For random `tau`, `F_j(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau` for each `j`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F_j(W1) = F_j(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F_j(c + s) - F_j(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 39062`, `g_c` has degree exactly `m` and
leading coefficient `2 f_D(j)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)`. (Roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives
`s = 0` and `W1 = W2`.)

Construction of `g_c` by evaluation. `H = 49152 = 3 * 2^14` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F_j(c + zeta^i) - F_j(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 98304` evaluations of `F_j` are each charged as
one target-compression unit (`C(1) = 237` operations), although a line evaluation (affine start, six more rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, and the executed shifts, masks, ors, modulo operations and loop control of the bit-reversed index `layout_index`, which are counted inside that function) is charged on top.

## 4. The program (per centre; at most two centres)

```
centre k = 0, 1 (line j = k):
  A  c := uniform 254-bit word (one random word + 2 control ops)
  B  g := monic g_c, by section 3 (98304 evaluations + one inverse NTT of size 49152 + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; 238 modular squarings, 45 of the steps also multiply by S by a streaming shift)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products; classical quotient steps when the parameter is at most 48) ; if deg G = 0 the centre fails;
                                       if deg G > 8 the centre is abandoned
  E  S := a root of G                 (Cantor-Zassenhaus: random shift a, gcd(G, (x+a)^((p-1)/2) - 1); at most 40 tries)
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (237 operations each) are equal and the pairs differ -> output, stop.
```

Implemented halts (all enforced in the executed program; a check adds 2 control operations to the ledger): at most 2 centres; `deg G <= 8` (otherwise the centre is abandoned);
stage D is checked at every entry of the half-gcd recursion, after every matrix application and matrix product, in every iteration of the classical base case and at the end of the stage, and stops the program as soon as the work charged since the stage began exceeds
@@BUDGET_GCD@@ operations; the largest charged work between two consecutive checks seen in the ledger runs is @@GAP_GCD@@ operations, and the bound used below is @@GAP_GCD_BOUND@@;
stage E (all shifts of the whole run together) is checked before every shift (at most 40 shifts per centre) and stops the program when more than @@BUDGET_ROOT@@ operations have been charged in total; one shift costs at most @@GAP_ROOT_BOUND@@ operations (the whole
root finder cost at most @@ROOTWORST@@ in 320 planted tests with `d <= 8`). A halt is a failure of the whole run and is included in the probability argument (section 8).

### 4.1 Machine model and charging rules

Every item below is counted by the executing code at the statement that executes it; none is estimated. The complete source is in section 10.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications; `x^e`: 253 squarings, 124 multiplications; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation): `LD(n)` adds `n` to the load counter and `n` to the control counter, `ST(n)` likewise.
* every loop, whatever its body: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left). The code is not unrolled; `loopc(n)` adds exactly this.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, multiplication, modulo, comparison, conditional branch, and the selection of an element of the 16-word register block by a computed index. They are added with `CTL(k)` next to the statement that executes them, and data-dependent tests (for example the test of the twiddle pointer, the tests of the radix-3 stage) are charged per executed test.
* one iteration of the innermost butterfly loop of a transform block: 9 control operations (`t += 2*half`: shift and add; bound comparison; branch; `t + half`; the addresses of `x[t]` and `x[t+half]`; the compare and branch on the twiddle pointer), counted as `CTL(9 * nb + 2)` after the loop that executed `nb` butterflies. The loops over `j`, `tp`, the elements of a block and the blocks of a pass are charged with `loopc` and the statements `idx = (b + tp * s) << (l0 + j)` (4), `half = 1 << (k-1-j)` (3), the test `if (idx)` (2) and the twiddle address (1 or 2) are charged where they are written (section 10, `blk_fwd`, `pass_fwd`).
* working registers: the 16-word array `x` of a block is the register file. Its 16 words are loaded once and stored once per pass block (each with its address operation), and a selection of an element of `x` by a computed index is charged as above. This is the only register assumption.
* a call of the budget check: 2 control operations; a random word: 1 plus 2 control operations.
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion (253 iterations of 9, plus 3 iterations of 8 for the search of the top bit).
* small-degree work in stages E and F, in the line setup and in the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations (a loop costs 3 per iteration and every such loop iteration performs at least one arithmetic operation; the remaining 3 cover the index operations).
* the reduced permutation evaluations of stage B: 237 each (section 3). Nothing else is charged as a unit.

Example of the rule (from `blk_fwd`, section 10): the butterfly loop `for (t = tp; t < K; t += 2 * half) { bf_fwd(&x[t], &x[t + half], w); nb++; }` is followed by `CTL(9 * nb + 2)`; `bf_fwd` performs the subtraction, the addition and, when `w` is set, the multiplication, each counted by the field routine.
All buffers are disjoint allocations and every index is below `2^17`, representable in one word. Every element read in a stage was written earlier in the same stage (the transform buffers are fully written by the first radix-3 stage before any pass reads them; operands are zero-extended by the radix-3 stage, never by reading stale slots).
Not charged (declared): conversion of constants to the internal Montgomery representation (constants of the program text), the bookkeeping of the allocator (`xalloc`, `xfree`: memory is accounted in section 7), the counter reads of the budget check beyond its 2 operations, formatting and printing.

### 4.2 Stage C: the powering schedule (in place, no stored spectra)

`N = 98304 = 3 * 2^15 >= 2m - 1` and `N' = 49152 = 3 * 2^14 >= m + 1`. A transform of size `3 * 2^a` is a twiddle-free radix-3 stage (Good-Thomas; `p - 1` is divisible by `3 * 2^32`) followed by three independent
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
The spectra of `MU` and of `g` are not stored: for each multiplication the second operand is transformed one row of the Good-Thomas layout at a time into a buffer `tmp` of `2^15` elements,
immediately multiplied into the corresponding row of `Y`, and discarded. (About 1.5 transform equivalents per step more than with cached spectra; this is what the ledger below pays for the memory saved.)
`MU` is computed once per centre from `g` by Newton iteration with the same row-wise products. The first 15 exponent bits after the leading one are absorbed by starting from the monomial `S^v` (`v < m`, 16 bits).

### 4.3 Stage D: half-gcd

Half-gcd of Knuth-Schoenhage / Thull-Yap type with parameter `k1 = k/2`; products by the same row-wise NTT products (operands generated one row at a time, outputs accumulated in a single buffer), classical Euclid below parameter 48,
ownership of inputs passed down the recursion so that no input is kept after its last use. The ledger counts every operation of the executed recursion (planted-gcd tests against classical Euclid on the same input: identical gcd).

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F_j(c+s) = F_j(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes
and compares them; the output is only emitted if they are equal and the pairs differ. Independent of the program, the pairs in `certificates/` are checked by the organizer's hash implementation.

## 6. Ledger (primitive operations; `C(1) = 237`)

Counts are the exact totals of the instrumented execution (`arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 237-operation unit charges).
The last column marks the stages whose cost depends on the data; every other stage costs exactly the same in every execution.

@@LEDGER_TABLE@@

Worst case for two centres (centre 0 fails or is abandoned after stage D, centre 1 runs everything up to stage G):
`@@WORST_FORMULA@@ = @@WORST_TOTAL@@` operations `= @@WORST_UNITS@@` units, `time_log2 = @@TIME_LOG2_EXACT@@`, claimed as `@@TIME_LOG2@@` (rounded up). One centre: budget `@@ONE_TOTAL@@` operations, `@@TIME_LOG2_ONE@@`.
The measured per-centre totals of the ledger run (@@N_RUNS@@ centres, init excluded) are @@MIN_ALL@@ and @@MAX_ALL@@; with init, the single-centre budget `@@ONE_TOTAL@@` exceeds the larger one by @@MARGIN@@ operations. The data-dependent stage D enters the worst case with its full budget.
Composition by type of the complete two-centre ledger run (centre 0 fails after stage D, centre 1 succeeds; init included; the control counter includes the address operations of loads and stores): add `@@T_ADD@@`, sub `@@T_SUB@@`, mul `@@T_MUL@@`, sqr `@@T_SQR@@`, loads `@@T_LD@@`, stores `@@T_ST@@`, control `@@T_CTL@@`, random words `@@T_RND@@`, unit charges `@@T_PERM@@`.

Stage C in detail (m = 39062): Newton for MU: @@NEWTON@@ operations; prefix and scaling: @@PREFIX@@; @@STEPS@@ squaring steps at @@PER_STEP@@ operations each (arith @@PER_STEP_ARITH@@).
A step is one forward and one inverse transform of size 98304 for the square, a forward transform, a row-wise generated operand transform and an inverse transform of size 98304 for the quotient, the same at size 49152 for `q g`,
plus about 4m loads, stores and fold operations with their loop and index control.

@@XCHECK@@

### 6.1 Ledger recomputation

The worst-case sum above, recomputed from the table entries:

```python
@@LEDGER_PY@@
```

## 7. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer (each buffer below is one allocation), at the moment of stage C:

| item | elements | bytes |
|---|---:|---:|
| twiddle table `rho^j`, `j < 2^14` | 16384 | 524288 |
| `Y` (transform buffer, `3 * 2^15`) | 98304 | 3145728 |
| `tmp` (one transform row, `2^15`) | 32768 | 1048576 |
| `MU` | 39061 | 1249952 |
| `g` | 39063 | 1250016 |
| `F` (fold / result) | 39062 | 1249984 |
| scalars, line constants, plans | | @@SCALAR_BYTES@@ |
| tracked heap peak | | @@HEAP_PEAK@@ |

Tracked peak per stage of the first centre (bytes, the allocator's high-water mark inside the stage, twiddle table included): @@STAGE_PEAKS@@. The stage D peak consists of the two inputs (2 x 1,250,016), the matrix of the first recursive call, the two results of the first application (2 x 49152 elements), the two transform rows (2 x 16384 elements) and the table; it equals the stage C value to within a few bytes by a coincidence of sizes. The allocator's global peak over the whole run is `@@HEAP_PEAK@@`. To the heap peak we add the static image of the executable (code, constants and tables:
@@STATIC_DESC@@), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit and finished normally) and 4,096 bytes for the allocator's own metadata:
`@@MEM_BYTES@@` bytes `= 2^@@MEM_LOG2@@`. The memory penalty is `max(0, @@MEM_LOG2@@ - 20) = @@MEM_PEN@@`.
Not counted, as they are not part of the abstract program: the dynamic C library and loader mappings and kernel structures of the host process (the program uses `memcpy`, `printf` and an allocator only for I/O and buffer management).
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. Success probability

The random experiment: the program draws `c_0`, `c_1` (one random word each) and the root-finder shifts, all independent and uniform; it stops with an output at the first centre whose `G` has a root (and the verification passes), and fails after the second centre or at any halt. Per centre the program succeeds iff `G` has at least one root. Let `K` be the number of nonzero squares among the `F_p`-roots of `g_c`.

**H1 (score-critical): per-centre success rate at least @@WLO@@.** The claim rests on the measured per-centre success rate of the program on the target, not on a model. @@N_CENTRES@@ complete single-centre executions of the program at the target (@@N_A@@ with an earlier build, @@N_B@@ with the final build; identical arithmetic; seeds 1000w+i (earlier build) and 10000w+i (final build), line j = seed mod 3, centre `c` drawn by the program's own generator) gave @@N_SUCC@@ successes (rate @@RATE@@, Wilson 95% interval [@@WLO@@, @@WHI@@]); every success was verified by two independent hash implementations. The runs pool the three lines: line 0 succeeded in @@BYJ0@@, line 1 in @@BYJ1@@, line 2 in @@BYJ2@@ runs. The program uses the same kind of line choice (centre `k` of a run uses line `(j0 + k) mod 3`, the two centres of a run lie on two different lines), so the pooled rate describes each of its centres. The root-count histogram of `G` was @@HIST@@.
Arithmetic of the claim: with per-centre success probability at least `q = @@WLO@@` and independent centres (fresh independent random words), the run succeeds with probability at least `1 - (1 - q)^2 = @@P2@@`; the total loss from the halts below is under `10^-6`; claimed `success_probability = 0.53`. Assumptions: the centres are independent of each other and of the sample; a centre of the program behaves like a centre of the sample (the sample used a deterministic generator for `c`); the lower end of a 95% interval holds for the true rate (this fails with probability about 2.5% by construction of the interval).
Context, not used for the claim: a random polynomial of degree `m` has on average one root in `F_p`, each root is a square with probability 1/2, so the number of useful roots is approximately Poisson with mean 1/2 and a centre succeeds with probability about `1 - exp(-1/2) = 0.3935` (two centres 0.632); toy analogues over a 38-bit prime (degrees 125 to 15625, up to 600,000 centres) gave 0.3937 +- 0.001. The sample rate @@RATE@@ is consistent with this model; the claim does not depend on it.
Parts that are not heuristics: the algebra of sections 2-3 (the digest polynomial, its exact degree and leading coefficient) and the exactness of the interpolation (checked by the executed program: collisions produced, section 5).
**Halts and caps as failures.** `P(K > 8)` is about `3.4e-9` under the Poisson context model (cap on `deg G`); the root finder reduces a squarefree `G` of degree `d >= 2` with probability at least `1 - 2^(1-d) >= 1/2` per shift, so `P(more than 40 shifts) < 2^-35`; the gcd budget (H3) is exceeded with negligible
probability. The total loss is below `10^-6`, so `P(success) >= @@P2@@ - 10^-6 > 0.53`.
**Randomness.** The executed program draws `c` and the shifts from a 64-bit xorshift generator seeded by the run's seed argument; the cost model has independent uniform random 256-bit words as a primitive (charged: 1 + 2 control per word) and the claim uses that idealisation.

**H3 (supporting).** The half-gcd cost on `(g, R - 1)` is concentrated: the Euclidean remainder sequence of two polynomials whose inputs are not special is normal (all quotients of degree 1) except with probability about `1/p` per
step; the stage has a hard budget (@@BUDGET_GCD@@ operations, about 1.5 times the largest observed cost; observed @@GCD_MIN@@ to @@GCD_MAX@@ in the @@N_RUNS@@ centres of the ledger run), a run exceeding it halts and counts as a failure. The worst-case total of section 6 charges the full budget for every centre.
**H2 (supporting).** The charges of section 4.1 describe the executed program: the instrumentation counts each executed field operation, each element load/store with its address operation, every loop iteration and the stated index and control operations. The 16-element register block is the one structural assumption.

## 9. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 10), @@N_CERT@@ machine-checked collision certificates (`certificates/`, from different centres and all three lines, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package may contain only declared Python experiments and certificates, so the C source is part of this document (section 10) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3` and run as `lean_attack 1 2 1001 2 1`.
* Ledger run. The counts of section 6 come from one complete execution with two centres (seed 1001, first line 2: centre 0 fails after stage D, centre 1 succeeds). Earlier builds of the program charged loop control at 4 per 16 elements; their figures are not used. The success statistics of section 8 come from runs whose arithmetic is identical to this build (the cost counters do not influence control flow, except the halts, which did not trigger).
* The scan allowance in the worst-case sum is @@GCD_SCAN@@ operations per centre (the scan for the degree of R-1 executes at most one test per coefficient, 9 operations each; in the ledger run it executed @@SCAN_OBS@@). The line-evaluation debug check of the source (`debug_check`) is off (0) in the ledger run. Conversions of runtime values into the internal representation (`c`, `N`) are conversions of program constants and are not charged.
* The cost claim assumes the model of section 4.1; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.

## 10. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters;
`budget_check()` adds 2 control operations and stops the program when the charged work since the last `budget_arm()` exceeds the armed limit. Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: `common.h`, `common.c`, `pallas.h`, `pallas.c`, `pallas_consts.h`, `attack.h`, `hgcd.h`, `ntt.c`, `poly.c`, `lean.c`, `line.c`, `euclid.c`, `hgcd.c`, `lean_attack.c`.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs.

@@APPENDIX@@
