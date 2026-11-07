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

