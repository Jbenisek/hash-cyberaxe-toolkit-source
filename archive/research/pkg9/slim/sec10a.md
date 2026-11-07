## 10. Evidence, scope and field meanings

Throughout this text costs and bounds are rounded up, and margins, rooms and the
whole numbers of the count that the claim uses are rounded down. Counts printed
with decimals are rounded to the nearest.

**What is exact.** Sections 2 to 5 and Lemmas L, H, Q, Q2, T, T2, T3, T4, N and
A. Lemma A says what stage A tests, not that a collision passes it. The declared
experiment `half-collision` runs one trial of 6.1 per organizer seed, with the
seven words of a context and a member number taken from the seed, and the
organizer recomputes both digests; Lemma T predicts that every trial agrees on
the 128 masked digest bits.

*What is new in the exact part and who has checked it.* Sections 1 to 3, Lemmas
L, H, Q, T and N and Fact P are those of entry c66f230d; new are the order of
Section 4 with Lemma T2, the loops with Lemma T3, the table with Lemma T4, the
sub-class with Lemma Q2 and Lemma A in the form of 6.3. All of it was written by
helper agents of the participant, instances of the same AI model as the author
of this text, and three further helper agents reviewed the assembled text (the
review is described under the limits below). Three independent reruns, by a
checking agent, a reviewing agent and a participant tool that reads the printed
text, found no wrong value in the displays, Table C and Lemmas Q, Q2, L, A, T2
and T4; only changes of wording were asked for, and they are made here. Lemma A
was checked by complete enumeration in three ways: the submitted program on all
2^16 patterns of the 13 bits of z and the 3 bits of e1 that the rule reads
(65,536 packed words); a second statement of rule and test typed by hand on
4,194,304 inputs; and seven wrong plans of the test, all of which the program
refuses. The statements (a) to (d) of 6.3 were compared with the rule and the
list V of the program on 262,144 cases: no difference. These are checks, not
proofs, and no person has read any part of this text.

**The seven-word model.** By 6.2 the residual of a trial is a function of the
constants and of seven 32-bit words: for E1 its first-half values d1 and b1 and
its a output a2 on message A, and for E3 the words Y4, Y9, w8 and its first-half
value h1 on A. In the algorithm Y4 takes every member of the sub-class equally
often; the model M says that over the trials the other six behave like
independent uniform words, independent of Y4. Under M a trial has R = 0 with
probability r * 2^-128, where r * 2^81 is the number of solutions of R = 0 among
the 2^209 values of the seven words with Y4 in the sub-class. Call r the *rate
of the sub-class*. Rule A is a condition on h1, so under M the trials with R = 0
that satisfy rule A have a rate of the same kind, r_A, counting only the
solutions that satisfy rule A; r_A is at most r. M and r_A >= 49,400,000
together give the rate that H1 assumes for a single trial. They do not give H1:
H1 also assumes that the good trials of a run do not come in clusters, and a
model of the single trial says nothing about that.

Given M, the rate is a property of the constants and the sub-class alone and can
be counted without sampling; the count says nothing about whether M holds. The
six words are not free in a trial: within one context each is a function of Y4,
and Y12 and w5 are the same in all 2,222,477 * 2^32 trials of a run with one
value of w5 and one member, which lie in 2,222,477 outer steps (6.4). M is a
statement about averages over the outer steps of a run, and the measurements
below show where it fails inside one context and inside one outer step.

**How r is counted (participant computation, not organizer-verified).** Write
tau, eps, beta for the XOR differences between A and B of E1's a output, c
output and first-half b, and eta, psi, tau', eps' for those of E3's first-half d
and b and its c and a outputs. Because E1's a1 and d1 are the same for A and B,
R = 0 holds exactly when tau' = tau, eps' = eps, psi = tau XOR ROR(tau, 1) and
eta = eps XOR ROL(beta XOR eps, 1); for Y4 in the class the left side of the
last equation is the constant 830303cf. The counter works in integers (128-bit
unsigned integers; exact fractions for the products and sums), has no sampling
branch, and needed no fallback on any outcome of the count below; no
floating-point number is on the path of a figure printed below as a fraction.

1. *The betas.* beta is a function of d1 alone: with c1 = Y11 + d1 and DY11 =
   Y11' - Y11 = 0a08818b, beta = ROR(c1 XOR (c1 + DY11), 12). As in Lemma Q, the
   d1 with a given beta are a share 2^-k of all d1, k being the number of bits
   of the mask ROL(beta,12) AND 7fffffff.
2. *The outcomes of one beta.* An outcome is a pair (tau, eps); the admissible
   tau are enumerated with a carry automaton, with no bound on the weight of
   tau. A beta for which beta XOR ROR(eta, 1) has odd weight contributes
   nothing; every other has two candidates for eps.
3. *The E3 side.* N3 is the number of quadruples (Y4, h1, Y9, w8) for which E3
   produces eta, psi, eps and tau; all of them have Y4 in the class.
4. *The E1 side.* P1 is the probability that E1 produces tau and eps when d1 is
   uniform among the values with this beta and b1 and a2 are uniform.
5. *The sum.* For the sub-class, N3 counts only the quadruples with Y4 in the
   sub-class, and the part of a beta in r is 2^(15 - k) times the sum over its
   outcomes of P1 * N3, where 15 is the number of bits that Lemma Q2 fixes, so
   that the sub-class is a share 2^-15 of all Y4: the sum of N3 over all 2^96
   values of (d1, b1, a2) is r * 2^81, and 2^96 / 2^81 = 2^15. r is the sum of
   the parts over all betas. Parts are not negative, so the sum over any set of
   betas is a lower bound for r. For r_A, N3 counts only the quadruples whose h1
   satisfies rule A.

**The count for this package (participant computation).** The count runs over
the 60 words beta that have a part in the rate of the whole class, the list of
entry c66f230d: of the 133,742 words that occur as beta, the 4,550 with k at
most 14 were enumerated, and for the 129,192 others a SAT solver was asked
whether the whole system has a solution with that beta and answered no for
129,147, without certificates. The integer enumeration of GPT Sol 6.1 over every
beta finds the same 60. A beta without a part in the class has none in the
sub-class; the other betas were not searched again here.

For the whole class the rate is 85074516985129/524288 = 162,266,763.66, from 60
betas and 453 outcomes with a nonzero product. For the sub-class it is

    r = 194382080300609/1048576 = 185,377,197.55,

from 53 betas and 317 outcomes, about 2^27.47, so that under M a trial has R = 0
with probability about 2^-100.53. The rate of the sub-class is 1.142 times the
rate of the class: under M the members do not have the same rate, and the
quarter of the class in which bits 21 and 26 of e1 are zero has more than its
share.

| beta | Outcomes | Part of r | With rule A | Kept for H1 |
| --- | ---: | ---: | ---: | ---: |
| 18b0e098 | 7 | 67,698,688 | 67,698,688 | 67,698,688 |
| 18b1a098 | 16 | 51,384,320 | 51,384,320 | 51,384,320 |
| 18d0e098 | 12 | 50,790,400 | 50,790,400 | 50,790,400 |
| 18d1a098 | 12 | 13,246,464 | 13,246,464 | 13,246,464 |
| 18b3e098 | 4 | 1,474,560 | 1,474,560 | 1,474,560 |
| 18d3e098 | 6 | 755,712 | 755,712 | 755,712 |
| 18d16398 | 6 | 13,328 | 456 | 0 |
| 18f1e098 | 8 | 3,465 | 1,665 | 0 |
| 45 others | 246 | 10,260.5523 | 5,846.4676 | 5,309.4537 |
| sum | 317 | 185,377,197.5523 | 185,358,111.4676 | 185,355,453.4537 |

"With rule A" is the part of the beta in r_A. "Kept for H1" adds only the
outcomes in which every solution satisfies rule A. The heaviest beta carries
36.5% of the count and the four heaviest 98.8%. The count rests on few paths.

*Rule A in the count.* Of the 317 outcomes, 99 have only solutions that satisfy
rule A, 76 have none that does, and 142 have both. The exact rate with rule A is

    r_A = 6219586146887739/33554432 = 185,358,111.47,

so the rule loses 19,086.08 of r, about one part in 10,000, and the sum over the
99 outcomes is 12147454997539/65536 = 185,355,453.45. H1 is set against this
smaller figure, as entry c66f230d set it against the outcomes without a
violating solution; the two differ by 2,658.01 and no figure of the claim
changes with the choice. On the whole class the same eight conditions keep
76,072,772.68, less than half, and no outcome there is free of violating
solutions: the rule belongs to this sub-class.

*The rules that were prepared.* The submitted program holds three rules, each
containing the one before it: the first four conditions; those and the two on
bits 2, 10 and 3, 11; and all eight. For each, the same counter gives the rate
inside the sub-class and the program's machine the cost.

| Rule | r_A, exact | Kept for H1 | Stage A, 2 | Entry | Charged | Scalar |
| ---: | ---: | ---: | --- | --- | ---: | ---: |
| 4 | 185,358,154.95 | 185,355,465.45 | 37, 128 | 1/2 | 15.1 | 96.7 |
| 6 | 185,358,125.47 | 185,355,465.45 | 41, 135 | 1/8 | 8.6 | 95.9 |
| 8 | 185,358,111.47 | 185,355,453.45 | 47, 135 | 1/32 | 7.7 | 95.7 |

Inside the sub-class the four further conditions cost 43.48 of the count and
divide the share of the batches that run stage 2 by sixteen. "Rule" is the
number of conditions, "Entry" the share of the batches that may run stage 2,
"Scalar" what the package would submit with that rule and the factor 49,400,000.
The rules with four and six conditions are not claimed; their figures are given
so that the choice can be seen.

**Where the sub-class and the rule come from, and the second count.** Both were
proposed by another AI model, GPT Sol 6.1 (OpenAI), run by the participant with
briefs that asked for exact counting. With a counter of its own it computed the
rate of sub-cubes of the class and searched for affine conditions on h1 that
keep the count; its answers give this sub-class, r = 194382080300609/1048576,
and the eight conditions, r_A = 6219586146887739/33554432. It calls its sets
"best found": its search over conditions is not exhaustive. A second instance of
the same model, given the decimal figures, reports the same two fractions and
calls the sub-class the only best of the sub-cubes with 15 fixed bits of e1, and
the eight conditions, in another basis of the same affine set, a certified best
among all sets of eight affine conditions on h1. The participant has not checked
these two statements, and nothing the participant has checked shows that no
better sub-class or rule exists. The participant's counter, extended by the
sub-class, agrees with the other model's files on 21 exact fractions (totals and
rule masses for this sub-class, for a second sub-class of 32,768 members and for
the whole class), on the rate of every beta and on 3,243 integers over 1,081
outcomes, with no difference; this was a recount with those figures at hand, not
a blind one. The other model does not give, and the participant alone has, the
figure "kept for H1", the split by beta, and the rules with four and six
conditions inside the sub-class.

**Checks of the counter (participant computations).** (1) Complete enumeration
with 8-bit words of every quadruple (Y4, h1, Y9, w8) through both executions of
E3 and every triple of the E1 side, over random constants, classes, sub-classes
with up to three more fixed bits of e1 and rules with parities of three bits:
five runs, 1,472,040 and 5,332,992 integers, none different from the counter.
(2) At 32 bits two functions compute the E3 side with its split by the rule and
agree on all 687 outcomes both counted; the other 285 (16 with a nonzero
product) were counted by one alone. The E1 count agrees with the earlier
calculator on 972 of 972 outcomes. (3) The untouched calculator of entry
c66f230d, with an option of its own for a sub-class, finished 54 of the 60 betas
in the time allowed, each equal to the part printed above at its one printed
decimal; the six unfinished carry together 0.3346 of the 185,377,197.55 of r, a
share of 1.8 * 10^-9. (4) For the whole class, a helper agent that audited entry
c66f230d counted both factors of all 453 outcomes with two programs written from
the definitions of 6.2 and 6.3 alone: the same total, 85074516985129/524288, and
the same parts for 60 of 60 betas. The checks that entry c66f230d reports for
the whole class (an approximate model counter on the sixteen largest outcomes,
brute force with 8-bit words, a sampler for the four heaviest betas) were not
repeated for the sub-class.

**How the constants and the class were found.** As in entry c66f230d: the six
constants come from a SAT solver search for a pinned call with the property of
Fact P and a zero residual, with the two words w4 related as the length
cancellation prescribes and a zero top byte of word 13; the class is the class
of the solver's solution, and the constants were chosen among the solver's sets
by the count. The constants and the class were chosen to make the count large,
and the sub-class and the rule by the count as well.
