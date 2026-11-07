# Hostile review of research\pkg8\pkg (draft claim time_log2 93.5)

Reviewer: hostile referee, 2026-10-07. Subject read in full: `blake3-r2/proof.md`
(2,917 lines), `blake3-r2/claim.json`, `submission-note-r2.md`.
Nothing was staged, submitted or written inside `pkg`. No network. `.key` not read.
No tool call was refused or stopped.

Every statement below is marked COUNTED (exhaustive or exact arithmetic),
MEASURED (with the counts), DERIVED (algebra from printed figures) or ESTIMATE.

## What I verified for myself first

I wrote my own 2-round BLAKE3-256 from Section 1 and my own copy of the
construction, Lemma A, Lemma N and the cluster procedure, and ran them
(`verify.py`, `verify2.py`, `yieldmeas.py`, `yield2.py`, `arith.py`,
`corrected.py` in this folder). The exact part stands:

- COUNTED: the round-1 schedule of Section 1 is the standard permutation applied
  to the identity; the eight calls read the message words the text prints.
- COUNTED: Fact P, including both rows of the intermediate table of 3.2,
  `W4' = 97475640`, `delta = fffffff8`, and `Y3, Y3', Y11, Y11'`.
- COUNTED: Lemma Q by exhaustion over all 524,288 members of the class (every
  one gives `eta = 830303cf`), and on 200,000 random words the mask test agrees
  with the eta test. Lemma Q2: mask `07ef8303` has 15 bits, 131,072 members, the
  17 free positions are exactly those printed.
- COUNTED: rule A is 32 of 8,192 patterns of the 13 bits it reads (2^-8); the
  gate is 2^-4; rule A implies the gate, exhaustively.
- MEASURED: Lemma A (a),(b),(c),(d) on 400,000 random (member, 36-bit z) pairs,
  guard bits filled: 0 mismatches against rule A written on the real
  `h1 = ROR(ROR(z,8) XOR e1,16)`, and `u + (2^32 - ALL)` is at most 2^32 with
  bit 32 set exactly on a pass.
- MEASURED: the theorem of Section 5, Lemma T and Lemma N on 300 trials with
  random context words and random members, built by my own implementation of
  steps O, M, Y, T, S2, S3 and hashed in full: 300 of 300 pairs of a 55-byte and
  a 63-byte message agree on digest words 0, 2, 5 and 7; `X` equal in both;
  `Y4 = y`; `Y3/Y11` as in Fact P; `ROL(h1,24) = z XOR ROL(e1,8)`;
  `n = D3 XOR ROL(D6,8)` in 300 of 300.
- MEASURED: the package's own `experiments/halfsearch.py --selftest 200 1`
  exits 0, 1,400 of 1,400 lanes right, stage A 37+10 = 47, stage 2 105+30 = 135,
  16 registers, and it contains no neighbour path (as disclosed).
- MEASURED (the new sections): on 400 outer tuples and 6,553,600 representatives
  of my own implementation, Section 10's cluster figures reproduce: yield
  **40.202 +- 0.465** (text 40.02); gate open 0.0626978 (text 0.0624630);
  representative words with an open lane 0.241610 (text 0.241596); opened
  clusters with no rule-A neighbour 0.1432 (text 0.1436); rule-A neighbours per
  opened cluster 2.5047 (text 2.5008); the 63 retention rates 0.5401 to 0.8689
  (text 0.543 to 0.874); representative words with a rule-A lane 0.026355 (text
  0.026178); neighbour words per representative 0.56428 (text 0.5625).

So the measurements the new sections rest on are sound. What is not sound is the
bookkeeping that turns them into the scalar.

---

## ERRORS

### E1. The success probability 0.39 is false as printed. The clusters lose 36 per cent of the good trials and nothing in the text pays for it. (score-critical)

Quoted, Section 7: *"Write N = 1,424,469 * 2^81 = 2^101.442 for the number of
trials of a run."* and *"Over the coins, the N trials behave with respect to the
event 'good' like independent events of probability at least 49,400,000 * 2^-128
... Under H1, H2 and H3 the algorithm outputs a collision with probability at
least ... 0.3904 >= 0.39"*.

A good trial is found only if it is **examined**. The algorithm examines a
representative always and a neighbour only when the representative's gate opens.
A trial that satisfies rule A passes the gate, but its representative need not:
the gate is carried to a neighbour only with probability 0.54 to 0.87 per
position. The share of the rule-A trials of a run that the procedure finds is
exactly the text's own 41.02 divided by the cluster size 64.

- DERIVED from the text's own figures: 41.02 / 64 = 0.640938.
- MEASURED by me (6,553,600 representatives): rule-A trials found divided by
  rule-A trials present = **0.643886** (41.202 / 64).

Therefore the expected number of good trials **found** in a run of N trials is
0.5 x 0.6409 = 0.3205, not 0.5, and

    success >= 1 - exp(-0.3205) - 0.003 = 0.2712   (0.2722 on my measured yield)

against the claimed 0.39 and the claim block's `success_probability: 0.39`.
The sentence *"If H5 fails, the number of trial-equivalents of a run falls short
of N and the success probability falls with it"* presupposes that the run carries
N trial-equivalents when H4 and H5 hold. It carries 0.641 N even then; N
trial-equivalents would need a yield of 63, not 40.02.

Two consequences inside Section 7 that are also wrong as printed:

- *"reaches 0.39 only when f is at least 49,323,560: the assumed 49,400,000
  leaves no slack on the probability side."* DERIVED: with the clusters the
  requirement is f >= **76,955,335**, which the assumed factor does **not** meet.
- *"Under M the count of Section 10 gives 185,355,453 * N / 2^128 = 1.87 expected
  good trials in a run ... the bound survives a clustering of the successes by
  that factor [3.74]."* DERIVED: 1.20 expected good trials found, and m up to
  **2.40**.

**Corrected statement.** Either (a) `success_probability` is 0.27, not 0.39; or
(b) the run must enumerate 64/41.02 = 1.5602 times as many trials: C0.d1 over
**2,222,477** values and not 1,424,469, N = 2^102.0837 and not 2^101.442. Under
(b) the scalar 93.5 survives, because 1.71 is a charge per *trial-equivalent* and
the number of trial-equivalents is unchanged (DERIVED:
1.71 * 2^101.442 / 430 * (1 + 2^-7) = 2^93.4791). Under (b) the trial count in
Section 6.4 ("How many trials"), Lemma T3, Section 7, Section 12's table
("trials 2^101.442") and claim.json's restriction ("a search over 2^101.442 such
pairs") are all wrong by the same factor, and the room under the stage-2 budget E
falls from 2.04 to 1.31 (DERIVED, see E13).

This is the fault the task warns about, in its worst form: the new mechanism was
priced in Section 8 and Section 12 but was never carried into Section 7.

### E2. Section 8, the charge ledger, is the pre-cluster ledger with a post-cluster total pasted into it. Its own rows contradict its own total on the same page.

Quoted, Section 8: *"Let W = 18,725 be the number of list words ... One value of
X2 has W batches for 131,072 trials ... P = W * 47 + W * 135 / 32 + 134 + 1 + ...
operations, and a trial costs P / 131072."*

- COUNTED: P = 959,206.0941 and P / 131,072 = **7.31816**.
- COUNTED: the per-trial column of the table sums to 7.31816 (6.714439 +
  0.602692 + 0.001022 + 2.46e-09 + 4.6e-13 + 7.63e-06).
- The total row prints **1.6389**. The ratio is 4.4653. The 1.6389 is
  67.225 / 41.02 (DERIVED), a figure that appears only in **Section 12** and
  nowhere in Section 8.

Quoted, same page: *"On every run the main loop therefore costs at most
1,424,469 * 2^64 * P operations with P = 959,206.0941, which is less than 1.639
per trial"* — false, it is 7.318 per trial — and three lines later *"The expected
cost is lower: ... a trial would cost 7.2367 operations on average"*. A page that
bounds a cost by 1.639 and then gives a lower expected cost of 7.2367 cannot be
recomputed by anyone. A referee who recomputes Section 8 from the printed figures
gets 7.32 per trial and a scalar of 95.7, which is exactly the no-cluster row of
the note's own table.

Also in Section 8 and stale for the cluster algorithm:

- *"47 the count of stage A"*: under the clusters stage A also tests the gate,
  which Section 10 prices at 9 (6 operations and 3 loads) per word. 47 is the
  count of the batch without the gate.
- *"1/32 the share of the batches that step 4 allows to run stage 2"*: DERIVED
  from the package's own rates, the cluster algorithm enters stage 2 on 0.1987 of
  its stage-A words (0.2002 on my measurement), six times 1/32.
- *"The first five terms are machine counts of the program."* True, and
  irrelevant: the program contains no neighbour path, so none of the five terms
  is a machine count of the procedure that is claimed.

**Corrected statement.** Section 8 must print the cluster ledger: the cost per
representative (67.225 budgeted; 56.0007 on the audit's measured rates; 52.350 on
mine), the rates it budgets at 1.2 times the mean, the gate and dispatch items,
and the division by 41.02 trial-equivalents.

### E3. Section 6.4 step 2(c) gives the wrong number of representatives: 2,048 instead of 16,384.

Quoted: *"then run the batches of 6.5 for the 2,048 REPRESENTATIVES of the
sub-class in the order of their numbers, seven in one packed word"*.

COUNTED: a representative has bits 14, 30 and 31 of e1 zero, so 131,072 / 8 =
**16,384** members of the sub-class are representative members, one per group of
eight. 2,048 is 131,072 / 64, which wrongly divides the member count by the whole
cluster size, although 56 of the 64 trials of a cluster differ in X2 and not in
the member. Section 10 says the right figure twice: *"all the representatives of
one value of X2 (16,384 of them, one per group of eight members)"*. The packed
words per value of X2 are 2,341 (16,384 / 7 rounded up), not 293.

### E4. Section 6.4 loops over all 2^32 values of X2 while 6.7 defines a representative by three bits of X2. As written the algorithm contradicts Lemma C.

Quoted, 6.4: *"for each of the 2^32 values of X2, in increasing order: run step M
... then run the batches ... for the 2,048 REPRESENTATIVES"*. Quoted, 6.7: *"A
representative is a trial whose bits 14, 30 and 31 of e1 and whose bits 14, 30
and 31 of X2 are zero."* Quoted, Lemma C: *"The algorithm enumerates the
representatives once ... so no trial is run through stage A twice."*

Only 2^29 of the 2^32 values of X2 hold any representative. Read literally, the
loop runs representatives at values of X2 where there are none, or runs each
cluster eight times; either way Lemma C's last clause is false of the algorithm
as printed. The outer loop also has to visit the seven sibling values of X2 for
the neighbour path, which the loop form of 6.4 ("next X2", one middle step per
value of X2) does not describe. GPT Sol 6.1 is credited in Section 13 with *"the
condition on the enumeration that makes it an execution property"* — that
condition is not in Lemma C.

**Corrected statement.** The middle loop runs over the 2^29 values of X2 whose
bits 14, 30 and 31 are zero, with 16,384 representatives (2,341 packed words)
each, and the neighbour path supplies the middle words of the seven sibling
values of X2 (Section 10's "cache of the mixed middle words, 258 per value of
X2"); the trials of a run are then 1,424,469 * 2^29 * 2^32 * 16,384 * 64, which
is the same count as before.

### E5. The data layout of 6.5 cannot serve the algorithm of 6.4. The lists and the table are indexed by seven *consecutive* members; the representatives are not consecutive.

Quoted, 6.4 step 2(b): *"build the table of 6.5: for each of the 18,725 words of
the list U, in order, run the lines of step Y for its seven members in one packed
word"*. Quoted, 6.5: *"For list word j, U[j] holds ROL(y, 7) and V[j] holds the
word v of Lemma A (c), one member y per lane; lane i belongs to member number
7j + i."* Quoted, Lemma T4: stated for "every list word j" of that layout.

COUNTED: the representative members are the 16,384 member numbers whose bits 10,
15 and 16 are zero. Seven of them are never seven consecutive members, so no
word of U, of V or of the table of 6.5 holds the seven lanes of a representative
word, and Lemma T4 — the lemma that licenses reusing a table across 2^32 values
of X2 — is proved about words the cluster algorithm never reads. Section 10
mentions a different layout in one clause (*"The table of the new layout holds
133,413 rows per outer step"*) and the package specifies it nowhere.

### E6. H4 and the definition of the yield are wrong by a factor of 16: "per representative whose gate opens" must read "per representative".

Quoted, H4: *"the number of trials found to satisfy rule A per representative
whose gate opens, divided by the probability that a trial satisfies rule A, is at
least 40.02"*. Quoted, Section 10: *"The yield is the number of neighbours found
to satisfy rule A per representative whose gate opens, divided by the probability
2^-8 that a trial satisfies rule A."*

MEASURED by me: per representative **whose gate opens** the number of rule-A
neighbours is 2.5047, which divided by 2^-8 is **641.2**; per representative it
is 0.157039, which divided by 2^-8 is **40.202**. Section 10's own bullet gives
itself away: *"40.018 ... on 16,777,218 representatives whose gate opens"* can
only be 40.018 if the divisor is all representatives.

The same fault in 6.7 — *"Section 10 reports 40.02 such trials found per
representative"* — and in the note's item 5 — *"a representative whose gate opens
yields 40.02 further trials that satisfy rule A"*. 40.02 is not a number of
trials: a cluster has 63 neighbours and an opened one yields 2.50 rule-A
neighbours. 40.02 is a number of trial-equivalents, i.e. a mass ratio.

### E7. The abstract describes the previous entry. It omits the clusters entirely, miscounts the heuristics and misstates the charge.

Quoted: *"The search is arranged in two levels ... Every batch runs stage A ...
Only a batch in which a trial satisfies rule A runs stage 2. A batch in which no
trial satisfies rule A is dropped ... A trial is charged 1.71 primitive
operations ... **Three heuristics are declared**: H1 ... H2 ... H3 ... Under the
three the search succeeds with probability at least 0.39."*

Five are declared; two of them (H4, H5) are marked score-critical; the gate, the
representatives, the neighbours and the word "cluster" do not occur in the
abstract at all, although they are worth 2.2 of the 4.1 bits of improvement over
c66f230d; and 1.71 is charged per trial-equivalent, not per trial. Section 7 line
1392 repeats it: *"None of the three heuristics is proved."*

### E8. claim.json declares three heuristics. H4 and H5, both score-critical, are not in the claim block at all, and the restrictions describe the algorithm without clusters.

- The `heuristics` array holds only `H1-residual-hit-rate`,
  `H2-e1-test-passes`, `H3-stage-2-entries`. Nothing in claim.json names a
  representative, a cluster, a gate, a yield or a trial-equivalent.
- Restriction 5: *"The success probability 0.39 holds only under heuristics H1,
  H2 and H3."* False: it needs H4 and H5 as well (and it is 0.27, see E1).
- Restriction 4: *"Every batch runs stage A, 37 operations plus 10 loads; only a
  batch in which a trial passes rule A runs stage 2, 105 plus 30. With stage 2
  counted for one batch in 32 and with the middle step, the table build and the
  outer step, a trial is charged 1.71 operations."* DERIVED: that chain gives
  7.32 and a scalar of 95.7. As written the claim block asserts that the
  no-cluster schedule costs 1.71.
- Restriction 4: *"With a load for every use, the convention of entry c66f230d,
  the same program counts 57 and 143 and the claim would be 96.0."* 96.0 is the
  no-cluster figure (the note's table labels it so); with the clusters it is 93.8.
- Restriction 4: *"The algorithm halts with failure when one batch in 32 has run
  stage 2"*: DERIVED, E is 0.26 of the batches of the cluster algorithm (see E13).
- Restriction 3 describes the search as *"batches of seven pairs"* examined
  *"only if one of its pairs passes a filter"* — the pre-cluster procedure.
- Restriction 6 ("Six 32-bit constants ... 48 bytes of advice ... the sub-class
  and rule A were proposed by another AI model") does not mention the six flip
  positions or the gate, which are also stored constants chosen by
  preprocessing.

A referee who reads only claim.json cannot learn that the entry has a cluster
procedure, which is where all of its new risk and most of its new gain sit.

### E9. Section 8 and Section 10 contradict each other on what the measurements were for, and the preprocessing estimate does not cover the selection of the flips and the gate.

Quoted, Section 8: *"The measurements on real and on scaled-down messages of
Section 10 test the heuristics and select nothing; they are not part of this
figure"*. Quoted, Section 10: *"**Where the six flips and the gate come from.**
Both were chosen by these measurements and not by a count."*

Flat contradiction. Section 8's estimate (2) names only *"the solver search that
produced all six constants and the counts by which the constants, eta, the
sub-class and rule A were selected"*. It does not cover the screen of 231,525
flip sets applied to every representative of a sample, the beam extended to five
and six flips, Grok 4.7's repeat of the same screen with a beam to eight, or GPT
Sol 6.1's exact ranking of all 200,787 rank-four gates on three partial
averages. Section 9 repeats the same incomplete list. ESTIMATE: the flip screen
alone is of the order of 2^31 sets-times-representatives and several
graphics-card hours, so 2^60 is probably still an honest ceiling — but the text
must say what the figure covers, and it says the opposite.

### E10. Section 7's claim that H4 and H5 do not enter the union bound is self-contradictory and false.

Quoted: *"H1 is read here over the trials this algorithm EXAMINES, which H5
asserts carry at least the average mass of the trials rule A keeps; H4 and H5 do
not enter that union bound, because they are about the charge and about the
trials examined, not about a budget being reached."*

The first clause makes the event "no trial is good" depend on which trials are
examined and on the mass they carry — that is H5 — and on how many rule-A trials
the neighbour path finds — that is H4. Both therefore enter the bound. Note also
that reading H1 over the examined trials, as the sentence says, makes the
expectation 2^97.81 * 2^-102.442 = 0.04 (DERIVED), not 0.5: the bound only works
in trial-equivalents, which is the arithmetic of E1.

### E11. Section 10 states the stage-2 rate of the neighbour path as a share when it is a count per representative, understating it by 1.78 times.

Quoted: *"Per representative, 0.5625 neighbour words go through stage A, nine
words whenever the gate opens, and 0.1364 of them enter stage 2."*

As printed, 0.1364 *of* 0.5625 is 0.0767 neighbour words into stage 2 per
representative. MEASURED by me: 0.56428 neighbour words per representative, of
which **0.24425** enter stage 2, that is **0.1379 per representative** — and the
text's own fourth agent prints *"0.1367 neighbour words into stage 2"* as a count,
and Grok's 56.0007 units per representative is only reproducible with 0.1364 as a
count (DERIVED: (1/7 + 0.5625) * 47 + (0.026178/7 + 0.1364) * 135 = 52.07). The
audits used the right number; the sentence of Section 10 does not say it, and a
reader who recomputes the charge from it gets 44.0 units per representative.

### E12. The memory statement of the abstract and Section 9 is contradicted by Section 10 and by the note.

Quoted, abstract and Section 9: *"The search needs less than 2^23 bytes of
memory"*, with the inventory *"the table of one outer step (5 * 18,725 words),
the lists U and V (2 * 18,725) ... fewer than 131,587 words, that is 4,210,784
bytes"*. Quoted, Section 10 and the note: the cluster layout *"holds 133,413 rows
per outer step against the 18,725 words of the five lists of 6.4, **about eight
times the memory**"*.

COUNTED: 4,210,784 + 2^19 = 4,735,072 < 2^23 = 8,388,608, a margin of 1.77.
Eight times the data is 33,686,272 bytes, which is 2^25 and breaks the 2^23
statement. On the kinder reading (133,413 rows of one 256-bit word each) the
total is 5,991,904 bytes and the bound survives. Section 10's own comparison is
also wrong: the five lists are 93,625 words, not 18,725, so "about eight times"
is off by about 5.6 on its own figures. The declared `memory_log2_bytes: 35` is
unaffected, so no claim field changes, but three places in the package give three
different memories for the same layout.

### E13. The stage-2 budget E and H3 were never recomputed for the clusters, and the sentence "one part in 32 of the batches" is now false.

Quoted, 6.4: *"A run has 1,424,469 * 2^64 pairs of an outer step and a value of
X2, which is at least J, and 18,725 batches for each pair. So E is less than one
part in 32 of the batches of a run."* Quoted, H3: *"where E is the budget of step
4, just under one in 32 of the batches"*.

DERIVED with E = 18,725 * J / 32 and J = 2^110 / 49,400,000, i.e. E = 2^93.6347:
under the cluster algorithm a run has 2^95.58 stage-A words (at the corrected
trial count of E1), so E is **0.26** of the batches of a run, one part in four.
The room between E and the expected entries is a factor of 1.307 on the
package's rates and 1.293 on mine, against 1.194 ("19 percent") in the
no-cluster setting — comparable by luck, not by design, and nowhere computed.
H3's `limitations` field still argues the budget from 0.02617 against 0.03125,
which are the shares of the representative words only; the neighbour words,
which are 80 per cent of the stage-A words, enter stage 2 at 0.244.

### E14. Section 10's rule table and Section 6.5's alternative conventions print the previous entry's scalars for this entry's own rule.

Quoted, Section 10: a table whose row *"8 | 185,358,111.47 | 185,355,453.45 |
47, 135 | 1/32 | 7.7 | **95.7**"* with the caption *"'Scalar' is what the package
would submit with that rule and the factor 49,400,000"*. The package submits 93.5
with that rule. Quoted, 6.5: *"the same program counts 57 and 143 for the two
stages ... and the claim would be 96.0"*, and *"the stages would be 50 and 139
and the claim 95.8"*. All three are no-cluster figures. The note's table labels
its rows *"no clusters"*; the proof does not, and the proof is what is filed.
Likewise 6.4's *"18,725 batches for each pair"*, 6.4's *"2^32 * 18,725 batches"*
per outer step and 6.5's *"all 18,725 batches of that value"* are the pre-cluster
batch population.

---

## DOUBTS

### D1. The yield is a mean over random outer words; a run is a walk. I could not bound it for a run and neither can the package.
Quoted, Section 10: *"The claim uses the average over the outer steps of a run;
no lower bound for the outer steps of a run exists, and the ranges of the outer
words of a run are not defined."* MEASURED by me over 400 (outer tuple, value of
X2) samples: the per-sample yield runs from **16.70 to 83.44** with a spread of
23 per cent, wider than the 13 to 14 per cent the text quotes per outer tuple
(the text's samples average two or more values of X2, so the figures are not the
same quantity). A run shares four seed words across all of its outer steps, and
its C0.d1 range is short. The claim is proportional to 1/(1 + yield), so this is
a live score risk that no measurement in or out of the package addresses.

### D2. H5 first part: I cannot verify it, and the strongest evidence for it is a 683,179-node decision diagram supplied by another model and read by one helper agent.
The measurements stop at proxies of probability 2^-32 and 2^-40 while the event
is at 2^-100.53. The package's own source says what must not be done with them
(*"the two measured ratios must not be multiplied without a proof that they
estimate different factors"*, *"a high retention of the rule does not imply that
the factor is one"*), and the text then prints *"The product of the two sides,
1.0012 plus or minus 0.0030, treats them as independent factors and is an
estimate"* — correctly flagged, but it is the only figure that covers both sides.

### D3. H5 second part is unmeasurable and its failure costs most of what the clusters gain.
Quoted, Section 10: *"if an opened cluster fired as one trial, with the 2.56
examined trials that an opened cluster has on average, the claimed exponent would
rise by 1.32, and by 1.81 for 3.5 trials, which is most of the 2.2 that the
clusters gain."* The 64 trials of a cluster share all six outer words and differ
in three bits of X2 and three bits of e1 — far closer than any two trials whose
independence H1 assumed in the previous entries. This is disclosed well in
Section 10 and in the note, and not at all in claim.json (E8).

### D4. No single machine count of the cluster batch exists.
Quoted, Section 10: *"What is NOT counted is one schedule that threads
representative word, gate, dispatch, neighbour words and both stages through a
single account of the 16 registers: every piece above is counted on its own
machine, and the register peak and the routing of the whole remain open."* The
67.225 units per representative, and so the 1.71, are assembled from pieces
counted on different machines, one of which (*"the 12 units were counted on an
earlier machine with a different second stage and were not replayed on this
one"*) is not even from this program. The non-cluster batch is counted twice over
and the cluster batch not once. Disclosed in Section 10 and the note; not in
Section 8 and not in claim.json.

### D5. Lemma C is true as arithmetic and is proved about an enumeration the text does not define.
COUNTED: bits 14, 30 and 31 of e1 are free in the sub-class (mask `07ef8303`
fixes 15 bits, none of them these three); the members split into 16,384 groups of
eight and the values of X2 into 2^29 groups of eight; a cluster is 64 trials and
the clusters partition the 2^49 trials of an outer step. The partition is right.
The clause *"and the algorithm runs stage A on it at most once"* is about the
algorithm of 6.4, which as printed is not that enumeration (E3, E4).

### D6. Section 9's advice inventory is incomplete.
Quoted: *"48 bytes in all ... There is no other stored data and no stored
collision."* The six flipped bit positions and the gate mask are stored constants
of the procedure and are not among the 48 bytes. COUNTED: 48 + 6 + 4 = 58 bytes
is still below 2^6 = 64, so `nonuniform_advice_log2_bytes: 6` survives; the
sentence does not.

### D7. Lemma T3 counts the trials of the printed ranges only.
It proves 1,424,469 * 2^81 distinct trials. Under the correction of E1 (b) the
run needs 2,222,477 * 2^81, and the same proof covers it; but the lemma, Section
7's N and Section 12's table all have to change together, and one of them being
left behind is how this fault arose in the first place.

### D8. The concessions are plain in Section 10 and in the note, and not plain where they are load-bearing.
Section 10 and the note say, well and without hedging: the yield is a measured
mean; the mass per examined trial is assumed; clumping of collisions inside a
cluster cannot be measured; no end-to-end run has a carried gate; the neighbour
path is not in the submitted program; the charge budgets at 1.2 times measured
means that are not bounds. Every one of those sentences is absent from the
abstract (E7), from Section 8 (E2) and from claim.json (E8), which are the three
places a referee reads first.

---

## STYLE

- There is no Section 6.6: the headings run 6.5, then 6.7.
- 6.4 step 2(c): *"If none of its trials satisfies rule A and none passes the
  gate, the batch ends"*. COUNTED: rule A implies the gate, so the first clause
  is redundant; the condition is "none passes the gate".
- Lemma C: *"Fix a context's six outer words"*. By 6.1 a context includes X2;
  these are an outer step's six words.
- H4: *"a yield lower by one part in ten raises the claimed time by about 0.15"*.
  DERIVED: log2(41.02/37.018) = 0.148. Correct.
- The note: *"a yield of 1 would put it back at 95.7"*. Only if the clusters are
  abandoned; with the clusters and a yield of 1 the charge per trial-equivalent
  is 33.6 and the claim is about 97.9.
- Section 8's final chain is right: COUNTED, 1.71 * 2^101.442 / 430 = 2^93.4678,
  times (1 + 2^-7) is 2^93.4791, plus 2^64 is still below 2^93.48, and the
  separate figures 2^-100.53, 3.7521, 0.027025, 7.2367, 119.038 and 49,323,560
  all reproduce exactly. The arithmetic of the claim is sound given 1.71 and N;
  it is the two inputs that are mis-stated (E1, E2).

---

## What would make this filable

1. Fix E1: choose reading (a) or (b) of the success argument and carry it through
   Section 6.4, Lemma T3, Section 7, Section 12 and claim.json. Under (b) the
   scalar stays 93.5 and the range of C0.d1 becomes at least 2,222,477.
2. Rewrite Section 8 as the cluster ledger (E2), with the gate and dispatch items
   and the division by 41.02 printed where the charge is made.
3. Fix the algorithm: 16,384 representatives, 2^29 values of X2, the sibling
   middle words, and a stated layout for the representative words and the table
   (E3, E4, E5).
4. Delete "whose gate opens" from H4 and from Section 10's definition of the
   yield, and stop calling 40.02 a number of trials (E6).
5. Rewrite the abstract and claim.json so that the clusters, H4 and H5 and the
   trial-equivalent charge appear in them (E7, E8).
6. Repair the preprocessing sentence (E9), the union-bound sentence (E10), the
   0.1364 sentence (E11), the memory sentences (E12), the E and H3 sentences
   (E13) and the stale scalars (E14).

Until 1 and 2 are done the entry asserts a success probability it does not have
and a charge that cannot be recomputed from the page it is printed on.
