t = open("sec4_mid.md", encoding="utf-8").read()


def rep(a, b, n=1):
    global t
    assert t.count(a) == n, (t.count(a), a[:80])
    t = t.replace(a, b)


rep("so E_S <= Q L / N' = 1.125e-05.", "so E_S <= Q L / N' = 8.139e-06.")
rep("+ PP p2 = 1.020e-06.", "+ PP p2 = 2.962e-08.")
rep("E_J2a = 1.119e-05.", "E_J2a = 8.083e-06.")
rep("so E_J2b <= PP (1 - theta) p2 = 9.516e-07.", "so E_J2b <= PP (1 - theta) p2 = 2.149e-08.")
rep("E_Y <= e^(-(c-1)/L) H = 5.598e-08.", "E_Y <= e^(-(c-1)/L) H = 1.023e-09.")
rep("P(Binomial(n2, p) >= 2) = 5.195e-05 and P_cut = 7.643e-05 (the program's `cut_halt`).",
    "P(Binomial(n2, p) >= 2) = 3.312e-08 and P_cut = 1.631e-05 (the program's `cut_halt`).")
a = t.index("Step 7 (the early halts and the small terms).")
b = t.index("Sensitivity to H1 (d).")
t = t[:a] + '''Step 7 (the early halts and the small terms). The attempt can end before it outputs the pair of Step 3 only by an early halt or by the events E1, E2, N1 >= k: the second cut (P_cut, Step 6); the recovery cap (P_rec, Step 4 (f)); the table full (finished trails are at most N1 + 59 outside 60 or more collisions, so tmax keys need N1 >= tmax - 59: P_table = 2.2e-12); a key false match (P_key = 1.846e-06: the stored ends are at most tmax fresh DP values, uniform on the DP class, and the key space is 2^41 * 1913 = 2^51.90); the stage-1 budget e2max = 2 mu2 + 64, mu2 = Q / 2^32 = 7.895e+28: the fresh stage-1 hits are at most the sum of eta_t = 1[low 32 bits of V_t zero], exactly Binomial(Q, 2^-32), above 1.5 mu2 with probability at most e^(-0.108 mu2); the repeated hits after merges come from at most 60 colliding trails, each repeating at most M points that lie in at most 60 lane windows of total length at most M, and every such union of windows holds more than 2 M / 2^32 hits with probability at most e^(-0.386 M / 2^32), so with 240 M <= Q (checked: M = 5.559e+34, Q = 3.391e+38) the repeated hits are below mu2 / 2 except with probability below e^-1000; the passing-batch budget pmax = 2 mu3 + 64, mu3 = B P13 = 4.076e+34, P13 = 1 - (1 - 2^-13)^256: a batch passes the first 13 planes only if one of its evaluations returns a value with the 13 low bits zero; for the fresh evaluations the batch indicator of some index t of the batch with the 13 low bits of V_t zero is exactly Bernoulli(P13), independent over batches (the V_t are independent and uniform on 256-bit values), so these batches are Binomial(B, P13), above 1.5 mu3 with probability at most e^(-0.108 mu3); the repeated evaluations are the at most 60 windows above, which hold more than 2 M / 2^13 values with the 13 low bits zero with probability at most e^(-0.386 M / 2^13), so with 240 M <= 2^13 mu3 (checked: 1.334e+37 <= 3.339e+38) the passing batches are below 2 mu3 except with probability below e^-1000; a recovery with no pair (a key false match, counted, or a start on another trail, 2^-100). The number of collisions: every fresh evaluation with xi = 0 is a collision with conditional probability at most (t - 1 + 2^17) / N' (L1), so E w^(number of collisions) <= exp((w - 1) H) for w = e^5 (the factor per evaluation is at most 1 + (w - 1)(t - 1 + 2^17)/N' <= e^((w-1)(t-1+2^17)/N')), and P(60 or more collisions) <= exp(-300 + (e^5 - 1) H). P_tiny collects Q 2^17 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-300 + (e^5 - 1) H), and 2^-90 for everything else of this step (the stage-1 and passing-batch budgets, the recovery with no pair) and for the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96). This proves the lemma. QED.
Consequently P_F >= 1 - P_coll - P_delay - P_own - P_long - P_age - P_rec - P_dist - P_cut - 2^-40 - P_key - P_table - P_tiny = 1 - 0.608642804 - 0.001272 - 8.139e-06 - 4.102e-08 - 2.149e-08 - 5.481e-05 - 4.041e-06 - 1.631e-05 - 9.1e-13 - 1.846e-06 - 2.2e-12 - P_tiny = 0.390000001 (float, planned at 0.390000001; the printed terms are rounded), and the exact evaluation of Appendix A is 0.39000000100041 >= 0.39 (B is the least multiple of 10^24 that reaches the planning target).

''' + t[b:]
rep("0.0073 bit for eps = 0.01 (Tp 1378); 0.0370 bit for eps = 0.05 (Tp 1350); 0.0760 bit for eps = 0.10 (Tp 1314); 0.2075 bit for eps = 0.25 (Tp 1199).",
    "0.0073 bit for eps = 0.01 (Tp 1903); 0.0370 bit for eps = 0.05 (Tp 1864); 0.0760 bit for eps = 0.10 (Tp 1815); 0.2075 bit for eps = 0.25 (Tp 1656).")
for s in ("1385", "90,653", "90653", "2^36", "e^2", "-120", "0.99741", "88410", "capr", "47-bit", "7 rounds", "seven"):
    assert s not in t, s
open("proof_3.md", "w", encoding="utf-8").write(t)
print(len(t))
