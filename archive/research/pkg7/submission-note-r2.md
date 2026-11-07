# blake3-r2-exploratory: a two-level search inside a sub-class, time_log2 = 95.7

## Credit first

This package continues my entry `c66f230d` (97.6) and uses ideas of others.
Each is named for what they did; apart from my helper agents, nobody named here
has reviewed this package. winglock, Th0rgal, 5kyguy and tekkac are named in
the co-author field of this submission, for the contributions this note credits
to them; no co-author is represented as having reviewed or endorsed the
package.

- **GPT Sol 6.1 (OpenAI)**, an AI model that I ran with briefs asking for exact
  counting: the sub-class of this package with its exact rate, the eight
  conditions of rule A, exact fractions for every rate (my counter reproduces
  them digit for digit), and a referee report on the text of `c66f230d`.
- **winglock**: the idea of searching only a sub-class of the members, chosen
  by an exact count per member, first used in entry `18a7fc52` (108.9) on the
  class of my entry `04638ed8` (112.4); to my knowledge `18a7fc52` is also the
  first public count of the model rate without sampling.
- **Th0rgal**: building the values that depend on the member alone once per
  outer step, first published in `df8bd46d` (111.75) for the family with
  lengths 60 and 62; and three coding steps from `8c81a219` (98.70): one stored
  constant across two calls, the one-bit rotation with one mask, and an order
  of operations that frees registers.
- **5kyguy**: masks kept in registers across the loop over the members,
  `404d14df` (112.12).
- **tekkac**: the seven 36-bit lanes with a masked rotation, ticket `2bf40fb`.
- **Grok 4.7 (xAI)**, an AI model that I ran: a hostile review of the text of
  `c66f230d`, and a tightened batch of its own that agrees in idea with the one
  used here (it is not the batch of this package).
- **A model reached through the service Venice**: a prior-art statement and an
  argument on bit-level fixing; unverified, and nothing of it is used in a
  proof or figure.
- **Helper agents**, instances of the AI model that wrote this text: the order
  of the construction, the program and its tests, the count, the checks, the
  audit of `c66f230d`, this text, its review and its corrections.

## Summary

This is a draft for blake3-r2-prefix-v1, lane exploratory. It keeps the pair of
lengths (55 and 63 bytes), the six constants and the exact half-collision of
`c66f230d`, and changes four things.

1. **Two levels.** The construction is solved in another order (outer step of
   six words, then X2, then the member). What depends only on the outer step
   and the member, ten of the lines of a trial, is computed once per outer step
   into a table of five lists and reused for 2^32 values of X2. A batch then
   computes only D0 and C2 before its first test.
2. **A sub-class.** Y4 runs over 131,072 of the 524,288 members of the class:
   those whose e1 = Y3 + Y4 has bits 21 and 26 zero. Under the model the rate
   of this quarter is 185,377,197.55 times the uniform rate, against
   162,266,763.66 for the whole class.
3. **A rule with eight conditions.** Rule A now has eight parity conditions on
   h1; inside the sub-class it keeps 185,358,111.47 of the 185,377,197.55
   counted. Three of its right sides depend on the member, so the test reads
   one word of a second fixed list. Only one batch in 32 may run stage 2.
4. **Registers.** Nine words (six masks and three constants of the rule test)
   stay in registers during a loop over the members. This is a change of the
   counting convention against `c66f230d`, and it is stated as such.

**Exact part (no heuristic).** For every choice of eight 32-bit words the
construction gives a 55-byte message and a 63-byte message whose complete
2-round digests agree on digest words 0, 2, 5 and 7. One of the eight words is
Y4.

**Heuristic part.** 2^101.442 trials with Y4 in the sub-class, seven per
256-bit word, in two stages. A trial is charged 7.7 operations (budgeted
7.3182): stage A 37 operations and 10 loads, stage 2 105 and 30, the middle
step 134 per value of X2, the table 74 per list word and the outer step 260. H1
assumes that a trial collides and passes rule A with probability at least
49,400,000 * 2^-128, and that such trials do not cluster; the count it is set
against is 185,355,453, 3.75 times larger. The total is below 2^95.65 and the
claim is 95.7. With the uniform rate the same search would claim 121.3.

**No full 2-round collision is exhibited**, and the search is far beyond
feasible computation.

## The same figures under stricter readings

| reading | stage A, stage 2 | charged | claim |
| --- | --- | ---: | ---: |
| this package: nine words kept in registers | 47, 135 | 7.7 | 95.7 |
| every read of a memory word a load (as in `c66f230d`) | 57, 143 | 9.2 | 96.0 |
| one more operation for every list or table load | 50, 139 | 8.1 | 95.8 |
| rule with six conditions, nine words kept | 41, 135 | 8.6 | 95.9 |

The second row is the program's own count with its line `KEPT = 0`; the third
is arithmetic on the first.

## Corrections to my entry c66f230d

That entry cannot be edited. Its text was examined by a hostile review (Grok
4.7), a referee report (GPT Sol 6.1) and an audit by a helper agent that had
written none of it. Section 11 of proof.md lists 24 points with the wrong and
the right sentence; none changes a lemma, the count or the 97.6, and only one
(the second below) changes what a declared figure is said to cover. The ones
that matter most:

- "H1 is M together with r_A >= 33,554,432" is wrong: the model gives a rate
  for one trial; H1 also assumes that successes do not cluster.
- "preprocessing_log2 = 63 ... also covers their selection and the selection of
  eta and of rule A" is wrong: the bound is for recomputing two message words
  at four given inputs; the selection has only an estimate from running times.
- The bound "one batch per trial that satisfies the rule" holds in every
  context; what single contexts exceed is the budget in its form on trials.
- Four cells under the heading "exact part" held the disclosed estimates: the
  exact total of the class is 85074516985129/524288 = 162,266,763.6588, not
  162,266,763.6579.
- Last digits: 2^15.4 not 2^15.3; 1.39 not 1.38; 0.1501 not 0.1500; 0.9994 not
  0.9993; 0.92 not 0.94; 144,123,440.89 not 144,123,441; "18.253 per trial"
  should read "less than 18.253".
- The note rejected the rule with six conditions on its count of 91,072,901
  alone; the exact count of that rule, 123,244,449, should have stood beside
  it.
- The note's sentence that other tickets count their inner loop without loads
  had no support and is withdrawn.
- Three reported points were examined and are not errors (proof.md Section 11,
  items 22 to 24).

## How the rate is counted

Under the seven-word model the rate is a number of solutions of a fixed system,
counted for each value beta of one difference by enumerating the outcomes of
one call and counting the other call exactly. For this package the counter
works in integers and splits every count by rule A. For the sub-class:
194382080300609/1048576 = 185,377,197.55 from 53 values of beta and 317
outcomes; with rule A 6219586146887739/33554432 = 185,358,111.47; without the
218 outcomes in which some solution violates the rule, 185,355,453.45, which is
the figure H1 is set against. GPT Sol 6.1 found the sub-class and the rule; its
fractions and mine are equal (21 fractions, every beta, 3,243 integers on 1,081
outcomes, three per outcome); the figure H1 is set against is mine alone. My
recount was not blind. Checks of my counter: complete enumeration with 8-bit
words with sub-classes and three-bit parities, 6,805,032 integers, none
different.

## What is assumed and what is not shown

- H1, H2 and H3 are assumptions. Both parts of H1, the factor 49,400,000 and
  the absence of clustering of the good trials, are assumed; no experiment
  measures the factor, and the count it is set against is not a measurement of
  the trials.
- The model does not hold inside one context for rule A, and in this
  arrangement not inside one outer step for the call E1; only averages over
  outer steps have its values (layout runs on a graphics card, for the whole
  class and the rules of `c66f230d`).
- For the sub-class with the new rule the processor samples are of at most 2^30
  real trials (a graphics-card run of 2^44.59 trials came later, below); in my
  three runs the rule passes with probability 2^-8.00 and 0.02617, 0.02622 and
  0.02622 of the batches run stage 2, against a budget of 0.03125; samples of
  the review in the ranges of the algorithm give 0.02617 to 0.02620. Single
  contexts reach 0.0421 and exceed the budget; H3 is a statement about the
  average of a run.
- A graphics-card run now has the sub-class and the new rule (2^44.59 real
  trials; rule A passes at 2^-8.000002 and a marker at 2^-32.2 is about 1.18
  times richer in the sub-class; its deeper marker at 2^-40.15 has 14 counts
  against 21.59 expected, which settles nothing at that precision, and the same
  sub-class on random outer words in a later run has 275 against 288.1), and a
  scaled-down end-to-end run with real collisions has both the sub-class and an
  eight-condition rule (121 collisions against 120.23 predicted); neither
  reaches rule A together with a collision, nor measures the kept mass.
- Scaled-down end-to-end runs now exist for this pair of lengths: in the
  two-level order 470 collisions against 467.6 predicted in 436 runs (the first
  92 runs were low, 56 against 74.8; the later ones were made because of that);
  in the order of `c66f230d` 345 against 335.76 in a plan fixed beforehand. The
  larger two-level job (8,448 runs, expectations written down before it ran) is
  8,108 against 8,313.6, -2.25 standard deviations: 3.3 percent low with 8-bit
  words (-2.65), level with 10-bit words (+0.19). The cause is not known; a
  shortfall of that size is far inside the margin of 3.75.
- Real messages in the order of `c66f230d`, whole class: 24 runs of 2^45 trials
  on another machine, 692 listed E1 outcomes against 690.78; nothing of this
  kind exists for the sub-class.
- The loops, their ranges and the processing of a passing trial are defined in
  the text only. The program counts the pieces.
- The sub-class and the rule were chosen by the count, and no measurement on
  real messages shows the gain of the sub-class.
- Three helper agents reviewed the assembled text once; the corrections and the
  evidence added after their review were not read again by them. No person has
  read it.

## Checks performed

- `python3 experiments/halfsearch.py --selftest 2000 1`: exit status 0; 14,000
  of 14,000 lanes right against the complete digests of their two real
  messages; the counts of the tables in every case; rule A right on 65,536 of
  65,536 packed words of patterns.
- The long self-test, 1,000,000 cases with seed 61: 7,000,000 of 7,000,000
  lanes right.
- The displays of Section 4 exactly as printed, run by a tool on 20,000 tuples
  of eight words: each of the 96 names equals its value in a forward
  compression of the real message, and Table C holds cell by cell.
- A second counting machine that shares no code with the program counts the
  same operations, loads and stores for all four pieces and refuses the batch
  with 15 registers.
- The decisions of the program equal those of its first form, which tests the
  rule as written on h1, on 200,000 batches.
- The count: my counter against the fractions of GPT Sol 6.1, 0 differences;
  complete enumeration with 8-bit words, 6,805,032 integers, none different.
- `python3 scripts/local_tracks.py check blake3-r2-exploratory` in a local
  mirror of the repository: `mechanically_valid`. The repository's test script:
  three runs with 23, 84 and 176 tests, all pass.
- Organizer intake run locally with the pinned image, with the mirror copy
  marked ready: both experiments `passed`, 256 of 256 mask events each, output
  identical on replay; the toy search tried 382.1 members on average; its
  counted batch reported 37 operations and 10 loads in stage A, 105 and 30 in
  stage 2 and 7 right lanes on every seed, and entered stage 2 on 9 of 256
  seeds.

## Package files

- `blake3-r2/proof.md`: Sections 1 to 9 the construction, the search and the
  cost; Section 10 the evidence; Section 11 the corrections to `c66f230d`;
  Section 12 what is the same and what is new; Section 13 credit.
- `blake3-r2/claim.json`, `blake3-r2/experiments/manifest.json`,
  `blake3-r2/experiments/halfsearch.py` (SHA-256
  cde9b8279eaad69a148d570714fbbcceea8bd81faab8ef10773faa9fa38f5563),
  `blake3-r2/certificates/manifest.json` (empty).

## Limitations

The claim 95.7 is a cost bound under three declared heuristics and one counting
convention, not a measured running time and not a collision. Everything about
the rate rests on a model that is known to fail inside one outer step and is
tested on real messages only for events of probability 2^-40 and above, and on
counts that only the participant and another AI model have made.
