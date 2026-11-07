# Orchard Poseidon, r = 1: two free rounds on a line, odd-part polynomial, root finding (exact ledger, low memory)

## 1. Claim

Target: `poseidon-orchard-r1-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, one partial round 4, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `time_log2 = 28.781` in target-compression units (`C(1) = 237` primitive operations per unit): a worst-case budget for at most two
  independent centres, every executed operation of the program charged (section 6). A single centre costs `27.781`.
* `memory_log2_bytes = 23.043` (`8,638,495` bytes, section 7), so the normalized cost is `28.781 + 3.043 = 31.824`.
* `success_probability = 0.53`: two independent centres. The per-centre success rate measured on the target is 28 of 65 complete executions; its Wilson 95% lower bound is 0.318.
  With that lower bound for both centres the run succeeds with probability at least `1 - (1 - 0.318)^2 = 0.534`, claimed as 0.53 (section 8). The Poisson root-count model (per centre `1 - exp(-1/2) = 0.3935`) is context only and is not used for the claim.
* The method (two free rounds on a special line, then the roots of a univariate polynomial) is a known approach. What is offered
  here is a complete finite implementation with an exact operation ledger and a low-memory schedule. Nothing here is an asymptotic estimate:
  every figure below is the count of an executed, instrumented program whose complete source is reproduced in section 10 (no omega = 2.8 substitution is used).
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
8,800,000,000 operations; the largest charged work between two consecutive checks seen in the ledger runs is 170,599,074 operations, and the bound used below is 214,000,000;
stage E (all shifts of the whole run together) is checked before every shift (at most 40 shifts per centre) and stops the program when more than 10,000,000 operations have been charged in total; one shift costs at most 2,500,000 operations (the whole
root finder cost at most 1,541,920 in 320 planted tests with `d <= 8`). A halt is a failure of the whole run and is included in the probability argument (section 8).

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

| stage | arith | other | total | data-dependent |
|---|---:|---:|---:|---|
| init: twiddle table `rho^j` (16384 entries), roots of unity (once per run) | 17,359 | 126,238 | 143,597 | no |
| line setup (constants of the line, 1 inversion) | 391 | 3,519 | 3,910 | no |
| random centre | 0 | 3 | 3 | no |
| B: 98304 line evaluations (units) + inverse NTT 49152 + normalisation | 1,436,260 | 41,901,929 | 43,338,189 | no |
| C: S^((p-1)/2) mod g (lean schedule) | 3,536,772,927 | 42,022,748,610 | 45,559,521,537 | no |
| D: gcd(g, R-1) (half-gcd), as observed in this run (includes the scan for the degree of R-1) | 355,770,866 | 5,494,709,464 | 5,850,480,330 | yes: budget 8,800,000,000 |
| E: root finding (deg G <= 8), at most 40 shifts per centre | - | - | 12 in the ledger run, at most 1,541,920 in 320 planted tests | yes: budget 10,000,000 in total |
| F, G: sqrt, 6 powers by e, 2 reference hashes (success path only) | - | - | 36,680 observed | allowance 200,000 for two executions |

Worst case for two centres (centre 0 fails or is abandoned after stage D, centre 1 runs everything up to stage G):
`init + 2 x (line + random + B + C + D budget + D gap bound + scan) + E budget + E gap bound + F,G allowance = 143,597 + 2 x 54,617,263,639 + 10,000,000 + 2,500,000 + 200,000 = 109,247,370,875` operations `= 460,959,370.8` units, `time_log2 = 28.78006`, claimed as `28.781` (rounded up). One centre: budget `54,630,107,236` operations, `27.781`.
The measured per-centre totals of the ledger run (2 centres, init excluded) are 51,453,335,488 and 51,453,343,969; with init, the single-centre budget `54,630,107,236` exceeds the larger one by 3,176,619,670 operations. The data-dependent stage D enters the worst case with its full budget.
Composition by type of the complete two-centre ledger run (centre 0 fails after stage D, centre 1 succeeds; init included; the control counter includes the address operations of loads and stores): add `2,715,539,688`, sub `2,534,837,889`, mul `2,470,953,120`, sqr `66,646,268`, loads `2,997,348,202`, stores `1,663,304,782`, control `90,411,597,007`, random words `2`, unit charges `46,596,096`.

Stage C in detail (m = 39062): Newton for MU: 302,883,363 operations; prefix and scaling: 508,491; 238 squaring steps at 190,151,482 operations each (arith 14,769,136).
A step is one forward and one inverse transform of size 98304 for the square, a forward transform, a row-wise generated operand transform and an inverse transform of size 98304 for the quotient, the same at size 49152 for `q g`,
plus about 4m loads, stores and fold operations with their loop and index control.

Analytic cross-check of the arithmetic of a step (field operations only). A dense forward or inverse transform of size 3 * 2^a does, in its three rows of length 2^a, 3 (a 2^(a-1) - (2^a - 1)) multiplications (the butterflies with twiddle index 0 are free) and 3 a 2^a additions or subtractions, and its radix-3 stage 8 * 2^a operations. For a = 15 this is 638,979 + 1,474,560 + 262,144 = 2,375,683 operations, for a = 14 it is 1,114,115. A step has a square (forward + inverse at a = 15, plus 98,304 pointwise squarings), a quotient product (forward of the operand, row-wise forward of MU, inverse: three transforms at a = 15, plus 98,304 pointwise products) and the product with g at a = 14 (three transforms, plus 49,152 pointwise products), plus about 92,895 operations of folding, subtraction and shifts. Upper estimate: 4,849,670 + 7,225,353 + 3,391,497 + 92,895 = 15,559,415 arithmetic operations per step, against 14,769,136 measured; the measured value is lower because the radix-3 stage skips the zero part of the padded operands and the inverse radix-3 stage computes only the needed outputs.

### 6.1 Ledger recomputation

The worst-case sum above, recomputed from the table entries:

```python
from math import ceil, log2
C = 237
init = 143597
line, rnd, build, power = 3910, 3, 43338189, 45559521537
d_budget, d_gap, scan = 8800000000, 214000000, 400000
e_budget, e_gap, fg = 10000000, 2500000, 200000
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
text 94,119 + data 768 + bss 5,336 = 100,223 bytes), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit and finished normally) and 4,096 bytes for the allocator's own metadata:
`8,638,495` bytes `= 2^23.043`. The memory penalty is `max(0, 23.043 - 20) = 3.043`.
Not counted, as they are not part of the abstract program: the dynamic C library and loader mappings and kernel structures of the host process (the program uses `memcpy`, `printf` and an allocator only for I/O and buffer management).
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. Success probability

The random experiment: the program draws `c_0`, `c_1` (one random word each) and the root-finder shifts, all independent and uniform; it stops with an output at the first centre whose `G` has a root (and the verification passes), and fails after the second centre or at any halt. Per centre the program succeeds iff `G` has at least one root. Let `K` be the number of nonzero squares among the `F_p`-roots of `g_c`.

**H1 (score-critical): per-centre success rate at least 0.318.** The claim rests on the measured per-centre success rate of the program on the target, not on a model. 65 complete single-centre executions of the program at the target (26 with an earlier build, 39 with the final build; identical arithmetic; seeds 1000w+i (earlier build) and 10000w+i (final build), line j = seed mod 3, centre `c` drawn by the program's own generator) gave 28 successes (rate 0.431, Wilson 95% interval [0.318, 0.552]); every success was verified by two independent hash implementations. The runs pool the three lines: line 0 succeeded in 8 of 22, line 1 in 9 of 21, line 2 in 11 of 22 runs. The program uses the same kind of line choice (centre `k` of a run uses line `(j0 + k) mod 3`, the two centres of a run lie on two different lines), so the pooled rate describes each of its centres. The root-count histogram of `G` was 0 roots: 37, 1 root: 20, 2 roots: 7, 3 roots: 1.
Arithmetic of the claim: with per-centre success probability at least `q = 0.318` and independent centres (fresh independent random words), the run succeeds with probability at least `1 - (1 - q)^2 = 0.534`; the total loss from the halts below is under `10^-6`; claimed `success_probability = 0.53`. Assumptions: the centres are independent of each other and of the sample; a centre of the program behaves like a centre of the sample (the sample used a deterministic generator for `c`); the lower end of a 95% interval holds for the true rate (this fails with probability about 2.5% by construction of the interval).
Context, not used for the claim: a random polynomial of degree `m` has on average one root in `F_p`, each root is a square with probability 1/2, so the number of useful roots is approximately Poisson with mean 1/2 and a centre succeeds with probability about `1 - exp(-1/2) = 0.3935` (two centres 0.632); toy analogues over a 38-bit prime (degrees 125 to 15625, up to 600,000 centres) gave 0.3937 +- 0.001. The sample rate 0.431 is consistent with this model; the claim does not depend on it.
Parts that are not heuristics: the algebra of sections 2-3 (the digest polynomial, its exact degree and leading coefficient) and the exactness of the interpolation (checked by the executed program: collisions produced, section 5).
**Halts and caps as failures.** `P(K > 8)` is about `3.4e-9` under the Poisson context model (cap on `deg G`); the root finder reduces a squarefree `G` of degree `d >= 2` with probability at least `1 - 2^(1-d) >= 1/2` per shift, so `P(more than 40 shifts) < 2^-35`; the gcd budget (H3) is exceeded with negligible
probability. The total loss is below `10^-6`, so `P(success) >= 0.534 - 10^-6 > 0.53`.
**Randomness.** The executed program draws `c` and the shifts from a 64-bit xorshift generator seeded by the run's seed argument; the cost model has independent uniform random 256-bit words as a primitive (charged: 1 + 2 control per word) and the claim uses that idealisation.

**H3 (supporting).** The half-gcd cost on `(g, R - 1)` is concentrated: the Euclidean remainder sequence of two polynomials whose inputs are not special is normal (all quotients of degree 1) except with probability about `1/p` per
step; the stage has a hard budget (8,800,000,000 operations, about 1.5 times the largest observed cost; observed 5,850,477,654 to 5,850,480,330 in the 2 centres of the ledger run), a run exceeding it halts and counts as a failure. The worst-case total of section 6 charges the full budget for every centre.
**H2 (supporting).** The charges of section 4.1 describe the executed program: the instrumentation counts each executed field operation, each element load/store with its address operation, every loop iteration and the stated index and control operations. The 16-element register block is the one structural assumption.

## 9. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 10), 16 machine-checked collision certificates (`certificates/`, from different centres and all three lines, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package may contain only declared Python experiments and certificates, so the C source is part of this document (section 10) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3` and run as `lean_attack 1 2 1001 2 1`.
* Ledger run. The counts of section 6 come from one complete execution with two centres (seed 1001, first line 2: centre 0 fails after stage D, centre 1 succeeds). Earlier builds of the program charged loop control at 4 per 16 elements; their figures are not used. The success statistics of section 8 come from runs whose arithmetic is identical to this build (the cost counters do not influence control flow, except the halts, which did not trigger).
* The scan allowance in the worst-case sum is 400,000 operations per centre (the scan for the degree of R-1 executes at most one test per coefficient, 9 operations each; in the ledger run it executed 10). The line-evaluation debug check of the source (`debug_check`) is off (0) in the ledger run. Conversions of runtime values into the internal representation (`c`, `N`) are conversions of program constants and are not charged.
* The cost claim assumes the model of section 4.1; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it.

## 10. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters;
`budget_check()` adds 2 control operations and stops the program when the charged work since the last `budget_arm()` exceeds the armed limit. Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: `common.h`, `common.c`, `pallas.h`, `pallas.c`, `pallas_consts.h`, `attack.h`, `hgcd.h`, `ntt.c`, `poly.c`, `lean.c`, `line.c`, `euclid.c`, `hgcd.c`, `lean_attack.c`.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs.

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

/* ---- implemented budget halt: if the charged work since budget_arm() exceeds the limit the program stops (exit 77).
 * The check itself is charged as 2 control operations. */
void budget_arm(uint64_t limit, const char *stage);   /* limit 0 disarms */
void budget_check(void);
uint64_t budget_maxgap(void);                          /* largest charged work between two checks since the last arm */

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
void poly_newton_mu(fp *mu, const fp *g, size_t m);   /* mu[0..m-2] = floor(x^(2m-2)/g), g monic of degree m */
void plan_invN(const plan_t *P, fp *out);              /* 1/N as a field element (cached, counted once) */

/* ---- modular exponentiation x^E mod g (loop.c) */
typedef struct { size_t m; plan_t PN, PNp; size_t mu_ld; } loopinfo_t;
void powx_lean(fp *F, const fp *g, size_t m, const uint64_t E[4], int quiet);
void powx_mod(fp *out, const fp *g, size_t m, const uint64_t E[4], int force_rows3, int quiet);

/* ---- gcd (hgcd.c) */
size_t poly_gcd(fp *out, const fp *a, size_t la, const fp *b, size_t lb); /* returns degree+1 of monic gcd stored in out (out has room la) */
void   hgcd_stats(uint64_t *base_steps);

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

static uint64_t bud_limit = 0; static snap_t bud_start; static const char *bud_stage = ""; static uint64_t bud_last = 0, bud_maxgap = 0;
void budget_arm(uint64_t limit, const char *stage) { bud_limit = limit; bud_start = snap(); bud_stage = stage; bud_last = 0; bud_maxgap = 0; }
uint64_t budget_maxgap(void) { return bud_maxgap; }
void budget_check(void) {
    if (!bud_limit) return;
    X.ctl += 2;
    uint64_t cur = snap_total(snap_sub(snap(), bud_start));
    if (cur - bud_last > bud_maxgap) bud_maxgap = cur - bud_last;
    bud_last = cur;
    if (cur > bud_limit) {
        printf("BUDGET HALT in stage %s: charged work %llu exceeded %llu", bud_stage, (unsigned long long)cur, (unsigned long long)bud_limit);
        putchar(10);
        fflush(stdout); exit(77);
    }
}
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
size_t poly_gcd_fast_own(fp *out, size_t cap, fp *x, size_t lx, fp *y, size_t ly); /* returns (size_t)-1 if the gcd has more than cap coefficients */ /* inputs are xalloc'ed and given away */
extern int hgcd_k1_pct;
size_t poly_gcd_fast(fp *out, const fp *a, size_t la, const fp *b, size_t lb);
/* plain Euclid (reference, counted) */
size_t poly_gcd_naive(fp *out, const fp *a, size_t la, const fp *b, size_t lb);
/* a = q*b + r (naive); q has la-lb+1 coefficients (if la>=lb), r has lb-1 slots; returns trimmed lr; *lq set */
void poly_divrem_naive(fp *q, size_t *lq, fp *r, size_t *lr, const fp *a, size_t la, const fp *b, size_t lb);
extern int hgcd_base_k;
extern uint64_t hgcd_stat_calls, hgcd_stat_base_steps, hgcd_stat_bigdiv;
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
    amax_g = amax; nmax_g = (size_t)1 << amax;
    uint64_t pm1[4], e[4]; limbs_sub1(pm1, PALLAS_P);
    fp five; fp_from_u64(&five, 5);
    /* rho_max = 5^((p-1)/2^amax) (5 is a non-residue so this has exact order 2^amax) */
    limbs_shr(e, pm1, amax);
    fp rho; fp_pow(&rho, &five, e);
    /* w = 5^((p-1)/3) */
    limbs_div3(e, pm1); fp_pow(&ntt_w3, &five, e);
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

/* mu = floor(x^(2m-2)/g), g monic degree m; mu has m-1 coefficients mu[0..m-2].
 * rev(g) mod x^(m-1) is inverted by Newton iteration (nu_{2l} = nu_l - x^l (nu_l * mid(rev(g) nu_l)) ), then mu_i = nu_{m-2-i}. */
void poly_newton_mu(fp *mu, const fp *g, size_t m) {
    size_t L = m - 1;
    fp *gr = NEW_FP(L), *nu = NEW_FP(L);
    for (size_t i = 0; i < L; i++) gr[i] = g[m - i];
    LD(L); ST(L); loopc(L); CTL(L);
    fp one; fp_set_one(&one);
    if (!fp_eq(&gr[0], &one)) { fprintf(stderr, "newton: g not monic\n"); exit(6); }
    nu[0] = one; ST(1);
    size_t l = 1;
    while (l < L) {
        size_t l2 = 2 * l < L ? 2 * l : L;
        fp *e = NEW_FP(l2 + l - 1);
        poly_mul(e, gr, l2, nu, l);                /* low l coefficients are 1,0,..,0 */
        fp *f = NEW_FP(2 * (l2 - l) + l);
        poly_mul(f, nu, l, e + l, l2 - l);         /* (nu * mid) , need first l2-l coefficients */
        for (size_t i = 0; i < l2 - l; i++) fp_neg(&nu[l + i], &f[i]);
        LD(l2 - l); ST(l2 - l); loopc(l2 - l);
        xfree(e); xfree(f);
        l = l2;
    }
    for (size_t i = 0; i < L; i++) mu[i] = nu[L - 1 - i];
    LD(L); ST(L); loopc(L);
    xfree(gr); xfree(nu);
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

### euclid.c

```c
/* Classical Euclid gcd (counted; loads/stores charged inside) and root finding for a product of distinct linear factors. */
#include "attack.h"
#include "pallas_consts.h"

static int deg_of(const fp *a, int top) { while (top >= 0 && fp_is_zero(&a[top])) top--; return top; }

/* returns degree of the monic gcd in out[0..deg]; inputs are not modified.  da, db are upper bounds on the degrees. */
size_t euclid_gcd(fp *out, const fp *a, size_t da, const fp *b, size_t db, size_t *dout) {
    size_t cap = (da > db ? da : db) + 1;
    fp *A = NEW_FP(cap), *B = NEW_FP(cap);
    memcpy(A, a, (da + 1) * sizeof(fp)); memcpy(B, b, (db + 1) * sizeof(fp));
    LD(da + db + 2); ST(da + db + 2); loopc(da + db + 2);
    int dA = deg_of(A, (int)da), dB = deg_of(B, (int)db);
    CTL(9 * (uint64_t)(dA + dB + 2));      /* degree scans: per test index, four-limb zero test, branch, decrement */
    if (dA < dB) { fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td; }
    while (dB >= 0) {
        fp ilc; fp_inv(&ilc, &B[dB]); LD(1); CTL(INV_CTL);
        while (dA >= dB) {
            fp q; fp_mul(&q, &A[dA], &ilc); LD(1);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            LD(2 * (size_t)dB); ST(dB); loopc(dB); CTL(dB);           /* index sh + i */
            fp_set_zero(&A[dA]); ST(1);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            CTL(9 * (uint64_t)(dA - nd + 1) + 6); LD(dA - nd);
            dA = nd;
            if (dA < 0) break;
        }
        fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td;
    }
    /* A is the last nonzero remainder, degree dA (after swap dB<0) */
    int dg = dA;
    if (dg < 0) { fprintf(stderr, "gcd of zero polynomials\n"); exit(8); }
    fp il; fp_inv(&il, &A[dg]);
    for (int i = 0; i <= dg; i++) fp_mul(&out[i], &A[i], &il);
    LD(dg + 1); ST(dg + 1); loopc(dg + 1);
    *dout = (size_t)dg;
    xfree(A); xfree(B);   /* note: A and B may have been swapped; both are valid allocations */
    return (size_t)dg;
}

/* ---- small-degree helpers for root finding (naive) ---- */
/* r = a mod G (G monic degree d, a has length la), result d coefficients */
static void reduce_mod(fp *a, size_t la, const fp *G, size_t d) {
    for (size_t i = la; i-- > d;) {
        fp c = a[i];
        if (fp_is_zero(&c)) continue;
        for (size_t j = 0; j < d; j++) { fp t; fp_mul(&t, &c, &G[j]); fp_sub(&a[i - d + j], &a[i - d + j], &t); }
        fp_set_zero(&a[i]);
    }
}
static void sqr_mod(fp *r, const fp *a, const fp *G, size_t d) {
    fp *t = NEW_FP(2 * d);
    for (size_t i = 0; i < 2 * d; i++) fp_set_zero(&t[i]);
    for (size_t i = 0; i < d; i++) {
        fp x; fp_sqr(&x, &a[i]); fp_add(&t[2 * i], &t[2 * i], &x);
        for (size_t j = i + 1; j < d; j++) { fp y; fp_mul(&y, &a[i], &a[j]); fp_add(&y, &y, &y); fp_add(&t[i + j], &t[i + j], &y); }
    }
    reduce_mod(t, 2 * d - 1, G, d);
    for (size_t i = 0; i < d; i++) r[i] = t[i];
    xfree(t);
}
static void mul_xa_mod(fp *r, const fp *a, const fp *av, const fp *G, size_t d) {   /* r = a * (x + av) mod G */
    fp *t = NEW_FP(d + 1);
    fp_set_zero(&t[0]);
    for (size_t i = 0; i < d; i++) t[i + 1] = a[i];
    for (size_t i = 0; i < d; i++) { fp x; fp_mul(&x, &a[i], av); fp_add(&t[i], &t[i], &x); }
    reduce_mod(t, d + 1, G, d);
    for (size_t i = 0; i < d; i++) r[i] = t[i];
    xfree(t);
}

#ifndef ROOT_TRIES
#define ROOT_TRIES 40
#endif
int find_root(fp *root, const fp *G0, size_t d0) {
    snap_t s0 = snap();
    int ok = 0;
    size_t d = d0;
    fp *G = NEW_FP(d0 + 1); memcpy(G, G0, (d0 + 1) * sizeof(fp));
    for (int tries = 0; tries < ROOT_TRIES && d > 1; tries++) {
        budget_check();
        fp av; rnd_fp254(&av);
        fp *B = NEW_FP(d);
        for (size_t i = 0; i < d; i++) fp_set_zero(&B[i]);
        /* start from x + a  (d >= 2 so it is already reduced) */
        B[0] = av; fp_set_one(&B[1]);
        int top = 253; while (top >= 0 && !((PALLAS_PM1H[top / 64] >> (top % 64)) & 1)) top--;
        for (int bit = top - 1; bit >= 0; bit--) {
            sqr_mod(B, B, G, d);
            if ((PALLAS_PM1H[bit / 64] >> (bit % 64)) & 1) mul_xa_mod(B, B, &av, G, d);
        }
        fp one; fp_set_one(&one);
        fp_sub(&B[0], &B[0], &one);
        fp *out = NEW_FP(d + 1); size_t dg = 0;
        if (d >= 1) {
            /* gcd(G, B) where B has degree < d (may be zero) */
            int allz = 1; for (size_t i = 0; i < d; i++) if (!fp_is_zero(&B[i])) allz = 0;
            if (allz) { xfree(out); xfree(B); continue; }
            euclid_gcd(out, G, d, B, d - 1, &dg);
        }
        if (dg > 0 && dg < d) {
            memcpy(G, out, (dg + 1) * sizeof(fp)); d = dg;
        }
        xfree(out); xfree(B);
    }
    if (d == 1) { fp_neg(root, &G[0]); ok = 1; }
    xfree(G);
    bound_mem_since(s0);
    return ok;
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

int hgcd_base_k = 48;
uint64_t hgcd_stat_calls, hgcd_stat_base_steps, hgcd_stat_bigdiv;

static size_t trimlen(const fp *c, size_t len) {
    size_t it = 1;
    while (len > 0 && fp_is_zero(&c[len - 1])) { len--; it++; }
    CTL(9 * it); LD(it);                 /* per test: len > 0 (compare, branch), index len - 1, the four-limb zero test (3 or, compare), branch, len-- */
    return len;
}
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
    if (getenv("HG_TRACE")) fprintf(stderr, "mat_mul Lmax=%zu N=%zu cur=%zu\n", Lmax, N, mem_cur);
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
 * own != 0: a and b are xalloc'ed arrays whose ownership passes to the callee. */
static void hgcd_base(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    fp *x = own ? (fp *)a : dupv(a, la), *y = own ? (fp *)b : dupv(b, lb);
    size_t lx = la, ly = lb, sum = 0;
    if (want_mat) mat_set_identity(R);
    while (ly > 0) {
        budget_check();
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
    budget_check();
    CTL(40);                                 /* the size computations, comparisons and branches of this call (about 40 executed operations) */
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
/* gcd(a, b) (la >= lb); the inputs are copied (the caller keeps its arrays).  Use poly_gcd_fast_own to give them away. */
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
size_t poly_gcd_fast(fp *out, const fp *a, size_t la, const fp *b, size_t lb) {
    return poly_gcd_fast_own(out, la, dupv(a, la), la, dupv(b, lb), lb);
}
```

### lean_attack.c

```c
/* Orchard Poseidon, r partial rounds: odd-part collision attack, lean schedule.
 * usage: lean_attack r ncentres seed [j0] [verbose]
 * Per centre: build g by evaluation + inverse NTT, S^((p-1)/2) mod g (lean in-place schedule), gcd(g, S^h-1) by half-gcd,
 * root splitting, back-map, verification by two reference hashes.  Stops after the first verified collision or after
 * ncentres failed centres.  Every field operation, 256-bit load/store, loop-control op and random word is counted. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include <time.h>
#include <math.h>

#ifndef BUDGET_GCD
#define BUDGET_GCD 8800000000ULL
#endif
#ifndef BUDGET_ROOT
#define BUDGET_ROOT 10000000ULL
#endif
#ifndef BUDGET_FIN
#define BUDGET_FIN 100000ULL
#endif
typedef struct { const char *name; snap_t d; double sec; size_t peak; } stage_t;
static stage_t st[16]; static int nst;
static snap_t cur; static clock_t tcur; static size_t gpeak;
static void stage_begin(void) { nst = nst; cur = snap(); tcur = clock(); mem_reset_peak(); }
static void stage_end(const char *name) {
    stage_t *s = &st[nst++]; s->name = name; s->d = snap_sub(snap(), cur); s->sec = (double)(clock() - tcur) / CLOCKS_PER_SEC; s->peak = mem_peak;
    if (mem_peak > gpeak) gpeak = mem_peak;
}
static void phex(const char *tag, const fp *a) { char h[65]; fp_to_hex(h, a); printf("%s 0x%s\n", tag, h); fflush(stdout); }

int main(int argc, char **argv) {
    int r = argc > 1 ? atoi(argv[1]) : 1;
    int ncen = argc > 2 ? atoi(argv[2]) : 1;
    uint64_t seed = argc > 3 ? strtoull(argv[3], 0, 0) : 1;
    int j0 = argc > 4 ? atoi(argv[4]) : 0;
    int verbose = argc > 5 ? atoi(argv[5]) : 0;
    rng_seed(seed);
    size_t m = poly_degree_m(r);
    printf("r=%d ncentres=%d seed=%llu m=%zu\n", r, ncen, (unsigned long long)seed, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    uint64_t tot_all = 0, tot_arith = 0; double tot_sec = 0; snap_t tot_t; memset(&tot_t, 0, sizeof tot_t);
    int success = 0, centres_done = 0; uint64_t root_spent = 0, gcd_gap = 0, max_gcd_gap = 0, max_root_gap = 0;
    stage_begin(); ntt_init(15); stage_end("ntt_init");
    printf("INIT arith=%llu other=%llu total=%llu", (unsigned long long)snap_arith(st[0].d), (unsigned long long)(snap_total(st[0].d) - snap_arith(st[0].d)), (unsigned long long)snap_total(st[0].d)); putchar(10);
    uint64_t pre_all = snap_total(st[0].d); tot_all += pre_all; tot_arith += snap_arith(st[0].d); nst = 0;
    tot_t.add += st[0].d.add; tot_t.sub += st[0].d.sub; tot_t.mul += st[0].d.mul; tot_t.sqr += st[0].d.sqr; tot_t.ld += st[0].d.ld; tot_t.st += st[0].d.st; tot_t.ctl += st[0].d.ctl;
    for (int ci = 0; ci < ncen && !success; ci++) {
        int j = (j0 + ci) % 3;
        nst = 0;
        line_t L;
        stage_begin(); { snap_t s0 = snap(); line_setup(&L, j); bound_mem_since(s0); } stage_end("line_setup");
        fp c;
        stage_begin(); rnd_fp254(&c); stage_end("random centre");
        fp *g = NEW_FP(m + 1);
        stage_begin(); build_g(g, &L, &c, r, 0); stage_end("build g");
        fp *F = NEW_FP(m);
        stage_begin(); powx_lean(F, g, m, PALLAS_PM1H, verbose ? 2 : 1); stage_end("S^((p-1)/2) mod g");
        fp one; fp_set_one(&one);
        stage_begin();
        fp_sub(&F[0], &F[0], &one);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R-1: executed tests only */
        fp G[9]; size_t lG = 0;
        budget_arm(BUDGET_GCD, "gcd");
        if (dR >= 0) lG = poly_gcd_fast_own(G, 9, g, m + 1, F, (size_t)dR + 1);
        else { xfree(g); xfree(F); }
        budget_check(); gcd_gap = budget_maxgap(); if (gcd_gap > max_gcd_gap) max_gcd_gap = gcd_gap;
        budget_arm(0, "");
        stage_end("gcd(g, S^h-1) (half-gcd)");
        size_t dG = lG == (size_t)-1 ? 0 : (lG ? lG - 1 : 0);
        fp nk1, rho1, nk2, rho2, dg1, dg2, cS;
        int found = 0;
        if (lG == (size_t)-1) printf("centre %d: gcd degree above 8: trial abandoned\n", ci);
        if (dG >= 1) {
            fp S;
            stage_begin(); budget_arm(BUDGET_ROOT - root_spent > 0 ? BUDGET_ROOT - root_spent : 1, "root"); found = find_root(&S, G, dG); budget_check(); if (budget_maxgap() > max_root_gap) max_root_gap = budget_maxgap(); budget_arm(0, ""); stage_end("root finding"); root_spent += snap_total(st[nst - 1].d);
            if (found) {
                stage_begin();
                snap_t s0 = snap();
                fp s; int sq = fp_sqrt(&s, &S);
                if (!sq) { printf("root not a square?!\n"); found = 0; }
                fp W1, W2;
                fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
                map_back(&nk1, &rho1, &L, &W1);
                map_back(&nk2, &rho2, &L, &W2);
                bound_mem_since(s0);
                stage_end("sqrt + map back");
                stage_begin();
                poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
                poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
                { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
                stage_end("verification (2 reference hashes)");
                int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
                success = found && fp_eq(&dg1, &dg2) && !same_in;
            }
        }
        uint64_t all = 0, arith = 0; double sec = 0;
        for (int i = 0; i < nst; i++) { all += snap_total(st[i].d); arith += snap_arith(st[i].d); sec += st[i].sec; }
        tot_all += all; tot_arith += arith; tot_sec += sec; centres_done++;
        for (int i = 0; i < nst; i++) { tot_t.add += st[i].d.add; tot_t.sub += st[i].d.sub; tot_t.mul += st[i].d.mul; tot_t.sqr += st[i].d.sqr; tot_t.ld += st[i].d.ld; tot_t.st += st[i].d.st; tot_t.ctl += st[i].d.ctl; tot_t.rnd += st[i].d.rnd; tot_t.perm += st[i].d.perm; }
        printf("CENTRE %d j=%d degG=%zu success=%d arith=%llu all=%llu sec=%.1f\n", ci, j, dG, success,
               (unsigned long long)arith, (unsigned long long)all, sec);
        if (verbose || success) {
            for (int i = 0; i < nst; i++)
                printf("  %-40s arith=%12llu other=%12llu total=%12llu %7.1fs peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
                       (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].sec, st[i].peak);
        }
        fflush(stdout);
        if (success) {
            phex("COLLISION nk1 ", &nk1); phex("COLLISION rho1", &rho1); phex("COLLISION nk2 ", &nk2); phex("COLLISION rho2", &rho2);
            phex("COLLISION digest", &dg1); phex("COLLISION centre", &c); (void)cS;
        }
    }
    int C = 216 + 21 * r;
    printf("SUMMARY r=%d centres=%d success=%d total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", r, centres_done, success,
           (unsigned long long)tot_all, (unsigned long long)tot_arith, (double)tot_all / C, log2((double)tot_all / C), gpeak, tot_sec);
    printf("GAPS gcd=%llu root=%llu", (unsigned long long)max_gcd_gap, (unsigned long long)max_root_gap); putchar(10);
    printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu", (unsigned long long)tot_t.add, (unsigned long long)tot_t.sub, (unsigned long long)tot_t.mul, (unsigned long long)tot_t.sqr, (unsigned long long)tot_t.ld, (unsigned long long)tot_t.st, (unsigned long long)tot_t.ctl, (unsigned long long)tot_t.rnd, (unsigned long long)tot_t.perm);
    putchar(10);
    return success ? 0 : 1;
}
```

