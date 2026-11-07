## 9. Memory, preprocessing and advice

The program is the lines of steps O, M, Y and T, the four packed pieces of 6.5
and a compression routine for the final check. Bound the code by 4096
instruction templates of at most four 256-bit words each: 2^14 words, which is
2^19 bytes. Data, one packed word of 256 bits each: the table of one outer step
(5 * 149,797 words), the lists U and V (2 * 149,797), and fewer than 1,024
words for the cells of the outer step and the middle step, the mixed middle
words of 6.7, the context, the fixed constants and masks, the counts of the
budgets, the temporaries and the two messages and digests of the final check:
fewer than 1,049,603 words, that is 33,587,296 bytes. The memory of the search
is therefore below 2^19 + 33,587,296 < 2^26 bytes. Nothing grows with
the number of trials: the table is overwritten at every outer step.

**The selection procedure SEL.** The values that the program stores (listed
under advice below) were selected by searches and counts. This section writes
that selection as a procedure, SEL. Its cost is charged as preprocessing, and
it has an upper bound by construction: every search of SEL runs over a range
stated here, and every run of a program in SEL halts as soon as it has
executed a stated number of primitive word operations, its cap, or holds 2^34
bytes. A run that halts so returns nothing, and SEL goes on. Operations are
counted as in Section 8, 430 to the unit. SEL runs two programs of the
participant that are not in the package: the solver kissat, on instances made
by a generator of the participant, and the counter of Section 10, which
computes in integer arithmetic the part of one beta in the rate of a given set
of members of the class, with or without a given rule on h1.

*Step 1, the pinned call (solver runs).* For each of the 116 runs of the
participant's solver log for this search (51 runs for the lengths 55 and 63,
the other 65 for nine other variants of the instance; bounds 97 to 118; logged
seeds), build the instance of the run and run kissat on it with the logged
seed, the two together with a cap of 2^56 operations. For the lengths 55 and
63 the instance is that of entry c66f230d (its Section 10): the call C3 for
both messages with equal b and d outputs, the two words w4 related as the
length cancellation prescribes for the XOR 8 of the lengths, the top byte of
word 13 zero, E1 and E3 for both messages, a zero residual, and a bound on the
number of bit positions, bit 31 excepted, at which a difference is active in
six additions of E1 and E3. A run that finds a model returns six constants X3,
X7, X11, X15, W4, W13 and the values of a solution, among them its Y4 and its
beta. Cost: at most 116 * 2^56 < 2^62.86 operations.

*Step 2, the constants and the class (a count for each model).* For each model
of step 1, compute Y3 and Y3' by C3 from its constants, its class
eta = ROR((Y3 + Y4) XOR (Y3' + Y4), 16) from the Y4 of its solution, and with
the counter the part of the beta of its solution in the rate of that class,
with a cap of 2^52. Output the six constants and the eta of the model with the
largest part. Cost: at most 116 * (2^52 + 2^10) < 2^58.86 operations.

*Step 3, the betas.* With DY11 = Y11' - Y11 for the output of step 2, mark for
every word c1 from 0 to 2^32 - 1 the word ROR(c1 XOR (c1 + DY11), 12) in a
table of 2^32 bits, then list the marked words. These are all the words that
occur as beta (Section 10, step 1 of the count): 133,742 for the constants of
3.2. If there are more than 133,742, SEL halts with failure. Cost: below 2^36
operations.

*Step 4, the sub-class.* For each of the 524,288 members y of the class and
each beta of step 3, compute with the counter the part of the beta in the rate
of the one-member set {y}, with a cap of 2^52; the rate of a member is the sum
of its parts. A part whose run reaches its cap is recorded as unfinished.
Parts are not negative, so a recorded rate is a lower bound, and it is exact
when none of its parts is unfinished. Then, for every sub-cube of the class,
that is for each of the 3^19 ways to fix each of the 19 free bits of e1 to 0,
to fix it to 1 or to leave it free, form the mean of the rates of its members,
in one pass that keeps no list of the means. The sub-class of 6.1 is one of
these sub-cubes: bits 21 and 26 of e1 fixed to 0, the other 17 free. Cost:
524,288 * 133,742 * 2^52 < 2^88.03 operations for the counts, and 2^38
additions of at most 32 operations each, with the comparisons of the pass,
below 2^43.02 for the means. This step follows winglock, who chose the
sub-class S8 of the entries 2125212 and 2bb5d604 from the exact rate of every
one of the 524,288 members of the same class (the best of 8,992,320 candidate
sub-classes, by the text of those entries).

*Step 5, rule A.* Let W be the sixteen bits 0 to 3, 6 to 13, 16, 17, 24 and 25
of h1. For each of the 2^16 patterns of W and each beta of step 3, compute with
the counter the part of the beta in the mass of the solutions with Y4 in the
sub-class whose h1 agrees with the pattern on W (a rule of sixteen one-bit
conditions), with a cap of 2^52, recording unfinished parts as in step 4. A
rule of eight independent affine conditions on the bits of W is a set of
patterns, an affine subspace of codimension 8, and its exact mass is the sum of
the masses of its 2^8 patterns. Generate every such subspace once, as the
solutions v of M v = c for a reduced row echelon matrix M over GF(2) with eight
rows, sixteen columns and rank 8, and a right side c: there are
2^8 * [16 choose 8]_2 < 2^73.79 of them, where [16 choose 8]_2 is the number of
subspaces of dimension 8 of a space of dimension 16 over GF(2). Cost:
65,536 * 133,742 * 2^52 < 2^85.03 operations for the counts, and at most 2^12
operations per rule to generate it, sum its 2^8 masses and compare, below
2^85.79 for all rules. Rule A reads only bits of W (6.3), so it is one of these
rules.

*Step 6, the flips and the gate of 6.7.* Draw a sample of 2^24 trials of the
sub-class, their seven context words and member numbers taken from SHA-256 of a
fixed text in counter mode. For every set F of at most six of the 49 candidate
bits (the 17 free bits of e1 in the sub-class and the 32 bits of X2),
16,122,225 non-empty sets, and every trial of the sample: evaluate the trial
with the bits of F cleared (its representative) and the 2^|F| - 1 trials that
flipping bits of F gives (its neighbours), each by the 96 lines of Section 4
and the eight conditions of rule A, at most 2^10 operations a trial; record
which of the eight conditions the representative violates and how many of its
neighbours satisfy rule A, in 2^8 tallies for the set F. From the tallies
form, for every gate that rule A implies (every subspace of the span of its
eight conditions, 417,199 of them, among them the 200,787 of rank four that
GPT Sol 6.1 ranked), the share of representatives that pass the gate and the
number of neighbours that satisfy rule A behind an open gate. Cost: at most
2^24 * 2^16 + 2^28 operations per set, with the sample below 2^63.95 in all.
The six flips of 6.7 (bits 14, 30 and 31 of e1 and of X2) are one of the sets,
and the gate of 6.7 (four of the eight conditions of rule A) is one of the
gates.

**The bound.** Steps 1 to 6 cost fewer than

    2^62.86 + 2^58.86 + 2^36 + 2^88.03 + 2^43.02 + 2^85.03 + 2^85.79 + 2^63.95
      < 2^88.45 operations,

which is below 2^(88.45 - 8.748) < 2^79.71 units. preprocessing_log2 = 80 is
this bound, rounded up, and it is included in T (Section 8). It bounds SEL as
defined, whatever the two programs do inside and whatever they return, because
every run halts at its cap and every loop has the range stated. It replaces
both figures that entry c66f230d and the earlier text of this package gave:
the bound 2^63 for recomputing W4 and W13 at the four given inputs, which SEL
does not need because step 1 returns all six constants, and the estimate below
2^60 operations, which is not used.

*What rests on records.* The bound rests on no record. That SEL returns the
six constants of 3.2 and eta = 830303cf does: on the participant's solver log,
by which the run for the lengths 55 and 63 with bound 104 and seed 506 found
these constants after 4,770 seconds, with a solution of class 830303cf and
beta 18b0e098; on the record of entry c66f230d (its Section 10) that for these
constants the part of the solver's beta in the class was the largest of the
sets of the log, 71,698,432 where the largest of the others was 13,107,200; on
the solver and the counter being deterministic for given inputs; and on the
participant's observation that the solver and the counting programs stayed
below 16 GB of memory. Every run of the log stopped within 9,000 seconds on one
processor core, and no processor core executes 2^40 primitive operations in a
second, so every run used fewer than 2^53.14 operations, below its cap of 2^56.
The generator of the instances, the solver log and the counter are not in the
package. If a record were wrong, SEL could return other constants or none; its
cost would stay within the bound.

The stored sub-class, rule A, flips and gate are members of the ranges of steps
4, 5 and 6, as their definitions in 6.1, 6.3 and 6.7 show; the stored bytes
listed under advice name them. SEL computes the same figure for every member of
each range, and choosing one member by those figures reads them once, inside
the bound of its step. SEL does not show that the stored ones are the best of
their ranges by any one criterion. The sub-class and rule A were proposed by
GPT Sol 6.1 from searches of its own, which the participant has not repeated;
by that model's statements, which the participant has not checked (Section
10), the sub-class is the only best of the sub-cubes with 15 fixed bits of e1
and the rule a best set of eight affine conditions on h1. The flips and the
gate were chosen by measurements on other samples (Section 10). Steps 4, 5 and
6 have not been run; the bound does not need them to have been.

*Memory of SEL.* Every program run of SEL halts when it holds 2^34 bytes, and
SEL runs one at a time. Its own data stay below 2^31 bytes: the table of step 3
(2^29 bytes), the sample of step 6 (2^29 bytes), the rates of step 4 and the
masses of step 5 (32 bytes a member or a pattern), and the tallies of step 6.
SEL therefore holds fewer than 2^34 + 2^31 bytes at any time, and the search,
which runs after it, fewer than 2^26 bytes: memory_log2_bytes = 35 bounds both,
2^34 + 2^31 < 2^35. The measurements of Section 10 on real and on scaled-down
messages are not part of SEL; they test the heuristics and select nothing, and
neither their work nor their memory is in these figures. The cost model does
not score memory.

nonuniform_advice_log2_bytes = 6 covers the 28 bytes of the six constants and
eta, the 8 bytes that name the two bits of the sub-class and their values, and
the 12 bytes of the two masks and the word ALL of Lemma A, 48 bytes in all.
These bytes are also the names by which the stored sub-class and rule are
chosen among the candidates of steps 4 and 5. The six flips and the gate of 6.7
are part of the algorithm of 6.4 and 6.7; stored as data they would take at
most 14 more bytes (six bit positions, and a mask and a value word for the
gate), 62 in all, still below 64. The lists U and V are not advice: the program
computes them from these constants by Lemmas Q2 and A. There is no other stored
data and no stored collision.
