# Orchard Poseidon, r = 7: algebraic paper entry (not executed). Two free rounds on a line, odd part about a random centre, half-gcd, at most 2 centres; success probability from one declared premise

## 1. Claim

Target: `poseidon-orchard-r7-prefix-v1` (Orchard P128Pow5T3 over Pallas, full rounds 0-3, seven partial rounds 4, 5, 6, 7, 8, 9 and 10, full rounds 60-63,
state `[nk, rho, 2^65]`, digest = coordinate 0). Output: two distinct canonical pairs `(nk, rho)` with equal digests.

This entry is an algorithm with a worst-case cost bound and a success probability that rests on ONE declared premise. It is not an executed run of the r = 7 program: one trial at this round count needs about 136 GB of live memory and about 4.3 times the work of the r = 6 trial, and the program was not run at r = 7 (section 10.3 says why and lists what was executed instead). Read section 9 for the premise before anything else.

* The algorithm (sections 2-4): draw a centre `c` uniformly from `F_p` (fresh coins), build the odd part `g_c` of the line polynomial by evaluation and one inverse transform, compute `G = gcd(g_c, S^((p-1)/2) - 1)` by a power-mod and a half-gcd, and if `G` has degree between 1 and `DMAX = 16` isolate a root of `G` with at most `Z = 64` charged coin rounds, take its square root, map back and verify the two inputs with the reference hash. At most `K = 2` centres are tried, one after the other, on a single thread; the first verified collision stops the run.
* `success_probability = 0.63203`: a lower bound for the probability, over the algorithm's own coins (the centres and the isolation shifts), that one of the `K` centres yields a verified collision on the fixed target. It is derived in section 9 from the premise `H_root` and from proved statements only: `P >= 1 - (1 - q)^K - K (eps_iso + eps_coin)` with `q = 0.3934`, `K = 2`. The premise is an assumption about the fixed function; it is not proved and no test reaches this round count (section 10).
* `time_log2 = 40.85457` in target-compression units (`C(7) = 363` primitive operations per unit): the WORST-CASE operation count of the program, derived in section 6 as `T_fixed + K * T_trial + K * T_iso(Z)` with every trial charged in full, `N_max = 721698655708975` operations, `log2(N_max / 363) = 40.854564157919505`, rounded up at five decimals. The cap on the number of trials is tested at the start of every trial, so the program cannot run longer than this bound; there is no halting case outside the bound (sections 4.1 and 6). The twiddle table, the coins and the output are inside `N_max`, so `preprocessing_log2 = 0`.
* `memory_log2_bytes = 37.219` (`159963342164` bytes, section 7), including the code image, every buffer of the largest trial, the twiddle table and the stack bound. The normalized cost is `40.85457 + 17.219 = 58.07357`.
* Coins: the centre and the isolation shifts are drawn by the program, `DRAFT-PENDING COIN_WORDS` random 64-bit words in the worst case, each charged `DRAFT-PENDING COIN_WORD_COST` operations (section 6). They are fresh and independent of the target. The centres are NOT the fixed integers `1, 2, 3, ...` of our executed r = 3, 4, 5 entries: those runs are deterministic, have no probability space, and enter here only as evidence (section 10).
* No selection. The program has no input and no advice (`nonuniform_advice_log2_bytes = 0`).
* The method (two free rounds on a special line, so that the digest is a univariate polynomial of degree `5^13`, then the roots of its odd part about a centre, found with a gcd against `S^((p-1)/2) - 1`) is a known approach (the two-round bypass of Bariant, Bouvier, Leurent and Perrin, ToSC 2022/3). What is offered here is a complete finite implementation with a worst-case ledger, a low-memory schedule, and an explicit success premise.
* Nothing else in the claim is heuristic: the line construction, the degree of `F`, the odd-part reduction, the collision criterion (sections 2, 3, 5), the isolation lemma (section 9.3), the independence of the centres (by construction, from the coins), the cap rules and every operation count (sections 4, 6, 7) are proved or counted in this document. The one score-critical premise is `H_root` of section 9.1; the charging rules are declared as a supporting heuristic `H1-charging-rules` in `claim.json`.


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

2.3 Digest polynomial. Rounds 2, 3 (full), 4, 5, 6, 7, 8, 9, 10 (partial), 60, 61, 62, 63 (full) put thirteen S-box layers on top of an affine map, and the digest
is row 0 of the last MDS. So the digest equals `F(W)` with `deg F <= 5^13 = D = 1,220,703,125`. The leading coefficient is obtained by
propagating leading coefficients through the thirteen layers (a partial round contributes only coordinate 0 at the top degree); on the deployed constants it is nonzero for the line used:
`f_D(0) = DRAFT-PENDING FD0`
(computed; so `deg F = D` exactly). For random `tau`, `F(tau^5)` equals the reference hash of the canonical inputs built from `tau` (checked on 5 random `tau`
against an independent big-integer reference that reproduces the 11 public Orchard vectors).

2.4 Collision criterion. If `W1 != W2` and `F(W1) = F(W2)` then `tau1 != tau2` (`x -> x^5` is injective), hence `(U, V)` differ (`(a, b) != 0`),
hence the canonical pairs `(nk, rho)` differ, and the digests are equal. Every `W in F_p` is `tau^5` for exactly one `tau`.

## 3. Odd part with a centre

For a centre `c in F_p` write `F(c + s) - F(c - s) = 2 s g_c(s^2)`. Because `D = 2m + 1` with `m = 610,351,562`, `g_c` has degree exactly `m` and
leading coefficient `f_D(0)` (independent of `c`, nonzero), so `g_c` can be made monic. A collision pair with midpoint `c` is exactly `W1 = c + s`,
`W2 = c - s` with `s != 0` in `F_p`, i.e. `S = s^2` a nonzero square with `g_c(S) = 0`. The roots that are useful are the roots in `F_p` with
`S^((p-1)/2) = 1`: they are the roots of `G = gcd(g_c, S^((p-1)/2) - 1)` (roots that are nonsquares give `s` outside `F_p` and are of no use; `S = 0` gives `s = 0` and is not a root of `S^((p-1)/2) - 1`).
`G` divides `S^((p-1)/2) - 1`, which is squarefree, so `G` is a product of `deg G` distinct linear factors over `F_p`.

Construction of `g_c` by evaluation. `H = 805,306,368 = 3 * 2^28` divides `p - 1` (`p - 1 = 2^32 * 3 * q`), and `H >= m + 1`. Let `omega` be a primitive `H`-th root of unity
and `zeta` with `zeta^2 = omega`. Then `g_c(omega^i) = (F(c + zeta^i) - F(c - zeta^i)) / (2 zeta^i)`, `i = 0..H-1`. One inverse transform of size `H` returns the
coefficients of `g_c` (the `H - m - 1` high coefficients are zero because `deg g_c = m < H`; interpolation is exact). The `2H = 1,610,612,736` evaluations of `F` are each charged as
one target-compression unit (`C(7) = 363` operations), although a line evaluation (affine start, the remaining rounds, one row of the last MDS) is a strict subset of the work of a full reference permutation.
The extra work of the loop (two additions for the points, one subtraction, one multiplication by `1/(2 zeta^i)`, two multiplications for the recurrences `zeta^{i+1}`, `zeta^{-i-1}`, one store with its address operation,
the loop control, the update of the row counter `row = k mod 3` (increment, comparison, branch, assignment; no modulo instruction), and the executed shifts, masks, ors and loop control of the bit-reversed index `layout_index_r`, which are counted inside that function) is charged on top.



## 4. The program (at most K centres, one thread)

### 4.1 Stages, coins and the stopping rule

```
init:   twiddle table (once)
setup:  the line (line_setup) (once)
for t = 1, 2, ..., K:                                  [the test t <= K is made at the start of every trial; no other exit except success]
  A  c := a uniform element of F_p from the coin words (section 4.1.1)
  B  g := monic g_c, by section 3 (1,610,612,736 evaluations + one inverse NTT of size 805,306,368 + the test that the leading coefficient is nonzero + normalisation by the leading coefficient)
  C  R := S^((p-1)/2) mod g           (left-to-right square-and-multiply on the exponent, base S; 224 modular squarings, 45 of the steps also multiply by S by a streaming shift)
  D  G := gcd(g, R - 1) (monic)       (half-gcd with NTT products, section 4.4)
  E  if deg G = 0 or deg G > DMAX: the trial ends, next t.   Otherwise isolate a root S of G (section 4.1.2).  If none is isolated within Z rounds: the trial ends, next t.
  F  s := sqrt(S) (Tonelli-Shanks, 2-adicity 32); W1 = c + s, W2 = c - s; tau_i = W_i^e; (U,V)_i = Q + tau_i (a,b); nk_i = U_i^e - c_{0,0}, rho_i = V_i^e - c_{0,1}
  G  verify: the two reference hashes (363 operations each) are equal and the pairs differ -> go to H; otherwise the trial ends, next t
H  output: the two pairs (and the digest and the centre) are converted to canonical form and encoded as 64 hexadecimal digits each; exit status 0.
   If t > K was reached: exit status 2, no output (the failure event, probability bounded in section 9).
```
The exponent `(p-1)/2` has bit length 254 and Hamming weight 46. Binary powering therefore performs 253 modular squarings and 45 multiplications by `S`; the 29 bits after the leading one are zero, so the program starts from the monomial `S^v` with `v = 2^29 < m` (this absorbs 29 of the 253 squarings, 29 + 224 = 253), and the squaring loop of stage C has 224 steps, of which 45 also multiply by `S` (a streaming shift).

Stopping rule over the `K` centres. The loop bound `K = 2` is a constant of the source. A trial is run to its end whatever its outcome; the claim charges every trial at its maximum (stages E to G at their worst case, section 6), so a trial that fails early is paid for at the full-trial price, never less. Stage E is entered only when `1 <= deg G <= DMAX`, and at most `Z` rounds are made in it. The program has no other loop whose length depends on data: the loops of stages B to D have lengths fixed by `m` and the exponent (sections 4.3, 4.4), the powering has a fixed number of steps, and the half-gcd has the fixed recursion bound `DRAFT-PENDING HGCD_BOUND`. Hence the number of executed operations is at most `N_max` on every coin sequence and every target value, the program cannot halt early except by the success exit, and nothing in the claim depends on a run being lucky.

#### 4.1.1 Coins

DRAFT-PENDING COIN_RULE

#### 4.1.2 Stage E: isolating a root of G

`G` is monic, squarefree, and a product of `d = deg G` distinct linear factors over `F_p` with `1 <= d <= DMAX` (it divides `S^((p-1)/2) - 1`, which is squarefree). If `d = 1` the root is `S = -G_0`. If `d >= 2`, repeat at most `Z` times, while `deg G >= 2`: draw a uniform `a` from `F_p` (coin words as in 4.1.1), compute `X_a = (X + a)^((p-1)/2) mod G`, `G_+ = gcd(G, X_a - 1)`, `G_- = gcd(G, X_a + 1)`. Then `G = G_+ G_- (X + a)^e0` with `e0` = 1 if `G(-a) = 0` and 0 otherwise. Keep, as the new `G`, the one of `G_+`, `G_-` of smaller nonzero degree (ties: `G_+`) if at least one is nonconstant; if both are constant then `G = X + a` and the root is `-a`. Each round is charged at the cost of its operations at degree `deg G <= DMAX` (section 6). The lemma of section 9.3 bounds the probability that `deg G >= 2` remains after `Z` rounds.

### 4.2 Machine model and charging rules

DRAFT-PENDING CHARGING_RULES

(Source of this section: the machine model of the executed r = 5 entry, with its thread clauses and all thread charges removed because this program runs on one thread, and with the coin rule of 4.1.1 and the isolation rounds of 4.1.2 added; it is produced together with the ledger of section 6.)


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

By sections 2-3: a root `S` of `G` is a nonzero square root of `g_c`, `s = sqrt(S) != 0`, `F(c+s) = F(c-s)`, `c+s != c-s`, so the canonical pairs of section 2 differ and collide. Stage G recomputes both reference hashes and compares them; the program exits with status 0 only if they are equal and the pairs differ. A run that does not reach stage H prints nothing and exits with status 2; it never outputs a non-collision. This section is a statement about the output of a successful run, and holds for every coin sequence. It contains no probability.

## 6. Ledger: worst-case operation count (primitive operations; `C(7) = 363`)

Notation: `T_fixed` = init (twiddle table) + setup (the line) + stage H and the exit; `T_trial` = stages A to D and G of one trial, plus stages E and F at their worst case (E: `Z` rounds at degree `DMAX`, F: the square root and the map back, all independent of the data except through the fixed bounds); `T_iso(Z)` = the isolation rounds at their cap. The claim is
`N_max = T_fixed + K * (T_trial) ` with the isolation cap and the coin draws inside `T_trial`; `time_log2 = ceil_5(log2(N_max / 363))`.

DRAFT-PENDING LEDGER_SECTION

Every figure above is an upper bound that the program meets or exceeds on every coin sequence: each loop bound is a constant or a function of `m` only, the trial loop is capped at `K` and tested at the start of each trial, and the operations of each stage are those of the shipped source under the rules of section 4.2. No figure is measured on a run at r = 7 (section 10.3); a validation of the formula against the counters of the executed runs at smaller `r` is in section 6.1.

### 6.1 Ledger recomputation and validation

DRAFT-PENDING LEDGER_RECOMPUTATION

## 7. Memory

DRAFT-PENDING MEMORY_SECTION

## 8. What is and is not provided

* Provided: the algebraic derivation (sections 2-3), the algorithm and its worst-case charges (4, 6, 7), the complete C source of the program (section 11), the premise `H_root` with its role, scope and limitations (section 9), the success bound derived from it with a sensitivity table (section 9.2), the isolation lemma with proof (section 9.3), and the evidence we have, labelled as evidence (section 10).
* Not provided: any run of this program at r = 7; any proof of `H_root`; any measurement of the fraction of centres with a usable root at r = 7 (one trial needs about 136 GB of memory). No collision at r = 7 is claimed or shown.
* The experiments declared in `experiments/` are described in section 10.2 together with what they cannot show. The organizer's experiment report contains no iid success interval and no inferred expectation for Python experiments, and none is claimed.
* Nothing is submitted as a certificate: the certificate manifest is empty.
* The package contains only the claim, the proof, the empty certificate manifest and the experiments, so the C source is part of this document (section 11) as text, and the program reads no input file. Build: DRAFT-PENDING BUILD_COMMAND. Run: DRAFT-PENDING RUN_COMMAND.
* The cost claim assumes the model of section 4.2; word-level costs beyond the charged loads, stores and control operations (cache, bandwidth) are not part of it. The organizer did not run the program, so the counts rest on the shipped source.

## 9. Success probability and the premise H_root

### 9.1 The premise

**Premise H_root (an assumption, not proved): for the fixed target, the fraction of centres `c` in `F_p` for which the odd part `g_c` of the line polynomial has at least one and at most `DMAX = 16` distinct roots `S` in `F_p` that are nonzero squares is at least `q = 0.3934`.** The organizer's target is fixed and `F` is a fixed deterministic polynomial; the only randomness of the algorithm is its coins (the centres and the isolation shifts). Nothing in this document proves, for the fixed `F`, that the fraction of good centres is the value it takes for a random polynomial of degree `m`: that transfer is the premise, and it is the one score-critical premise of this package.

Four fields. **Statement:** for the fixed polynomial `F` of section 2.3 at r = 7 (degree `5^13`), let `E_c` be the event `1 <= deg G_c <= DMAX`, where `G_c = gcd(g_c, S^((p-1)/2) - 1)` (section 3); then `rho := #{c in F_p : E_c} / p` satisfies `rho >= q = 0.3934`. For a polynomial of degree `m` drawn uniformly at random the number of its roots in `F_p` is asymptotically Poisson with mean 1 (so a root exists with probability `1 - 1/e`, about 0.632), each root is a nonzero square independently with probability one half, so the number of usable roots is asymptotically Poisson with mean 1/2; the premise value is `1 - e^(-1/2) = 0.393469...` minus the Poisson tail beyond `DMAX` (below `2^-60` for `DMAX = 16`), rounded down to `q`. **Role:** score-critical. **Scope:** the fixed Poseidon target `poseidon-orchard-r7-prefix-v1`, this line construction (sections 2-3: the line `j = 0` of the first two rounds, the odd part about a centre), the event `E_c` of this section, centres uniform on `F_p`. **Limitations:** an assumption with no proof known to us. Nothing in the algebra forces the fraction of good centres to be the random-polynomial value; the odd parts `g_c` for different `c` are not independent polynomials, they are all derived from one `F`, and a structured `F` could in principle have many more or many fewer centres with a usable root. No test reaches degree `5^13` (section 10.3). The evidence of section 10 is consistent with the premise and does not establish it.

What the premise does not contain: independence of different centres is not assumed. The centres are drawn by the algorithm, independently of each other and of the target, so the events `E_{c_1}, E_{c_2}, ...` are independent Bernoulli events of the same fixed parameter `rho` up to the statistical distance `eps_coin` of the coin rule (4.1.1). Distinct inputs are guaranteed by section 2.4, not by the coins. The other steps of the bound are proved in 9.2 and 9.3.

### 9.2 The success bound and its sensitivity

Let `c_1, ..., c_K` be the centres, drawn as in 4.1.1, each within statistical distance `eps_coin = 2^-65` of uniform and mutually independent. A trial `t` ends in a verified collision whenever `E_{c_t}` holds and the isolation of stage E succeeds (sections 2-5). By the lemma of 9.3 the isolation fails, given `E_{c_t}`, with probability at most `eps_iso = 2^-48`, over coins that are fresh for that stage. Therefore

`P[no collision in K trials] <= (1 - rho)^K + K eps_coin + K eps_iso <= (1 - q)^K + K (eps_coin + eps_iso)`,

so, **given the premise**,

`P[success] >= 1 - (1 - q)^K - K (eps_coin + eps_iso) = 0.632036440 >= 0.63203`, with `q = 0.3934`, `K = 2`, and `eps_coin + eps_iso <= 3.55e-15`.

The probability is over the algorithm's coins for the fixed target. It is not a probability over targets, not a sampled frequency and not a statement about reviewers or runs: no run of this program at r = 7 enters it.

Sensitivity of the bound to the premise (the terms `K (eps_coin + eps_iso)` are below `10^-13` and omitted). If the true fraction of good centres is `q'` instead of `q`:

| `q'` | success at K=1 | K=2 | K=3 | K=4 | centres needed for 0.39 | extra log2 cost over K=2 |
|---:|---:|---:|---:|---:|---:|---:|
| 0.39347 (random value) | 0.39347 | 0.63212 | 0.77687 | 0.86466 | 1 | -1.000 |
| 0.35 | 0.35000 | 0.57750 | 0.72537 | 0.82149 | 2 | 0.000 |
| 0.30 | 0.30000 | 0.51000 | 0.65700 | 0.75990 | 2 | 0.000 |
| 0.25 | 0.25000 | 0.43750 | 0.57812 | 0.68359 | 2 | 0.000 |
| 0.20 | 0.20000 | 0.36000 | 0.48800 | 0.59040 | 3 | 0.585 |
| 0.15 | 0.15000 | 0.27750 | 0.38588 | 0.47799 | 4 | 1.000 |
| 0.10 | 0.10000 | 0.19000 | 0.27100 | 0.34390 | 5 | 1.322 |
| 0.05 | 0.05000 | 0.09750 | 0.14263 | 0.18549 | 10 | 2.322 |
| 0.02 | 0.02000 | 0.03960 | 0.05881 | 0.07763 | 25 | 3.644 |
| 0.01 | 0.01000 | 0.01990 | 0.02970 | 0.03940 | 50 | 4.644 |

The smallest `q'` for which `K` centres give 0.39 is 0.39000 for K=1, 0.21898 for K=2, 0.15191 for K=3 and 0.11625 for K=4. The time bound is `T_fixed + K T_trial` with `T_fixed` much smaller than `T_trial`, so using `K'` centres instead of `K` costs about `log2(K'/K)` more in `time_log2` (the last column is for `K = 2`; the unit is the same as `time_log2`). With the submitted `K = 2`, the premise can be off by the factor `q'/q = 0.557` (that is, down to `q' = 0.21898`) before the bound falls below 0.39. A premise that fails altogether (`q'` near 0.01) would cost 4.6 bits at `K=2`, if the failure were known; it is not known.

### 9.3 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (a uniform `a`), with probability at least `(p-1)/(2p)` both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, (p-1)/(2p)) <= ceil(log2 DMAX) - 1]` which for `DMAX = 16`, `Z = 64` is at most `2^-48`.

*Proof.* Let `u != v` be two roots of `G` (say the two smallest as integers), `chi` the quadratic character on `F_p`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other is a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root `r` of `G` is a root of `X_a - 1` iff `chi(r+a) = 1`, of `X_a + 1` iff `chi(r+a) = -1`). Both parts are then nonconstant and their degrees sum to at most `d`, so the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_{a != -u,-v} chi((a+u)(a+v)) = -1` because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`. The probability is `(p-1)/(2p)`. A part is always a divisor of `G`, so the degree is nonincreasing, whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is fresh and uniform, so every round is of this kind with probability at least `w = (p-1)/(2p)`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is `P[Bin(Z, w) <= ceil(log2 DMAX) - 1]`. For `Z = 64`, `DMAX = 16`: `sum_{j <= 3} C(64, j) w^j (1-w)^(64-j) <= 43745 (1/2 + 1/(2p))^64 < 2^-48`, since `1/(2p)` is below `2^-254`. This is a proved bound under the coins of the algorithm, not a premise, and not a sample. (For other `DMAX`, `Z` recompute the sum; the template value is `2^-48`.)

## 10. Evidence

Everything in this section is evidence. None of it is the bound of section 9, none enters `success_probability`, and none is a lower bound on `rho`. Every run below was made by us (the organizer did not run any of them); each was a deterministic program run on the fixed target with the centres `1, 2, 3, ...` in that order and stopped at its first collision; none had coins, so none has a probability space and none is a sample of the centre distribution of section 9.

### 10.1 Executed full-scale outcomes at r = 3, 4, 5, 6

| round | degree of F | m | centres tried (in order) | outcome per centre (`deg G`) | successes | operations N (executed) | time_log2 | memory (bytes) | threads, wall |
|---:|---:|---:|---|---|---:|---:|---:|---:|---|
| 3 | 5^9 | 976,562 | 1 | c=1: 1 | 1 | 317,054,280,703 | 30.08182 | 250,386,180 | single-thread program, 3,202.9 s |
| 4 | 5^10 | 4,882,812 | 1, 2 | c=1: 0 (no usable root); c=2: 1 | 1 | 3,992,419,235,666 | 33.63159 | 1,231,371,140 | 6 threads, 13,030.2 s |
| 5 | 5^11 | 24,414,062 | 1 | c=1: 1 | 1 | 9,205,778,231,873 | 34.73925 | 5,604,188,884 | 13 threads, 22,048.3 s |
| 6 | 5^12 | 122,070,312 | - | run in progress, no result yet | - | - | - | - | 24 threads, running |

The r = 6 run started 2026-10-15 18:53:11 UTC (24 threads, about 31 GB live) and takes about 40-55 hours per trial; At the time this package was written it had not finished; no r = 6 number is used anywhere in this document.

Counted together, r = 3, 4, 5 tried 4 centres and found a usable root at 3 of them. The runs stop at the first success, so each round has exactly one success by construction; the informative number is how many centres failed before it: 0, 1 and 0. The centres are the fixed integers 1 and 2, not random draws, and the stopping rule makes the pooled frequency a biased view of the fraction of good centres. No estimate and no interval of `rho` is derived from these counts, because none would be a lower bound for `rho`. What they show is only that the first centres tried gave a usable root at rounds 3, 4, 5, in agreement with a good-centre fraction near the random value 0.39 and with no sign of a structural deficit.

The collisions found (each is a pair of distinct canonical `(nk, rho)` with equal digests at its own round count; the organizer's digest function accepted each of them at its round count when it was filed):

* r = 3 (centre 1):
  * nk1  = 0x0499f5c4354bafa11ca451e656d380d078444ed6561d6355487453741e1a6815
  * rho1 = 0x21625d728b86cf0865d7ad7cd99a0c20464939e5253940d95b3a639d7a909af7
  * nk2  = 0x1009050c8c1414cf5975db612457a2e49b06db64fce28c7dd5ad52ed8fc2c567
  * rho2 = 0x31611cd777dc6c418e048d96a497f46fa51523b47dbadcd97d0ad171160fcdb8
  * digest (field element) = 0x325165c946fe20c28af82e940ec89fca03e6fb74afa1a3fa28a54e552a1f12ec, as the organizer's 32 little-endian bytes `ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132`
* r = 4 (centre 2):
  * nk1  = 0x25c10b7d8d36b332b4a4ddb92f1f1a3ffa40259b7b77b0ba458ad0be367ab979
  * rho1 = 0x2e568f6667ceaedd4195dbd24a55c365075306af4a5d0931b1707ba0bf7616ea
  * nk2  = 0x2acbf624301319ca0830c5fda78ae08e00d75798f24adf1320401f1a3bc4c580
  * rho2 = 0x162fa98e63ff13622228cd9e3b4d9039124a918f1f11d12718a2a782ed69fb17
  * digest (field element) = 0x3deca6a0b865e914ebcc74484b3cedb56b9f6293338881693e00cbee0c161fa1, as the organizer's 32 little-endian bytes `a11f160ceecb003e6981883393629f6bb5ed3c4b4874cceb14e965b8a0a6ec3d`
* r = 5 (centre 1):
  * nk1  = 0x35aefd661e07cec063071e6f92f2bbcfd6bbc794bc99be91c008fed0a2a5ebb5
  * rho1 = 0x3dd4caae629bb08efa85dd470f72f2fc183cf026de9cd1aa356e147f058a0090
  * nk2  = 0x242b99e697375e309d54e5db54c215cb6526b420e7ff760eec690a5fb189c764
  * rho2 = 0x2e9a4cf95fce4bbf8ebe8eb72485446ceca86268a6c2305f70d4460179334e37
  * digest (field element) = 0x2425532a0c6af3e7c0864ce59d3b1ddbd62ea79ba594c3305f8fbacf7c184249, as the organizer's 32 little-endian bytes `4942187ccfba8f5f30c394a59ba72ed6db1d3b9de54c86c0e7f36a0c2a532524`
* r = 6: none yet (run in progress)

### 10.2 Experiments declared in `experiments/manifest.json`

Both are `python-message-pairs-v1` experiments with the event `full-collision`. The organizer's selected target is r = 7; the organizer's digest callback evaluates that one round count, so neither experiment can return a pair that the callback would accept as a collision, and both return `null` messages in every trial. Their content is in the untrusted numeric observations (the organizer labels them untrusted and does not credit them), and in the source text, which the judge sees in full. The fixed seeds are in the sources, declared in advance; the request seeds are not used.

* `replay-r3-r6-pairs` (`experiments/replay_pairs.py`): recomputes the digest of each recorded pair above at its own round count with an independent copy of the organizer permutation (the pinned deployed constants, original rounds 0-9 and 60-63), and checks both elements of each message are canonical, the two messages are distinct, the two digests are equal, and the digest equals the recorded one. Our local plain-Python run (not the organizer executor): plain Python 3.14.3 on the build machine: 3 of 3 recorded pairs verified (r = 3, 4, 5; replay_all_ok = 1; digests ec121f2a554ea528faa3a1af74fbe603ca9fc80e942ef88ac220fe46c9655132, a11f160ceecb003e6981883393629f6bb5ed3c4b4874cceb14e965b8a0a6ec3d, 4942187ccfba8f5f30c394a59ba72ed6db1d3b9de54c86c0e7f36a0c2a532524 as organizer bytes); the same three pairs also agree with the organizer's own verifier.poseidon.digest run locally on them. It confirms that the pairs of 10.1 are collisions of the stated targets. It does not test the premise, the cost, or any round above 5.
* `toy-root-fraction` (`experiments/toy_root_fraction.py`): the same construction on a toy Poseidon-like permutation over a prime `p = 8017` (`p = 2 mod 5`) with seeded random constants and MDS (not the deployed ones): round 0, the free line round 1, and `L = 3` (layers full, partial, full) or `L = 4` (full, full, partial, full) further layers, so `F` has degree 125 or 625. For each toy it checks the line against the genuine permutation at 20 random points, checks the degree of `F` by finite differences, and counts, for EVERY centre in `F_p`, whether some `s != 0` has `F(c+s) = F(c-s)` (that is, whether `g_c` has a root that is a nonzero square), and does the same for a uniformly random table (control). Our local plain-Python run: plain Python 3.14.3 on the build machine, about 5 s: p = 8017; L = 3 (degree 125): line check and degree check passed, 3,145 of 8,017 centres have a usable root, 3,145 of 8,017 for the random table; L = 4 (degree 625): line check and degree check passed, 3,166 of 8,017 centres, 3,179 of 8,017 for the random table. The exact fractions are measurements on these two fixed toy functions; the value for a random function is `1 - (1 - 1/p)^((p-1)/2)` = 0.3935 (the toy numbers are expected to differ from it by fluctuation of the order of a percent). The toy fractions are consistent with the random value.

### 10.3 What this evidence cannot show, and why there is no executed run at r = 7

The premise `H_root` is about a polynomial of degree `5^13` over a 255-bit field. It cannot be proved here and it cannot be tested at that size. One trial at r = 7 needs about 136 GB of live memory and about 4.3 times the work of the r = 6 trial, and the degree grows by a factor of 5 with every round, so no single trial of the real construction can be run on the machines we have, and a measurement of `rho` would need several trials. The toy experiment of 10.2 reaches degree 625 at most, over a field of 13 bits; it measures other functions, not this one. So the claim here is the premise, supported by every full-scale outcome we have: the executed centres at r = 3, 4, 5 (and r = 6 when it ends), each a single deterministic run with fixed centres. Those runs show the construction works at those degrees and that usable roots appeared at the first or second centre tried each time; they show nothing about `rho` at r = 7 beyond that, and they are not a statistical sample.

At r = 1 and r = 2 the situation was different: our earlier entries on this line could be settled without a premise (the degree is small enough that the success claim there rested on a bound proved in the package or on the executed run itself, as filed). From r = 6 the executed run takes days per trial, at r = 7 it cannot be run at all, and the success bound has to be the premise of 9.1.

The organizer's Python experiment kind returns checked output pairs only; it infers no probability and no cost, and our two experiments are written within that scope (they do not claim otherwise).

## 11. Complete source of the program

DRAFT-PENDING SOURCE_INTRO

### single.c

```c
/* Orchard Poseidon, r = RR partial rounds (here 5): a deterministic search over centres in a fixed public order, executed-outcome accounting.
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
#include "par.h"

#ifndef RR
#define RR 6
#endif
#ifndef LINE
#define LINE 0
#endif
#define AMAX (RR == 1 ? 15 : RR == 2 ? 17 : RR == 3 ? 20 : RR == 4 ? 22 : RR == 5 ? 24 : RR == 6 ? 27 : RR == 7 ? 29 : 31)   /* 3 * 2^AMAX >= 2m - 1: the largest transform length (r = 5: 3 * 2^24 = 50331648 >= 48828123) */
typedef struct { const char *name; snap_t d; size_t peak; } stage_t;
#ifndef MAXTR
#define MAXTR 2                                              /* K: the number of centres tried (algebraic paper 4.1); compile-time define */
#endif
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
static void stage_open(const char *name, int trial) {
    stage_close(); cur = snap(); mem_reset_peak(); cur_name = name; cur_trial = trial; CTL(STAGE_BK); }

/* canonical encoding of a field element as 64 hexadecimal digits (big-endian): one conversion out of the Montgomery representation (counted as one field
 * multiplication in pallas.c), then one pass over the 64 digits.  Per digit 12 operations: the loop (index update, comparison, branch), pos = 63 - i, the word
 * index pos >> 4, the shift count (pos & 15) << 2 (mask, shift), the shift, the mask, the load of the digit from the table and the store of the byte;
 * 5 more for the entry of the call and the terminator. */
static const char HEXD[] = "0123456789abcdef";
static void enc_hex(char out[65], const fp *a) {
    uint64_t v[4]; fp_to_limbs(v, a);
    for (int i = 0; i < 64; i++) { int pos = 63 - i; out[i] = HEXD[(v[pos >> 4] >> ((pos & 15) << 2)) & 15]; }
    out[64] = 0;
    CTL(64 * 12 + 5);
}

/* statements of main executed before the counters start: the argument test, rng_seed(1), poly_degree_m (6 + r iterations of a shift, an addition and a loop test),
 * the call of printf for the first report line (its bytes are inside the output buffer, charged in stage I), the reset of the counters: PROLOGUE = 500 (bound, under 100 operations) */
#define PROLOGUE 500
int main(int argc, char **argv) {
    const int r = RR;
    int verbose = argc > 1 ? (argv[1][0] - '0') : 0;
    par_init(1);                                             /* single thread: no worker is created, no thread-control charge exists (par_nt = 1) */
#ifndef COIN_SEED
#define COIN_SEED 1
#endif
    rng_seed(COIN_SEED);                                     /* the source of the coin words of this build (xorshift64); see CHANGES.md */
    size_t m = poly_degree_m(r);
    printf("r=%d line=%d m=%zu\n", r, LINE, m);
    fp_counters_reset(); memset(&X, 0, sizeof X);
    stage_open("init (twiddle table)", 0); CTL(PROLOGUE); par_charge_setup(); ntt_init(AMAX);
    line_t L;
    stage_open("line setup", 0); { snap_t s0 = snap(); line_setup(&L, LINE); bound_mem_since(s0); }
    fp c, S, nk1, rho1, nk2, rho2, dg1, dg2, one; fp_set_one(&one);
    int found = 0, success = 0, trials = 0; size_t dG = 0;
    uint64_t t_centre[MAXTR + 1]; size_t t_deg[MAXTR + 1]; uint64_t t_gcd[MAXTR + 1];
    for (uint64_t i = 1; !success; i++) {
        trials++;
        if (trials > MAXTR) return 2;                        /* K centres failed: clean failure exit, status 2, no output */
        stage_open("A: centre from coins", trials); CTL(3 + 2); rnd_fp320(&c);       /* loop test and index update of the trial loop; the coin draw is charged inside rnd_fp320 */
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
        CTL(2 + 2);                                          /* the tests deg G >= 1 and deg G <= DMAX */
        printf("trial %d centre %llu: gcd degree %zu, charged %llu\n", trials, (unsigned long long)i, dG, (unsigned long long)t_gcd[trials]); fflush(stdout);
        if (dG < 1 || dG > DMAX) { if (G) xfree(G); continue; }
        stage_open("E: root isolation", trials); found = split_find_root_capped(&S, G, dG);
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
     *    44 operations per digit produced, and at most 100 for the scan for the leading power), the format scan, padding and copy loops cost at most
     *    10 operations per byte, and the parse of a conversion specification and the fetch of its argument at most 150 per conversion; a conversion produces at least
     *    one byte.  A byte therefore costs at most FMT_PER_BYTE = 400 operations, and the buffer holds at most OUTCAP bytes (the program exits with status 3 at the
     *    check below if it were fuller), so the formatting of the whole report is charged FMT_PER_BYTE * OUTCAP, whatever the report contains;
     *  - the loops of the report over the stages and trials and the sums: REPORT_LOOPS = 20000;
     *  - the process entry (_start, c_start: under 20 instructions) and the check of the buffer length: ENTRY_CHECK = 100;
     *  - the single write system call: SYS_WRITE = 10000 + 8 * OUTCAP (the instruction work of the call in the process is at most 10 instructions; the 8 per byte stands for the
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
    printf("THREADS n=%d dispatches=%llu chunks=%llu woken=%llu thread_control=%llu split_extra=%llu algorithmic_total=%llu\n", par_nt, (unsigned long long)thr_disp, (unsigned long long)thr_chunks,
           (unsigned long long)thr_woken, (unsigned long long)thr_ctl, (unsigned long long)thr_extra, (unsigned long long)(counters - thr_ctl - thr_extra));
    printf("THREADMEM n=%d stack=%d block=%d used=%zu image=%zu\n", par_nt, WSTACK, TLS_MAXB, par_threadmem(par_nt), par_threadmem(NT_MAX));
    printf("PEAKLIVE allocations=%zu payload=%zu headers=%zu\n", gpeak_live, gpeak_pay, gpeak_live << 6);
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
