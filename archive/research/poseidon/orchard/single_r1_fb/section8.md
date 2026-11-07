## 8. Success probability

**Statement.** One attempt of the program of section 4 (DEG_CAP = @@CAP@@, one uniform centre `c`, uniform shifts in stage E) outputs a digest collision with probability at least **0.3934647661**. The claimed value `@@PCLAIM@@` is below it.
The random experiment: the program draws the centre `c` (one uniform 254-bit word) and the shifts of stage E; all are independent and uniform (the cost model has independent uniform random words as a primitive; the executed program uses a 64-bit xorshift generator, and the claim uses the idealisation, D18 below).
The attempt succeeds iff `1 <= N(c) <= @@CAP@@` and stage E isolates a root, where `N(c)` is the number of nonzero squares `S` in `F_p` with `g_c(S) = 0` (stage D then returns `G` with `deg G = N(c)`).

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
| V5 | R_0 = x^p mod g; R_j = R_(j-1) o R_(j-1) mod g (j = 1..14); the chain for x^(p^l) (8 more compositions); two gcds of degree 39062 | @@V5_DESC@@ | deg g_l - deg g_1 = 20269; SHA-256 of f, u, R_j mod f (table in sec. 8.6.3) |
| total | | @@TOTAL_DESC@@ | |

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

**What the verifier does not cover, stated plainly.** (1) The cited theorems (sec. 8.8) are not recomputed. (2) The reference hash of V1 is a straight-line implementation inside the verifier (rounds 0-3, 4, 60-63 with the organizer constants); the two certificates of the package are checked by the organizer's hash. (3) The transcription of the lemmas of sec. 8.1-8.6 is a matter for reading, not for computation. (4) @@RUN_STATUS@@

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
