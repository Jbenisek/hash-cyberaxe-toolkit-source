# Orchard Poseidon, r = 1: two free rounds on a line, odd-part polynomial, root finding (exact ledger, low memory)

## 1. Claim

Target: `poseidon-orchard-r1-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, one partial round 4, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = 25.837` in target-compression units (`C(1) = 237` primitive operations per unit): a worst-case budget for at most two
  independent centres, every operation of the program charged (section 6). A single centre costs `24.838`.
* `memory_log2_bytes = 23.042` (`8,636,079` bytes, section 7), so the normalized cost is `25.837 + 3.042 = 28.879`.
* `success_probability = 0.60`: two independent centres, each succeeding with probability `1 - exp(-1/2) = 0.3935` under heuristic H1
  (two centres: 0.632). The claim 0.60 needs only a per-centre success probability of at least 0.37.
* The method (two free rounds on a special line, then the roots of a univariate polynomial) is a known approach. What is offered
  here is a complete finite implementation with an exact operation ledger and a low-memory schedule. Nothing here is an asymptotic estimate:
  every figure below is the count of an executed, instrumented program (no omega = 2.8 substitution is used).
* The collisions stored in `certificates/` (16 pairs from 16 different centres) are outputs of this program. They check the construction at the
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
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store,
four control operations for the bit-reversed index) is charged on top.

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
800,000,000 operations; the largest charged work between two consecutive checks seen in the ledger runs is 21,617,616 operations, and the bound used below is 28,000,000;
stage E (all shifts of the whole run together) is checked before every shift (at most 40 shifts per centre) and stops the program when more than 10,000,000 operations have been charged in total; one shift costs at most 1,000,000 operations (the whole
root finder cost at most 761,102 in 320 planted tests with `d <= 8`). A halt is a failure of the whole run and is included in the probability argument (section 8).

### 4.1 Machine model and charging rules

Every item below is counted by the executing library; none is estimated.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications; `x^e`: 253 squarings, 124 multiplications; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each. Working registers are charged as a block of 16 elements: a pass of four butterfly layers loads 16 elements, keeps them in registers, and stores them (this is the only register assumption).
* loop control: 4 operations (index update, bound comparison, branch, spare) per 16 elements of a straight loop; 12 per 16-element transform block (4 loop operations plus 8 for the twiddle pointers: one shift and one addition for each of the four layers); a call of the budget check: 2; a random word: 1 plus 2.
* small-degree work in stages E and F is charged generously: 2 loads, 1 store and 1 control operation on top of every arithmetic operation.
* the reduced permutation evaluations of stage B: 237 each (section 3). Nothing else is charged as a unit.
Addressing. Each transform pass kernel is specialised for its constant stride (two plan sizes, four passes, forward / inverse / fused kernels), so the 16 element addresses of a block are a base register plus immediates and the base update is part of the control operations above; the dense loops of stages B-D are straight loops with the 4-per-16 rule; the radix-3 stage and its row-wise operand generation are split into index ranges on which the set of non-zero inputs and the cyclic offset are constant (the boundaries come from the operand lengths, computed once per call), so no modular index arithmetic is executed per element. The implementation measured below uses generic loops with the same counts; specialised kernels would enlarge the code by a few tens of kilobytes (under 1% of the memory figure, not included). All buffers are disjoint allocations and every index is below `2^17`, representable in one word. Every element read in a stage was written earlier in the same stage (the transform buffers are fully written by the first radix-3 stage before any pass reads them; operands are zero-extended by the radix-3 stage, never by reading stale slots).
Not charged (declared): conversion of constants to the internal Montgomery representation (constants of the program text), formatting and printing.

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

Counts are the exact totals of the instrumented executions (`arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 237-operation unit charges).
The last column marks the stages whose cost depends on the data; every other stage costs exactly the same in every execution.

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table `rho^j` (16384 entries), roots of unity (once per run) | 17,359 | 20,480 | 37,839 | no |
| line setup (constants of the line, 1 inversion) | 391 | 1,564 | 1,955 | no |
| random centre | 0 | 3 | 3 | no |
| B: 98304 line evaluations (units) + inverse NTT 49152 + normalisation | 1,436,260 | 24,567,311 | 26,003,571 | no |
| C: S^((p-1)/2) mod g (lean schedule) | 3,536,772,927 | 2,704,810,640 | 6,241,583,567 | no |
| D: gcd(g, R-1) (half-gcd), as observed in this run (includes the scan for the degree of R-1, 78,126 ops) | 355,770,866 | 434,514,508 | 790,285,374 | yes: budget 800,000,000 |
| E: root finding (deg G <= 8), at most 40 shifts per centre | - | - | 5 (one root) to 761,102 (320 planted tests, d <= 8) | yes: budget 10,000,000 in total |
| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | about 18,300 observed | allowance 200,000 for two executions |

Worst case for two centres (centre 0 fails or is abandoned after stage D, centre 1 runs everything up to stage G):
`init + 2 x (line + random + B + C + D budget + D gap bound + scan) + E budget + E gap bound + F,G allowance = 37,839 + 2 x 7,095,689,096 + 10,000,000 + 1,000,000 + 200,000 = 14,202,616,031` operations `= 59,926,649.9` units, `time_log2 = 25.83669`, claimed as `25.837` (rounded up). One centre: budget `7,106,926,935` operations, `24.838`.
The measured totals of complete single-centre executions (39 executions in the campaign of section 8) lie in `[7,057,874,470, 7,057,961,691]`, below the budget of one centre (`7,106,926,935`) by at least 48,965,244 operations.
Composition by type of the complete two-centre ledger run (centre 0 fails after stage D, centre 1 succeeds; init included): add `2,715,539,688`, sub `2,534,837,889`, mul `2,470,953,120`, sqr `66,646,268`, loads `2,997,163,555`, stores `1,663,304,782`, control `1,620,758,761`, random words `2`, unit charges `46,596,096`.

Stage C in detail (m = 39062): Newton for MU: 40,263,761 operations; prefix and scaling: 175,813; 238 squaring steps at 26,055,226 operations each (arith 14,769,136).
A step is one forward and one inverse transform of size 98304 for the square, a forward transform, a row-wise generated operand transform and an inverse transform of size 98304 for the quotient, the same at size 49152 for `q g`,
plus about 4m loads, stores and fold operations.

Analytic cross-check of the arithmetic of a step (a reader can recompute it). A dense forward or inverse transform of size 3 * 2^a does, in its three rows of length 2^a, 3 (a 2^(a-1) - (2^a - 1)) multiplications (the butterflies with twiddle index 0 are free) and 3 a 2^a additions or subtractions, and its radix-3 stage 8 * 2^a operations. For a = 15 this is 638,979 + 1,474,560 + 262,144 = 2,375,683 operations, for a = 14 it is 1,114,115. A step has a square (forward + inverse at a = 15, plus 98,304 pointwise squarings), a quotient product (forward of the operand, row-wise forward of MU, inverse: three transforms at a = 15, plus 98,304 pointwise products) and the product with g at a = 14 (three transforms, plus 49,152 pointwise products), plus about 92,895 operations of folding, subtraction and shifts. Upper estimate: 4,849,670 + 7,225,353 + 3,391,497 + 92,895 = 15,559,415 arithmetic operations per step, against 14,769,136 measured; the measured value is lower because the radix-3 stage skips the zero part of the padded operands and the inverse radix-3 stage computes only the needed outputs.

### 6.1 Ledger recomputation

The worst-case sum above, recomputed from the table entries:

```python
from math import ceil, log2
C = 237
init = 37839
line, rnd, build, power = 1955, 3, 26003571, 6241583567
d_budget, d_gap, scan = 800000000, 28000000, 100000
e_budget, e_gap, fg = 10000000, 1000000, 200000
per_centre = line + rnd + build + power + d_budget + d_gap + scan
N = init + 2 * per_centre + e_budget + e_gap + fg
print('N =', format(N, ','))
print('units =', round(N / C, 1))
print('time_log2 =', '%.5f' % log2(N / C), ' claimed', ceil(log2(N / C) * 1000) / 1000)
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
| scalars, line constants, plans | | 96 |
| tracked heap peak | | 8,468,640 |

Tracked peak per stage of the first centre (bytes, the allocator's high-water mark inside the stage, twiddle table included): line_setup 524,288; random centre 524,288; build g 3,347,168; S^((p-1)/2) mod g 8,468,544; gcd(g, S^h-1) 8,468,640. The stage D peak consists of the two inputs (2 x 1,250,016), the matrix of the first recursive call, the two results of the first application (2 x 49152 elements), the two transform rows (2 x 16384 elements) and the table; it equals the stage C value to within a few bytes by a coincidence of sizes. The allocator's global peak over the whole run is `8,468,640`. To the heap peak we add the static image of the executable (code, constants and tables:
text 91,703 + data 768 + bss 5,336 = 97,807 bytes), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit and finished normally) and 4,096 bytes for the allocator's own metadata:
`8,636,079` bytes `= 2^23.042`. The memory penalty is `max(0, 23.042 - 20) = 3.042`.
Not counted, as they are not part of the abstract program: the dynamic C library and loader mappings and kernel structures of the host process (the program uses `memcpy`, `printf` and an allocator only for I/O and buffer management).
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. Success probability

The random experiment: the program draws `c_0`, `c_1` (one random word each) and the root-finder shifts, all independent and uniform; it stops with an output at the first centre whose `G` has a root (and the verification passes), and fails after the second centre or at any halt. Per centre the program succeeds iff `G` has at least one root. Let `K` be the number of nonzero squares among the `F_p`-roots of `g_c`.

**H1 (score-critical).** For `c` uniform in `[0, 2^254)` (statistically `2^-129` from uniform on `F_p`) and each `j`, `K` is distributed as Poisson with mean `1/2` (the number of `F_p`-roots of a random polynomial of degree `m`
has mean 1, each root is a square with probability 1/2 independently), so `P(K >= 1) = 1 - exp(-1/2) = 0.3935`; the trials of different centres (and lines) are independent. With two centres `P = 1 - (1 - 0.3935)^2 = 0.632`.
Support: (i) 65 complete single-centre executions of the program at the target (26 with an earlier build, 39 with the final build; identical arithmetic; seeds 1000w+i (earlier build) and 10000w+i (final build), line j = seed mod 3) gave 28 successes (rate 0.431, Wilson 95% interval [0.318, 0.552]) and every success was verified by two
independent hash implementations; the root-count histogram of `G` was 0 roots: 37, 1 root: 20, 2 roots: 7, 3 roots: 1; (ii) earlier toy analogues of the same construction (38-bit prime with the same 2-adicity pattern, random constants, degrees 125 to 15625, up to 600,000 centres)
gave rates 0.3937 +- 0.001 at degree 125 and consistent values at the larger degrees (reported, not shipped). The target-size sample cannot resolve 0.3935 from 0.39 (that is why two centres are used); the claim 0.60 stays valid for any per-centre rate
of at least 0.37; the target-size sample alone does not establish that (lower end of its 95% interval: 0.318), so the claim rests on H1 and not on the sample.
Parts that are not heuristics: the algebra of sections 2-3 (the digest polynomial, its exact degree and leading coefficient) and the exactness of the interpolation (checked by the executed program: collisions produced, section 5).
**Halts and caps as failures.** `P(K > 8)` is `3.4e-9` for Poisson(1/2) (cap on `deg G`); the root finder reduces a squarefree `G` of degree `d >= 2` with probability at least `1 - 2^(1-d) >= 1/2` per shift, so `P(more than 40 shifts) < 2^-35`; the gcd budget (H3) is exceeded with negligible
probability. The total loss is below `10^-6`, so `P(success) >= 0.632 - 10^-6 > 0.60`.
**Randomness.** The executed program draws `c` and the shifts from a 64-bit xorshift generator seeded by the run's seed argument; the cost model has independent uniform random 256-bit words as a primitive (charged: 1 + 2 control per word) and the claim uses that idealisation.

**H3 (supporting).** The half-gcd cost on `(g, R - 1)` is concentrated: the Euclidean remainder sequence of two polynomials whose inputs are not special is normal (all quotients of degree 1) except with probability about `1/p` per
step; the stage has a hard budget (800,000,000 operations; observed 790,284,664 to 790,285,374 in 39 executions), a run exceeding it halts and counts as a failure.
**H2 (supporting).** The charges of section 4.1 describe the executed program: the instrumentation counts each executed field operation, each element load/store and the stated control operations. The 16-element register block is the one structural assumption.

## 9. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7, 10), 16 machine-checked collision certificates (`certificates/`, from different centres and all three lines, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* Not provided: the C source of the instrumented library (the package may contain only declared Python experiments); the counts of section 6 are therefore not recomputable by a reader. The structure of every stage and the charging rules
  are given; the dominant term is the 238 squaring steps of stage C at 26,055,226 operations each.
* Builds. Earlier build (26 campaign executions, seeds 1000w+i): same arithmetic and outputs, control charge 4 per transform block, budgets 760,000,000 (D) and 40,000,000 (E); its cost figures are not used here. Final build (the ledger runs and 39 campaign executions, seeds 10000w+i): control charge 12 per transform block, budgets 800,000,000 (D) and 10,000,000 (E), the budget checks of section 4, and extra counter output. Seeds 2000 and 3000 re-run with the final build gave the same collisions and the same arithmetic operation counts (3,893,983,768 and 3,893,983,802). The success statistics pool both builds; every cost range quoted comes from final-build executions only.
* The scan allowance in the worst-case sum is 100,000 operations per centre (the scan for the degree of R-1 costs 78,126 and is inside the observed stage D totals). The line-evaluation debug check of the source (`debug_check`) is off (0) in every ledger and campaign run. Conversions of runtime values into the internal representation (`c`, `N`) are conversions of program constants and are not charged.
* The cost claim assumes the model of section 4.1; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.

## 10. Appendix: executed code of the charged stages (verbatim excerpts of the instrumented implementation)

Counters: `LD(n)`, `ST(n)`, `CTL(n)` add `n` to the load, store and control counters; `loopc(n)` adds 4 per 16 elements; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters;
`budget_check()` adds 2 control operations and stops the program when the charged work since the last `budget_arm()` exceeds the armed limit. In `blk_fwd` the twiddle `tw[idx << shift]` is
one load. Buffers are obtained from the tracked allocator (`NEW_FP`).

### lean.c: Newton iteration for MU (row-wise products)

```c
static void newton_lean(fp *MU, const fp *g, size_t m, fp *GR, fp *Y, fp *tmp) {
    size_t L = m - 1;
    for (size_t i = 0; i < L; i++) GR[i] = g[m - i];
    LD(L); ST(L); loopc(L);
    fp one; fp_set_one(&one);
    if (!fp_eq(&GR[0], &one)) { fprintf(stderr, "newton: g not monic\n"); exit(6); }
    MU[0] = one; ST(1);
    size_t l = 1;
    while (l < L) {
        size_t l2 = 2 * l < L ? 2 * l : L;
        plan_t P1 = plan3_for_len(l2 + l - 1);
        conv_mulc_otf(&P1, Y, MU, 0, l, tmp, GR, l2, 0, l2);
        fp inv1; plan_invN(&P1, &inv1);
        for (size_t i = 0; i < l2 - l; i++) fp_mul(&Y[i], &Y[l + i], &inv1);
        LD(l2 - l); ST(l2 - l); loopc(l2 - l);
        plan_t P2 = plan3_for_len(l2 - 1);
        conv_mulc_otf(&P2, Y, Y, 0, l2 - l, tmp, MU, l, 0, l2 - l);
        fp inv2; plan_invN(&P2, &inv2);
        for (size_t i = 0; i < l2 - l; i++) { fp t; fp_mul(&t, &Y[i], &inv2); fp_neg(&MU[l + i], &t); }
        LD(l2 - l); ST(l2 - l); loopc(l2 - l);
        l = l2;
    }
    for (size_t i = 0; i < L / 2; i++) { fp t = MU[i]; MU[i] = MU[L - 1 - i]; MU[L - 1 - i] = t; }
    LD(L); ST(L); loopc(L);
}
```

### lean.c: stage C, the lean powering loop

```c
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
    int top = 255; while (top > 0 && !ebit(E, top)) top--;
    size_t v = 1; int bit = top;
    while (bit >= 1 && ((v << 1) | (size_t)ebit(E, bit - 1)) < m) { v = (v << 1) | (size_t)ebit(E, bit - 1); bit--; CTL(2); }
    for (size_t i = 0; i < m; i++) fp_set_zero(&Y[i]);
    ST(m); loopc(m);
    { fp invN; plan_invN(&PN, &invN); Y[v] = invN; ST(1); }
    snap_t sC = snap();
    int steps = 0;
    for (int b = bit - 1; b >= 0; b--) {
        conv_sq(&PN, Y, m, 2 * m - 1);
        for (size_t i = 0; i < m; i++) {
            if (i + Np <= 2 * m - 2) { fp_add(&F[i], &Y[i], &Y[i + Np]); LD(2); } else { F[i] = Y[i]; LD(1); }
        }
        ST(m); loopc(m);
        for (size_t i = 0; i + 1 < m; i++) Y[i] = Y[m + i];
        LD(m - 1); ST(m - 1); loopc(m - 1);
        conv_mulc_otf(&PN, Y, Y, 0, m - 1, tmp, MU, m - 1, gamma, m - 1);
        conv_mulc_otf(&PNp, Y, Y, 0, m - 1, tmp, g, m + 1, 0, m);
        for (size_t i = 0; i < m; i++) fp_sub(&Y[i], &F[i], &Y[i]);
        LD(2 * m); ST(m); loopc(m);
        if (ebit(E, b)) mulx_(Y, g, m);
        CTL(3);
        steps++;
        if (!quiet && steps % 32 == 0) fprintf(stderr, "  lean step %d/%d\n", steps, bit);
    }
    { fp Nf; uint64_t vv[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, vv);
      for (size_t i = 0; i < m; i++) fp_mul(&F[i], &Y[i], &Nf);
      LD(m); ST(m); loopc(m); }
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

### ntt.c: one 16-element register block (forward layers)

```c
static inline void blk_fwd(fp *x, int k, int l0, size_t b, size_t s, int shift) {
    size_t K = (size_t)1 << k;
    for (int j = 0; j < k; j++) {
        size_t half = (size_t)1 << (k - 1 - j);
        for (size_t tp = 0; tp < half; tp++) {
            size_t idx = (b + tp * s) << (l0 + j);
            const fp *w = NULL;
            if (idx) { w = &tw[idx << shift]; LD(1); }
            for (size_t t = tp; t < K; t += 2 * half) bf_fwd(&x[t], &x[t + half], w);
        }
    }
}
```

### ntt.c: one forward pass

```c
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++)
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            for (size_t t = 0; t < G; t++) x[t] = base[t * s];
            LD(G);
            blk_fwd(x, k, l0, b, s, P->shift);
            for (size_t t = 0; t < G; t++) base[t * s] = x[t];
            ST(G); CTL(12);
        }
}
```

### ntt.c: last forward pass + pointwise product + first inverse pass

```c
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t G = (size_t)1 << k, ngrp = P->n >> k;
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * G;
        for (size_t t = 0; t < G; t++) x[t] = base[t];
        LD(G);
        blk_fwd(x, k, l0, 0, 1, P->shift);
        if (mode == M_SQ) { for (size_t t = 0; t < G; t++) fp_sqr(&x[t], &x[t]); }
        else { const fp *cb = C + grp * G; for (size_t t = 0; t < G; t++) fp_mul(&x[t], &x[t], &cb[t]); LD(G); }
        blk_inv(x, k, l0, 0, 1, P->shift, P->n >> 1);
        for (size_t t = 0; t < G; t++) base[t] = x[t];
        ST(G); CTL(12);
    }
}
```

### ntt.c: one row of the radix-3 stage of the second operand

```c
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N; int c0 = P->c0 % 3;
    for (size_t i0 = 0; i0 < n; i0++) {
        int rot = (int)((c0 * (i0 % 3)) % 3);
        fp u[3], v[3], o[3]; int nz[3];
        for (int t = 0; t < 3; t++) {
            size_t pos = i0 + n * (size_t)t, idx = (pos + N - boff) % N;
            int any = 0; fp acc;
            for (; idx < lenB; idx += N) {            /* fold modulo x^N - 1 when lenB > N */
                if (!any) { acc = B[idx]; any = 1; } else fp_add(&acc, &acc, &B[idx]);
                LD(1);
            }
            nz[t] = any; if (any) u[t] = acc;
        }
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }
        if (mask == 0) fp_set_zero(&o[r]);
        else dft3_sel(v, mask, 1 << r, o);
        tmp[i0] = o[r]; ST(1);
    }
    CTL(4 * ((n + 2) / 3));
}
```

### ntt.c: product with a row-wise generated operand

```c
void conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                   const fp *B, size_t lenB, size_t boff, size_t outlen) {
    if (P->rows != 3) { fprintf(stderr, "conv_mulc_otf needs a rows==3 plan\n"); exit(9); }
    stageA_fwd(P, dst, src, off, len);
    for (int r = 0; r < 3; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        stageA_row(P, tmp, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmp, P, l0, P->kk[p]); l0 += P->kk[p]; }
        l0 = 0;
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; }
        pass_fused(row, P, l0, P->kk[P->npass - 1], M_MULC, tmp);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); }
    }
    stageA_inv(P, dst, outlen);
}
```

### ntt.c: sum of products with row-wise generated operands (used by the half-gcd)

```c
void conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                  const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen) {
    if (P->rows != 3) { fprintf(stderr, "conv_sum_otf needs a rows==3 plan\n"); exit(9); }
    size_t n = P->n;
    for (int r = 0; r < 3; r++) {
        fp *row = out + (size_t)r * n;
        for (int t = 0; t < nt; t++) {
            int l0 = 0;
            stageA_row(P, tmpA, r, A[t], lenA[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpA, P, l0, P->kk[p]); l0 += P->kk[p]; }
            l0 = 0;
            stageA_row(P, tmpB, r, B[t], lenB[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpB, P, l0, P->kk[p]); l0 += P->kk[p]; }
            if (t == 0) { for (size_t i = 0; i < n; i++) fp_mul(&row[i], &tmpA[i], &tmpB[i]); LD(2 * n); ST(n); }
            else if (sign[t] > 0) { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_add(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            else { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_sub(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            loopc(n);
        }
        int l0 = P->a;
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); }
    }
    stageA_inv(P, out, outlen);
}
```

### hgcd.c: application of the inverse matrix

```c
static void apply_inv(fp **c, size_t *lc, fp **d, size_t *ld, const mat_t *R, const fp *a, size_t la, const fp *b, size_t lb) {
    if (R->h == 0) { *c = dupv(a, la); *lc = la; *d = dupv(b, lb); *ld = lb; return; }
    size_t sumdeg = R->len[0] - 1;
    size_t nres = la - sumdeg;                     /* deg c + 1 */
    plan_t P = plan3_for_len(nres);
    size_t N = P.N;
    fp *tA = NEW_FP(P.n), *tB = NEW_FP(P.n);
    *c = NEW_FP(N); *d = NEW_FP(N);
    if (getenv("HG_TRACE")) fprintf(stderr, "apply_inv la=%zu lb=%zu sumdeg=%zu nres=%zu N=%zu cur=%zu\n", la, lb, sumdeg, nres, N, mem_cur);
    int odd = R->h & 1;
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
    fp inv; plan_invN(&P, &inv);
    for (size_t i = 0; i < nres; i++) fp_mul(&(*c)[i], &(*c)[i], &inv);
    for (size_t i = 0; i < nres; i++) fp_mul(&(*d)[i], &(*d)[i], &inv);
    LD(2 * nres); ST(2 * nres); loopc(2 * nres);
    *lc = trimlen(*c, nres); *ld = trimlen(*d, nres);
}
```

### hgcd.c: half-gcd recursion

```c
void hgcd(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    hgcd_stat_calls++;
    budget_check();
    size_t n = la - 1;
    if (lb == 0 || n - (lb - 1) > k) {
        if (want_mat) mat_set_identity(R);
        if (own) {
            if (c) { *c = (fp *)a; *lc = la; } else xfree((void *)a);
            if (d) { *d = (fp *)b; *ld = lb; } else xfree((void *)b);
        } else {
            if (c) { *c = dupv(a, la); *lc = la; }
            if (d) { *d = dupv(b, lb); *ld = lb; }
        }
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
        if (own) { cc = (fp *)a; dd = (fp *)b; } else { cc = dupv(a, la); dd = dupv(b, lb); }
        lcc = la; ldd = lb;
    } else {
        apply_inv(&cc, &lcc, &dd, &ldd, &R1, a, la, b, lb);
        budget_check();
        if (own) { xfree((void *)a); xfree((void *)b); }
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
    poly_divrem_naive(q, &lq, rem, &lrem, cc, lcc, dd, ldd);
    xfree(cc);
    if (dq > 32) hgcd_stat_bigdiv++;
    size_t k3 = k2 - dq;
    mat_t R2;
    hgcd(&R2, c, lc, d, ld, dd, ldd, rem, lrem, k3, want_mat, 1);
    if (want_mat) {
        mat_mulQ(&R1, q, lq);
        mat_mul(R, &R1, &R2);
        budget_check();
        mat_free(&R2);
    }
    mat_free(&R1);
    xfree(q);
}
```

### hgcd.c: gcd driver (inputs given away)

```c
size_t poly_gcd_fast_own(fp *out, size_t cap, fp *x, size_t lx, fp *y, size_t ly) {
    if (lx < ly) { fp *t = x; x = y; y = t; size_t tl = lx; lx = ly; ly = tl; }
    if (lx == ly && ly > 0) {   /* equal degrees: one division step first */
        fp *q = NEW_FP(1), *r = NEW_FP(lx); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
        xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
    }
    while (ly > 0) {
        size_t n = lx - 1;
        if (n <= 2 * (size_t)hgcd_base_k) {
            fp *q = NEW_FP(lx - ly + 1), *r = NEW_FP(lx); size_t lq, lr;
            poly_divrem_naive(q, &lq, r, &lr, x, lx, y, ly);
            xfree(x); x = y; lx = ly; y = r; ly = lr; xfree(q);
            continue;
        }
        fp *c, *d; size_t lc, ld;
        hgcd(NULL, &c, &lc, &d, &ld, x, lx, y, ly, (n + 1) / 2, 0, 1);
        if (ld == 0) { x = c; lx = lc; y = d; ly = 0; break; }
        fp *q = NEW_FP(lc - ld + 1), *r = NEW_FP(lc); size_t lq, lr;
        poly_divrem_naive(q, &lq, r, &lr, c, lc, d, ld);
        xfree(c); xfree(q);
        x = d; lx = ld; y = r; ly = lr;
    }
    budget_check();
    size_t l = lx > cap ? (size_t)-1 : monic_out(out, x, lx);
    xfree(x); xfree(y);
    return l;
}
```

### line.c: one line evaluation F_j(W) (stage B, charged as one unit)

```c
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
```

### line.c: stage B

```c
void build_g(fp *g, const line_t *L, const fp *c, int r, int debug_check) {
    size_t m = poly_degree_m(r);
    plan_t P = plan_for_len(m + 1, 1);
    size_t H = P.N;
    fp *buf = NEW_FP(H);
    fp theta, psi, ipsi, s, u, one;
    fp_set_one(&one);
    plan_theta(&P, &theta);
    if (!fp_sqrt(&psi, &theta)) { fprintf(stderr, "theta not a square?\n"); exit(7); }
    fp_inv(&ipsi, &psi);
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
    }
    ST(H); loopc(H); CTL(4 * H);   /* one store per point; s, u, c, psi, ipsi stay in registers; 4 control ops per point for the bit-reversed index */
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
    fp_inv(&il, &buf[m]);                    /* 1/(H g_m) */
    for (size_t k = 0; k < m; k++) fp_mul(&g[k], &buf[k], &il);
    fp_set_one(&g[m]);
    LD(m + 1); ST(m + 1); loopc(m + 1);
    xfree(buf);
}
```

