# fixC: replacement texts for proof.md and claim.json

Base: research/pkg10/pkg (copy of 6cf06388). Fixes 1 (H4, H5 declared; success
under H1 to H6), 2 (neighbour budgets as halts, H6, success rebalanced), 5 (J
defined once), 6 (reviewer sentence deleted), and the sentences that conceded
a lower-bound charge or uncounted routing (fix 3, number left as [CHARGE]).

Each pair: OLD is exact text of the base file (line breaks as in the file),
NEW replaces it. Line numbers are those of the base file. Where a NEW text ends
mid-line, rewrap that paragraph to 80 columns after applying. claim.json texts
are single JSON string fragments and are not wrapped. The same pairs are split
by target in EDITS-proof.md and EDITS-claim.md for tools_integrate.py edits.

## proof.md

### P1: fix 1, 2; base line 35-40 (opening, heuristics named)

OLD
```
Three heuristics
are declared: H1, that a trial satisfies rule A and completes the collision
with probability at least 92,675,904 * 2^-128 = 2^-101.534, and that such
trials do not come in clusters; H2, that a budget on the passes of the second
test suffices; and H3, that at most one batch in 32 runs stage 2. Under the
three the search succeeds with probability at least 0.39.
```

NEW
```
Six heuristics are
declared: H1, that a trial satisfies rule A and completes the collision with
probability at least 92,675,904 * 2^-128 = 2^-101.534, and that such trials
do not come in clusters; H2, that a budget on the passes of the second test
suffices; H3, that at most one batch in 32 runs stage 2; H4, that over a run
the neighbours of a representative (Section 6.7) yield at least 40.02
trial-equivalents on average; H5, that the trials examined carry at least the
average collision mass and that collisions do not clump inside a cluster; and
H6, that three budgets on the neighbour path suffice. Under the six the search
succeeds with probability at least 0.39.
```

### P2: fix 2, 5; base line 746-753 (6.4 step 4 and the paragraph after it)

OLD
```
4. Halt with failure if 2^84 trials have been processed in step 3 without R =
   0; or if E batches have run stage 2, where E is 18,725 * J / 32 rounded down
   and J is 2^110 / 92,675,904 rounded up; or when all trials are exhausted.

A run has 1,184,670 * 2^64 pairs of an outer step and a value of X2, which is
at least J, and 18,725 batches for each pair. So E is less than one part in 32
of the batches of a run. E is the constant `STAGE_2_BUDGET` of the submitted
program, and J is its `RUN_PAIRS`.
```

NEW
```
4. Halt with failure if 2^84 trials have been processed in step 3 without R =
   0; or if E batches have run stage 2; or if G representatives have opened
   their gate; or if W neighbour words have gone through stage A; or if S
   neighbour words have entered stage 2; or when all trials are exhausted. The
   algorithm keeps a count of each of these events over the run and halts with
   failure as soon as one count reaches its budget. With J defined first, the
   budgets are

       J = 2^110 / 92,675,904 rounded up, times 64 / 41.02, rounded up,
       E = 18,725 * J / 32 rounded down,
       G = 1.2 * 0.0624630 * 2,048 * J rounded down,
       W = 1.2 * 0.5625 * 2,048 * J rounded down,
       S = 1.2 * 0.1364 * 2,048 * J rounded down.

   J pairs of an outer step and a value of X2 hold, at 41.02
   trial-equivalents per representative, at least 2^127 / 92,675,904
   trial-equivalents, at which the rate of H1 gives one half of a good trial
   on average (Section 7); J is 21,853,299,106,075,760,480,725,513, about
   1,184,669.72 * 2^64. A pair holds
   2,048 representatives on average, one for each cluster of 64 of its 131,072
   trials, so 2,048 * J is the number of representatives in J pairs. G, W and
   S are 1.2 times the measured means of 6.7 and Section 10 times that number:
   the gate opens for 0.0624630 of the representatives, and per representative
   0.5625 neighbour words go through stage A and 0.1364 enter stage 2.

A run has 1,184,670 * 2^64 pairs of an outer step and a value of X2, which is
at least J, and 18,725 batches for each pair. So E is less than one part in 32
of the batches of a run. E is the constant `STAGE_2_BUDGET` of the submitted
program, J is its `RUN_PAIRS`, and G, W and S are its constants [NAMES OF G, W
AND S].
```

### P3: fix 2; base line 757 (6.4, the budgets that can end a run)

OLD
```
of the two budgets of step 4 has ended the run before.
```

NEW
```
of the budgets of step 4 has ended the run before.
```

### P4: fix 2; base line 776 (6.4, what the program holds)

OLD
```
middle step, batch), the two lists, and the constant E.
```

NEW
```
middle step, batch), the two lists, the constant E and
the budgets G, W and S of step 4.
```

### P5: fix 2; base line 1213 (Section 7, H1)

OLD
```
no trial is good is at most exp(-1/2) + 0.002.
```

NEW
```
no trial is good is at most exp(-1/2) + 0.001.
```

### P6: fix 6; base line 1277-1280 (Section 7, end of H5)

OLD
```
Trials of one cluster share their six
outer words and differ in three bits of X2 and three bits of e1, so this is the
assumption of this package that a reviewer should test first; Section 10 says
what would settle it.
```

NEW
```
Trials of one cluster share their six
outer words and differ in three bits of X2 and three bits of e1. Section 10
says what would settle the second part.
```

### P7: fix 1, 2; base line 1282-1293 (Section 7: H6 inserted, success restated)

OLD
```
Under H1, H2 and H3 the algorithm outputs a collision with probability at least
1 - exp(-1/2) - 0.002 - 0.0005 - 0.0005 > 0.3934 - 0.003 = 0.3904 >= 0.39: by
the union bound over the three events "no trial is good", "the budget of step 3
is reached" and "the budget E is reached", which need not be independent. H1 is
read here over the trials this algorithm EXAMINES, which H5 asserts carry at
least the average mass of the trials rule A keeps; H4 and H5 do not enter that
union bound, because they are about the charge and about the trials examined,
not about a budget being reached. If H5 fails, the number of trial-equivalents
of a run falls short of N and the success probability falls with it; if H4
fails, the charge of Section 8 is too low by the ratio. When it outputs a pair,
the pair is a genuine collision: step 3 checks both complete digests, and the
messages have different lengths.
```

NEW
```
**Heuristic H6 (supporting, new in this package).** With probability at least
0.9995 over the coins, fewer than G representatives of a run open their gate,
fewer than W neighbour words go through stage A and fewer than S neighbour
words enter stage 2, where G, W and S are the budgets of step 4, each 1.2 times
its measured mean per representative. (Section 10 measures, on real messages of
the sub-class over 256 random outer tuples with 32 random values of X2 each,
the gate open for 0.0624630 of the representatives, 0.5625 neighbour words per
representative through stage A and 0.1364 per representative into stage 2,
each reproduced by three further programs to within half a per cent. The count
per value of X2 is not binomial; single values of X2 have between 0.41 and 1.64
times the mean share of open gates, so a single value of X2 can exceed the
budget on its own representatives, and single outer tuples have between
0.058577 and 0.066032. H6 is a statement about the totals over a run and is not
true value by value. That the average over the outer steps of one run stays
below 1.2 times the measured means is the assumption.)

Under H1 to H6 the algorithm outputs a collision with probability at least
1 - (exp(-1/2) + 0.001) - 0.0005 - 0.0005 - 0.0005 > 0.3934 - 0.0025 =
0.3909 >= 0.39, which is 0.39097 to five places. This is the union bound over
the four events "no trial is good", "the budget of step 3 is reached", "the
budget E is reached" and "a budget of the neighbour path is reached", which
need not be independent: H1 bounds the first by exp(-1/2) + 0.001, and H2, H3
and H6 bound the other three by 0.0005 each. H4 and H5 are premises of this
statement and of the time statement of Section 8, with no allowance of their
own. H1 is read here over the trials this algorithm EXAMINES: H4 gives their
number in trial-equivalents, and H5 says that they carry at least the average
mass of the trials rule A keeps, with no more clustering of good trials than
H1 allows. If H4 or H5 fails, the success probability falls with the yield or
with the mass; if H4 fails, the charge per trial-equivalent of Section 8 is
too low by the ratio. When it outputs a pair, the pair is a genuine collision:
step 3 checks both complete digests, and the messages have different lengths.
```

### P8: fix 2; base line 1296-1298 (Section 7, sensitivity to the factor)

OLD
```
trials give 1 - exp(-f * 759,300 / 2^47) - 0.003 with the same allowances,
which reaches 0.39 only when f is at least 92,532,532: the assumed 92,675,904
leaves no slack on the probability side.
```

NEW
```
trials give 1 - exp(-f * 759,300 / 2^47) - 0.0025 with the same allowances,
which reaches 0.39 only when f is at least 92,379,824: the assumed 92,675,904
leaves no slack on the probability side.
```

### P9: fix 1, 2; base line 1328 (end of Section 7)

OLD
```
None of the three heuristics is proved.
```

NEW
```
None of the six heuristics is proved.
```

### P10: fix 3 (text); base line 1363-1365 (Section 8, after the ledger)

OLD
```
The charge is 4.3
percent above the budgeted cost; that difference is margin for operations that
a reader may find uncounted, 0.49 per batch of seven trials.
```

NEW
```
The charge,
[CHARGE] per trial-equivalent, is an upper bound on the cost of the search that
includes the routing of the representative word, the gate, the dispatch, the
neighbour words and both stages through the 16 registers of the machine of
6.5.
```

### P11: fix 2; base line 1934-1937 (Section 10, the gate and the neighbour path)

OLD
```
Section 8 therefore
charges the share of open gates and of entered neighbour words at **1.2 times**
these measured means, a budget of the kind entry c66f230d set at 1.194 times its
measured share, and it is not proved either. Two stricter readings are on record:
```

NEW
```
Section 8 therefore
charges the share of open gates and of entered neighbour words at **1.2 times**
these measured means, a budget of the kind entry c66f230d set at 1.194 times its
measured share. Step 4 of 6.4 halts the run with failure when one of these
budgets, or the one on the neighbour words through stage A, is reached; that a
run stays within them is H6, and it is not proved either. Two stricter readings
are on record:
```

### P12: fix 3 (text); base line 2069-2072 (Section 10, the program paragraph)

OLD
```
What is NOT counted is one schedule that threads
representative word, gate, dispatch, neighbour words and both stages through a
single account of the 16 registers: every piece above is counted on its own
machine, and the register peak and the routing of the whole remain open.
```

NEW
```
The charge of
Section 8, [CHARGE] per trial-equivalent, is an upper bound that includes the
routing of representative word, gate, dispatch, neighbour words and both
stages through the 16 registers.
```

### P13: fix 3 (text); base line 2142-2143 (What does not exist)

OLD
```
- No count of the whole cluster procedure in one account of the 16 registers,
  and no self-test running one; the submitted program lacks the neighbour path.
```

NEW
```
- No part of the charge outside the count: the charge of Section 8, [CHARGE]
  per trial-equivalent, is an upper bound that includes the routing of the
  whole cluster procedure through the 16 registers.
```

### P14: fix 3 (text); base line 2207-2210 (Limits of the evidence)

OLD
```
- Since the neighbour path's pieces are counted separately on a copy of the
  program, the charge of Section 8 is below the true one by whatever routing
  them through the 16 registers costs; its two audits, by other AI models and
  not read line by line by a person, differ by 0.18 per trial-equivalent.
```

NEW
```
- The charge of Section 8, [CHARGE] per trial-equivalent, is an upper bound
  that includes the routing of the neighbour path's pieces through the 16
  registers; its two audits, by other AI models and not read line by line by a
  person, differ by 0.18 per trial-equivalent.
```

### P15: fix 1, 2; base line 2298 (Field meanings)

OLD
```
- success_probability = 0.39 holds under H1, H2 and H3 as shown in Section 7.
```

NEW
```
- success_probability = 0.39 holds under H1 to H6 as shown in Section 7.
```

## claim.json

### C1: fix 2, 5; base line line 20, restrictions[3], last sentence

OLD
```
The algorithm halts with failure when one batch in 32 has run stage 2 or when 2^84 trials that passed the second test have been processed.
```

NEW
```
The algorithm halts with failure when E batches, just under one in 32 of the batches of a run, have run stage 2, when 2^84 trials that passed the second test have been processed, or when one of three budgets on the neighbour path of proof.md Section 6.7 is reached: representatives whose gate opens, neighbour words that go through stage A and neighbour words that enter stage 2, each 1.2 times its measured mean (proof.md Section 6.4, step 4).
```

### C2: fix 1, 2; base line line 21, restrictions[4]

OLD
```
The success probability 0.39 holds only under heuristics H1, H2 and H3.
```

NEW
```
The success probability 0.39 holds only under heuristics H1 to H6.
```

### C3: fix 2; base line line 28, H1 statement

OLD
```
the probability that no trial has this event is at most exp(-1/2) + 0.002.
```

NEW
```
the probability that no trial has this event is at most exp(-1/2) + 0.001.
```

### C4: fix 2; base line line 42, H1 limitations

OLD
```
the success bound needs a factor of at least 92,532,532.
```

NEW
```
the success bound needs a factor of at least 92,379,824.
```

### C5: fix 5; base line line 62, H3 scope

OLD
```
The budget E is 18,725 * J / 32 rounded down, with J = 2^110 / 92,675,904 rounded up; a run has at least J pairs
```

NEW
```
The budget E is 18,725 * J / 32 rounded down, with J = 2^110 / 92,675,904 rounded up, times 64 / 41.02, rounded up, which is the constant RUN_PAIRS of the submitted program, 21,853,299,106,075,760,480,725,513 (proof.md Section 6.4, step 4); a run has at least J pairs
```

## Placeholders and figures to carry

- [CHARGE] occurs in P10, P12, P13 and P14 (four times in proof.md): the upper
  bound per trial-equivalent from fixA.
- [NAMES OF G, W AND S] in P2: the program's names for the three budgets.
- J = 21,853,299,106,075,760,480,725,513 (the program's RUN_PAIRS formula);
  E = 18,725 * J / 32 rounded down = 12,787,594,555,039,644,218,799,538,466.
  For checking fixA's constants, the formulas of P2 give
  G = 3,354,679,595,981,562,413,648,013,849,
  W = 30,210,000,684,239,131,288,554,949,171,
  S = 7,325,589,499,253,720,013,793,591,230.
- Success: 1 - (exp(-1/2) + 0.001) - 3 * 0.0005 = 0.390969, which is 0.39097,
  not 0.39047 (0.39047 was the old figure with 0.002 and two allowances).
- Factor needed for success 0.39 with the new allowances: 92,379,824 (was
  92,532,532), in proof Section 7 (P8) and claim.json H1 limitations (C4).
- Evidence line numbers in HEURISTICS.json are base-file numbers; P2 and P7
  add lines, so tools_integrate.py repoint must renumber them.

## Left unchanged on purpose

- proof 2048-2050 ("does not contain the neighbour path") and 2281-2285 ("the
  four pieces"): depend on what fixA puts in the program.
- proof 2106-2107 ("Neither audit has executed the whole procedure in one
  register account"): about the two audits, not the charge.
- submission-note-r2.md 190 ("H1, H2 and H3 are assumptions") and 282-284
  ("the charge is a lower bound"): outside this task's two files.
- claim.json holds no sentence conceding a lower bound or uncounted routing.
