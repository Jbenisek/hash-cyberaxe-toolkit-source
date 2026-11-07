# Orchard Poseidon, r = 2: one deterministic run on the fixed target, executed operation count (two free rounds on a line, odd part about a fixed centre, half-gcd)

## 1. Claim

Target: `poseidon-orchard-r2-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, two partial rounds 4 and 5, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `success_probability = 1`: the procedure is deterministic (centres `c_i = i` in the fixed order `i = 1, 2, 3, ...`, section 4) and it was executed once, from the start, on the fixed target, where it stopped with the collision at trial 1 (`c = 1`); every executed trial, failed ones included, is charged. There is no probability statement and no worst-case bound anywhere in this document.
* `time_log2 = 27.05075` in target-compression units (`C(2) = 258` primitive operations per unit): the executed operation count of that one run, all 1 trials, `N = 35,867,804,181` operations (section 6), `log2(N / 258) = 27.05074`, rounded up at five decimals. The twiddle table is built inside the run and is part of `N`, so `preprocessing_log2 = 0`.
* `memory_log2_bytes = 25.287` (`40,933,715` bytes, section 7): the peak of live data of the executed run (maximum over the trials) plus the static image, a stack bound and allocator metadata. The normalized cost is `27.05075 + 5.287 = 32.33775`.
* No selection: no centre was chosen or screened beforehand. The run began at `c_1 = 1`, every trial it executed is in the count `N`, and the table of section 6 lists them all. `memory` is the maximum over the trials (the buffers of a trial are released before the next).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^8`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is a known approach. What is offered here is a complete finite implementation with an executed operation ledger and a low-memory schedule. No heuristic premise is used.
* The collision stored in `certificates/` is the output of this program. It is checked at the selected target with the organizer's hash.

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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5 (partial, r = 2), 60, 61, 62, 63 (full) put eight S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^8 = D = 1953125`. The leading coefficient is obtained by
propagating leading coefficients through the seven layers (a partial round contributes only coordinate 0 at the top degree); if it vanished on the line used, `g_c` would have lower degree; the program inverts the computed leading coefficient and every output is checked by the reference hash.

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 195312`, `g_c` has degree exactly `m` and
leading coefficient `2 f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 196608 = 3 * 2^14` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 393216` evaluations of `F` are each charged as
one target-compression unit (`C(2) = 258` operations), although a line evaluation (affine start, six more rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, and the executed shifts, masks, ors, modulo operations and loop control of the bit-reversed index `layout_index`, which are counted inside that function) is charged on top.


## 4. The program (one deterministic run)

```
init:   twiddle table
setup:  the line (line_setup)
A  c := c_i = i (the integer i as a field element; one conversion, 2 control ops)
B  g := monic g_c, by section 3 (393216 evaluations + one inverse NTT of size 196608 + normalisation by the leading coefficient)
C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; 236 modular squarings, 45 of the steps also multiply by S by a streaming shift)
D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
E  S := a root of G                 (only if deg G >= 1: root isolation, for degree 1 S = -G_0; otherwise the trial ends and the next centre is tried)
F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
G  verify: the two reference hashes (258 operations each) are equal and the pairs differ -> output and stop; otherwise the next trial
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 17 bits after the leading one are zero, so the program starts from the monomial `S^v` with `v = 2^17 < m` (this absorbs 17 of the 253 squarings, 17 + 236 = 253), and the squaring loop of stage C has 236 steps, of which 45 also multiply by `S` (a streaming shift).

Determinism. The program takes no input and reads no file. It executes init and setup once, then trials `i = 1, 2, 3, ...` (stages A to D, and E to G when `deg G >= 1`), and returns exit status 0 at the first trial whose two reference hashes agree with distinct pairs. The only random draws are the shifts of the root isolation (generator seeded with the constant 1), which are made only in a trial with `deg G >= 2`; a trial with `deg G = 1` makes none. Every trial, failed or not, is executed to its end and counted by the same counters, and the buffers of a failed trial are released before the next trial begins. In the executed run the trials are listed in section 6; the last trial is the one that produced the certificate.

### 4.2 Machine model and charging rules
Every item below is counted by the executing code at the statement that executes it; none is estimated. The complete source is in section 9. The rules for loop control, address work and loads and stores follow the price list of the public r = 2 entries (quoted from section 4.1 of the revision of tanctl that reuses the kernels of entry 186052af: "A radix-2 butterfly is charged 9/2 units: the twiddle update multiplication, the twiddle product, one addition, one subtraction and one half unit of loop/address work ... Loop control: a radix-8 pass processes eight elements, twelve butterflies, per loop iteration (one index update, one comparison, one branch: 3 units per 12 butterflies), so 1/2 unit per butterfly is conservative; every other per-element loop (pointwise steps, padding, copies, folds, remainders, shifts) is unrolled eight elements per iteration and charged 1/2 unit per element."). We adopt exactly those two statements: 1/2 unit per butterfly and 1/2 unit per element of an unrolled loop. Where the earlier engine of this author charged more (address formation for every load and store, 3 to 9 control operations per block), the charge is replaced by these rules; nothing else was lowered.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each (`LD(n)`, `ST(n)`); no separate address-formation operation is charged: the register-block kernels use constant displacements from a block base, as in the public entries. The loads of twiddles and of the constants of the radix-3 stage are charged as loads (`LD(1)` per use).
* loop and address work in half units (counter `hc`, macro `HC(n)` adds `n` half units; two half units are one operation, the whole run is rounded up once): one half unit per butterfly (`BF`, `BFN`, `IB`, `IBN` in `ntt_kern.h`), one half unit per element of every pointwise step fused into the transform, three half units (one per element) per position of the radix-3 Good-Thomas stage, and `loopc(n)` = `n` half units after every other loop of `n` elements (copy, fold, pad, subtraction, scaling, schoolbook inner loops: these are unrolled eight elements per pass in the rule above). The radix-3 stage is executed by three-position unrolled kernels (the rotation of the Good-Thomas index repeats every three positions, so the choice of the constant permutation and of the input pattern is resolved at the unrolled kernel, not per element); the per-region setup of that stage is charged as the constants 25 and 30 in `ntt.c`.
* per-call constants of a transform pass (`CTLK` in `ntt.c`): computing the pass tables and the call and return: `18 + 6k` (forward), `19 + 6k` (inverse and fused pass) operations for a pass of `k` layers.
* every other executed index or control operation outside the transform kernels, one each: shift, mask, or, addition, subtraction, multiplication, modulo, comparison, conditional branch. They are added with `CTL(k)` next to the statement that executes them (the gcd, the divisions, the root isolation, the line setup, the bit-reversed index of stage B), and data-dependent tests are charged per executed test.
* transform kernels are generated, straight-line code (`gen_kern.py` is part of the source of section 9; its output `ntt_kern.h` is listed there). A block kernel for `k` layers (1 to 4; 2^k data words `x[]`) has no loop and no branch: each butterfly is the literal statements `fp_sub`, `fp_add`, `fp_mul` (three field operations, none for the multiplication when the twiddle is 1 at `b = 0`) plus its half unit, and every twiddle load is a literal `LD(1)`.
* working registers (disclosed assumption): a block keeps its 2^k <= 16 data words `x[]` in registers; the twiddle operand and the butterfly temporary need two further words, so the kernels assume a register file of 18 words of 256 bits. Strides, shift counts, base pointers and loop indices are held in integer registers (not charged as memory accesses). The real cost of a machine with fewer registers would be higher; this is the one structural assumption of the model.
* the centre c_i = i: one conversion (one multiplication) and one control operation; the shifts `a = 1, 2, 3, ...` of the root isolation are drawn the same way (no random words are used anywhere).
* the reduced permutation evaluations of stage B: 258 each (`C(2)`), instead of their (smaller) expanded arithmetic (`X.perm`). Nothing else is charged as a unit.
* small-degree work in the line setup and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 1 control operation.
* Montgomery conversions: every conversion of an integer to or from the internal representation (`fp_from_limbs`, `fp_to_limbs`, `fp_from_u64`, `fp_from_hex`) is one Montgomery multiplication and is charged as one field multiplication in `pallas.c`, so it is inside every count of section 6. The constants of `pallas_consts.h` are stored in Montgomery form and need no conversion.
* the budget checks of the earlier engine are not armed in this run (no halt exists in the executed run); the program makes no random draw.
* Not charged, and why: (a) the bookkeeping of the allocator (`xalloc`, `xfree`): the abstract machine has no allocator, its working state is a set of arrays, which is what section 7 measures; (b) formatting and printing: only the verbose flag of the ledger run, not part of the submitted computation; (c) a hardware self-check, `fault_probe` in `lean.c`, executed every 32 squarings (seven times per trial): a known product and a round trip of a transform of length 96, with all counters and the peak restored afterwards. It is not part of the computation and does not affect any value; its cost was measured at 4,235 operations per execution and is bounded here by 5,000 per execution, so over the run (7 executions per trial) at most `35,000` operations over the run, and that bound is added to the counted total in section 6 (rather than subtracting it). The line `FAULTS detected=0` of the run reports that none of its checks failed.

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

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes
and compares them; the program returns success only if they are equal and the pairs differ. Independent of the program, the pair in `certificates/` is checked by the organizer's hash, and the digest `0x3ab2143957ab5cfff46c586d178bda5719070a9795fdbf25272f32cd82cf3451` is printed by the run.

## 6. Ledger: the executed run (primitive operations; `C(2) = 258`)

The count is the instrumented total of one execution of the shipped source (`gcc -O3`, run as `exec_attack 2 8 1 0 1 0 0 1` under `ulimit -s 64`; the argument only turns on printing of the powering breakdown for the first trial). `arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 258-operation unit charges. Nothing is bounded, extrapolated or taken from another run: every figure below is a counter of the same execution.

| stage | arith | other | total |
|---|---:|---:|---:|
| init: twiddle table (once) | 66,509 | 104,398 | 170,907 |
| setup: the line | 391 | 3,608 | 3,999 |
| A: centre c_i = i (all trials) | 0 | 1 | 1 |
| B: 393,216 evaluations (258 units each) + inverse NTT 196,608 + normalisation (all trials) | 6,421,153 | 109,612,408 | 116,033,561 |
| C: `S^((p-1)/2) mod g` (m = 195312, 236 steps per trial, all trials) | 16,131,772,597 | 12,598,711,324 | 28,730,483,921 |
| D: half-gcd of (g, R - 1) (all trials) | 3,170,520,527 | 3,850,520,954 | 7,021,041,481 |
| E: root of G (last trial only) | 1 | 4 | 5 |
| F: square root, back-map (last trial only) | 3,066 | 29,661 | 32,727 |
| G: two reference hashes (last trial only) | 516 | 2,064 | 2,580 |
| rounding: half units are rounded up once for the run, not once per stage line | | | -1 |
| total of the counted run | | | 35,867,769,181 |
| uncounted self-checks (section 4.2, stated bound) | | | 35,000 |
| total N | | | 35,867,804,181 |

| trial | centre c_i | deg G | charge of the trial (operations) |
|---:|---:|---:|---:|
| 1 | 1 | 1 | 31,882,331,315 |

Total `N = 35,867,804,181` operations `= 139,022,496.8` units, `log2(N / 258) = 27.05074`, claimed as `27.05075` (rounded up).
The half-gcd of stage D charged 7,021,041,481 operations in this run (summed over all trials, degrees 195312 and 195311). Composition by type of the run (init included; the control counter includes the address operations of loads and stores): add `6,717,662,614`, sub `6,311,270,452`, mul `6,137,434,798`, sqr `142,416,896`, loads `7,698,272,294`, stores `4,328,358,512`, control `445,604,160`, unit charges `101,449,728`.

Stage C in detail (m = 195312): Newton for MU: 177,807,647 operations; prefix and scaling: 976,763; 236 squaring steps at 120,981,777 operations each (arith 67,931,733). Of the arithmetic of stage C, 16,131,772,597 operations; the transforms are the largest term.

### 6.1 Ledger recomputation

```python
from math import log2, ceil
C = 258
stages = [170907, 3999, 1, 116033561, 28730483921, 7021041481, 5, 32727, 2580, -1]
run = sum(stages)
probe_bound = 35000
N = run + probe_bound
print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

## 7. Memory

Peak of live data of the executing program, tracked by the allocator that serves every buffer (each buffer is one allocation). Stage C at `m = 195312`: the twiddle table (`2^14` elements, 524,288 bytes), `Y` (`3 * 2^15` elements, 3,145,728), `tmp` (`2^15` elements, 1,048,576), `MU` (1,249,952),
`g` (1,250,016) and the result `F` (1,249,984). Tracked peaks of the run per stage (maximum over the trials): setup 2,097,152; A 2,097,152; B 14,638,624; C 37,624,320; D 40,741,792; E 2,097,216; F 2,097,152; G 2,097,152. The largest is 40,741,792 bytes. To the heap peak we add the static image of the executable (code, constants and tables: text 116,059 + data 768 + bss 5,464 = 122,291 bytes), a stack bound of 65,536 bytes (the complete run was executed under a 64 KiB stack limit) and 4,096 bytes for the allocator's own metadata:
`40,933,715` bytes `= 2^25.287`. The memory penalty is `max(0, 25.287 - 20) = 5.287`.
Counted: every buffer of the program (the tracked heap peak above), the executable's own code, constants and tables (text + data + bss), the stack bound and the allocator metadata. Not counted, as they are not part of the abstract program: the dynamically linked C library code and loader mappings and the kernel structures of the host process; the program uses the library only for `malloc`/`free`/`memcpy`/`memset` (whose buffers are counted) and, in the ledger run only, printing.
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 9), one machine-checked collision certificate (`certificates/`, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package contains only the certificate, so the C source is part of this document (section 9) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3` and run as `exec_attack 2 8 1 0 1 0 0 1`.
* The cost is the executed count of one run of the fixed procedure from its first centre, every trial charged. It says nothing about how many trials another sequence of centres would need.
* The cost claim assumes the model of section 4.2; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it. The organizer did not run the program, so the counts rest on the shipped source.
* What a referee can rerun (one core): (a) the collision certificate against the organizer's hash, seconds; (b) the ledger recomputation of section 6.1, seconds; (c) `gcc -O3` of the source of section 9 and `exec_attack 2 8 1 0 1 0 0 1` under `ulimit -s 64`, which reproduces every count of section 6 and the peak of section 7 and prints the collision (about 20 to 40 minutes per trial).

## 9. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter; `CTL(n)` adds `n` to the control counter; `HC(n)` and `loopc(n)` add `n` half units; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()`/`snap_restore()` read and restore all counters. Buffers are obtained from the tracked allocator (`NEW_FP`).
The program is built as `gcc -O3 -march=native -o exec_attack lean_attack.c common.c ntt.c poly.c loop.c lean.c line.c euclid.c hgcd.c pallas.c -lm`, and the counted run is `ulimit -s 64; ./exec_attack 2 8 1 0 1 0 0 1` (r = 2, at most 8 centres, seed 1 unused, line 0 fixed, verbose printing, no budgets, fixed line). Unused parts of the files (`powx_mod` in `loop.c`, `build_g`'s debug flag, budget tables in `budgets.h`) are not executed by this run.
The files are shown in full, in the order: `common.h`, `common.c`, `pallas.h`, `pallas.c`, `pallas_consts.h`, `attack.h`, `hgcd.h`, `budgets.h`, `gen_kern.py`, `ntt_kern.h`, `ntt.c`, `poly.c`, `loop.c`, `lean.c`, `line.c`, `euclid.c`, `hgcd.c`, `lean_attack.c`.
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

typedef struct { uint64_t ld, st, ctl, rnd, perm, hc; } xcnt_t;   /* hc: half units (loop/address work, 1/2 unit each, accepted ledger rule) */   /* perm: reduced permutation evaluations charged as C(r) primitive operations each */
extern xcnt_t X;
#define LD(n)  (X.ld  += (uint64_t)(n))
#define ST(n)  (X.st  += (uint64_t)(n))
#define CTL(n) (X.ctl += (uint64_t)(n))
#define HC(n)  (X.hc  += (uint64_t)(n))   /* n half units */
/* a simple loop is unrolled 16x: 4 control ops (index update, bound compare, branch, spare) per 16 elements */
static inline void loopc(size_t nel) { X.hc += (uint64_t)nel; }   /* unrolled loop: 1/2 unit per element (accepted ledger rule: 8x unrolled, one index update + compare + branch per 8 elements) */

typedef struct { uint64_t add, sub, mul, sqr, ld, st, ctl, rnd, perm, hc; } snap_t;
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
void ctl_add(uint64_t n) { X.ctl += n; }
size_t mem_cur = 0, mem_peak = 0;

snap_t snap(void) {
    snap_t s; s.add = fp_cnt.add; s.sub = fp_cnt.sub; s.mul = fp_cnt.mul; s.sqr = fp_cnt.sqr;
    s.ld = X.ld; s.st = X.st; s.ctl = X.ctl; s.rnd = X.rnd; s.perm = X.perm; s.hc = X.hc; return s;
}
snap_t snap_sub(snap_t a, snap_t b) {
    snap_t s; s.add = a.add - b.add; s.sub = a.sub - b.sub; s.mul = a.mul - b.mul; s.sqr = a.sqr - b.sqr;
    s.ld = a.ld - b.ld; s.st = a.st - b.st; s.ctl = a.ctl - b.ctl; s.rnd = a.rnd - b.rnd; s.perm = a.perm - b.perm; s.hc = a.hc - b.hc; return s;
}
uint64_t snap_arith(snap_t s) { return s.add + s.sub + s.mul + s.sqr; }
uint64_t snap_total(snap_t s) { return snap_arith(s) + s.ld + s.st + s.ctl + s.rnd + s.perm + (s.hc + 1) / 2; }
void snap_restore(snap_t s) {
    fp_cnt.add = s.add; fp_cnt.sub = s.sub; fp_cnt.mul = s.mul; fp_cnt.sqr = s.sqr;
    X.ld = s.ld; X.st = s.st; X.ctl = s.ctl; X.rnd = s.rnd; X.perm = s.perm; X.hc = s.hc;
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

extern void ctl_add(uint64_t n);   /* common.c: charges n integer / control operations */
void fp_pow(fp *r, const fp *a, const uint64_t e[4]) {
    fp_cnt.pow_calls++;
    int top = -1;
    for (int i = 255; i >= 0; i--) { ctl_add(6); if ((e[i / 64] >> (i % 64)) & 1) { top = i; break; } }   /* scan: loop (3), word index and shift, test */
    if (top < 0) { fp_set_one(r); return; }
    fp base = *a, acc = *a;                    /* leading 1 bit: acc = a, no operation */
    for (int i = top - 1; i >= 0; i--) {
        fp_sqr(&acc, &acc); ctl_add(8);   /* loop (3), word index, shift, and, branch */
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
        ctl_add(8);
        unsigned i = 0; fp u = t;
        while (!fp_eq(&u, &one)) { fp_sqr(&u, &u); ctl_add(5); i++; if (i >= m) return 0; }   /* i == m: t has order 2^m => non-residue */
        b = z;
        for (unsigned k = 0; k + i + 1 < m; k++) { fp_sqr(&b, &b); ctl_add(5); }                  /* b = z^(2^(m-i-1)) */
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

### budgets.h

```c
#define BUDGET_R1_GCD 2680000000ULL
#define BUDGET_R1_ROOT 187665120ULL
#define BUDGET_R2_GCD 21108000000ULL
#define BUDGET_R2_ROOT 187665120ULL
```

### gen_kern.py

```python
"""Generates ntt_kern.h: straight-line register-block kernels (k = 1..4 layers) for the forward and inverse butterflies.
Twiddle pointers walk with one addition per twiddle; every pointer line carries its integer-operation charge (CTL)."""
out = ['/* generated by gen_kern.py: straight-line butterfly blocks, k = 1..4 layers; x[] is the register block */',
       '#define BF(u, v, w) do { HC(1); fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, (w)); } while (0)',
       '#define BFN(u, v) do { HC(1); fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); (v) = t_; } while (0)',
       '#define IB(u, v, w) do { HC(1); fp tt_, A_ = (u); fp_mul(&tt_, &(v), (w)); fp_sub(&(u), &A_, &tt_); fp_add(&(v), &A_, &tt_); } while (0)',
       '#define IBN(u, v) do { HC(1); fp tt_ = (v); fp_sub(&(v), &(u), &tt_); fp_add(&(u), &(u), &tt_); } while (0)']


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
                    out.append('    const fp *w%d = tw; /* b == 0: the twiddle at tp == 0 is 1 */' % j)
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
open('ntt_kern.h', 'w', newline='\n').write('\n'.join(out) + '\n')
```

### ntt_kern.h

```c
/* generated by gen_kern.py: straight-line butterfly blocks, k = 1..4 layers; x[] is the register block */
#define BF(u, v, w) do { HC(1); fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); fp_mul(&(v), &t_, (w)); } while (0)
#define BFN(u, v) do { HC(1); fp t_; fp_sub(&t_, &(u), &(v)); fp_add(&(u), &(u), &(v)); (v) = t_; } while (0)
#define IB(u, v, w) do { HC(1); fp tt_, A_ = (u); fp_mul(&tt_, &(v), (w)); fp_sub(&(u), &A_, &tt_); fp_add(&(v), &A_, &tt_); } while (0)
#define IBN(u, v) do { HC(1); fp tt_ = (v); fp_sub(&(v), &(u), &tt_); fp_add(&(u), &(u), &tt_); } while (0)
static inline void kf1(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    const fp *w0 = tw + (b << sjs[0]); LD(1); CTL(2);
    BF(x[0], x[1], w0);
}
static inline void kf1z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[1]);
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
}
static inline void ki1(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w0 = tw + ((nh - (b << sj[0])) << sh); LD(1); CTL(4);
    IB(x[0], x[1], w0);
}
static inline void ki1z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
    const fp *w0 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[3], w0);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w1 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
    w0 += D[0]; LD(1); CTL(1);
    BF(x[1], x[5], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[2], x[6], w0);
    w0 += D[0]; LD(1); CTL(1);
    BF(x[3], x[7], w0);
    BFN(x[0], x[2]);
    BFN(x[4], x[6]);
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
    w1 += D[1]; LD(1); CTL(1);
    BF(x[1], x[3], w1);
    BF(x[5], x[7], w1);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
    BFN(x[4], x[5]);
    BFN(x[6], x[7]);
    const fp *w2 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w2 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w0 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w2 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w3 = tw; /* b == 0: the twiddle at tp == 0 is 1 */
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
    const fp *w3 = tw + (nh << sh); CTL(1); /* b == 0: the twiddle at tp == 0 is 1 */
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
```

### ntt.c

```c
/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 words in registers) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"
/* Accepted ledger rule (tanctl PR 37 proof, sections 4.1 and 5.2): loop/address work is 1/2 unit per butterfly and 1/2 unit per element of every
 * unrolled loop (a radix-8 pass has 3 control units per 12 butterflies, so 1/2 per butterfly is conservative).  The per-block CTL() charges of the
 * earlier engine are replaced by HC() half units on each butterfly / element; only per-call constants remain (CTLK). */
#undef CTL
#define CTLK(n) (X.ctl += (uint64_t)(n))
#define CTL(n) ((void)0)

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
    for (size_t j = 1; j < nmax_g / 2; j++) { fp_mul(&tw[j], &tw[j - 1], &rho); ST(1); }
    loopc(nmax_g / 2);
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
    int np = (a + 3) / 4; P.npass = np;
    int rem = a;
    /* last pass gets 4 layers; earlier passes take the rest, first pass smallest */
    for (int i = np - 1; i >= 0; i--) { int k = rem >= 4 ? 4 : rem; P.kk[i] = k; rem -= k; }
    if (rows == 3) {
        size_t n = P.n, beta = 0;
        for (size_t b = 1; b < n; b += 2) if ((3 * b) % n == 1) { beta = b; break; }
        P.c0 = (int)((3 * beta - 1) / n);
    }
    return P;
}
plan_t plan_for_len(size_t len, int allow3) {
    for (int a = 2; a <= amax_g; a++) {
        if (((size_t)1 << a) >= len) return make_plan(1, a);
        if (allow3 && 3 * ((size_t)1 << a) >= len) return make_plan(3, a);
    }
    fprintf(stderr, "length %zu too large for amax=%d\n", len, amax_g); exit(5);
}
static size_t brv(size_t x, int a) { size_t r = 0; for (int i = 0; i < a; i++) { r = (r << 1) | (x & 1); x >>= 1; } return r; }
size_t layout_index(const plan_t *P, size_t k) {
    size_t row = P->rows == 3 ? k % 3 : 0;
    return row * P->n + brv(k % P->n, P->a);
}
void plan_theta(const plan_t *P, fp *theta) {
    fp rho = tw[(size_t)1 << P->shift];
    if (P->rows == 1) { *theta = rho; return; }
    int e = (3 - P->c0 % 3) % 3;              /* omega3^(-c0) */
    fp_mul(theta, &rho, &W3[e]);
}

/* ---------- butterflies: straight-line register blocks (ntt_kern.h) ---------- */
#include "ntt_kern.h"
/* Charging convention of this file: LD/ST = one 256-bit load/store; CTL(n) = n executed integer / comparison / branch / shift / address
 * operations, each counted as 1.  Every statement that executes such operations carries its CTL charge next to it. */

static void kf_run(int k, int z, fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    CTL(7);   /* call, switch on k (compare, jump table), z test (2), call/return of the kernel (2) */
    switch (k) {
    case 1: if (z) kf1z(x, tw, b, D, sjs); else kf1(x, tw, b, D, sjs); break;
    case 2: if (z) kf2z(x, tw, b, D, sjs); else kf2(x, tw, b, D, sjs); break;
    case 3: if (z) kf3z(x, tw, b, D, sjs); else kf3(x, tw, b, D, sjs); break;
    default: if (z) kf4z(x, tw, b, D, sjs); else kf4(x, tw, b, D, sjs); break;
    }
}
static void ki_run(int k, int z, fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    CTL(7);   /* call, switch on k, z test (2), call/return of the kernel (2) */
    switch (k) {
    case 1: if (z) ki1z(x, tw, b, D, sj, sh, nh); else ki1(x, tw, b, D, sj, sh, nh); break;
    case 2: if (z) ki2z(x, tw, b, D, sj, sh, nh); else ki2(x, tw, b, D, sj, sh, nh); break;
    case 3: if (z) ki3z(x, tw, b, D, sj, sh, nh); else ki3(x, tw, b, D, sj, sh, nh); break;
    default: if (z) ki4z(x, tw, b, D, sj, sh, nh); else ki4(x, tw, b, D, sj, sh, nh); break;
    }
}
/* per-pass tables: sj[j] = l0 + j, sjs[j] = l0 + j + shift, D[j] = s << sjs[j] (twiddle pointer step between consecutive tp of layer j) */
static void pass_tables(int k, int l0, size_t s, int shift, size_t *D, int *sj, int *sjs) {
    for (int j = 0; j < k; j++) { sj[j] = l0 + j; sjs[j] = l0 + j + shift; D[j] = s << sjs[j]; }
    CTL(6 * (uint64_t)k + 4);                            /* per layer: three additions, a shift, a store, loop step */
}
/* One pass of k layers over a row, blocks of G = 2^k elements at stride s.  Charges per block: loop (3: increment, compare, branch),
 * block base (1), b == 0 test (2), element address updates (1 per element load/store when s > 1; none when s == 1: constant displacements),
 * twiddle pointers (inside the kernel).  Per group: loop (3) and base address (2). */
static void load_block(fp *x, const fp *base, size_t s, size_t G) {
    if (s == 1) { for (size_t t = 0; t < G; t++) x[t] = base[t]; }
    else { for (size_t t = 0; t < G; t++) x[t] = base[t * s]; CTL(G); }
    LD(G);
}
static void store_block(fp *base, const fp *x, size_t s, size_t G) {
    if (s == 1) { for (size_t t = 0; t < G; t++) base[t] = x[t]; }
    else { for (size_t t = 0; t < G; t++) base[t * s] = x[t]; CTL(G); }
    ST(G);
}
static void pass_fwd(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0;
    CTLK(18 + 6 * k);                                            /* s, G, Gs, ngrp: shift, shift, mul, shift; call, return */
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        CTL(5);                                        /* group loop + base address */
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            CTL(6);                                    /* block loop (3), base (1), b == 0 test (2) */
            load_block(x, base, s, G);
            kf_run(k, b == 0, x, tw, b, D, sjs);
            store_block(base, x, s, G);
        }
    }
}
static void pass_inv(fp *row, const plan_t *P, int l0, int k) {
    size_t s = P->n >> (l0 + k), G = (size_t)1 << k, Gs = G * s, ngrp = (size_t)1 << l0, nh = P->n >> 1;
    CTLK(19 + 6 * k);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, s, P->shift, D, sj, sjs);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        for (size_t b = 0; b < s; b++) {
            fp *base = row + grp * Gs + b;
            load_block(x, base, s, G);
            ki_run(k, b == 0, x, tw, b, D, sj, P->shift, nh);
            store_block(base, x, s, G);
        }
    }
}
enum { M_NONE = 0, M_SQ = 1, M_MULC = 2 };
/* last forward pass + pointwise + first inverse pass (s == 1): one register block, constant displacements, b == 0 always */
static void pass_fused(fp *row, const plan_t *P, int l0, int k, int mode, const fp *C) {
    size_t G = (size_t)1 << k, ngrp = P->n >> k, nh = P->n >> 1;
    CTLK(19 + 6 * k);
    size_t D[4]; int sj[4], sjs[4]; pass_tables(k, l0, 1, P->shift, D, sj, sjs);
    fp x[16];
    for (size_t grp = 0; grp < ngrp; grp++) {
        fp *base = row + grp * G;
        CTL(4);                                        /* loop (3), base (1) */
        for (size_t t = 0; t < G; t++) x[t] = base[t];
        LD(G);
        kf_run(k, 1, x, tw, 0, D, sjs);
        HC(G);   /* pointwise: 1/2 unit per element */
        if (mode == M_SQ) { for (size_t t = 0; t < G; t++) fp_sqr(&x[t], &x[t]); }
        else { const fp *cb = C + grp * G; CTL(2); for (size_t t = 0; t < G; t++) fp_mul(&x[t], &x[t], &cb[t]); LD(G); }
        ki_run(k, 1, x, tw, 0, D, sj, P->shift, nh);
        for (size_t t = 0; t < G; t++) base[t] = x[t];
        ST(G);
    }
}

/* ---------- radix-3 stage ---------- */
static void dft3_full(const fp *v, fp *o) {
    fp t1, t2, m1, m2;
    fp_add(&t1, &v[1], &v[2]); fp_sub(&t2, &v[1], &v[2]);
    fp_add(&o[0], &v[0], &t1);
    fp_mul(&m1, &t1, &CH); fp_add(&m1, &m1, &v[0]);
    fp_mul(&m2, &t2, &DL);
    fp_add(&o[1], &m1, &m2); fp_sub(&o[2], &m1, &m2);
}
/* o[k] = sum over inputs flagged in nzmask of v[i] w^(ik); only outputs flagged in need are produced.
 * Each executed test, loop step and index operation is charged where it occurs. */
static void dft3_sel(const fp *v, int nzmask, int need, fp *o) {
    CTL(3);                                             /* call, full-case test (2) */
    if (nzmask == 7 && need == 7) { dft3_full(v, o); return; }
    for (int k = 0; k < 3; k++) {
        CTL(6);                                         /* loop (3), need test: shift, and, branch (3) */
        if (!((need >> k) & 1)) continue;
        int first = 1; fp acc; fp_set_zero(&acc);
        for (int i = 0; i < 3; i++) {
            CTL(6);                                     /* loop (3), nz test (3) */
            if (!((nzmask >> i) & 1)) continue;
            fp term = v[i]; int e = (i * k) % 3;
            CTL(4);                                     /* i*k, mod, e test, branch */
            if (e) fp_mul(&term, &v[i], &W3[e]);
            CTL(2);                                     /* first test */
            if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
        }
        o[k] = acc;
    }
}
/* Radix-3 stage helpers.  Mask tables: for an input pattern nzb (bit t set = position t of the Good-Thomas triple is nonzero) and the
 * rotation rot of the element, bit i1 of the DFT input mask is set when nzb has bit (rot + i1) % 3. */
static int mask_of(int nzb, int rot) {
    int m = 0;
    for (int i1 = 0; i1 < 3; i1++) if ((nzb >> ((rot + i1) % 3)) & 1) m |= 1 << i1;
    return m;
}
/* All three outputs from the inputs flagged in mask (switch on the mask: 3 operations, then straight-line field operations). */
static void dft3_masked(const fp *v, int mask, fp *o) {
    CTL(3);
    fp t;
    switch (mask) {
    case 1: o[0] = o[1] = o[2] = v[0]; break;
    case 2: o[0] = v[1]; fp_mul(&o[1], &v[1], &W3[1]); fp_mul(&o[2], &v[1], &W3[2]); break;
    case 4: o[0] = v[2]; fp_mul(&o[1], &v[2], &W3[2]); fp_mul(&o[2], &v[2], &W3[1]); break;
    case 3: fp_add(&o[0], &v[0], &v[1]); fp_mul(&t, &v[1], &W3[1]); fp_add(&o[1], &v[0], &t); fp_mul(&t, &v[1], &W3[2]); fp_add(&o[2], &v[0], &t); break;
    case 5: fp_add(&o[0], &v[0], &v[2]); fp_mul(&t, &v[2], &W3[2]); fp_add(&o[1], &v[0], &t); fp_mul(&t, &v[2], &W3[1]); fp_add(&o[2], &v[0], &t); break;
    case 6: { fp a, b; fp_add(&o[0], &v[1], &v[2]);
              fp_mul(&a, &v[1], &W3[1]); fp_mul(&b, &v[2], &W3[2]); fp_add(&o[1], &a, &b);
              fp_mul(&a, &v[1], &W3[2]); fp_mul(&b, &v[2], &W3[1]); fp_add(&o[2], &a, &b); break; }
    default: dft3_full(v, o); break;
    }
}
/* output k only, inputs flagged in mask: o = sum_i v[i] w^(ik).  Per input: presence test (2), first test (2), exponent selection by the switch on k (2 per call). */
static void dft3_one(const fp *v, int mask, int k, fp *o) {
    CTL(3);
    int first = 1; fp acc;
    for (int i = 0; i < 3; i++) {
        CTL(4);
        if (!((mask >> i) & 1)) continue;
        fp term = v[i]; int e = (i * k) % 3;
        if (e) fp_mul(&term, &v[i], &W3[e]);
        if (first) { acc = term; first = 0; } else fp_add(&acc, &acc, &term);
    }
    CTL(2);
    *o = acc;
}
static void stageA_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    size_t n = P->n;
    CTL(6);
    if (P->rows == 1) {
        fp z; fp_set_zero(&z);
        if (dst == src && off == 0) { for (size_t i = len; i < n; i++) dst[i] = z; if (n > len) { ST(n - len); loopc(n - len); } return; }
        for (size_t i = 0; i < n; i++) { if (i < len) { dst[i] = src[off + i]; LD(1); } else dst[i] = z; }
        ST(n); loopc(n); CTL(2 * n); return;
    }
    /* regions of constant nonzero pattern: [0,b1) all three positions, [b1,b2) positions 0,1, [b2,b3) position 0, [b3,n) none */
    size_t b1 = len > 2 * n ? len - 2 * n : 0, b2 = len > n ? len - n : 0, b3 = len;
    if (b1 > n) b1 = n;
    if (b2 > n) b2 = n;
    if (b3 > n) b3 = n;
    size_t bnd[5] = { 0, b1, b2, b3, n }; static const int NZB[4] = { 7, 3, 1, 0 };
    CTLK(25);
    int c0 = P->c0 % 3;
    for (int q = 0; q < 4; q++) {
        int nzb = NZB[q], MT[3];
        for (int r = 0; r < 3; r++) MT[r] = mask_of(nzb, r);
        CTLK(30);                                        /* region loop, mask table (3 entries x 9 operations) */
        int rot = (int)((c0 * (bnd[q] % 3)) % 3);
        rot = (rot + 3 - c0) % 3; CTL(6);
        for (size_t i0 = bnd[q]; i0 < bnd[q + 1]; i0++) {
            fp u[3], v[3], o[3];
            HC(3);   /* Good-Thomas triple: 1/2 unit per element, loop unrolled by 3 so the rotation is constant */                             /* loop; rot update: add, compare, branch, subtract; mask lookup */
            rot = rot + c0; if (rot >= 3) rot -= 3;
            int mask = MT[rot];
            CTL(2);
            if (mask == 0) { fp_set_zero(&o[0]); o[1] = o[0]; o[2] = o[0]; }
            else {
                for (int t = 0; t < 3; t++) { CTL(3); if ((nzb >> t) & 1) { u[t] = src[off + i0 + n * (size_t)t]; LD(1); CTL(2); } }
                CTL(3);                                 /* switch on rot: constant permutation */
                switch (rot) { case 0: v[0] = u[0]; v[1] = u[1]; v[2] = u[2]; break; case 1: v[0] = u[1]; v[1] = u[2]; v[2] = u[0]; break; default: v[0] = u[2]; v[1] = u[0]; v[2] = u[1]; break; }
                dft3_masked(v, mask, o);
            }
            dst[i0] = o[0]; dst[i0 + n] = o[1]; dst[i0 + 2 * n] = o[2];
            ST(3); CTL(2);
        }
    }
}
static void stageA_inv(const plan_t *P, fp *buf, size_t outlen) {
    if (P->rows == 1) return;
    size_t n = P->n; int c0 = P->c0 % 3;
    CTL(6);
    /* regions of constant needed pattern: position i0 + n*t is needed iff i0 < outlen - n*t */
    size_t r0 = outlen < n ? outlen : n, r1 = outlen > n ? (outlen - n < n ? outlen - n : n) : 0, r2 = outlen > 2 * n ? (outlen - 2 * n < n ? outlen - 2 * n : n) : 0;
    size_t bnd[4] = { 0, r2, r1, r0 }; static const int TSET[3] = { 7, 3, 1 };
    CTLK(25);
    for (int q = 0; q < 3; q++) {
        int tset = TSET[q], NT[3];
        for (int r = 0; r < 3; r++) NT[r] = mask_of(tset, r);
        CTLK(30);
        int rot = (int)((c0 * (bnd[q] % 3)) % 3);
        rot = (rot + 3 - c0) % 3; CTL(6);
        for (size_t i0 = bnd[q]; i0 < bnd[q + 1]; i0++) {
            CTL(3 + 4 + 2);
            rot = rot + c0; if (rot >= 3) rot -= 3;
            int need = NT[rot];
            HC(3);
            fp A[3], B[3], v[3];
            for (int k = 0; k < 3; k++) A[k] = buf[i0 + n * (size_t)k];
            LD(3); CTL(2);
            B[0] = A[0]; B[1] = A[2]; B[2] = A[1];
            CTL(2);
            if (need == 7) dft3_full(B, v); else dft3_sel(B, 7, need, v);
            CTL(3);                                     /* switch on rot for the destination permutation */
            int dd[3];
            if (rot == 0) { dd[0] = 0; dd[1] = 1; dd[2] = 2; } else if (rot == 1) { dd[0] = 1; dd[1] = 2; dd[2] = 0; } else { dd[0] = 2; dd[1] = 0; dd[2] = 1; }
            for (int i1 = 0; i1 < 3; i1++) { CTL(3); if ((need >> i1) & 1) { buf[i0 + n * (size_t)dd[i1]] = v[i1]; ST(1); CTL(2); } }
        }
    }
}
/* lean variant: row r of the Good-Thomas stage for the compact vector B */
static void stageA_row(const plan_t *P, fp *tmp, int r, const fp *B, size_t lenB, size_t boff) {
    size_t n = P->n, N = P->N; int c0 = P->c0 % 3, rot = (3 - P->c0 % 3) % 3;
    size_t nb = N - boff;                               /* boff < N or boff = 0 */
    CTL(10);
    for (size_t i0 = 0; i0 < n; i0++) {
        fp u[3], v[3]; int nz[3], nzb = 0; fp o;
        HC(3);
        rot = rot + c0; if (rot >= 3) rot -= 3;
        for (int t = 0; t < 3; t++) {
            size_t idx = i0 + n * (size_t)t + nb;       /* position + N - boff */
            int any = 0; fp acc;
            CTL(2 + 3 + 2);                             /* idx (2: add, add), reduction mod N (compare, branch, subtract), any, loop-entry compare */
            if (idx >= N) idx -= N;
            for (; idx < lenB; idx += N) {              /* fold modulo x^N - 1 when lenB > N */
                CTL(2 + 2 + 1);                         /* compare, branch, first test (2), increment */
                if (!any) { acc = B[idx]; any = 1; } else fp_add(&acc, &acc, &B[idx]);
                LD(1);
            }
            CTL(3);                                     /* nz assignment, if (any), nzb bit */
            nz[t] = any; if (any) { u[t] = acc; nzb |= 1 << t; }
        }
        CTL(3);                                         /* switch on rot for the permutation */
        int mask = 0;
        for (int i1 = 0; i1 < 3; i1++) { int t = (rot + i1) % 3; if (nz[t]) { v[i1] = u[t]; mask |= 1 << i1; } }
        CTL(4);                                         /* mask from nzb: table lookup (2), mask == 0 test (2) */
        if (mask == 0) fp_set_zero(&o);
        else dft3_one(v, mask, r, &o);
        tmp[i0] = o; ST(1); CTL(1);
    }
}

void ntt_fwd(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len) {
    stageA_fwd(P, dst, src, off, len);
    CTL(4);
    for (int r = 0; r < P->rows; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(4);
        for (int p = 0; p < P->npass; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
    }
}
void ntt_inv(const plan_t *P, fp *buf, size_t outlen) {
    CTL(4);
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = P->a;
        CTL(4);
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    stageA_inv(P, buf, outlen);
}
static void conv_core(const plan_t *P, fp *buf, int mode, const fp *C) {
    for (int r = 0; r < P->rows; r++) {
        fp *row = buf + (size_t)r * P->n; int l0 = 0;
        CTL(6);
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
        pass_fused(row, P, l0, P->kk[P->npass - 1], mode, C ? C + (size_t)r * P->n : NULL);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
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

/* ---------- lean variant: the spectrum of the second operand is generated one row at a time (rows==3 plans only) ---------- */
void conv_mulc_otf(const plan_t *P, fp *dst, const fp *src, size_t off, size_t len, fp *tmp,
                   const fp *B, size_t lenB, size_t boff, size_t outlen) {
    if (P->rows != 3) { fprintf(stderr, "conv_mulc_otf needs a rows==3 plan\n"); exit(9); }
    stageA_fwd(P, dst, src, off, len);
    for (int r = 0; r < 3; r++) {
        fp *row = dst + (size_t)r * P->n; int l0 = 0;
        CTL(8);
        stageA_row(P, tmp, r, B, lenB, boff);
        for (int p = 0; p < P->npass; p++) { pass_fwd(tmp, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
        l0 = 0;
        for (int p = 0; p < P->npass - 1; p++) { pass_fwd(row, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
        pass_fused(row, P, l0, P->kk[P->npass - 1], M_MULC, tmp);
        for (int p = P->npass - 2; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    stageA_inv(P, dst, outlen);
}
plan_t plan3_for_len(size_t len) {
    for (int a = 2; a <= amax_g; a++) if (3 * ((size_t)1 << a) >= len) return make_plan(3, a);
    fprintf(stderr, "plan3: length %zu too large\n", len); exit(5);
}

/* out (P->N slots) = sum_t sign[t] * (A_t * B_t mod x^N - 1) * N, all operands compact (folded modulo x^N-1 if longer than N);
 * the first term must have sign +1.  tmpA, tmpB: P->n slots each.  Only positions < outlen of out are produced. */
void conv_sum_otf(const plan_t *P, fp *out, int nt, const fp *const *A, const size_t *lenA, const fp *const *B,
                  const size_t *lenB, const int *sign, fp *tmpA, fp *tmpB, size_t outlen) {
    if (P->rows != 3) { fprintf(stderr, "conv_sum_otf needs a rows==3 plan\n"); exit(9); }
    size_t n = P->n;
    for (int r = 0; r < 3; r++) {
        fp *row = out + (size_t)r * n;
        CTL(8);
        for (int t = 0; t < nt; t++) {
            int l0 = 0;
            budget_check();
            CTL(8);
            stageA_row(P, tmpA, r, A[t], lenA[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpA, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
            l0 = 0;
            stageA_row(P, tmpB, r, B[t], lenB[t], 0);
            for (int p = 0; p < P->npass; p++) { pass_fwd(tmpB, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(5); }
            if (t == 0) { for (size_t i = 0; i < n; i++) fp_mul(&row[i], &tmpA[i], &tmpB[i]); LD(2 * n); ST(n); }
            else if (sign[t] > 0) { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_add(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            else { for (size_t i = 0; i < n; i++) { fp x; fp_mul(&x, &tmpA[i], &tmpB[i]); fp_sub(&row[i], &row[i], &x); } LD(3 * n); ST(n); }
            loopc(n);
        }
        int l0 = P->a;
        budget_check();
        for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(5); }
    }
    budget_check();
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
    for (int i = 0; i < 64; i++) if (invcache[i].used && invcache[i].N == P->N) { *out = invcache[i].inv; return; }
    fp Nf; uint64_t v[4] = { P->N, 0, 0, 0 }; fp_from_limbs(&Nf, v);
    fp inv; fp_inv(&inv, &Nf);
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
            LD(2);
        }
        r[k] = acc; ST(1);
    }
    loopc(la * lb);
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
    LD(L); ST(L); loopc(L);
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

### loop.c

```c
/* x^E mod g by left-to-right square-and-multiply with Barrett reduction in the transform domain.
 *
 * State s = a / N (N = size of the big cyclic transform) so that no explicit scaling is ever needed:
 *   Y := conv_sq(s) = N*(s*s) = a^2/N = T/N                               (T = a^2, degree <= 2m-2)
 *   Z := conv(T1/N, mu') = q                      T1 = coefficients m..2m-2 of T, mu' = x^(N-m+2)*mu  (window lands at 0..m-2)
 *   Z := conv_{N'}(q, g)/(N N') = (q g mod x^N'-1)/N
 *   Y_i := Y_i + Y_{i+N'} - Z_i  (i < m)  = (T mod (x^N'-1) - q g mod (x^N'-1))/N = (T - q g)/N = a_new / N   (N' >= m)
 * Barrett quotient: q = floor(T1 * mu / x^(m-2)), mu = floor(x^(2m-2)/g), T1 = floor(T / x^m)  (exact for polynomials).
 * "x * s mod g" (when the exponent bit is 1) is a streaming shift with subtraction of lead * g. */
#include "common.h"
#include <time.h>

static int ebit(const uint64_t E[4], int i) { return (int)((E[i / 64] >> (i % 64)) & 1); }

static void mulx(fp *Y, const fp *G, size_t m) {
    fp c = Y[m - 1]; LD(1);
    for (size_t i = m - 1; i >= 1; i--) {
        fp t; fp_mul(&t, &c, &G[i]); fp_sub(&Y[i], &Y[i - 1], &t);
    }
    fp t; fp_mul(&t, &c, &G[0]); fp_neg(&Y[0], &t);
    LD(2 * m); ST(m); loopc(m);
}

static void combine(fp *Y, const fp *Z, size_t m, size_t Np) {
    for (size_t i = 0; i < m; i++) {
        fp y = Y[i];
        if (i + Np <= 2 * m - 2) { fp_add(&y, &y, &Y[i + Np]); LD(1); }
        fp_sub(&y, &y, &Z[i]);
        Y[i] = y;
    }
    LD(2 * m); ST(m); loopc(m);
}

void powx_mod(fp *out, const fp *g, size_t m, const uint64_t E[4], int force_rows3, int quiet) {
    plan_t PN, PNp;
    if (force_rows3) {
        int a = 2; while (3 * ((size_t)1 << a) < 2 * m - 1) a++; PN = make_plan(3, a);
        a = 2; while (3 * ((size_t)1 << a) < m + 1) a++; PNp = make_plan(3, a);
    } else { PN = plan_for_len(2 * m - 1, 1); PNp = plan_for_len(m + 1, 1); }
    size_t N = PN.N, Np = PNp.N;
    fp *Y = NEW_FP(N), *Z = NEW_FP(N), *CM = NEW_FP(N), *CG = NEW_FP(Np);
    /* Barrett data */
    {
        fp *mu = NEW_FP(m - 1);
        poly_newton_mu(mu, g, m);
        size_t gamma = N - (m - 2);
        for (size_t i = 0; i < N; i++) fp_set_zero(&CM[i]);
        ST(N); loopc(N);
        for (size_t i = 0; i < m - 1; i++) { CM[(i + gamma) % N] = mu[i]; }
        LD(m - 1); ST(m - 1); loopc(m - 1);
        xfree(mu);
        ntt_fwd(&PN, CM, CM, 0, N);
        /* g transform at size N', scaled by 1/(N N') */
        memcpy(CG, g, (m + 1) * sizeof(fp)); LD(m + 1); ST(m + 1); loopc(m + 1);
        ntt_fwd(&PNp, CG, CG, 0, m + 1);
        fp i1, i2, sc; plan_invN(&PN, &i1); plan_invN(&PNp, &i2); fp_mul(&sc, &i1, &i2);
        for (size_t i = 0; i < Np; i++) fp_mul(&CG[i], &CG[i], &sc);
        LD(Np); ST(Np); loopc(Np);
    }
    /* exponent prefix: start from the monomial x^v with v < m */
    int top = 255; while (top > 0 && !ebit(E, top)) top--;
    size_t v = 1; int bit = top;
    while (bit >= 1 && ((v << 1) | (size_t)ebit(E, bit - 1)) < m) { v = (v << 1) | (size_t)ebit(E, bit - 1); bit--; CTL(2); }
    for (size_t i = 0; i < m; i++) fp_set_zero(&Y[i]);
    ST(m); loopc(m);
    { fp invN; plan_invN(&PN, &invN); Y[v] = invN; ST(1); }
    clock_t t0 = clock(); int steps = 0;
    for (int b = bit - 1; b >= 0; b--) {
        conv_sq(&PN, Y, m, 2 * m - 1);
        conv_mulc(&PN, Z, Y, m, m - 1, CM, m - 1);
        conv_mulc(&PNp, Z, Z, 0, m - 1, CG, m);
        combine(Y, Z, m, Np);
        if (ebit(E, b)) mulx(Y, g, m);
        CTL(3);
        steps++;
        if (!quiet && steps % 32 == 0) fprintf(stderr, "  step %d/%d  %.1fs\n", steps, bit, (double)(clock() - t0) / CLOCKS_PER_SEC);
    }
    { fp Nf; uint64_t vv[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, vv);
      for (size_t i = 0; i < m; i++) fp_mul(&out[i], &Y[i], &Nf);
      LD(m); ST(m); loopc(m); }
    xfree(Y); xfree(Z); xfree(CM); xfree(CG);
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
    LD(2 * m); ST(m); loopc(m);
}

/* MU[0..m-2] = floor(x^(2m-2)/g); GR (>= m-1 slots) and Y, tmp are scratch */
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


/* Uncounted hardware-fault probe (not part of the charged program; counters are restored): a known field identity, an NTT round trip of a
 * fixed small vector and a 64-bit checksum, repeated every 32 squarings.  A mismatch is printed as FAULT and counted in fault_count. */
int fault_count = 0;
static void fault_probe(int step) {
    snap_t keep = snap(); size_t pk_keep = mem_peak;
    fp a, b, c, d; fp_from_u64(&a, 123456789ULL); fp_from_u64(&b, 987654321ULL);
    fp_mul(&c, &a, &b); fp_from_u64(&d, 123456789ULL * 987654321ULL % 1000000007ULL * 0 + 0); (void)d;
    uint64_t v[4]; fp_to_limbs(v, &c);
    int bad = !(v[0] == 121932631112635269ULL && v[1] == 0 && v[2] == 0 && v[3] == 0);
    plan_t P = plan3_for_len(96); fp *t = NEW_FP(P.N); for (size_t i = 0; i < 96; i++) fp_from_u64(&t[i], i * i + 1);
    ntt_fwd(&P, t, t, 0, 96); ntt_inv(&P, t, 96);
    fp Nf; { uint64_t w[4] = { P.N, 0, 0, 0 }; fp_from_limbs(&Nf, w); }
    for (size_t i = 0; i < 96; i++) { fp e, f; fp_from_u64(&e, i * i + 1); fp_mul(&f, &e, &Nf); if (!fp_eq(&f, &t[i])) bad = 1; }
    xfree(t);
    snap_restore(keep); mem_peak = pk_keep;
    if (bad) { fault_count++; printf("FAULT detected at squaring step %d\n", step); fflush(stdout); }
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
    int top = 255; while (top > 0 && !ebit(E, top)) top--;
    size_t v = 1; int bit = top;
    while (bit >= 1 && ((v << 1) | (size_t)ebit(E, bit - 1)) < m) { v = (v << 1) | (size_t)ebit(E, bit - 1); bit--; CTL(12); }
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
        ST(m); loopc(m);   /* fold: unrolled, 1/2 unit per element */
        for (size_t i = 0; i + 1 < m; i++) Y[i] = Y[m + i];
        LD(m - 1); ST(m - 1); loopc(m - 1);
        conv_mulc_otf(&PN, Y, Y, 0, m - 1, tmp, MU, m - 1, gamma, m - 1);
        conv_mulc_otf(&PNp, Y, Y, 0, m - 1, tmp, g, m + 1, 0, m);
        for (size_t i = 0; i < m; i++) fp_sub(&Y[i], &F[i], &Y[i]);
        LD(2 * m); ST(m); loopc(m);
        if (ebit(E, b)) mulx_(Y, g, m);
        CTL(3);
        steps++;
        if (steps % 32 == 0) fault_probe(steps);
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
    X.rnd += 1; X.ctl += 2;      /* one random 256-bit word, one mask, one spare */
}

size_t poly_degree_m(int r) { size_t D = 1; for (int i = 0; i < 6 + r; i++) D *= 5; return (D - 1) / 2; }

void bound_mem_since(snap_t s0) {
    snap_t d = snap_sub(snap(), s0);
    uint64_t ops = snap_arith(d);
    X.ld += 2 * ops; X.st += ops; X.ctl += ops;
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
    fp_inv(&ipsi, &psi);
    { fp two, half; fp_add(&two, &one, &one); fp_inv(&half, &two); u = half; }
    s = one;
    size_t nrow = P.n, rowi = 0, posi = 0;            /* layout position of point k: row (k mod 3) * n + bit-reversed (k mod n), kept incrementally */
    CTL(8);
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
        buf[(P.rows == 3 ? rowi * nrow : 0) + posi] = v; ST(1);
        CTL(3 + 3 + 2 + 2);                           /* loop (3); row update: add, compare, branch (3); address: mul, add (2); spare/pointer for s,u (2) */
        if (P.rows == 3) { rowi++; if (rowi == 3) rowi = 0; }
        /* bit-reversed increment of the position counter (k mod n) */
        { size_t bit = nrow >> 1; CTL(3);
          while (posi & bit) { posi ^= bit; bit >>= 1; CTL(5); }   /* test, branch, xor, shift, loop */
          posi |= bit; CTL(2); }
        fp_mul(&s, &s, &psi); fp_mul(&u, &u, &ipsi);
    }
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
    CTL(dA + dB + 2);
    if (dA < dB) { fp *t = A; A = B; B = t; int td = dA; dA = dB; dB = td; }
    while (dB >= 0) {
        fp ilc; fp_inv(&ilc, &B[dB]); LD(1);
        while (dA >= dB) {
            fp q; fp_mul(&q, &A[dA], &ilc); LD(1);
            size_t sh = (size_t)(dA - dB);
            for (int i = 0; i < dB; i++) { fp t; fp_mul(&t, &q, &B[i]); fp_sub(&A[sh + i], &A[sh + i], &t); }
            LD(2 * (size_t)dB); ST(dB); loopc(dB);
            fp_set_zero(&A[dA]); ST(1);
            int nd = dA - 1; while (nd >= 0 && fp_is_zero(&A[nd])) nd--;
            CTL(dA - nd + 1); LD(dA - nd);
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
        fp av; fp_from_u64(&av, (uint64_t)tries + 1); CTL(1);   /* deterministic shifts a = 1, 2, 3, ... (executed-outcome convention) */
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
    CTL(5 * it);
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
    fp inv; fp_inv(&inv, &b[lb - 1]);
    *lq = la - lb + 1;
    for (size_t i = la - lb + 1; i-- > 0;) {
        fp qi; fp_mul(&qi, &w[i + lb - 1], &inv); LD(1);
        q[i] = qi; ST(1);
        for (size_t j = 0; j + 1 < lb; j++) { fp t; fp_mul(&t, &qi, &b[j]); fp_sub(&w[i + j], &w[i + j], &t); }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(8);
        budget_check();
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
    LD(2 * (len - N)); ST(len - N); loopc(len - N);
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
            ST(l);
            for (int t = 0; t < 2; t++) {
                size_t la = A->len[2 * i + t], lb = B->len[2 * t + j];
                if (!la || !lb) continue;
                fp *tmp = NEW_FP(la + lb - 1);
                poly_mul_naive(tmp, A->e[2 * i + t], la, B->e[2 * t + j], lb);
                for (size_t u = 0; u < la + lb - 1; u++) fp_add(&o[u], &o[u], &tmp[u]);
                LD(2 * (la + lb - 1)); ST(la + lb - 1); loopc(la + lb - 1);
                xfree(tmp);
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
        budget_check(); CTL(12);
        size_t dq = lx - ly;
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
    hgcd_stat_calls++; CTL(40);
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

/* ---- gcd */
static size_t monic_out(fp *out, const fp *x, size_t lx) {
    if (!lx) return 0;
    fp inv; fp_inv(&inv, &x[lx - 1]);
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
 * usage: lean_attack r ncentres seed [j0] [verbose] [budget_gcd budget_root] [fixed_line]
 * Per centre: build g by evaluation + inverse NTT, S^((p-1)/2) mod g (lean in-place schedule), gcd(g, S^h-1) by half-gcd,
 * root splitting, back-map, verification by two reference hashes.  Stops after the first verified collision or after
 * ncentres failed centres.  Every field operation, 256-bit load/store, loop-control op and random word is counted. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include "budgets.h"
#include <time.h>
#include <math.h>

#ifndef BUDGET_GCD
#define BUDGET_GCD 0ULL   /* 0: use the table budget_table() below */
#endif
#ifndef BUDGET_ROOT
#define BUDGET_ROOT 0ULL
#endif
#ifndef BUDGET_FIN
#define BUDGET_FIN 100000ULL
#endif
#ifndef DEG_CAP
#define DEG_CAP 16
#endif
/* budgets per target (operations of the run's cost model); derivation in proof.md section 4.4 (computed by bound_gcd.c) */
static void budget_table(int r, uint64_t *gcd, uint64_t *root) {
    switch (r) {
    case 1: *gcd = BUDGET_R1_GCD; *root = BUDGET_R1_ROOT; break;
    case 2: *gcd = BUDGET_R2_GCD; *root = BUDGET_R2_ROOT; break;
    default: *gcd = 0; *root = 0;
    }
}
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
    uint64_t bgcd = BUDGET_GCD, broot = BUDGET_ROOT;
    /* executed-outcome form: no budget halts (a halt is not an executed-outcome event); budgets only if given on the command line */
    if (argc > 6 && strtoull(argv[6], 0, 0)) bgcd = strtoull(argv[6], 0, 0);
    if (argc > 7 && strtoull(argv[7], 0, 0)) broot = strtoull(argv[7], 0, 0);
    int fixed_line = argc > 8 ? atoi(argv[8]) : 0;   /* 1: every centre uses line j0 */
    int amax = 2; while (3 * ((size_t)1 << amax) < 2 * m - 1) amax++;
    printf("r=%d ncentres=%d seed=%llu m=%zu\n", r, ncen, (unsigned long long)seed, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    uint64_t tot_all = 0, tot_arith = 0; double tot_sec = 0; snap_t tot_t; memset(&tot_t, 0, sizeof tot_t);
    int success = 0, centres_done = 0; uint64_t root_spent = 0, gcd_gap = 0, max_gcd_gap = 0, max_root_gap = 0;
    stage_begin(); ntt_init(amax); stage_end("ntt_init");
    printf("INIT arith=%llu other=%llu total=%llu", (unsigned long long)snap_arith(st[0].d), (unsigned long long)(snap_total(st[0].d) - snap_arith(st[0].d)), (unsigned long long)snap_total(st[0].d)); putchar(10);
    uint64_t tot_hc = st[0].d.hc; uint64_t pre_all = snap_total(st[0].d) - (st[0].d.hc + 1) / 2; tot_all += pre_all; tot_arith += snap_arith(st[0].d); nst = 0;
    tot_t.add += st[0].d.add; tot_t.sub += st[0].d.sub; tot_t.mul += st[0].d.mul; tot_t.sqr += st[0].d.sqr; tot_t.ld += st[0].d.ld; tot_t.st += st[0].d.st; tot_t.ctl += st[0].d.ctl;
    for (int ci = 0; ci < ncen && !success; ci++) {
        int j = fixed_line ? j0 % 3 : (j0 + ci) % 3;
        nst = 0;
        line_t L;
        stage_begin(); { snap_t s0 = snap(); line_setup(&L, j); bound_mem_since(s0); } stage_end("line_setup");
        fp c;
        stage_begin(); fp_from_u64(&c, (uint64_t)ci + 1); CTL(1); stage_end("centre c_i = i (i = 1, 2, 3, ...)");
        fp *g = NEW_FP(m + 1);
        stage_begin(); build_g(g, &L, &c, r, 0); stage_end("build g");
        fp *F = NEW_FP(m);
        stage_begin(); powx_lean(F, g, m, PALLAS_PM1H, verbose ? 2 : 1); stage_end("S^((p-1)/2) mod g");
        fp one; fp_set_one(&one);
        stage_begin();
        fp_sub(&F[0], &F[0], &one);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(4 * m); LD(m + 1);
        fp G[DEG_CAP + 1]; size_t lG = 0;
        if (bgcd) budget_arm(bgcd, "gcd");
        if (dR >= 0) lG = poly_gcd_fast_own(G, DEG_CAP + 1, g, m + 1, F, (size_t)dR + 1);
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
            stage_begin(); if (broot) budget_arm(broot - root_spent > 0 ? broot - root_spent : 1, "root"); found = find_root(&S, G, dG); budget_check(); if (budget_maxgap() > max_root_gap) max_root_gap = budget_maxgap(); budget_arm(0, ""); stage_end("root finding"); root_spent += snap_total(st[nst - 1].d);
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
                { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += ops; }
                stage_end("verification (2 reference hashes)");
                int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
                success = found && fp_eq(&dg1, &dg2) && !same_in;
            }
        }
        uint64_t all = 0, arith = 0; double sec = 0;
        for (int i = 0; i < nst; i++) { tot_hc += st[i].d.hc; all += snap_total(st[i].d) - (st[i].d.hc + 1) / 2; arith += snap_arith(st[i].d); sec += st[i].sec; }
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
    tot_all += (tot_hc + 1) / 2;   /* half units summed over the whole run, rounded up once */
    extern int fault_count; printf("FAULTS detected=%d\n", fault_count);
    printf("HALFUNITS hc=%llu\n", (unsigned long long)tot_hc);
    int C = 216 + 21 * r;
    printf("SUMMARY r=%d centres=%d success=%d total_all=%llu total_arith=%llu units=%.1f log2_units=%.4f heap_peak=%zu secs=%.1f\n", r, centres_done, success,
           (unsigned long long)tot_all, (unsigned long long)tot_arith, (double)tot_all / C, log2((double)tot_all / C), gpeak, tot_sec);
    printf("GAPS gcd=%llu root=%llu", (unsigned long long)max_gcd_gap, (unsigned long long)max_root_gap); putchar(10);
    printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu", (unsigned long long)tot_t.add, (unsigned long long)tot_t.sub, (unsigned long long)tot_t.mul, (unsigned long long)tot_t.sqr, (unsigned long long)tot_t.ld, (unsigned long long)tot_t.st, (unsigned long long)tot_t.ctl, (unsigned long long)tot_t.rnd, (unsigned long long)tot_t.perm);
    putchar(10);
    return success ? 0 : 1;
}
```

