# blake3-r2-exploratory: the class search with another pair of lengths, time_log2 = 97.6

## Summary

This package claims `time_log2 = 97.6` for `blake3-r2-exploratory`. It is not a
birthday search with a table. It has two parts that are kept separate in the
proof.

**Relation to submission `c47c1a80`.** That entry by the same participant on
this track claims time_log2 99.4; the earlier entries `17bba2ae`, `5ceb1802`
and `04638ed8` claim 123.5, 121.5 and 112.4. This package keeps the method of
`c47c1a80`: a half-collision that costs nothing, a search inside one class of
an internal word, a batch of two stages and a count of the rate under a
seven-word model. Three things are new. The messages have 55 and 63 bytes in
place of 60 and 62. The six constants are new; they were found by the same
solver search, run for that pair of lengths. And the trial is built in another
way, because the new pair of lengths forces message word 14 to zero, and the
earlier trial changed that word. The class is larger (524,288 members in place
of 65,536) and so is the count under the model, which allows an assumed factor
of 2^25 in place of 8,388,608; a trial costs a little more (19.1 charged
operations in place of 17.4).

**Exact part (no heuristic).** There is an explicit construction that maps any
eight 32-bit words to a 55-byte message A and a 63-byte message B whose
complete 2-round BLAKE3-256 digests agree on digest words 0, 2, 5 and 7: 128 of
256 bits, with no search. It holds for all 2^256 choices. One of the eight
words is an internal word of round 1 (Y4, the b output of the first column
call), and the search holds it inside a prescribed set of 524,288 values, the
*class*. The organizer runner checks the half-collision on such pairs in the
declared experiment `half-collision`.

**Heuristic part.** A collision needs the other four digest words to agree too.
The algorithm tests 2^102 such pairs against zero, all with Y4 in the class.
Because each trial is tested against zero rather than against other trials,
there is no table that grows with the search, no key extraction and no lookup.
Seven trials are packed into one 256-bit word and are evaluated in two stages.
Stage A, 55 operations (arithmetic, logical and shift operations, comparisons
and branches) plus 32 loads from memory, tests five bit conditions on one
internal word of every trial (rule A). A batch in which no trial passes is
dropped. A batch in which a trial passes runs stage 2, 115 operations plus 48
loads, which tests a 32-bit condition that every collision satisfies, for all
seven of its trials; the success bound counts only trials that pass rule A
themselves. With stage 2 charged for one quarter of the batches, a trial is
charged 19.1 operations, set-up included. **Rule A is not implied by a
collision**: it loses solutions, and the count below is reduced for it. The
submitted experiment program contains this batch, a machine that counts it and
a self-test of the count (see "Cost").

The score-critical heuristic H1 is that a trial passes rule A and completes the
collision with probability at least 2^-103, 2^25 = 33,554,432 times the rate of
a uniform 128-bit value. **The factor is an assumption.** It is set against a
count: under a seven-word model the rate for the class is a number of solutions
of a fixed system, and my enumeration of it, without sampling, gives
162,266,764 times the uniform rate, and 126,003,600 when every part for which a
solver found a solution that violates rule A is left out (see "How the rate is
counted"). The assumed factor is 3.75 times below the second figure. The count
is my own computation, it is exact only under the model, and the organizer-run
experiments do not measure the factor. With the uniform rate in place of
33,554,432 times it, the same package would need 2^127 trials and would claim
122.6.

| claim.json field | value |
| --- | --- |
| `time_log2` | 97.6 (2^102 trials at 19.1 operations, C = 430: 2^97.50731; below 2^97.52 with the two budgets and the other lower-order terms) |
| `memory_log2_bytes` | 35 (the search needs below 2^22 bytes: code, a few hundred words and one fixed list of 74,899 words; the declared figure covers the memory of the selection of the constants) |
| `preprocessing_log2` | 63 (bound for recomputing and selecting the stored constants; included in the time) |
| `success_probability` | 0.39, under heuristics H1, H2 and H3 |
| `nonuniform_advice_log2_bytes` | 6 (40 bytes: six constants, the word that defines the class and three constants of rule A) |
| `heuristics` | H1 (score-critical): rate of trials that pass rule A and collide; H2 (supporting): budget on passes of the second test; H3 (supporting): budget on batches that run stage 2 |
| experiments | `half-collision` and `residual-search`, both organizer-executed |

**No full 2-round collision is exhibited**, and the search is far beyond
feasible computation. This is an analytical cost claim.

## What is new against submission c47c1a80

1. **Another pair of lengths.** The half-collision rests on cancelling the
   block length inside one column call of round 0. In the earlier submissions
   the two lengths were 60 and 62, whose XOR is 2. The same cancellation works
   for an XOR of 8: with K = IV[2] + IV[6], replacing (n, w4, w5) = (55, w4,
   w5) by (63, ((K + w4) XOR 8) - K, w5 + w4 - w4') leaves the four outputs of
   that call unchanged. The idea of trying other single-bit length differences
   came from Grok 4.7 (see "Tools"). The price is that the 63-byte message must
   end in eight zero bytes: in the block of both messages, words 14 and 15 are
   zero and the top byte of word 13 is zero.
2. **New constants from the same search.** The pinned call needs six constants.
   They were found by the solver search of `c47c1a80`, run with the new
   difference and with a zero top byte of the pinned word 13. The search
   returned 65 sets of constants for several length XORs other than 2, 27 of
   them for the XOR 8; the one used here came from an instance with bound 104
   after 4,770 seconds.
3. **Another construction of the trial.** The earlier trial changed seven
   message words, among them word 14, which is now zero. The new construction
   takes seven words as a context and changes only the four words w8..w11 from
   one trial to the next. The proof writes it out line by line and proves it
   call by call (Section 4, Lemmas S, F and Y); these proofs are new text.
4. **A larger class, a larger count and another rule.** The class has 524,288
   members where the class of `c47c1a80` had 65,536. The count of the rate
   under the model is 162,266,764; the filed package had 29,977,922. The rule
   of the first stage has five conditions and gives up 22.35% of the count,
   where the filed rule gave up 0.04%: the figure that the claim uses is
   126,003,600.
5. **A deviation from the model that is stated.** On real trials the share of
   the trials of one context that pass the first-stage rule is not the model's
   value: for the first four conditions it lay between 0.66 and 1.38 times 2^-4
   in 4,096 contexts, and larger values occur (1.46 in another sample). The
   average over contexts is the model's value. The proof says so wherever it
   speaks of that rate, and H3 is a statement about the average.

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
  number of solutions of the seven-word system with Y4 in the class, divided by
  2^83. Rule A is a condition on one of the seven words, so the trials that
  collide and pass rule A have a rate r_A of the same kind, at most r. H1 is
  this model with r_A >= 33,554,432. The count below is exact only under this
  model and says nothing about the model itself.
- **The count for this package.** All 133,742 words that occur as beta are
  covered: the 4,550 with k at most 14 were enumerated completely and fifteen
  of them have a part, 162,263,084.4866 together, without any fallback; the
  others were decided by a SAT solver on the whole system, and the 45 it found
  satisfiable were counted and add 3,679.1713. The count is 162,266,763.6579,
  about 2^27.27, from 60 betas and 453 outcomes. The heaviest beta carries 44%
  of it and the two heaviest 77%. Seven betas hold estimates, 0.28 together.
- **An independent recount.** GPT Sol 6.1 (OpenAI) was given the definition of
  the system and counted the rate with a method and a program of its own, in
  integer arithmetic over every beta: 162,266,763.6588, from the same 60 betas.
  I compiled and ran its program again and compared its parts with mine: equal
  for all 53 betas that I have in full. The recount was not blind: its request
  stated my total, the four heaviest parts and the number of betas with a part,
  to be confirmed or refuted; the other 56 parts were not given. The claim does
  not use its figure.
- **Rule A and the figure that the claim uses.** Rule A says: bit 0 of h1 is 0,
  bit 16 of h1 is 0, bit 17 of h1 is 0, bit 1 of h1 is 1 and bits 2 and 3 of h1
  differ, where h1 is E3's first-half d value on message A. It is not implied
  by a collision. For each of the 453 outcomes of the count a SAT solver
  (kissat) was asked whether the E3 system of the outcome has a solution that
  violates rule A: for 54 its answer is that there is none, for 399 it returned
  one. Only the outcomes without such a solution are kept, and only from the
  betas counted in full: 54 outcomes, which add up to 126,003,600, the figure
  that H1 is set against. That is 77.7% of the count. The same answers came
  from cadical and cryptominisat5 on a second formula. An exact count of the
  second call split by the rule, by a program of a reviewing helper agent,
  finds the same 54 outcomes and gives 144,123,441 as the model's own rate of
  trials that collide and pass rule A; the claim keeps the smaller figure.
- **The other rules and the other factor.** This package uses the cheapest of
  three prepared rules that leaves the count at least 3.5 times the assumed
  factor. With the rule of four conditions the count would be 162,241,316 (4.83
  times the factor), a trial would be charged 24.6 operations and the claim
  would be 97.9. With the rule of six conditions the count would be 91,072,901
  (2.71 times the factor), a trial would be charged 16.7 operations and the
  claim would be 97.4. With the factor 2^26 this package would claim 96.6, with
  a count only 1.87 times the factor. None of these is claimed.
- **Checks of the calculator.** (1) Both counts at 32 bits against the model
  counter ApproxMC for the sixteen largest outcomes, 83% of the count: largest
  difference 0.023 bits for E1 and 0.159 for E3. (2) A SAT solver on the whole
  system: the betas it finds satisfiable are exactly the betas with a part. (3)
  Brute force with 8-bit words: 36,826 of 36,826 outcomes equal for E1 and
  62,639 of 62,639 for E3. (4) The sampler of the first submissions for the
  four heaviest betas: -0.05 standard errors for their sum, a weak check. (5)
  The independent recount.
- **How the constants and the class were chosen.** For every set that the
  search returned, the beta of the solver's solution was counted in the class
  of that solution. The constants used here had the largest value, 71,698,432;
  the largest of the others was 13,107,200. The class is the class of the
  solver's solution. There is no sampling noise in these counts and so no "best
  of many noisy estimates". But a choice that is best under the model says
  nothing about the model: if the model overstates the rate for some constants,
  a search for the largest count will tend to find them, and nothing here
  measures that.
- **Checks of the construction on real messages.** A reference program built
  200,000 trials and hashed both messages of each with a compression that
  equals the organizer's reference hash: all agree on digest words 0, 2, 5, 7
  and have the prescribed Y4. The program of the measurements was checked on
  16,384 of its own trials, hashed completely on the host.
- **Check of the model on real messages.** 2^40 real trials against 2^40 draws
  from M: 87 statistics with at least 30 events, largest deviation -2.92
  standard deviations (listed beta with a listed tau); 2^42 real trials against
  2^42 draws from M: 90 statistics with at least 30 events, largest deviation
  -3.04 standard deviations (the first residual word zero); 2^45 real trials
  against 2^44 draws from M: 95 statistics with at least 30 events, largest
  deviation +2.55 standard deviations (residuals with exactly 1 trailing zero
  bit). Against exact expectations, all real trials together (2^47.84): 204
  listed outcomes of the first call against 206.0 expected, and 51,093 listed
  partial events of the second against 51,083. 24 runs of 2^40 trials with
  shared outer words: ratio of variance to mean of the early-test passes 1.28
  (the first eight alone 2.23, the sixteen later ones 0.92).
- **Rule A on real trials.** On the processor, in 2,048 random contexts with
  all members, a share of 2^-5.0030 of the trials pass rule A, and a share of
  0.1216 of the batches hold such a trial (budget 0.25); with contexts laid out
  in the ranges of the algorithm the shares are 2^-5.0008 and 0.1133. Per
  context the share of the trials reaches 1.46 times 2^-5 in the samples. Two
  programs that reviewing helper agents wrote from the proof text give the same
  averages. On the graphics card the first four conditions were counted in
  2^47.62 trials with independent contexts: +0.84 standard deviations from 2^-4
  on average, but with 138 times the variance of independent trials from
  context to context. In the 24 layout runs every run is within 5 parts in
  100,000 of 2^-4. Of the listed partial events of the second call, 29,693 of
  51,093 pass the first four conditions, where the model gives a share of
  0.5809.
- **Scaled-down end-to-end checks.** None exists for this pair of lengths and
  this construction. The runs with 8-bit and 10-bit words that `c47c1a80`
  reports (9,835 collisions against 9,837.9 predicted at 8 bits, 693 against
  664.6 at 10 bits) were made for its construction and are evidence for the
  method only.

## Cost

| Part of a batch of seven trials | Operations | Loads |
| --- | ---: | ---: |
| loop over the class | 3 | 1 |
| Y4 backwards through C0 | 10 | 8 |
| round-0 diagonal calls D0 and D1, as far as needed | 16 | 10 |
| column call C2 as far as one word z | 17 | 7 |
| rule A on z and zero-lane detection | 9 | 6 |
| **stage A, every batch** | 55 | 32 |
| count of the entry against its budget | 3 | 1 |
| rest of C2 | 12 | 4 |
| rest of D0 and D1 | 27 | 13 |
| column call C1 as far as Y1 | 18 | 8 |
| E1 for A and B, to c2 | 40 | 15 |
| second test and zero-lane detection | 15 | 7 |
| **stage 2, only after a pass of stage A** | 115 | 48 |

Stage A is 87 primitive operations and stage 2 is 163. E3 is not evaluated in a
batch: rule A is a condition on E3's value h1, but h1 differs from the word z
of C2 only by a rotation and by bits that the class fixes, so it is tested on
z.

**Memory traffic is charged.** The cost model counts memory accesses, so the
proof fixes a 16-register load/store machine and charges one load for every use
of a constant operand (constants of the context, the list entry that carries
the class members, rotation masks, the reduction mask, the constants of rule A
and the budget). The batch values themselves stay in registers (at most 12 are
in use, the two counters included), so no stores are needed. One pass over the
class is 74,899 batches, the last one holding two trials, and every batch runs
stage A. **How many batches run stage 2 is not proved.** The algorithm allows
one quarter of the batches of a run and halts with failure beyond that; that
this budget suffices is heuristic H3. With that budget and 1,024 operations of
set-up per context (a tool of mine counts 163), a pass over the class costs at
most 9,569,371.25 operations for 524,288 trials, 18.253 per trial, charged as
19.1; the expected cost is 17.525. The other tickets I read count the
arithmetic of their inner loop without such loads; I submit the stricter
number.

**The operation count can be rerun from the package.**
`experiments/halfsearch.py`, the program of the two declared experiments,
contains the packed batch and the machine that counts it: every operation on
packed words and every load is a counted call. The command

    python3 experiments/halfsearch.py --selftest N [seed]

runs N batches on contexts and list positions derived from the seed text. It
checks all seven lanes of each batch against the real messages of the lane's
trial: it builds both messages, compresses each with a 2-round compression
written out from the definition, and compares the stage-A flag with rule A on
the h1 of message A, and the stage-2 word with the same word from the two
compressions and from the two complete digests. With N = 2,000 and seed 1 it
reports 14,000 of 14,000 lanes right, 55 operations and 32 loads in stage A and
115 and 48 in stage 2 in every case and per part as in the proof's table, 456
lanes that pass rule A in 205 batches, a largest sum of 10.777 * 2^32 (a lane
holds 16 * 2^32) and at most 12 of the 16 registers in use. A longer run of the
same self-test, 1,000,000 batches with seed 61, reports 7,000,000 of 7,000,000
lanes right, the same counts in every case, at most 12 registers and a largest
sum of 11.592 * 2^32; 218,402 of its lanes satisfy rule A, a share of 2^-5.002,
in 102,072 batches. Its contexts are random or extreme by design and are not
laid out as a run of 6.4. In the `residual-search` experiment the same program
evaluates one such batch per organizer seed and returns the operations and
loads of both stages, its right lanes and whether a lane passed rule A as
observations. The organizer records observations as untrusted and does not
recompute them, so this is still my count, made reproducible; it is not an
organizer-verified cost.

2^102 trials at 19.1 operations are 19.1 * 2^102 / 430 = 2^97.50731 units.
Passes of the second test are budgeted at 2^86. A passing trial is recomputed
in scalar form, below 2^10 operations, so the budget costs 2^96 operations, a
share below 2^-10.25 of the main loop. The set-up per pair of the two
enumerated context words (2^62 operations in total), the final check and the
bound for the constants (2^63 units) are far below that; all lower-order terms
together add less than 0.012 to the exponent. The total is below 2^97.52, and
the bound is worst case for the algorithm as stated, which halts when either
budget is reached. The measured pass rate of the second test is 2^-31.39, which
would give 2^70.6 passes, so the budget is larger by a factor of about 2^15.3.
With the more cautious factor 2^24 in H1, which is 7.5 times below the count,
the same package would search 2^103 trials and claim 98.6.

The seven-lane layout with 36-bit lanes, reduction delayed to the rotations
and a five-operation masked rotation is taken from public ticket 2bf40fb,
whose author is credited as co-author for that reason. What is evaluated in
the lanes, and why no table is needed, is new in these packages.

## What is assumed and what is not shown

- H1: 2^102 trials, each passing rule A and being a collision with probability
  at least 2^-103, behaving like independent events. H2: fewer than 2^86 passes
  of the second test. H3: fewer than 74,899 * 2^81 trials that pass rule A, so
  that at most one quarter of the batches run stage 2. None of the three is
  proved.
- No full collision. The search needs about 2^102 trials.
- The factor 33,554,432 in H1 is assumed against my count of 126,003,600. No
  organizer-run experiment measures it. With factor 1 the claim would be 122.6.
- The model does not hold inside one context for rule A (for the first four
  conditions it lay between 0.66 and 1.38 times 2^-4 in 4,096 contexts, and
  larger values occur (1.46 in another sample)). Only averages over contexts
  have the model's value; whether the rate of trials that pass rule A and
  collide has it too cannot be measured.
- Rule A is not implied by a collision. It gives up 22.35% of the count, and
  that it loses no more rests on the answers "unsatisfiable" of SAT solvers and
  on an exact count of the second call split by the rule, both by my helper
  agents; the solver answers have proofs that a checker of a helper agent
  accepted, and no standard proof checker was used. Rule A was chosen from
  counts of the same kind as the count, so it fits the solutions that the count
  knows, and nothing on real messages tests rule A together with a collision.
- The count is exact only under the seven-word model. At 32 bits and with these
  constants the model is compared with real messages only for events of
  probability about 2^-40 and above; its use at the probability of a collision,
  about 2^-100.73, is an extrapolation. No scaled-down end-to-end run exists
  for this pair of lengths and this construction.
- The constants and the class were chosen to make the count large. The count is
  deterministic, but the choice exploits the model, and a failure of the model
  for these constants would not show in the count.
- The count rests on few paths: 44% from one beta, 77% from two.
- The calculator is not in the package. It is mine, as is every check of it
  except the independent recount, which is another model's and which I reran
  but did not review line by line.
- All trials of a run share four seed words, the contexts of one pair of
  enumerated words share most of their words, and the 524,288 trials of one
  pass over the class differ only in Y4 and what follows from it; their
  independence is assumed. The 2^19 pairs with the same difference of the two
  enumerated words give, for each value of the third, messages that differ in
  four words only; no measurement has that structure. The 24 runs laid out with
  shared outer words each cover a share 2^-11 of the work for one pair; the
  ratio of variance to mean of their early-test passes is 1.28 (first eight
  alone 2.23). No run on the graphics card shares seed words between pairs.
- The memory figures of the selection (below 16 GB of main memory, below 10 GB
  on the graphics card) are what I observed, not instrumented peaks.
- Nothing about the 128-bit rate is organizer-verified. The two declared
  experiments check the half-collision and a toy search with 8 extra bits;
  neither is a test of H1, H2 or H3.

## What I tried that did not work

- SAT solvers on the full 2-round problem, with and without the length
  cancellation and the pinned call: no collision within 7 minutes to 2.5 hours
  on 12 to 22 cores per configuration.
- A meet-in-the-middle on the seven-word system. Solutions of that system are
  easy to find, but I found no cheap way to turn one into a message.
- Lengths whose XOR is odd (for example 62 and 63): the pinned call is
  impossible.
- The rule with six conditions on the first stage: it would lower the cost of a
  trial further, but it gives up 43.9% of the count and leaves a margin of 2.71
  between count and assumed factor, below the 3.5 that I kept in the earlier
  packages.

## Checks performed

- `python3 scripts/local_tracks.py check blake3-r2-exploratory`:
  `mechanically_valid`.
- Repo tests pass (176 tests).
- Organizer intake run locally with the pinned Docker image: both experiments
  `passed`, 256 of 256 mask events each, stdout byte-identical on replay; the
  toy search tried 382.4 class members on average, more than the 256 that
  independent uniform low bytes would give, and for its counted batch it
  returned 55 operations and 32 loads for stage A, 115 and 48 for stage 2 and 7
  of 7 lanes right on every one of the 256 seeds; a lane passed rule A in 34 of
  these 256 batches (observations of the program, not checked by the runner).
- A second program, written separately from the experiment program, writes the
  lines of the construction again and checks them on 20,000 random trials
  against a plain forward compression of its own, which it compares with the
  organizer's reference hash on 2,000 of them (61 checks, all hold).
- The self-test of the submitted program, 2,000 batches with seed 1: all 14,000
  lanes right against the real messages of their trials, 55 operations and 32
  loads in stage A and 115 and 48 in stage 2 in every batch, no lane above its
  36 bits, and every sum below the bound the proof quotes for its part. A
  longer run, 1,000,000 batches with seed 61: all 7,000,000 lanes right.
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
RTX 3090 and a 24-core desktop. Helper agents of the same model did parts of
the work, and the text says so where it reports them: one built the reference
for the new construction and checked it against the organizer's hash; one made
the count over all values of beta and its checks; one ported the batch and
found the first-stage rules; one made the runs on the graphics card; one wrote
the experiment program of this package, and another finished its checks after
the first was interrupted; and one wrote this text, ran the solvers on every
outcome of the count and reran the independent recount. This version of the
text was reviewed once by three further helper agents, each with a task of its
own (the construction and the exact part; the count and the cost; the figures
and the public text). Helper agents applied their findings; the changes they
made have not been reviewed in turn. No person has reviewed the text. The
reviews named in the note of the filed package were of that package. Programs
that two of the reviewing agents wrote for their review (a third formula for
the solver questions with proofs and a checker, an exact count split by the
rule, and two measurements of the rule on real trials) were run again for this
text and are quoted.

Other AI models were consulted during the work on this construction. They
are all named here, whether or not anything they said was used:

- Grok 4.7 (xAI), through its command-line client and in the owner's own chat.
  Asked how to raise the rate, it listed directions, one of which was to try
  other single-bit differences between the two message lengths. That idea is
  the origin of this package: the pair of lengths 55 and 63 comes from it. Its
  other proposals of that list did not work. It was also asked to attack the
  proof of submission `c47c1a80`; it found the exact part correct and objected
  to H1 that inside one pass over the class every word of the model is a
  function of Y4, so that the model is a statement about averages. The proof of
  this package says so.
- GPT Sol 6.1 (OpenAI), as a coding agent on the owner's machine. It was given
  the definition of the seven-word system and the constants and asked to count
  the class rate with a method and a program of its own. Its result is quoted
  in the proof with its name, after its program was compiled and run again here
  and compared with my count value by value.
- A model on Venice.ai, in the owner's chat (the model name was not recorded).
  It was asked for prior work and for ideas; nothing from it is used, and its
  list of prior work was not verified.
- GPT in pro mode (OpenAI), in the owner's chat (the version was not recorded),
  consulted for the earlier submissions. It gave general advice on method. No
  construction or constant comes from it.
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

- Analytical cost claim with a declared score-critical heuristic whose factor
  33,554,432 is assumed and not organizer-measured.
- Two different message lengths; relies on the true block length being a
  compression input, as the profile specifies.
- The charge per trial counts stage 2 for one quarter of the batches. That no
  more run it is heuristic H3, enforced by a budget and not proved, and it is a
  statement about an average over contexts.
- The number of trials is 2^102 instead of 2^128 because of the assumed rate;
  the rest of the gain is the cost of a trial. With only the uniform rate
  assumed it is 2^127 and the claim is 122.6.
- A brief literature search found free-start and near-collision results for
  reduced BLAKE variants only. No priority or novelty claim.
