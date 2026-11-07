## 10. Evidence, scope and field meanings

**What is exact.** Sections 2 to 5 and Lemmas Q, F, Y, K, T, E, N and A.
Lemma A says what stage A tests, not that a collision passes it. The
declared experiment `half-collision` runs one trial of 6.1 per organizer
seed, with nine state words, alpha and a member number taken from the seed,
and the organizer recomputes both digests; Lemma T predicts that every trial
agrees on the 128 masked digest bits.

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
says nothing about whether M holds.

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

**The count for this package.** The betas were listed by increasing k.
{{beta_cover_sentence}} For {{betas_no_eps}} betas of the list beta XOR ROR(eta, 1)
has odd weight, so that no eps exists. The other {{betas_evaluated}} were enumerated
completely{{enumerated_caveat}}, and {{betas_with_mass}} of them have a nonzero part; these parts add up to
{{exact_listed}}. {{extra_betas_sentence}} What is left out,
{{betas_left_out}}, makes the figure a lower bound for r.
It is about 2^{{exact_log2}}, so that under M a trial has R = 0 with probability about
2^-{{hit_exp}}, or more, since the figure is a lower bound.

{{exact_table}}

In the table, k is the number of bits that beta fixes in c1, "outcomes" is
{{outcomes_meaning}}, and "exact part" is the
class-rate part of the beta. The heaviest beta, {{heaviest_beta}}, carries {{heaviest_share}}% of the
count, and the two heaviest together {{top2_share}}%.

{{recount_sentence}}

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

Which outcomes these are was decided with a SAT solver. For each of the
{{rule_outcomes}} outcomes with a nonzero product P1 * N3, over all betas of the list,
the E3 system of step 3 was written as a CNF formula from its definition:
the unknowns Y4, h1, Y9 and w8, E3 for both messages, and the four XOR
differences that the outcome prescribes. The solver kissat was asked two
questions. First, whether the formula has a solution. It has one for all
{{rule_outcomes}} outcomes, and every model, evaluated again in plain arithmetic, is a
solution of its outcome with Y4 in the class; {{rule_models_passing}} of these models satisfy
rule A. Second, whether the formula has a solution together with the
clause that h1 violates rule A. For {{rule_ok}} outcomes the answer is that it has
none: if these answers are right, every solution of these outcomes
satisfies rule A, and stage A drops none of them. {{rule_heaviest_sentence}} For
the other {{rule_bad}} outcomes, in {{rule_bad_betas}} betas, the solver
returned a solution that violates rule A, and each was evaluated again in
plain arithmetic. These {{rule_bad}} outcomes carry {{rule_lost}} of the count,
{{rule_lost_pct}}% of it:

{{rule_table}}

The {{rule_bad}} outcomes one by one, so that the questions can be put again;
"Adds" is what the outcome adds to the count, as in the table of the
heaviest beta:

{{rule_dropped_table}}

{{rule_exact_decimals}} {{rule_worst}} Without these outcomes the count is

    {{exact_total}} - {{rule_lost}} = {{rule_count}}.

This is the figure that H1 is set against. Under M it is a lower bound for
the rate of the trials with R = 0 that satisfy rule A, provided that the
{{rule_ok}} answers "no solution" are right. {{rule_sat2_sentence}} The figure is
{{rule_kept}} of the count of all solutions.

{{calc2_sentence}} {{calc2_total_sentence}}

{{rule_split_sentence}} {{rule_fit_sentence}} {{rule_sat_other}} {{rule_amc_sentence}}

{{rule_example_paragraph}}

*The sampler as a check.* The last three columns of the first table come
from the sampler of submission {{last_submission}}, which is used here as a check and
not for the figure. For one beta it draws d1 among the values with that
beta and b1, a2 uniformly, keeps the draws that require the class, and
counts E3 for each kept draw with the count of step 3. {{sampled_betas_cap}} betas of the
table were given {{sampler_setup}} each. The runs of every beta, and of
every class, use the same seeds, {{sampler_seeds}}, so the figures of different
betas are not independent of each other. "Sampler" is the mean of the
class-rate parts of the runs, "error" is the standard deviation of the
runs divided by the square root of their number, and "deviation" is the
difference from the exact part in units of that error. {{sampler_sum_sentence}}
{{review_seed_sentence}} {{sampler_far_sentence}} {{review_sampler_sentence}}
{{extra_sampler_sentence}} {{sampler_note}}

*The other classes, and why this one is used.* {{class_search_sentence}}In
all, {{classes_counted}} classes of these constants have a count over one common list,
the {{class_common}} lightest betas:

{{class_table}}

{{class_table_rest}} {{class_list_caveat}}

{{class_choice_paragraph}} {{class_other_samplers}}

**Checks of the calculator (participant computations).** The E3 count of
step 3 is the program of submission {{last_submission}}; the checks reported there
were made with other constants: a SAT solver and the approximate model
counter ApproxMC on 30 outcomes, brute force with 8-bit words on 400
constant sets, and further checks against ApproxMC on 440 outcomes with
ratios of sums between 0.969 and 1.050. The enumeration of outcomes of step 2 and the E1
count of step 4 are new code, written in the night before this text. Five
checks were made of the calculator as it is used here.

{{other_checks_paragraph}}

{{e1bf_paragraph}}

{{e1amc_paragraph}}

{{e3check_paragraph}}

Fifth, the enumeration of step 2 was run without any limit on the weight of
tau for every beta of the table: the program's limit was set to 31, the
largest possible weight below bit 31. {{fifth_detail}}

What these checks cover: the E1 count against brute force only for 8-bit
words and against an independent counter {{e1amc_cover}}; the E3
count against an independent counter {{e3check_cover}}; and the
whole calculation against the sampler for the betas of the table that were
sampled, which carry {{sampled_share}}% of the count, to within the sampler's errors. The
sampler shares the E3 count with the calculator, so that comparison tests
the enumeration of outcomes and the E1 count, not the E3 count. All of
these are participant computations.

{{review_checks_paragraph}}

{{review2_paragraph}}

{{solution_paragraph}}

**How the constants and the class were found.** The constants come from a
solver search, not from farming random sets. One CNF instance holds, with
real word values: the call C3 for both messages with equal b and d outputs,
so that every model is a set of constants with the property of Fact P; E1
and E3 for both messages; a zero residual; and a bound on the number of bit
positions, bit 31 excepted, at which a difference is active in six
additions of E1 and E3. The solver is kissat. When its log was read for
this text it held {{search_pins}} sets of
constants found in this way, in runs of up to {{search_longest_min}} minutes each, several
at a time on a desktop machine; the search for further sets was still
running. The constants of 3.2 came from an instance
with bound {{search_bound}}, after {{search_seconds}} seconds, with {{search_cost}} active positions; the
solver's solution has eta = {{search_eta}} and beta = {{search_beta}}.
{{cand_sentence}} {{search_class_sentence}} The bound
steers the search towards solutions that are reached with high probability
under M; the count, not the bound, is what H1 is set against.
{{solver_beta_sentence}}

**Checks of the trial on real messages (participant computation).**
{{host_check_sentence}} A second program, written independently from the
text of this proof, checked each of Lemmas Q, F, Y, K, T, N and A on 20,000
random trials with these constants and this class against a plain forward
compression, and evaluated the two solutions that this section prints.

**Checks of the model on real messages (participant measurement).** Real
trials of 6.1 were compared with the same number of draws from M (Y4 a
uniform member of the class, the other six words uniform and independent),
on the same statistics: how often each of the four residual words, or its
low 16 bits, is zero, how many trials have a residual of weight at most 32
or at most 40, how often the early test of Lemma E passes, and in how many
trials E1 requires the class. The last of these is the event
eps XOR ROL(beta XOR eps, 1) = eta, so a trial in which E1 requires the
class is a trial that passes the E1 test of Lemma N. The algorithm of this
package uses the E1 test and not the early test; both are reported because
the programs print both.

In these comparisons the real trials are not laid out as in 6.4. Every
thread of the generating program draws its own context, nine random state
words from a random stream of its own, independent of the other threads,
and makes 4,096 trials in it, each with a random alpha and a random member
of the class. No two contexts share seed words, and X12 and X13 are not
restricted. These comparisons therefore measure rates averaged over
independent contexts. They do not test a run of 6.4, in which all contexts
share the four seed words.

{{real_model_paragraph}}

{{deep_paragraph}}

{{e1deep_paragraph}}

{{e3deep_paragraph}}

{{layout_paragraph}}

{{dispersion_paragraph}}

**Rule A and the E1 test on real trials (participant measurement).** The
runs above did not record rule A. The thread that found the rule ran real
trials of 6.1 for these constants and this class with a program of the same
kind that also counts rule A, in the layout of the runs above: every run
has its own four seed words, shared by all its contexts, X12 is below 2^{{x12_bits}},
and the two differences from 6.4 named above apply. {{a_runs_cap}} runs of 2^{{a_run_trials}}
trials counted {{a_counts}} trials that satisfy rule A, where a share of
2^-{{rule_pass_exp}} is {{a_expected}}: they are {{a_devs}} standard deviations of a binomial
count away from it, and no run differs from it by more than {{a_rel}} of its
value. Together {{a_count}} of 2^{{a_trials}} trials satisfy rule A, a share of
2^{{a_rate}} ({{a_dev_sum}} standard deviations from 2^-{{rule_pass_exp}}). A batch runs stage 2
only if one of its seven trials satisfies rule A, so at most seven times
this share of the batches do, {{a_share}}, against the budget of {{stage2_share}} in
step 4. In the same runs {{a_e1_passes}} trials passed the E1 test, a share of
2^{{a_e1_rate}}, and {{a_early_passes}} the early test of Lemma E. These runs have no
model run beside them; they give pass rates and nothing about M. The self-test
of the program reports the same share of lanes on its own, much smaller,
sample (6.5).

{{lay_paragraph}}

{{seeds_paragraph}}

The same comparisons were made earlier for the constants of submission
{{last_submission}} and are reported there. For its class the largest deviation with
independent contexts was 1.5 standard deviations. Two other classes of
those constants and the search that does not restrict Y4 showed 2.6, 2.7
and, in two runs of the unrestricted search with opposite signs, 3.1: a
spread between runs that is larger than a Poisson count allows and that was
not explained. Those figures belong to other constants. They are repeated
here because they bear on M and on these programs in general.

{{real_depth_sentence}}

**Scaled-down end-to-end check of the class search (participant
computation, other constants).** With short words the whole search can be
run and its collisions counted. These runs were made before the constants
of this package were found. They use constant sets of their own with 8-bit
and 10-bit words, none of which is derived from the constants of 3.2, and
the rate they are compared with is computed by brute force, the role that
the calculator has at 32 bits. They are evidence for the method, that is
for M and for the independence of the trials at the depth of actual
collisions when words are short. They are not evidence about the constants
or the class of this package.

The toy hash is BLAKE3 with 2 rounds and W-bit words, for W = 8 and W = 10.
Its IV words are the top W bits of the real IV words. The permutation, the
flags 11 and the block lengths 60 and 62 are the same. G uses the rotations
(4, 3, 2, 1) for W = 8 and (5, 4, 3, 2) for W = 10. Everything used from
Sections 3 to 6 is independent of the word size and is applied unchanged:
the length cancellation of 3.1, a pinned call as in 3.2, Lemma H, the
construction of Section 4, and the trial of 6.1 with Lemmas F, Y, K and T. A
constant set is six W-bit constants with the property of Fact P. As in 6.1,
eta is the XOR difference of E3's first-half d value, a function of Y4
alone, and a class is the set of all Y4 with one eta.

For a constant set the number of solutions of the seven-word system is
computed by brute force for every value of Y4 separately, over all values of
the other six words. The class rate r of a class is the mean of that number
over its members, divided by 2^(2W); it is exact. The class with the largest
r is used; it has n members, a power of two.

One run is 2^(4W) trials of 6.1 for one choice of (X2, X9, X13, X14): every
value of X5, X6 and X10, and either (a) every value of X12, with member
number (X10 + X12) mod n, or (b) every X12 that is a multiple of n, each
with all n members of the class. Layout (b) is the one of 6.4 in that the
whole class is tried with everything else held fixed. In both layouts a run
differs from a run of 6.4 in the words it holds fixed: here X2, X9, X13 and
X14, there the seed words X2, X5, X6 and X9. The residual of every
trial is computed in full; rule A, the tests of 6.3 and the packing of 6.5
are not used. The E1 test and the packing change the cost of a trial and
not its outcome. Rule A drops trials, and these runs do not test it. M predicts
r collisions per run. Every collision found is checked again by building
both messages and evaluating the toy hash on each in full. The number of
runs of every series was fixed before the series started.

Results for W = 8:

| Constants | Class (members) | Layout | Runs | Predicted | Observed |
| --- | --- | --- | ---: | ---: | ---: |
| 30 19 41 90 28 9b | f7 (2) | (a) | 20 | 296.6 | 305 |
| 55 c9 21 52 63 5b | 35 (16) | (a) | 20 | 208.8 | 205 |
| 73 6a 84 e7 e3 44 | 97 (8) | (a) | 40 | 2,895.0 | 2,898 |
| 73 6a 84 e7 e3 44 | 97 (8) | (b) | 40 | 2,895.0 | 2,938 |
| 55 c9 21 52 63 5b | 35 (16) | (b) | 40 | 417.5 | 383 |
| 49 58 24 e9 20 b7 | 97 (8) | (b) | 40 | 3,125.0 | 3,106 |

"Predicted" is r times the number of runs; one run is 2^32 trials. In total
9,835 collisions were observed and 9,837.9 predicted. The largest deviation
is 1.7 standard deviations of a Poisson count (383 against 417.5). No trial
produced a Y4 outside its class, and no collision failed the full re-hash.
A further 20 runs with Y4 held at the single best member of the first set
gave 308 collisions against 296.6 predicted.

Results for W = 10:

| Constants | Class (members) | Layout | Runs | Predicted | Observed |
| --- | --- | --- | ---: | ---: | ---: |
| 3ad 17c 2d3 ab 1d7 48 | 36a (16) | (a) | 12 | 170.2 | 192 |
| af 23e 186 d3 12 70 | 1be (16) | (a) | 12 | 61.7 | 48 |
| 39b aa da 25e 279 163 | 3f2 (16) | (b) | 10 | 290.9 | 300 |
| 3ad 17c 2d3 ab 1d7 48 | 36a (16) | (b) | 10 | 141.8 | 153 |

One run is 2^40 trials. In total 693 collisions were observed and 664.6
predicted. The deviations are +1.7, -1.7, +0.5 and +0.9 standard deviations
of a Poisson count; their squares sum to 7.0 over the four rows. No trial
produced a Y4 outside its class, and no collision failed the full re-hash.

The dispersion of the collisions per run was computed for every series as
the ratio of their variance to their mean, which is 1 for independent
trials. Over the eleven series, the ten of the two tables and the 20 runs
with Y4 held at one member, it lies between 0.46 and 1.60, and pooled over
their 253 degrees of freedom it is 0.96. One series stands out: constants
49 58 24 e9 20 b7 in layout (b), 40 runs, has 1.60, about 2.65 standard
errors above 1 (for 40 runs the standard error of the ratio is 0.23). In
every one of these series every run had a collision, as it must with
between 4 and 78 collisions per run on average. So these series do not
test whether a run has at least one collision. {{toyalg_forward_sentence}}

The same check was made for the search that does not restrict Y4, whose
trials are outputs of step S1 enumerated by four one-word parameters, 2^(4W)
per run. There M predicts c collisions per run, where c is the exact number
of solutions of the seven-word system divided by 2^(3W). Ten constant sets
with c from 0.03 to 4.05, seven at 8 bits and three at 10 bits, and 1,465
runs gave 1,813 collisions against 1,807.2 predicted. No set differs from
its prediction by more than 1.7 standard deviations of a Poisson count. A
collision occurred in 658 runs, against 660.2 expected for independent
trials. The weakest series of that check is one of two on the 8-bit set
with c = 4.051: 40 runs of a CPU program gave 161 collisions against 162.0
predicted, but a collision in only 37 runs where 39.3 are expected; 200
runs of the GPU version on the same constants gave 826 against 810.2 and a
collision in 196 runs against 196.5. A further 10-bit job on three more
constant sets was stopped before any set had finished and contributes
nothing.

These checks test M and the independence of the trials down to actual
collisions for words of 8 and 10 bits, for runs laid out as described here
and for the constant sets named in the tables. They do not prove either for
32-bit words or for the constants of this package.

{{toyalg_intro}}

{{toyalg_table}}

{{toyalg_results}}

{{toyalg_scope}}

{{toystage_paragraph}}

The declared experiment `residual-search` runs the search of Section 6 at toy
scale: one context and one alpha per seed, then the members of the class in
order from a number taken from the seed, stopping at the first trial whose
residual has a zero low byte in digest word 1. The search runs without rule
A, without the E1 test and without the packing of 6.5. The organizer checks
that every returned pair agrees on 136 digest bits. It checks the trial
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
- Rule A is not implied by a collision; it loses solutions. That it loses
  no more than the count allows rests on the answers of SAT solvers, for {{rule_ok}}
  of the {{rule_outcomes}} outcomes of the count, that no solution violates rule A.
  These are {{rule_unsat_basis}}; the solvers were run and the formulas
  written by the participant and the participant's helper agents. The
  {{rule_bad}} outcomes with a violating solution are left out in full. Rule A was
  read off counts of the same kind as the count itself, for this class: it
  was chosen to fit the solutions that the count knows. {{rule_fit_limit}} No
  measurement on real messages reaches the event of H1, so none tests rule A
  together with R = 0, and the scaled-down runs with staged tests use rules
  of another kind.
- The count is exact only under M. It counts the solutions of the
  seven-word system; that the trials of the algorithm meet those solutions
  at the rate M predicts is the assumption. M has been tested end to end,
  down to actual collisions, only for words of {{toy_bits_all}} and with other
  constants. For 32-bit words and {{real_scope}} it has been compared with
  real messages only for events of probability about 2^-32 and
  above{{real_largest_clause}}{{e1deep_limit_clause}}. Its use at the
  probability of the event R = 0, about 2^-{{hit_exp}}, is an extrapolation that no
  feasible experiment can test directly.
- The constants and the class were chosen to make the count large: by a
  solver search that minimises the number of active bit positions of one
  solution, and then by the count itself. {{class_rank_sentence}}
  The count is deterministic, so no
  sampling noise enters it and no choice among noisy estimates was made.
  But a choice that is best under M says nothing about M. If M overstates
  the rate for some constants, a search for the largest count under M will
  tend to find those constants, and nothing here measures that.
- The count rests on few paths: {{heaviest_share}}% of it comes from one beta and {{top2_share}}%
  from two, {{top2_outcomes_clause}}. An error in the
  count of these outcomes would change the figure in proportion. The
  sampler confirms the betas it was run on to within its errors, and it
  shares the E3 count with the calculator.
- The calculator is not part of the package, and it and every check of it
  are the participant's, the checks of the reviewing helper agents
  included. Its E1 count
  and its enumeration of outcomes are new code, written in the night before
  this text, checked against brute force only for 8-bit words and against
  an independent counter {{e1amc_cover}}. Its E3 count is the program of
  submission {{last_submission}}, whose checks were made with other constants, apart
  from the fourth check above.
- The count covers {{betas_list}}{{outside_clause}}.
  Everything else is left out. That can
  only make the true class rate under M larger than the figure.
- All trials of a run share the four seed words: X2, X6, X9 and S5 are the
  same in every trial of a run, w5 and the column-state words S2, S6, S10
  and S14 take at most 256 values in a run because they depend on X6 and
  X12 only, trials of one context share most of their other words, and the
  {{members}} trials of one context and one alpha differ only in Y4 and what
  follows from it. Independence of the trials is assumed, not shown. With a
  count that rests on few paths, whether a run contains a collision may
  depend on a few shared words more than it would for a rate spread over
  many paths; this was not examined. The 32-bit comparison gave every
  context its own random words and so measures rates averaged over
  independent contexts. {{layout_limit_sentence}}
  {{run_distribution_sentence}}
- The comparisons of M with real messages that were made for the constants
  of submission {{last_submission}} showed deviations of up to 3.1 standard deviations
  in settings other than its own class, among them a spread between two
  runs that was not explained. For the constants of this package fewer
  runs exist, and what they show is stated above.
- Single-word statistics are not evidence for the joint rate. An earlier
  version of this construction, cancelled by the submitter before screening,
  used other constants and inferred a rate of half the uniform one from the
  frequencies of single zero residual words; a count of the kind described
  above gave 0.024 for those constants. For some constant sets one residual
  word vanishes 40 times more often than a uniform word while the count is
  zero.
- H2 rests on the pass rate of the E1 test measured on {{pass_measured_on}}
  with these constants: {{pass_count}} passes in 2^{{pass_trials}} trials with
  independent contexts. That the number of passes of a full run of 2^{{T}}
  trials stays near the mean is assumed. {{h2_limit_sentence}}
- H3 rests on the share of trials that satisfy rule A in {{a_runs}} runs of
  2^{{a_run_trials}} real trials with shared seed words, each within {{a_rel}} of
  2^-{{rule_pass_exp}} relatively{{h3_layout_limit}}; and on the fact that a uniform word
  satisfies the rule with that probability. The budget is {{a_margin}} times seven
  times the share measured in those {{a_runs}} runs. That no run of 2^{{T}} trials
  has a share that far above the mean is assumed. {{h3_seeds_limit}}{{h3_spread_layout}}
  If either budget of step 4 is exceeded the algorithm halts with
  failure: that lowers the success probability, by the 0.0005 allowed for
  each of H2 and H3, and does not raise the time bound.
- The charge of {{charge}} operations per trial is the budgeted cost of a
  two-stage batch. With one stage, as in the submissions named below, a
  trial costs {{previous_charge}} charged operations and the total would be larger by a
  factor of about 2^{{charge_gain}}.
  The stage counts are those of the machine in the submitted program; no
  organizer run verifies them.
- The two memory figures of the preprocessing in Section 9 are observations
  of the runs and were not measured by a tool.

**Scope and limitations.**

- No full collision of the 2-round hash is exhibited. The search is an
  analytical cost claim like other packages on this track; unlike a birthday
  search it tests each trial against zero and so needs no memory that grows
  with the number of trials.
- The two messages have different lengths, 60 and 62 bytes, and the
  construction relies on the true block length being a compression input, as
  the target profile specifies.
- The gain over a generic birthday search has three sources: half of the
  digest is matched by construction, which removes the table and about half
  of the round-1 work per trial; the constants are chosen so that the
  remaining half can match at all with a useful rate; and the search stays
  inside one class of Y4, where that rate is assumed to be {{factor}} times
  the uniform one. The exponent of the number of trials is {{T}} instead of
  128, and 127 if only the uniform rate is assumed.
- The construction and the trial are those of the
  submissions {{submissions_plain}} on this track, which
  claim {{submission_scores}}. What is new here is the set of constants, the
  class, the count that replaces the sampled estimate of the rate, and the
  batch: it has two stages, with rule A in front and the E1 test of Lemma N
  in place of the early test of Lemma E, where those submissions have a
  batch of one stage. {{step_sentence}}
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
  three constants of rule A, {{advice_bytes}} bytes, by {{advice_limit}} bytes.
- success_probability = 0.39 holds under H1, H2 and H3 as shown in
  Section 7.

The required baseline_improved identifier blake3-r2-nominal-v2 names the
organizer's nominal display reference 128, which is not an established attack,
a qualified baseline or a security bound. The claimed scalar {{time_log2}} is lower
than that display value. Whether a qualified result improves the Yukon
incumbent is decided separately, and no Pareto dominance claim follows from
the scalar.
