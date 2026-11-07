## 10. Evidence, scope and field meanings

**What is exact.** Sections 2 to 5 and Lemmas Q, T, E, N and A. Lemma A
says what stage A tests, not that a collision passes it. The declared
experiment `half-collision` runs one trial of 6.1 per organizer seed, with
the seven words of a context and a member number taken from the seed, and
the organizer recomputes both digests; Lemma T predicts that every trial
agrees on the 128 masked digest bits.

*What is new in the exact part and who has checked it.* The length pair,
step S1, step T and Lemmas S, F and Y are new against the submissions named
below; Lemmas L, H, Q, E, N and A are those of the earlier text with the
new constants, and Lemma A is restated for a rule with a condition that
joins two bits of z (in this rule two neighbouring bits; the submitted
program handles any distance). The proofs of Lemmas S, F and Y are written out
assignment by assignment in Section 4. {{exact_review_sentence}}
Machine checks of the same statements are reported under "Checks of the
construction on real messages" below; they are checks on random inputs,
not proofs.

**The seven-word model.** By 6.2 the residual of a trial is a function of
the constants and of seven 32-bit words: for E1 its first-half values d1 and
b1 and its a output a2 on message A, and for E3 the words Y4, Y9, w8 and its
first-half value h1 on message A. (E1's a1 and d1 are the same for A and B,
so a1 enters only through d1 and a2; each of the seven words is a bijective
image of one input or message word of its call when the others are fixed.)
In the algorithm Y4 takes every member of the class equally often. The model
M says that over the trials the other six words behave like independent
uniform words, independent of Y4. Under M a trial has R = 0 with probability
r * 2^-128, where r * 2^{{sol_exp}} is the number of solutions of R = 0 among the
2^{{space_exp}} values of the seven words with Y4 in the class. Call r the *class
rate*. Rule A is a condition on h1, one of the seven words, so under M the
trials with R = 0 that satisfy rule A have a rate of the same kind, r_A,
which counts only the solutions that satisfy rule A; r_A is at most r. H1
is M together with r_A >= {{factor}}.

Given M, the class rate is a property of the constants and the class alone:
the number of solutions of a system of equations in seven words. It can be
counted without sampling, and this section describes the count. The count
says nothing about whether M holds. In a trial the six words are not free:
within one context each of them is a function of Y4. M is therefore a
statement about averages over the contexts of a run, and the measurements
below show one place where it fails inside a single context.

**How r is counted (participant computation, not organizer-verified).**
Write tau, eps for the XOR differences between A and B of E1's a and c
outputs and beta for that of its first-half b. As in the proof of Lemma E,
E1's d and b output differences are ROR(tau, 8) and ROR(beta XOR eps, 7),
and E3's d and b output differences are ROR(eta XOR eps', 8) and
ROR(psi XOR tau', 7), where eta, psi are the XOR differences of E3's
first-half d and b and tau', eps' those of its c and a outputs. So R = 0
holds exactly when tau' = tau, eps' = eps, psi = tau XOR ROR(tau, 1) and
eta = eps XOR ROL(beta XOR eps, 1). For Y4 in the class the left side of the
last equation is the constant {{eta}}.

1. *The betas.* beta is a function of d1 alone: with c1 = Y11 + d1 and
   DY11 = Y11' - Y11 = {{DY11}}, beta = ROR(c1 XOR (c1 + DY11), 12). As in
   Lemma Q, the d1 with a given beta are those for which c1 has prescribed
   bits on the mask ROL(beta,12) AND 7fffffff; they are a share 2^-k of all
   d1, where k is the number of bits of the mask. Only finitely many words
   occur as beta, and they can be listed by increasing k.
2. *The outcomes of one beta.* An outcome is a pair (tau, eps). In E1,
   a2' = a2 + delta + (b1' - b1), and b1' - b1 = (b1 XOR beta) - b1 is a
   signed sum over the bits of beta. So tau = a2 XOR a2' is one of the XOR
   differences that an addition can show when its additive difference is
   delta plus such a signed sum. These words are enumerated by a
   depth-first search over the bits of tau, lowest first, with a carry
   automaton that keeps, for every carry, the number of sign choices on the
   lower bits of beta that lead to it; a branch ends when no sign choice is
   left. No bound is put on the weight of tau. For eps, the last equation
   above says eps XOR ROR(eps, 1) = beta XOR ROR(eta, 1). A word has the
   form eps XOR ROR(eps, 1) exactly when its weight is even, and then for
   exactly two words eps, each the complement of the other. So a beta for
   which beta XOR ROR(eta, 1) has odd weight contributes nothing, and every
   other beta has two candidates for eps.
3. *The E3 side.* For an outcome, N3 is the number of quadruples
   (Y4, h1, Y9, w8) for which E3 produces eta, psi, eps and tau; all of
   them have Y4 in the class. For a word x and a mask m, (x XOR m) - x is
   the signed sum over the bits i of m of (1 - 2 x_i) 2^i, so an addition
   whose XOR output difference is prescribed fixes the bits of its result
   on that mask once its additive input difference is known. E3 has four
   such additions. Their additive differences are the constant Y3' - Y3 and
   three signed sums (over the bits of eta, psi and ROR(eta XOR eps, 8));
   the admissible values of those three are enumerated with a carry
   automaton, and for each choice the number of completions is a product of
   two carry automata, one for Y4 against e1 = Y3 + Y4 and one for g1 + h2.
   When the enumeration exceeds a work budget the program uses a uniform
   random subset with the matching weight; it reports every outcome for
   which it did, and such a value is an estimate and not a count.
4. *The E1 side.* For an outcome, P1 is the probability that E1 produces
   tau and eps when d1 is uniform among the values with this beta and b1
   and a2 are uniform. Put nu = ROR(tau, 8), the XOR difference of E1's d
   output. Two additive differences are involved: db = b1' - b1, a signed
   sum over the bits of beta, and dd = d2' - d2, a signed sum over the bits
   of nu. The first must make the addition a2 + (delta + db) show tau, the
   second must make the addition c2 + (DY11 + dd) show eps. For every such
   pair (db, dd) the bits of a2 on tau, of d2 on nu and of c2 on eps are
   prescribed, and the number of pairs (c1, a2) that have them is counted
   by an automaton over the bits of c1 with two state bits, the borrow of
   d1 = c1 - Y11 and the carry of c2 = c1 + d2. A triple (c1, b1, a2)
   determines db and dd, so the counts of the pairs (db, dd) are added.
   When the list of the db or of the dd exceeds a limit the program falls
   back to a product formula that treats the additions as independent; it
   reports every outcome for which it did, and such a value is not a count.
5. *The sum.* The class-rate part of a beta is 2^({{share_exp}} - k) times the sum
   over its outcomes of P1 * N3. Here {{share_exp}} is the number of bits that
   Lemma Q fixes, so that the class is a share 2^-{{share_exp}} of all Y4. r is the
   sum of the parts over all betas: the sum of N3 over all 2^96 values of
   (d1, b1, a2) is r * 2^{{sol_exp}}, and 2^96 / 2^{{sol_exp}} = 2^{{share_exp}}. Parts are not
   negative, so the sum over any set of betas is a lower bound for r.

Steps 1 to 5 use no random number unless one of the two fallbacks of steps
3 and 4 is taken. The arithmetic is double-precision floating point: sums
and products of integers, with a relative rounding error of 2^-53 per
operation once a value exceeds 2^53.

**The count for this package.** {{count_paragraph}}

{{exact_table}}

{{exact_table_paragraph}}

**An independent recount (another AI model, checked here).**
{{recount_paragraph}}

*The outcomes of the heaviest beta.* The counting program is not part of
this package. So that the largest part of the count can be recomputed
without it, the outcomes of the heaviest beta are written out here.

{{outcome_table}}

{{outcome_paragraph}}

**Rule A and the count that the claim uses (participant computation).**
Rule A is a condition on h1, one of the four words of the E3 side. So for
an outcome (tau, eps) the number N3 of step 3 splits into the quadruples
whose h1 satisfies rule A and those whose h1 violates it, and under M the
rate of the trials with R = 0 that satisfy rule A is the sum of step 5 with
the first of the two numbers in place of N3. The claim does not use that
sum. It uses a smaller figure: every outcome for which a solver found a
solution that violates rule A is left out in full, with all its solutions.

{{rule_paragraph}}

{{rule_table}}

{{rule_kept_paragraph}}

{{rule_kept_table}}

{{rule_count_before}}

    {{rule_count}}.

{{rule_count_after}}

{{rule_second_paragraph}}

{{rule_checks_paragraph}}

{{solutions_paragraph}}

*The other rules and the other factor.* {{rules_alt_paragraph}}

{{rules_alt_table}}

{{rules_alt_after}}

**Checks of the calculator (participant computations).** The E3 count of
step 3 is the program of submission {{last_submission}}, and the enumeration of
outcomes and the E1 count are those of that submission; the checks reported
there were made with other constants and with delta = 2 or -2. For this
package the calculator was built again from the same sources, and the
following checks were made for these constants, this class and delta = -8.

{{check_amc_paragraph}}

{{check_sys_paragraph}}

{{check_bf_paragraph}}

{{check_sampler_paragraph}}

What these checks cover: the E1 count against brute force only for 8-bit
words and against an approximate independent counter for the sixteen
heaviest outcomes at 32 bits; the E3 count in the same two ways; which
betas have a part, against a solver on a formula of the whole system; the
whole count against the independent recount above, which is the only
check that covers both factors of every outcome; and the E3 factor of
every outcome against the exact count reported with rule A above. All of
these are participant computations.

**How the constants and the class were found.** {{search_paragraph}}

**Checks of the construction on real messages (participant
computations).** {{construction_checks_paragraph}}

**Checks of the model on real messages (participant measurement).** Real
trials of 6.1 were compared with draws from M (Y4 a uniform member of the
class, the other six words uniform and independent), on the same
statistics: how often each of the four residual words, or its low 16 bits,
is zero, how many trials have a residual of low weight or with many
trailing zero bits, how often the early test of Lemma E passes, and in how
many trials E1 requires the class. The last of these is the event
eps XOR ROL(beta XOR eps, 1) = eta, so a trial in which E1 requires the
class is a trial that passes the E1 test of Lemma N. The algorithm of this
package uses the E1 test and not the early test; both are reported because
the programs print both. For some events the probability under M is known
exactly from the count, and the real trials are then compared with that
number directly: the event that E1 has one of the betas of the table with
k <= 14 ("listed beta"), that it also has a tau of one of the counted
outcomes of that beta, that it has both tau and eps of a counted outcome
("listed E1 outcome"), and an event on the E3 side alone, that E3 shows
the differences psi and eps of a counted outcome after its first six
assignments ("listed partial E3 event").

{{gpu_layout_note}}

{{real_model_paragraph}}

{{deep_paragraph}}

{{layout_paragraph}}

{{spread_paragraph}}

**Rule A on real trials: the model fails inside one context (participant
measurement).** {{ctx_paragraph}}

{{rule_runs_paragraph}}

{{joint_paragraph}}

{{rule_real_paragraph}}

{{rule_layout_paragraph}}

{{rule_review_paragraph}}

{{e1_real_paragraph}}

**Scaled-down end-to-end checks (participant computations; another
construction, other constants).** With short words the whole search can be
run and its collisions counted. Such runs exist only for the construction
of submission {{last_submission}}, with lengths 60 and 62 and its trial, and with
constant sets of their own with 8-bit and 10-bit words; they are reported
in the text of that submission and are not repeated here. They compared the
collisions found with the model's exact prediction: 9,835 against 9,837.9
predicted over six series at 8 bits, 693 against 664.6 over four series at
10 bits, and 1,813 against 1,807.2 for the search without the class
restriction. They are evidence for the method, that is for M and for the
independence of the trials at the depth of actual collisions when words
are short, in another layout of the trial. No scaled-down run has been
made for lengths 55 and 63, for steps S1 and T of this text, or with a
first-stage rule of the kind used here. This is the largest piece of
evidence that the filed package has and this package does not have.

The declared experiment `residual-search` runs the search of Section 6 at toy
scale: one context per seed, then the members of the class in order from a
number taken from the seed, stopping at the first trial whose residual has
a zero low byte in digest word 1. The search runs without rule A, without
the E1 test and without the packing of 6.5. The organizer checks that
every returned pair agrees on 136 digest bits. It checks the trial
generator and the residual computation on real digests. It is not a test of
H1, H2 or H3 and says nothing direct about 128 bits. Beside the search, the
program evaluates one packed batch per seed on the counting machine of 6.5
and returns the operations and loads of its two stages, its right lanes and
whether a lane satisfied rule A as observations; the organizer records them
as untrusted and does not check them.

**Limits of the evidence.**

- The factor 2^{{F}} in H1 is assumed. It is set against a count of
  {{rule_count}} under M, from a participant computation. The organizer-run
  experiments do not measure the factor, and the success bound needs it to
  be at least {{f_min}}. With factor 1, the uniform rate, the same search
  needs 2^127 trials and gives time_log2 = {{uniform_time}}.
- M does not hold inside one context for rule A: the share of the trials
  of one context that satisfy the rule depends on the context
  ({{ctx_limit_clause}}). Only the average over contexts has the model's
  value. Every statement of this text about the pass rate of rule A, about
  the stage-2 budget and about r_A is a statement about that average. The
  cause of the dependence was not analysed. Whether the rate of the good
  trials, which need rule A and R = 0 together, also has the model's value
  on average was not measured and cannot be: no measurement reaches R = 0.
  If the good trials sat mostly in contexts with a low share, r_A would be
  overstated. One measurement joins the rule with a deep event of E3
  ({{joint_limit_clause}}) and shows no such shift; it has the first four
  conditions only, an event of one call, and a probability far above that
  of R = 0, so it does not exclude it.
- Rule A is not implied by a collision; it loses solutions. That it loses
  no more than the count allows rests on the answers, for {{rule_ok}}
  of the {{rule_outcomes}} outcomes of the count, that no solution violates rule A.
  {{rule_cert_limit}} The {{rule_bad}} outcomes with a violating
  solution are left out in full, and that is {{rule_lost_pct}}% of the count: this
  rule gives up far more than the rule of the filed package did
  ({{filed_lost_pct}}%). Rule A was read off counts of the same kind as the count
  itself, for this class: it was chosen to fit the solutions that the count
  knows. No measurement on real messages reaches the event of H1, so none
  tests rule A together with R = 0.
- The count is exact only under M. It counts the solutions of the
  seven-word system; that the trials of the algorithm meet those solutions
  at the rate M predicts is the assumption. For 32-bit words and these
  constants M has been compared with real messages only for events of
  probability about 2^-{{deep_exp}} and above. Its use at the probability of
  the event R = 0, about 2^-{{hit_exp}}, is an extrapolation that no feasible
  experiment can test directly. M has been tested end to end, down to
  actual collisions, only for words of 8 and 10 bits, with other constants
  and with the trial of the earlier submissions, not with steps S1 and T.
- The constants and the class were chosen to make the count large: by a
  solver search that minimises the number of active bit positions of one
  solution, and then by the count itself. The count is deterministic, so no
  sampling noise enters it and no choice among noisy estimates was made.
  But a choice that is best under M says nothing about M. If M overstates
  the rate for some constants, a search for the largest count under M will
  tend to find those constants, and nothing here measures that.
- The count rests on few paths: {{heaviest_share}}% of it comes from one beta and {{top2_share}}%
  from two, and {{top_outcomes_share}}% from {{top_outcomes}} outcomes. An error in the count of
  these outcomes would change the figure in proportion.
- The calculator is not part of the package, and it and every check of it
  are the participant's. The statement that no beta with k >= 15 beyond
  the {{heavy_betas}} counted ones has a part rests on a solver's answers
  "unsatisfiable" for {{unsat_betas}} betas, from one solver and one formula,
  without certificates, and on the independent recount, which visited every
  beta with its own method.
- The independent recount was made by another AI model with a program of
  its own. It was not blind: the request stated the participant's total,
  the four heaviest parts and the number of betas with a part. Its program
  was compiled and run again by the participant's helper agents, and its
  parts were compared beta by beta; its method was read in its own
  description and was not re-derived or reviewed line by line.
- All trials of a run share the four seed words S11, S4, X13 and w0, the
  2^32 contexts of one pair (vc, vd) share everything that step S1 computes
  without X14, and the {{members}} trials of one context differ only in Y4
  and what follows from it. There is a further shared structure: step S1
  reads vc and vd only in X8 = vc - vd and in its last line, vb. So the
  2^{{d_bits}} pairs (vc, vd) with the same difference vc - vd have, for every
  X14, the same state S and the same words w0..w7 and w12, and the
  2^{{group_trials_exp}} trials of such a group and one X14 are messages that differ
  only in w8..w11. The 2^{{ctx}} pairs are 2^32 such groups. No measurement
  has this structure: every layout run holds a single pair. Independence
  of the trials is assumed, not shown. With a count that rests on few paths, whether a run contains a
  collision may depend on a few shared words more than it would for a rate
  spread over many paths; this was not examined. {{layout_limit_sentence}}
- Single-word statistics are not evidence for the joint rate. An earlier
  version of this construction, cancelled by the submitter before screening,
  used other constants and inferred a rate of half the uniform one from the
  frequencies of single zero residual words; a count of the kind described
  above gave 0.024 for those constants.
- H2 rests on the pass rate of the E1 test measured on real trials with
  these constants: {{pass_count}} passes in 2^{{pass_trials}} trials with
  independent contexts, and {{pass_layout_count}} in the {{layout_runs}} layout runs. That the
  number of passes of a full run of 2^{{T}} trials stays near the mean is
  assumed. The budget is 2^{{pass_margin}} times the passes expected at the
  measured rate.
- H3 rests on the share of the trials that satisfy rule A, averaged over
  contexts: {{h3_limit_sentence}} The budget on trials is {{budget_over_rule}} times
  2^-{{rule_pass_exp}}. That the average over the contexts of one run of 2^{{T}}
  trials is not that far above the mean is assumed. If either budget of
  step 4 is exceeded the algorithm halts with failure: that lowers the
  success probability, by the 0.0005 allowed for each of H2 and H3, and
  does not raise the time bound.
- The charge of {{charge}} operations per trial is the budgeted cost of a
  two-stage batch plus a margin of {{alpha_margin_pct}}%. The stage counts are those of
  the machine in the submitted program; no organizer run verifies them.
  The work per pair (vc, vd) is bounded in words and was not counted on the
  machine; with the bound of Section 8 it is a share below 2^-40 of the
  main loop.
- The two memory figures of the preprocessing in Section 9 are observations
  of the runs and were not measured by a tool.

**Scope and limitations.**

- No full collision of the 2-round hash is exhibited. The search is an
  analytical cost claim like other packages on this track; unlike a birthday
  search it tests each trial against zero and so needs no memory that grows
  with the number of trials.
- The two messages have different lengths, 55 and 63 bytes, and the
  construction relies on the true block length being a compression input, as
  the target profile specifies. The 63-byte message ends in eight zero
  bytes: in the zero-filled block of both messages the words 14 and 15 and
  the top byte of word 13 are zero.
- The gain over a generic birthday search has three sources: half of the
  digest is matched by construction, which removes the table and about half
  of the round-1 work per trial; the constants are chosen so that the
  remaining half can match at all with a useful rate; and the search stays
  inside one class of Y4, where that rate is assumed to be {{factor}} times
  the uniform one. The exponent of the number of trials is {{T}} instead of
  128, and 127 if only the uniform rate is assumed.
- The half-collision, the class search, the two tests and the two-stage
  batch are those of the submissions {{submissions_plain}} on
  this track, which claim {{submission_scores}}. What is new against the last
  of them is the pair of lengths, 55 and 63 in place of 60 and 62, with the
  zero words that it forces; the constants, found by the same solver search
  run for that length pair; the construction of Section 4, in which the
  context is seven words and a trial changes four message words; the
  class; rule A; and the counts of the batch. {{filed_compare_sentence}}
- A brief literature search found free-start collisions and near-collisions
  of the compression function for reduced BLAKE variants, and no collision
  attack on the 2-round BLAKE3 hash. No priority or novelty claim is made.
- The time bound counts the arithmetic, logical and shift operations of the
  packed batch, its comparisons and its branches, and one load for
  every use of a constant or list entry, on a 16-register machine, with
  stage 2 counted for the share of the batches that step 4 allows. It is an
  upper bound under that convention, not a measured running time. The count
  of a batch can be rerun with the self-test of the submitted program
  (6.5); that is a participant check and no organizer run verifies it.

**Field meanings.**

- time_log2 = {{time_log2}} bounds total charged time by 2^{{time_log2}} units.
- memory_log2_bytes = {{memory_log2}} bounds the storage of the preprocessing and of
  the search by 2^{{memory_log2}} bytes; the search alone needs less than 2^{{online_log2}}
  bytes (Section 9).
- preprocessing_log2 = {{preprocessing_log2}} bounds the recomputation of the six constants and
  the selection of the constants, of eta and of rule A by 2^{{preprocessing_log2}}
  target-compression units.
- nonuniform_advice_log2_bytes = {{advice_log2}} bounds the stored constants, eta and the
  constants of rule A, {{advice_bytes}} bytes, by {{advice_limit}} bytes.
- success_probability = 0.39 holds under H1, H2 and H3 as shown in
  Section 7.

The required baseline_improved identifier blake3-r2-nominal-v2 names the
organizer's nominal display reference 128, which is not an established attack,
a qualified baseline or a security bound. The claimed scalar {{time_log2}} is lower
than that display value. Whether a qualified result improves the Yukon
incumbent is decided separately, and no Pareto dominance claim follows from
the scalar.
