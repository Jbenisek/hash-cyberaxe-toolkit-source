# blake3-r2-exploratory: a free half-collision and a counted class, time_log2 = {{time_log2}}

## Summary

This package claims `time_log2 = {{time_log2}}` for `blake3-r2-exploratory`. Unlike
the other tickets on this track that I have read, it is not a birthday search
with a table. It has two parts that are kept separate in the proof.

**Relation to submissions {{submissions}}.** Those
three entries by the same participant on this track (time_log2 {{submission_scores}})
use the same half-collision and, the last of them, the same class search.
This package keeps the construction and the trial of
`{{last_submission}}` unchanged. Four things are new: the six constants, the class,
what the assumed rate is set against, which is now a count without
sampling in place of a sampled estimate, and the batch, which now has two
stages. {{step_note}}

**Exact part (no heuristic).** There is an explicit construction that maps any
nine 32-bit words to a 60-byte message A and a 62-byte message B whose complete
2-round BLAKE3-256 digests agree on digest words 0, 2, 5 and 7: 128 of 256
bits, with no search. It holds for all 2^288 choices. A second exact
construction walks through such pairs while it holds one internal word of
round 1 (Y4, the b output of the first column call) inside a prescribed set
of {{members}} values, the *class*. The organizer runner checks the
half-collision on such pairs in the declared experiment `half-collision`.

**Heuristic part.** A collision needs the other four digest words to agree
too. The algorithm tests 2^{{T}} such pairs against zero, all with Y4 in the
class. Because each trial is tested against zero rather than against other
trials, there is no table that grows with the search, no key extraction and
no lookup. Seven trials are packed into one 256-bit word and are evaluated
in two stages. Stage A, {{stage_a_ops}} operations (arithmetic, logical and shift
operations, comparisons and branches) plus {{stage_a_loads}} loads from memory, tests
{{rule_conditions}} bit conditions on one internal word of every trial (rule A). A batch
in which no trial passes is dropped. A batch in which a trial passes runs stage 2,
{{stage_2_ops}} operations plus {{stage_2_loads}} loads, which tests a 32-bit condition that every
collision satisfies, for all seven of its trials; the success bound counts
only trials that pass rule A themselves. With stage 2 charged for {{stage2_share_words}} of the batches, a
trial is charged {{charge}} operations, set-up included. **Rule A is not implied
by a collision**: it loses solutions, and the count below is reduced for
it. The submitted experiment program contains this batch, a machine that
counts it and a self-test of the count (see "Cost").

The score-critical heuristic H1 is that a trial passes rule A and completes
the collision with
probability at least 2^-{{T1}}, 2^{{F}} = {{factor}} times the rate of a uniform
128-bit value. **The factor is an assumption.** It is set against a count:
under a seven-word model the rate for the class is a number of solutions of
a fixed system, and my enumeration of it, without sampling, gives
{{exact_total}} times the uniform rate as a lower bound, and {{rule_count}}
when every part for which a solver found a solution that violates rule A is left out (see "How
the rate is counted"). The assumed factor is {{exact_over_factor}} times below the
second figure. The
count is my own computation, it is exact only under the model, and the
organizer-run experiments do not measure the factor. With the uniform rate
in place of {{factor}} times it, the same package would need 2^127 trials
and would claim {{uniform_time}}.

| claim.json field | value |
| --- | --- |
| `time_log2` | {{time_log2}} (2^{{T}} trials at {{charge}} operations, C = 430: 2^{{main_exp}}; below 2^{{total_bound}} with the two budgets and the other lower-order terms) |
| `memory_log2_bytes` | {{memory_log2}} (the search needs below 2^{{online_log2}} bytes: code, a few hundred words and one fixed list of {{list_words}} words; the declared figure covers the memory of the selection of the constants) |
| `preprocessing_log2` | {{preprocessing_log2}} (bound for recomputing and selecting the stored constants; included in the time) |
| `success_probability` | 0.39, under heuristics H1, H2 and H3 |
| `nonuniform_advice_log2_bytes` | {{advice_log2}} ({{advice_bytes}} bytes: six constants, the word that defines the class and three constants of rule A) |
| `heuristics` | H1 (score-critical): rate of trials that pass rule A and collide; H2 (supporting): budget on passes of the second test; H3 (supporting): budget on batches that run stage 2 |
| experiments | `half-collision` and `residual-search`, both organizer-executed |

**No full 2-round collision is exhibited**, and the search is far beyond
feasible computation. This is an analytical cost claim.

## What is new against the earlier submissions

1. **Constants found by a solver, not by farming.** The constants of the
   earlier submissions were the best of 4,140 random valid sets. Here one
   SAT instance (solver kissat) holds the pinned call for both messages,
   the two calls E1 and E3 that produce the open half of the digest, for
   both messages and with real word values, a zero residual, and a bound on
   the number of bit positions at which a difference is active in six
   additions. Every model is a valid set of constants together with one
   solution of the system that the residual depends on. When this note was written the search had returned
   {{search_pins}} such sets and was still running; the one used here came from an instance with bound
   {{search_bound}} after {{search_seconds}} seconds.
2. **A larger class with a far larger count.** For the new constants the difference
   W4 - W4' is {{delta}}, that is -2 where the earlier constants had +2;
   every formula of the proof is stated for the word W4 - W4' and holds for
   both. The class is eta = {{eta}}. It has {{members}} members, {{free_bits}} free
   bits of one word, where the class of `{{last_submission}}` had 4,096; the word
   ROL(eta,16) has bit 31 here, and Lemma Q is stated so that it covers
   that case (bit 31 of the word that carries the class is always free).
3. **Under the model, the rate is counted, not sampled.** In the earlier submission the rate
   of the class was a sampled estimate, 7,319 with a standard error of 816
   for a heavy-tailed quantity. Here the outcomes of one of the two calls
   are enumerated completely, and for each outcome both its probability and
   the number of matching inputs of the other call are counted. The result
   is a deterministic number. The sampler of the earlier submission is kept
   as a check of the new calculator. The calculator is not part of the
   package; the proof prints the outcomes of the heaviest beta with their
   two counts, and one complete solution inside the class, so that the
   largest part of the figure can be recomputed without it.
4. **A batch of two stages.** In the earlier submissions every batch
   computed the first halves of both calls E1 and E3, {{previous_batch}}. Here every
   batch computes only as far as one word of the column call C2, from which
   the bits of E3 that rule A needs follow, and stops unless one of its
   seven trials passes rule A; about one batch in ten goes on. The second
   stage tests a necessary condition on E1 alone (Lemma N of the proof) in
   place of the earlier early test, so E3 is not evaluated in a batch at
   all. Rule A was read off the counts. Almost all counted solutions
   satisfy it, not all: {{rule_lost_pct}}% of the count is given up, and the cost of a
   trial falls from {{previous_charge}} to {{charge}} charged operations.

## What is new against the earlier version of this package

{{draft_note}}

## Where the half-collision comes from

Three observations, each exact.

1. **The block length can be cancelled in round 0.** For a single-block
   message the true block length n is the initial value of v[14], and in
   round 0 it is read only by the column call G(2,6,10,14, w4, w5). With
   K = IV[2] + IV[6], replacing (n, w4, w5) = (60, w4, w5) by
   (62, ((K + w4) XOR 2) - K, w5 + w4 - w4') leaves that call's four outputs
   unchanged. So a 60-byte and a 62-byte message that share every other word
   have the **same state after round 0**, and round 1 starts from zero state
   difference with word differences only in w4 and w5.
2. **One round-1 column call can be pinned.** In round 1, w4 is the first word
   of C3 = G(3,7,11,15, w4, w13). For the six constants given in the proof,
   changing w4 to w4' changes only the a and c outputs of C3, not b and d.
3. **Then half the digest does not see the difference.** The diagonal calls
   G(0,5,10,15) and G(2,7,8,13) of round 1 read neither v[3], v[11], w4 nor
   w5, so their outputs are identical for A and B, and digest words 0, 2, 5,
   7 are XORs of exactly those outputs.

To put the six constants in place I use the fact that round 0 with a fixed
initial state is invertible: the state after it determines the message. The
construction takes the state after round 0 as its input (nine free words, the
rest pinned or derived) and computes the sixteen message words by inverting
each G call. The class search then gives Y4 any wanted value at no cost: the
column call that outputs it reads message word w6 only in its second half,
so w6 is solved from the wanted Y4, and five more message words absorb what
that changes. The proof lists the formulas and proves them call by call.

## How the rate is counted

The remaining 128 digest bits come from the calls E1 = G(1,6,11,12, w12, w5)
and E3 = G(3,4,9,14, w15, w8) only, and they depend on seven 32-bit words:
three of E1 and four of E3, one of which is Y4. Everything in this section is
my own computation; none of it is organizer-verified.

- **Model.** Over the trials, the six words other than Y4 behave like
  independent uniform words. Then the hit rate is r * 2^-128, where r is the
  number of solutions of the seven-word system with Y4 in the class, divided
  by 2^{{sol_exp}}. Rule A is a condition on one of the seven words, so the trials
  that collide and pass rule A have a rate r_A of the same kind, at most r.
  H1 is this model with r_A >= {{factor}}. The count below is exact only
  under this model and says nothing about the model itself.
- **The calculator.** Write beta for the XOR difference of E1's first-half b
  value; it depends on one of E1's words alone, and only finitely many
  words occur. A beta fixes k bits of that word, so it occurs with
  probability 2^-k. For one beta the outcomes of E1 are pairs (tau, eps) of XOR
  differences of its a and c outputs. tau runs over every difference that
  the addition in question can show, enumerated by a search over its bits
  with a carry automaton and no limit on its weight; eps is one of two
  words that the class fixes, or none. For each outcome the calculator
  counts the inputs of E3 that match it (the count of the earlier
  submissions) and the probability that E1 produces it (a new automaton
  over the bits of one word, with a borrow and a carry as its state). The
  class-rate part of a beta is a weighted sum of the products, and r is
  the sum over all betas; leaving betas out makes the figure a lower bound.
- **The count for this package.** {{beta_cover_sentence}}
  {{betas_no_eps}} betas of the list have no eps and contribute nothing, {{betas_evaluated}} were
  enumerated completely{{enumerated_caveat}}, and {{betas_with_mass}} have a nonzero part: {{exact_listed}} together.
  {{extra_betas_sentence}} That is about 2^{{exact_log2}}. The heaviest beta carries {{heaviest_share}}% of it
  and the two heaviest {{top2_share}}%. {{recount_sentence}}
- **Rule A and the figure that the claim uses.** Rule A says:
  {{rule_a_inline}}, where h1 is E3's first-half d value on message A. It is
  not implied by a collision. For each of the {{rule_outcomes}} outcomes of the count a
  SAT solver (kissat) was asked whether the E3 system of the outcome has a
  solution that violates rule A: for {{rule_ok}} its answer is that there is none,
  for {{rule_bad}} it returned one. These {{rule_bad}} outcomes are left out in full, which
  removes {{rule_lost}} and leaves {{rule_count}}, the figure that H1 is set against.
  {{rule_sat2_note}}
  {{calc2_sentence}} {{calc2_total_sentence}}
  {{rule_split_sentence}} {{rule_fit_note}} {{rule_example_note}}
- **The choice of the class.** {{class_search_sentence}}{{classes_counted_cap}} classes of
  these constants have a count over the same {{class_common}} betas. The class
  used has {{class_own_common}} there; {{class_choice_short}}.
- **The sampler as a check.** The sampler of `{{last_submission}}` draws E1 at random for
  one beta and counts E3 for each draw. {{sampled_betas_cap}} betas, which carry {{sampled_share}}% of
  the count, were given {{sampler_setup}} each, with the same seeds for
  every beta. {{sampler_sum_sentence}} {{sampler_far_sentence}}
  {{review_sampler_sentence}}
  {{extra_sampler_sentence}} {{sampler_note}} The sampler uses the same
  E3 count as the calculator, so it checks the enumeration of outcomes and
  the E1 count, not the E3 count.
- **Checks of the calculator.** (1) Against the sampler on other constants,
  among them the class and the heaviest beta of `{{last_submission}}`: 6,164.7 counted
  against 6,168 sampled with standard error 810. (2) The new E1 count
  against brute force with 8-bit words: {{bf_summary}}. (3) The E1 count at 32
  bits against the model counter ApproxMC, for these constants:
  {{e1amc_summary}}. (4) The E3 count for these constants
  against a SAT solver and ApproxMC, {{e3check_cover}}:
  {{e3_summary}}. (5) No limit on the weight of tau was used. The proof
  gives the figures. The E1 count and the enumeration of outcomes are new
  code, written in the night before this text.
- **Checks by reviewing helper agents.** {{review_note_sentence}}
- **How the constants and the class were chosen.** {{cand_sentence_note}}
  {{search_class_sentence_note}} There is no sampling noise in these counts and
  so no "best of many noisy estimates". But a choice that is best under
  the model says nothing about the model: if the model overstates the rate
  for some constants, a search for the largest count will tend to find
  them, and nothing here measures that.
- **Check of the trial on real messages.** {{host_check_note}}
- **Check of the model on real messages, independent contexts.** Real
  trials of the class search with these constants were compared with the
  same number of draws from the model on how often residual words vanish,
  on low residual weights, on the early test of the earlier submissions
  (Lemma E of the proof; the algorithm of this package does not use it) and
  on the number of trials in which E1 requires the class, which are the
  passes of this package's second test. Every thread of the
  generating program has its own random context and makes 4,096 trials
  with random alpha and random class members; that is not the algorithm's
  layout, in which all contexts of a run share four seed words. Result:
  {{real_model_note}}. {{deep_note_sentence}}
- **Deeper counts on real messages, one call at a time.** {{deep_counts_note}}
- **Real trials in a shared-seed layout.** {{layout_note_sentence}}
  {{layout_spread_note}} For the constants of `{{last_submission}}` the same comparisons showed
  deviations of up to 3.1 standard deviations in settings other than its
  own class, among them a spread between two runs that I have not
  explained; that bears on the model in general.
- **Rule A and the second test on real trials.** {{a_runs_cap}} runs of 2^{{a_run_trials}}
  real trials with shared seed words: {{a_count}} of 2^{{a_trials}} trials
  satisfy rule A, a share of 2^{{a_rate}}, and no run is further than {{a_rel}}
  of its value from 2^-{{rule_pass_exp}}; {{a_e1_passes}} trials pass the second test. These
  runs have no model run beside them. {{lay_note}} {{seeds_note}}
  {{rule_amc_note_sentence}}
- **Scaled-down end-to-end check, with other constants.** The same attack
  was run in full on toy versions of the hash with 8-bit and 10-bit words
  (2 rounds, IV truncated to the top bits, rotations 4, 3, 2, 1 and 5, 4,
  3, 2), where a complete run is 2^32 or 2^40 trials and real collisions
  can be counted. These runs were made before the constants of this
  package were found and use small constant sets of their own; they are
  evidence for the method, not for these constants. For a constant set the
  rate of every class is computed exactly by brute force, the best class
  is searched, and the model predicts r collisions per run. At 8 bits:
  9,835 collisions against 9,837.9 predicted over six series of runs
  (largest deviation 1.7 standard deviations). At 10 bits: 693 against
  664.6 over four series (deviations +1.7, -1.7, +0.5 and +0.9 standard
  deviations). The variance-to-mean ratio of the collisions per run, 1 for
  independent trials, is 0.46 to 1.60 over the eleven class series and
  0.96 pooled; one series of 40 runs is at 1.60, about 2.65 standard errors
  above 1. Every class run of these series had many collisions, so they do
  not test "at least one collision per run"; the runs of the next item do.
  The same check without the class restriction
  (ten constant sets, 1,465 runs) gave 1,813 collisions against 1,807.2
  predicted; its weakest series had a collision in 37 of 40 runs where
  39.3 are expected. Every hit was confirmed by hashing both messages in
  full. A toy run of these series holds the words X2, X9, X13 and X14
  fixed, which is not the split of the algorithm (seed words X2, X5, X6,
  X9).
- **Scaled-down runs in the algorithm's own layout, with other constants.**
  {{toyalg_note_sentence}}
- **Scaled-down runs with staged tests, with other constants.**
  {{toystage_note_sentence}}

## Cost

| Part of a batch of seven trials | Operations | Loads |
| --- | ---: | ---: |
| loop over the class | 3 | 1 |
| Y4 backwards through C0 | 9 | 7 |
| round-0 column call K3 with one output kept | 27 | 14 |
| column call C2 as far as one word z | 16 | 8 |
| rule A on z and zero-lane detection | 9 | 6 |
| **stage A, every batch** | {{stage_a_ops}} | {{stage_a_loads}} |
| count of the entry against its budget | 3 | 1 |
| rest of C2 | 12 | 4 |
| round-0 diagonal call D1 | 9 | 6 |
| column call C1 as far as Y1 | 17 | 9 |
| E1 for A and B, to c2 | 40 | 15 |
| second test and zero-lane detection | 15 | 7 |
| **stage 2, only after a pass of stage A** | {{stage_2_ops}} | {{stage_2_loads}} |

Stage A is {{stage_a_total}} primitive operations and stage 2 is {{stage_2_total}}. E3 is not
evaluated in a batch: rule A is a condition on E3's value h1, but h1 differs
from the word z of C2 only by a rotation and by bits that the class fixes,
so it is tested on z.

**Memory traffic is charged.** The cost model counts memory accesses, so the
proof fixes a 16-register load/store machine and charges one load for every
use of a constant operand (per-context and per-alpha constants, the list
entry that carries the class members, rotation masks, the reduction mask,
the constants of rule A and the budget). The batch values themselves stay in
registers (at most {{st_registers}} are in use, the two counters included), so no stores are
needed. One pass over the class is {{list_words}} batches, the last one holding
{{rest}} trials, and every batch runs stage A. **How many batches run stage 2
is not proved.** The algorithm allows {{stage2_share_words}} of the batches of a run
and halts with failure beyond that; that this budget suffices is heuristic
H3. A uniform word passes rule A with probability 2^-{{rule_pass_exp}}, so at most
{{rule_share}} of the batches are expected, and real trials show a share of
2^{{a_rate}} of the trials. With that budget and fewer than 256 operations of
set-up, a pass over the class costs at most {{alpha_ops}} operations for
{{members}} trials, {{per_trial}} per trial, charged as {{charge}}; the expected cost is
{{per_trial_expected}}. The other tickets I read count the arithmetic of their inner loop
without such loads; I submit the stricter number.

**The operation count can be rerun from the package.** `experiments/halfsearch.py`,
the program of the two declared experiments, contains the packed batch and
the machine that counts it: every operation on packed words and every load
is a counted call. The command

    python3 experiments/halfsearch.py --selftest N [seed]

runs N batches on contexts, values of alpha and list positions derived from
the seed text. It checks all seven lanes of each batch against the real
messages of the lane's trial: it builds both messages, compresses each with
a 2-round compression written out from the definition, and compares the
stage-A flag with rule A on the h1 of message A, and the stage-2 word with
the same word from the two compressions and from the two complete digests.
It prints one JSON line: cases, lanes checked and lanes right, the lanes
that pass rule A and the batches in which one does, operations and loads
per part and per stage, the largest lane of a sum per part next to the
bound the proof gives, the registers in use, the number of constants, the
class members in the list, and the flags on words with zero lanes and on
all patterns of the bits that rule A reads. With N = {{st_cases}} and seed {{st_seed}} it
reports {{st_lanes}} of {{st_lanes}} lanes right, {{stage_a_ops}} operations and {{stage_a_loads}} loads in stage A
and {{stage_2_ops}} and {{stage_2_loads}} in stage 2 in every case and per part as in the proof's
table, {{st_pass_a}} lanes that pass rule A in {{st_entered}} batches, a largest sum of
{{st_largest}} * 2^32 (a lane holds 16 * 2^32) and at most {{st_registers}} of the 16 registers in
use. {{big_selftest_sentence}} In the `residual-search` experiment the same
program evaluates one such batch per organizer seed and returns the
operations and loads of both stages, its right lanes and whether a lane
passed rule A as observations. The organizer records
observations as untrusted and does not recompute them, so this is still my
count, made reproducible; it is not an organizer-verified cost.

2^{{T}} trials at {{charge}} operations are {{charge}} * 2^{{T}} / 430 = 2^{{main_exp}} units.
Passes of the second test are budgeted at 2^{{pass_budget}}. A passing trial is
recomputed in scalar form, below 2^10 operations, so the budget costs
2^{{pass_ops}} operations, a share below 2^-{{pass_share}} of the main loop. Per-context
set-up (2^{{ctx_ops}} operations in total), the final check and the bound for the
constants (2^63 units) are far below that; all lower-order terms together
add less than 0.012 to the exponent. The total is below 2^{{total_bound}}, and the
bound is worst case for the algorithm as stated, which halts when either
budget is reached. The pass budget corresponds to a pass rate of 2^-{{pass_shift}}; the
measured pass rate is 2^{{pass_rate}}, which would give 2^{{pass_expected}} passes, so the budget
is larger by a factor of about 2^{{pass_margin}}. With the more cautious factor 2^{{alt_F}}
in H1, which is {{exact_over_alt}} times below the count, the same package would search
2^{{alt_T}} trials and claim {{alt_time}}.

The seven-lane layout with 36-bit lanes, reduction delayed to the rotations
and a five-operation masked rotation is taken from public ticket 2bf40fb,
whose author is credited as co-author for that reason. What is evaluated in
the lanes, and why no table is needed, is new in these packages.

## What is assumed and what is not shown

- H1: 2^{{T}} trials, each passing rule A and being a collision with
  probability at least 2^-{{T1}}, behaving like independent events. H2: fewer
  than 2^{{pass_budget}} passes of the second test. H3: fewer than {{stage2_budget}}
  trials that pass rule A, so that at most {{stage2_share_words}} of the batches run
  stage 2. None of the three is proved.
- No full collision. The search needs about 2^{{T}} trials.
- The factor {{factor}} in H1 is assumed against my count of {{rule_count}}.
  No organizer-run experiment measures it. With factor 1 the claim would
  be {{uniform_time}}.
- Rule A is not implied by a collision. That it loses no more than the
  {{rule_lost}} given up rests on {{rule_unsat_note}},
  without a checked certificate. Rule A was chosen from counts of the same
  kind as the count, so it fits the solutions that the count knows, and
  nothing on real messages tests rule A together with a collision.
- The stage-2 budget (H3) rests on {{a_runs}} runs of real trials with shared
  seed words{{h3_note_more}} and on the fact that a uniform word passes rule A with
  probability 2^-{{rule_pass_exp}}. If a run exceeded it the algorithm would halt with
  failure; the time bound would hold.
- The count is exact only under the seven-word model. The model is tested
  end to end only on versions with words of {{toy_bits_all}}, with other constants.
  At 32 bits and with these constants it is compared with real messages
  only for events of probability about 2^-32 and above{{deep_limit_note}}; its use at the
  probability of a collision, about 2^-{{hit_exp}}, is an extrapolation.
- The constants and the class were chosen to make the count large. The
  count is deterministic, but the choice exploits the model, and a failure
  of the model for these constants would not show in the count.
  {{class_rank_sentence}}
- The count rests on few paths: {{heaviest_share}}% from one beta, {{top2_share}}% from two.
- The calculator is not in the package. It is mine, as is every check of
  it, those of my reviewing helper agents included. Its E1 count and its
  enumeration of outcomes are new code, checked against brute force only
  at 8 bits and against an independent counter {{e1amc_cover}}.
- The count covers {{betas_list}}; the rest is left out,
  which can only make the true rate under the model larger.
- All trials of a run share four seed words, trials of one context share
  most of their other words, and the {{members}} trials of one pass over the
  class differ only in Y4 and what follows from it; their independence is
  assumed. With a count that rests on few paths I have not examined
  whether collisions depend on a few shared words. {{layout_spread_limit}}
  {{run_distribution_note}}
- The memory figures of the selection (below 16 GB of main memory, below
  10 GB on the graphics card) are what I observed, not instrumented peaks.
- Nothing about the 128-bit rate is organizer-verified. The two declared
  experiments check the half-collision and a toy search with 8 extra bits;
  neither is a test of H1, H2 or H3.

## What I tried that did not work

- SAT solvers on the full 2-round problem, with and without the length
  cancellation and the pinned call: no collision within 7 minutes to 2.5
  hours on 12 to 22 cores per configuration.
- A meet-in-the-middle on the seven-word system. Solutions of that system are
  easy to find, but I found no cheap way to turn one into a message: in a
  guess-and-determine model of all G calls, no set of five or fewer extra
  guessed words determines the state once the seven words are fixed.
- Sparse additive differences in the pinned call: the residual then never
  cancels.
- Lengths whose XOR is odd (for example 62 and 63): the pinned call is
  impossible.
- A solver search on differences alone, without real word values: four of
  the five paths it returned had no matching input of E3 for any value of
  Y3 that I tried. The search that produced these constants carries real
  values for that reason.

## Checks performed

{{local_checks}}
- A second program, written from the text of the proof, checked every lemma
  of the class search on 20,000 random trials with these constants and this
  class against a plain forward compression of its own, which it compared
  with the organizer's reference hash on 2,000 of them.
- The self-test of the submitted program, {{st_cases}} batches with seed {{st_seed}}: all
  {{st_lanes}} lanes right against the real messages of their trials, {{stage_a_ops}}
  operations and {{stage_a_loads}} loads in stage A and {{stage_2_ops}} and {{stage_2_loads}} in stage 2 in every
  batch, no lane above its 36 bits, and every sum below the bound the proof
  quotes for its part. {{big_note_sentence}}
- A second program checked the batch of the submitted program against the
  research program in which the two-stage batch was first written, and its
  reference values against a forward compression of its own.
- {{review_reruns_note}}
- The contest's judge pipeline was not run locally and no provider key was
  used.

## Package files and next steps

The package is `proof.md`, `claim.json`, `experiments/halfsearch.py` (the
two experiments and the self-test of the operation count),
`experiments/manifest.json` and `certificates/manifest.json` (empty: no
collision is exhibited).

Open, in order of value: an argument in words for what rule A keeps, in
place of the solvers' answers; real trials in the exact layout of the
algorithm that record the second test, and rule A over whole runs and not
over samples of the contexts; the cause of the spread between runs in the
layout of the algorithm; runs in the exact layout, with S5 shared, and with
residual statistics kept; the remaining checks for the class with the
largest count; scaled-down runs in the algorithm's layout with constants chosen by
a solver as here; and a test of the two calls together below 2^-32 on real
messages, which I do not know how to make ({{e1deep_open}}).

## Tools

Mathematics, code and text: Claude Opus 5.5 in Claude Code. Measurements: one
RTX 3090 and a 24-core desktop. Helper agents of the same model did parts
of the work, and the text says so where it reports them: some drafted parts
of the text; three reviewed the earlier version of this package, before
rule A and the two-stage batch existed, and some of the checks are theirs;
one made the scaled-down runs in the algorithm's layout; one found rule A
and the second test, wrote the two-stage batch, counted it first and made
the runs that record rule A on real trials and the scaled-down runs with
staged tests; and one assembled this version of the package from those
results, ran the solver on every outcome of the count and recounted the
parts. {{version_review_sentence}}

Other AI models were consulted during the work on this construction. They
are all named here, whether or not anything they said was used:

- Grok 4.7 (xAI), through its command-line client and in the owner's own
  chat. For this package it was given a brief on how to raise the rate. Its
  concrete proposals were not usable; it agreed that the choice of the
  constants is the lever. Earlier it had been asked to attack the argument
  and had concluded that the hit rate had to be measured rather than
  assumed.
- A model on Venice.ai, in the owner's chat (the model name was not
  recorded), consulted for the earlier submissions. Nothing from it is
  used.
- GPT in pro mode (OpenAI), in the owner's chat (the version was not
  recorded), consulted for the earlier submissions. It gave general advice
  on method. No construction or constant comes from it.
- GPT-6 Luna (effort high), running as an agent on a second machine of the
  owner's (RTX 3070 cards), ran measurement jobs with my programs for the
  earlier submissions. No result of it is used in this package.

Public notes of other teams on this contest were read for their accounting
conventions (how loads, registers and memory are counted). No construction
and no figure comes from them.

No text or code from any other model is in the package. The submitter is
responsible for every claim and every error in it.

Effort: xhigh (Claude Opus 5.5). Grok 4.7 was run through its command-line
client with that client's default settings; no effort level was set for it.

## Limitations

- Analytical cost claim with a declared score-critical heuristic whose
  factor {{factor}} is assumed and not organizer-measured.
- Two different message lengths; relies on the true block length being a
  compression input, as the profile specifies.
- The charge per trial counts stage 2 for {{stage2_share_words}} of the batches. That
  no more run it is heuristic H3, enforced by a budget and not proved.
- The number of trials is 2^{{T}} instead of 2^128 because of the assumed
  rate; the rest of the gain is the cost of a trial. With only the uniform
  rate assumed it is 2^127 and the claim is {{uniform_time}}.
- A brief literature search found free-start and near-collision results for
  reduced BLAKE variants only. No priority or novelty claim.
