## 7. Success probability

The probability space is the one uniform 256-bit word of step 1, for the fixed target. The algorithm is otherwise deterministic. The trials depend on that word only through the four words C0.c1, D3.d1, S15 and S9. A run walks {{nd}} * 2^81 = 2^{{trials_walk_log2}} trials. Of the 64 trials of a cluster it EXAMINES the representative always and the 63 neighbours only when the gate opens, and so finds {{cluster_equivalents}} trial-equivalents per representative (6.7, H4): write N = {{nd_eq}} * 2^81 = 2^{{trials_log2}} for the trial-equivalents a run finds, which is what the rate of H1 and the charge of Section 8 are per. The walked range of C0.d1 is 64 / {{cluster_equivalents}} times the range that N alone would need, so that the equivalents a run finds reach N.

Call a trial *good* when R = 0 and the trial satisfies rule A. By 6.4 a good trial is found unless a budget of step 4 ends the run before.

**Heuristic H1 (score-critical).** Over the coins, the N trials behave with respect to the event "good" like independent events of probability at least {{factor}} * 2^-128 = 2^-{{rate_log2}} each, to the extent that the probability that no trial is good is at most exp(-1/2) + 0.002. This is one assumption with two parts: a rate, and that the good trials of a run do not come in clusters. Neither part follows from the other, and neither follows from the model of Section 10. The factor {{factor}} is assumed. Section 10 describes what it is set against: for Y4 in the sub-class and under the seven-word model, a count in integer arithmetic of the solutions of R = 0 that satisfy rule A, {{kept_exact}}, and the smaller figure {{kept_cons}} that leaves out every outcome of the count in which some solution violates rule A; participant computations, of which the first equals the fraction of another AI model and the second is the participant's alone. The organizer-run experiments do not measure the factor.

**Heuristic H2 (supporting).** With probability at least 0.9995 over the coins, fewer than 2^{{pass_budget_log2}} of the N trials pass the E1 test of Lemma N without having R = 0. (The budget corresponds to a pass rate of 2^-{{pass_rate_budget}}. The pass rate measured on real trials of the whole class in the arrangement of this package is 2^-31.41, which would give 2^{{pass_expected}} passes, below the budget by a factor of more than 2^{{pass_room}}; in the sub-class the graphics-card run of Section 10 counts 9,537 passes of the E1 test in 2^44.585 trials, a rate of 2^-31.37. Step 3 processes only the passes that lie in batches that ran stage 2, which are fewer. That the number of passes of one run stays near this mean is part of the assumption.)

**Heuristic H3 (supporting).** With probability at least 0.9995 over the coins, fewer than E of the batches of a run hold a trial that satisfies rule A, where E is the budget of step 4, just under one in {{share_inv}} of the batches. (A batch runs stage 2 exactly when one of its trials satisfies rule A. In every context the number of such batches is at most the number of trials that satisfy the rule; so H3 holds whenever fewer than E trials of the run satisfy rule A, a share of {{trial_share}} times 2^-8 of the trials, where a uniform h1 satisfies the rule with probability 2^-8. H3 is a statement about the total over a run and is not true context by context. Measured on 2^30 real trials of the sub-class, three times, the share of the batches that run stage 2 is {{entry_1}}, {{entry_2}} and {{entry_3}}, against the budget {{budget_share}}; single contexts have between {{ctx_min}} and {{ctx_max}}, so a single context can exceed the budget on its own batches; the averages of 512 outer steps over 16 values of X2 each lie between {{outer_min}} and {{outer_max}}. That the average over the outer steps of one run stays below the budget, with the room of {{entry_room}} percent that these samples show, is the assumption.)

**Heuristic H4 (score-critical, new in this package).** Over the coins, the number of trials found to satisfy rule A
per representative, divided by the probability that a trial satisfies rule A, is at least
{{yield}} on the run as a whole. This is the yield of 6.7. It is a measured mean, not a count: Section 10 reports
three independent measurements of it on real messages, and a spread of about 14 per cent between outer steps. The
charge of Section 8 divides by {{cluster_equivalents}} trial-equivalents per representative, which is one for the
representative and {{yield}} for its neighbours, so the claimed time is proportional to 1 / (1 + {{yield}}) and a
yield lower by one part in ten raises the claimed time by about 0.15.

**Heuristic H5 (score-critical, new in this package).** Over the coins, the trials that this algorithm examines
carry, per trial, at least the collision mass that rule A keeps on average over the whole sub-class, and the good
trials of a run do not come in clusters any more than H1 already allows. The first part is the question whether
selecting a trial because its representative passed the gate biases the trial: Section 10 reports measurements that
find no bias (one part in two thousand on one side of the event and three parts in a thousand on the other), and the
exact model of Section 10 shows that the collision mass of a member does not depend on the three bits of e1 that the
clusters flip. The second part cannot be measured: the collision has probability about 2^-{{r_sub_prob}} per trial,
and the deepest events these tools reach are about 2^-32 and 2^-40. What is measured is clustering of rule-A passes
inside a cluster, which is slightly NEGATIVE (a passing neighbour next to a passing neighbour carries one of the
four heavy first-side values 3.0 per cent less often than independent trials). Trials of one cluster share their six
outer words and differ in three bits of X2 and three bits of e1, so this is the assumption of this package that a
reviewer should test first; Section 10 says what would settle it.

Under H1, H2 and H3 the algorithm outputs a collision with probability at least 1 - exp(-1/2) - 0.002 - 0.0005 - 0.0005 > 0.3934 - 0.003 = 0.3904 >= 0.39: by the union bound over the three events "no trial is good", "the budget of step 3 is reached" and "the budget E is reached", which need not be independent. H1 is read here over the trials this algorithm EXAMINES, which H5 asserts carry at least the average mass of the trials rule A keeps; H4 and H5 do not enter that union bound, because they are about the charge and about the trials examined, not about a budget being reached. If H5 fails, the number of trial-equivalents of a run falls short of N and the success probability falls with it; if H4 fails, the charge of Section 8 is too low by the ratio. When it outputs a pair, the pair is a genuine collision: step 3 checks both complete digests, and the messages have different lengths.

*Sensitivity to the factor.* If the rate of good trials is f * 2^-128, the N trials give 1 - exp(-f * {{nd}} / 2^47) - 0.003 with the same allowances, which reaches 0.39 only when f is at least {{f_min}}: the assumed {{factor}} leaves no slack on the probability side. The margin of the claim lies between the assumed {{factor}} and the counted {{kept_cons_int}}, a factor of {{margin}}. It is nominally the margin of entry c66f230d, but it is tighter. There 3.75 was the ratio to a figure that left out about 18 million of the exact count with rule A, and that count and the whole count were {{filed_margin_exact}} and {{filed_margin_all}} times the factor 2^25. Here the rule loses almost nothing, and the three figures, {{kept_cons_int}}, {{kept_exact_int}} and {{r_sub_int}}, are {{margin}}, {{margin_exact}} and {{margin_all}} times the factor. For an f between 1 and {{factor}} the same success probability needs 2^127 / f trials and, at the same {{charge}} operations per trial, the total of Section 8 is below 2^({{uniform_bound}} - log2 f): below 2^{{bound_2dec}} at the assumed factor, and below 2^{{uniform_bound}} at f = 1, the uniform rate, where the package would submit {{uniform_claim}}. With the more cautious f = 2^25 = 33,554,432, the factor of entry c66f230d, which is {{margin_2_25}} times below the count, the same package would search 2^102 trials, with C0.d1 below 2^21, and would submit {{claim_2_25}}.

*Remark on clustering.* H1 asks for more than a rate: it asks that the good trials do not come in clusters. Under M the count of Section 10 gives {{kept_cons_int}} * N / 2^128 = {{expected_good}} expected good trials in a run, or more, where H1 needs 0.5. Suppose that these trials came in clusters of m on average and that the clusters fell independently. Then a run would contain one with probability about 1 - exp(-{{expected_good}} / m), and the bound 0.39 would hold for m up to {{cluster_m}}. So if the counted rate is right, the bound survives a clustering of the successes by that factor. This is a remark and not a proof: the counted rate rests on M, and nothing here bounds m. Two dependences are measured and stated in Section 10: the share of the trials that satisfy rule A depends on the context, and the rates of single events of E1 depend on the outer step.

None of the three heuristics is proved. Section 10 lists the evidence.

## 8. Charged time

One 2-round target compression costs one unit and every other primitive word operation, every load and every store included, costs 1/C units with C = 430.

**The cost, with every term.** The clusters of 6.7 change what a cost is per. Stage A runs on a
REPRESENTATIVE word, not on every member, and a trial of a cluster is examined only when its representative passes
the gate; what the charge is per is therefore a TRIAL-EQUIVALENT, the collision mass that rule A keeps on one trial
of the sub-class on average. A representative yields {{cluster_equivalents}} of them: one for itself and
{{yield}} for the neighbours its gate opens (H4). The table below is per representative, and the last two rows
divide by {{cluster_equivalents}}.

Let R = {{reps}} be the representatives of one value of X2 and {{rep_words}} the packed words that hold them.

| Term | How often | Per representative |
| --- | --- | ---: |
| stage A and the gate, per representative | always | 71 / 7 |
| the dispatch of the lanes a gate opens | {{gate_share}} | 513 / 16 |
| a word entering stage 2, inputs placed | {{entered_share}} | {{entered_word}} |
| lists, table and middle cache | amortised, 6.7 | {{cluster_overhead}} |
| **budgeted, per representative** | | **{{cluster_per_rep}}** |
| **budgeted, per trial-equivalent** | | **{{budgeted}}** |
| charged, per trial-equivalent | | **{{charge}}** |

The first three rows are machine counts of the program (Section 10); the budget of the neighbour path is
{{budget_factor}} times its measured share, as 6.4 budgets the entry to stage 2. The charge is {{charge_margin}}
per cent above the budget. The cost table of the entry this package improves on, which charges {{nocluster_charge}}
per trial without clusters and claims {{nocluster_claim}}, is Section 12.

The first five terms are machine counts of the program. The term "loop control" is a bound stated in words in 6.4 and is not a machine count. The charge is {{charge_margin}} percent above the budgeted cost; that difference is margin for operations that a reader may find uncounted, {{charge_room}} per batch of seven trials.

- **Main loop.** For one value of X2 the {{members}} members take {{list_words}} batches: {{full_words}} full ones and one that holds the last four members and is charged in full. A run has {{nd}} * 2^64 values of X2 in {{nd}} * 2^32 outer steps, and so {{list_words}} * {{nd}} * 2^64 batches. Every batch runs stage A, {{a_total}} primitive operations by 6.5, memory loads included. By step 4 fewer than one batch in {{share_inv}} runs stage 2, {{s2_total}} operations each. On every run the main loop therefore costs at most {{nd}} * 2^64 * P operations with P = {{p_x2}}, which is less than {{budgeted_up}} per trial. It is charged {{charge}} per trial, that is {{charge}} * N operations. This is the budgeted cost, a bound for every run. The expected cost is lower: if the trials of a batch satisfied rule A independently with probability 2^-8, a share of {{indep_share_6}} of the batches, which rounds to {{indep_share}}, would run stage 2 and a trial would cost {{expected}} operations on average; the measured share is lower still (H3).
- **Per outer step.** Nothing is charged separately: the outer step and the build of the table are machine counts and are in P.
- **Lists.** The lists U and V are computed once from eta, the sub-class, Y3 and the rule: {{members}} members at fewer than 64 operations for each list, 2^24 operations.
- **Passes of the E1 test.** At most 2^{{pass_budget_log2}} are processed (step 4). The batch keeps no values of a passing trial. Its batch is evaluated again, both stages, and the rest is added in the same packed form: Y9 by the sixth and seventh assignment of C1; the b output of E1 for A and for B; S0 by the first five assignments of K0 from the stored words w0 and w1, then D0.a1 and w8; y from the list word U[j]; E3 for A and for B; the four words of R, their comparison with zero in the lane of the trial, the count of the processed trials, and the nine loads that put the kept words back into their registers. That is below 2^10 operations each: 2^{{pass_ops_log2}} operations, a share below 2^-{{pass_share}} of the main loop. This bound is stated in words and was not written out on the machine.
- **Final step.** Steps S2, S3 and two complete hash evaluations with their input handling: below 2^11 operations and 2 units, once.
- **Randomness.** One random word, charged as one operation.
- **Preprocessing.** The six constants of 3.2, the word eta, the two bits of the sub-class and rule A with the plan of its test are stored in the program. The constants were found by a solver search and chosen by the count of Section 10; the sub-class and the rule were read off exact counts of the same kind. Two different figures are involved, and this text keeps them apart. (1) A bound: a pair (W4, W13) with the property of Fact P and a zero top byte of W13, for the four given inputs X3, X7, X11, X15, is found by exhaustive search over at most 2^64 candidates at two G evaluations and a comparison each, below 128 operations: 2^71 operations, below 2^63 units. This bound covers the recomputation of those two words and nothing else. (2) An estimate: the solver search that produced all six constants and the counts by which the constants, eta, the sub-class and rule A were selected used fewer than 2^60 primitive operations in total, by the participant's estimate from the running times; that is not a count and not a bound, and no bounded algorithm for the selection is given. The measurements on real and on scaled-down messages of Section 10 test the heuristics and select nothing; they are not part of this figure, and some of them ran on graphics cards for hours.

Total:

    T <= ({{charge}} * N + 2^{{pass_ops_log2}} + 2^60 + 2^24 + 2^11 + 1) / 430 + 2 + 2^63
       <  {{charge}} * N * (1 + 2^-7) / 430 + 2^64
       <  2^{{bound_4dec}} + 2^64
       <  2^{{bound_2dec}}.

Here N = {{nd}} * 2^81 = 2^{{trials_log2_6}} and {{charge}} * N / 430 = 2^({{trials_log2_6}} + {{charge_log2}} - {{l430}}) = 2^{{main_log2}}; the three logarithms are rounded so that the result is not too small. The terms after the first add up to less than 2^{{side_log2}}, which is below {{charge}} * N * 2^-7, itself more than 2^{{allow_log2}}, and log2(1 + 2^-7) < 0.01123. The submitted bound is time_log2 = {{time_log2}}, the total rounded up to one decimal. The 2^60 in the first line is the estimate (2) above, entered as if it were a bound; if the selection had cost 2^90 operations instead, the total would still be below 2^{{bound_2dec}}. This is a worst-case bound for the algorithm as stated, which halts within its two budgets on every run.

The algorithm has no sorting and no lookup by value: a trial is tested against zero, not against other trials. It has three kinds of lists, all read in the order of the list position: the fixed list U, read once per outer step by the build; the fixed list V, read by stage A; and the table of the current outer step, five words per list word, written once per outer step and read by the batches of all its 2^32 values of X2. Their loads are counted, 1 of the {{build_loads}} loads of the build, 3 of the {{a_loads}} loads of stage A and 4 of the {{s2_loads}} loads of stage 2, and so are the 5 stores per list word. One table word serves seven members times 2^32 values of X2; that this is allowed is Lemma T4 (b). If a table had to be built for every value of X2, the build would add {{build_per_trial_alone}} operations per trial.

## 9. Memory, preprocessing and advice

The program is the lines of steps O, M, Y and T, the four packed pieces of 6.5 and a compression routine for the final check. Bound the code by 4096 instruction templates of at most four 256-bit words each: 2^14 words, which is 2^19 bytes. Data, one packed word of 256 bits each: the table of one outer step (5 * {{list_words}} words), the lists U and V (2 * {{list_words}}), and fewer than 512 words for the cells of the outer step and the middle step, the context, the fixed constants and masks, the temporaries and the two messages and digests of the final check: fewer than {{mem_words}} words, that is {{mem_bytes}} bytes. The memory of the search is therefore below 2^19 + {{mem_bytes}} < 2^{{search_mem_log2}} bytes. Nothing grows with the number of trials: the table is overwritten at every outer step.

*Memory of the preprocessing.* The computations by which the constants, the class, the sub-class and the rule were selected needed far more memory than the search. The solver search and the counting programs ran on a desktop machine and stayed below 16 GB of main memory, 2^34 bytes; the sampling programs and the programs for real messages stayed below 10 GB of the memory of one graphics card. These two limits are the participant's observation of the runs, not instrumented peaks. memory_log2_bytes = 35 covers both at once, 2^34 + 10 * 2^30 < 2^35 bytes, and with them the search. The cost model does not score memory.

preprocessing_log2 = 63 is the bound (1) of Section 8 for recomputing the two pinned message words at the four given inputs. It is not a bound for the selection of the four inputs, of eta, of the sub-class or of rule A; for that selection the text has only the estimate (2) of Section 8, which is below 2^63 units and is the participant's. Both are included in T. nonuniform_advice_log2_bytes = 6 covers the 28 bytes of the six constants and eta, the 8 bytes that name the two bits of the sub-class and their values, and the 12 bytes of the two masks and the word ALL of Lemma A, 48 bytes in all. The lists U and V are not advice: the program computes them from these constants by Lemmas Q2 and A. There is no other stored data and no stored collision.
