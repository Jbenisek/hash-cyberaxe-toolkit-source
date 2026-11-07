# blake3-r2-exploratory: the class search with another pair of lengths, time_log2 = {{time_log2}}

## Summary

This package claims `time_log2 = {{time_log2}}` for `blake3-r2-exploratory`. It is
not a birthday search with a table. It has two parts that are kept separate
in the proof.

**Relation to submission `{{last_submission}}`.** That entry by the same participant
on this track claims time_log2 {{last_score}}; the earlier entries {{submissions}}
claim {{submission_scores_before}}. This package keeps the method of
`{{last_submission}}`: a half-collision that costs nothing, a search inside one class
of an internal word, a batch of two stages and a count of the rate under a
seven-word model. Three things are new. The messages have 55 and 63 bytes
in place of 60 and 62. The six constants are new; they were found by the
same solver search, run for that pair of lengths. And the trial is built
in another way, because the new pair of lengths forces message word 14 to
zero, and the earlier trial changed that word. {{filed_compare_note}}

**Exact part (no heuristic).** There is an explicit construction that maps any
eight 32-bit words to a 55-byte message A and a 63-byte message B whose
complete 2-round BLAKE3-256 digests agree on digest words 0, 2, 5 and 7: 128
of 256 bits, with no search. It holds for all 2^256 choices. One of the
eight words is an internal word of round 1 (Y4, the b output of the first
column call), and the search holds it inside a prescribed set of {{members}}
values, the *class*. The organizer runner checks the half-collision on such
pairs in the declared experiment `half-collision`.

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
{{exact_total}} times the uniform rate, and {{rule_count}}
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
| `nonuniform_advice_log2_bytes` | {{advice_log2}} ({{advice_bytes}} bytes: six constants, the word that defines the class and {{advice_rule_words}} constants of rule A) |
| `heuristics` | H1 (score-critical): rate of trials that pass rule A and collide; H2 (supporting): budget on passes of the second test; H3 (supporting): budget on batches that run stage 2 |
| experiments | `half-collision` and `residual-search`, both organizer-executed |

**No full 2-round collision is exhibited**, and the search is far beyond
feasible computation. This is an analytical cost claim.

## What is new against submission {{last_submission}}

1. **Another pair of lengths.** The half-collision rests on cancelling the
   block length inside one column call of round 0. In the earlier
   submissions the two lengths were 60 and 62, whose XOR is 2. The same
   cancellation works for an XOR of 8: with K = IV[2] + IV[6], replacing
   (n, w4, w5) = (55, w4, w5) by (63, ((K + w4) XOR 8) - K, w5 + w4 - w4')
   leaves the four outputs of that call unchanged. The idea of trying other
   single-bit length differences came from Grok 4.7 (see "Tools"). The
   price is that the 63-byte message must end in eight zero bytes: in the
   block of both messages, words 14 and 15 are zero and the top byte of
   word 13 is zero.
2. **New constants from the same search.** The pinned call needs six
   constants. They were found by the solver search of `{{last_submission}}`, run with
   the new difference and with a zero top byte of the pinned word 13.
   {{search_note}}
3. **Another construction of the trial.** The earlier trial changed seven
   message words, among them word 14, which is now zero. The new
   construction takes seven words as a context and changes only the four
   words w8..w11 from one trial to the next. The proof writes it out line
   by line and proves it call by call (Section 4, Lemmas S, F and Y); these
   proofs are new text.
4. **A larger class, a larger count and another rule.** The class has
   {{members}} members where the class of `{{last_submission}}` had {{filed_members}}. The count
   of the rate under the model is {{exact_total}}; the filed package had
   {{filed_count}}. The rule of the first stage has {{rule_conditions}} conditions and gives
   up {{rule_lost_pct}}% of the count, where the filed rule gave up {{filed_lost_pct}}%: the
   figure that the claim uses is {{rule_count}}.
5. **A deviation from the model that is stated.** On real trials the share
   of the trials of one context that pass the first-stage rule is not the
   model's value: {{ctx_note}}. The average over contexts is the model's
   value. The proof says so wherever it speaks of that rate, and H3 is a
   statement about the average.

## Where the half-collision comes from

Three observations, each exact.

1. **The block length can be cancelled in round 0.** For a single-block
   message the true block length n is the initial value of v[14], and in
   round 0 it is read only by the column call G(2,6,10,14, w4, w5). With the
   replacement above, a 55-byte and a 63-byte message that share every other
   word have the **same state after round 0**, and round 1 starts from zero
   state difference with word differences only in w4 and w5.
2. **One round-1 column call can be pinned.** In round 1, w4 is the first word
   of C3 = G(3,7,11,15, w4, w13). For the six constants given in the proof,
   changing w4 to w4' changes only the a and c outputs of C3, not b and d.
3. **Then half the digest does not see the difference.** The diagonal calls
   G(0,5,10,15) and G(2,7,8,13) of round 1 read neither v[3], v[11], w4 nor
   w5, so their outputs are identical for A and B, and digest words 0, 2, 5,
   7 are XORs of exactly those outputs.

To put the six constants in place I use the fact that every assignment of
a G call can be solved for any of its terms. The construction takes seven
words (two values inside the first column call of round 1, two state words
after the column step of round 0, two state words after round 0 and one
message word) and the wanted value of Y4, and computes the sixteen message
words. The proof lists the fifty lines of the context and the twenty-two
lines of the trial and checks every one of the nine calls involved
assignment by assignment.

## How the rate is counted

The remaining 128 digest bits come from the calls E1 = G(1,6,11,12, w12, w5)
and E3 = G(3,4,9,14, w15, w8) only, and they depend on seven 32-bit words:
three of E1 and four of E3, one of which is Y4. Everything in this section is
my own computation unless another model is named; none of it is
organizer-verified.

- **Model.** Over the trials, the six words other than Y4 behave like
  independent uniform words. Then the hit rate is r * 2^-128, where r is the
  number of solutions of the seven-word system with Y4 in the class, divided
  by 2^{{sol_exp}}. Rule A is a condition on one of the seven words, so the trials
  that collide and pass rule A have a rate r_A of the same kind, at most r.
  H1 is this model with r_A >= {{factor}}. The count below is exact only
  under this model and says nothing about the model itself.
- **The count for this package.** {{count_note}}
- **An independent recount.** {{recount_note}}
- **Rule A and the figure that the claim uses.** Rule A says:
  {{rule_a_inline}}, where h1 is E3's first-half d value on message A. It is
  not implied by a collision. {{rule_note}}
- **The other rules and the other factor.** {{rules_alt_note}}
- **Checks of the calculator.** {{checks_note}}
- **How the constants and the class were chosen.** {{search_choice_note}}
  There is no sampling noise in these counts and so no "best of many noisy
  estimates". But a choice that is best under the model says nothing about
  the model: if the model overstates the rate for some constants, a search
  for the largest count will tend to find them, and nothing here measures
  that.
- **Checks of the construction on real messages.** {{construction_note}}
- **Check of the model on real messages.** {{real_note}}
- **Rule A on real trials.** {{rule_real_note}}
- **Scaled-down end-to-end checks.** None exists for this pair of lengths
  and this construction. The runs with 8-bit and 10-bit words that
  `{{last_submission}}` reports (9,835 collisions against 9,837.9 predicted at 8 bits,
  693 against 664.6 at 10 bits) were made for its construction and are
  evidence for the method only.

## Cost

| Part of a batch of seven trials | Operations | Loads |
| --- | ---: | ---: |
| loop over the class | 3 | 1 |
| Y4 backwards through C0 | 10 | 8 |
| round-0 diagonal calls D0 and D1, as far as needed | 16 | 10 |
| column call C2 as far as one word z | 17 | 7 |
| rule A on z and zero-lane detection | {{rule_part_ops}} | {{rule_part_loads}} |
| **stage A, every batch** | {{stage_a_ops}} | {{stage_a_loads}} |
| count of the entry against its budget | 3 | 1 |
| rest of C2 | 12 | 4 |
| rest of D0 and D1 | 27 | 13 |
| column call C1 as far as Y1 | 18 | 8 |
| E1 for A and B, to c2 | 40 | 15 |
| second test and zero-lane detection | 15 | 7 |
| **stage 2, only after a pass of stage A** | {{stage_2_ops}} | {{stage_2_loads}} |

Stage A is {{stage_a_total}} primitive operations and stage 2 is {{stage_2_total}}. E3 is not
evaluated in a batch: rule A is a condition on E3's value h1, but h1 differs
from the word z of C2 only by a rotation and by bits that the class fixes,
so it is tested on z.

**Memory traffic is charged.** The cost model counts memory accesses, so the
proof fixes a 16-register load/store machine and charges one load for every
use of a constant operand (constants of the context, the list entry that
carries the class members, rotation masks, the reduction mask, the
constants of rule A and the budget). The batch values themselves stay in
registers (at most {{st_registers}} are in use, the two counters included), so no stores are
needed. One pass over the class is {{list_words}} batches, the last one holding
{{rest_words}} trials, and every batch runs stage A. **How many batches run stage 2
is not proved.** The algorithm allows {{stage2_share_words}} of the batches of a run
and halts with failure beyond that; that this budget suffices is heuristic
H3. With that budget and {{prep_bound}} operations of set-up per context (a tool of
mine counts {{prep_total}}), a pass over the class costs at most {{alpha_ops}}
operations for {{members}} trials, {{per_trial}} per trial, charged as {{charge}}; the
expected cost is {{per_trial_expected}}. The other tickets I read count the arithmetic of
their inner loop without such loads; I submit the stricter number.

**The operation count can be rerun from the package.** `experiments/halfsearch.py`,
the program of the two declared experiments, contains the packed batch and
the machine that counts it: every operation on packed words and every load
is a counted call. The command

    python3 experiments/halfsearch.py --selftest N [seed]

runs N batches on contexts and list positions derived from the seed text.
It checks all seven lanes of each batch against the real messages of the
lane's trial: it builds both messages, compresses each with a 2-round
compression written out from the definition, and compares the stage-A flag
with rule A on the h1 of message A, and the stage-2 word with the same word
from the two compressions and from the two complete digests. With
N = {{st_cases}} and seed {{st_seed}} it reports {{st_lanes}} of {{st_lanes}} lanes right, {{stage_a_ops}}
operations and {{stage_a_loads}} loads in stage A and {{stage_2_ops}} and {{stage_2_loads}} in stage 2 in
every case and per part as in the proof's table, {{st_pass_a}} lanes that pass
rule A in {{st_entered}} batches, a largest sum of {{st_largest}} * 2^32 (a lane holds
16 * 2^32) and at most {{st_registers}} of the 16 registers in use.
{{big_selftest_sentence}} In the `residual-search` experiment the same
program evaluates one such batch per organizer seed and returns the
operations and loads of both stages, its right lanes and whether a lane
passed rule A as observations. The organizer records observations as
untrusted and does not recompute them, so this is still my count, made
reproducible; it is not an organizer-verified cost.

2^{{T}} trials at {{charge}} operations are {{charge}} * 2^{{T}} / 430 = 2^{{main_exp}} units.
Passes of the second test are budgeted at 2^{{pass_budget}}. A passing trial is
recomputed in scalar form, below 2^10 operations, so the budget costs
2^{{pass_ops}} operations, a share below 2^-{{pass_share}} of the main loop. The set-up per
pair of the two enumerated context words (2^{{ctx_ops}} operations in total), the
final check and the bound for the constants (2^63 units) are far below
that; all lower-order terms together add less than 0.012 to the exponent.
The total is below 2^{{total_bound}}, and the bound is worst case for the algorithm
as stated, which halts when either budget is reached. The measured pass
rate of the second test is 2^{{pass_rate}}, which would give 2^{{pass_expected}} passes, so
the budget is larger by a factor of about 2^{{pass_margin}}. With the more cautious
factor 2^{{alt_F}} in H1, which is {{exact_over_alt}} times below the count, the same package
would search 2^{{alt_T}} trials and claim {{alt_time}}.

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
- The model does not hold inside one context for rule A ({{ctx_note}}).
  Only averages over contexts have the model's value; whether the rate of
  trials that pass rule A and collide has it too cannot be measured.
- Rule A is not implied by a collision. It gives up {{rule_lost_pct}}% of the count,
  and {{rule_cert_note}}. Rule A was chosen from counts
  of the same kind as the count, so it fits the solutions that the count
  knows, and nothing on real messages tests rule A together with a
  collision.
- The count is exact only under the seven-word model. At 32 bits and with
  these constants the model is compared with real messages only for events
  of probability about 2^-{{deep_exp}} and above; its use at the probability of a
  collision, about 2^-{{hit_exp}}, is an extrapolation. No scaled-down
  end-to-end run exists for this pair of lengths and this construction.
- The constants and the class were chosen to make the count large. The
  count is deterministic, but the choice exploits the model, and a failure
  of the model for these constants would not show in the count.
- The count rests on few paths: {{heaviest_share}}% from one beta, {{top2_share}}% from two.
- The calculator is not in the package. It is mine, as is every check of
  it except the independent recount, which is another model's and which I
  reran but did not review line by line.
- All trials of a run share four seed words, the contexts of one pair of
  enumerated words share most of their words, and the {{members}} trials of
  one pass over the class differ only in Y4 and what follows from it;
  their independence is assumed. The 2^{{d_bits}} pairs with the same difference of
  the two enumerated words give, for each value of the third, messages that
  differ in four words only; no measurement has that structure. {{layout_limit_note}}
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
  easy to find, but I found no cheap way to turn one into a message.
- Lengths whose XOR is odd (for example 62 and 63): the pinned call is
  impossible.
- The rule with six conditions on the first stage: it would lower the cost
  of a trial further, but it gives up {{rule6_lost_pct}}% of the count and leaves a
  margin of {{rule6_margin}} between count and assumed factor, below the 3.5 that I
  kept in the earlier packages.

## Checks performed

{{local_checks}}
- A second program, written separately from the experiment program,
  writes the lines of the construction again and checks them on {{check_trials}}
  random trials against a plain forward compression of its own, which it
  compares with the organizer's reference hash on 2,000 of them
  ({{check_result}}).
- The self-test of the submitted program, {{st_cases}} batches with seed {{st_seed}}: all
  {{st_lanes}} lanes right against the real messages of their trials, {{stage_a_ops}}
  operations and {{stage_a_loads}} loads in stage A and {{stage_2_ops}} and {{stage_2_loads}} in stage 2 in every
  batch, no lane above its 36 bits, and every sum below the bound the proof
  quotes for its part. {{big_note_sentence}}
- The contest's judge pipeline was not run locally and no provider key was
  used.

## Package files and next steps

The package is `proof.md`, `claim.json`, `experiments/halfsearch.py` (the
two experiments and the self-test of the operation count),
`experiments/manifest.json` and `certificates/manifest.json` (empty: no
collision is exhibited).

Open, in order of value: scaled-down end-to-end runs of this construction
with short words, which the filed package has for its own construction and
this one lacks; the cause of the dependence of rule A on the context, and a
measurement of rule A with all its conditions on the graphics card, in the
layout of the algorithm (on the processor it exists); an argument in words
for what rule A keeps, or a standard proof checker for the solvers'
answers; a review of the new construction lemmas by a person (helper
agents of the same model have checked them); and a test of the two calls
together below 2^-32 on real messages, which I do not know how to make.

## Tools

Mathematics, code and text: Claude Opus 5.5 in Claude Code. Measurements: one
RTX 3090 and a 24-core desktop. Helper agents of the same model did parts
of the work, and the text says so where it reports them: one built the
reference for the new construction and checked it against the organizer's
hash; one made the count over all values of beta and its checks; one
ported the batch and found the first-stage rules; one made the runs on the
graphics card; one wrote the experiment program of this package, and
another finished its checks after the first was interrupted; and one wrote
this text, ran the solvers on every outcome of the count and reran the
independent recount. {{version_review_sentence}} Programs that two of the
reviewing agents wrote for their review (a third formula for the solver
questions with proofs and a checker, an exact count split by the rule, and
two measurements of the rule on real trials) were run again for this text
and are quoted.

Other AI models were consulted during the work on this construction. They
are all named here, whether or not anything they said was used:

- Grok 4.7 (xAI), through its command-line client and in the owner's own
  chat. Asked how to raise the rate, it listed directions, one of which
  was to try other single-bit differences between the two message lengths.
  That idea is the origin of this package: the pair of lengths 55 and 63
  comes from it. Its other proposals of that list did not work. It was
  also asked to attack the proof of submission `{{last_submission}}`; it found the
  exact part correct and objected to H1 that inside one pass over the
  class every word of the model is a function of Y4, so that the model is
  a statement about averages. The proof of this package says so.
- GPT Sol 6.1 (OpenAI), as a coding agent on the owner's machine. It was given the
  definition of the seven-word system and the constants and asked to count
  the class rate with a method and a program of its own. Its result is
  quoted in the proof with its name, after its program was compiled and
  run again here and compared with my count value by value.
- A model on Venice.ai, in the owner's chat (the model name was not
  recorded). It was asked for prior work and for ideas; nothing from it is
  used, and its list of prior work was not verified.
- GPT in pro mode (OpenAI), in the owner's chat (the version was not
  recorded), consulted for the earlier submissions. It gave general advice
  on method. No construction or constant comes from it.
- GPT-6 Luna (effort high), running as an agent on a second machine of the
  owner's (RTX 3070 cards), ran measurement jobs with my programs for the
  earlier submissions. No result of it is used in this package.

Public notes of other teams on this contest were read for their accounting
conventions (how loads, registers and memory are counted). No construction
and no figure comes from them.

No text or code from any other model is in the package. One figure, the
independent recount, is quoted from another model's computation, with its
name. The submitter is responsible for every claim and every error in it.

Effort: xhigh (Claude Opus 5.5). Grok 4.7 was run through its command-line
client with that client's default settings; no effort level was set for it.

## Limitations

- Analytical cost claim with a declared score-critical heuristic whose
  factor {{factor}} is assumed and not organizer-measured.
- Two different message lengths; relies on the true block length being a
  compression input, as the profile specifies.
- The charge per trial counts stage 2 for {{stage2_share_words}} of the batches. That
  no more run it is heuristic H3, enforced by a budget and not proved, and
  it is a statement about an average over contexts.
- The number of trials is 2^{{T}} instead of 2^128 because of the assumed
  rate; the rest of the gain is the cost of a trial. With only the uniform
  rate assumed it is 2^127 and the claim is {{uniform_time}}.
- A brief literature search found free-start and near-collision results for
  reduced BLAKE variants only. No priority or novelty claim.
