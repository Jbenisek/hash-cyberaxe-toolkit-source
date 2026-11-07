# poseidon-orchard-r23: birthday search, one trail with distinguished points

Method: the textbook collision search (Pollard rho with distinguished points, van Oorschot-Wiener) on the Orchard hash with 23 partial rounds. The accounting, the single-trail recovery and the success lemma are our own. No other participant's program was used or run. Claim: time_log2 = 127.020, memory below 1 MiB (1,020,704 bytes, claimed 2^20), success probability 0.39, no preprocessing, no advice. The attack is generic: it uses no property of the rounds.

## 1. Target and walk

Target `poseidon-orchard-r23-prefix-v1`: input two canonical elements (m0, m1) of the Pallas base field, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (N = p, about 2^254); initial state [m0, m1, 2^65]; rounds 0-3 full, 4-26 partial, 60-63 full (constants and MDS as deployed); digest = state[0], the complete element compared. Unit: one call of the permutation; C(23) = 216 + 21 * 23 = 699 primitive operations.

Walk. The attempt draws two coins, rho0 and x_0, each the low 254 bits of a uniformly random 256-bit word (every 254-bit word is below p, so both are canonical). It iterates F(x) = digest(x, rho0): x_i = F(x_{i-1}). The output of F is a canonical field element, so it is again an admissible first input. Two inputs (x, rho0) and (y, rho0) with x != y and F(x) = F(y) are a collision of the target.

## 2. The program (Appendix B `rho.py`: `attack`, `search`, `plan`)

1. Coins: rho0, x_0 (two random words, two ANDs).
2. Loop for i = 1 .. S: state := [x, rho0, 2^65] (coordinate 1 already holds x, the digest of the previous call; coordinates 2 and 3 are set: 2 operations), one permutation call, x := state[0]. If x mod 2^128 < T (T = 27554) x is a distinguished point (DP): the table is scanned (Section 6); if x is already stored the trail has closed: go to 3; otherwise store (x, i). If the table already holds MCAP = 15,500 DPs, halt (failure). After S steps, halt (failure).
3. Recovery. The repeat is x_b = x_a (b = i, a its stored index), L = b - a. Let (s, x_s) be the entry stored just before a (the start x_0 at index 0 if none). Compute x_{s+L} from the nearest stored point at or before s + L (bisection on the stored indices, then at most gmax evaluations, else halt). If x_s = x_{s+L} halt (start on the cycle). Then iterate both from (x_s, x_{s+L}) in lockstep; the first time F(A) = F(B) return (A, B); after gmax rounds halt.

Parameters (integers, `python3 rho.py --plan`, Appendix A): S = n + d, n = 169483031945336737308724230378684940288 (= 133698538 * 2^100, log2 126.9944), d = 98811576601361441296079740815032512, gmax = 222326047353063242916179416833823151, MCAP = 15,500.

## 3. Correctness of the recovery (deterministic)

Let t be the least index with x_t = x_j for some j < t, mu = j, lambda = t - mu. For i >= mu, x_i = x_{i+lambda}. A repeated DP is found at b = a' + lambda where a' is the first DP with index at least mu: DPs with index in [t, a' + lambda) repeat values of x_mu .. x_{a'-1}, which hold no DP; so a = a' and L = lambda. The entry stored before a is a DP with index < mu or the start, so s < mu <= a, or s = 0 = mu (halt: start on the cycle). With s < mu, x_s != x_{s+L} and the least m >= 1 with x_{s+m} = x_{s+m+L} is m = mu - s <= a - s, so the lockstep stops within a - s rounds and returns (x_{mu-1}, x_{mu-1+L}): distinct, with equal F. All of s, a and q = s + L are below t. The recovery uses at most gmax + 2 gmax = 3 gmax evaluations when every gap between consecutive stored points below t is at most gmax.

## 4. Success probability for a uniformly random function

In this section F is a uniformly random function on the N field elements (lazy sampling) and x_0 is any fixed element: every statement holds conditionally on the start. D = (2^126 + 1) T is the exact number of DPs in the field (p = 2^254 + c with c = p mod 2^128 >= T), theta = D / N = 2^-113.25003. Every index used below is at most S < SMAX = 2^128. Write theta_lo = (D - 2^128) / N and theta_hi = D / (N - 2^128).

Lemma 1. (i) Given x_0 .. x_i with no repeat, x_{i+1} is uniform on the field, so it repeats one of the i + 1 earlier values with probability (i + 1) / N. (ii) Given x_0, t and mu, the sequence x_1 .. x_{t-1} is uniform over all sequences of t - 1 distinct elements different from x_0: every such sequence together with the event x_t = x_mu has probability N^-t. (iii) Hence for 1 <= j < t, given x_0, t, mu and x_1 .. x_{j-1}, the value x_j is uniform over the N - j unused elements, of which D - k are DPs with k <= j; so theta_lo <= P(x_j is a DP | x_0, t, mu, x_1 .. x_{j-1}) <= theta_hi.

Proof of (iii): (D - k) / (N - j) >= (D - j) / N >= theta_lo and (D - k) / (N - j) <= D / (N - j) <= theta_hi, as j < 2^128. The bound conditions on every earlier value, including the DP status of earlier points, so it applies after a stored point as well.

Lemma 2. With n, d = ceil(8 / theta_lo), gmax = ceil(18 / theta_lo), S = n + d and MCAP = 15,500, the attempt succeeds with probability at least 0.39.
(a) Trail: P(t > n) = prod_{i<n} (1 - (i + 1)/N) <= exp(-n (n + 1) / 2N) by (i). The start lies on the cycle (mu = 0) with probability at most 1/N at each step: n / N in all.
(b) Detection: given x_0, t <= n, mu and lambda >= d, the d values x_mu .. x_{mu+d-1} (all below t) contain no DP with probability at most (1 - theta_lo)^d <= exp(-theta_lo d) <= e^-8, by (iii) in increasing order. A DP at a' among them gives b = a' + lambda <= t + d - 1 < S. P(lambda < d, t <= n) <= n d / N (at each t <= n and each lambda < d, x_t = x_{t-lambda} has probability at most 1/N).
(c) Table: the stored DPs lie below t (Section 3); by (iii) their number is dominated by Binomial(S, theta_hi), mean mu_S = S theta_hi = 13731.71, so P(more than MCAP) <= exp(-mu_S) (e mu_S / (MCAP + 1))^(MCAP + 1) = e^-109.38 <= e^-100.
(d) Gaps: a stored point at position i < t followed by gmax positions below t with no DP has probability at most P(x_i is a DP) exp(-theta_lo gmax) by (iii); summed over i, with the start: (S theta_hi + 1) e^-18.
Total: success >= 1 - exp(-n (n + 1) / 2N) - n / N - eps, eps = e^-8 + n d / N + (S theta_hi + 1) e^-18 + e^-100 = 1.1231e-3. `plan` evaluates this in 80-digit decimal arithmetic: 0.390000002301729877 >= 0.39; n is the least multiple of 2^100 that reaches 0.39. One attempt: no restart, no amplification, no advice.

## 5. Operation ledger (unit: target compressions; C = 699)

Machine: the Pallas field RAM of `orchard-cost-v2.json` with 256-bit words. A call of the reference permutation is 1 unit and pays for its own arithmetic, constants and loads; every other word operation (add, AND, shift, compare, branch, register move, assignment, aligned 256-bit load or store) is 1/699. The permutation transforms its three-word state (registers s0, s1, s2) in place. The loops as executed (register names; CAP holds 2^65, M holds 2^128 - 1, ENDP is the table end pointer):

Trail step, 9 operations + 1 call (W_STEP = 9):
```
loop: ADD   i, i, 1          ; step counter
      MOV   s1, rho0         ; state coordinate 2
      MOV   s2, CAP          ; state coordinate 3   (s0 already holds x)
      CALL  PERM             ; 1 unit
      MOV   x, s0
      AND   u, x, M
      CMPLT f, u, T
      BR    f, dp            ; to the table scan
      CMPLT g, i, S
      BR    g, loop
```
Recovery: the walk to x_q costs 5 operations per evaluation (ADD, MOV s1, MOV s2, CALL, CMPLT, BR); a lockstep round of two evaluations costs 15 (ADD j; MOV s0, A; MOV s1; MOV s2; CALL; MOV nA, s0; the same four moves for B; CMPEQ nA, nB; BR; MOV A, nA; MOV B, nB; CMPLT j, GMAX; BR): at most 7.5 per evaluation. Charged W_REC = 10 per evaluation for at most 3 gmax evaluations.
Table scan, 6 per entry examined (W_SCAN): LOAD v, [p]; CMPEQ v, x; BR; ADD p, p, 64; CMPLT p, ENDP; BR. Insertion, 3 (W_INS): STORE [ENDP], x; STORE [ENDP + 32], i; ADD ENDP, ENDP, 64. Bisection probe, 11 executed, 12 charged (W_PROBE): ADD, ADD 1, SHR, SHL 6, ADD base, LOAD [a + 32], CMPLE, BR, MOV or SUB, CMPLT, BR.
Fixed part: at most MCAP + 1 DP events, each scanning at most MCAP + 1 entries and inserting once; one bisection of at most 15 probes; MISC = 2000 for the coins, masks, constants, halts and report: OTHER_FIXED = (MCAP + 2)(6 (MCAP + 1) + 3) + 15 * 12 + 2000 = 1,441,827,698 operations.

Total (every halt charged at its limit): T = S (1 + 9/699) + 3 gmax (1 + 10/699) + OTHER_FIXED / 699 = 1.7244182e+38 units, log2 T = 127.019377; claimed 127.020 (rounded up). `python3 rho.py --selftest` runs the search at width 14 and checks that its counted operations stay below this formula for its parameters.

## 6. Memory and the table

The table is one array of 64-byte entries, each two aligned 256-bit words: the value x (a canonical field element) and the index i (< 2^128). Entry 0 is the start (x_0, 0); entries 1 .. are the DPs in increasing index order, so the bisection runs on the array itself. Nothing else is stored: no hash table, no second index, no per-entry metadata. `rho.py` keeps the same array (`pts`) and the same scan (`lookup`).
Bytes: (MCAP + 2) * 64 = 992,128 for the table; at most 600 instructions at 36 bytes (256-bit immediates) = 21,600 for code; 192 round constants, 9 MDS entries and the capacity at 32 bytes = 6,464; at most 16 registers = 512. Total 1,020,704 <= 2^20 = 1,048,576: the memory term of the score is 0 (with twice the code bytes the total is 1,042,304, still below 2^20).

## 7. Premise H1 and its evidence

H1 (claim.json `H1-random-function-model`), the only premise of the claim.
- Statement: for the attempt's coins rho0 and x_0 (uniform 254-bit words), the search of Section 2 on the real map F(x) = digest(x, rho0) succeeds with probability at least P_F, the success probability of the same search on a uniformly random function, which Lemma 2 bounds by P_F >= 0.390000002. This is an assumption; no proof is known.
- Role: score-critical. It is the only step from Lemma 2 to the claimed success probability; the recovery (Section 3), the ledger (Section 5) and the memory (Section 6) are proved.
- Scope: target poseidon-orchard-r23-prefix-v1, inputs (x, rho0), one trail with the parameters of Section 2 (S = 1.70e38 evaluations). Not claimed for other round counts or budgets.
- Limitations: the evidence below is measured on outputs truncated to 16 to 40 bits, on trails of at most 4,013,103 steps; the 254-bit map over 2^127 steps cannot be observed, so the transfer to full width is the premise itself.

Evidence: measurements of the real map at r = 23. Our own code (Appendix C, with our C field library; `rho.py`'s `digest` equals the organizer's `verifier/poseidon.py` digest on 24 of 24 inputs at r = 23, and the organizer digest confirms all 10319 of the 10319 pairs the runs returned: distinct messages (A, rho), (B, rho) whose digests agree in the low w bits). Each measurement was run twice, run A and run B, on disjoint functions and starts (32 minutes in all). The measurements are evidence for H1 only: no parameter of the attempt is taken from them.
- Map at width w: F_w(v) = low w bits of digest(v, rho), v in [0, 2^w). Each trial draws its own rho (the function index) and start, as the attempt draws rho0 and x_0. The walk runs until its first repeat, with every value kept, giving the exact t (first repeat), mu and lambda of Section 3.
- Collision rate: for a random function on N = 2^w points, P(t > n) = prod_{i<=n} (1 - i/N), so t^2 / 2N is exponential with mean 1. The hazard multiplier c = K / sum(t^2 / 2N) estimates the factor on the collision rate (c = 1 for a random function; 95% interval from the Gamma law of the sum).
- Distinguished points at density theta = 2^10 / 2^(w/2) (low w/2 bits below 2^10; 1/16 at w = 16, 20): theta times the mean gap between consecutive DPs (1 for a random function) and theta times the mean detection delay a' - mu over walks with lambda > 20 / theta (1 - theta for a random function).
- The full search (`search` of Section 2, with Lemma 2 parameters computed by the same formula for N = 2^w, D = 2^(w/2+10), SMAX = 2^(w/2+3), at widths 24 to 40): the fraction of runs that return a verified pair, against the Lemma 2 bound for that width.
- Control: the same program on a keyed pseudo-random function (splitmix64), five times as many trials per width.

| w | trials A + B | c run A / run B | c pooled [95%] | control c [95%] | success run A / run B (pooled, [95%]) | Lemma 2 bound | theta x mean DP gap | theta x mean detection delay | largest DP gap / gmax |
|---|---|---|---|---|---|---|---|---|---|
| 16 | 2000 + 2000 | 0.981 / 0.970 | 0.975 [0.945, 1.006] | 1.000 [0.987, 1.014] | - | - | 0.955 | 0.929 | - |
| 20 | 2000 + 2000 | 1.020 / 1.028 | 1.024 [0.993, 1.056] | 0.995 [0.981, 1.008] | - | - | 0.987 | 0.920 | - |
| 24 | 2000 + 2000 | 1.014 / 1.013 | 1.013 [0.982, 1.045] | 0.996 [0.982, 1.010] | 0.415 / 0.406 (1644/4000, [0.396, 0.426]) | 0.3900 | 0.999 | 0.733 | 54 / 73 |
| 28 | 600 + 600 | 0.954 / 1.089 | 1.017 [0.961, 1.076] | 0.996 [0.971, 1.022] | 0.392 / 0.417 (485/1200, [0.377, 0.432]) | 0.3900 | 0.999 | 0.897 | 211 / 291 |
| 32 | 200 + 200 | 0.991 / 0.956 | 0.973 [0.880, 1.071] | 1.023 [0.978, 1.068] | 0.425 / 0.445 (174/400, [0.387, 0.484]) | 0.3900 | 0.999 | 1.102 | 1029 / 1162 |
| 36 | 60 + 60 | 1.099 / 0.838 | 0.951 [0.789, 1.129] | 1.031 [0.951, 1.115] | 0.417 / 0.283 (42/120, [0.271, 0.439]) | 0.3900 | 1.003 | 1.125 | 2984 / 4645 |
| 40 | 12 + 12 | 1.673 / 0.632 | 0.918 [0.588, 1.320] | 1.034 [0.857, 1.227] | 0.583 / 0.333 (11/24, [0.279, 0.649]) | 0.3900 | 0.997 | 1.100 | 11466 / 18578 |

Regime and result: in 13 of the 14 run-and-width cells the 95% interval of the hazard multiplier contains 1; the exception (run B, w = 28: c = 1.089 [1.004, 1.178]) lies above 1, on the side of more collisions, and one exclusion in 14 is what 95% intervals give by chance. Pooled over 13744 walks it is 1.004, 95% interval [0.987, 1.020]. The weighted slope of log c against width is +0.0016 per bit (standard error 0.0019): no trend is detected. The search succeeded in 2356/5744 = 0.410 of its runs at widths 24 to 40, against a mean Lemma 2 bound of 0.3900. DP gaps follow the geometric law the lemma uses (theta x mean gap 0.997 to 1.003 at widths 24 to 40), and no gap of these Orchard runs reached gmax.
Extrapolation: from widths 16 to 40, where c is measured, to width 254, by H1. The measurements show the rate law that Lemma 2 uses on the real round function at the claimed round count. They do not bound c at full width.
Sensitivity: if the true collision rate is c / N per earlier value with c = 1 - e, the same success needs n larger by c^(-1/2), that is 0.5 log2(1/c) bit of time: 0.0072 bit for e = 0.01, 0.0370 for e = 0.05, 0.076 for e = 0.10. At the lower end of the measured interval (c = 0.987) the price is 0.0097 bit.
Why the attempt draws rho0: on one fixed map the success over starts alone depends on that map's longest cycle. For the rho = 0 map we measured 0.130, 0.615 and 0.375 at widths 24, 28 and 32. For 80 fixed pseudo-random maps at width 24 (40 per run, 200 starts each) the per-map fractions ranged from 0.005 to 0.920 (standard deviation 0.26 and 0.18 in the two runs). Drawing rho0 as a coin makes the attempt's probability an average over maps, which is what Lemma 2 bounds.

## 8. Experiments

None are declared. The organizer runner's Python path calls `digest_fn(b"")` to size the digest (`experiments/runner.py`), and the Orchard digest rejects any input other than two 32-byte encodings, so a declared Poseidon experiment fails before its program runs. The measurements of Section 7 were run with our own code (Appendix C), and their data are in Appendix D.


## Appendix A: `python3 rho.py --plan`

theta 8.097392835639327e-35; theta_log2 -113.2500258511542; n 169483031945336737308724230378684940288; n_over_2^100 133698538; d 98811576601361441296079740815032512; gmax 222326047353063242916179416833823151; eps_total 0.001123127200352159; steps 169581843521938098750020310119499972800; T_units 1.7244182076717042e+38; time_log2 127.0193773064612; mean_stored_bound 13731.70804789051; ln_P_table_overflow -109.38155622143495; n_log2 126.99440844867615; success_lower_bound 0.3900000023017299; success_lower_bound_decimal 0.390000002301729877; other_fixed 1441827698; W_STEP 9; W_REC 10; memory_bytes 1020704

## Appendix B: the program and its ledger, `rho.py` (verbatim, standard library only; `--plan` prints the parameters and the ledger)

```python
"""Generic collision search on the Orchard hash with 23 partial rounds: one trail of x -> digest(x, rho0) for a random rho0, distinguished points, one table.

Target: poseidon-orchard-r23-prefix-v1 (initial state [x, 0, 2^65], 8 full + 23 partial rounds, digest = state[0], no feed-forward).
Sections: 1 deployed constants (halo2_poseidon 0.2.0, copied from our own checked file), 2 the hash, 3 the search (`search`),
4 parameters and ledger (`plan`, `python3 rho.py --plan`), 5 small self-checks and command line.
No outside code or library is used; standard library only.
"""
import sys
import json
import hashlib
from math import log, log2, exp, sqrt, ceil
from decimal import Decimal, getcontext

# ================================================================ 1 constants
P = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001
ROUND_CONSTANTS = (
    (0x360d7470611e473d353f628f76d110f34e71162f31003b7057538c2596426303, 0x2bab94d7ae222d135dc3c6c5febfaa314908ac2f12ebe06fbdb74213bf63188b, 0x150c93fef652fb1c2bf03e1a29aa871fef77e7d736766c5d0939d92753cc5dc8),
    (0x3270661e68928b3a955d55db56dc57c103cc0a60141e894e14259dce537782b2, 0x073f116f04122e25a0b7afe4e2057299b407c370f2b5a1ccce9fb9ffc345afb3, 0x2a32ec5c4ee5b1837affd09c1f53f5fd55c9cd2061ae93ca8ebad76fc71554d8),
    (0x270326ee039df19e651e2cfc740628ca634d24fc6e2559f22d8ccbe292efeead, 0x27c6642ac633bc66dc100fe7fcfa54918af895bce012f182a068fc37c182e274, 0x1bdfd8b01401c70ad27f57396989129d710e1fb6ab976a459ca18682e26d7ff9),
    (0x162a14c62f9a89b814b9d6a9c84dd678f4f6fb3f9054d373c832d824261a35ea, 0x2d193e0f76de586b2af6f79e3127feeaac0a1fc71e2cf0c0f79824667b5b6bec, 0x044ca3cc4a85d73b81696ef1104e674f4feff82984990ff85d0bf58dc8a4aa94),
    (0x1cbaf2b371dac6a81d0453416d3e235cb8d9e2d4f314f46f6198785f0cd6b9af, 0x1d5b2777692c205b0e6c49d061b6b5f4293c4ab038fdbbdc343e07610f3fede5, 0x2e9bdbba3dd34bffaa30535bdd749a7e06a9adb0c1e6f962f60e971b8d73b04f),
    (0x2de11886b18011ca8bd5bae36969299fde40fbe26d047b05035a13661f22418b, 0x2e07de1780b8a70d0d5b4a3f1841dcd82ab9395c449be947bc998884ba96a721, 0x0f69f1854d20ca0cbbdb63dbd52dad16250440a99d6b8af3825e4c2bb74925ca),
    (0x2eb1b25417fe17670d135dc639fb09a46ce5113507f96de9816c059422dc705e, 0x115cd0a0643cfb988c24cb44c3fab48aff36c661d26cc42db8b1bdf4953bd82c, 0x26ca293f7b2c462d066d7378b999868bbb57ddf14e0f958ade801612311d04cd),
    (0x17bf1b93c4c7e01a2a830aa162412cd90f160bf9f71e967ff5209d14b24820ca, 0x35b41a7ac4f3c571a24f8456369c85dfe03c0354bd8cfd3805c86f2e7dc293c5, 0x3b1480080523c439435927994849bea964e14d3beb2dddde72ac156af435d09e),
    (0x2cc6810031dc1b0d4950856dc907d57508e286442a2d3eb2271618d874b14c6d, 0x25bdbbeda1bde8c1059618e2afd2ef999e517aa93b78341d91f318c09f0cb566, 0x392a4a8758e06ee8b95f33c25dde8ac02a5ed0a27b61926cc6313487073f7f7b),
    (0x272a55878a08442b9aa6111f4de009485e6a6fd15db89365e7bbcef02eb5866c, 0x2d5b308b0cf02cdfefa13c4e60e26239a6ebba011694dd129b925b3c5b21e0e2, 0x16549fc6af2f3b72dd5d293d72e2e5f244dff42f18b46c56ef38c57c311673ac),
    (0x1b10bb7a82afce39fa69c3a2ad52f76d76398265344203119b7126d9b46860df, 0x0f1e7505ebd91d2fc79c2df7dc98a3bed1b36968ba0405c090d27f6a00b7dfc8, 0x2f313faf0d3f6187537a7497a3b43f46797fd6e3f18eb1caff457756b819bb20),
    (0x3a5cbb6de450b481fa3ca61c0ed15bc55cad11ebf0f7ceb8f0bc3e732ecb26f6, 0x3dab54bc9bef688dd92086e253b439d651baa6e20f892b62865527cbca915982, 0x06dbfb42b979884de280d31670123f744c24b33b410fefd4368045acf2b71ae3),
    (0x068d6b4608aae810c6f039ea1973a63eb8d2de72e3d2c9eca7fc32d22f18b9d3, 0x366ebfafa3ad381c0ee258c9b8fdfccdb868a7d7e1f1f69a2b5dfcc5572555df, 0x39678f65512f1ee404db3024f41d3f567ef66d89d044d022e6bc229e95bc76b1),
    (0x21668f016a8063c0d58b7750a3bc2fe1cf82c25f99dc01a4e534c88fe53d85fe, 0x39d00994a8a5046a1bc749363e98a768e34dea56439fe1954bef429bc5331608, 0x1f9dbdc3f84312636b203bbe12fb3425b163d41605d39f99770c956f60d881b3),
    (0x027745a9cddfad95e5f17b9e0ee0cab6be0bc829fe5e66c69794a9f7c336eab2, 0x1cec0803c504b635788d695c61e932122fa43fe20a45c78d52025657abd8aee0, 0x123523d75e9fabc172077448ef87cc6eed5082c8dbf31365d3872a9559a03a73),
    (0x1723d1452c9cf02df419b848e5d694bf27feba35975ee7e5001779e3a1d357f4, 0x1739d180a16010bdfcc0573d7e61369421c3f776f572836d9dab1ee4dcf96622, 0x2d4e6354da9cc554acce32391794b627fafa96fbeb0ab89370290452042d048d),
    (0x153ee6142e535e334a869553c9d007f88f3bd43f99260621670bcf6f8b485dcd, 0x0c45bfd3a69aaa65635ef7e7a430b486968ad4424af83700d258d2e2b7782172, 0x0adfd53b256a6957f2d56aec831446006897ac0a8ffa5ff10e5633d251f73307),
    (0x315d2ac8ebdbac3c8cd1726b7cbab8ee3f87b28f1c1be4bdac9d36a8b7516d63, 0x1b8472712d02eef4cfaec23d2b16883fc9bb60d1f6959879299ce44ea423d8e1, 0x3c1cd07efda6ff24bd0b70fa2255eb6f367d2c54e36928c9c4a5404198adf70c),
    (0x136052d26bb3d373687f4e51b2e1dcd34a16073f738f7e0cbbe523aef9ab107a, 0x16c96beef6a0a848c1bdd859a1232a1d7b3cfbb873032681676c36c24ef967dd, 0x284b38c57ff65c262ab7fed8f499a9fb012387bab4f1662d067eec7f2d6340c4),
    (0x0c5993d175e81f6639e242198897d17cfc06772c1c0411a6af1dff204c922f86, 0x03bf7a3f7bd043dafcda655d1ba9c8f9f24887ad48e17759bbf53f67b1f87b15, 0x3188fe4ee9f9fafbb0cf999567f00e734c8f9cbe69f0e8279b5cd09e36d8be62),
    (0x171f528ccf6584375a39768c480d61e13af5bf77c1c42652afea99a2ec6c595a, 0x12f4175c4ab45afc196e41859b35ef88812c3286ee7000675a0563b9b8e9f1d5, 0x3a509e155cb7ebfd8f8fdcf800a9ac697e23e1aabe96cfab0e74d4d369118b79),
    (0x10f2a685df4a27c81a89920e2504c3b3984bc8f2e4c1b69e98712c65678cfd30, 0x09e5f49790c8a0e21d8d93d54ab91a0e54573c9333c56321e8a16728cc9d4918, 0x352d69bed80ee3e52bf35705d9f84a3442d17ed6ee0fab7e609a740347cf5fea),
    (0x058ee73ba9f3f293491562faf2b190d3c634debd281b76a63a758af6fa84e0e8, 0x232f99cc911eddd9cd0f1fc55b1a3250092cb92119bc76be621a132510a43904, 0x201beed7b8f3ab8186c22c6c5d4869f0f9efd52ca6bc2961c3b97c1e301bc213),
    (0x1376dce6580030c6a1c9291d58602f5129388842744a1210bf6b3431ba94e9bc, 0x1793199e6fd6ba342b3356c38238f761072ba8b02d92e7226454843c5486d7b3, 0x22de7a7488dcc7359fee9c20c87a67df3c66160dc62aacac06a3f1d3b433311b),
    (0x3514d5e9066bb160df8ff37fe2d8edf8dbe0b77fae77e1d030d6e3fd516b47a8, 0x30cd3006931ad636f919a00dabbf5fa5ff453d6f900f144a19377427137a81c7, 0x253d1a5c5293412741f81a5cf613c8df8f9e4b2cae2ebb515b6a74220692b506),
    (0x035b461c02d79d19a35e9613e7f5fe92851b3a59c990fafc73f666cb86a48e8e, 0x23a9928079d175bd5bc00eedd56b93e092b1283c2d5fccde7cfbf86a3aa04780, 0x13a7785ae134ea92f1594a0763c611abb5e2ea3436eef957f1e4ccd73fa00a82),
    (0x39fce308b7d43c574962ae3c0da17e313889c57863446d88bbf04f5252de4279, 0x1aae18833f8e1d3ac0fdf01662f60d22bef00a08c6ed38d23b57e34489b53fad, 0x1a761ce82400af018b2e80c064fd83ed27c1b3fd8f85d8a855513e033398513f),
    (0x275a03e45adda7c316dd1a87ca22e1ccdcf6af2830a502875244ca749b73e481, 0x2e5a10f08b5ab8bbeb08e47e5feabcf807e561453fc5648b58a253cfb6a95786, 0x1459cb8587208473b84e9c333b2932f1c141a5b6d594bec4e033d82cefe78ce3),
    (0x193ae5921d78b5de7b92ce810e14a40052f9332fbffcfbbd5cec7e7b338fbe1b, 0x3097898a5d0011a489111fb2c4660281374384f4a072820560224be67248e82c, 0x378d97bf8c864ae7571782fd96ce54b41979b2d1c465b4d9549980de862930f5),
    (0x2eb04ea7c01d97ec88136287ce376b08dbc7f5cb4609342137ea32a971d17884, 0x36425347ea03f6412302a1c22e49baec861cbda476804e6cead3726f1af2e7b0, 0x26b72df47408ad42cc996cd85c98a1d83f5b5ca5a19a9701ecd627e59590d09e),
    (0x130180e44e2924db1f05636c610b89aade01212ee4588f8959bece31f0a31e95, 0x219e97737d3979ba73275acaed5f579cdf7793cc89e5b52f9ea8e7bc79263550, 0x3cdb93598a5ca5283461363f81c489a23b0672dd7d42cbb49c12635df251d153),
    (0x0e59e6f332d7ed3720724b927a0ca81c4ad0447045a7c5aa2861ce16f219d5a9, 0x1b064342d51a42753d7369467222697a172cc07b9d33fbf943b0a3fcff2036bd, 0x30b82a998cbd8e8a2f363c55b2882e0b78fa9fb9171221b73eb310228a0e5f6c),
    (0x23e4ab37183acba463df7a76e858a4aa8ad71ea715be0573e46f6d4298740107, 0x2795d5c5fa4280225d33094e0beda75bacfe14640de044f2fca995e2b59914a1, 0x3001ca401e89601cd765f26dd03f4c45a6687c3df16c8fe4c26d909dee8b53c0),
    (0x0072e45cc676b08ef7bf86e89280827fe84b5bebae4e501de7fea6bdf3471380, 0x13de705484874bb5e2abe4c518ce599eb64829e2d40e41bdd0c54ddeb26b86c0, 0x0408a9fcf9d61abf315950f1211defe882bb18e5af1b05bb38915b432a9959a5),
    (0x2780b9e75b55676ebb4e4a1400ccd2c4ae4d23b0b41be9a834070cbee26886a0, 0x3a570d4d7c4e7ac3f80333ec85634ac9dc4d8fbefe24405a9405592098b4056f, 0x0c13cca7cb1f9d2cf347c247fcf09294e2cc1507bebdcc6278d2b247899520b4),
    (0x14f59baa03cd0ca4d2614a197c6b794b0b50bb2eb82df74d2e8c88f7707470e0, 0x307defee925dfb436f546e1704c39c60a51d54ede66167f5be52476e0a16f3be, 0x1960cd511a91e0607a07e7674b5a2621661106836adfe5e7380b67d80473dce3),
    (0x2301ef9c63ea84c5ca2ad0fb56672500b8ee335d88284cbe15aaf1f7712589dd, 0x029a5a47da79a488d10f4cd52be97f6bc86182d1b4246b585e68478c4d6027a9, 0x32d7b16a7f11cc962360d17d890e55cbf97fe46b6a9254282cc4f962eaae2260),
    (0x26703e48c03b81ca18e857a98d498cf7a5f2404cd7b35eb0c0cab915d5363d9f, 0x048682a35b3265bc88ac8d25a24603f1f44388bd6b89221ef691123ae112b928, 0x06b1390441fa7030d72cddc6cf06b50791d6e1715164775e3ab7defcb8d803e2),
    (0x31aa0eeb868c626d1689426dce05fcd843b360f6386a86d7bcd795414a6e2e86, 0x239464f75bf7b6af057abad3764c104b90efd8f41b2078b2ed77f5d576b99cc3, 0x0a64d4c04fd426bda45e19ed813a54aba5cc47c59654b2a7b2cb487307c1cecf),
    (0x21fbbdbb73670734576a4ad259860fb1777c7a921a062e9d1f7315322f658735, 0x31b86f3cf01705d4d9371ca2eb95acf35b86d29463d31564674324003fc52146, 0x2bfde53354377c9105ef1736d09056f613541d65157ee1ce7045f48aa4eb4f6f),
    (0x1233ca936ec24671d558f36e65f8eca7f4d5239c11d0eafa5a13a58d20011e2f, 0x27d452a43ac7dea2c437846d8e0b2b30878058d0234a576f6e70af0a7a924b3a, 0x2699dba82184e413e816ea8da493e0fa6a30641a1c3d87b2a02576b94392f980),
    (0x36c722f0efcc8803c3988baee42e4b10f18584664f8cab49608c6f7a61b56e55, 0x02b3ff48861e339b08b0f2ec89ccaa3785c38899a7b5a8336e49ac170dbb7fcd, 0x0b70d061d58d8a7f60162f4427bc657b6fc3ff4c49eb59ada8c5ae03ad98e405),
    (0x3fc2a13f127f96a4f8753adeb9d7cee2ad3de8be46ed96932e06cc4af33b0a06, 0x0c41a6e48dd23a511bd63434ac8c419f00cb3d621e171d80c12080ac117ee15f, 0x2de8072a6bd86884ed4476537169084e72aaad7e4e75339d9685213e9692f5e1),
    (0x03557a8f7b38a17f9d3496a3d9fe05ecb81cf735cc9c39c00ad01184567b027c, 0x0b5f59552f498735ee976d34282f1a37060f43363d818e5445bcb5ac00826abc, 0x0e2923a5fee7b878fedbb18570dc7300f5d646e57507e5482f2909e17e22b0df),
    (0x1d785005a7a00592c787be97020a7fddcf1cb37c3b032af6f71eed73f15b3326, 0x1ad772c273d9c6df0ba5fedcb8f25bd2a590b88a3b0602940acfbfb223f8f00d, 0x027bd64785fcbd2aa78f3275c278234b810510eb61f0672dc1ce13d60f2f5031),
    (0x20800f441b4a0526ce6f8ffea1031b6de224313469457b8e8337f5e07923a853, 0x3d5ad61d7b65f9386eea2cd49f4312b436cdc8eed662ad37a33d7bed89a4408a, 0x13338bc351fc46dd02c5f91be4dd8e3d1df96cc03ea4b26d3bbbae94cc195284),
    (0x25e52be507c92760b87db1e2af3ea923646c49f9b46cbf19c5271c297852819e, 0x1c492d64c157aaa471096d8b1b983c98a34c83a3485c6b2d5c380ab701b52ea9, 0x0c5b801579992718f4e6c5e7a573f592d43487bc288df682a20c0b3da0da4ca3),
    (0x1090b1b4d2bebe7a68695c0cd7cbf43d584e9e62a7f9554e7ea33c93e40833cf, 0x33e38018a801387a68f5ce5cbed19cad1b218e35ecf2328ee383e1ec3baa8d69, 0x1654af18772b2da5eef8d83d0e876bac5f4a02d28729e3aeb76b0b3d787ee953),
    (0x1678be3cc9c6799344742de88c5ab0d5bb0893870367ec6cef7ce6a013265477, 0x3780bd1e01f34c227ff9c6be546e928adaf1818355b13b4faf5d47893348f766, 0x1e83d6315c9f125b0786018e7cb772675d11e69aa6c0b98ca12380320d7cc1de),
    (0x354afd0a2f9d0b26160b41552f2931c8c486894d76e0c33b1799603e855ce731, 0x00cd6d29f166eadc2d8affa62905c5a560b00dbe1faced078b997ee06be1bff3, 0x1d6219352768e3aedbe0e3d7cdbc66efc60d01973f18305708d0641917082f2c),
    (0x146336e25db5181de48d2370d7d1a142afe3ca1db8d4f529fa08dd9806387577, 0x0005d8e085fd72ee997a21163e2e43df022e54b49c13d907a901d3ce84de0ad4, 0x364e97c7a38932270dd5e61c8a4e86426f8ebc1d2296021a1c36f31341964484),
    (0x01189910671bc16b561c6fff15346878fa97ec80ad307a52d7a00c03d2e0baaa, 0x162a7c80f4d2d12e5229dfaa01231a454c0f7e001df490aa63fd8ac57a95ca8c, 0x2a0d6c09576666bb2604e4afb09f8603caff31b4fda3212432e69efb22f40b96),
    (0x0978e5c51e1e5649e16a4d603d5a808ef444d10d63a74e2cc0a0180f8cbfc0d2, 0x1bdcee3aaca9cd25ebe19bbdce25101105087d903bdacfd103f4460ebc351b6e, 0x1862cccb70b5b885e49479140b1944fd0c947321e0075e3ff61964bf3ade7670),
    (0x1f3e91d863c16922bc26cc883a1987e139ee99c1cc6e5ddac3267da6e94adc50, 0x1af47a48a6016a49ef5c08f8478f663afa661465c656ad990f85b4ac2c367406, 0x3c8ee901956e3d3f009d57338c6935051c3698b0a2e3da100eabcd87e7d01b15),
    (0x1660a8cde7fec55368d0b024f591b520e10ce2b7069f4dbd8b94772189673476, 0x0f6d991929d5e4e71303936334dd11323963c2c1f5586e2f9d8d0f67fdaa79d5, 0x02b9cea1921cd9f6cc625eaaab52b4dc4e7fda770712f3437a433091e1ce2d3a),
    (0x14a323b99b900331214f7c6784acb565d8caf468976f04723797b2d8376043b3, 0x190476b580cb9277ec01ea79642d5760718b7fbc7788af78347fef2c00f0953a, 0x090a3a9d869d2eefa42463d30b442b6f9660902b60087651ff4e7e6fb268dfd7),
    (0x3877a955863675670dbe8fd2270a6795e365001304f9a11ef983387ea0456203, 0x2d894691240fe9535df39a2cc63ddc0a60118c53a218135239c0af0fe01f4a06, 0x21b9c18292bdbc597ef71780201661895914e855eeb44aa11aca9eaf9bba9850),
    (0x2fe76be7cff723e2505a05f2a6ae834c272e1cc6c36a296833f509a74ad9d39b, 0x187aa448f391e3ca929981d7cfce253bd15bff840ddae8a50df9fa97277fa8b4, 0x0b7083ad751707bf007ab3aa3617f422663ccf7b2ffe4b5ef0c66af5ffc73736),
    (0x030ddbb470493f163bc4ca9902c52acb1975b962f6cb8e0b2f9b20f1fbd49791, 0x3130fbaffb5aa82a950b0ab18d3546df8fb8ab9d60ea17b23a1c62ca8fbf2525, 0x337f544707c430f04f74d74bac2ee45715ce2ead2fcd051e43a876180dc382e0),
    (0x349979919015394fac9d91b0930dac757d8e471a9fb95fef26de98a8736d1d11, 0x027cc4efe3fb35dd2305cd7a921ec5f13bf93da6fff31d95ccfcb61831d5c775, 0x037f9f2365954c5b61b71a3698682ad267f1c6b7314764afc3fa2629635d27de),
    (0x1f697cac4d07feb710f1cc6df8b4bcd760414abe362d01c977c5b024848371ae, 0x267a750fe5d7cfbc26e6c851fbd572a63145c478063109d6786add244aa0ef29, 0x0c91feab4a43193a678c9996d9a472c8af285fa82ce4fae5180e2b4d3e756f65),
    (0x1745569a0a3e30142186c3038ea05e697e3b83af4a4ba3ba79c47c573ac410f7, 0x29863d546e7e7c0deca5120778a56711fdff66c6f3b5ffe11e0388522696191f, 0x1148d6ab2bd00192bf06bae49ef853f6a79a03df833994c62f225e6366bfe390),
    (0x02e0e121b0f3dfefe18b1499060da366f745f45d350d41d4f4f6331a8b265d15, 0x0d0aa46e76a6a278b89ef73a40a2b274690401736d44a653078ae6aa151054b7, 0x13943675b04aa986eee545f3fa6d3d08392dde710f1f06db9a4d532c7b6e0958),
    (0x2901ec61942d34aad97a11d63088f5d9c9f2b3257530dafe961fc818dcbb66b5, 0x20204a2105d22e7ef431d54434a3e0cf22ffa2a2af9fa3e3fdf544b963d1fdc7, 0x3a8a628295121d5c5c1e3e9e27a571c3a004abe8e01528c41211b9e2190d6852),
)
MDS = (
    (0x0ab5e5b874a68de7b3d59fbdc8c9ead497d7a0ab23850b56323f2486d7e11b63, 0x31916628e58a5abb293f0f0d886c7954240d4a7cbf7357368eca5596e996ab5e, 0x07c045d5f5e9e5a6d803952bbb364fdfa0a3b71a5fb1573519d1cf25d8e8345d),
    (0x233162630ebf9ed7f8e24f66822c2d9f3a0a464048bd770ad049cdc8d085167c, 0x25cae2599892a8b0b36664548d60957d78f8365c85bbab07402270113e047a2e, 0x22f5b5e1e6081c9774938717989a19579aad3d8262efd83ff84d806f685f747a),
    (0x2e29dd59c64b1037f333aa91c383346421680eabc56bc15dfee7a9944f84dbe4, 0x1d1aab4ec1cd678892d15e7dceef1665cbeaf48b3a0624c3c771effa43263664, 0x3bf763086a18936451e0cbead65516b975872c39b59a31f615639415f6e85ef1),
)

# ================================================================ 2 the target hash (Orchard Poseidon, ConstantLength<2>, 8 full + 23 partial rounds)
CAPACITY = 1 << 65
PARTIAL = 23
ROUND_IDX = tuple(range(4)) + tuple(range(4, 4 + PARTIAL)) + tuple(range(60, 64))   # original rounds 0-3 full, 4..26 partial (23 of them), 60-63 full


def digest(m0, m1):
    """Digest of the Orchard hash of the two canonical field elements (m0, m1): initial state [m0, m1, 2^65], 31 rounds, output state[0]."""
    a, b, c = m0, m1, CAPACITY
    for i in ROUND_IDX:
        k = ROUND_CONSTANTS[i]
        a = (a + k[0]) % P
        b = (b + k[1]) % P
        c = (c + k[2]) % P
        a2 = a * a % P
        a = a2 * a2 % P * a % P
        if i < 4 or i >= 60:
            b2 = b * b % P
            b = b2 * b2 % P * b % P
            c2 = c * c % P
            c = c2 * c2 % P * c % P
        a, b, c = ((MDS[0][0] * a + MDS[0][1] * b + MDS[0][2] * c) % P,
                   (MDS[1][0] * a + MDS[1][1] * b + MDS[1][2] * c) % P,
                   (MDS[2][0] * a + MDS[2][1] * b + MDS[2][2] * c) % P)
    return a


def enc(x):
    """Canonical 32-byte little-endian encoding (x < P)."""
    assert 0 <= x < P
    return x.to_bytes(32, "little")


# ================================================================ 3 the search: one trail, distinguished points, one table, recovery
# Operation charges, in word operations (1/C unit each), summed in the counters `ops` and priced in `plan` (proof.md Sections 5 and 6):
W_LOOP = 7        # trail step: counter add, register move of the digest into x, AND with the 128-bit mask, compare with T, branch, loop-bound compare, branch
W_INIT = 2        # before EVERY evaluation F(x) = digest(x, rho0): state coordinate 2 := rho0 (register move) and coordinate 3 := 2^65 (the permutation overwrites all three)
W_STEP = W_LOOP + W_INIT        # 9 other operations per trail step
W_RLOOP = 8       # recovery evaluation: counter, two register moves, equality compare and branch, loop control
W_REC = W_RLOOP + W_INIT        # 10 other operations per recovery evaluation (each of the walks F(B), F(A), F(B) initialises its own state)
W_SCAN = 6        # one table entry examined by a lookup: load the value word, compare, branch, pointer add 64, loop-bound compare, branch
W_INS = 3         # one insertion: store the value word, store the index word, end pointer add 64 (entries are two aligned 256-bit words)
W_PROBE = 12      # one probe of the bisection: lo+hi, +1, shift, index shift, base add, load the index word, compare, branch, bound update, loop compare, branch (11, 12 charged)


def lookup(pts, x, ops):
    """Table lookup by linear scan of the entry array (no second index structure): the entry k >= 1 with value x, or None. Charged W_SCAN per entry examined."""
    for k in range(1, len(pts)):
        ops["table"] += W_SCAN
        if pts[k][1] == x:
            return k
    return None


def search(F, is_dp, x0, steps, mcap, gmax):
    """Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}).  Every value x_i, i >= 1, with is_dp(x_i) is stored with its index
    in the entry array `pts` (entry = value word + index word, nothing else is stored).  Halts (failure) after `steps` evaluations, when more than
    `mcap` distinguished points would be stored, or when the recovery needs a gap longer than gmax.  When a distinguished value repeats
    (x_b = x_a, a < b) the trail is periodic from a with period L = b - a; the recovery finds the least i with x_i = x_{i+L} and returns the
    pair (x_{i-1}, x_{i+L-1}) with x_{i-1} != x_{i+L-1} and F equal on both.
    Returns (pair or None, status, evaluations, ops); ops counts the evaluations (trail, rec) and the table operations (table, probe) actually executed;
    the other operations of the ledger are W_STEP * trail + W_REC * rec + table + probe (see ledger_ops)."""
    ops = {"trail": 0, "rec": 0, "table": 0, "probe": 0}
    ev = 0
    pts = [(0, x0)]                       # stored points in increasing index order; pts[0] is the start
    x, i = x0, 0
    k = None
    while i < steps:
        x = F(x)                          # state := [x, 0, 2^65] (W_INIT), then one permutation call
        i += 1
        ev += 1
        ops["trail"] += 1
        if is_dp(x):
            k = lookup(pts, x, ops)
            if k is not None:
                break
            if len(pts) > mcap:
                return None, "table", ev, ops
            ops["table"] += W_INS
            pts.append((i, x))
    if k is None:
        return None, "steps", ev, ops
    a = pts[k][0]
    L = i - a                             # x_i = x_a with i = b
    s, A = pts[k - 1]                     # last stored point before a (index s < mu <= a, or the start)
    q = s + L
    lo, hi = 0, len(pts) - 1              # nearest stored point at or before q (q < b), then walk to x_q
    while lo < hi:
        mid = (lo + hi + 1) // 2
        ops["probe"] += W_PROBE
        if pts[mid][0] <= q:
            lo = mid
        else:
            hi = mid - 1
    idx, B = pts[lo]
    if q - idx > gmax:
        return None, "gap", ev, ops
    for _ in range(q - idx):
        B = F(B)
        ev += 1
        ops["rec"] += 1
    if A == B:
        return None, "start-on-cycle", ev, ops
    for _ in range(gmax):                 # lockstep: the first index where the two walkers meet
        nA, nB = F(A), F(B)
        ev += 2
        ops["rec"] += 2
        if nA == nB:
            return (A, B), "found", ev, ops
        A, B = nA, nB
    return None, "gap", ev, ops


# ================================================================ 4 the claim's parameters and ledger (plan)
T_DP = 27554                              # a value x is a distinguished point iff (x mod 2^128) < T_DP
# Exact count over the field: p = 2^254 + c with c = p mod 2^128 >= T_DP, so exactly D = (2^126 + 1) * T_DP of the p field elements are distinguished.
D_DP = ((1 << 126) + 1) * T_DP            # theta = D_DP / P (about 27554 / 2^128 = 2^-113.25)
SMAX = 1 << 128                           # every index of the program is below SMAX (S < 2^128; the index word has 128 bits)
MCAP = 15500                              # table capacity in distinguished points; (MCAP + 2) entries of 64 bytes
C_UNIT = 699                            # C(23) = 216 + 21*23
KD, H, TAB = 8, 18, 100                  # detection window d = ceil(KD/theta_lo), gap cap gmax = ceil(H/theta_lo), table tail <= e^-TAB
GRAIN = 1 << 100                         # n is the least multiple of 2^100 that reaches the success bound
# Everything that is not a trail step or a recovery evaluation, as a worst-case count: every distinguished-point event (at most MCAP + 1) scans at
# most MCAP + 1 entries and inserts once; one bisection of at most 15 probes; MISC = the random word, the mask, the capacity and threshold constants,
# the halts, the counters' setup and the report (a few hundred operations, 2000 allowed).
MISC = 2000
OTHER_FIXED = (MCAP + 2) * (W_SCAN * (MCAP + 1) + W_INS) + 15 * W_PROBE + MISC


def ledger_ops(ops):
    """Word operations (other than permutation calls) of a run, from its counters."""
    return W_STEP * ops["trail"] + W_REC * ops["rec"] + ops["table"] + ops["probe"]


def _bound(n, d, N, th_hi):
    """Proven lower bound on P_F(success) for budget n, in 80-digit decimal arithmetic (every term is an upper bound on a failure probability)."""
    e = lambda x: (-Decimal(x)).exp()
    eps = e(KD) + n * d / N + ((n + d) * th_hi + 1) * e(H) + e(TAB)
    return 1 - e(Decimal(n) * (n + 1) / (2 * N)) - n / N - eps, eps


def plan():
    getcontext().prec = 80
    N = Decimal(P)
    th_hi = Decimal(D_DP) / (N - SMAX)    # upper bound on P(fresh value is a DP | any history), Lemma 1
    theta = D_DP / P
    d = -(-KD * P // (D_DP - SMAX))       # integers (ceil), with theta_lo = (D_DP - SMAX) / P
    gmax = -(-H * P // (D_DP - SMAX))
    nf = 0.994 * sqrt(P)                  # float guess, then the exact search for the least multiple of GRAIN
    for _ in range(60):
        eps = exp(-KD) + nf * d / P + ((nf + d) * theta + 1) * exp(-H) + exp(-TAB)
        nf = sqrt(2 * P * (-log(0.61 - nf / P - eps)))
    k = int(nf // GRAIN) + 1
    while _bound(k * GRAIN, d, N, th_hi)[0] < Decimal("0.39"):
        k += 1
    while _bound((k - 1) * GRAIN, d, N, th_hi)[0] >= Decimal("0.39"):
        k -= 1
    n = k * GRAIN
    succ, eps = _bound(n, d, N, th_hi)
    steps = n + d
    assert steps < SMAX
    T = steps * (1 + W_STEP / C_UNIT) + 3 * gmax * (1 + W_REC / C_UNIT) + OTHER_FIXED / C_UNIT
    mean = steps * float(th_hi)
    # Chernoff tail of Binomial(S, theta_hi), which dominates the stored count (Lemma 1): P(X >= MCAP + 1) <= exp(-mu) (e mu / (MCAP + 1))^(MCAP + 1)
    lchern = -mean + (MCAP + 1) * (1 + log(mean / (MCAP + 1)))
    assert lchern <= -TAB
    mem = (MCAP + 2) * 64 + 600 * 36 + 6464 + 512
    return {"theta": theta, "theta_log2": log2(theta), "n": n, "n_over_2^100": k, "d": d, "gmax": gmax, "eps_total": float(eps), "steps": steps,
            "T_units": T, "time_log2": log2(T), "mean_stored_bound": mean, "ln_P_table_overflow": lchern, "n_log2": log2(n),
            "success_lower_bound": float(succ), "success_lower_bound_decimal": str(succ)[:20], "other_fixed": OTHER_FIXED,
            "W_STEP": W_STEP, "W_REC": W_REC, "memory_bytes": mem}


def attack(coin):
    """The claimed attempt (one run, not repeated). coin = two uniformly random 256-bit words; rho0 and x0 are their low 254 bits (every
    254-bit word is below p, so both are canonical). The walk is F(x) = digest(x, rho0). Returns the two 64-byte messages or None."""
    pr = plan()
    m254 = (1 << 254) - 1
    rho0, x0 = coin[0] & m254, coin[1] & m254
    pair, status, ev, ops = search(lambda x: digest(x, rho0), lambda x: (x & ((1 << 128) - 1)) < T_DP, x0, pr["steps"], MCAP, pr["gmax"])
    if pair is None:
        return None
    return enc(pair[0]) + enc(rho0), enc(pair[1]) + enc(rho0)


# ================================================================ 5 small self-check (reduced width) and command line
NB = 14                                  # walk width of the self-check: the low 14 bits of the real 23-partial-round digest of (v, rho)


def is_dp_n(x):
    return x < (1 << (NB - 4))           # density 1/16


def run_rho(seed):
    """The search of `attack` on the reduced map v -> low NB bits of digest(v, rho), rho and the start taken from the seed."""
    rho = int(seed, 16) >> 2
    x0 = int(seed[:8], 16) % (1 << NB)
    cache = {}

    def F_n(v):
        r = cache.get(v)
        if r is None:
            r = cache[v] = digest(v, rho) & ((1 << NB) - 1)
        return r
    pair, status, ev, ops = search(F_n, is_dp_n, x0, 256, 64, 160)
    if pair is None:
        return None, None, {"status": status, "evals": ev, "ops": ops}
    a, b = pair
    assert a != b and F_n(a) == F_n(b)
    return enc(a) + enc(rho), enc(b) + enc(rho), {"status": status, "evals": ev, "ops": ops}


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--plan":
            print(json.dumps(plan(), indent=1))
        elif sys.argv[1] == "--selftest":
            ok = 0
            worst = 0
            for t in range(40):
                ma, mb, ob = run_rho(hashlib.sha256(b"t%d" % t).hexdigest())
                if ma is not None:
                    ok += 1
                # the counters of the run stay inside the ledger formula for its parameters (steps 256, mcap 64, gmax 160)
                o = ob["ops"]
                bound = W_STEP * 256 + W_REC * 3 * 160 + (64 + 2) * (W_SCAN * 65 + W_INS) + 15 * W_PROBE
                assert ledger_ops(o) <= bound and o["trail"] <= 256 and o["rec"] <= 3 * 160
                worst = max(worst, ledger_ops(o))
            print("rho-n14 pairs:", ok, "of 40; largest counted other-operations:", worst)
        return
    print(json.dumps(plan(), indent=1))


if __name__ == "__main__":
    main()
```

## Appendix C: the measurement program `h1meas.c` (verbatim; links our C Pallas field and Orchard permutation, `pallas.c`)

Built with `gcc -O2`. Arguments per job: family (o: Orchard digest at r partial rounds; c: control), fixed (0: function index j = seedbase * 1000003 + k, the rho of trial k), r = 23, w, T, h, S, mcap, gmax (Lemma 2 parameters for N = 2^w, D = T * 2^(w-h), SMAX = 2^(h+3)), trials, seedbase. Run A used seedbases 1xxxxx, run B 2xxxxx (disjoint functions and starts).

```c
/* h1meas.c - measurements of the Orchard map at r partial rounds on truncated outputs (our own code, 2026-10-15).
 * Map at width w: F_w(v) = low w bits of digest(v, rho), v in [0, 2^w) (v and rho are canonical field elements; rho is the function index j).
 * Per trial: walk v_0 (from the seed), v_i = F_w(v_{i-1}) until the first repeat (exact, hash map of all values):
 *   t = least index with v_t in {v_0..v_{t-1}}, mu = index of that earlier value, lambda = t - mu.
 * DP statistics at density theta = T/2^h (DP iff (v mod 2^h) < T): gaps between consecutive DPs among v_1..v_{t-1}.
 * Then the search of rho.py (one trail, DPs, table cap mcap, budget S, recovery with gap cap gmax) is run on the same map;
 * trail values are taken from the stored walk (they are digest values), the recovery evaluates the digest afresh and the returned
 * pair is checked (distinct, equal F_w).
 * Usage: h1meas fam fixed r w T h S mcap gmax K seedbase   -> one JSON line per trial on stdout.
 *   fam o|c; fixed 0: trial k uses function index j = seedbase*1000003 + k (rho = j, or control key j), fixed f >= 1: j = f - 1 for every trial (one fixed function, many starts).
 *   start v_0 = splitmix(seedbase*1000003 + k) mod 2^w.
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include "../impl/pallas.h"

static int R, W, FAM;              /* FAM 'o': Orchard digest(v, rho) ; FAM 'c': control, keyed splitmix (a pseudo-random function) */
static uint64_t MASK, RHO, CKEY;
static uint64_t splitmix(uint64_t x) {
    x += 0x9e3779b97f4a7c15ULL; x = (x ^ (x >> 30)) * 0xbf58476d1ce4e5b9ULL; x = (x ^ (x >> 27)) * 0x94d049bb133111ebULL;
    return x ^ (x >> 31);
}
static uint64_t Fw(uint64_t v) {
    if (FAM == 'c') return splitmix(splitmix(v ^ CKEY) + CKEY) & MASK;
    uint64_t a[4] = {v, 0, 0, 0}, z[4] = {RHO, 0, 0, 0}, o[4];
    poseidon_hash_r(a, z, R, o);
    return o[0] & MASK;          /* W <= 62 */
}

int main(int argc, char **argv) {
    if (argc != 12) { fprintf(stderr, "usage: h1meas fam fixed r w T h S mcap gmax K seedbase\n"); return 2; }
    FAM = argv[1][0]; int FIXED = atoi(argv[2]); argv += 2;
    R = atoi(argv[1]); W = atoi(argv[2]);
    uint64_t T = strtoull(argv[3], 0, 10); int H = atoi(argv[4]);
    uint64_t S = strtoull(argv[5], 0, 10), MCAP = strtoull(argv[6], 0, 10), GMAX = strtoull(argv[7], 0, 10);
    int K = atoi(argv[8]); uint64_t SB = strtoull(argv[9], 0, 10);
    MASK = (W >= 64) ? ~0ULL : ((1ULL << W) - 1); uint64_t HM = (1ULL << H) - 1;
    /* walk cap: 12 sqrt(N) (P(t > cap) <= exp(-72) for a random mapping); hash table 2^k >= 2 cap */
    uint64_t cap = (uint64_t)(12.0 * (double)(1ULL << (W / 2)) * ((W & 1) ? 1.41421356 : 1.0));
    uint64_t hsz = 1; while (hsz < 2 * cap) hsz <<= 1;
    uint64_t *hk = malloc(hsz * 8); uint32_t *hv = malloc(hsz * 4); uint64_t *tr = malloc((cap + 1) * 8);
    uint64_t *pi = malloc((MCAP + 2) * 8), *pv = malloc((MCAP + 2) * 8);   /* table: index word, value word */
    if (!hk || !hv || !tr || !pi || !pv) { fprintf(stderr, "alloc\n"); return 1; }
    for (int k = 0; k < K; k++) {
        memset(hk, 0, hsz * 8);
        uint64_t j = FIXED ? (uint64_t)(FIXED - 1) : SB * 1000003ULL + (uint64_t)k; RHO = j; CKEY = splitmix(j ^ 0x5bd1e995ULL);
        uint64_t v = splitmix(SB * 1000003ULL + (uint64_t)k) & MASK;
        uint64_t t = 0, mu = 0; int cens = 0;
        uint64_t hm = hsz - 1;
        /* insert v_0 */
        for (uint64_t i = 0;; i++) {
            tr[i] = v;
            uint64_t h = (splitmix(v) & hm);
            while (hk[h] && hk[h] != v + 1) h = (h + 1) & hm;
            if (hk[h]) { t = i; mu = hv[h]; break; }
            hk[h] = v + 1; hv[h] = (uint32_t)i;
            if (i >= cap) { cens = 1; t = i; break; }
            v = Fw(v);
        }
        uint64_t lam = t - mu;
        /* DP gaps among v_1..v_{t-1} */
        uint64_t ndp = 0, last = 0, ngap = 0, sgap = 0, maxgap = 0; int first = 1;
        for (uint64_t i = 1; i < t; i++) if ((tr[i] & HM) < T) {
            ndp++;
            if (!first) { uint64_t g = i - last; ngap++; sgap += g; if (g > maxgap) maxgap = g; }
            first = 0; last = i;
        }
        /* first DP at index >= mu (cycle), detection delay */
        int64_t aprime = -1;
        for (uint64_t i = (mu ? mu : 1); i < t; i++) if ((tr[i] & HM) < T) { aprime = (int64_t)i; break; }
        if (mu == 0 && aprime < 0 && (tr[0] & HM) < T) aprime = -1;  /* start is not a stored DP */
        /* the search of rho.py on this trail */
        const char *st = "steps"; uint64_t ev = 0, rec = 0, A = 0, B = 0; int ok = 0;
        if (!cens) {
            uint64_t np = 1; pi[0] = 0; pv[0] = tr[0];
            uint64_t i = 0, x = tr[0]; int64_t hit = -1;
            while (i < S) {
                i++; ev++;
                x = (i < t) ? tr[i] : tr[mu + (i - mu) % lam];
                if ((x & HM) < T) {
                    for (uint64_t q = 1; q < np; q++) if (pv[q] == x) { hit = (int64_t)q; break; }
                    if (hit >= 0) break;
                    if (np > MCAP) { st = "table"; break; }
                    pi[np] = i; pv[np] = x; np++;
                }
            }
            if (hit >= 0) {
                uint64_t a = pi[hit], L = i - a, s = pi[hit - 1]; A = pv[hit - 1];
                uint64_t q = s + L; uint64_t lo = 0, hi = np - 1;
                while (lo < hi) { uint64_t m = (lo + hi + 1) / 2; if (pi[m] <= q) lo = m; else hi = m - 1; }
                uint64_t idx = pi[lo]; B = pv[lo];
                if (q - idx > GMAX) st = "gap";
                else {
                    for (uint64_t j = 0; j < q - idx; j++) { B = Fw(B); rec++; }
                    if (A == B) st = "start-on-cycle";
                    else {
                        st = "gap";
                        for (uint64_t j = 0; j < GMAX; j++) {
                            uint64_t nA = Fw(A), nB = Fw(B); rec += 2;
                            if (nA == nB) { st = "found"; ok = (A != B) && (Fw(A) == Fw(B)); break; }
                            A = nA; B = nB;
                        }
                    }
                }
            } else if (strcmp(st, "table")) st = "steps";
        }
        printf("{\"fam\":\"%c\",\"fn\":%llu,\"r\":%d,\"w\":%d,\"seedbase\":%llu,\"k\":%d,\"v0\":%llu,\"t\":%llu,\"mu\":%llu,\"lambda\":%llu,\"cens\":%d,"
               "\"ndp\":%llu,\"ngap\":%llu,\"sgap\":%llu,\"maxgap\":%llu,\"aprime\":%lld,\"status\":\"%s\",\"evals\":%llu,\"rec\":%llu,"
               "\"A\":%llu,\"B\":%llu,\"pair_ok\":%d}\n",
               FAM, (unsigned long long)j, R, W, (unsigned long long)SB, k, (unsigned long long)tr[0], (unsigned long long)t, (unsigned long long)mu,
               (unsigned long long)lam, cens, (unsigned long long)ndp, (unsigned long long)ngap, (unsigned long long)sgap,
               (unsigned long long)maxgap, (long long)aprime, st, (unsigned long long)ev, (unsigned long long)rec,
               (unsigned long long)(strcmp(st, "found") ? 0 : A), (unsigned long long)(strcmp(st, "found") ? 0 : B), ok);
        fflush(stdout);
    }
    return 0;
}
```

## Appendix D: measurement data (per run, family and width; keys as in Section 7)

```json
{"A/ctrl/w16":{"K":10000,"censored":0,"c_hat":1.0023,"c_lo":0.9827,"c_hi":1.022,"mean_t_over_sqrt_piN_2":0.9988,"dp_theta":0.0625,"dp_gaps":189051,"theta_x_mean_gap":0.9531,"theta_x_mean_detection_delay":0.9714,"max_gap_x_theta":10.56},
"A/ctrl/w20":{"K":10000,"censored":0,"c_hat":0.9933,"c_lo":0.9739,"c_hi":1.0128,"mean_t_over_sqrt_piN_2":1.0018,"dp_theta":0.0625,"dp_gaps":793591,"theta_x_mean_gap":0.9871,"theta_x_mean_detection_delay":0.9292,"max_gap_x_theta":11.94},
"A/ctrl/w24":{"K":10000,"censored":0,"c_hat":0.9936,"c_lo":0.9742,"c_hi":1.0131,"mean_t_over_sqrt_piN_2":1.0034,"dp_theta":0.25,"dp_gaps":12863844,"theta_x_mean_gap":0.9995,"theta_x_mean_detection_delay":0.7609,"max_gap_x_theta":13.75,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":4038,"success_frac":0.4038,"success_ci":[0.3942,0.4135],"pairs_verified":4038,"status":{"steps":5960,"found":4038,"start-on-cycle":2},
"frac_t_le_n":0.4016,"model_t_le_n":0.3987,"max_gap_vs_gmax":"55 / 73"},
"A/ctrl/w28":{"K":3000,"censored":0,"c_hat":0.9986,"c_lo":0.9632,"c_hi":1.0347,"mean_t_over_sqrt_piN_2":1.0016,"dp_theta":0.0625,"dp_gaps":3853564,"theta_x_mean_gap":0.9992,"theta_x_mean_detection_delay":0.9496,"max_gap_x_theta":15.25,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":1197,"success_frac":0.399,"success_ci":[0.3816,0.4166],"pairs_verified":1197,"status":{"found":1197,"steps":1803},
"frac_t_le_n":0.397,"model_t_le_n":0.3984,"max_gap_vs_gmax":"244 / 291"},
"A/ctrl/w32":{"K":1000,"censored":0,"c_hat":1.0354,"c_lo":0.9722,"c_hi":1.1005,"mean_t_over_sqrt_piN_2":0.9875,"dp_theta":0.015625,"dp_gaps":1264429,"theta_x_mean_gap":1.0006,"theta_x_mean_detection_delay":0.9907,"max_gap_x_theta":14.5,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":406,"success_frac":0.406,"success_ci":[0.376,0.4367],"pairs_verified":406,"status":{"steps":594,"found":406},
"frac_t_le_n":0.404,"model_t_le_n":0.3983,"max_gap_vs_gmax":"928 / 1162"},
"A/ctrl/w36":{"K":300,"censored":0,"c_hat":1.0514,"c_lo":0.9358,"c_hi":1.1737,"mean_t_over_sqrt_piN_2":0.9788,"dp_theta":0.00390625,"dp_gaps":376661,"theta_x_mean_gap":0.999,"theta_x_mean_detection_delay":0.951,"max_gap_x_theta":15.43,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":121,"success_frac":0.4033,"success_ci":[0.3494,0.4597],"pairs_verified":121,"status":{"found":121,"steps":179},
"frac_t_le_n":0.4,"model_t_le_n":0.3983,"max_gap_vs_gmax":"3951 / 4645"},
"A/ctrl/w40":{"K":60,"censored":0,"c_hat":0.946,"c_lo":0.7218,"c_hi":1.1999,"mean_t_over_sqrt_piN_2":0.9958,"dp_theta":0.0009765625,"dp_gaps":76074,"theta_x_mean_gap":1.0064,"theta_x_mean_detection_delay":0.953,"max_gap_x_theta":14.83,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":27,"success_frac":0.45,"success_ci":[0.3309,0.5751],"pairs_verified":27,"status":{"steps":33,"found":27},
"frac_t_le_n":0.45,"model_t_le_n":0.3983,"max_gap_vs_gmax":"15188 / 18578"},
"A/orch/w16":{"K":2000,"censored":0,"c_hat":0.9813,"c_lo":0.9388,"c_hi":1.0248,"mean_t_over_sqrt_piN_2":1.0091,"dp_theta":0.0625,"dp_gaps":38300,"theta_x_mean_gap":0.9535,"theta_x_mean_detection_delay":0.999,"max_gap_x_theta":11.75},
"A/orch/w20":{"K":2000,"censored":0,"c_hat":1.0202,"c_lo":0.976,"c_hi":1.0654,"mean_t_over_sqrt_piN_2":0.9873,"dp_theta":0.0625,"dp_gaps":155996,"theta_x_mean_gap":0.9894,"theta_x_mean_detection_delay":0.9026,"max_gap_x_theta":11.81},
"A/orch/w24":{"K":2000,"censored":0,"c_hat":1.0135,"c_lo":0.9696,"c_hi":1.0584,"mean_t_over_sqrt_piN_2":0.9894,"dp_theta":0.25,"dp_gaps":2536862,"theta_x_mean_gap":0.9994,"theta_x_mean_detection_delay":0.7339,"max_gap_x_theta":13.5,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":831,"success_frac":0.4155,"success_ci":[0.3941,0.4372],"pairs_verified":831,"status":{"steps":1169,"found":831},
"frac_t_le_n":0.409,"model_t_le_n":0.3987,"max_gap_vs_gmax":"54 / 73"},
"A/orch/w28":{"K":600,"censored":0,"c_hat":0.9543,"c_lo":0.8794,"c_hi":1.0321,"mean_t_over_sqrt_piN_2":1.0191,"dp_theta":0.0625,"dp_gaps":785227,"theta_x_mean_gap":0.9979,"theta_x_mean_detection_delay":0.9405,"max_gap_x_theta":13.06,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":235,"success_frac":0.3917,"success_ci":[0.3534,0.4313],"pairs_verified":235,"status":{"steps":365,"found":235},
"frac_t_le_n":0.3883,"model_t_le_n":0.3984,"max_gap_vs_gmax":"209 / 291"},
"A/orch/w32":{"K":200,"censored":0,"c_hat":0.9913,"c_lo":0.8587,"c_hi":1.1333,"mean_t_over_sqrt_piN_2":0.9948,"dp_theta":0.015625,"dp_gaps":255419,"theta_x_mean_gap":0.9983,"theta_x_mean_detection_delay":1.0569,"max_gap_x_theta":14.5,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":85,"success_frac":0.425,"success_ci":[0.3585,0.4943],"pairs_verified":85,"status":{"steps":115,"found":85},
"frac_t_le_n":0.42,"model_t_le_n":0.3983,"max_gap_vs_gmax":"928 / 1162"},
"A/orch/w36":{"K":60,"censored":0,"c_hat":1.0994,"c_lo":0.8389,"c_hi":1.3945,"mean_t_over_sqrt_piN_2":0.9374,"dp_theta":0.00390625,"dp_gaps":71505,"theta_x_mean_gap":1.0076,"theta_x_mean_detection_delay":1.1115,"max_gap_x_theta":10.92,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":25,"success_frac":0.4167,"success_ci":[0.3006,0.5427],"pairs_verified":25,"status":{"found":25,"steps":35},
"frac_t_le_n":0.4167,"model_t_le_n":0.3983,"max_gap_vs_gmax":"2795 / 4645"},
"A/orch/w40":{"K":12,"censored":0,"c_hat":1.6725,"c_lo":0.8632,"c_hi":2.7434,"mean_t_over_sqrt_piN_2":0.712,"dp_theta":0.0009765625,"dp_gaps":11005,"theta_x_mean_gap":0.995,"theta_x_mean_detection_delay":0.9288,"max_gap_x_theta":11.2,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":7,"success_frac":0.5833,"success_ci":[0.3195,0.8067],"pairs_verified":7,"status":{"found":7,"steps":5},
"frac_t_le_n":0.5833,"model_t_le_n":0.3983,"max_gap_vs_gmax":"11466 / 18578"},
"A/orch0/w24":{"K":200,"censored":0,"c_hat":0.9077,"c_lo":0.7863,"c_hi":1.0378,"mean_t_over_sqrt_piN_2":1.1267,"dp_theta":0.25,"dp_gaps":280530,"theta_x_mean_gap":1.0298,"theta_x_mean_detection_delay":2.3512,"max_gap_x_theta":10.5,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":26,"success_frac":0.13,"success_ci":[0.0903,0.1837],"pairs_verified":26,"status":{"steps":174,"found":26},
"frac_t_le_n":0.13,"model_t_le_n":0.3987,"max_gap_vs_gmax":"42 / 73"},
"A/orch0/w28":{"K":200,"censored":0,"c_hat":2.3334,"c_lo":2.0212,"c_hi":2.6677,"mean_t_over_sqrt_piN_2":0.7004,"dp_theta":0.0625,"dp_gaps":178857,"theta_x_mean_gap":1.0028,"theta_x_mean_detection_delay":0.5644,"max_gap_x_theta":9.88,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":131,"success_frac":0.655,"success_ci":[0.5868,0.7174],"pairs_verified":131,"status":{"steps":69,"found":131},
"frac_t_le_n":0.65,"model_t_le_n":0.3984,"max_gap_vs_gmax":"158 / 291"},
"A/orch0/w32":{"K":100,"censored":0,"c_hat":1.1175,"c_lo":0.9092,"c_hi":1.3469,"mean_t_over_sqrt_piN_2":0.9649,"dp_theta":0.015625,"dp_gaps":125589,"theta_x_mean_gap":0.9838,"theta_x_mean_detection_delay":0.5977,"max_gap_x_theta":8.62,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":37,"success_frac":0.37,"success_ci":[0.2818,0.4678],"pairs_verified":37,"status":{"steps":63,"found":37},
"frac_t_le_n":0.37,"model_t_le_n":0.3983,"max_gap_vs_gmax":"552 / 1162"},
"A/ctrlfix/w24":{"functions":40,"starts_each":200,"mean_success":0.4952,"sd_success":0.2643,"min":0.005,"max":0.92},
"A/ctrlfix/w28":{"functions":40,"starts_each":200,"mean_success":0.4839,"sd_success":0.2182,"min":0.0,"max":0.835},
"B/ctrl/w16":{"K":10000,"censored":0,"c_hat":0.9985,"c_lo":0.979,"c_hi":1.0181,"mean_t_over_sqrt_piN_2":1.0026,"dp_theta":0.0625,"dp_gaps":190089,"theta_x_mean_gap":0.9532,"theta_x_mean_detection_delay":0.9437,"max_gap_x_theta":10.5},
"B/ctrl/w20":{"K":10000,"censored":0,"c_hat":0.996,"c_lo":0.9766,"c_hi":1.0156,"mean_t_over_sqrt_piN_2":1.0003,"dp_theta":0.0625,"dp_gaps":791410,"theta_x_mean_gap":0.9883,"theta_x_mean_detection_delay":0.9394,"max_gap_x_theta":12.12},
"B/ctrl/w24":{"K":10000,"censored":0,"c_hat":0.9978,"c_lo":0.9783,"c_hi":1.0174,"mean_t_over_sqrt_piN_2":1.0008,"dp_theta":0.25,"dp_gaps":12827062,"theta_x_mean_gap":0.9997,"theta_x_mean_detection_delay":0.7377,"max_gap_x_theta":13.25,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":4021,"success_frac":0.4021,"success_ci":[0.3925,0.4117],"pairs_verified":4021,"status":{"steps":5977,"found":4021,"start-on-cycle":2},
"frac_t_le_n":0.3989,"model_t_le_n":0.3987,"max_gap_vs_gmax":"53 / 73"},
"B/ctrl/w28":{"K":3000,"censored":0,"c_hat":0.9937,"c_lo":0.9585,"c_hi":1.0296,"mean_t_over_sqrt_piN_2":0.998,"dp_theta":0.0625,"dp_gaps":3839791,"theta_x_mean_gap":0.9991,"theta_x_mean_detection_delay":0.9431,"max_gap_x_theta":18.69,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":1250,"success_frac":0.4167,"success_ci":[0.3991,0.4344],"pairs_verified":1250,"status":{"steps":1750,"found":1250},
"frac_t_le_n":0.4153,"model_t_le_n":0.3984,"max_gap_vs_gmax":"299 / 291"},
"B/ctrl/w32":{"K":1000,"censored":0,"c_hat":1.0102,"c_lo":0.9486,"c_hi":1.0738,"mean_t_over_sqrt_piN_2":0.9892,"dp_theta":0.015625,"dp_gaps":1268735,"theta_x_mean_gap":0.9991,"theta_x_mean_detection_delay":0.9532,"max_gap_x_theta":15.59,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":419,"success_frac":0.419,"success_ci":[0.3888,0.4498],"pairs_verified":419,"status":{"steps":581,"found":419},
"frac_t_le_n":0.416,"model_t_le_n":0.3983,"max_gap_vs_gmax":"998 / 1162"},
"B/ctrl/w36":{"K":300,"censored":0,"c_hat":1.012,"c_lo":0.9007,"c_hi":1.1297,"mean_t_over_sqrt_piN_2":0.9899,"dp_theta":0.00390625,"dp_gaps":381524,"theta_x_mean_gap":0.9973,"theta_x_mean_detection_delay":1.0251,"max_gap_x_theta":14.01,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":126,"success_frac":0.42,"success_ci":[0.3655,0.4765],"pairs_verified":126,"status":{"found":126,"steps":174},
"frac_t_le_n":0.4133,"model_t_le_n":0.3983,"max_gap_vs_gmax":"3587 / 4645"},
"B/ctrl/w40":{"K":60,"censored":0,"c_hat":1.1392,"c_lo":0.8693,"c_hi":1.445,"mean_t_over_sqrt_piN_2":0.9333,"dp_theta":0.0009765625,"dp_gaps":72098,"theta_x_mean_gap":0.9949,"theta_x_mean_detection_delay":0.8959,"max_gap_x_theta":9.79,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":26,"success_frac":0.4333,"success_ci":[0.3157,0.559],"pairs_verified":26,"status":{"steps":34,"found":26},
"frac_t_le_n":0.4333,"model_t_le_n":0.3983,"max_gap_vs_gmax":"10027 / 18578"},
"B/orch/w16":{"K":2000,"censored":0,"c_hat":0.9695,"c_lo":0.9275,"c_hi":1.0124,"mean_t_over_sqrt_piN_2":1.0187,"dp_theta":0.0625,"dp_gaps":38679,"theta_x_mean_gap":0.9566,"theta_x_mean_detection_delay":0.862,"max_gap_x_theta":9.62},
"B/orch/w20":{"K":2000,"censored":0,"c_hat":1.0277,"c_lo":0.9832,"c_hi":1.0733,"mean_t_over_sqrt_piN_2":0.9788,"dp_theta":0.0625,"dp_gaps":155350,"theta_x_mean_gap":0.9849,"theta_x_mean_detection_delay":0.9386,"max_gap_x_theta":11.31},
"B/orch/w24":{"K":2000,"censored":0,"c_hat":1.0133,"c_lo":0.9694,"c_hi":1.0582,"mean_t_over_sqrt_piN_2":0.9941,"dp_theta":0.25,"dp_gaps":2550047,"theta_x_mean_gap":0.9991,"theta_x_mean_detection_delay":0.7311,"max_gap_x_theta":13.0,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":813,"success_frac":0.4065,"success_ci":[0.3852,0.4282],"pairs_verified":813,"status":{"found":813,"steps":1185,"start-on-cycle":2},
"frac_t_le_n":0.4005,"model_t_le_n":0.3987,"max_gap_vs_gmax":"52 / 73"},
"B/orch/w28":{"K":600,"censored":0,"c_hat":1.0894,"c_lo":1.004,"c_hi":1.1783,"mean_t_over_sqrt_piN_2":0.9606,"dp_theta":0.0625,"dp_gaps":738673,"theta_x_mean_gap":0.9998,"theta_x_mean_detection_delay":0.8537,"max_gap_x_theta":13.19,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":250,"success_frac":0.4167,"success_ci":[0.3779,0.4565],"pairs_verified":250,"status":{"steps":350,"found":250},
"frac_t_le_n":0.4133,"model_t_le_n":0.3984,"max_gap_vs_gmax":"211 / 291"},
"B/orch/w32":{"K":200,"censored":0,"c_hat":0.9555,"c_lo":0.8276,"c_hi":1.0924,"mean_t_over_sqrt_piN_2":0.9969,"dp_theta":0.015625,"dp_gaps":255785,"theta_x_mean_gap":0.9987,"theta_x_mean_detection_delay":1.1476,"max_gap_x_theta":16.08,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":89,"success_frac":0.445,"success_ci":[0.3778,0.5143],"pairs_verified":89,"status":{"steps":111,"found":89},
"frac_t_le_n":0.445,"model_t_le_n":0.3983,"max_gap_vs_gmax":"1029 / 1162"},
"B/orch/w36":{"K":60,"censored":0,"c_hat":0.8383,"c_lo":0.6397,"c_hi":1.0633,"mean_t_over_sqrt_piN_2":1.1316,"dp_theta":0.00390625,"dp_gaps":87131,"theta_x_mean_gap":0.9986,"theta_x_mean_detection_delay":1.1381,"max_gap_x_theta":11.66,"n":264230,"S":266295,"gmax":4645,"mcap":1528,"lemma_bound":0.39,"success":17,"success_frac":0.2833,"success_ci":[0.1851,0.4077],"pairs_verified":17,"status":{"steps":43,"found":17},
"frac_t_le_n":0.2833,"model_t_le_n":0.3983,"max_gap_vs_gmax":"2984 / 4645"},
"B/orch/w40":{"K":12,"censored":0,"c_hat":0.6325,"c_lo":0.3265,"c_hi":1.0375,"mean_t_over_sqrt_piN_2":1.2093,"dp_theta":0.0009765625,"dp_gaps":18623,"theta_x_mean_gap":0.9984,"theta_x_mean_detection_delay":1.2563,"max_gap_x_theta":9.43,"n":1056909,"S":1065166,"gmax":18578,"mcap":1528,"lemma_bound":0.39,"success":4,"success_frac":0.3333,"success_ci":[0.1381,0.6094],"pairs_verified":4,"status":{"found":4,"steps":8},
"frac_t_le_n":0.3333,"model_t_le_n":0.3983,"max_gap_vs_gmax":"9652 / 18578"},
"B/orch0/w24":{"K":200,"censored":0,"c_hat":0.9207,"c_lo":0.7975,"c_hi":1.0526,"mean_t_over_sqrt_piN_2":1.1208,"dp_theta":0.25,"dp_gaps":279278,"theta_x_mean_gap":1.029,"theta_x_mean_detection_delay":2.4838,"max_gap_x_theta":10.5,"n":4131,"S":4164,"gmax":73,"mcap":1532,"lemma_bound":0.39,"success":26,"success_frac":0.13,"success_ci":[0.0903,0.1837],"pairs_verified":26,"status":{"steps":174,"found":26},
"frac_t_le_n":0.13,"model_t_le_n":0.3987,"max_gap_vs_gmax":"42 / 73"},
"B/orch0/w28":{"K":200,"censored":0,"c_hat":2.0256,"c_lo":1.7545,"c_hi":2.3158,"mean_t_over_sqrt_piN_2":0.7547,"dp_theta":0.0625,"dp_gaps":192586,"theta_x_mean_gap":1.0037,"theta_x_mean_detection_delay":0.5116,"max_gap_x_theta":9.88,"n":16518,"S":16648,"gmax":291,"mcap":1529,"lemma_bound":0.39004,"success":115,"success_frac":0.575,"success_ci":[0.5057,0.6415],"pairs_verified":115,"status":{"found":115,"steps":85},
"frac_t_le_n":0.565,"model_t_le_n":0.3984,"max_gap_vs_gmax":"158 / 291"},
"B/orch0/w32":{"K":100,"censored":0,"c_hat":1.1172,"c_lo":0.909,"c_hi":1.3466,"mean_t_over_sqrt_piN_2":0.9661,"dp_theta":0.015625,"dp_gaps":125812,"theta_x_mean_gap":0.9835,"theta_x_mean_detection_delay":0.5897,"max_gap_x_theta":8.73,"n":66060,"S":66577,"gmax":1162,"mcap":1528,"lemma_bound":0.39,"success":38,"success_frac":0.38,"success_ci":[0.291,0.4779],"pairs_verified":38,"status":{"found":38,"steps":62},
"frac_t_le_n":0.37,"model_t_le_n":0.3983,"max_gap_vs_gmax":"559 / 1162"},
"B/ctrlfix/w24":{"functions":40,"starts_each":200,"mean_success":0.443,"sd_success":0.1771,"min":0.05,"max":0.74},
"B/ctrlfix/w28":{"functions":40,"starts_each":200,"mean_success":0.4306,"sd_success":0.2585,"min":0.015,"max":1.0}}
```
