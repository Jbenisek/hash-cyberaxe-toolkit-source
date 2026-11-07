t = open("sec4_src.md", encoding="utf-8").read()


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:80])
    t = t.replace(a, b)


rep('''Lemma 1 (a statement about g itself, no premise). A pair x != y of evaluated inputs on two different finished trails with g(x) = g(y) is output: both trails continue identically from g(x), so they end at the same DP with the same key and
pass 1 of step 6 recomputes the two lengths and pass 2 aligns and walks them; it returns the first merge pair, found within max(l1, l2) <= capr batches (a trail is cut at a slice check once its age is >= c, slice checks are S batches apart, so every length is below c + S). The returned pair satisfies g(x) = g(y) with x != y, so f(x) = f(y); the recovery checks equality before it returns.
The key determines F (F < 1385 <= 2^11 and the key holds its 11 low bits), so equal keys of two DPs differ only if their bits above 157 differ. The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its lane is flagged and examined. A 47-bit key match without a merge ends the run (failure, cost bounded by one recovery).''',
'''Lemma 1 (a statement about g itself, no premise). Let x != y be evaluated inputs on two different finished trails with g(x) = g(y), both trails of length at most c_r. Both trails continue identically from g(x), so they end at the same DP with the same key and step 6 runs on them. Pass 1 reaches both DPs within c_r steps and keeps the checkpoints. With A the longer trail and d = l1 - l2, P(j): A_(j+d) = B_j holds for j = l2 (the common DP) and, once true, stays true (A_(j+1+d) = g(A_(j+d)) = g(B_j) = B_(j+1)); P(0) is false because the start of B is not on A (B joins A at its point after y, which is not its start). The bisection keeps P(lo D) false and P(min(hi D, l2)) true, so the first j with P(j) true lies in (lo D, min(hi D, l2)], and the joint walk from A_(lo D + d), B_(lo D) reaches it within D steps; the pair returned there is a merge pair: a != b and g(a) = g(b), so f(a) = f(b). The recovery checks equality before it returns. Pass 2 needs at most 17 D batches (Section 3.3).
The key determines F (F < 1913 <= 2^11 and the key holds its 11 low bits), so equal keys of two DPs differ only if their bits above 162 differ. The table returns the stored trail number of a key exactly: the slot of an entry and the run structure give its 16 quotient bits, the slot stores the other 36 (Section 7). The lanes do not interact: the generated step applies the same function to every lane (Section 3.2), so lane l holds g^b of its start after b batches, exactly as a single scalar chain would.
The stage-1 test loses no event: a DP has its 32 low bits zero, so its batch passes the first 13 planes and its lane is a hit. A 52-bit key match without a merge ends the run (failure, cost bounded by one recovery).''')
rep('''Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 0.99741 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) = ceil(t / 256) the batch of t; N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(16 L) = 61422809913526798459092889428117006, S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 88410.08, tmax = 90,653, CMAX = 1 (the program halts when a second trail would be cut). Pi_m = (1 - 0/N')(1 - 1/N') ... (1 - (m-1)/N') is the probability that m independent uniform values of a set of N' elements are distinct. PP = Q (Q - 1) / (2 N') = 0.49741, H = (Q (Q - 1) / 2 + 2^17 Q) / N' = 0.49741. Let k = 90634 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 257, p = e^(-c/L) >= (1 - theta)^c, p2 = e^(-(c-1)/L) (1 + (c - 1) theta / (1 - theta)), and tmax = 90,653.''',
'''Lemma 2 (for the random function F; no premise). Let LANES = 256, B batches, Q = 256 B = 0.99652 * 2^128 evaluations numbered t = 1, ..., Q batch by batch and lane by lane inside a batch, b(t) = ceil(t / 256) the batch of t; N = 2^256, theta = Tp / 2^122 = 1 / L, c = ceil(20 L) = 55587161350127166666128889086475466, c_r = ceil(12.4 L), S = 2^48, M = c + S, N' = (1 - theta) N, q = Q / L = 122005.65, tmax = 124,633, CMAX = 1 (the program halts when a second trail would be cut). Pi_m = (1 - 0/N')(1 - 1/N') ... (1 - (m-1)/N') is the probability that m independent uniform values of a set of N' elements are distinct. PP = Q (Q - 1) / (2 N') = 0.49652, H = (Q (Q - 1) / 2 + 2^17 Q) / N' = 0.49652. Let k = 124616 be the least integer with e^-q (e q / k)^k <= 2^-40, n2 = k + 257, p = e^(-c/L) >= (1 - theta)^c, p2(x) = e^(-(x-1)/L) (1 + (x - 1) theta / (1 - theta)) (decreasing for x > 2), p2 = p2(c).''')
rep('''    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = Pi_Q / (1 - k Q / N') = 0.608103896   (the first collision exists),''',
'''    P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_rec - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny,
where
    P_coll = Pi_Q / (1 - k Q / N') = 0.608642804   (the first collision exists),''')
rep('''of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.001757   (the merged''', '''of (Pi_a - Pi_b) e^(-theta (B - ceil(b / 256))) = 0.001272   (the merged''')
rep('''    P_own = Q L / N' = 1.125e-05   (the first''', '''    P_own = Q L / N' = 8.139e-06   (the first''')
rep('''((1 - p) N') = 1.796e-06   (its partner''', '''((1 - p) N') = 4.102e-08   (its partner''')
rep('''    P_age = PP p2 = 9.516e-07   (the merged trail is too old when it reaches the DP),''',
'''    P_age = PP p2 = 2.149e-08   (the merged trail is too old when it reaches the DP),
    P_rec = 2 PP p2(12.4 L) = 5.481e-05   (one of the two trails is longer than c_r, so pass 1 of the recovery halts; p2(12.4 L) >= p2(c_r)),''')
rep('''    P_dist = PP L (Q + 2^17) / N' = 5.597e-06''', '''    P_dist = PP L (Q + 2^17) / N' = 4.041e-06''')
rep('''(Step 6) = 7.643e-05, with E_S''', '''(Step 6) = 1.631e-05, with E_S''')
rep('''    P_key = C(tmax, 2) / (2^kb Tp) = 4.3e-05, kb = 36,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 2.4e-12,
    P_tiny = Q 2^17 / N + k^2 L / N' + 255 Q / N' + exp(-120 + (e^2 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q, which holds here).
The numbers are printed by `python3 bsrho.py --loss` (the function `_lossq`) and Appendix A recomputes the whole bound in exact rationals and 60-digit decimals (`certify`, outward rounding) and asserts the result >= 0.39: P_F >= 0.390000001000 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^24 for which the float bound reaches 0.390000001 (Appendix A).''',
'''    P_key = C(tmax, 2) / (2^kb Tp) = 1.846e-06, kb = 41,
    P_table = e^-q (e q / (tmax - 59))^(tmax - 59) = 2.2e-12,
    P_tiny = Q 2^17 / N + k^2 L / N' + 255 Q / N' + exp(-300 + (e^5 - 1) H) + 2^-90 (Step 7; it needs 240 M <= Q and 240 M <= 2^13 B P13, which hold here).
The numbers are printed by `python3 bsrho.py --loss` (the function `_lossq`); Appendix A gives the bound evaluated in exact rationals and 60-digit decimals with outward rounding: P_F >= 0.39000000100041 >= 0.39 (the program's float value, planned at the target 0.390000001, is 0.390000001). The program's B is the least multiple of 10^24 for which the float bound reaches 0.390000001.''')
rep('''(G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, and that it is undisturbed''',
    '''(G4) rho(y) <= B - b(t) and a(t) + rho(y) <= c - 1, (G5) a(t) + rho(y) <= c_r - 1 and a(y) + rho(y) <= c_r - 1, and that it is undisturbed''')
rep('''The two trails are different (G1), finished, with the same key, and the inputs of t and of y are different (t is fresh) with g(t) = g(y): Lemma 1 applies. QED.''',
    '''The two trails are different (G1), finished, with the same key, of lengths a(t) + 1 + rho(y) and a(y) + 1 + rho(y), both at most c_r (G5), and the inputs of t and of y are different (t is fresh) with g(t) = g(y): Lemma 1 applies. QED.''')
rep('''(e) Disturbance.''', '''(f) (G5) fails. The first part, a(t) + rho(y) >= c_r, is the second part of (d) with c_r in place of c: probability at most p2(c_r) per pair. The second part, a(y) + rho(y) >= c_r: the evaluations of the trail of y up to y are fresh and not DPs, so a(y) <= g(y), and xi_y = 0; the g(y) coins 0 before y, the coin of y and the rho(y) - 1 coins 0 after it form a run of 0s of length at least c_r, and the coins before and after y are disjoint and dominated by independent geometric variables, so the probability is at most p2(c_r) as in (d). At most Q (Q - 1) / 2 pairs, each with hazard at most 1 / N': 2 PP p2(c_r) <= 2 PP p2(12.4 L) = P_rec.
(e) Disturbance.''')
rep('''the attempt succeeds unless one of the failures (a) to (e) occurs for the first collision, or E1, E2, N1 >= k occur, or the run halts early: P_F >= 1 - P_coll - 2^-40 - P_own - P_long - P_delay - P_age - P_dist - 255 Q / N' - P(E1) - P(E2) - P(early halt). The early halts are charged in Step 6 (second cut) and Step 7 (table full, key false match, stage-1 budget).''',
    '''the attempt succeeds unless one of the failures (a) to (f) occurs for the first collision, or E1, E2, N1 >= k occur, or the run halts early: P_F >= 1 - P_coll - 2^-40 - P_own - P_long - P_delay - P_age - P_rec - P_dist - 255 Q / N' - P(E1) - P(E2) - P(early halt). The early halts are charged in Step 6 (second cut) and Step 7 (table full, key false match, stage-1 and passing-batch budgets).''')
open("sec4_mid.md", "w", encoding="utf-8").write(t)
print(len(t))
