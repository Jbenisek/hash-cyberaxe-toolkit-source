## 10. Evidence

This section is the evidence for the premise `H-GEOM-w@@W@@` and for the digest of the target. The executions of 10.1 and the computations of 10.3 are ours; the experiment of 10.2 is run by the organizer's runner. None of it enters `success_probability` or the bound of section 9, and none is a lower bound on the probability of `E_c`.

### 10.1 Executed full-scale outcomes at r = 3, 4, 5

| run | degree of F | m | centres tried (in order) | outcome per centre (`deg G`) | successes | operations N (executed) | time_log2 | memory (bytes) | threads, wall |
|---|---:|---:|---|---|---:|---:|---:|---:|---|
| r = 3, earlier program | 5^9 | 976,562 | 1 (fixed) | c=1: 1 | 1 | 317,054,280,703 | 30.08182 | 250,386,180 | 1 thread, 3,202.9 s |
| r = 4, earlier program | 5^10 | 4,882,812 | 1, 2 (fixed) | c=1: 0 (no usable root); c=2: 1 | 1 | 3,992,419,235,666 | 33.63159 | 1,231,371,140 | 6 threads, 13,030.2 s |
| r = 5, earlier program | 5^11 | 24,414,062 | 1 (fixed) | c=1: 1 | 1 | 9,205,778,231,873 | 34.73925 | 5,604,188,884 | 13 threads, 22,048.3 s |

These are the executed entries of the same construction with the centres 1, 2, ... in place of coin draws (their operation counts are the instrumented totals of those runs, thread charges included). Usable roots appeared at three of the four centres tried; each run stops at its first success.

The collisions found (each is a pair of distinct canonical `(nk, rho)` with equal digests at its own round count, accepted by the organizer's digest function when the entry was filed):
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

### 10.2 The organizer experiment declared in `experiments/manifest.json`

One experiment, `lowbits-birthday` (`experiments/exp_lowbits.py`, kind `python-message-pairs-v1`, event `digest-xor-mask` with mask `fffc` followed by 30 zero bytes and expected value zero). For each organizer trial the program searches at most 1200 fresh inputs derived from the trial seed for two distinct canonical messages whose digests of the selected target `poseidon-orchard-r@@R@@-prefix-v1` agree in the first 14 bits of the big-endian reading, and returns the pair (or two nulls). Its source is 15,748 bytes (the limit for experiment sources is 65,536). Its event is a reduced one on the digest of the selected target: the program computes its candidates with its own copy of the permutation (constants embedded), and a returned pair counts only if the organizer's callback gives digests that agree in those 14 bits, so a pair is accepted only when that copy agrees with the target. The digest map so checked is the map whose line polynomial `F` the premise concerns.

@@EXECUTOR_STATUS_SENTENCE@@

### 10.3 Computed theorems for the generic line (Grok, job 135)

Grok (xAI), our research partner, computed the hypothesis of `H-GEOM-w` exactly over the Pallas field for a toy permutation, by exact computation (the cycle types, factorisations and leading coefficients below are the printed results): width 3, S-box `x -> x^5`, `M = [[2,1,1],[1,2,1],[1,1,2]]` (every minor nonzero mod `p`), round `i` adds the constants `(3i+1, 3i+2, 3i+3)`, every round full, output coordinate 0, on the generic line `(L, 2L+1, 3L+5)`. Notation as in 9.1: `D = deg F`, `G(c,t) = (F(c+t) - F(c-t))/(2t) = H(c, t^2)`, `m = (D-1)/2`; the cycle types below are those of `H(c, u)` (or of `F(x) - a`) at the stated values over `F_p`, which by Dedekind give elements of the arithmetic monodromy.

* **Theorem A (one full round).** `D = 5`. The curve `G = 0` is absolutely irreducible (`F'` has 4 simple roots, so `u` is not a square in the function field); the cycle types of `F(x) - a` at `a = 8, 1, 5` are `(5)`, `(4,1)`, `(2,1,1,1)`, so the arithmetic monodromy is `S_5`. The pair scheme `G(c,s1) = G(c,s2) = 0` is geometrically reduced and of pure dimension 1, and its part off `s1^2 = s2^2` has exactly one absolutely irreducible component defined over `F_p`: the resultant in `c` of `G(c,s1)` and `G(c,s2)` is a constant times `(s1-s2)^4 (s1+s2)^4 Phi(s1,s2)` with `Phi` of degree 8, and `Phi` is irreducible at specialisations of `s1` over `F_(p^k)` for `k = 2, 4, 8`, hence absolutely irreducible. So the hypothesis holds with `w = 1`, with no further assumption.
* **Theorem B (two full rounds).** `D = 25`, `deg H = 12`. The cycle types of `H(c,u)` at `c = 1, 9, 103` are `(12)`, `(11,1)`, `(7,1,1,1,1,1)`; a 12-cycle, an 11-cycle and a 7-cycle (7 is prime and at most 12 - 3) give, by Jordan's theorem, `A_12` inside the arithmetic monodromy, and the 12-cycle is odd, so it is `S_12`; the geometric monodromy is `A_12` or `S_12`, both 2-transitive. Hence `G = 0` is absolutely irreducible, the pair scheme is geometrically reduced of pure dimension 1, and the off-diagonal scheme `{H(c,u1) = H(c,u2) = 0, u1 != u2}` in the coordinates `(c, u1, u2)` is absolutely irreducible.
* **Theorem D (degrees).** For every `N <= 17` rounds and every listed line and schedule, the output coordinate has degree exactly `5^N` over `F_p` (the leading coefficient is an integer, nonzero mod `p`). This is the fact of section 2.3 (`deg F = D`) for the toy.
* The axis line `(L, 0, 0)` is a different case (Theorem C): there `F = R(X + c0)^5` is decomposable, its geometric monodromy is imprimitive, and the hypothesis fails (`w = 0`). The theorems above are for the generic line.

Our line is generic in this sense. The polynomial that the construction of section 2 produces is dense: in our miniature runs (`p` of 20 and of 24 bits, `r` up to 4, run twice with identical digests of the coefficient vectors) every coefficient of the digest polynomial in `W` is nonzero up to the 0 to 2 zeros expected of a random polynomial, each residue of the exponent modulo 5 and modulo 25 carries its fair share, and the polynomial `g` that the algorithm builds is dense likewise. This is evidence for `H-GEOM-w@@W@@` at one and two rounds on a generic line, with the group-theoretic certificate (an `m`-cycle, an `(m-1)`-cycle and a prime cycle of length at most `m - 3`) that proves it for any further explicit `F` it is computed for.

### 10.4 Scope

One trial at r = @@R@@ needs @@TRIAL_MEM@@ of live memory and @@TRIAL_WORK@@. The claim is the premise `H-GEOM-w@@W@@` with the reduction of section 9.2; the executed centres at r = 3, 4, 5, the experiment of 10.2 and the theorems of 10.3 are the evidence for it.
