"""Applies the cold-read fixes to sec4_head_t.md, step6_new.txt, step7_new.txt and reassembles sec4_t.md."""
def edit(path, pairs):
    s = open(path, encoding="utf-8").read()
    for a, b in pairs:
        assert s.count(a) == 1, (path, s.count(a), a[:70])
        s = s.replace(a, b)
    open(path, "w", encoding="utf-8", newline="\n").write(s)


edit("sec4_head_t.md", [
    ("Lemma 2 below is a theorem about F: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F); it has no premise besides H1 (a premise about g, not about F). H1 clause (d) (Section 5) is the premise that the lazy-sampling hazard of F also holds for the adaptive choices of the program (which trails finish, are cut or abort depend on earlier outputs).",
     "Lemma 2 below is a theorem about F with no premise: its inputs are Lemma 1 (a statement about g itself) and the lazy-sampling facts of Step 1 (statements about F, exact for the adaptive choices of the program: which trails finish, are cut or abort depend on earlier outputs). H1 enters only in the passage from A_F to the real attempt; its clause (d) (Section 5) says that g has the collision hazard that F has by construction."),
    ("If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c - 1 coins: probability at most",
     "If t and y are on different lanes the two coin sets are disjoint and g(t), rho(y) - 1 are dominated by independent geometric variables with values in 0, 1, 2, ...; the sum of two such variables is at least c - 1 only if a single i.i.d. sequence of coins has at most one 1 among its first c coins, hence among its first c - 1 coins: probability at most"),
    ("If they are on the same lane and (G1) holds, y is on an earlier trail", "If they are on the same lane and (G1) and (G3) hold, y is on an earlier trail"),
    ("(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane,",
     "(a) (G1) fails: y is among the a(t) earlier evaluations of the trail of t; a(t) is at most g(t), the number of consecutive 0 coins just before t on its lane (g(t) as in Step 6 (ii)),"),
    ("The event W(t, y) is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^16) / N'; summing over the pairs, sum of P(W(t, y)) <= P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^16) / N' = P_dist.",
     "For this bound W(t, y) is taken without the restriction to N1 <= k - 1 and outside E1, E2: it is the event (tau = t, V_t = V_y), which is F_t-measurable, so P(W(t, y) and disturbed) <= P(W(t, y)) L (Q + 2^16) / N'; the events W(t, y) for different (t, y) are disjoint (the values V_y are distinct before tau), so the sum of P(W(t, y)) is at most P(tau <= Q) <= sum over t of (t - 1)/N' = PP: PP L (Q + 2^16) / N' = P_dist."),
    ("each a collision with conditional probability at most (Q + 2^16) / N' given the history (L1).",
     "each a collision with conditional probability at most (Q + 2^16) / N' given the history (L1; the last one, a DP-valued evaluation, is covered by E2, and counting it here only overcounts)."),
])
s6 = open("step6_new.txt", encoding="utf-8").read()
assert "rho(" in s6
s6 = s6.replace("rho(", "sigma(")
open("step6_new.txt", "w", encoding="utf-8", newline="\n").write(s6)
edit("step7_new.txt", [
    ("P_tiny collects Q 2^16 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-300 + (e^5 - 1) H), and 2^-90 for the recovery with no pair, the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96).",
     "P_tiny collects Q 2^16 / N (E1), k^2 L / N' (E2), 255 Q / N' (Step 4 (b)), exp(-300 + (e^5 - 1) H), and 2^-90 for everything else of this step (the stage-1 budget, the recovery with no pair) and for the rounding of the factors 1 - kQ/N' and of the enclosures of Pi (each below 2^-96)."),
    ("- 2^-90 = {Pl:.9f} (float, planned at 0.390000001)", "- 2^-90 = {Pl:.9f} (float, planned at 0.390000001; the printed terms are rounded)"),
])
h = open("sec4_head_t.md", encoding="utf-8").read().replace("{log2keys40}-bit", "{keybits}-bit")
s6 = open("step6_new.txt", encoding="utf-8").read()
s7 = open("step7_new.txt", encoding="utf-8").read().replace("at most 59 colliding trails", "at most 60 colliding trails").replace("at most 59 lane windows", "at most 60 lane windows")
open("sec4_t.md", "w", encoding="utf-8", newline="\n").write(h.rstrip("\n") + "\n\n" + s6.rstrip("\n") + "\n\n" + s7.rstrip("\n") + "\n")
print("ok")
