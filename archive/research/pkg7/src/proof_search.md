## 6. The search for the other half

**6.1 Trials.** A *context* is the six words of an outer step (C0.c1, C0.d1, D3.d1, S15, S9, w5), a word X2, and everything that steps O and M compute from them. The class and the sub-class defined next are sets of values of Y4. A **trial** is a context and a member y of the sub-class; its messages A and B are the output of steps O, M, Y, T, S2 and S3 for the context's seven words and y. Only steps Y and T depend on y: the trials of one context differ in the four message words w8..w11 and in nothing else of the message (Lemma T2 (c)). Step Y does not depend on X2: for one outer step and one member its ten names are the same for all 2^32 values of X2. The table of 6.5 rests on this.

{{part_class_q}}

*The sub-class.* The search uses only the members of the class whose e1 = Y3 + Y4 has bit 21 and bit 26 equal to zero. With Lemma Q that is the set of all Y4 with

    ((Y3 + Y4) AND {{cube_mask}}) = {{cube_value}}.

**Lemma Q2.** The sub-class is a subset of the class and has {{members}} members: the 17 bits of e1 at the positions 2 to 7, 10 to 14, 20 and 27 to 31, where {{cube_mask}} has a zero, are free, and Y4 = e1 - Y3.

Proof. {{cube_mask}} = 03cf8303 OR 04200000, and 04200000 has the bits 21 and 26, which are two of the 19 positions that Lemma Q leaves free. The value {{cube_value}} has zeros at both. So the condition is the condition of Lemma Q together with bit 21 = bit 26 = 0, and 17 positions stay free. QED.

Member number k of the sub-class, for 0 <= k < {{members_plain}}, is the Y4 whose e1 has the bits of k at its 17 free positions, in increasing order of position. From here on "member" means a member of the sub-class. Why a part of the class is searched and not all of it is a matter of the count of Section 10: under the model of that section the rate of collisions differs from member to member, and it is higher on this part. Nothing exact depends on that.

**Lemma T.** For every context and every member y of the class, and so for every member of the sub-class, the messages A and B of the trial are distinct messages of 55 and 63 bytes whose complete 2-round digests agree on digest words 0, 2, 5 and 7; in both compressions Y4 = y; and the XOR difference between A and B of E3's first-half d value is eta = 830303cf.

Proof. The first two statements are the theorem of Section 5. In both compressions w15 = 0 and Y14 is the same, the a input of E3 is Y3 for A and Y3' for B by Fact P, and Y4 = y is a member of the class, so the difference is eta by the definition of the class. QED.

{{part_residual}}

**6.3 Two tests of a trial.** The algorithm uses two tests: rule A, a condition on one word of E3 (Lemma A), and the E1 test, a 32-bit condition on E1 alone (Lemma N). The early test of the first entries on this track (Lemma E of entry c66f230d) is not used and is not restated.

{{part_lemma_n}}

*Rule A.* Let h1 be the second value of E3 on message A, as in 6.2, and write h[i] for bit i of h1, bit 0 being the lowest. A trial *satisfies rule A* when all of the following hold:

    h[0] = 0;    h[1] = 1;    h[16] = 0;    h[17] = 0;
    h[2] XOR h[10] = 1;    h[3] XOR h[11] = 1;
    h[3] XOR h[12] XOR h[24] = 0;    h[6] XOR h[13] XOR h[25] = 0.

These are eight conditions, each on one bit or on the XOR of two or three bits. Each of them contains a bit that no other contains (bits 0, 1, 16, 17, 10, 11, 12 and 13), so they are independent and a uniform word satisfies rule A with probability 2^-8. The first four are the first four conditions of the rule of entry c66f230d; the other four replace its fifth condition (bits 2 and 3 of h1 differ), which is not part of this rule.

**Lemma A.** Write z[i] and e[i] for bit i of the words z and e1 defined next.

(a) For a trial of 6.1 let z = C2.d1 XOR Y2 be the XOR of the second and the fifth value of C2, and e1 = Y3 + Y4. Then ROL(h1, 24) = z XOR ROL(e1, 8): h[i] = z[(i + 24) mod 32] XOR e[(i + 16) mod 32].

(b) For every Y4 in the sub-class, the trial satisfies rule A exactly when

    z[24] = 0;    z[25] = 1;    z[8] = 1;    z[9] = 1;
    z[26] XOR z[2] = 0;    z[27] XOR z[3] = e[27];
    z[27] XOR z[4] XOR z[16] = e[28];   z[30] XOR z[5] XOR z[17] = 1 XOR e[29].

The bits 27, 28 and 29 of e1 are free in the sub-class, so the last three right sides depend on the member.

(c) Let Z be a word of 36 bits or a lane of a packed word of 6.5 whose low 32 bits are z; its bits 32 to 35 and the neighbouring lanes may hold anything. Form the word y by

    s = (Z << 12) AND 0003c000;    y = Z XOR s;
    s = s << 12;                   y = y XOR s;
    s = (y << 13) AND 40010000;    y = y XOR s,

the shifts being shifts of the whole packed word and each mask word holding the printed value in every lane (6.5). Write y[i] for bit i of the lane. Then

    y[8] = z[8];    y[9] = z[9];    y[24] = z[24];    y[25] = z[25];
    y[26] = z[26] XOR z[2];    y[27] = z[27] XOR z[3];
    y[16] = z[16] XOR z[4] XOR z[3];    y[30] = z[30] XOR z[17] XOR z[5].

Put ALL = 4f010300, the word with the bits 8, 9, 16, 24, 25, 26, 27 and 30. For a member of the sub-class let v be the word with

    v[8] = 0;    v[9] = 0;    v[24] = 1;    v[25] = 0;    v[26] = 1;
    v[27] = 1 XOR e[27];    v[16] = 1 XOR e[27] XOR e[28];    v[30] = e[29]

and zeros elsewhere. Then the trial satisfies rule A exactly when (y XOR v) AND ALL = ALL.

(d) Put u = (y XOR v) AND ALL. Then u + (2^32 - ALL) is at most 2^32, and its bit 32 is 1 exactly when the trial satisfies rule A.

Proof. (a) The sixth assignment of C2 is Y14 = ROR(C2.d1 XOR Y2, 8) = ROR(z, 8), and the second assignment of E3 is h1 = ROR(Y14 XOR e1, 16). So h1 = ROR(z, 24) XOR ROR(e1, 16), and rotating left by 24 gives the claim.

(b) By (a) the eight conditions read: z[24] XOR e[16] = 0; z[25] XOR e[17] = 1; z[8] XOR e[0] = 0; z[9] XOR e[1] = 0; z[26] XOR e[18] XOR z[2] XOR e[26] = 1; z[27] XOR e[19] XOR z[3] XOR e[27] = 1; z[27] XOR e[19] XOR z[4] XOR e[28] XOR z[16] XOR e[8] = 0; z[30] XOR e[22] XOR z[5] XOR e[29] XOR z[17] XOR e[9] = 0. The bits 0, 1, 8, 9, 16, 17, 18, 19, 22 and 26 of e1 lie in the mask {{cube_mask}} of Lemma Q2, so they have the same value for every member of the sub-class: in {{cube_value}} the bits 0, 1, 8, 9, 18 and 19 are 1 and the bits 16, 17, 22 and 26 are 0. Inserting these values gives the conditions on z. Bit 26 is fixed only in the sub-class, not in the class.

(c) Follow the three steps on one lane. In Z << 12, position p of a lane holds bit p - 12 of the same lane for 12 <= p <= 35, and the mask 0003c000 keeps the positions 14 to 17. So the first s holds z[2], z[3], z[4], z[5] at the positions 14 to 17 and nothing else, and after the first step y differs from Z only there. The second s holds the same four bits at the positions 26 to 29, still inside the lane; after the second step y[26] = z[26] XOR z[2] and y[27] = z[27] XOR z[3], and the positions 3 and 17 hold z[3] and z[17] XOR z[5]. In y << 13 the positions 16 and 30 hold the bits 3 and 17 of the lane, and the mask 40010000 keeps exactly these two positions; after the third step y[16] = (z[16] XOR z[4]) XOR z[3] and y[30] = z[30] XOR (z[17] XOR z[5]). The positions 8, 9, 24 and 25 were never changed. Every bit that entered one of the eight positions is a bit 2, 3, 4, 5, 8, 9, 16, 17, 24, 25, 26, 27 or 30 of the lane itself: no bit above 31 and no bit of another lane. That proves the eight equations. A position of v holds a 1 exactly where the right side that (b) requires is 0, so bit t of y XOR v is 1 exactly when y[t] has the required value, where the required values are: z[8] = 1, z[9] = 1, z[24] = 0, z[25] = 1, z[26] XOR z[2] = 0, z[27] XOR z[3] = e[27], these being six of the conditions of (b) as they stand; y[30] = 1 XOR e[29], the eighth; and y[16] = e[27] XOR e[28], which is the XOR of the sixth and the seventh condition, because y[16] = (z[27] XOR z[3]) XOR (z[27] XOR z[4] XOR z[16]). When the sixth condition holds, the condition at position 16 holds exactly when the seventh does. So all eight positions of ALL hold a 1 in y XOR v exactly when all eight conditions of (b) hold.

(d) u has no bit outside ALL, so u <= ALL, and u + (2^32 - ALL) >= 2^32 exactly when u = ALL; the sum is at most 2^32. By (c), u = ALL exactly when the trial satisfies rule A. QED.

*What Lemma A does not say.* Lemma A says that the word of (c) tests rule A exactly. It does not say that a collision satisfies rule A, and that is not true: there are solutions of R = 0 with Y4 in the sub-class whose h1 violates rule A. Rule A is therefore a filter that loses solutions. A batch in which no trial satisfies it is dropped, whether or not one of its trials has a zero residual; a trial that fails rule A is examined further only if another trial of its batch satisfies it (6.4). How much is lost is a question about the count of Section 10 and is answered there: inside the sub-class the rule keeps all but {{rule_loss}} of the {{r_sub}} counted, and the figure that H1 is set against leaves out, in full, every outcome of the count in which some solution violates rule A. On the whole class the same eight conditions would keep less than half of the count; the rule is a rule for this sub-class only.

**6.4 Algorithm.**

1. Draw one fresh uniform 256-bit word and take from it the four words C0.c1, D3.d1, S15 and S9.
2. For each of the {{nd}} values of C0.d1 from 0 to {{nd_last}}, in increasing order, and for each of the 2^32 values of w5, in increasing order, do one *outer step*: (a) run step O for the six words and store the 21 words of 6.5 that the later steps load; (b) build the table of 6.5: for each of the {{list_words}} words of the list U, in order, run the lines of step Y for its seven members in one packed word and store five words; (c) for each of the 2^32 values of X2, in increasing order: run step M and store its nine words; then run the batches of 6.5 for the {{members}} members of the sub-class in the order of their numbers, seven members in one packed word. Every batch runs stage A, which reads two words of the table and one word of the list V and tests rule A for its seven trials. If none of them satisfies rule A the batch ends and its trials are dropped. Otherwise the batch runs stage 2, which reads the three other words of the table and evaluates the E1 test for its seven trials.
3. For every trial of a batch that ran stage 2 whose E1 test word is zero, compute its words by steps Y and T and R in full. If R = 0, build A and B by steps S2 and S3 from the trial's words, evaluate H(A) and H(B), check that they agree, output (A, B) and halt. The last word of the list holds four members; its three spare lanes repeat the last member, and a member is processed once however many lanes hold it.
4. Halt with failure if 2^{{pass_budget_log2}} trials have been processed in step 3 without R = 0; or if E batches have run stage 2, where E is {{list_words}} * J / {{share_inv}} rounded down and J is 2^110 / {{factor}} rounded up; or when all trials are exhausted.

A run has {{nd}} * 2^64 pairs of an outer step and a value of X2, which is at least J, and {{list_words}} batches for each pair. So E is less than one part in {{share_inv}} of the batches of a run. The number E is the constant `STAGE_2_BUDGET` of the submitted program, and J is its `RUN_PAIRS`.

A trial with R = 0 that satisfies rule A is found: its batch runs stage 2, its E1 test word is zero by Lemma N, and step 3 computes its residual, unless one of the two budgets of step 4 has ended the run before. A trial with R = 0 that violates rule A is found only if another trial of its batch satisfies rule A; Section 7 does not count such trials.

**The ranges.**

| Word | Values | Where it comes from |
| --- | --- | --- |
| C0.c1, D3.d1, S15, S9 | any word, fixed for the run | random word of step 1 |
| C0.d1 | 0, 1, .., {{nd_last}} | slow outer loop |
| w5 | 0, 1, .., 2^32 - 1 | outer loop, piece "next w5" |
| X2 | 0, 1, .., 2^32 - 1 | middle loop, piece "next X2" |
| member number k | 0, 1, .., {{members_last}} | lists U and V, table |

List word j holds the members 7j, .., 7j + 6; list word {{last_word}} holds the numbers {{last_first}} to {{members_last}}, and the last of them three times more.

*What the submitted program holds of this, and what it does not.* The program contains the four counted pieces (outer step, table build for one list word, middle step, batch), the two lists, and the constant E. It contains no loop over C0.d1, w5 or X2, no step 3 and no budget of step 3, and it does not act on the result of an end test; its experiments draw all seven context words as full 32-bit words. The ranges above, the form of the loops and step 3 are defined by this text only.

**The loop form and the two end tests.** The counted piece *next X2* is: load the cell X2, add 1, reduce to 32 bits, load the cell `X2 end`, compare, branch; then store the new X2 and form and store X2 + w7. It is the first part of the middle step. The middle loop is this piece followed by the rest of step M and the {{list_words}} batches, repeated, and it is entered behind the branch with X2 = 0 in the register:

    X2 := 0;  go to (*)
    repeat
        X2 := (X2 + 1) mod 2^32;  leave the loop if X2 = 0
    (*) store X2, form and store X2 + w7
        the rest of step M, the class loop entry, the batches

The cell `X2 end` holds 0, so the comparison is true exactly when the word has come back to 0, after the passes for 0, 1, .., 2^32 - 1. The first half of the piece is executed 2^32 times in an outer step (the last time it leaves the loop) and the second half 2^32 times (the first time from the entry), so the piece is executed once per value of X2, as 6.5 counts it. The outer loop over w5 has the same form with the piece *next w5*, the cell `w5 end`, which holds 0, and the words w5 and w5 + delta: the piece is executed once per outer step. The loop over the list words, in the build and in the batches, advances the list position, compares it with {{list_words}} and branches (the part "loop" of 6.5), once per list word.

*What starts a loop.* The machine counts of 6.5 do not contain: the entry of the middle loop, once per outer step (X2 := 0 and the four words that the first half of the piece would have fetched: at most 5 operations and loads); setting the list position to zero before the build and before the batches of a value of X2 (one operation each); and, once per value of C0.d1, the next value of C0.d1 with its end test, its store and the entry of the loop over w5 (at most 16 operations, loads and stores). They are at most 1 operation per value of X2, at most 8 per outer step and at most 16 per value of C0.d1, and Section 8 adds them as such. They are stated in words and were not written out on the machine.

**Lemma T3 (the trials of a run are distinct).** For every choice of the four words of step 1, the {{nd}} * 2^32 * 2^32 * {{members}} = {{nd}} * 2^81 quadruples (C0.d1, w5, X2, k) of step 2 give pairwise distinct messages A, and so that many distinct pairs (A, B). Each pair is a trial with the properties of Lemma T.

Proof. The properties are Lemma T, which holds for all values of the eight words. For distinctness, take two different quadruples. They differ in C0.d1, in w5, in X2 or in k, and two different member numbers are two different words y: by Lemma Q2 the number fills the 17 free bit positions of e1 = Y3 + Y4, and y = e1 - Y3. So the two tuples of eight words (C0.c1, C0.d1, D3.d1, S15, S9, w5, X2, y) differ in at least one word, and by Lemma T2 (d) they give different blocks and so different messages A. QED.

**How many trials.** One outer step supplies 2^32 values of X2 with {{members}} members each: 2^49 trials, in 2^32 * {{list_words}} batches, all with one table. With the factor {{factor}} of H1 the search needs 2^127 / {{factor}} = 2^{{trials_log2}} trials. The {{nd}} values of C0.d1 (2^46 / {{factor}}, rounded up) give {{nd}} * 2^81 trials, which is that many or more, in {{nd}} * 2^32 = 2^{{outer_log2}} outer steps. Entry c66f230d ran C0.d1 (its vd) below 2^19 and all {{members_class}} members; here the members are a quarter and the range of C0.d1 is 2.72 times as long.

The probability space of Section 7 is the one random word of step 1; the trials depend on it only through the four words C0.c1, D3.d1, S15 and S9. All trials of a run share these four words; the 2^49 trials of one outer step share six words; the {{members}} trials of one context share seven. Some names are shared more widely, as the lines of Section 4 show. X9 and X14 are computed from D3.d1 and S9 alone, so with the four constant words six of the sixteen words of X are the same in every trial of a run. Of the 29 lines of step O, 25 (among them w6 and w7) do not read C0.d1. Y8 and Y12 are computed from C0.c1, D3.d1, S9, w5 and y alone: for one value of w5 and one member, Y12 and w5, two of the words that E1 reads, are the same in all {{nd}} * 2^32 trials of a run with them, about 2^{{w5_family_log2}}, and a run has 2^49 such pairs of w5 and a member.

{{part_packed}}

*The two lists.* For list word j, U[j] holds ROL(y, 7) and V[j] holds the word v of Lemma A (c), one member y per lane; lane i belongs to member number 7j + i. Each list has {{list_words}} packed words, because {{members_plain}} = {{full_words}} * 7 + 4; the three spare lanes of the last word repeat its last member. Both are computed once, before step 2, from eta, the two bits of the sub-class, Y3 and the rule (Lemmas Q2 and A), and are the same for the whole search. The build of the table reads U; stage A of a batch reads V; step 3 reads U for the member of a passing lane.

*The words of an outer step.* Step O is run with every value in all seven lanes, and 21 words are stored, each below 2^32 in every lane, in the form in which the later pieces load them:

- loaded by the build of the table (7): C0.b1, -C0.c1, -C0.b1 - w6, -X4, ROL(C0.d1,16), S6, -S11;
- loaded by the middle step (8): -D2.b1 - W13, ROL(X13,8), -S2 - S7, S9 + 1, 1 - S6, D2.c1 + 1, ROL(S4,7), w7;
- loaded by a batch (6): S10 + X15, X14, X13, X9, w5, w5 + delta.

*The table of an outer step.* Five lists of {{list_words}} packed words each, built once per outer step from U, the seven words above and the word C0.d1 of the slow loop. For list word j and lane i, with y the member of that lane and the names of step Y:

    Y12[j] = Y12        XA[j] = C0.a1 - X4        X6[j] = X6
    X1[j]  = X1         R[j]  = ROL(D1.d1, 16)

all modulo 2^32 and below 2^32 in every lane. The build computes, in every lane:

- C0 backwards: Y8 = U[j] XOR C0.b1; Y12 = Y8 + (-C0.c1), reduced and stored; Y0 = ROL(Y12,8) XOR C0.d1; C0.a1 = Y0 + (-C0.b1 - w6); XA = C0.a1 + (-X4), reduced and stored; X12 = C0.a1 XOR ROL(C0.d1,16).
- D1 backwards: D1.c1 = (X12 XOR M) + (X11 + 1), which is X11 - X12; D1.b1 = ROR(D1.c1 XOR S6, 12); X6 = ROR(D1.b1 XOR X11, 7), stored; D1.d1 = D1.c1 + (-S11); X1 = ROL(X12,8) XOR D1.d1, reduced and stored; R = ROL(D1.d1,16), stored.

*The words of a middle step.* Step M is run in all seven lanes, and nine words are stored: X2 itself; the seven words that a batch loads, X2 + w7, -w2, w0, S5, w3, S12 and w12 - S1 - S6; and w1, which no batch loads (it is a word of the message and is needed in step 3).

*What a batch computes.* The seven trials of a batch share a context and are seven consecutive members. A batch has two stages. Stage A computes in every lane:

- D0, as far as C2 needs it: X0 = XA[j] + (-w2); D0.d1 = X0 XOR ROL(X15,8); X10 = D0.d1 + (S10 + X15), which is the third value S10 + D0.d1 plus X15 in one addition.
- C2 to z: its first value C2.a1 = X6[j] + (X2 + w7), its second, third and fourth value, the fifth as the first plus the fourth plus w0, and z, the XOR of the fifth and the second.
- Rule A: the word y of Lemma A (c) from z, u = (y XOR V[j]) AND ALL, the sum u + (2^32 - ALL) of Lemma A (d), and whether its bit 32 is set in some lane.

If it is set in no lane, the batch ends. Otherwise stage 2 computes:

- The entry count: the number of batches that have run stage 2 is advanced and compared with its budget E (step 4).
- C2, rest: z and the third value of C2 are formed again (see the machine below); Y14 = ROR(z, 8); and Y6 from the third value plus Y14 and the fourth value.
- D0, rest, and C1 to Y1: D0's third value as X10 + (-X15), D0.b1 with S5, and X5; C1's first value X5 + X1[j] + w3, its second, third and fourth value; D1.a1 = R[j] XOR S12; and the sum of C1's first value, its fourth value and D1.a1, which is Y1 + S1 + S6, since w10 = D1.a1 - S1 - S6.
- E1 on A and B: a1 as that sum plus Y6 plus the stored w12 - S1 - S6; d1 = ROR(a1 XOR Y12[j], 16); c1, c1', b1, b1', a2, a2', c2, c2', with Y11' and w5 + delta for B.
- The E1 test: eps = c2 XOR c2', beta XOR eps, the word n of Lemma N, and whether n is zero in some lane.

Nothing of E3 is evaluated in a batch: rule A is a condition on E3.h1, but by Lemma A it is tested on z, a value of C2, with the bits of e1 folded into the constants and into the list V. The words w8..w11 are never formed in a batch; step 3 computes them, with the values of C1 and E3 that the batch leaves out, for the trials it processes.

**Lemma T4 (the table).** Fix the six words of an outer step, and let the memory hold the 21 words that step O stores for them. (a) For every list word j the build stores the five words displayed above: in lane i, the values Y12, C0.a1 - X4, X6, X1 and ROL(D1.d1,16) of the member of that lane, each below 2^32. (b) These five words do not depend on X2. (c) For every value of X2, every list word j and every lane, the lines of a batch that read a table word compute names of the trial (the six words, X2, the member of the lane):

    X0 = XA[j] - w2                          C2.a1 = X6[j] + X2 + w7
    C2.b1 = ROR(X6[j] XOR C2.c1, 12)         C1.a1 = X5 + X1[j] + w3
    D1.a1 = R[j] XOR S12                     E1.d1 = ROR(E1.a1 XOR Y12[j], 16).

Proof. (a) The ten lines of the build are the ten lines of step Y with the packed forms of this section: U[j] is ROL(y,7); an addition of a stored word -v is the subtraction of v; and (X12 XOR M) + (X11 + 1) is X11 - X12 modulo 2^32 in a lane, because XOR with M complements the low 32 bits. No sum leaves its lane (below), so the low 32 bits of every lane are the scalar value, and the words that are stored after a sum are reduced by an AND with M; R and X6 are rotation outputs. XA is the name C0.a1 plus the stored -X4. (b) Y12, C0.a1, X6, X1 and D1.d1 are table lines and X4 is an outer line, so by Lemma T2 (c) none of them depends on X2. (c) The six equations are the lines for X0, C2.a1, C2.b1, C1.a1, D1.a1 and E1.d1 of Section 4 with the words of (a) in the place of the names: XA[j] - w2 = C0.a1 - X4 - w2, R[j] XOR S12 = ROL(D1.d1,16) XOR S12, and the other four contain X6, X1 and Y12 as they stand. QED.

*The machine, and which words are kept in registers.* The pieces run on a load/store machine with 16 registers. One operation is charged for every addition, XOR, AND, OR and shift of 256-bit words, for every comparison and for every branch, so PROR = 5. One load is charged every time a word is fetched from memory, from a list or from the table into a register, and one store every time a register is written to memory or to the table. Shift distances are fixed in the instruction. A register may hold a memory word across several operations, and that is the one place where this text counts differently from entry c66f230d, which charged a load for every use of a constant. Here nine words are loaded once per value of X2, in the last part of the middle step ("class loop entry", 9 loads), and stay in their registers for all {{list_words}} batches of that value: the two masks of the rotation by 16, the two masks of the rotation by 12, the two masks of Lemma A (c), ALL, 2^32 - ALL, and the word that has every bit of the seven lanes except bit 32. A batch reads them without a load. Stage 2 needs the registers of the last four of them for its own values and loads these four words again at its end (the part "restore", 4 loads, charged to stage 2). Stage A does not keep z and the third value of C2 in registers; stage 2 forms both again (5 operations and 3 loads, charged to stage 2). Two registers hold the list position and the entry count for the whole search. With that, the batch uses all 16 registers, and 15 do not run it, under the program's convention that the result of an instruction may reuse a register whose source value is used for the last time on that same instruction; if instead every source stays live until its instruction finishes, the batch peaks at 17 registers, and the one extra word, spilled and loaded again inside the batch, costs far less than the margin already left between the budget and the charge. The idea of keeping masks in registers across a loop is credited in Section 13. Under the convention of entry c66f230d, with every read of a memory word charged as a load, the same program counts {{kept0_a}} and {{kept0_2}} for the two stages (its line `KEPT = 0`), and the claim would be {{kept0_claim}}; no address arithmetic is charged for the list and table loads, as in that entry, and with one operation for each such load the stages would be {{addr_a}} and {{addr_2}} and the claim {{addr_claim}}.

*No lane overflows.* Put B = 2^32. Table words, list words, stored words, rotation outputs and constants are below B, and an XOR with a value below B keeps a bound that is a multiple of B. In the build, Y12 and C0.a1 are sums below 2B, XA is below 3B before it is reduced, D1.c1 is below 3B and D1.d1 below 4B, and X1 is below 4B before it is reduced. In stage A, X0 is below 2B and X10 below 3B; C2's first value is below 2B, its third, X10 plus a rotation output, below 4B, and its fifth below 4B, so z is below 4B; by Lemma A (c) the bits of z above 31 never reach a position that is read, and by Lemma A (d) the sum of rule A is at most B. In stage 2, z and the third value are formed again within the same bounds and the sum for Y6 is below 5B; X10 + (-X15) is below 4B; C1's first value is below 3B, its third below 2B, and Y1 + S1 + S6, a value below 3B plus two values below B, below 5B; in E1, a1 is below 7B, c1 and c1' are below 2B, the two a2 are below 9B and c2 and c2' are below 3B. In the E1 test beta XOR eps is below 4B, so its shift to the left by one bit stays inside the lane, n is reduced by an AND with M, and the sum that forms the flags is below 2B. So every sum of a batch is below 9B and every sum of the build below 4B, which is below 2^36 = 16B: no carry leaves a lane, the low 32 bits of every lane equal the scalar value modulo 2^32, and XOR and PROR read only those bits. For the outer step and the middle step a participant tool derives the bounds by interval arithmetic on a second machine: below 7B and below 8B. Every word that is stored and every word that enters the flags of stage 2 is below B.

*Operation counts.* For the rule with {{rule_n_word}} conditions, on the machine above:

{{batch_table}}

So stage A is {{a_ops}} + {{a_loads}} = {{a_total}} and stage 2 is {{s2_ops}} + {{s2_loads}} = {{s2_total}}. The three other pieces:

{{pieces_table}}

The build is {{build_sum}} per list word, that is {{build_total}} * {{list_words}} = {{build_per_outer}} per outer step; the middle step is {{middle_sum}} and the outer step {{outer_sum}}. Registers in use at one time, the two for the list position and the entry count included: {{reg_batch}} in a batch, {{reg_outer}} in the outer step, {{reg_build}} in the build, {{reg_middle}} in the middle step.

Each XOR followed by a rotation is 6 operations, a two-term sum 1 and a three-term sum 2. The loads of stage A are the list end, XA[j], -w2, ROL(X15,8), S10 + X15, X6[j], X2 + w7, X14, w0 and V[j]: {{a_loads}}. In the part "rule A" the word y is 8 operations (two shifts with an AND and an XOR, one shift with an XOR), u is an XOR with the loaded V[j] and an AND, the sum is one addition, and the flags are an OR with the word that has every bit except bit 32 of each lane, a comparison with that word and the branch: 14 operations and one load. The loads of stage 2 are the budget; X6[j], X2 + w7 and w0 for z, and the two mask pairs of the rotations by 8 and by 7; -X15, S5, X1[j], w3, X13, X9, R[j] and S12; w12 - S1 - S6, Y12[j], Y11, w5, Y11' and w5 + delta; the mask of the rotation by one bit, M, the mask of bit 32 and eta; and the four words of the part "restore": {{s2_loads}}. The count of the middle step is for all 21 lines of step M and its nine stores; two of the lines (S0 and w1) and the store of w1 serve only step 3 and are counted for every value of X2 all the same.

*The count in the submitted program.* The program of the two declared experiments, experiments/halfsearch.py, contains the four pieces and the machine that counts them. A packed word is one integer with seven 36-bit lanes. Every addition, XOR, AND, OR and shift of packed words is a call that adds one operation, every fetch of a memory word, list word or table word is a call that adds one load unless the word is one of the nine kept in registers, every write is a call that adds one store, and every comparison and every branch adds one operation. The pieces are written with these calls only. The program always evaluates both stages of a batch, so that stage 2 is counted and checked for every batch; the algorithm runs stage 2 only after a pass of stage A. The command

    python3 experiments/halfsearch.py --selftest N [seed]

runs N cases. A case is one outer step, one word of each list of the table, one middle step and one packed batch; the seven context words and the list position of a case come from SHAKE-256 of the seed text (default 1) and the case number. Every fourth case is the last batch of the sub-class, and in every fifth case each context word is 0, 2^32 - 1 or as drawn. Every lane is checked against the real messages of its trial. The program builds the messages A and B of the trial by steps O, M, Y, T, S2 and S3 and compresses each in full, with a 2-round compression written out from Section 1 and with no shortcut of the batch. From these two compressions it takes Y4 of A; h1, the second value of E3 on A; the word n of Lemma N, from E1 evaluated for A and for B on their own states and words; and the two digests. A lane is right when the sixteen words of the 55 bytes of A are the words of the trial, Y4 is the member of the lane, the digests agree on digest words 0, 2, 5 and 7, the stage-A flag says whether h1 satisfies rule A as written in 6.3, the reduced word of stage 2 equals n, n equals D3 XOR ROL(D6, 8) of the two digests, and the stage-2 flag says whether n is nonzero; no lane of a case counts as right unless every word that the outer step, the build and the middle step have stored is the word of the context, and unless both branches are taken exactly when one of the seven words in front of them is zero. The program prints one JSON line with the cases, the lanes checked and right, the lanes that satisfy rule A and the batches in which one does, operations, loads and stores per part of the four pieces, whether they are the same in every case and equal to the tables above, the largest lane of a sum per part next to its bound, the registers in use per piece, the words kept in registers, the members in the lists, and two complete enumerations: the flags of stage 2 on all 128 patterns of zero and nonzero lanes, and the flags of stage A on packed words in which every pattern of the 13 bits of z that rule A reads, with every pattern of the bits 27 to 29 of e1, occurs once in every lane. Its exit status is 0 only if all of these agree with this section.

With N = {{st_cases}} and seed 1 it reports {{st_lanes}} of {{st_lanes}} lanes right; {{a_ops}} operations and {{a_loads}} loads in stage A and {{s2_ops}} and {{s2_loads}} in stage 2, per part as in the table and the same in every case; largest sums of {{st_sums}} times 2^32 in the parts "X0 to X10", "C2 to z", "rule A", "C2, rest", "C1 to Y1", "E1, A and B" and "E1 test", below the bounds {{st_bounds}}; {{members}} members in the {{list_words}} words of each list; and {{reg_batch}}, {{reg_outer}}, {{reg_build}} and {{reg_middle}} registers. In that run {{st_rule_lanes}} lanes satisfy rule A, in {{st_rule_batches}} batches. None of the words n of that run is zero, so the flags of stage 2 are also formed for all 128 patterns of zero and nonzero lanes: all 128 are right. For rule A the program forms {{st_patterns}} packed words in which each of the 2^16 patterns occurs once in every lane, with different other bits and filled guard bits, and compares the stage-A flags with rule A as written on h1 = ROR(ROR(z, 8) XOR e1, 16): all {{st_patterns}} are right. In {{st_satisfied}} of these words some lane satisfies the rule; that is 7 * 256, each lane in 256 of the words, the share 2^-8.

A longer run of the same self-test, {{lt_cases}} cases with seed 61, reports {{lt_lanes}} of {{lt_lanes}} lanes right, the same counts in every case, the same registers and a largest sum of {{lt_largest}} * 2^32; {{lt_rule_lanes}} of its lanes satisfy rule A, in {{lt_rule_batches}} batches. Its contexts are random or extreme by design and are not laid out as a run of 6.4, and every fourth case is the short last batch, whose spare lanes repeat a member, so these two counts are not a measurement of a rate. A participant tool with a second counting machine, which shares no code with the machine of the program, counts the same operations, loads and stores for all four pieces and refuses the batch with 15 registers; another derives the bounds of the sums for all inputs by interval arithmetic and finds every one below the bound of its part.

In the declared experiment `residual-search` the same program evaluates, per organizer seed, one outer step, the table words of one list word, one middle step and one batch, for that seed's context and the list position that holds the first member tried, and returns the operations and loads of the two stages of the batch, its number of right lanes and whether a lane satisfied rule A as observations. The organizer's runner records observations as untrusted and does not recompute them. The self-test and these observations therefore show what the program in the package counts, and that its lanes agree with the program's own compression of the real messages. They are a participant check, not an organizer verification of the cost.
