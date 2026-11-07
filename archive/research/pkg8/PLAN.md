# pkg8: the cluster package for the 55/63 path (plan, main session, 2026-10-07 about 01:30)

Draft target: time_log2 about 93.1 to 93.5 at margin 3.75 (estimate; the charge step decides). NOT to be filed
without the owner's approval. Owner's direction: do every check we can and state plainly in the text what we could
not test (memory `do-our-best-admit-limits`).

## Base

The FINAL text of research\pkg7 (after its correction pass fix3 and its evidence pass), with its program as the
experiment (research\pkg7\blake3-r2\experiments\halfsearch.py, validated; it demonstrates the trials, the sub-class
and the first-stage rule on real messages). If the program attempt of research\pkg8\program succeeds and passes its
self-test, use it instead and say so.

## What is added to the pkg7 text

1. Claim: the new charge per trial-equivalent and time_log2 from research\pkg8\charge\COST8.md (cross-checked
   against Grok job24 and, when the owner relays it, Sol's gpt_sol_answer_U2.md). Kept mass of K8 in C15:
   185,358,111.47; with the cheap second-stage test 185,351,809 (gpt_sol_answer_O.md section O4).
2. A section "The cluster procedure": representatives (e1 bits 14, 30, 31 and X2 bits 14, 30, 31 zero), the 63
   neighbours, the gate H4 on the representative, the rule K8 for stage 2; why it pays (the four parities of H4
   survive the six flips with 0.905 to 0.983, the other conditions of K8 do not).
3. Lemma (partition): every trial of the sub-class lies in exactly one cluster; the first stage runs on each trial
   at most once (gpt_sol_answer_U.md section 2, with its proof; checked by enumeration in
   research\pkg8_program\verify\VERDICT8.md).
4. The gate is optimal for these flips: among all 200,787 rank-4 relaxations of K8, and among ranks 0 to 8, H4 has
   the lowest exact cost (gpt_sol_answer_T.md section 5).
5. Yield: neighbours found per trial-equivalent S' = 40.02, measured three times independently
   (research\h8\cluster2\measure\MEASURE.md 40.018 se 0.012; research\pkg8_program\verify 40.032 se 0.075;
   research\grok\work\job22_gated 40.027); it varies by about 14 percent between outer tuples. A MEASURED MEAN, a new
   kind of figure in a claim: say so.
6. Mass per examined trial: no selection bias found (research\h8\cluster2\bias\BIAS.md: 0.99950 +- 0.00036 on the
   h1 and member side, 1.0017 +- 0.0030 on the side-1 tally; research\pkg8_program\evidence\EVIDENCE8.md). The exact
   factor F of gpt_sol_answer_S.md does not apply to a corner representative with a weaker gate; its re-derived form
   is in gpt_sol_answer_U.md section 6 / T section 3. State F as measured, with its error.
7. Evidence of the procedure end to end: the toy test research\pkg8\toy (if it exercises a gate carried to the
   neighbours) and the earlier ones (research\h8\cluster\small; research\h8\cluster2\bias section 5), with their
   limits.
8. Heuristics: those of pkg7, plus: the yield of a run equals the measured mean; the mass per examined trial equals
   the class average; clusters do not clump collisions beyond what the success bound absorbs (BIAS.md section 3).
9. Limits, plainly: what our agents could not test (the neighbour path not run end to end in the submitted program,
   if so; the yield and F measured, not proved; the budget of the neighbour path measured, not proved, with the
   largest share seen for one X2 at 1.72 times the mean), and that teams with more resources can test them.
10. Credits: as pkg7 (winglock, Th0rgal, 5kyguy, tekkac in the co-author field, if the owner keeps that choice for
    this package too) plus: the bit-level checker helper that found the neighbour effect; the measuring helper that
    found the gate-weaker-than-rule design; Grok 4.7 (hostile review of the idea, independent re-measurement, the
    exact program equations, the charge count); GPT Sol 6.1 (gate optimality, partition proof, charge audit); the
    cloud Opus 5.5 if its results are used.

## Order of work

charge (running) -> pkg7 final text -> pkg8 text built from it -> validation -> three reviews + Grok hostile review
-> fixes -> research\pkg8\MORNING.md for the owner.
