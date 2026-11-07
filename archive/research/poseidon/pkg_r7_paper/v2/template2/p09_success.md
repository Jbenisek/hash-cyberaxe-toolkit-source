## 9. Success probability and the premise `H-GEOM-w@@W@@`

### 9.1 The premise

Notation. `p` is the Pallas prime, `D = 5^@@DEXP@@`, and `F` is the fixed polynomial of section 2.3 at r = @@R@@ (degree `D`, leading coefficient `f_D(0) != 0`). Put
`G(c, t) = (F(c + t) - F(c - t)) / (2 t)` in `F_p[c, t]`, a polynomial of total degree `D - 1` (section 3: `G(c, t) = g_c(t^2)`). For `c` in `F_p` let `k(c)` be the number of nonzero squares `S = t^2` with `G(c, t) = 0`; this is `deg G_c` of section 3. Let `V` be the Zariski closure of `{ (c, s_1, s_2) : G(c, s_1) = G(c, s_2) = 0, s_1^2 != s_2^2 }`.

**Premise `H-GEOM-w@@W@@` (an assumption, not proved).** The plane curve `G = 0` has at least one absolutely irreducible component defined over `F_p`, and `V` is a curve (pure dimension 1) with at most `w = @@W@@` absolutely irreducible components defined over `F_p`.

Four fields (as in claim.json). **Statement:** the premise above. **Role:** score-critical. **Scope:** the fixed target `poseidon-orchard-r@@R@@-prefix-v1`, this line construction (the line `j = @@LINE@@` of the first two rounds, section 2), the polynomial `F` of section 2.3; centres uniform on `F_p`. Nothing is claimed for other round counts. **Limitations:** an assumption with no proof known to us. It concerns this `F`, not every polynomial of degree `D`: it is false for permutation polynomials, in particular for every pure composition of maps `x -> a x^5 + b` (`p = 2 mod 5`, so those maps are bijective), and it is not implied by a statement about components over the algebraic closure alone (`F(X) = X^3` over `F_101`: `(F(X) - F(Y)) / (X - Y)` splits into two conjugate lines over `F_(101^2)`, the curve has no off-diagonal rational point, and `k` is zero for every `c`). No test reaches degree `5^@@DEXP@@`; no count of rational points of either curve is available for the real `F`. The explicit constants of 9.2 make the reduction usable for r <= 7 only; the plane genus bound used there gives nothing at r >= 8.

What the premise does not contain: no random-polynomial model, no independence of different centres (they are independent because the program draws them from independent random words), no statement about the number of roots beyond the two moments of 9.2.

### 9.2 The reduction to explicit constants, and the success bound

For `c` uniform in `F_p` write `E[.]` for the mean over `c`.

(a) *Squares.* For `t != 0` the values `t` and `-t` give the same `S = t^2` and different points `(c, t)`, so `E[k] = N* / (2p)` with `N* = #{ (c, t) : t != 0, G(c, t) = 0 }`.

(b) *First moment.* Put `d = D - 1`. By the first part of the premise, `G = 0` has an absolutely irreducible component `C_1` defined over `F_p`, of degree at most `d`. Weil's bound for the normalisation of `C_1` (genus at most `(d-1)(d-2)/2`), the count of the singular points of the plane model (at most `(d-1)(d-2)/2`, each with at most `d` branches) and the at most `d` points at infinity give `|#C_1(F_p) - p| <= (d-1)(d-2) sqrt(p) + d (d-1)(d-2)/2 + 2 d + 1`. The points with `t = 0` (at most `d`, since `G(c, 0) = F'(c)` has degree `d`) are inside the term `2d`; further rational components of `G = 0` only add points. Hence `E[k] >= 1/2 - e_1` with `e_1 = ((d-1)(d-2) (2^127 + 1) + d (d-1)(d-2)/2 + 2d + 1) / (2p)` (`sqrt(p) < 2^127 + 1`); `e_1 < @@E1@@` at r = @@R@@.

(c) *Second moment.* `k(k-1)` counts ordered pairs of distinct usable squares; each pair lifts to 4 points `(s_1, s_2)` by independent signs, and `s_1^2 != s_2^2` is the open condition that defines `V`. So `E[k(k-1)] <= #V(F_p) / (4p)` (the closure only adds points). By the second part of the premise `V` is a curve; it lies in the intersection of the surfaces `G(c, s_1) = 0` and `G(c, s_2) = 0` of degree `d` each. The two surfaces have no common component (a common component would be a factor `h(c)` of `G(c, t)`, but as a polynomial in `c` the leading coefficient of `G` is `D f_D(0)`, independent of `t` and nonzero), so the intersection is a curve of degree `d^2` and `V`, a part of it, has degree at most `delta = d^2` (the two diagonal curves `s_2 = +-s_1` of the intersection are not in `V`, and removing them only lowers the degree). A curve of degree `delta` has geometric genus at most `(delta-1)(delta-2)/2` (project to a plane). For a union of components of total degree `delta`, an absolutely irreducible component defined over `F_p` has at most `p + 1 + (delta_i-1)(delta_i-2) sqrt(p) + (delta_i-1)(delta_i-2)/2` rational points (Weil's bound for its normalisation, plus at most one point per singular point of the plane model), and these terms sum to at most the same expression with `delta` in place of `delta_i`; an `F_p`-component that is not absolutely irreducible has all its rational points on two conjugate components, at most `delta^2` points in all. With at most `w` absolutely irreducible components over `F_p`, `#V(F_p) <= w (p + 1) + (delta-1)(delta-2) sqrt(p) + (delta-1)(delta-2)/2 + delta^2`. Hence `E[k(k-1)] <= w/4 + e_2` with `e_2 = (w + (delta-1)(delta-2) (2^127 + 1) + (delta-1)(delta-2)/2 + delta^2) / (4p)`; `e_2 < @@E2@@` at r = @@R@@.

(d) *Cauchy-Schwarz.* `(E[k])^2 = (E[k 1_(k >= 1)])^2 <= E[k^2] P(k >= 1)` and `E[k^2] = E[k] + E[k(k-1)]`, so `P(k >= 1) >= a^2 / (a + b)` with `a = E[k]` and `b = E[k(k-1)]`. The right side increases in `a` and decreases in `b`, so its minimum over `a >= 1/2 - e_1`, `b <= w/4 + e_2` is at the corner: `P(k >= 1) >= (1/2 - e_1)^2 / (1/2 - e_1 + w/4 + e_2) = @@Q_CS@@`.

(e) *The cap `DMAX`.* `k >= DMAX + 1` implies `k(k-1) >= (DMAX+1) DMAX = @@DD1@@`, so by Markov `P(k > DMAX) <= (w/4 + e_2) / @@DD1@@ = @@TAIL@@`. Therefore, for `c` uniform, the event `E_c : 1 <= k(c) <= DMAX` has probability at least `q = @@Q_CS@@ - @@TAIL@@ = @@Q_EXACT@@`; the entry uses `q = @@Q@@`.

(f) *Centres and isolation.* The program draws its centres `c_1, ..., c_K` from independent random words by the rule of 4.1.1; each is within statistical distance `eps_coin < 2^-65` of uniform (the exact value is @@EPS_COIN@@), and the draws are independent. If `E_(c_t)` holds, the isolation of stage E fails with probability at most `eps_iso = @@EPS_ISO@@ < 2^-48` over words that are fresh for that stage (lemma 9.4). A trial with `E_(c_t)` and a successful isolation ends in a verified collision (sections 2-5). Therefore

`P[no collision in K trials] <= (1 - q)^K + K (eps_coin + eps_iso)`,

and, given the premise,

`P[success] >= 1 - (1 - q)^K - K (eps_coin + eps_iso) = @@P_SUCC_EXACT@@ >= @@P_SUCC@@`, with `q = @@Q@@`, `K = @@K@@`, `w = @@W@@`.

The probability is over the program's random words for the fixed target. It is not a probability over targets and not a sampled frequency, and no run of this program at r = @@R@@ enters it. The arithmetic of (b)-(f) is recomputed with exact rationals by the script of Appendix D, which prints every number used here. If only `k >= 1` were required (no cap `DMAX` in the program), the same arithmetic would give @@P_NOTAIL@@ for two centres.

### 9.3 Sensitivity

The premise has the parameter `w`. With the same constants: `w = 1`: `P(k >= 1) >= @@W1_QCS@@`, success @@W1_SUCC@@; `w = 2` (this entry): @@W2_QCS@@ and @@W2_SUCC@@; `w = 3`: @@W3_QCS@@ and @@W3_SUCC@@, which is below 0.39 at `K = 2` (it would need `K = 3`, success @@W3_K3@@, at about 0.585 more bit of time). If instead the true good fraction `q'` of centres (the probability of `E_c`) is what the premise would give, the success at `K` centres is `1 - (1 - q')^K` (the terms `K (eps_coin + eps_iso)` are below `10^-14`):

| `q'` | K=1 | K=2 | K=3 | K=4 |
|---:|---:|---:|---:|---:|
@@SENS_ROWS@@

The smallest `q'` for which `K` centres give 0.39 is @@QMIN_K1@@ for K=1, @@QMIN_K2@@ for K=2, @@QMIN_K3@@ for K=3 and @@QMIN_K4@@ for K=4. The time bound is `T_fixed + K T_trial` with `T_fixed` much smaller than `T_trial`, so `K'` centres instead of `K` cost about `log2(K'/K)` more in `time_log2`. With the submitted `K = @@K@@` the good fraction can be smaller than `q` by the factor `@@Q_RATIO_K@@` (down to `q' = @@Q_MIN_K@@`) before the bound falls below 0.39.

### 9.4 Lemma (isolation), proved

**Lemma.** Let `G` be monic of degree `d` with `2 <= d <= DMAX`, a product of `d` distinct linear factors over `F_p`. In one round of 4.1.2 (a uniform `a`), with probability at least `(p-1)/(2p)` both `G_+` and `G_-` are nonconstant, and then the kept part has degree at most `floor(d/2)`. The degree never increases. Hence after `Z` rounds the probability that `deg G >= 2` remains is at most `P[Bin(Z, (p-1)/(2p)) <= ceil(log2 DMAX) - 1]`, which for `DMAX = @@DMAX@@`, `Z = @@Z@@` equals at most @@EPS_ISO@@ (the exact sum below).

*Proof.* Let `u != v` be two roots of `G`, `chi` the quadratic character on `F_p`. In a round the roots of the shifted `G` are `r + a`. If `a` is not `-u`, not `-v`, and `chi(u+a) != chi(v+a)`, then exactly one of `u+a`, `v+a` is a nonzero square and the other a nonsquare; so `(u+a)^((p-1)/2) = 1` for one and `-1` for the other, one root lies in `G_+` and the other in `G_-` (a root of the shifted `G` is a root of `Z^((p-1)/2) - 1` iff its character is `+1`, of `Z^((p-1)/2) + 1` iff it is `-1`). Both parts are then nonconstant, their degrees sum to at most `d`, and the smaller has degree at most `floor(d/2)`. The number of `a` with `chi(u+a) chi(v+a) = -1`: `sum_(a != -u,-v) chi((a+u)(a+v)) = -1`, because the quadratic `a^2 + (u+v) a + uv` has nonzero discriminant `(u-v)^2` (the standard evaluation of a quadratic character sum), so the count of `a` outside `{-u,-v}` with product `-1` is `((p-2) + 1)/2 = (p-1)/2`. The probability is `(p-1)/(2p)`. A part is always a divisor of `G`, so the degree is nonincreasing whatever happens in a round that is not of this kind. Conditional on any history of earlier rounds, the next `a` is fresh and uniform, so every round is of this kind with probability at least `w = (p-1)/(2p)`, and at most `ceil(log2 DMAX)` such rounds bring `d <= DMAX` to 1 (16 -> 8 -> 4 -> 2 -> 1). The failure probability is at most `P[Bin(Z, w) <= ceil(log2 DMAX) - 1] = sum_(j <= 3) C(64, j) w^j (1-w)^(64-j) = @@EPS_ISO@@`, computed exactly in Appendix D. This is a proved bound under the random words of the program, not a premise and not a sample.

