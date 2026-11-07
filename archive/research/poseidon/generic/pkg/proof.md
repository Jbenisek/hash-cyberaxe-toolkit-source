# poseidon-orchard-r56: plain birthday search, one trail with distinguished points

Credit: this is the textbook collision search (Pollard rho with distinguished points, van Oorschot-Wiener) applied to the complete Orchard hash; we add nothing to the mathematics. The accounting (single trail, one table, recovery from stored points) is our own. No other participant's program was used or run. Claim: time_log2 = 127.009, memory below 1 MiB (claimed 2^20 bytes), success probability 0.39. It is a generic attack: no property of the 56 partial rounds is used, and it does not beat the nominal 127 (it is 0.009 above it). Its point is that it exists at every round count including the full one.

## 1. Target and relation

Target `poseidon-orchard-r56-prefix-v1`: input two canonical field elements (nk, rho) of the Pallas base field, p = 0x40000000000000000000000000000000224698fc094cf91b992d30ed00000001 (about 2^254); initial state [nk, rho, 2^65]; all 64 deployed rounds (4 full, 56 partial, 4 full); digest = state[0], canonical 32-byte little-endian, the complete element compared. Reference unit: one call of the permutation = one target compression; C(56) = 216 + 21 * 56 = 1392 primitive operations.

Walk. Fix rho = 0 and write F(x) = digest(x, 0), a map from the field into the field. Two inputs (x, 0) and (y, 0) with x != y and F(x) = F(y) are a collision of the target; both are canonical encodings, distinct as pairs. The search iterates x_0, x_i = F(x_{i-1}) and returns the pair (x_{mu-1}, x_{mu-1+L}) at the merge point of the trail (Section 3). The output of F is a canonical field element, so it is again an admissible input: no conversion is needed and no operation is spent on one. This is the whole reason the walk is on F itself.

## 2. The program (`experiments/rho.py`, function `search`; parameters in `plan`)

1. x_0 = a uniformly random 254-bit word (one random word and one AND with 2^254 - 1; every 254-bit word is below p, so no rejection).
2. Loop for i = 1 .. S: x = F(x) (one reference call). If x mod 2^128 < T (T = 27554, density theta = T / 2^128 = 2^-113.25003): x is a distinguished point (DP). If the value is already in the table the trail has closed: go to 3. Otherwise store (i, x) (48 bytes). If the table already holds 2^14 DPs, halt (failure). After S steps without a repeated DP, halt (failure).
3. Recovery. The repeated value is x_b = x_a (b = i, a its first stored index), L = b - a. Let (s, x_s) be the stored entry just before the one at index a (the start x_0 at index 0 if there is none). Compute x_{s+L} from the nearest stored point at or before s + L by iterating F (more than gmax steps: halt). If x_s = x_{s+L} halt (start on the cycle). Then iterate both from (x_s, x_{s+L}) in lockstep: the first time F(A) = F(B) return (A, B). More than gmax lockstep rounds: halt.

Parameters: S = n + d with n = 1.6948e38 (log2 126.9944, a multiple of 2^100, `plan`), d = 8 / theta = 9.880e34, gmax = 18 / theta = 2.2229e35, table 2^14 DPs. `python3 experiments/rho.py --plan` prints them (Appendix).

## 3. Correctness of the recovery (deterministic)

Let t be the least index with x_t = x_j for some j < t, mu = j (the trail enters its cycle at mu; lambda = t - mu is the cycle length). For i >= mu, x_i = x_{i+lambda}. A repeated DP is found at b = a' + lambda where a' is the first DP with index at least mu: DPs with index in [t, a' + lambda) would repeat values of x_mu .. x_{a'-1}, which hold no DP; so a = a' and L = lambda (a stored value repeats only along the cycle, and the first repeat is at a' + lambda). The stored entry before a is a DP with index < mu (none lies in [mu, a)) or the start; so s < mu <= a, or s = 0 = mu (halt: start on the cycle, x_0 = x_L). With s < mu, x_s != x_{s+L} and the least m >= 1 with x_{s+m} = x_{s+m+L} is m = mu - s <= a - s, so the lockstep stops within a - s rounds and returns (x_{mu-1}, x_{mu-1+L}), which differ and have equal F. The nearest stored point before q = s + L < t exists (x_0). The number of evaluations in the recovery is at most gmax (walk to x_q) + 2 gmax (lockstep) = 3 gmax when every gap between consecutive stored points is at most gmax (the halts).

## 4. Success probability (Lemma 2, for a uniformly random function F)

Model H1 (Section 7): F is a uniformly random function from the N = p field elements to themselves, and the DP set (density theta, fixed by the program before the walk) is independent of F. All statements below are theorems for that F; Section 7 declares that the real F behaves so.

(a) The trail. Given x_0, .., x_i with no earlier repeat, x_i was never queried, so F(x_i) is uniform: it equals one of the i + 1 earlier values with probability (i + 1) / N. Hence P(t > n) = prod_{i<n} (1 - (i + 1)/N) <= exp(-n (n + 1) / (2N)). The merge value x_t = x_0 (j = 0, the start on the cycle) has probability at most 1/N at each step: at most n / N in all (it gives no collision).
(b) Detection. Given the equality pattern of x_0 .. x_t, the distinct values x_1 .. x_{t-1} are uniform distinct elements (the pattern's probability does not depend on the values), so the DP flags of any m of them are hypergeometric with no flag with probability at most (1 - theta)^m <= exp(-theta m). A DP in the first min(lambda, d) cycle values makes the detection happen by step t + d, so S = n + d suffices. P(no such DP) <= exp(-theta d) + P(lambda < d), and P(lambda < d, t <= n) <= n d / N (at each step t and each lambda < d the probability that x_t = x_{t-lambda} is at most 1/N).
(c) Table. The number of stored DPs among S fresh values is dominated by Binomial(S, theta): P(more than 2^14) <= exp(-mu) (e mu / 2^14)^(2^14), mu = S theta = 13731.7: the logarithm is -241.08 (`plan`, ln_P_table_overflow).
(d) Gaps. A gap longer than g after a stored point (a DP or the start) has probability at most (S theta + 1) exp(-theta g) (the flags of fresh values are independent); g = gmax: theta gmax = 18. All positions used by the recovery (s, a, q < t) lie among the first t - 1 distinct values, so (d) covers them.
Total failure probability beyond (a): eps = exp(-8) + n d / N + (S theta + 1) exp(-18) + exp(-100) = 1.1230e-3 (the exp(-100) is the table term, with room). The program's n is the least multiple of 2^100 with 1 - exp(-n (n + 1)/2N) - n/N - eps >= 0.39: `plan` gives 0.3900000006. So P_F(success) >= 0.39.

Single attempt: no restart, no amplification, nothing stored from an earlier run, no advice.

## 5. Operation ledger (unit: target compressions; C = 1392)

Machine. Pallas field RAM with 256-bit words (the profile of `orchard-cost-v2.json`): a call of the reference permutation is 1 unit and pays for all its arithmetic, constants and loads; every other word operation costs 1/1392 (the cost model's `word_operation` weight); no operation in the table below is a field operation, so nothing is counted twice.

Trail step (executed at most S times): the call x = F(x): 1 unit; the other operations: step counter add 1, register move of the digest into x 1, AND with the 128-bit mask 1, compare with T 1, branch 1, loop-bound compare 1 and branch 1 = 7 (W_STEP). Recovery evaluation (at most 3 gmax): 1 unit and 8 other operations (the counter, the two register moves, the equality compare and its branch, loop control). All table work (a DP happens at most 2^14 + 2 times; per DP a lookup and a store, at most 2000 operations each with a hash probe), the bisection over stored indices (at most 15 probes, 100 operations each), the random word, the mask, the halts and the report are bounded together by OTHER_FIXED = 10^8 operations (about 7.2e4 units; the true figure is below 10^8 by a factor of 10 or more). The program uses no load or store for its trail variables (registers).

Total: T = S (1 + 7/1392) + 3 gmax (1 + 8/1392) + 10^8 / 1392 = 1.711053e38 units, log2 T = 127.00815. Claimed time_log2 = 127.009 (rounded up). Preprocessing: none (preprocessing_log2 = 0). The claim is the full budget that achieves 0.39 (every halt charged at its limit), as the cost model requires, not an expected running time.

## 6. Memory

Table: 2^14 + 2 entries (the DPs, the start, the closing one) of 48 bytes (32 value, 16 index): 786,528. Code and constants: the permutation (a loop over 64 rounds, at most 150 instructions), the search, the recovery: at most 600 instructions at 36 bytes (256-bit immediates in the instruction word): 21,600; round constants 192 * 32 + MDS 9 * 32 + capacity 32: 6,464; registers (at most 16 words): 512. Sum 815,104 bytes <= 2^20 = 1,048,576. Claimed 2^20, so the memory term of the score is 0.

## 7. Premise H1 (declared, score-critical) and its evidence

H1: on the walk x -> digest(x, 0) the search succeeds with probability at least P_F of Section 4 (F uniformly random, flags independent). The Orchard permutation at 56 partial rounds is not known to have any structure that lowers the collision hazard of a walk of 2^127 steps; no proof is known and none is claimed. The experiments run this program at width 14 (organizer sandbox, real 56-round digest) and the real full-width map for 64 points; they check that every returned pair is a pair of distinct canonical inputs whose digests agree in the stated low bits. They are program checks: no number of the claim is estimated from them.

Sensitivity: if the hazard of a fresh step is (1 - e) / N instead of 1 / N, the budget needs a factor (1 - e)^(-1/2) in n: 0.0072 bit for e = 0.01, 0.0370 bit for e = 0.05, 0.076 bit for e = 0.10.

## 8. Experiments

`rho-n14`: the search of Section 2 at width 14 (the low 14 bits of the real 56-round digest of (v, 0), v below 2^14, DP density 1/16, 256 steps, table 64, gap cap 160): returns the two messages (v, 0), (w, 0) when the search ends with a pair. `proj-w254`: 64 points of the real walk at full width from a seed start; returns two distinct inputs whose digests agree in the low 10 bits. Both use `digest` of `rho.py`, which equals the organizer's digest at r = 56 on the vectors we compared.

## Appendix: `python3 experiments/rho.py --plan`

theta 8.097392835639327e-35 (log2 -113.2500258511542); n 1.6948300785997533e+38; d 9.87972321756372e+34; gmax 2.222937723951837e+35; eps_total 0.0011230430872070788; steps 1.6958180509215098e+38; T_units 1.711053011264217e+38; time_log2 127.00815206332808; mean_stored 13731.704936079681; ln_P_table_overflow -241.08428768200974; success_lower_bound 0.39000000055505574.
