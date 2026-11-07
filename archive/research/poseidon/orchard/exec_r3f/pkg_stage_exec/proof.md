# Orchard Poseidon, r = 3: one deterministic run on the fixed target, executed operation count (two free rounds on a line, odd part about a fixed centre, half-gcd)

## 1. Claim

Target: `poseidon-orchard-r3-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, three partial rounds 4, 5 and 6, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

* `success_probability = 1`: the procedure is deterministic (centres `c_i = i` in the fixed order `i = 1, 2, 3, ...`, section 4) and it was executed once, from the start, on the fixed target, where it stopped with the collision at trial 1 (`c = 1`); every executed trial, failed ones included, is charged. There is no probability statement and no worst-case bound of the algorithm anywhere in this document (the constants of stage I and of the stage bookkeeping, section 4.2, are bounds on fixed straight-line work).
* `time_log2 = 30.62543` in target-compression units (`C(3) = 279` primitive operations per unit): the executed operation count of that one run, all 1 trials, `N = 462,143,854,728` operations (section 6), `log2(N / 279) = 30.62543`, rounded up at five decimals. The twiddle table is built inside the run and is part of `N`, so `preprocessing_log2 = 0`; the memory of this preprocessing is covered by the footprint of section 7 (the twiddle table is one of its buffers).
* `memory_log2_bytes = 28.114` (`290,356,404` bytes, section 7): the larger of (i) the whole statically linked executable image, whose bss holds the static arena that serves every buffer, plus a stack bound, and (ii) the measured peak resident memory of the run. The normalized cost is `30.62543 + 8.114 = 38.73943`.
* No selection: the start and the order of the centres are fixed in the source; no centre was chosen. The run began at `c_1 = 1`, every trial it executed is in the count `N`, and the table of section 6 lists them all. An earlier build of the same algorithm with the C library allocator (the r = 3 entry filed before this one) ran centre 1, and monitoring runs of centres 2 to 11, after the order of the centres was fixed in the source; they select nothing and change no parameter, and the result of this run does not depend on them. The algorithm is the single counted run of this source; no other run is part of `N`. `memory` is the maximum over the trials (the buffers of a trial are released before the next).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^9`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is a known approach. What is offered here is a complete finite implementation with an executed operation ledger and a low-memory schedule. No heuristic premise is used.
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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6 (partial), 60, 61, 62, 63 (full) put nine S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^9 = D = 1953125`. The leading coefficient is obtained by
propagating leading coefficients through the nine layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = 0x11f9cfdeecb8c5965318cbdc58480d2e6db510f12862658af639ce81578c3e23`
(computed; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 976562`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 1572864 = 3 * 2^19` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 3145728` evaluations of `F` are each charged as
one target-compression unit (`C(3) = 279` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, and the executed shifts, masks, ors, modulo operations and loop control of the bit-reversed index `layout_index`, which are counted inside that function) is charged on top.


## 4. The program (one deterministic run)

```
init:   twiddle table
setup:  the line (line_setup)
A  c := c_i = i (the integer i as a field element; one conversion, 2 control ops)
B  g := monic g_c, by section 3 (3145728 evaluations + one inverse NTT of size 1572864 + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; 234 modular squarings, 45 of the steps also multiply by S by a streaming shift)
D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
E  S := a root of G                 (only if deg G >= 1: root isolation, for degree 1 S = -G_0; otherwise the trial ends and the next centre is tried)
F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
G  verify: the two reference hashes (279 operations each) are equal and the pairs differ -> stop the search; otherwise the next trial
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each (section 4.2)
I  report: the stage rows, the trial rows and the counters are formatted into one buffer and written by one system call; exit (stage I, section 4.2)
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 19 bits after the leading one are zero, so the program starts from the monomial `S^v` with `v = 2^19 < m` (this absorbs 19 of the 253 squarings, 19 + 234 = 253), and the squaring loop of stage C has 234 steps, of which 45 also multiply by `S` (a streaming shift).

Determinism. The program takes no input and reads no file. It executes init and setup once, then trials `i = 1, 2, 3, ...` (stages A to D, and E to G when `deg G >= 1`; the source caps the search at `MAXTR = 64` trials, exit status 2 without a collision, a cap this run did not reach), and, at the first trial whose two reference hashes agree with distinct pairs, runs stage H and returns exit status 0. The only random draws are the shifts of the root isolation (generator seeded with the constant 1), which are made only in a trial with `deg G >= 2`; a trial with `deg G = 1` makes none. Every trial, failed or not, is executed to its end and counted by the same counters; the stages form a chain without a gap (`stage_open` in `single.c` closes the previous stage as it opens the next, so every charged operation, the control of the trial loop included, belongs to exactly one stage and one trial); and the buffers of a failed trial are released before the next trial begins. In the executed run the trials are listed in section 6; the last trial is the one that produced the certificate.

### 4.2 Machine model and charging rules
Every item below is counted by the executing code at the statement that executes it; none is estimated. The complete source is in section 9.
* canonical `F_p` addition, subtraction, negation (one subtraction), doubling (one addition), multiplication and squaring: 1 each; inversion and exponentiation are expanded (`a^(p-2)`: 254 squarings and 76 multiplications, 330 operations; `x^e`; `x^((p-1)/2)` on a single element: counted exactly).
* load or store of a 256-bit element of an array: 1 each, and each such access is charged together with one address-formation operation (one control operation): `LD(n)` adds `n` to the load counter and `n` to the control counter, `ST(n)` likewise.
* every loop that is not unrolled: `3n + 2` control operations for `n` iterations (the index update, the bound comparison and the conditional branch of each iteration, and one comparison and branch when the loop is left); `loopc(n)` adds exactly this after such a loop of `n` iterations. Loops that are unrolled (macro `FOR8` in `common.h`: the pointwise, copy, fold and subtraction loops of the powering and of the products) execute their body 8 times per pass without any branch inside the body; the macro itself adds 1 operation for the bound `n & ~7`, 3 operations at the end of every pass of 8 (index update, comparison, branch), 2 when the main loop is left, and then runs the remaining 0 to 7 elements in a plain loop (3 per iteration, 2 on exit). The loads and stores of the body are charged inside the body, per element.
* every other executed index or control operation, one each: shift, mask, or, addition, subtraction, multiplication, modulo, comparison, conditional branch, and the selection of an element of the register block (16 data words) by a computed index. They are added with `CTL(k)` next to the statement that executes them, and data-dependent tests are charged per executed test.
* transform kernels are generated, straight-line code (`gen_kern.py` is part of the source of section 9; its output `ntt_kern.h` and `ntt_a3.h` are listed there). A block kernel for `k` layers (1 to 4; 2^k data words `x[]`) has no loop and no branch: each butterfly is the literal statements `fp_sub`, `fp_add`, `fp_mul` (three field operations, none for the multiplication when the twiddle is 1 at `b = 0`), and every twiddle load is a literal statement carrying its own charge on the same line: the first twiddle of a layer `tw + (b << sjs[j])`: shift and addition (2 operations), the load and its address formation (`LD(1)`); every further twiddle of the layer: one addition of the stride `D[j]` and `LD(1)`. In the inverse kernel the first twiddle address `tw + ((nh - (b << sj[j])) << sh)` costs 4 operations. The kernel for `b = 0` is a second generated variant that omits the twiddle of `tp = 0` (it is 1) and its multiplication. A pass function (`pf1..4`, `pi1..4`, `pu1..4_sq/_mul` in `ntt_kern.h`) contains the group loop and the block loop around the kernel: group base address (1), block base address (1), 3 operations per loop iteration and 2 on loop exit as written in the generated code, the loads and stores of the 2^k words of the block each with `LD(1)` / `ST(1)` (one address formation each); the block `b = 0` of a group is peeled so that no per-block test of `b` is executed. The wrapper (`pass_fwd`, `pass_inv`, `pass_fused`) charges the computation of the pass constants (a loop over the layers) and the `switch` on `k` (and on the mode) once per pass.
* working registers (disclosed assumption): a block keeps its 2^k <= 16 data words `x[]` in registers; the twiddle operand and the butterfly temporary need two further words, so the kernels assume a register file of 18 words of 256 bits. Strides, shift counts, base pointers and loop indices are held in integer registers (not charged as memory accesses). The 256-bit constants of the radix-3 kernels (`W3[1]`, `W3[2]`, `CH`, `DL`) are not assumed to be in registers: every use is charged as one load (`LD(1)` in the generated statement). The real cost of a machine with fewer registers would be higher; this is the one structural assumption of the model.
* half twiddle table: only `tw[m] = rho^(2m)` is stored (`nmax/4` words, plus the word `RHO = rho` in static data). A twiddle `rho^v` with odd `v` is recomputed as `tw[(v-1)/2] * RHO` by `twget` (header of `ntt_kern.h`): the table word is the usual charged load, `RHO` is one more charged load, and the multiplication is a counted `fp_mul`. Every fetch through `twget` also charges 3 integer operations (parity test, branch, index shift). Odd virtual indices occur only in layer 0 of a pass with `l0 + sh = 0`; in layers `j >= 1` the index is even and is formed with a shift by one position less (charged). The table build (stage "init") performs `nmax/4 - 1` multiplications instead of `nmax/2 - 1`.
* a random word: 1 plus 2 control operations for a 254-bit word (`rnd_fp254`).
* the bit loops of inversion and exponentiation executed outside stages with a per-operation rule: 2,310 control operations per inversion.
* small-degree work in the line setup, the schoolbook `Z^((p-1)/2)` for `d <= 40` and the verification is charged generously: on top of every arithmetic operation 2 loads, 1 store and 6 control operations.
* the reduced permutation evaluations of stage B: 279 each (section 3), instead of their (smaller) expanded arithmetic. Nothing else is charged as a unit.
* dispatch and selection: the source contains `switch` statements (on `k` and on the mode, once per pass) and three tables of function pointers (`RGF`, `RGI`, `RGR`: the region driver of the radix-3 stage chosen by the pattern of nonzero inputs and the class of `c0`, once per region); each is charged by `CTL` next to the statement (4 operations for a table lookup and indirect call, 4 for the `switch` on `k`). Every other selection (`if`, `?:`, `while` tests, the test of the mode in `pass_fused`, the tests of `P->rows`, the choice of the operand pointer in `conv_core`, the validity tests, the choice between the schoolbook and the fast division, the tests of the recursion in `hgcd`) is charged by a `CTL` next to the statement, as the comments show.
* radix-3 stage (generated in `ntt_a3.h`): the positions `i0` of a row are processed by straight-line position kernels, one per (pattern of nonzero inputs, rotation): `LD(1)` per nonzero input, the field operations of the selected linear map written out (each multiplication by a constant preceded by the `LD(1)` of the constant), `ST(1)` per output. A region driver runs the kernels of the three phases of `i0 mod 3` over a range of positions: head (positions until the phase is 0), a loop of three positions per iteration (`i += 3`, comparison, branch: 4 operations per iteration), tail; every test of the head, loop bound and tail is charged next to its statement. The ranges of constant pattern are computed by `split_regions` (breakpoints, insertion sort, patterns), each of whose operations is charged next to its statement; one call costs a few hundred operations.
* every executed statement of the stages (`poly_gcd_own`, `hgcd`, `divrem_fast`, `gcd_cl`, `taylor_shift`, `split_find_root`) is charged where it is written, including the compare, branch and subtraction of every loop test, as the comments of section 9 show.
* Montgomery conversions: every conversion of an integer to or from the internal representation (`fp_from_limbs`, `fp_to_limbs`, `fp_from_u64`, `fp_from_hex`; for example the centre `c_i` of stage A, the random words in `taylor_shift` and `rnd_fp254`, the constants of the twiddle setup, the inputs of the two reference hashes, and the six conversions of the output in stage H) is one Montgomery multiplication and is charged as one field multiplication: `pallas.c` increments the multiplication counter in `fp_from_limbs` and `fp_to_limbs`, and every other conversion function calls them. The constants of `pallas_consts.h` are stored in Montgomery form and need no conversion.
* output (stages H and I): in stage H the program converts `nk1`, `rho1`, `nk2`, `rho2`, the digest and the centre out of the Montgomery representation (6 charged multiplications) and encodes each as 64 hexadecimal digits in `enc_hex` of `single.c`, 12 operations per digit (loop update, comparison and branch; `pos = 63 - i`; word index; mask; scaling of the shift count; shift; mask; table load; byte store) and 5 more per call. In stage I the program charges, before it formats its report and before it prints the one total, everything it executes after the last algorithm step; this is inside the total `N`: (i) the formatting and copying of the whole report: every report line, the collision lines included, is formatted by the small `printf` of `nolibc.c` (`vfmt`, a loop over the format string with one digit loop per number and one copy loop per field; it has no division, modulo or floating point: a decimal number is formed by comparing with the powers of ten and subtracting them, at most about 44 operations per digit produced and at most about 100 for the scan for the leading power; a hexadecimal one by shifts and masks) into one static buffer of `OUTCAP` = 8,192 bytes; the format scan, padding and copy loops cost at most about 10 operations per byte, and the parse of a conversion specification and the fetch of its argument at most about 150 per conversion, which yields at least one byte, so `FMT_PER_BYTE` = 400 per byte is an upper bound, and the buffer is charged in full, `400 * 8,192` = 3,276,800 operations, whatever it holds (the program ends with exit status 3, and no collision line, if the buffer overflowed, which the check shows did not happen); (ii) the loops of the report over the stage and trial rows and the sums (the report prints no quotient and no logarithm): `REPORT_LOOPS` = 20,000; (iii) the process entry (`_start`, `c_start`, under 20 instructions) and the buffer-length check: 100; (iv) the single `write` system call that emits the whole buffer: `SYS_WRITE` = 10,000 + (8,192 << 3) = 75,536 operations (the instruction work in the process is about 10 instructions; the rest stands for the kernel's copy of the buffer and its own instructions); (v) the single `exit_group` system call: `SYS_EXIT` = 10,000; (vi) the bookkeeping of the stages (reading the nine counters, the subtractions and additions into the stage row, the search of the row by name, the reset of the memory peak): `STAGE_BK` = 1,000 per stage opened (a bound: under 400 operations), plus 1,000 for the closing of stage I; (vii) the statements of `main` before the counters start (`rng_seed`, `poly_degree_m`, the argument test): `PROLOGUE` = 500 (a bound), and the four snapshots of the counters in `powx_lean` for the powering breakdown line: 500 (a bound). The write is made once, as the last action, so the total printed in the buffer is the total of the counters with all of (i) to (vii) already added. There is no other system call in the run: the program contains no `mmap`, `munmap`, `clock_gettime` or second `write`.
* allocator: `xalloc` and `xfree` (`common.c`) serve every buffer from one static arena in the bss (no system call), with a 64-byte header per block (size, size of the previous block, in-use flag) and a walk over the blocks in address order: a request of more than 196,608 bytes (header included) takes the first free block that fits and is cut from its bottom, a smaller request takes the last free block that fits and is cut from its top; a block is split when the remainder is at least 128 bytes, and `xfree` merges the block with a free neighbour on either side. Every executed load, store, comparison, branch and address or size computation of both functions is charged where it is written in `common.c`, with the rules of this section (`ldz` and `stz` charge a load or store and its address operation; each comparison and its branch is charged 2; each add, subtract or mask 1; each loop pass of the block search 3), and the statistics lines (bytes in use, live blocks, peaks, extent) are charged a flat `ALLOC_STATS` = 64 per call (a bound: about 40). The allocator charges are inside the totals of the stages in which the calls occur. The memory it uses is the arena of section 7.
* loops, stated plainly. Every loop of the C code is charged per iteration (`3n + 2`, plus the address operations of its loads and stores) except those that are written out straight-line in the source: (i) the loops in the generated kernels (`ntt_kern.h`, `ntt_a3.h`, produced by `gen_kern.py`): the butterflies of a block and the radix-3 position kernels contain no loop at all, only the group loop and block loop around them, which are charged per iteration; (ii) the macro `FOR8` (`common.h`), which copies the loop body eight times in the source per pass (genuinely unrolled by 8, with a plain loop for the remaining 0 to 7 elements) and is charged 3 per pass of 8 plus the entry and exit terms above. The sites of `FOR8` are: `ntt.c` (8 lines), `lean.c` (5 lines). Every other `for` or `while` loop in the source (the copies, folds and scalings charged with `loopc`, the schoolbook loops, the Euclid loops, the loops of the setup) is a real loop charged `3n + 2` and is not claimed to be unrolled; a compiler may unroll it, which would only lower the real cost.
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

`hgcd(a, b, k)` (`deg a = n`) returns, for `h = max{ j : d_j <= k }`, the matrix `R_h` (when asked) and the pair `(r_h, r_{h+1})`. The code: if `b = 0` or `n - deg b > k` return the identity. If `k <= 96`, plain Euclid (`poly_divrem_naive`) while the next quotient degree fits the remaining parameter; a division step whose quotient has two coefficients (the normal case) is one pass over the remainder, `r_k = a_k - q0 b_k - q1 b_(k-1)`, with `b_(k-1)` kept from the previous iteration and no copy of `a` (per element 2 loads, 2 multiplications, 2 subtractions, 1 store, each load and store with its address operation, the loop control of 3 and the test `if (k)` of 2 operations), and `R := R Q` for a two-coefficient quotient is likewise one pass per entry pair (`mul_add_q2`).
Otherwise, `k1 = ceil(k/2)` (`k1 = floor(n/2)` if `2 k1 > n`), `s = n - 2 k1`: (1) `R1 = hgcd(a quo x^s, b quo x^s, k1)` (the top parts, matrix wanted); (2) `(c, d) = R1^{-1} (a, b)` by NTT products (`apply_inv`): `c = s (r22 a - r12 b)`, `d = s (r11 b - r21 a)`, `s = (-1)^h`, evaluated cyclically on `3 * 2^j` points (the high coefficients of `c` and `d` cancel, so the cyclic result is exact); the Good-Thomas rows are processed one at a time, and in each row `a` and `b` and each of the four matrix entries are transformed once (six forward transforms of a row) and the two output rows are inverse transformed (`conv_bilin_otf`), the sign of each output being absorbed in the scale factor `1/N`; (3) if `d = 0` or the next quotient degree `deg c - deg d` exceeds `k - d_1`
(`d_1 = deg R1`) return `R1` and `(c, d)`; (4) divide `c = q d + e` (`divrem_any`); (5) `R2, (c', d') = hgcd(d, e, k - d_1 - deg q)`; return `R1 Q R2` (matrix products by NTT, only if the matrix is wanted; the product of the two 2 x 2 matrices transforms each of the eight entries once per row, with the right-factor entries of one column pair held and the left-factor entries streamed, and inverse transforms the four outputs, `conv_bilin_otf` again).
The outer function `poly_gcd_own` repeats, while `deg b > 0` and `n = deg a > 192`: `(c, d) = hgcd(a, b, floor((n+1)/2))`, one division `c = q d + e` and `(a, b) := (d, e)`; at or below 192 it runs classical Euclid; at the end it scales the last nonzero remainder to be monic (one inversion, `deg + 1` multiplications).

**Division.** `divrem_any(a, b)`, `la - lb + 1` quotient coefficients `kq`: if `kq <= 64` or `lb <= 64` schoolbook (`poly_divrem_naive`); otherwise (`divrem_fast`) the reversed Newton identity: `q_rev = (a_rev * inv(b_rev mod x^kq)) mod x^kq`, `q = reverse(q_rev)`, `r = a - q b` (low `lb - 1` coefficients), with
the reciprocal by Newton iteration `g_{2t} = g_t - x^t (g_t * mid(f g_t))` and all products by `poly_mul`.

## 5. Why the output is a collision

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes
and compares them; the program returns success only if they are equal and the pairs differ. Independent of the program, the pair in `certificates/` is checked by the organizer's hash, and the digest `0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec` is printed by the run.

## 6. Ledger: the executed run (primitive operations; `C(3) = 279`)

The count is the instrumented total of one execution of the shipped source (`gcc -O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c`, run as `single 1` under `ulimit -s 64`; the argument only turns on printing of the powering breakdown for the first trial). `arith` = additions, subtractions, multiplications, squarings; `other` = loads, stores, control, random words, and the 279-operation unit charges. Nothing is extrapolated or taken from another run: every figure below is a counter of the same execution; the only bounds are the stated constants of stage I and of the stage bookkeeping (section 4.2). The program prints one total: the sum of the stage rows, the sum of the trial rows and the counters of the whole run are computed separately and printed in the line `RECONCILE`, which reads `ok=1` only if the three are equal (stages 462,143,854,728 = trials 462,143,854,728 = counters 462,143,854,728). The table below and the table of trials are two groupings of the same counters.

| stage | arith | other | total |
|---|---:|---:|---:|
| init: twiddle table (once) | 263,117 | 1,852,420 | 2,115,537 |
| setup: the line | 391 | 4,519 | 4,910 |
| A: centre c_i = i (all trials) | 1 | 1,124 | 1,125 |
| B: 3,145,728 evaluations (279 units each) + inverse NTT 1,572,864 + normalisation (all trials) | 56,924,395 | 1,210,603,350 | 1,267,527,745 |
| C: `S^((p-1)/2) mod g` (m = 976562, 234 steps per trial, all trials) | 145,991,406,825 | 244,090,390,811 | 390,081,797,636 |
| D: half-gcd of (g, R - 1) (all trials) | 20,120,915,196 | 50,668,051,095 | 70,788,966,291 |
| E: root of G (last trial only) | 2 | 1,108 | 1,110 |
| F: square root, back-map (last trial only) | 3,068 | 40,614 | 43,682 |
| G: two reference hashes (last trial only) | 558 | 6,054 | 6,612 |
| H: canonical encoding of the output (6 conversions, 384 hexadecimal digits) | 6 | 5,638 | 5,644 |
| I: formatting of the report buffer (bound), the single write, exit_group, entry (constants) | 0 | 3,384,436 | 3,384,436 |
| total N | | | 462,143,854,728 |

| trial | centre c_i | deg G | half-gcd charge | charge of the trial (stages A to G) |
|---:|---:|---:|---:|---:|
| 1 | 1 | 1 | 70,788,965,277 | 462,138,344,201 |
| outside the trials: init, line setup, stage H | | | | 5,510,527 |
| total N | | | | 462,143,854,728 |

Total `N = 462,143,854,728` operations (stage rows, trial rows plus the row outside the trials, and the counters of the run, all equal) `= 1,656,429,586.8` units, `log2(N / 279) = 30.62543`, claimed as `30.62543` (rounded up).
The half-gcd of stage D charged 70,788,965,277 operations in this run (summed over all trials, degrees 976562 and 976561). Composition by type of the run (init included; the control counter includes the address operations of loads and stores): add `56,286,046,560`, sub `54,465,276,770`, mul `54,434,033,657`, sqr `984,156,572`, loads `62,794,777,849`, stores `31,857,238,448`, control `200,444,666,760`, unit charges `877,658,112`.

Stage C in detail (m = 976562): Newton for MU: 1,482,633,071 operations; prefix and scaling: 12,699,152; 234 squaring steps at 1,660,612,839 operations each (arith 621,669,807). Of the arithmetic of stage C, 145,991,406,825 operations; the transforms are the largest term.

### 6.1 Ledger recomputation

```python
from math import log2, ceil
C = 279
stages = [2115537, 4910, 1125, 1267527745, 390081797636, 70788966291, 1110, 43682, 6612, 5644, 3384436]   # init, line setup, A, B, C, D, E, F, G, H
trials = [462138344201]   # stages A to G of each trial
outside = 5510527     # init, line setup, stage H
N = sum(stages)
assert N == sum(trials) + outside
print('N =', format(N, ','), ' units =', round(N / C, 1), ' time_log2 =', '%.5f' % (ceil(log2(N / C) * 100000 - 1e-6) / 100000))
```

## 7. Memory

The executable is linked statically and without any C library (`gcc -O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c`): `nolibc.c` (section 9) supplies the process entry, the two system calls the program executes (`write`, once, and `exit_group`, once), `memcpy`, `memset`, `memmove`, `strcmp` and the small `printf` (no division, modulo or floating point) that appends the report to one buffer; there is no loader, no shared library, no other library code and no other system call. Three terms make up the memory.
(a) The whole executable image: every loadable segment, text + data + bss as printed by `size` for the linked program: text 276,852 + data 32 + bss 290,013,984 = 290,290,868 bytes. It consists of the code, tables and static state of the shipped source only (the transform kernels are most of it).
(b) The heap is inside term (a): every buffer of the program is served by `xalloc` from one static arena of `290,000,000` bytes in the bss (`ARENA` in `common.h`, a multiple of 64; the bss of the image is `290,013,984` bytes and contains it together with the 8,192-byte output buffer and the other static state). Nothing is mapped from the kernel at run time. The size is fixed in `common.h`: a multiple of 64 chosen above the measured need, with no tuning (the peak of the bytes in use is 236,357,184, the rest is space left between blocks and the margin; the arena is not claimed to be the smallest that fits); the run prints the highest end address of any block over the whole run, `290,000,000` bytes (`ARENA size=... extent=...` in the run output; it equals the arena size because small blocks are cut from the top of the free block they use), and stops with status 2 if a request does not fit, which did not happen. Each block has a 64-byte header (size, size of the previous block, in-use flag; it keeps the payload 64-byte aligned) and a payload rounded up to a multiple of 64 bytes; the allocator is described, with its charges, in section 4.2. At the peak of the bytes in use (stage D) there were 11 live blocks holding 236,356,480 bytes of payload; their 11 headers of 64 bytes (704 bytes) are inside the figure of 236,357,184 bytes in use. The largest buffers (stage C at `m = 976562`) are the twiddle table (`2^18` elements, 8,388,608 bytes), `Y` (`3 * 2^20` elements, 100,663,296), `tmp` (`2^20` elements, 33,554,432), `MU` (31,249,952), `g` (31,250,016) and the result `F` (31,249,984). Peaks of bytes in use per stage (maximum over the trials): init (twiddle table) 8,388,672; line setup 8,388,672; A 39,638,784; B 89,970,496; C 236,356,736; D 236,357,184; E 8,388,864; F 8,388,672; G 8,388,672; H 8,388,672; I 8,388,672.
(c) A stack bound of 65,536 bytes: the complete run was executed under `ulimit -s 64`.
Total: the larger of (a) + (c) = `290,356,404` bytes (the heap is inside (a)) and the measured peak of the run, `275,972,096` bytes (below): `290,356,404` bytes `= 2^28.114` (rounded up at three decimals); the measured peak is below the counted sum, so the claim takes the sum. The memory penalty is `max(0, 28.114 - 20) = 8.114`.
The pages the kernel itself maps for a process outside its executable image (the vdso and vvar mappings, page tables) and the kernel's buffer for the one `write` are the kernel's memory and lie outside the program's memory figure. Measured peak: the counted run was executed under memmeter (a helper that forks the program, reads its `wait4` maximum resident set and samples `VmHWM` and the summed `VmRSS` of the process tree every 10 ms); its peak was 275,972,096 bytes.
The program has no stored advice and no precomputed data beyond what it computes itself (the twiddle table is built at run time and charged in stage "init").

## 8. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the executed algorithm and its charges (4, 6, 7), the complete C source of the instrumented program (section 9), one machine-checked collision certificate (`certificates/`, checked by the organizer's hash).
* No Python experiment is declared: the experiment runner sizes the digest from the digest of the empty message, which the Orchard digest (exactly two 32-byte field encodings) does not define.
* The package contains only the certificate, so the C source is part of this document (section 9) as text, and the program reads no input file. The counts of section 6 are the output of that source compiled with `gcc -O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c` and run as `single 1`.
* The cost is the executed count of one run of the fixed procedure from its first centre, every trial charged. It says nothing about how many trials another sequence of centres would need.
* The cost claim assumes the model of section 4.2; in particular word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it. The organizer did not run the program, so the counts rest on the shipped source.
* Reproduction on one core: (a) the collision certificate against the organizer's hash, seconds; (b) the ledger recomputation of section 6.1, seconds; (c) `gcc -O3 -march=native -static -nostdlib -fno-stack-protector -U_FORTIFY_SOURCE -D_FORTIFY_SOURCE=0 -fno-pie -no-pie -ffunction-sections -fdata-sections -Wl,--gc-sections -o single single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c nolibc.c` (the source of section 9) and `single 1` under `ulimit -s 64`, which reproduces every count of section 6 and prints the collision (about 5810 s).

## 9. Complete source of the instrumented program

Counters: `LD(n)`, `ST(n)` add `n` to the load or store counter and `n` to the control counter (address operations), `CTL(n)` adds `n` to the control counter, `loopc(n)` adds `3n + 2` to the control counter; every `fp_*` call increments the counter of its own kind
(`fp_add`, `fp_sub`, `fp_mul`, `fp_sqr`; `fp_neg` is one subtraction); `X.perm += k` adds `k` primitive operations; `snap()` reads all counters; `snap_restore()` restores them where a block is charged by a stated unit instead of its expansion (the line evaluations of stage B, charged `X.perm += 279` each). Buffers are obtained from the tracked allocator (`NEW_FP`).
The files are shown in full, in the order: `outbuf.h`, `nolibc.c`, `common.h`, `common.c`, `pallas.h`, `pallas.c`, `pallas_consts.h`, `attack.h`, `hgcd.h`, `ntt.c`, `gen_kern.py`, `ntt_kern.h`, `ntt_a3.h`, `poly.c`, `lean.c`, `line.c`, `split.c`, `hgcd.c`, `single.c`.
`pallas_consts.h` holds the deployed Orchard constants (round constants, MDS, field constants) as Montgomery limbs. The root isolation of `split.c` for `deg G >= 2` is not executed by this run (the run has `deg G = 1`).

### outbuf.h

```c
#ifndef OUTBUF_H
#define OUTBUF_H
#include <stddef.h>
#define OUTCAP 8192              /* capacity of the output buffer: the whole report is appended to it and written by one write */
void out_flush(void);
extern size_t out_len;
#endif
```

### nolibc.c

```c
/* Minimal runtime for the statically linked, libc-free executable (no C library is linked): the process entry, the Linux system calls the program uses
 * (write once, exit_group once), memcpy / memset / memmove / strcmp, and a small printf that appends the report to one output buffer.  The printf has no
 * integer division, no modulo and no floating point: a decimal number is formed by comparing with the powers of ten and subtracting them, a hexadecimal one by
 * shifts and masks.
 * There is no mmap, munmap or clock system call: memory is one static arena (common.c) and the program reads no clock.
 * What executes here is charged in single.c, stage I (process entry, the formatting of the whole output buffer, the single write, exit_group). */
#include <stdint.h>
#include <stddef.h>
#include <stdarg.h>
#include <stdio.h>
#include "outbuf.h"

static inline long sys3(long n, long a, long b, long c) { long r; __asm__ volatile("syscall" : "=a"(r) : "0"(n), "D"(a), "S"(b), "d"(c) : "rcx", "r11", "memory"); return r; }
void exit(int code) { for (;;) sys3(231, code, 0, 0); }
static void wr(int fd, const char *s, size_t n) { while (n) { long r = sys3(1, fd, (long)s, (long)n); if (r <= 0) return; s += r; n -= (size_t)r; } }

void *memcpy(void *d, const void *s, size_t n) { void *r = d; __asm__ volatile("rep movsb" : "+D"(d), "+S"(s), "+c"(n) : : "memory"); return r; }
void *memset(void *d, int c, size_t n) { void *r = d; __asm__ volatile("rep stosb" : "+D"(d), "+c"(n) : "a"(c) : "memory"); return r; }
void *memmove(void *d, const void *s, size_t n) {
    if ((uintptr_t)d <= (uintptr_t)s || (uintptr_t)d >= (uintptr_t)s + n) return memcpy(d, s, n);
    unsigned char *dd = d; const unsigned char *ss = s; while (n--) dd[n] = ss[n]; return d;
}
int strcmp(const char *a, const char *b) { while (*a && *a == *b) { a++; b++; } return (unsigned char)*a - (unsigned char)*b; }
size_t strlen(const char *s) { size_t n = 0; while (s[n]) n++; return n; }

/* printf: %d %i %u %x %s %c %% with flags '-' and '0', width, precision for %s, length l ll z (no %f) */
static const uint64_t P10[20] = { 1ULL, 10ULL, 100ULL, 1000ULL, 10000ULL, 100000ULL, 1000000ULL, 10000000ULL, 100000000ULL, 1000000000ULL, 10000000000ULL, 100000000000ULL,
    1000000000000ULL, 10000000000000ULL, 100000000000000ULL, 1000000000000000ULL, 10000000000000000ULL, 100000000000000000ULL, 1000000000000000000ULL, 10000000000000000000ULL };
static int vfmt(char *o, size_t cap, const char *f, va_list ap) {
    size_t n = 0;
#define PUT(ch) do { if (n < cap) o[n] = (ch); n++; } while (0)
    for (; *f; f++) {
        if (*f != '%') { PUT(*f); continue; }
        f++;
        int left = 0, zero = 0, w = 0, prec = -1, lng = 0;
        for (;; f++) { if (*f == '-') left = 1; else if (*f == '0') zero = 1; else break; }
        while (*f >= '0' && *f <= '9') w = (w << 3) + (w << 1) + (*f++ - '0');
        if (*f == '.') { f++; prec = 0; while (*f >= '0' && *f <= '9') prec = (prec << 3) + (prec << 1) + (*f++ - '0'); }
        while (*f == 'l' || *f == 'z') { lng = 1; f++; }
        char tmp[80]; int tl = 0; const char *src = tmp; char c = *f;
        if (c == '%') { PUT('%'); continue; }
        if (c == 'c') { tmp[tl++] = (char)va_arg(ap, int); }
        else if (c == 's') { src = va_arg(ap, const char *); if (!src) src = "(null)"; while (src[tl] && (prec < 0 || tl < prec)) tl++; }
        else if (c == 'd' || c == 'i' || c == 'u' || c == 'x') {
            uint64_t v; int neg = 0;
            if (c == 'd' || c == 'i') { int64_t sv = lng ? va_arg(ap, long) : va_arg(ap, int); if (sv < 0) { neg = 1; v = (uint64_t)0 - (uint64_t)sv; } else v = (uint64_t)sv; }
            else v = lng ? va_arg(ap, unsigned long) : va_arg(ap, unsigned);
            if (neg) tmp[tl++] = '-';
            if (c == 'x') { int k = 15; while (k > 0 && !((v >> (k << 2)) & 15)) k--; for (; k >= 0; k--) tmp[tl++] = "0123456789abcdef"[(v >> (k << 2)) & 15]; }
            else { int k = 19; while (k > 0 && v < P10[k]) k--; for (; k >= 0; k--) { char dg = 0; while (v >= P10[k]) { v -= P10[k]; dg++; } tmp[tl++] = (char)('0' + dg); } }
        } else { PUT('%'); PUT(c); continue; }
        int pad = w > tl ? w - tl : 0;
        if (!left) { char pc = (zero && c != 's') ? '0' : ' '; if (pc == '0' && tl && src[0] == '-') { PUT('-'); src++; tl--; } for (int i = 0; i < pad; i++) PUT(pc); }
        for (int i = 0; i < tl; i++) PUT(src[i]);
        if (left) for (int i = 0; i < pad; i++) PUT(' ');
    }
    return (int)n;
}
int vsnprintf(char *o, size_t cap, const char *f, va_list ap) { int n = vfmt(o, cap ? cap - 1 : 0, f, ap); if (cap) o[(size_t)n < cap - 1 ? (size_t)n : cap - 1] = 0; return n; }
int snprintf(char *o, size_t cap, const char *f, ...) { va_list ap; va_start(ap, f); int n = vsnprintf(o, cap, f, ap); va_end(ap); return n; }
/* The report is appended to one static buffer of OUTCAP bytes; nothing is written until out_flush, which makes the single write system call. */
static char outbuf[OUTCAP]; size_t out_len = 0;
static void out_put(int fd, const char *p, size_t n) {
    if (fd != 1) { wr(fd, p, n); return; }                /* stderr: error paths only, never executed in the recorded run */
    for (size_t k = 0; k < n; k++) { if (out_len < OUTCAP) outbuf[out_len] = p[k]; out_len++; }
}
static int vout(int fd, const char *f, va_list ap) {
    if (fd != 1) { char b[1024]; int n = vfmt(b, sizeof b, f, ap); if (n > (int)sizeof b) n = (int)sizeof b; wr(fd, b, (size_t)n); return n; }
    int n = vfmt(outbuf + (out_len < OUTCAP ? out_len : OUTCAP), out_len < OUTCAP ? OUTCAP - out_len : 0, f, ap); out_len += (size_t)n; return n;
}
void out_flush(void) { wr(1, outbuf, out_len < OUTCAP ? out_len : OUTCAP); }
FILE *stdout = (FILE *)1, *stderr = (FILE *)2;
int printf(const char *f, ...) { va_list ap; va_start(ap, f); int n = vout(1, f, ap); va_end(ap); return n; }
int fprintf(FILE *fp, const char *f, ...) { va_list ap; va_start(ap, f); int n = vout((int)(intptr_t)fp, f, ap); va_end(ap); return n; }
int puts(const char *s) { out_put(1, s, strlen(s)); out_put(1, "\n", 1); return 0; }
int putchar(int c) { char ch = (char)c; out_put(1, &ch, 1); return c; }
int fputc(int c, FILE *fp) { char ch = (char)c; out_put((int)(intptr_t)fp, &ch, 1); return c; }
int putc(int c, FILE *fp) { return fputc(c, fp); }
int fputs(const char *s, FILE *fp) { out_put((int)(intptr_t)fp, s, strlen(s)); return 0; }
size_t fwrite(const void *p, size_t sz, size_t n, FILE *fp) { for (size_t i = 0; i < n; i++, p = (const char *)p + sz) out_put((int)(intptr_t)fp, (const char *)p, sz); return n; }   /* gcc turns fprintf(stderr, "text") into fwrite; error paths only; no multiplication */
int fflush(FILE *fp) { (void)fp; return 0; }

int main(int, char **);
void c_start(long *sp) { int argc = (int)sp[0]; exit(main(argc, (char **)(sp + 1))); }
__asm__(".globl _start\n_start:\n xor %ebp,%ebp\n mov %rsp,%rdi\n and $-16,%rsp\n call c_start\n");
```

### common.h

```c
/* Shared definitions for the Orchard odd-part root finder.  All field arithmetic goes through pallas.c
 * (counted: add, sub, mul, sqr).  Additional charged primitives are counted here: 256-bit loads (ld), stores (st),
 * loop-control / index operations (ctl) and random words (rnd).  The charging rules are in proof.md section 4.2. */
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
extern size_t mem_cur, mem_peak;        /* mem_peak: peak allocator footprint (see common.c) */
extern size_t mem_live, mem_peak_live, mem_peak_pay;   /* live allocations now; live allocations and live payload bytes at the footprint peak */
void  mem_reset_peak(void);

/* ---- field helpers */
#ifndef ARENA
#define ARENA 290000000            /* bytes of the static arena (multiple of 64), set per build: see the definition used for this run */
#endif
extern size_t mem_used, arena_hwm;
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
typedef struct { int nh, ns; const fp *H[2]; size_t lH[2]; const fp *S[2]; size_t lS[2]; signed char o[2][2]; signed char sg[2][2]; } bilin_grp_t;
void   conv_bilin_otf(const plan_t *P, int nout, fp *const *out, const size_t *outlen, int ng, const bilin_grp_t *G, fp *tH0, fp *tH1, fp *tS, int *eps);   /* shared-transform sums of products, row by row (rows==3 plans) */
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

/* Allocation from ONE static arena in .bss (no mmap, no munmap, no other system call).  The arena is ARENA bytes (a multiple of 64, set in common.h; it is part of the
 * executable image, so the memory figure is the whole image from `size`; the run reports the highest end address of any block, `extent`).  It is a sequence
 * of blocks laid end to end; every block starts with a 64-byte header { size = the block's bytes including the header, prev = size of the block before it
 * (0 for the first), used = 0 or 1 } and the payload follows (64-byte aligned; the block size is 64 + the payload rounded up to a multiple of 64).
 * xalloc: a large block (more than SMALL_BLOCK bytes, header included) takes the first fit in address order and is cut from the bottom of that free block; a small block takes the last fit and is cut from the top of that free block (this keeps the large buffers together and leaves less unusable space between them than plain first fit); a block is split when the remainder is at least 128 bytes.  xfree: the block is marked free and merged with a free
 * neighbour on either side.  Every executed operation of both functions is charged where it is written, with the rule of common.h: ldz / stz = one load /
 * store plus one address operation; CTL(2) = one comparison plus its branch; CTL(1) = one add / sub / and / assignment of a register.  The statistics lines
 * (bytes in use, live blocks, peaks, extent) are charged a flat ALLOC_STATS = 64 per call (they are at most 6 loads, 6 stores, 8 adds and 4 compare-branch
 * pairs = 6*2 + 6*2 + 8 + 8 = 40 operations).  The first call also writes the header of the single initial free block (charged). */
size_t mem_live = 0, mem_peak_live = 0, mem_peak_pay = 0, mem_used = 0, arena_hwm = 0;
typedef struct { size_t size, prev, used; char pad[40]; } bhdr_t;
static char arena[ARENA] __attribute__((aligned(64)));
static int arena_ready = 0;
#define ALLOC_STATS 64
#define SMALL_BLOCK 196608          /* blocks of at most this many bytes (header included) are placed from the top of the free space, larger ones from the bottom */
static inline size_t ldz(const size_t *p) { X.ld++; X.ctl++; return *p; }
static inline void stz(size_t *p, size_t v) { X.st++; X.ctl++; *p = v; }
void *xalloc(size_t bytes) {
    CTL(2); if (!arena_ready) { bhdr_t *h0 = (bhdr_t *)arena; stz(&h0->size, ARENA); stz(&h0->prev, 0); stz(&h0->used, 0); arena_ready = 1; X.st++; X.ctl++; }
    size_t need = 64 + ((bytes + 63) & ~(size_t)63); CTL(4);
    int small = need <= SMALL_BLOCK; CTL(2);         /* comparison with the small-block limit, assignment */
    char *p = arena, *cand = NULL; size_t csz = 0; CTL(3);
    for (;;) {                                        /* walk the blocks in address order */
        CTL(2); if (p >= arena + ARENA) break;
        bhdr_t *h = (bhdr_t *)p;
        size_t b = ldz(&h->size), u = ldz(&h->used);
        CTL(4); if (!u && b >= need) { cand = p; csz = b; CTL(2); if (!small) break; }   /* fits: remember it; a large block takes the first fit, a small block the last */
        p += b; CTL(3);                               /* advance, loop back */
    }
    CTL(2); if (!cand) {
        fprintf(stderr, "out of memory (%zu)\n", bytes); exit(2); }
    p = cand; size_t sz = csz;
    bhdr_t *h = (bhdr_t *)p;
    size_t rem = sz - need; CTL(3);                   /* subtraction, comparison, branch */
    if (rem >= 128) {
        char *nn = p + sz; CTL(3);                    /* end of the block, comparison with the arena end, branch */
        if (small) {                                  /* small block: carved from the TOP of the free block; the free part keeps the header h */
            bhdr_t *n = (bhdr_t *)(p + rem); CTL(1);
            stz(&h->size, rem);
            stz(&n->size, need); stz(&n->prev, rem); stz(&n->used, 0);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, need);
            p = (char *)n; h = n; sz = need;
        } else {                                      /* large block: carved from the BOTTOM of the free block */
            bhdr_t *n = (bhdr_t *)(p + need); CTL(1);
            stz(&n->size, rem); stz(&n->prev, need); stz(&n->used, 0);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, rem);
            stz(&h->size, need); sz = need;
        }
    }
    stz(&h->used, 1);
    mem_cur += sz - 64; mem_live++; mem_used += sz;
    size_t ext = (size_t)(p - arena) + sz;
    if (ext > arena_hwm) arena_hwm = ext;
    if (mem_used > mem_peak) { mem_peak = mem_used; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
    CTL(ALLOC_STATS);
    return p + 64;
}
void xfree(void *q) {
    CTL(2); if (!q) return;
    char *p = (char *)q - 64; CTL(1);
    bhdr_t *h = (bhdr_t *)p;
    size_t sz = ldz(&h->size), prev = ldz(&h->prev);
    stz(&h->used, 0);
    mem_cur -= sz - 64; mem_live--; mem_used -= sz;   /* (payload bytes are tracked by block: informational) */
    CTL(ALLOC_STATS);
    char *n = p + sz; CTL(3);
    if (n < arena + ARENA) {
        bhdr_t *nh = (bhdr_t *)n;
        size_t nu = ldz(&nh->used); CTL(2);
        if (!nu) {
            sz += ldz(&nh->size); CTL(1); stz(&h->size, sz);
            char *nn = p + sz; CTL(3);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, sz);
        }
    }
    CTL(2);
    if (prev) {
        bhdr_t *ph = (bhdr_t *)(p - prev); CTL(1);
        size_t pu = ldz(&ph->used); CTL(2);
        if (!pu) {
            size_t psz = prev + sz; CTL(1); stz(&ph->size, psz);
            char *nn = (char *)ph + psz; CTL(3);
            if (nn < arena + ARENA) stz(&((bhdr_t *)nn)->prev, psz);
        }
    }
}
void mem_reset_peak(void) { mem_peak = mem_used; mem_peak_live = mem_live; mem_peak_pay = mem_cur; }
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

/* ---- conversions between canonical integers and the Montgomery representation: each conversion is one Montgomery multiplication and is counted as one field multiplication (fp_cnt.mul) */
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

/* ---- register helpers: they compare or set the four limbs of a value held in registers and increment no field counter; the caller charges the comparison, branch or store where it executes it (CTL / ST, see proof.md section 4.2) */
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

/* ---------- raw limb helpers (every counted operation below increments its counter, then calls these) ---------- */
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
void build_g(fp *g, const line_t *L, const fp *c, int r);

/* map a pair of roots back to inputs: W -> (nk, rho) */
void map_back(fp *nk, fp *rho, const line_t *L, const fp *W);

/* gcd and root finding */
size_t euclid_gcd(fp *out, const fp *a, size_t da, const fp *b, size_t db, size_t *dout); /* classical; out receives gcd (monic) */
int  find_root(fp *root, const fp *G, size_t d);           /* G monic, product of distinct linear factors; returns 1 on success */

/* minor-stage memory charge: 2 loads + 1 store + 1 control op per primitive executed since s0 */
void bound_mem_since(snap_t s0);

/* split.c: root isolation (charged as executed) */
size_t gcd_cl(fp *out, const fp *a, size_t da, const fp *b, size_t db);       /* classical Euclid; monic gcd; returns degree */
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

### ntt.c

```c
/* NTT engine: radix-2 DIF/DIT rows (register-blocked passes of up to 4 layers = 16 data words in registers, plus 2 working words) with an optional
 * twiddle-free Good-Thomas radix-3 stage (N = 3 * 2^a).  p-1 = 2^32 * 3 * q2, so both exist natively.
 * Layout (verified in pfa_check.py): row (k mod 3), bit-reversed position of (k mod n) holds f(theta^k). */
#include "common.h"
#include "pallas_consts.h"

static fp *tw = NULL;          /* half table: tw[m] = rho_max^(2m), m < nmax/4 (the odd powers are recomputed: rho_max^(2m+1) = tw[m] * RHO) */
static fp RHO;                  /* rho_max (one stored word) */
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
/* r = a / 3 for a multiple of 3, by long division over the 256 bits (no division instruction): rem = 2 rem + bit; if rem >= 3 then rem -= 3 and set the quotient bit */
static void limbs_div3(uint64_t r[4], const uint64_t a[4]) {
    uint64_t rem = 0, taken = 0;
    for (int i = 0; i < 4; i++) r[i] = 0;
    for (int i = 255; i >= 0; i--) {
        rem = (rem << 1) | ((a[i >> 6] >> (i & 63)) & 1);
        if (rem >= 3) { rem -= 3; r[i >> 6] |= (uint64_t)1 << (i & 63); taken++; }
    }
    CTL(4 * 4 + 2 + 12 * 256 + 2 + 7 * taken);         /* clearing loop; per bit: loop 3, i>>6, load, i&63, shift, and, rem<<1, or, compare + branch (2) = 12; per set bit: subtract, i>>6, i&63, shift, load, or, store = 7 */
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
    CTL(400);               /* limbs_sub1, limbs_shr: at most 4 iterations of at most 20 operations each per call, two calls (limbs_div3 charges itself) */
    CTL(2 + 8);             /* the test ntt_w3 == 1 (four limb comparisons: 8 operations; compare, branch) */
    fp one; fp_set_one(&one);
    if (fp_eq(&ntt_w3, &one)) { fprintf(stderr, "5 is a cube?\n"); exit(3); }
    fp_set_zero(&ZERO);
    tw = NEW_FP(nmax_g / 4);
    RHO = rho; ST(1);
    fp rho2; fp_sqr(&rho2, &rho);
    tw[0] = one; ST(1);
    for (size_t j = 1; j < nmax_g / 4; j++) { fp_mul(&tw[j], &tw[j - 1], &rho2); LD(1); ST(1); }
    loopc(nmax_g / 4);
    CTL(5 * INV_CTL);       /* control of the bit loops of fp_pow (x2) and fp_inv (x1): at most INV_CTL each; the other setup is a few dozen straight-line operations */
    W3[0] = one; W3[1] = ntt_w3; fp_sqr(&W3[2], &ntt_w3);
    fp two, half; fp_from_u64(&two, 2); fp_inv(&half, &two);
    fp s; fp_add(&s, &W3[1], &W3[2]); fp_mul(&CH, &s, &half);          /* (w+w^2)/2 = -1/2 */
    fp d; fp_sub(&d, &W3[1], &W3[2]); fp_mul(&DL, &d, &half);
}
void ntt_free(void) { if (tw) xfree(tw); tw = NULL; }
size_t ntt_table_bytes(void) { return (nmax_g / 4) * sizeof(fp) + sizeof(fp); }

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
    fp rho; CTL(3);                              /* test of shift, index shift */
    if (P->shift == 0) { rho = RHO; } else { rho = tw[(size_t)1 << (P->shift - 1)]; }
    LD(1);
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

/* ---------- shared-transform bilinear sums (rows==3 plans only) ----------
 * out_k = eps_k * (sum of signed products of operand spectra), computed row by row of the Good-Thomas layout.  A group has nh held operands
 * (transformed once per row into tH[h]) and ns streamed operands (each transformed once per row into tS and multiplied with the held ones);
 * the product of streamed s and held h is accumulated into output o[s][h] (-1: no product) with sign sg[s][h].  The first product of an output
 * is assigned, its sign is returned as eps_k (0: output has no product); the caller applies eps_k with the 1/N scale.  Every operand
 * spectrum is formed once per row, every output row is inverse transformed once. */
void conv_bilin_otf(const plan_t *P, int nout, fp *const *out, const size_t *outlen, int ng, const bilin_grp_t *G, fp *tH0, fp *tH1, fp *tS, int *eps) {
    CTL(2);
    if (P->rows != 3) { fprintf(stderr, "conv_bilin_otf needs a rows==3 plan\n"); exit(9); }
    size_t n = P->n;
    fp *tH[2] = { tH0, tH1 };
    for (int k = 0; k < nout; k++) eps[k] = 0;
    CTL(2 + 3 * nout);
    for (int g = 0; g < ng; g++) for (int s = 0; s < G[g].ns; s++) for (int h = 0; h < G[g].nh; h++) {
        int o = G[g].o[s][h]; CTL(6);
        if (o >= 0 && !eps[o]) eps[o] = G[g].sg[s][h];
    }
    for (int r = 0; r < 3; r++) {
        int done[4] = { 0, 0, 0, 0 }; CTL(2 + 2 + nout);
        for (int g = 0; g < ng; g++) {
            const bilin_grp_t *gp = &G[g]; int l0; CTL(3 + 4);
            for (int h = 0; h < gp->nh; h++) {
                l0 = 0; CTL(3 + 3);
                stageA_row(P, tH[h], r, gp->H[h], gp->lH[h], 0);
                for (int p = 0; p < P->npass; p++) { pass_fwd(tH[h], P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
            }
            for (int s = 0; s < gp->ns; s++) {
                l0 = 0; CTL(3 + 3);
                stageA_row(P, tS, r, gp->S[s], gp->lS[s], 0);
                for (int p = 0; p < P->npass; p++) { pass_fwd(tS, P, l0, P->kk[p]); l0 += P->kk[p]; CTL(4); }
                for (int h = 0; h < gp->nh; h++) {
                    int o = gp->o[s][h]; CTL(3 + 5);                /* loop, o test, done[] test, sign test */
                    if (o < 0) continue;
                    fp *row = out[o] + (size_t)r * n; const fp *hh = tH[h];
                    if (!done[o]) { done[o] = 1; FOR8(i, n, fp_mul(&row[i], &tS[i], &hh[i]); LD(2); ST(1)); }
                    else if (gp->sg[s][h] == eps[o]) { FOR8(i, n, fp x; fp_mul(&x, &tS[i], &hh[i]); fp_add(&row[i], &row[i], &x); LD(3); ST(1)); }
                    else { FOR8(i, n, fp x; fp_mul(&x, &tS[i], &hh[i]); fp_sub(&row[i], &row[i], &x); LD(3); ST(1)); }
                }
            }
        }
        for (int k = 0; k < nout; k++) {
            CTL(3);
            if (!eps[k]) continue;
            fp *row = out[k] + (size_t)r * n; int l0 = P->a;
            for (int p = P->npass - 1; p >= 0; p--) { l0 -= P->kk[p]; pass_inv(row, P, l0, P->kk[p]); CTL(4); }
        }
        CTL(2);
    }
    for (int k = 0; k < nout; k++) { CTL(3); if (eps[k]) stageA_inv(P, out[k], outlen[k]); }
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
       '#define IBN(u, v) do { fp tt_ = (v); fp_sub(&(v), &(u), &tt_); fp_add(&(u), &(u), &tt_); } while (0)',
       '/* half twiddle table: tw[m] = rho^(2m) is stored; the virtual twiddle rho^v is tw[v/2] for even v and tw[(v-1)/2] * rho for odd v.  The',
       '   caller charges the one load of the fetched table word; the odd branch also loads rho (LD) and multiplies (fp_mul, counted in pallas.c).  Every',
       '   call charges the parity test (and, branch) and the index shift: 3. Layers j >= 1 of a pass have even virtual indices (shift l0+j+sh >= 1). */',
       'static inline const fp *twget(const fp *tw, size_t v, fp *wt) {',
       '    CTL(3);',
       '    if (v & 1) { *wt = tw[v >> 1]; LD(1); fp_mul(wt, wt, &RHO); return wt; }',
       '    return &tw[v >> 1];',
       '}']


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
                        if j == 0:
                            out.append('    size_t v0 = 0; fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1; v0 = virtual index */')
                        else:
                            out.append('    const fp *w%d = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */' % j)
                else:
                    if j == 0:
                        out.append('    size_t v0 = b << sjs[0]; CTL(1); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);')
                    else:
                        out.append('    const fp *w%d = tw + (b << (sjs[%d] - 1)); LD(1); CTL(3);' % (j, j))
                    for t in ts:
                        out.append('    BF(x[%d], x[%d], w%d);' % (t, t + half, j))
            else:
                if j == 0:
                    out.append('    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);')
                else:
                    out.append('    w%d += D[%d] >> 1; LD(1); CTL(2);' % (j, j))
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
                            if j == 0:
                                out.append('    size_t v0 = nh << sh; CTL(1); fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1 */')
                            else:
                                out.append('    const fp *w%d = tw + ((nh << sh) >> 1); CTL(2); /* b == 0: the twiddle at tp == 0 is 1 */' % j)
                    else:
                        if j == 0:
                            out.append('    size_t v0 = (nh - (b << sj[0])) << sh; CTL(3); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);')
                        else:
                            out.append('    const fp *w%d = tw + (((nh - (b << sj[%d])) << sh) >> 1); LD(1); CTL(5);' % (j, j))
                        for t in ts:
                            out.append('    IB(x[%d], x[%d], w%d);' % (t, t + half, j))
                else:
                    if j == 0:
                        out.append('    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);')
                    else:
                        out.append('    w%d -= D[%d] >> 1; LD(1); CTL(2);' % (j, j))
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
/* half twiddle table: tw[m] = rho^(2m) is stored; the virtual twiddle rho^v is tw[v/2] for even v and tw[(v-1)/2] * rho for odd v.  The
   caller charges the one load of the fetched table word; the odd branch also loads rho (LD) and multiplies (fp_mul, counted in pallas.c).  Every
   call charges the parity test (and, branch) and the index shift: 3. Layers j >= 1 of a pass have even virtual indices (shift l0+j+sh >= 1). */
static inline const fp *twget(const fp *tw, size_t v, fp *wt) {
    CTL(3);
    if (v & 1) { *wt = tw[v >> 1]; LD(1); fp_mul(wt, wt, &RHO); return wt; }
    return &tw[v >> 1];
}
static inline void kf1(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    size_t v0 = b << sjs[0]; CTL(1); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[0], x[1], w0);
}
static inline void kf1z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[1]);
}
static inline void ki1(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    size_t v0 = (nh - (b << sj[0])) << sh; CTL(3); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[0], x[1], w0);
}
static inline void ki1z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
}
static inline void kf2(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    size_t v0 = b << sjs[0]; CTL(1); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[0], x[2], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[1], x[3], w0);
    const fp *w1 = tw + (b << (sjs[1] - 1)); LD(1); CTL(3);
    BF(x[0], x[1], w1);
    BF(x[2], x[3], w1);
}
static inline void kf2z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[2]);
    size_t v0 = 0; fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1; v0 = virtual index */
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[1], x[3], w0);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
}
static inline void ki2(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w1 = tw + (((nh - (b << sj[1])) << sh) >> 1); LD(1); CTL(5);
    IB(x[0], x[1], w1);
    IB(x[2], x[3], w1);
    size_t v0 = (nh - (b << sj[0])) << sh; CTL(3); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[0], x[2], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[1], x[3], w0);
}
static inline void ki2z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
    IBN(x[2], x[3]);
    IBN(x[0], x[2]);
    size_t v0 = nh << sh; CTL(1); fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1 */
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[1], x[3], w0);
}
static inline void kf3(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    size_t v0 = b << sjs[0]; CTL(1); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[0], x[4], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[1], x[5], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[2], x[6], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[3], x[7], w0);
    const fp *w1 = tw + (b << (sjs[1] - 1)); LD(1); CTL(3);
    BF(x[0], x[2], w1);
    BF(x[4], x[6], w1);
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[1], x[3], w1);
    BF(x[5], x[7], w1);
    const fp *w2 = tw + (b << (sjs[2] - 1)); LD(1); CTL(3);
    BF(x[0], x[1], w2);
    BF(x[2], x[3], w2);
    BF(x[4], x[5], w2);
    BF(x[6], x[7], w2);
}
static inline void kf3z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    BFN(x[0], x[4]);
    size_t v0 = 0; fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1; v0 = virtual index */
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[1], x[5], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[2], x[6], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[3], x[7], w0);
    BFN(x[0], x[2]);
    BFN(x[4], x[6]);
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[1], x[3], w1);
    BF(x[5], x[7], w1);
    BFN(x[0], x[1]);
    BFN(x[2], x[3]);
    BFN(x[4], x[5]);
    BFN(x[6], x[7]);
}
static inline void ki3(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    const fp *w2 = tw + (((nh - (b << sj[2])) << sh) >> 1); LD(1); CTL(5);
    IB(x[0], x[1], w2);
    IB(x[2], x[3], w2);
    IB(x[4], x[5], w2);
    IB(x[6], x[7], w2);
    const fp *w1 = tw + (((nh - (b << sj[1])) << sh) >> 1); LD(1); CTL(5);
    IB(x[0], x[2], w1);
    IB(x[4], x[6], w1);
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[1], x[3], w1);
    IB(x[5], x[7], w1);
    size_t v0 = (nh - (b << sj[0])) << sh; CTL(3); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[0], x[4], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[1], x[5], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[2], x[6], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[3], x[7], w0);
}
static inline void ki3z(fp *x, const fp *tw, size_t b, const size_t *D, const int *sj, int sh, size_t nh) {
    IBN(x[0], x[1]);
    IBN(x[2], x[3]);
    IBN(x[4], x[5]);
    IBN(x[6], x[7]);
    IBN(x[0], x[2]);
    IBN(x[4], x[6]);
    const fp *w1 = tw + ((nh << sh) >> 1); CTL(2); /* b == 0: the twiddle at tp == 0 is 1 */
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[1], x[3], w1);
    IB(x[5], x[7], w1);
    IBN(x[0], x[4]);
    size_t v0 = nh << sh; CTL(1); fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1 */
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[1], x[5], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[2], x[6], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[3], x[7], w0);
}
static inline void kf4(fp *x, const fp *tw, size_t b, const size_t *D, const int *sjs) {
    size_t v0 = b << sjs[0]; CTL(1); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[0], x[8], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[1], x[9], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[2], x[10], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[3], x[11], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[4], x[12], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[5], x[13], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[6], x[14], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[7], x[15], w0);
    const fp *w1 = tw + (b << (sjs[1] - 1)); LD(1); CTL(3);
    BF(x[0], x[4], w1);
    BF(x[8], x[12], w1);
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[1], x[5], w1);
    BF(x[9], x[13], w1);
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[2], x[6], w1);
    BF(x[10], x[14], w1);
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[3], x[7], w1);
    BF(x[11], x[15], w1);
    const fp *w2 = tw + (b << (sjs[2] - 1)); LD(1); CTL(3);
    BF(x[0], x[2], w2);
    BF(x[4], x[6], w2);
    BF(x[8], x[10], w2);
    BF(x[12], x[14], w2);
    w2 += D[2] >> 1; LD(1); CTL(2);
    BF(x[1], x[3], w2);
    BF(x[5], x[7], w2);
    BF(x[9], x[11], w2);
    BF(x[13], x[15], w2);
    const fp *w3 = tw + (b << (sjs[3] - 1)); LD(1); CTL(3);
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
    size_t v0 = 0; fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1; v0 = virtual index */
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[1], x[9], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[2], x[10], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[3], x[11], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[4], x[12], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[5], x[13], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[6], x[14], w0);
    v0 += D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    BF(x[7], x[15], w0);
    BFN(x[0], x[4]);
    BFN(x[8], x[12]);
    const fp *w1 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[1], x[5], w1);
    BF(x[9], x[13], w1);
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[2], x[6], w1);
    BF(x[10], x[14], w1);
    w1 += D[1] >> 1; LD(1); CTL(2);
    BF(x[3], x[7], w1);
    BF(x[11], x[15], w1);
    BFN(x[0], x[2]);
    BFN(x[4], x[6]);
    BFN(x[8], x[10]);
    BFN(x[12], x[14]);
    const fp *w2 = tw; /* b == 0: the twiddle at tp == 0 is 1; the pointer is the base register */
    w2 += D[2] >> 1; LD(1); CTL(2);
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
    const fp *w3 = tw + (((nh - (b << sj[3])) << sh) >> 1); LD(1); CTL(5);
    IB(x[0], x[1], w3);
    IB(x[2], x[3], w3);
    IB(x[4], x[5], w3);
    IB(x[6], x[7], w3);
    IB(x[8], x[9], w3);
    IB(x[10], x[11], w3);
    IB(x[12], x[13], w3);
    IB(x[14], x[15], w3);
    const fp *w2 = tw + (((nh - (b << sj[2])) << sh) >> 1); LD(1); CTL(5);
    IB(x[0], x[2], w2);
    IB(x[4], x[6], w2);
    IB(x[8], x[10], w2);
    IB(x[12], x[14], w2);
    w2 -= D[2] >> 1; LD(1); CTL(2);
    IB(x[1], x[3], w2);
    IB(x[5], x[7], w2);
    IB(x[9], x[11], w2);
    IB(x[13], x[15], w2);
    const fp *w1 = tw + (((nh - (b << sj[1])) << sh) >> 1); LD(1); CTL(5);
    IB(x[0], x[4], w1);
    IB(x[8], x[12], w1);
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[1], x[5], w1);
    IB(x[9], x[13], w1);
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[2], x[6], w1);
    IB(x[10], x[14], w1);
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[3], x[7], w1);
    IB(x[11], x[15], w1);
    size_t v0 = (nh - (b << sj[0])) << sh; CTL(3); fp wt0; const fp *w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[0], x[8], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[1], x[9], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[2], x[10], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[3], x[11], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[4], x[12], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[5], x[13], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[6], x[14], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
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
    const fp *w2 = tw + ((nh << sh) >> 1); CTL(2); /* b == 0: the twiddle at tp == 0 is 1 */
    w2 -= D[2] >> 1; LD(1); CTL(2);
    IB(x[1], x[3], w2);
    IB(x[5], x[7], w2);
    IB(x[9], x[11], w2);
    IB(x[13], x[15], w2);
    IBN(x[0], x[4]);
    IBN(x[8], x[12]);
    const fp *w1 = tw + ((nh << sh) >> 1); CTL(2); /* b == 0: the twiddle at tp == 0 is 1 */
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[1], x[5], w1);
    IB(x[9], x[13], w1);
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[2], x[6], w1);
    IB(x[10], x[14], w1);
    w1 -= D[1] >> 1; LD(1); CTL(2);
    IB(x[3], x[7], w1);
    IB(x[11], x[15], w1);
    IBN(x[0], x[8]);
    size_t v0 = nh << sh; CTL(1); fp wt0; const fp *w0; /* b == 0: the twiddle at tp == 0 is 1 */
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[1], x[9], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[2], x[10], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[3], x[11], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[4], x[12], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[5], x[13], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
    IB(x[6], x[14], w0);
    v0 -= D[0]; w0 = twget(tw, v0, &wt0); LD(1); CTL(1);
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

static int ebit(const uint64_t E[4], int i) { return (int)((E[i >> 6] >> (i & 63)) & 1); }   /* word index by a shift, bit index by a mask; charged 7 at each use: shift, mask, address, load, shift, and, return */

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
    CTL(4 + 8);                                  /* fp_eq: four limb comparisons (8 operations), compare, branch; setup */
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
    int top = 255; while (top > 0 && !ebit(E, top)) { top--; CTL(3 + 7 + 2); }      /* loop, ebit (7: shift, mask, address, load, shift, and, return), test */
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
        CTL(3 + 7 + 2 + 2);                  /* loop, ebit (7), if, steps++ and the quiet test */
        steps++;
        CTL(6);
        if (!quiet && (steps & 31) == 0) fprintf(stderr, "  lean step %d/%d\n", steps, bit);
    }
    { fp Nf; uint64_t vv[4] = { N, 0, 0, 0 }; fp_from_limbs(&Nf, vv);
      for (size_t i = 0; i < m; i++) fp_mul(&F[i], &Y[i], &Nf);
      LD(m); ST(m); loopc(m); }
    CTL(2);                                      /* test of quiet */
    if (quiet == 2) {
        snap_t n_ = snap_sub(sB, sA), l_ = snap_sub(snap(), sC), p_ = snap_sub(sC, sB);
        printf("lean-pow breakdown: newton total=%llu arith=%llu | prefix+scale total=%llu | loop steps=%d total=%llu arith=%llu",
               (unsigned long long)snap_total(n_), (unsigned long long)snap_arith(n_), (unsigned long long)snap_total(p_), steps,
               (unsigned long long)snap_total(l_), (unsigned long long)snap_arith(l_));
        putchar(10);
    }
    CTL(500);                                    /* the four snapshots of the counters (sA, sB, sC and the one in the report branch) and the report branch: bound 500 (4 x 9 loads, 3 subtractions of 9) */
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
    X.ctl += 4 * 11 + 1 + 2;                 /* four xorshift calls (11 each), the 254-bit mask (one AND), the call of fp_from_limbs with the address of v (2) */
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
void build_g(fp *g, const line_t *L, const fp *c, int r) {
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
    ntt_inv(&P, buf, m + 1);                 /* buf[k] = H * g_k */
    fp il;
    CTL(5); if (fp_is_zero(&buf[m])) { fprintf(stderr, "leading coefficient of g vanishes\n"); exit(7); }   /* four-limb zero test, branch: g must have degree exactly m */
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
/* Stage tools of the two-family attack: classical Euclid gcd, deflation by a known root,
 * Taylor shift, Z^((p-1)/2) mod G, and the isolation of one root of a monic product of distinct linear factors.
 * Every executed operation is charged as in common.h. */
#include "attack.h"
#include "pallas_consts.h"
#include "hgcd.h"

uint64_t SPL_shift, SPL_pow, SPL_gcd, SPL_div, SPL_misc, SPL_levels, SPL_tries;

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
                        SPL_gcd += snap_total(snap_sub(snap(), t0));
            CTL(4);
            if (a >= 1 && a <= d - 1) {
                size_t b = d - a;
                CTL(3);
                if (a <= b) { xfree(G); G = Ap; d = a; }
                else {
                    t0 = snap();
                    size_t dold = d; fp *q = NEW_FP(b + 1), *rem = NEW_FP(d + 1); size_t lq, lr;
                    divrem_any_pub(q, &lq, rem, &lr, G, d + 1, Ap, a + 1);
                    CTL(4);                                                  /* the test of the remainder and the quotient length */
                    if (lr != 0 || lq != b + 1) { fprintf(stderr, "split: division left a remainder\n"); exit(80); }
                    xfree(rem); xfree(Ap); xfree(G); G = q; d = b;
                    SPL_div += snap_total(snap_sub(snap(), t0));
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
#define BASEK 96
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
    CTL(3);                                                          /* the test of the quotient length */
    if (la == lb + 1 && lb >= 2) {
        /* quotient of two coefficients q0 + q1 X, remainder in one pass: r_k = a_k - q0 b_k - q1 b_(k-1); b_(k-1) is the previous b_k (register), no copy of a */
        fp inv; fp_inv(&inv, &b[lb - 1]); CTL(INV_CTL);
        fp q1, q0, t; fp_mul(&q1, &a[lb], &inv);
        fp_mul(&t, &q1, &b[lb - 2]); fp_sub(&t, &a[lb - 1], &t); fp_mul(&q0, &t, &inv);
        LD(3); q[0] = q0; q[1] = q1; ST(2); *lq = 2; CTL(6);
        fp prev; fp_set_zero(&prev);
        for (size_t k = 0; k + 1 < lb; k++) {
            fp bk = b[k], x, y;
            fp_mul(&x, &q0, &bk); fp_sub(&x, &a[k], &x);
            if (k) { fp_mul(&y, &q1, &prev); fp_sub(&x, &x, &y); }
            r[k] = x; prev = bk;
        }
        LD(2 * (lb - 1)); ST(lb - 1); loopc(lb - 1); CTL(4 + 2 * (lb - 1));      /* + the test `if (k)` of every iteration: compare, branch */
        *lr = trimlen(r, lb - 1);
        return;
    }
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
/* two-coefficient q (q0 + q1 X): o_k = e_k q0 + e_(k-1) q1 + f_k in one pass (e_(k-1) is the previous e_k, register) */
static size_t mul_add_q2(fp **res, const fp *e, size_t le, const fp *q, const fp *f, size_t lf) {
    size_t lt = le ? le + 1 : 0;
    size_t lo = lt > lf ? lt : lf;
    fp *o = NEW_FP(lo ? lo : 1);
    fp prev; fp_set_zero(&prev);
    for (size_t k = 0; k < lo; k++) {
        fp acc, t; int have = 0;
        if (k < le) { fp ek = e[k]; fp_mul(&acc, &ek, &q[0]); have = 1; if (k) { fp_mul(&t, &prev, &q[1]); fp_add(&acc, &acc, &t); } prev = ek; }
        else if (k == le && le) { fp_mul(&acc, &prev, &q[1]); have = 1; }
        if (k < lf) { if (have) fp_add(&acc, &acc, &f[k]); else acc = f[k]; }
        o[k] = acc;
    }
    LD(le + lf); ST(lo); loopc(lo); CTL(8 + 8 * lo);                  /* 8 per iteration: the tests k < le, k != 0, k < lf, have (compare, branch each); 8 once for the entry and exit */
    *res = o;
    return trimlen(o, lo);
}
static void mat_mulQ(mat_t *R, const fp *q, size_t lq) {
    fp *n0, *n2; size_t l0, l2;
    if (lq == 2) {
        CTL(2);
        l0 = mul_add_q2(&n0, R->e[0], R->len[0], q, R->e[1], R->len[1]);
        l2 = mul_add_q2(&n2, R->e[2], R->len[2], q, R->e[3], R->len[3]);
    } else {
    l0 = poly_mul_add_small(&n0, R->e[0], R->len[0], q, lq, R->e[1], R->len[1]);
    l2 = poly_mul_add_small(&n2, R->e[2], R->len[2], q, lq, R->e[3], R->len[3]);
    }
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
    fp *tH = NEW_FP(P.n), *tS = NEW_FP(P.n);
    *c = NEW_FP(N); *d = NEW_FP(N);
    int sgn = (R->h & 1) ? -1 : 1;
    CTL(60);                                 /* operand selection: at most 60 executed comparisons, branches and index operations (fixed upper bound) */
    /* c = s (r22 a - r12 b), d = s (r11 b - r21 a), s = (-1)^h.  Shared transforms: a and b are transformed once per row, every matrix entry once per row. */
    bilin_grp_t G[2]; int ng = 0;
    {
        const fp *V[2] = { a, b }; size_t lV[2] = { la, lb };
        const int ec[2] = { 3, 1 }, ed[2] = { 2, 0 };                 /* entry multiplying V[v] in c and in d */
        const int sc[2] = { sgn, -sgn }, sd[2] = { -sgn, sgn };
        for (int v = 0; v < 2; v++) {
            bilin_grp_t *g = &G[ng]; memset(g, 0, sizeof *g); g->nh = 1; g->H[0] = V[v]; g->lH[0] = lV[v];
            g->o[0][0] = g->o[1][0] = g->o[0][1] = g->o[1][1] = -1;
            if (!lV[v]) continue;
            if (R->len[ec[v]]) { g->S[g->ns] = R->e[ec[v]]; g->lS[g->ns] = R->len[ec[v]]; g->o[g->ns][0] = 0; g->sg[g->ns][0] = (signed char)sc[v]; g->ns++; }
            if (R->len[ed[v]]) { g->S[g->ns] = R->e[ed[v]]; g->lS[g->ns] = R->len[ed[v]]; g->o[g->ns][0] = 1; g->sg[g->ns][0] = (signed char)sd[v]; g->ns++; }
            if (g->ns) ng++;
            CTL(10);
        }
    }
    fp *outs[2] = { *c, *d }; size_t olen[2] = { nres, nres }; int eps[2];
    conv_bilin_otf(&P, 2, outs, olen, ng, G, tH, NULL, tS, eps);
    xfree(tH); xfree(tS);
    if (consume) mat_free((mat_t *)R);
    fp inv; plan_invN(&P, &inv);
    for (int k = 0; k < 2; k++) {
        fp *o = outs[k]; CTL(3);
        if (!eps[k]) { for (size_t i = 0; i < nres; i++) fp_set_zero(&o[i]); ST(nres); loopc(nres); continue; }
        fp sc = inv; if (eps[k] < 0) fp_neg(&sc, &inv);
        for (size_t i = 0; i < nres; i++) fp_mul(&o[i], &o[i], &sc);
        LD(nres); ST(nres); loopc(nres);
    }
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
    /* shared transforms: the entries of the right factor (held, up to two per group) and of the left factor (streamed) are transformed once per row */
    fp *tH0 = NEW_FP(P.n), *tH1 = NEW_FP(P.n), *tS = NEW_FP(P.n);
    fp *ob[4]; size_t ol[4];
    for (int k_ = 0; k_ < 4; k_++) { ob[k_] = NEW_FP(N); ol[k_] = L[k_]; }
    bilin_grp_t G[2]; int ng = 0;
    for (int t = 0; t < 2; t++) {
        bilin_grp_t *g = &G[ng]; memset(g, 0, sizeof *g); int hj[2] = { -1, -1 };
        g->o[0][0] = g->o[1][0] = g->o[0][1] = g->o[1][1] = -1;
        for (int j = 0; j < 2; j++) if (B->len[2 * t + j]) { hj[j] = g->nh; g->H[g->nh] = B->e[2 * t + j]; g->lH[g->nh] = B->len[2 * t + j]; g->nh++; }
        for (int i = 0; i < 2; i++) if (A->len[2 * i + t]) {
            g->S[g->ns] = A->e[2 * i + t]; g->lS[g->ns] = A->len[2 * i + t];
            for (int j = 0; j < 2; j++) if (hj[j] >= 0) { g->o[g->ns][hj[j]] = (signed char)(2 * i + j); g->sg[g->ns][hj[j]] = 1; }
            g->ns++;
        }
        if (g->nh && g->ns) ng++;
        CTL(20);
    }
    int eps[4];
    conv_bilin_otf(&P, 4, ob, ol, ng, G, tH0, tH1, tS, eps);
    xfree(tH0); xfree(tH1); xfree(tS);
    fp inv; plan_invN(&P, &inv);
    for (int k = 0; k < 4; k++) {
        size_t l = L[k]; fp *o = NEW_FP(l ? l : 1); CTL(3);
        if (eps[k]) {
            fp sc = inv; if (eps[k] < 0) fp_neg(&sc, &inv);
            for (size_t u = 0; u < l; u++) fp_mul(&o[u], &ob[k][u], &sc);
            LD(l); ST(l); loopc(l);
        }
        xfree(ob[k]);
        out->e[k] = o; out->len[k] = l ? trimlen(o, l) : 0;
    }
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


void hgcd(mat_t *R, fp **c, size_t *lc, fp **d, size_t *ld, const fp *a, size_t la, const fp *b, size_t lb, size_t k, int want_mat, int own) {
    hgcd_stat_calls++;
    CTL(40);                                 /* the size computations, comparisons and branches of this call (at most 40 executed operations, fixed upper bound) */
    size_t n = la - 1;
    if (lb == 0 || n - (lb - 1) > k) {
        if (want_mat) mat_set_identity(R);
        CTL(4);                              /* the two ownership tests */
        if (c) { if (own & 1) *c = (fp *)a; else *c = dupv(a, la); *lc = la; } else if (own & 1) xfree((void *)a);
        if (d) { if (own & 2) *d = (fp *)b; else *d = dupv(b, lb); *ld = lb; } else if (own & 2) xfree((void *)b);
        return;
    }
    if (k <= (size_t)hgcd_base_k) { hgcd_base(R, c, lc, d, ld, a, la, b, lb, k, want_mat, own); return; }
    size_t k1 = (k + 1) >> 1;                /* ceil(k/2): an addition and a shift */
    if (k1 + k1 > n) k1 = n >> 1;
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
/* Orchard Poseidon, r = RR partial rounds (here 3): a deterministic search over centres in a fixed public order, executed-outcome accounting.
 * usage: single [verbose]          (RR is set by the define below)
 * Trial i = 1, 2, 3, ... uses the centre c_i = i (the field element with the integer value i).  Each trial is run completely: line j = LINE,
 * g = monic odd part of (F(c+s) - F(c-s))/s in S = s^2 (degree m = (5^(6+RR) - 1)/2), R = S^((p-1)/2) mod g, G = gcd(g, R - 1) (half-gcd), and, when
 * deg G >= 1, one root S of G, s = sqrt(S), W1 = c + s, W2 = c - s, back-map, verify with two reference hashes.  The program stops at the FIRST trial that
 * yields a collision, then encodes the output in canonical hexadecimal (stage H).  Every operation of every executed trial, failed trials included, is
 * charged (common.h), and every charged operation belongs to exactly one stage (the stage chain below has no gap), so the stage table, the per-trial
 * table and the counters of the whole run give one and the same total.  The generator (seed 1) is used only by the root isolation, which runs only
 * when deg G >= 2.  There are no bounds; the one cap is MAXTR = 64 trials (exit code 2 without a collision), which the run does not reach. */
#include "attack.h"
#include "hgcd.h"
#include "pallas_consts.h"
#include "outbuf.h"

#ifndef RR
#define RR 3
#endif
#ifndef LINE
#define LINE 0
#endif
#define AMAX (RR == 1 ? 15 : RR == 2 ? 17 : 20)   /* 3 * 2^AMAX >= 2m - 1: the largest transform length (r = 3: 3 * 2^20 = 3145728 >= 1953123) */
typedef struct { const char *name; snap_t d; size_t peak; } stage_t;
#define MAXTR 64
static stage_t st[16]; static int nst;
static snap_t cur; static size_t gpeak, gpeak_live, gpeak_pay;
static const char *cur_name = NULL; static int cur_trial = 0;          /* the open stage and the trial it belongs to (0: none) */
static uint64_t trial_tot[MAXTR + 1];
static snap_t snap_add(snap_t a, snap_t b) { snap_t r; r.add = a.add + b.add; r.sub = a.sub + b.sub; r.mul = a.mul + b.mul; r.sqr = a.sqr + b.sqr; r.ld = a.ld + b.ld; r.st = a.st + b.st; r.ctl = a.ctl + b.ctl; r.rnd = a.rnd + b.rnd; r.perm = a.perm + b.perm; return r; }
/* close the open stage: its counters are added to the row of its name and to the total of its trial; the peak is the maximum over the visits */
static void stage_close(void) {
    if (!cur_name) return;
    snap_t d = snap_sub(snap(), cur);
    int k = 0; while (k < nst && strcmp(st[k].name, cur_name)) k++;
    if (k == nst) { st[k].name = cur_name; memset(&st[k].d, 0, sizeof st[k].d); st[k].peak = 0; nst++; }
    stage_t *s = &st[k]; s->d = snap_add(s->d, d); if (mem_peak > s->peak) s->peak = mem_peak;
    if (mem_peak > gpeak) { gpeak = mem_peak; gpeak_live = mem_peak_live; gpeak_pay = mem_peak_pay; }
    trial_tot[cur_trial] += snap_total(d);
    cur_name = NULL;
}
/* The stage bookkeeping (reading the nine counters twice, the subtraction, the search of the row by name, the additions into the row, the comparisons of the peaks,
 * the reset of the peak) is itself executed code: each stage_open (which includes the stage_close of the previous stage) is charged STAGE_BK = 1000 operations in
 * the stage it opens (bound: 9 loads + 9 subtractions + 9 additions + 9 stores + a search over at most 16 rows of at most 3 operations each + a name comparison
 * of at most 8 operations per row: under 400). */
#define STAGE_BK 1000
/* open the next stage (closing the previous one first, so no charged operation falls between two stages) */
static void stage_open(const char *name, int trial) { stage_close(); cur = snap(); mem_reset_peak(); cur_name = name; cur_trial = trial; CTL(STAGE_BK); }

/* canonical encoding of a field element as 64 hexadecimal digits (big-endian): one conversion out of the Montgomery representation (counted as one field
 * multiplication in pallas.c), then one pass over the 64 digits.  Per digit 12 operations: the loop (index update, comparison, branch), pos = 63 - i, the word
 * index pos >> 4, the shift count 4 * (pos & 15) (mask, multiply), the shift, the mask, the load of the digit from the table and the store of the byte;
 * 5 more for the entry of the call and the terminator. */
static const char HEXD[] = "0123456789abcdef";
static void enc_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    for (int i = 0; i < 64; i++) { int pos = 63 - i; out[i] = HEXD[(v[pos >> 4] >> (4 * (pos & 15))) & 15]; }
    out[64] = 0;
    CTL(64 * 12 + 5);
}

/* statements of main executed before the counters start: the argument test, rng_seed(1), poly_degree_m (6 + r iterations of a shift, an addition and a loop test),
 * the call of printf for the first report line (its bytes are inside the output buffer, charged in stage I), the reset of the counters: PROLOGUE = 500 (bound, under 100 operations) */
#define PROLOGUE 500
int main(int argc, char **argv) {
    const int r = RR;
    int verbose = argc > 1 ? (argv[1][0] - '0') : 0;
    rng_seed(1);
    size_t m = poly_degree_m(r);
    printf("r=%d line=%d m=%zu\n", r, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_open("init (twiddle table)", 0); CTL(PROLOGUE); ntt_init(AMAX);
    line_t L;
    stage_open("line setup", 0); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); }
    fp c, S, nk1, rho1, nk2, rho2, dg1, dg2, one; fp_set_one(&one);
    int found = 0, success = 0, trials = 0; size_t dG = 0;
    uint64_t t_centre[MAXTR + 1]; size_t t_deg[MAXTR + 1]; uint64_t t_gcd[MAXTR + 1];
    for (uint64_t i = 1; !success; i++) {
        trials++;
        if (trials > MAXTR) { fprintf(stderr, "too many trials\n"); return 2; }
        stage_open("A: centre c_i = i", trials); CTL(3 + 2); fp_from_u64(&c, i);       /* loop test and index update of the trial loop; the conversion is one counted multiplication */
        t_centre[trials] = i; t_deg[trials] = 0; t_gcd[trials] = 0;
        fp *g = NEW_FP(m + 1);
        stage_open("B: build g", trials); build_g(g, &L, &c, r);
        fp *F = NEW_FP(m);
        stage_open("C: S^((p-1)/2) mod g", trials); powx_lean(F, g, m, PALLAS_PM1H, (verbose && i == 1) ? 2 : 1);
        stage_open("D: gcd(g, S^h - 1) (half-gcd)", trials);
        fp_sub(&F[0], &F[0], &one);
        int dR = (int)m - 1; while (dR >= 0 && fp_is_zero(&F[dR])) dR--;
        CTL(9 * (uint64_t)((int)m - dR)); LD((int)m - dR);   /* the scan for the degree of R - 1: executed tests only */
        size_t lG = 0; fp *G = NULL;
        snap_t sg = snap();
        G = poly_gcd_own(&lG, g, m + 1, F, (size_t)dR + 1);
        t_gcd[trials] = snap_total(snap_sub(snap(), sg));
        dG = lG ? lG - 1 : 0; t_deg[trials] = dG;
        CTL(2);                                              /* the test deg G >= 1 */
        printf("trial %d centre %llu: gcd degree %zu, charged %llu\n", trials, (unsigned long long)i, dG, (unsigned long long)t_gcd[trials]); fflush(stdout);
        if (dG < 1) { if (G) xfree(G); continue; }
        stage_open("E: root isolation", trials); found = split_find_root(&S, G, dG);
        CTL(2);
        if (!found) continue;
        stage_open("F: sqrt + map back", trials);
        snap_t s0 = snap();
        fp s; int sq = fp_sqrt(&s, &S);
        CTL(12000);                                  /* Tonelli-Shanks control */
        CTL(2);
        if (!sq) { printf("root not a square?!\n"); found = 0; continue; }
        fp W1, W2;
        fp_add(&W1, &c, &s); fp_sub(&W2, &c, &s);
        map_back(&nk1, &rho1, &L, &W1);
        map_back(&nk2, &rho2, &L, &W2);
        bound_mem_since(s0);
        stage_open("G: verification (2 reference hashes)", trials);
        poseidon_hash_r_fp(&dg1, &nk1, &rho1, r);
        poseidon_hash_r_fp(&dg2, &nk2, &rho2, r);
        { snap_t d = snap_sub(snap(), cur); uint64_t ops = snap_arith(d); X.ld += 2 * ops; X.st += ops; X.ctl += 6 * ops; }
        int same_in = fp_eq(&nk1, &nk2) && fp_eq(&rho1, &rho2);
        int same_dg = fp_eq(&dg1, &dg2);
        CTL(3 * 8 + 2 * 3 + 2);                              /* three four-limb equality tests (8 operations each), the two tests combined, the test that ends the search */
        success = found && same_dg && !same_in;
    }
    /* stage H: the output of the program, the two canonical pairs (and the digest and the centre), encoded in canonical hexadecimal */
    char hx[6][65];
    stage_open("H: canonical encoding of the output", 0);
    enc_hex(hx[0], &nk1); enc_hex(hx[1], &rho1); enc_hex(hx[2], &nk2); enc_hex(hx[3], &rho2); enc_hex(hx[4], &dg1); enc_hex(hx[5], &c);
    /* stage I: everything the program does after the last charged algorithm step is charged here, BEFORE the report is formatted, so that the one total printed
     * includes it.  All of it executes; none of it is left outside the total:
     *  - the stage bookkeeping of the closing of stage I (STAGE_BK);
     *  - the formatting and the copy of the whole report: every byte of the report is produced by the small printf of nolibc.c (vfmt) into the output buffer.
     *    The printf has no integer division, modulo or floating point: a decimal number is formed by comparing with the powers of ten and subtracting them (at most
     *    about 44 operations per digit produced, and at most about 100 for the scan for the leading power), the format scan, padding and copy loops cost at most about
     *    10 operations per byte, and the parse of a conversion specification and the fetch of its argument at most about 150 per conversion; a conversion produces at least
     *    one byte.  A byte therefore costs at most FMT_PER_BYTE = 400 operations, and the buffer holds at most OUTCAP bytes (the program exits with status 3 at the
     *    check below if it were fuller), so the formatting of the whole report is charged FMT_PER_BYTE * OUTCAP, whatever the report contains;
     *  - the loops of the report over the stages and trials and the sums: REPORT_LOOPS = 20000;
     *  - the process entry (_start, c_start: under 20 instructions) and the check of the buffer length: ENTRY_CHECK = 100;
     *  - the single write system call: SYS_WRITE = 10000 + 8 * OUTCAP (the instruction work of the call is about 10 instructions; the 8 per byte stands for the
     *    kernel copy of the buffer), and the single exit_group system call: SYS_EXIT = 10000.
     * There is no other system call in the run (no mmap, munmap, clock_gettime, or second write). */
#define FMT_PER_BYTE 400
#define REPORT_LOOPS 20000
#define ENTRY_CHECK 100
#define SYS_WRITE (10000 + (OUTCAP << 3))
#define SYS_EXIT 10000
    stage_open("I: report formatting, single write, exit", 0);
    CTL(STAGE_BK + (uint64_t)FMT_PER_BYTE * OUTCAP + REPORT_LOOPS + ENTRY_CHECK + SYS_WRITE + SYS_EXIT);
    stage_close();                                           /* from here on only the report of the counters is printed */
    printf("TRIALS %d\n", trials);
    uint64_t all = 0, arith = 0, trs = 0;
    for (int i = 0; i < nst; i++) { all += snap_total(st[i].d); arith += snap_arith(st[i].d); }
    for (int t = 0; t <= trials; t++) trs += trial_tot[t];
    uint64_t counters = snap_total(snap());
    for (int i = 0; i < nst; i++)
        printf("  %-40s arith=%12llu other=%12llu total=%12llu peak=%zu\n", st[i].name, (unsigned long long)snap_arith(st[i].d),
               (unsigned long long)(snap_total(st[i].d) - snap_arith(st[i].d)), (unsigned long long)snap_total(st[i].d), st[i].peak);
    for (int t = 1; t <= trials; t++)
        printf("TRIALROW %d centre %llu degG %zu gcd %llu total %llu\n", t, (unsigned long long)t_centre[t], t_deg[t], (unsigned long long)t_gcd[t], (unsigned long long)trial_tot[t]);
    printf("TRIALROW 0 outside the trials (init, line setup, output encoding, report and write) total %llu\n", (unsigned long long)trial_tot[0]);
    printf("RECONCILE stages=%llu trials=%llu counters=%llu ok=%d\n", (unsigned long long)all, (unsigned long long)trs, (unsigned long long)counters, all == trs && trs == counters);
    printf("RESULT found=%d success=%d roots_degree=%zu\n", found, success, dG);
    printf("SPLIT levels=%llu tries=%llu shift=%llu pow=%llu gcd=%llu div=%llu\n", (unsigned long long)SPL_levels, (unsigned long long)SPL_tries, (unsigned long long)SPL_shift,
           (unsigned long long)SPL_pow, (unsigned long long)SPL_gcd, (unsigned long long)SPL_div);
    printf("SUMMARY total_all=%llu total_arith=%llu heap_peak=%zu\n", (unsigned long long)counters, (unsigned long long)arith, gpeak);
    printf("ARENA size=%zu extent=%zu\n", (size_t)ARENA, arena_hwm);
    printf("PEAKLIVE allocations=%zu payload=%zu headers=%zu\n", gpeak_live, gpeak_pay, gpeak_live * 64);
    { snap_t tt = snap();
      printf("TYPES add=%llu sub=%llu mul=%llu sqr=%llu ld=%llu st=%llu ctl=%llu rnd=%llu perm=%llu\n", (unsigned long long)tt.add, (unsigned long long)tt.sub, (unsigned long long)tt.mul, (unsigned long long)tt.sqr,
             (unsigned long long)tt.ld, (unsigned long long)tt.st, (unsigned long long)tt.ctl, (unsigned long long)tt.rnd, (unsigned long long)tt.perm); }
    if (success) {
        printf("COLLISION nk1  0x%s\nCOLLISION rho1 0x%s\nCOLLISION nk2  0x%s\nCOLLISION rho2 0x%s\nCOLLISION digest 0x%s\nCOLLISION centre 0x%s\n", hx[0], hx[1], hx[2], hx[3], hx[4], hx[5]);
    }
    if (out_len > OUTCAP) return 3;
    out_flush();                                             /* the single write */
    return success ? 0 : 1;
}
```

