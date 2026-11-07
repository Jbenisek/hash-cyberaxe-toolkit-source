# blake3-r2-exploratory: a free half-collision and a counted class, time_log2 = 99.4

## Summary

This package claims `time_log2 = 99.4` for `blake3-r2-exploratory`. Unlike the
other tickets on this track that I have read, it is not a birthday search with
a table. It has two parts that are kept separate in the proof.

**Relation to submissions `17bba2ae`, `5ceb1802` and `04638ed8`.** Those three
entries by the same participant on this track (time_log2 123.5, 121.5 and
112.4) use the same half-collision and, the last of them, the same class
search. This package keeps the construction and the trial of `04638ed8`
unchanged. Four things are new: the six constants, the class, what the assumed
rate is set against, which is now a count without sampling in place of a
sampled estimate, and the batch, which now has two stages. The claim is 13.0
bits below that of `04638ed8`: 12 bits are the factor that H1 assumes, 2^23 =
8,388,608 here and 2^11 = 2,048 there, and about 0.97 bits are the cost of a
trial, 17.4 charged operations here and 34 there; the rest is rounding.

**Exact part (no heuristic).** There is an explicit construction that maps any
nine 32-bit words to a 60-byte message A and a 62-byte message B whose complete
2-round BLAKE3-256 digests agree on digest words 0, 2, 5 and 7: 128 of 256
bits, with no search. It holds for all 2^288 choices. A second exact
construction walks through such pairs while it holds one internal word of round
1 (Y4, the b output of the first column call) inside a prescribed set of 65,536
values, the *class*. The organizer runner checks the half-collision on such
pairs in the declared experiment `half-collision`.

**Heuristic part.** A collision needs the other four digest words to agree too.
The algorithm tests 2^104 such pairs against zero, all with Y4 in the class.
Because each trial is tested against zero rather than against other trials,
there is no table that grows with the search, no key extraction and no lookup.
Seven trials are packed into one 256-bit word and are evaluated in two stages.
Stage A, 64 operations (arithmetic, logical and shift operations, comparisons
and branches) plus 36 loads from memory, tests six bit conditions on one
internal word of every trial (rule A). A batch in which no trial passes is
dropped. A batch in which a trial passes runs stage 2, 96 operations plus 42
loads, which tests a 32-bit condition that every collision satisfies, for all
seven of its trials; the success bound counts only trials that pass rule A
themselves. With stage 2 charged for one eighth of the batches, a trial is
charged 17.4 operations, set-up included. **Rule A is not implied by a
collision**: it loses solutions, and the count below is reduced for it. The
submitted experiment program contains this batch, a machine that counts it and
a self-test of the count (see "Cost").

The score-critical heuristic H1 is that a trial passes rule A and completes the
collision with probability at least 2^-105, 2^23 = 8,388,608 times the rate of
a uniform 128-bit value. **The factor is an assumption.** It is set against a
count: under a seven-word model the rate for the class is a number of solutions
of a fixed system, and my enumeration of it, without sampling, gives 29,977,922
times the uniform rate as a lower bound, and 29,965,882 when every part for
which a solver found a solution that violates rule A is left out (see "How the
rate is counted"). The assumed factor is 3.57 times below the second figure.
The count is my own computation, it is exact only under the model, and the
organizer-run experiments do not measure the factor. With the uniform rate in
place of 8,388,608 times it, the same package would need 2^127 trials and would
claim 122.4.

| claim.json field | value |
| --- | --- |
| `time_log2` | 99.4 (2^104 trials at 17.4 operations, C = 430: 2^99.37282; below 2^99.39 with the two budgets and the other lower-order terms) |
| `memory_log2_bytes` | 35 (the search needs below 2^20 bytes: code, a few hundred words and one fixed list of 9,363 words; the declared figure covers the memory of the selection of the constants) |
| `preprocessing_log2` | 63 (bound for recomputing and selecting the stored constants; included in the time) |
| `success_probability` | 0.39, under heuristics H1, H2 and H3 |
| `nonuniform_advice_log2_bytes` | 6 (40 bytes: six constants, the word that defines the class and three constants of rule A) |
| `heuristics` | H1 (score-critical): rate of trials that pass rule A and collide; H2 (supporting): budget on passes of the second test; H3 (supporting): budget on batches that run stage 2 |
| experiments | `half-collision` and `residual-search`, both organizer-executed |

**No full 2-round collision is exhibited**, and the search is far beyond
feasible computation. This is an analytical cost claim.

## What is new against the earlier submissions

1. **Constants found by a solver, not by farming.** The constants of the
   earlier submissions were the best of 4,140 random valid sets. Here one SAT
   instance (solver kissat) holds the pinned call for both messages, the two
   calls E1 and E3 that produce the open half of the digest, for both messages
   and with real word values, a zero residual, and a bound on the number of bit
   positions at which a difference is active in six additions. Every model is a
   valid set of constants together with one solution of the system that the
   residual depends on. When this note was written the search had returned 21
   such sets and was still running; the one used here came from an instance
   with bound 108 after 2,149 seconds.
2. **A larger class with a far larger count.** For the new constants the
   difference W4 - W4' is fffffffe, that is -2 where the earlier constants had
   +2; every formula of the proof is stated for the word W4 - W4' and holds for
   both. The class is eta = e7c1815f. It has 65,536 members, 16 free bits of
   one word, where the class of `04638ed8` had 4,096; the word ROL(eta,16) has
   bit 31 here, and Lemma Q is stated so that it covers that case (bit 31 of
   the word that carries the class is always free).
3. **Under the model, the rate is counted, not sampled.** In the earlier
   submission the rate of the class was a sampled estimate, 7,319 with a
   standard error of 816 for a heavy-tailed quantity. Here the outcomes of one
   of the two calls are enumerated completely, and for each outcome both its
   probability and the number of matching inputs of the other call are counted.
   The result is a deterministic number. The sampler of the earlier submission
   is kept as a check of the new calculator. The calculator is not part of the
   package; the proof prints the outcomes of the heaviest beta with their two
   counts, and one complete solution inside the class, so that the largest part
   of the figure can be recomputed without it.
4. **A batch of two stages.** In the earlier submissions every batch computed
   the first halves of both calls E1 and E3, 154 operations and 74 loads for
   every batch. Here every batch computes only as far as one word of the column
   call C2, from which the bits of E3 that rule A needs follow, and stops
   unless one of its seven trials passes rule A; about one batch in ten goes
   on. The second stage tests a necessary condition on E1 alone (Lemma N of the
   proof) in place of the earlier early test, so E3 is not evaluated in a batch
   at all. Rule A was read off the counts. Almost all counted solutions satisfy
   it, not all: 0.0402% of the count is given up, and the cost of a trial falls
   from 34 to 17.4 charged operations.

## What is new against the earlier version of this package

An earlier version of this package was prepared and not filed. It has the same
constants, the same class (eta = e7c1815f), the same count of 29,977,922 and
the same assumed factor 2^23, a batch of one stage with 154 operations and 74
loads, 34 charged operations per trial, and time_log2 100.4. Against it, four
things are new here. (1) The batch has two stages: stage A, 100 operations with
its loads, tests rule A, six bit conditions on one internal word; only a batch
in which a trial passes runs stage 2, 138 operations. A trial is charged 17.4
operations, which lowers the claim by 1.0 to 99.4. (2) The test of the second
stage is another necessary condition, on one of the two calls alone (Lemma N),
in place of the early test of Lemma E. (3) Rule A is not implied by a
collision, so the figure that H1 is set against is smaller: 29,965,882, the
count without every outcome for which the solver found a solution that violates
rule A (40 of 287 outcomes, 12,040 of the count). (4) A third heuristic, H3, is
declared: at most one eighth of the batches enter stage 2, with a budget that
the algorithm enforces. The budget on the passes of the second test is now
2^-16 of the trials, and H2 and H3 are each allowed a failure probability of
0.0005. The declared advice is 2^6 bytes, because the three constants of rule A
are stored with the six constants and eta.

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
  number of solutions of the seven-word system with Y4 in the class, divided by
  2^80. Rule A is a condition on one of the seven words, so the trials that
  collide and pass rule A have a rate r_A of the same kind, at most r. H1 is
  this model with r_A >= 8,388,608. The count below is exact only under this
  model and says nothing about the model itself.
- **The calculator.** Write beta for the XOR difference of E1's first-half b
  value; it depends on one of E1's words alone, and only finitely many words
  occur. A beta fixes k bits of that word, so it occurs with probability 2^-k.
  For one beta the outcomes of E1 are pairs (tau, eps) of XOR differences of
  its a and c outputs. tau runs over every difference that the addition in
  question can show, enumerated by a search over its bits with a carry
  automaton and no limit on its weight; eps is one of two words that the class
  fixes, or none. For each outcome the calculator counts the inputs of E3 that
  match it (the count of the earlier submissions) and the probability that E1
  produces it (a new automaton over the bits of one word, with a borrow and a
  carry as its state). The class-rate part of a beta is a weighted sum of the
  products, and r is the sum over all betas; leaving betas out makes the figure
  a lower bound.
- **The count for this package.** The list given to the calculator holds every
  beta with k at most 14: 4,272 betas, the smallest k being 9. A uniform d1 has
  a beta of the list with probability 0.469; that is not the share of the class
  rate that the list holds, which is not known. 2,110 betas of the list have no
  eps and contribute nothing, 2,162 were enumerated completely (for three of
  them, all without a part, not without sampling: see the second count below),
  and 39 have a nonzero part: 29,977,922 together. No beta outside that list
  was counted, so the count is 29,977,922. That is about 2^24.84. The heaviest
  beta carries 47% of it and the two heaviest 60%. The calculator was run a
  second time for all 39 betas with a nonzero part and returned the same parts.
  Its output states, for every one of them, how many outcomes went through the
  random-subset branch of the E3 count and how many E1 counts fell back to a
  product formula: 0 and 0 in all. Of the 508 outcomes of these betas that have
  a nonzero E3 count, 287 have a nonzero E1 count as well; only these enter the
  sum.
- **Rule A and the figure that the claim uses.** Rule A says: bit 16 of h1 is
  1, bits 0 and 1 of h1 are equal, bits 1 and 2 of h1 are equal, bits 2 and 3
  of h1 are equal, bits 3 and 4 of h1 differ and bits 23 and 24 of h1 differ,
  where h1 is E3's first-half d value on message A. It is not implied by a
  collision. For each of the 287 outcomes of the count a SAT solver (kissat)
  was asked whether the E3 system of the outcome has a solution that violates
  rule A: for 247 its answer is that there is none, for 40 it returned one.
  These 40 outcomes are left out in full, which removes 12,040 and leaves
  29,965,882, the figure that H1 is set against. Two other solvers (cadical and
  cryptominisat5), on a formula that a reviewing helper agent wrote separately,
  give the same answer for every outcome; no certificate was checked for any of
  them. For this package the 39 betas with a nonzero part were counted once
  more with the compiled calculator in its present form, which was run and not
  built again: it returns the same 39 parts, 29,977,922 in all, no outcome
  through either fallback, and the same 287 outcomes with a nonzero product.
  The products P1 * N3 of the single outcomes are taken from the recount that
  prints both factors in full; their logarithms agree with the two decimals
  that the calculator prints for every outcome. The whole list was also counted
  once more with that binary, all 4,272 betas: the same betas have no eps, the
  same 39 have a part, every part is the same, and the sum is 29,977,922. For
  three betas of the list, c81cd8b3, f81c2873 and f81c28b3, all without a part,
  that run reports what the per-beta file of the first count does not record:
  the E3 count of seven outcomes went through the random-subset branch, so
  these values are estimates. The 69 outcomes of these betas with a nonzero E3
  value all have an exact E1 count of zero, so their product is zero whatever
  N3 is. An outcome whose E3 value that branch estimated as zero would be
  missing from the sum; that can only make the figure smaller. So for these
  betas the E3 side was not counted without sampling. How much of the rate rule
  A really keeps was counted for a shorter list. The thread that found the rule
  split the E3 count of every outcome by the bits of h1, with a program of its
  own, for the 242 outcomes of the 30 betas with a part among the 1,500
  lightest betas, whose parts add up to 29,862,848: rule A keeps 0.999839 of
  that sum. The figure that the claim uses keeps less, because it gives up in
  full every outcome for which a violating solution was found. The rule was
  read from 30 of the 39 betas. In the nine that were added later the outcomes
  with a violating solution carry 1.25% of their part, against 0.036% in those
  30; betas that are not counted may violate the rule more often still. The
  proof prints one complete solution of the system that violates rule A.
- **The choice of the class.** A solver search with the constants held fixed,
  which asks for a solution with a pair (eta, beta) not seen before, returned
  40 pairs in 33 different classes. An exact grid over 2,847 classes within
  Hamming distance 6 of the first two, restricted to the 522 betas with k at
  most 12, was stopped before it had finished; the classes that its partial
  output showed as strong were counted in full as well. This exploration was
  closed before the text was finished, so the figures that follow are its final
  state. 34 classes of these constants have a count over the same 1,500 betas.
  The class used has 29,862,848 there; it is the second largest of the 34
  classes counted: eta = e74181df has 36,249,523 over the same list and
  36,358,944 over 4,272 betas, and nearly the same checks (ApproxMC on the E1
  count, a SAT solver and ApproxMC on the E3 count, 2^40 real trials against
  the model, 2^42 real trials against the model, eight layout runs with
  variance over mean 0.74 and 40 listed E1 outcomes against 37.52 in 2^44 real
  trials); it lacks a run that counts partial E3 events on real messages. The
  class used is kept because this note, the proof, the run on partial E3 events
  and the reviews were made for it, and because rule A and the two-stage batch
  are worked out for it alone; with a batch of one stage the assumed factor and
  the claim would be the same for either class.
- **The sampler as a check.** The sampler of `04638ed8` draws E1 at random for
  one beta and counts E3 for each draw. Four betas, which carry 82% of the
  count, were given 16 runs of 2^34 draws each, with the same seeds for every
  beta. For these four betas together the sampler gives 24,522,752 with
  standard error 1,451,568 against 24,515,584 counted; the single betas lie
  between -1.0 and +2.1 standard errors. That the sums agree so closely is a
  cancellation: the four differences are -0.52, +0.80, -0.34 and +0.07 million.
  The deviation of +2.1 for beta 58146852 is not explained. A reviewing helper
  agent compared the sampler's draws per outcome with the calculator's P1: for
  this beta the chi-square statistic is 29.1 on 10 degrees of freedom, for the
  other three 9.8 on 12, 3.3 on 6 and 11.1 on 10; its own Monte Carlo of the
  same probabilities agrees with the calculator. So the excess is on the
  sampler's side, and its cause was not found. The sampler runs are short
  because the sampler fails when a run is long and the rate is as high as here
  (its output buffer overflows). The sampler uses the same E3 count as the
  calculator, so it checks the enumeration of outcomes and the E1 count, not
  the E3 count.
- **Checks of the calculator.** (1) Against the sampler on other constants,
  among them the class and the heaviest beta of `04638ed8`: 6,164.7 counted
  against 6,168 sampled with standard error 810. (2) The new E1 count against
  brute force with 8-bit words: all 55,447 outcomes with solutions of 40 random
  cases equal. (3) The E1 count at 32 bits against the model counter ApproxMC,
  for these constants: 16 outcomes of one beta with a largest difference of
  0.00 bits, and one outcome that it counts as zero has no solution. (4) The E3
  count for these constants against a SAT solver and ApproxMC, for the outcomes
  of four betas: ratio of sums 0.994 for the 30 largest counts and 0.999 for
  the other 17, and the 40 zero counts tested have no solution. (5) No limit on
  the weight of tau was used. The proof gives the figures. The E1 count and the
  enumeration of outcomes are new code, written in the night before this text.
- **Checks by reviewing helper agents.** Three reviewing helper agents wrote
  programs of their own from the proof of an earlier version of this package
  (same constants, class and count; rule A and the two-stage batch came later
  and were not in front of them). Two of them compared the whole calculation at
  8-bit words with a brute force of the seven-word system (in one case 60
  constant sets, 17,258 pairs of a class and a beta, 694,652,928 solutions, no
  pair differs). They made Monte Carlo estimates at 32 bits of the E1
  probabilities (sums of P1 * N3 between 0.980 and 1.012 of the calculator's on
  the four sampled betas) and of E3 counts (four within 0.14 bit, six within
  0.12 bit). One found the solution inside the class that the proof prints.
  They are helper agents of mine, not independent parties.
- **How the constants and the class were chosen.** For 17 of the sets that the
  search returned, the class of the solver's solution was counted over its 150
  lightest betas. The constants used here had the largest count, 5,072,896; the
  largest of the others was 2,925,288 and their median 9,618. The class of this
  package is not the class of that solution; its eta differs from that of the
  solver's solution in one bit. How it was chosen among the classes counted is
  said under "The choice of the class" above. There is no sampling noise in
  these counts and so no "best of many noisy estimates". But a choice that is
  best under the model says nothing about the model: if the model overstates
  the rate for some constants, a search for the largest count will tend to find
  them, and nothing here measures that.
- **Check of the trial on real messages.** A host program rebuilt the messages
  of 16,384 random trials of the class search with these constants and this
  class, and hashed both messages of each in full: all agree on digest words 0,
  2, 5, 7, have Y4 in the class and the residual the proof computes.
- **Check of the model on real messages, independent contexts.** Real trials of
  the class search with these constants were compared with the same number of
  draws from the model on how often residual words vanish, on low residual
  weights, on the early test of the earlier submissions (Lemma E of the proof;
  the algorithm of this package does not use it) and on the number of trials in
  which E1 requires the class, which are the passes of this package's second
  test. Every thread of the generating program has its own random context and
  makes 4,096 trials with random alpha and random class members; that is not
  the algorithm's layout, in which all contexts of a run share four seed words.
  Result: 2^40 trials of each kind: early test passes 11,418 on real messages
  against 11,249 in the model; residuals of weight at most 32: 105,429 against
  104,997; the largest deviation among the printed statistics is 2.5 standard
  deviations. A second comparison with 2^42 trials of each kind: early test
  passes 45,141 against 45,349, trials in which the first call requires the
  class 5,877 against 6,035, largest deviation 2.1 standard deviations.
- **Deeper counts on real messages, one call at a time.** Two runs of 2^44 real
  trials found 42 and 59 trials with one of the 69 E1 outcomes that carry most
  of the count, together 101 where the calculator predicts 86.32 (+1.6 standard
  deviations; the second run alone +2.4). The second of these runs also found
  721 trials with one of 69 partial E3 events, two of the three conditions that
  the E3 count puts on an outcome, where a program derived from that count
  predicts 706.0; the same counter on 2^42 draws from the model found 161
  against 176.5. In both runs the trials whose beta is one of the six heaviest
  are slightly too few: -1.8 and -1.5 standard deviations, together -2.3, about
  6 in a million. I have not explained it. These counts test E1 alone, and E3
  alone without the third of its conditions. Nothing tests the full E3 count or
  E1 and E3 together on real messages.
- **Real trials in a shared-seed layout.** Eight runs of 2^40 real trials with
  shared seed words gave 11,382, 11,211, 11,200, 11,098, 11,621, 11,308, 11,148
  and 11,098 early-test passes (11,418 with independent contexts); the ratio of
  their variance to their mean is 2.8 (chi-square 19.4 on 7 degrees of
  freedom), so the pass count of a run varies between runs by more than chance,
  which is not explained. These runs record only the early test and the number
  of trials in which E1 requires the class. The number of trials in which E1
  requires the class shows no such excess. The spread bears on the independence
  that H1 assumes; the proof says what was measured on it. For the constants of
  `04638ed8` the same comparisons showed deviations of up to 3.1 standard
  deviations in settings other than its own class, among them a spread between
  two runs that I have not explained; that bears on the model in general.
- **Rule A and the second test on real trials.** Four runs of 2^38 real trials
  with shared seed words: 17,179,784,810 of 2^40 trials satisfy rule A, a share
  of 2^-6.0000, and no run is further than 1.3e-05 of its value from 2^-6;
  1,390 trials pass the second test. These runs have no model run beside them.
  In the layout of the algorithm itself, on a CPU with contexts sampled and
  every pass over the class complete, 24 samples of 2^30 trials have a share of
  trials between 0.999565 and 1.000452 times 2^-6 and a share of batches that
  run stage 2 between 0.103535 and 0.104059 (budget 0.125); the program is a
  reviewing helper agent's, run again for this note. Over 8,192 sets of seed
  words, 2^15 sampled batches each, the share of batches that run stage 2 is
  0.10383 in all and at most 0.1112 for one set. ApproxMC agrees with the E3
  counts of the 30 heaviest outcomes within 0.10 bit (a check of the E3 count
  for this class, made by the thread that found rule A).
- **Scaled-down end-to-end check, with other constants.** The same attack was
  run in full on toy versions of the hash with 8-bit and 10-bit words (2
  rounds, IV truncated to the top bits, rotations 4, 3, 2, 1 and 5, 4, 3, 2),
  where a complete run is 2^32 or 2^40 trials and real collisions can be
  counted. These runs were made before the constants of this package were found
  and use small constant sets of their own; they are evidence for the method,
  not for these constants. For a constant set the rate of every class is
  computed exactly by brute force, the best class is searched, and the model
  predicts r collisions per run. At 8 bits: 9,835 collisions against 9,837.9
  predicted over six series of runs (largest deviation 1.7 standard
  deviations). At 10 bits: 693 against 664.6 over four series (deviations +1.7,
  -1.7, +0.5 and +0.9 standard deviations). The variance-to-mean ratio of the
  collisions per run, 1 for independent trials, is 0.46 to 1.60 over the eleven
  class series and 0.96 pooled; one series of 40 runs is at 1.60, about 2.65
  standard errors above 1. Every class run of these series had many collisions,
  so they do not test "at least one collision per run"; the runs of the next
  item do. The same check without the class restriction (ten constant sets,
  1,465 runs) gave 1,813 collisions against 1,807.2 predicted; its weakest
  series had a collision in 37 of 40 runs where 39.3 are expected. Every hit
  was confirmed by hashing both messages in full. A toy run of these series
  holds the words X2, X9, X13 and X14 fixed, which is not the split of the
  algorithm (seed words X2, X5, X6, X9).
- **Scaled-down runs in the algorithm's own layout, with other constants.** The
  same attack was run with words of 8 to 10 bits in the layout of the algorithm
  itself: four seed words per run, the contexts in a fixed order, every alpha
  and every member of the best class, with the number of contexts set so that
  the model predicts 0.5 or 1.7 collisions per run. Result: 18,080 runs at an
  expected 0.5 collisions per run: 7,072 with a collision against 7,113.9 +-
  65.7 predicted, 9,010 collisions against 9,040.0, and no two collisions of a
  run in the same context; 4,300 runs at 1.7 per run: 3,518 against 3,514.5;
  one job of the six is 2.0 standard deviations low (544 against 582.3). Two of
  the six jobs were added after earlier ones had been read, which the plan
  records. This is the direct test of "at least one collision per run" that the
  note of `04638ed8` named as missing. It is at small word sizes and with other
  constants, not evidence for these constants.
- **Scaled-down runs with staged tests, with other constants.** Scaled-down
  runs with staged tests of the lossless kind: 13,337 collisions against
  13,505.6 predicted at 8 bits; 84 collisions against 93.3 predicted at 10
  bits. The rule on h1 in these runs is of the kind that every solution
  satisfies, found by brute force; every collision found passed it and the
  second test, and the test word of every trial equalled the word of the
  residual that the proof's Lemma N names. They test the logic of dropping
  trials early and the second test, not rule A of this package, which loses
  solutions.

## Cost

| Part of a batch of seven trials | Operations | Loads |
| --- | ---: | ---: |
| loop over the class | 3 | 1 |
| Y4 backwards through C0 | 9 | 7 |
| round-0 column call K3 with one output kept | 27 | 14 |
| column call C2 as far as one word z | 16 | 8 |
| rule A on z and zero-lane detection | 9 | 6 |
| **stage A, every batch** | 64 | 36 |
| count of the entry against its budget | 3 | 1 |
| rest of C2 | 12 | 4 |
| round-0 diagonal call D1 | 9 | 6 |
| column call C1 as far as Y1 | 17 | 9 |
| E1 for A and B, to c2 | 40 | 15 |
| second test and zero-lane detection | 15 | 7 |
| **stage 2, only after a pass of stage A** | 96 | 42 |

Stage A is 100 primitive operations and stage 2 is 138. E3 is not evaluated in
a batch: rule A is a condition on E3's value h1, but h1 differs from the word z
of C2 only by a rotation and by bits that the class fixes, so it is tested on
z.

**Memory traffic is charged.** The cost model counts memory accesses, so the
proof fixes a 16-register load/store machine and charges one load for every use
of a constant operand (per-context and per-alpha constants, the list entry that
carries the class members, rotation masks, the reduction mask, the constants of
rule A and the budget). The batch values themselves stay in registers (at most
11 are in use, the two counters included), so no stores are needed. One pass
over the class is 9,363 batches, the last one holding 2 trials, and every batch
runs stage A. **How many batches run stage 2 is not proved.** The algorithm
allows one eighth of the batches of a run and halts with failure beyond that;
that this budget suffices is heuristic H3. A uniform word passes rule A with
probability 2^-6, so at most 0.109375 of the batches are expected, and real
trials show a share of 2^-6.0000 of the trials. With that budget and fewer than
256 operations of set-up, a pass over the class costs at most 1,098,067.75
operations for 65,536 trials, 16.756 per trial, charged as 17.4; the expected
cost is 16.448. The other tickets I read count the arithmetic of their inner
loop without such loads; I submit the stricter number.

**The operation count can be rerun from the package.**
`experiments/halfsearch.py`, the program of the two declared experiments,
contains the packed batch and the machine that counts it: every operation on
packed words and every load is a counted call. The command

    python3 experiments/halfsearch.py --selftest N [seed]

runs N batches on contexts, values of alpha and list positions derived from the
seed text. It checks all seven lanes of each batch against the real messages of
the lane's trial: it builds both messages, compresses each with a 2-round
compression written out from the definition, and compares the stage-A flag with
rule A on the h1 of message A, and the stage-2 word with the same word from the
two compressions and from the two complete digests. It prints one JSON line:
cases, lanes checked and lanes right, the lanes that pass rule A and the
batches in which one does, operations and loads per part and per stage, the
largest lane of a sum per part next to the bound the proof gives, the registers
in use, the number of constants, the class members in the list, and the flags
on words with zero lanes and on all patterns of the bits that rule A reads.
With N = 2,000 and seed 1 it reports 14,000 of 14,000 lanes right, 64
operations and 36 loads in stage A and 96 and 42 in stage 2 in every case and
per part as in the proof's table, 215 lanes that pass rule A in 177 batches, a
largest sum of 8.509 * 2^32 (a lane holds 16 * 2^32) and at most 11 of the 16
registers in use. Longer runs of the same self-test, N = 1,200,000 with seed 61
and N = 1,200,000 with seed 62, report 16,800,000 of 16,800,000 lanes right and
the same counts in every batch; 261,798 lanes pass rule A, which is a share of
2^-6.004, in 205,330 of the 2,400,000 batches, a share of 0.0856 (every fourth
batch of the self-test is the last batch of the class, whose seven lanes hold
only two different members, so this share is below that of a run); no stage-2
test word is zero; the largest lane of a sum is 9.496 times 2^32, and at most
11 registers are in use. In the `residual-search` experiment the same program
evaluates one such batch per organizer seed and returns the operations and
loads of both stages, its right lanes and whether a lane passed rule A as
observations. The organizer records observations as untrusted and does not
recompute them, so this is still my count, made reproducible; it is not an
organizer-verified cost.

2^104 trials at 17.4 operations are 17.4 * 2^104 / 430 = 2^99.37282 units.
Passes of the second test are budgeted at 2^88. A passing trial is recomputed
in scalar form, below 2^10 operations, so the budget costs 2^98 operations, a
share below 2^-10.12 of the main loop. Per-context set-up (2^67 operations in
total), the final check and the bound for the constants (2^63 units) are far
below that; all lower-order terms together add less than 0.012 to the exponent.
The total is below 2^99.39, and the bound is worst case for the algorithm as
stated, which halts when either budget is reached. The pass budget corresponds
to a pass rate of 2^-16; the measured pass rate is 2^-29.42, which would give
2^74.58 passes, so the budget is larger by a factor of about 2^13.42. With the
more cautious factor 2^22 in H1, which is 7.1 times below the count, the same
package would search 2^105 trials and claim 100.4.

The seven-lane layout with 36-bit lanes, reduction delayed to the rotations
and a five-operation masked rotation is taken from public ticket 2bf40fb,
whose author is credited as co-author for that reason. What is evaluated in
the lanes, and why no table is needed, is new in these packages.

## What is assumed and what is not shown

- H1: 2^104 trials, each passing rule A and being a collision with probability
  at least 2^-105, behaving like independent events. H2: fewer than 2^88 passes
  of the second test. H3: fewer than 9,363 * 2^85 trials that pass rule A, so
  that at most one eighth of the batches run stage 2. None of the three is
  proved.
- No full collision. The search needs about 2^104 trials.
- The factor 8,388,608 in H1 is assumed against my count of 29,965,882. No
  organizer-run experiment measures it. With factor 1 the claim would be 122.4.
- Rule A is not implied by a collision. That it loses no more than the 12,040
  given up rests on the answers of three SAT solvers for 247 outcomes, without
  a checked certificate. Rule A was chosen from counts of the same kind as the
  count, so it fits the solutions that the count knows, and nothing on real
  messages tests rule A together with a collision.
- The stage-2 budget (H3) rests on four runs of real trials with shared seed
  words, on samples of real trials in the algorithm's own layout and on the
  fact that a uniform word passes rule A with probability 2^-6. If a run
  exceeded it the algorithm would halt with failure; the time bound would hold.
- The count is exact only under the seven-word model. The model is tested end
  to end only on versions with words of 8 to 10 bits, with other constants. At
  32 bits and with these constants it is compared with real messages only for
  events of probability about 2^-32 and above (somewhat deeper for one call at
  a time, E3 only without its third condition); its use at the probability of a
  collision, about 2^-103.16, is an extrapolation.
- The constants and the class were chosen to make the count large. The count is
  deterministic, but the choice exploits the model, and a failure of the model
  for these constants would not show in the count. Among the 34 classes of
  these constants that were counted, the class used is the second largest.
- The count rests on few paths: 47% from one beta, 60% from two.
- The calculator is not in the package. It is mine, as is every check of it,
  those of my reviewing helper agents included. Its E1 count and its
  enumeration of outcomes are new code, checked against brute force only at 8
  bits and against an independent counter for one beta at 32 bits.
- The count covers all 4,272 betas with k at most 14; the rest is left out,
  which can only make the true rate under the model larger.
- All trials of a run share four seed words, trials of one context share most
  of their other words, and the 65,536 trials of one pass over the class differ
  only in Y4 and what follows from it; their independence is assumed. With a
  count that rests on few paths I have not examined whether collisions depend
  on a few shared words. On real messages the number of passes of the early
  test of Lemma E, which this package's algorithm does not use, varies between
  runs by more than chance, which I have not explained. The distribution of
  collisions within one run of the algorithm has been tested directly only for
  words of 8 to 10 bits and with other constants.
- The memory figures of the selection (below 16 GB of main memory, below 10 GB
  on the graphics card) are what I observed, not instrumented peaks.
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

- `python3 scripts/local_tracks.py check blake3-r2-exploratory`:
  `mechanically_valid`.
- Repo tests pass (176 tests).
- Organizer intake run locally with the pinned Docker image: both experiments
  `passed`, 256 of 256 mask events each, stdout byte-identical on replay; the
  toy search tried 334.9 class members on average, more than the 256 that
  independent uniform low bytes would give, and for its counted batch it
  returned 64 operations and 36 loads for stage A, 96 and 42 for stage 2 and 7
  of 7 lanes right on every one of the 256 seeds; a lane passed rule A in 22 of
  these 256 batches (observations of the program, not checked by the runner).
- A second program, written from the text of the proof, checked every lemma of
  the class search on 20,000 random trials with these constants and this class
  against a plain forward compression of its own, which it compared with the
  organizer's reference hash on 2,000 of them.
- The self-test of the submitted program, 2,000 batches with seed 1: all 14,000
  lanes right against the real messages of their trials, 64 operations and 36
  loads in stage A and 96 and 42 in stage 2 in every batch, no lane above its
  36 bits, and every sum below the bound the proof quotes for its part. Longer
  runs of the same self-test: 16,800,000 lanes, all right.
- A second program checked the batch of the submitted program against the
  research program in which the two-stage batch was first written, and its
  reference values against a forward compression of its own.
- Three programs of reviewing helper agents were run again for this version:
  the questions on rule A with a second formula and other solvers (three
  solvers in all, the same answer for each of the 287 outcomes), and two counts
  of rule A and of the batches that run stage 2 on real trials in the
  algorithm's layout (24 samples of 2^30 trials; 8,192 sets of seed words with
  2^15 sampled batches each).
- The contest's judge pipeline was not run locally and no provider key was
  used.

## Package files and next steps

The package is `proof.md`, `claim.json`, `experiments/halfsearch.py` (the
two experiments and the self-test of the operation count),
`experiments/manifest.json` and `certificates/manifest.json` (empty: no
collision is exhibited).

Open, in order of value: an argument in words for what rule A keeps, in place
of the solvers' answers; real trials in the exact layout of the algorithm that
record the second test, and rule A over whole runs and not over samples of the
contexts; the cause of the spread between runs in the layout of the algorithm;
runs in the exact layout, with S5 shared, and with residual statistics kept;
the remaining checks for the class with the largest count; scaled-down runs in
the algorithm's layout with constants chosen by a solver as here; and a test of
the two calls together below 2^-32 on real messages, which I do not know how to
make (the counts of E1 outcomes reach about 2^-38.57 and the count of partial
E3 events 2^-34.54, each for one call alone).

## Tools

Mathematics, code and text: Claude Opus 5.5 in Claude Code. Measurements: one
RTX 3090 and a 24-core desktop. Helper agents of the same model did parts of
the work, and the text says so where it reports them: some drafted parts of the
text; three reviewed the earlier version of this package, before rule A and the
two-stage batch existed, and some of the checks are theirs; one made the
scaled-down runs in the algorithm's layout; one found rule A and the second
test, wrote the two-stage batch, counted it first and made the runs that record
rule A on real trials and the scaled-down runs with staged tests; and one
assembled this version of the package from those results, ran the solver on
every outcome of the count and recounted the parts. Three further helper agents
of the same model then reviewed the version with rule A and the two-stage
batch, one for the mathematics and the cost, one for the figures and one
reading as a hostile judge. They are not independent parties. Their findings
were worked into this text by a helper agent that maintains the package, three
of their programs were taken into its tools and run again, and the text says
where a result comes from them. A further helper agent of the same model then
checked these changes against the files and ran the three programs once more,
with the same output; what was changed after that check has not been reviewed.

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

- Analytical cost claim with a declared score-critical heuristic whose factor
  8,388,608 is assumed and not organizer-measured.
- Two different message lengths; relies on the true block length being a
  compression input, as the profile specifies.
- The charge per trial counts stage 2 for one eighth of the batches. That no
  more run it is heuristic H3, enforced by a budget and not proved.
- The number of trials is 2^104 instead of 2^128 because of the assumed rate;
  the rest of the gain is the cost of a trial. With only the uniform rate
  assumed it is 2^127 and the claim is 122.4.
- A brief literature search found free-start and near-collision results for
  reduced BLAKE variants only. No priority or novelty claim.
