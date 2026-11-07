# A free half-collision and a two-level sub-class search for 2-round BLAKE3

The scalar below is `time_log2` under `collision-frontier-v5`. Memory is a separately reported resource bound.

This exploratory package targets blake3-r2-prefix-v1. It has an exact part and a heuristic part, and it keeps them apart. It continues entry c66f230d of the same participant (time_log2 97.6) on the same pair of lengths and with the same six constants. Section 11 corrects the errors that were found in the text of that entry, Section 12 says what is the same and what is new, and Section 13 credits the people and the models whose work is used here.

**Exact part.** An explicit construction maps any eight 32-bit words to a 55-byte message A and a 63-byte message B whose complete 2-round BLAKE3-256 digests agree on digest words 0, 2, 5 and 7, that is on 128 of the 256 digest bits. There is no search in this construction and no probability: it holds for all 2^256 choices of the eight words (Sections 2 to 5). One of the eight words is the value of one internal word of round 1, called Y4. The search holds Y4 inside a set of {{members}} values, a *sub-class* of the class of {{members_class}} values that entry c66f230d searched (Section 6.1).

**Heuristic part.** A collision needs the other four digest words to agree as well. The algorithm searches 2^{{trials_log2}} such pairs, all with Y4 in the sub-class, for one where they do. The search is arranged in two levels: the values of a trial that depend only on the outer loop and on Y4 are computed once per outer step and kept in a table of fixed size, which serves 2^32 passes over the sub-class. Nothing grows with the number of trials, and nothing is sorted or looked up by value. Seven trials are evaluated in one 256-bit word, in two stages. Every batch runs stage A, which tests {{rule_n_word}} bit conditions on one internal word of every trial (rule A). Only a batch in which a trial satisfies rule A runs stage 2, which tests a 32-bit condition that every collision satisfies. A batch in which no trial satisfies rule A is dropped; a trial that fails rule A is examined further only if another trial of its batch satisfies it, and Section 7 does not count such a trial. A trial is charged {{charge}} primitive operations, memory loads and stores included. Three heuristics are declared: H1, that a trial satisfies rule A and completes the collision with probability at least {{factor}} * 2^-128 = 2^-{{rate_log2}}, and that such trials do not come in clusters; H2, that a budget on the passes of the second test suffices; and H3, that at most one batch in {{share_inv}} runs stage 2. Under the three the search succeeds with probability at least 0.39. Total charged time is below 2^{{bound_2dec}} target-compression units, so the claimed scalar is {{time_log2}}. The search needs less than 2^{{search_mem_log2}} bytes of memory; the declared 2^35 bytes also cover the computations by which the constants, the class, the sub-class and the rule were selected (Sections 6 to 9).

The rate in H1 is an assumption: {{factor}} times the rate of a uniform 128-bit value. It is not read off single digest words. Section 10 describes what it is set against. The remaining half of the digest depends on seven words, one of which is Y4. Under the model that the other six behave like independent uniform words over the trials, the rate is the number of solutions of a fixed system of equations, and that number is counted in integer arithmetic: it is {{r_sub}} times 2^-128 for Y4 in the sub-class ({{r_class}} for the whole class). Rule A is not implied by a collision: some solutions violate it and are lost. Of the count, {{kept_exact_int}} satisfy rule A; the figure that the claim uses is the smaller {{kept_cons_int}}, which leaves out in full every part of the count in which some solution violates rule A. H1 assumes {{factor}} times, {{margin}} times less. The rates with and without rule A are equal, to the last digit of every fraction, to those of another AI model (GPT Sol 6.1), which proposed the sub-class and the rule; the figure {{kept_cons_int}} that the claim uses is the participant's alone. The counting programs are not part of the package, and they and all their checks are the participant's or that model's. The model was compared with real messages only on events of probability about 2^-40 and above. In the arrangement of this package those comparisons show that the model does not hold inside one outer step, neither for rule A nor for the call E1: only averages over outer steps have the model's values (Section 10). No measurement exists for the sub-class with rule A beyond samples of at most 2^30 real trials on a processor, and the organizer-run experiments measure neither the model nor the factor. With the uniform rate, and not {{factor}} times it, the same search needs 2^127 trials and gives time_log2 = {{uniform_claim}}.

No full 2-round collision is exhibited, and the search is far beyond feasible computation. What is exhibited, and checked by the organizer's own runner, is the exact half-collision on trials of the search and a toy-scale run of the search over the sub-class, without the two tests, the table and the packing that set the cost of a trial. The program the organizer runs also contains the four counted pieces of the search (outer step, table build, middle step, packed two-stage batch), a machine that counts their operations, loads and stores, and a self-test of that count (Section 6.5). Those counts are the program's own; the organizer does not check them.

{{part_s1_s3}}

## 4. Construction: the message from eight words, in three levels

The construction places the six constants of 3.2 where Lemma H needs them, keeps w14 = w15 = 0, and gives the word Y4, the b output of C0, a prescribed value. Its input is eight free words. Six of them belong to an *outer step*:

    C0.c1, C0.d1, D3.d1, S15, S9, w5,

where C0.c1 and C0.d1 are the third and the second value of the round-1 call C0, D3.d1 is the second value of the round-0 call D3, S15 and S9 are words of the state after the column step of round 0 and w5 is a message word. The seventh is X2, a word of the state after round 0; the six words and X2 together are a *context*. The eighth is y, the value that Y4 is to have. The state words X3, X7, X11, X15 are the constants, w4 = W4, w13 = W13 and w14 = w15 = 0.

*Names.* For a call TAG of Section 1, TAG.a1, TAG.d1, TAG.c1 and TAG.b1 are its first, second, third and fourth value (Section 2); its other four values are its outputs and carry the names of the state they are written to (S after the column step of round 0, X after round 0, Y after the column step of round 1). In the names of entry c66f230d, C0.c1 = vc, C0.d1 = vd, C0.b1 = vb and C0.a1 = va.

The construction has four steps. Step O reads the six words of the outer step. Step M reads X2 in addition. Step Y reads the six words and y, and not X2. Step T reads everything. In every step a name on the right is one of the eight words, a constant or a name assigned on an earlier line of this step or of a step it may read, and all arithmetic is modulo 2^32. (The submitted program computes steps O and M in its functions `outer` and `middle`, which it describes as the first and the second part of "Step S1", the name of entry c66f230d; step Y is its function `member` and step T is in its function `trial`.)

**Step O (the outer step; 29 lines).**

    K2, forwards from w5; its first four values are constants:
        K2.a1 = IV[2] + IV[6] + W4;   K2.d1 = ROR(55 XOR K2.a1, 16)
        K2.c1 = IV[2] + K2.d1;   K2.b1 = ROR(IV[6] XOR K2.c1, 12)
        S2 = K2.a1 + K2.b1 + w5;   S14 = ROR(K2.d1 XOR S2, 8)
        S10 = K2.c1 + S14;   S6 = ROR(K2.b1 XOR S10, 7)
    D3 with w14 = w15 = 0, from D3.d1, its inputs S9, S14, its output X3:
        D3.a1 = ROL(D3.d1,16) XOR S14;   D3.c1 = S9 + D3.d1
        D3.b1 = X3 - D3.a1;   S4 = ROL(D3.b1,12) XOR D3.c1
        S3 = D3.a1 - S4;   X14 = ROR(D3.d1 XOR X3, 8)
        X9 = D3.c1 + X14;   X4 = ROR(D3.b1 XOR X9, 7)
    K3, backwards from its outputs S3, S15:
        K3.d1 = ROL(S15,8) XOR S3;   K3.c1 = IV[3] + K3.d1
        K3.b1 = ROR(IV[7] XOR K3.c1, 12);   S11 = K3.c1 + S15
        S7 = ROR(K3.b1 XOR S11, 7);   K3.a1 = ROL(K3.d1,16) XOR 11
        w6 = K3.a1 - IV[3] - IV[7];   w7 = S3 - K3.a1 - K3.b1
    C0, third assignment and fourth value; D2, backwards from X7, X8, S7:
        X8 = C0.c1 - C0.d1;   C0.b1 = ROR(X4 XOR C0.c1, 12)
        D2.b1 = ROL(X7,7) XOR X8;   D2.c1 = ROL(D2.b1,12) XOR S7
        X13 = X8 - D2.c1

**Step M (the middle step; 21 lines, from X2).**

    D2, rest:
        D2.a1 = X2 - D2.b1 - W13;   D2.d1 = ROL(X13,8) XOR X2
        S13 = ROL(D2.d1,16) XOR D2.a1;   S8 = D2.c1 - D2.d1
        w12 = D2.a1 - S2 - S7
    K1, backwards from its outputs S9, S13:
        K1.c1 = S9 - S13;   K1.d1 = K1.c1 - IV[1]
        K1.a1 = ROL(K1.d1,16);   K1.b1 = ROR(IV[5] XOR K1.c1, 12)
        S1 = ROL(S13,8) XOR K1.d1;   S5 = ROR(K1.b1 XOR S9, 7)
        w2 = K1.a1 - IV[1] - IV[5];   w3 = S1 - K1.a1 - K1.b1
    K0, backwards from its outputs S4, S8:
        K0.b1 = ROL(S4,7) XOR S8;   K0.c1 = ROL(K0.b1,12) XOR IV[4]
        K0.d1 = K0.c1 - IV[0];   K0.a1 = ROL(K0.d1,16)
        S12 = S8 - K0.c1;   S0 = ROL(S12,8) XOR K0.d1
        w0 = K0.a1 - IV[0] - IV[4];   w1 = S0 - K0.a1 - K0.b1

**Step Y (the member; 10 lines, from y and the outer step, without X2).**

    C0, backwards from its b output y:
        Y8 = ROL(y,7) XOR C0.b1;   Y12 = Y8 - C0.c1
        Y0 = ROL(Y12,8) XOR C0.d1;   C0.a1 = Y0 - C0.b1 - w6
        X12 = ROL(C0.d1,16) XOR C0.a1
    D1, backwards from its outputs X11, X12, with its inputs S6, S11:
        D1.c1 = X11 - X12;   D1.b1 = ROR(S6 XOR D1.c1, 12)
        X6 = ROR(D1.b1 XOR X11, 7);   D1.d1 = D1.c1 - S11
        X1 = ROL(X12,8) XOR D1.d1

**Step T (the four words w8..w11; 12 lines).**

    C0, its first assignment:
        X0 = C0.a1 - X4 - w2
    D0, backwards from its outputs X0, X15:
        D0.d1 = ROL(X15,8) XOR X0;   D0.c1 = S10 + D0.d1
        X10 = D0.c1 + X15;   D0.b1 = ROR(S5 XOR D0.c1, 12)
        X5 = ROR(D0.b1 XOR X10, 7);   D0.a1 = ROL(D0.d1,16) XOR S15
        w8 = D0.a1 - S0 - S5;   w9 = X0 - D0.a1 - D0.b1
    D1, rest:
        D1.a1 = ROL(D1.d1,16) XOR S12;   w10 = D1.a1 - S1 - S6
        w11 = X1 - D1.a1 - D1.b1

Steps O, M, Y and T assign the eleven message words w0..w3 and w6..w12 (w5 is one of the six words; w4 = W4, w13 = W13, w14 = w15 = 0 are constants); fourteen of the sixteen words S0..S15 (S9 and S15 are two of the six); and X0, X1, X4, X5, X6, X8, X9, X10, X12, X13, X14 (X2 is the seventh word).

**Step S2.** w4' = W4' and w5' = w5 + W4 - W4', all modulo 2^32. For the constants of 3.2 that is w5' = w5 + fffffff8, the same as w5 - 8.

**Step S3.** A is the first 55 bytes of the little-endian encoding of w0..w15. B is the first 63 bytes of the encoding of the same words with w4, w5 replaced by w4', w5'.

*Round 1, forwards (24 lines).* The tests of 6.3 read values of round 1. They are computed from the names above by running C1 and C2 forwards and the first five assignments of E1 and of E3 for message A. Y3 and Y11 are the constants of Fact P for w4 = W4, and Y4 = y.

    C1, the call G(X1, X5, X9, X13; w3, w10):
        C1.a1 = X1 + X5 + w3;   C1.d1 = ROR(X13 XOR C1.a1, 16)
        C1.c1 = X9 + C1.d1;   C1.b1 = ROR(X5 XOR C1.c1, 12)
        Y1 = C1.a1 + C1.b1 + w10;   Y13 = ROR(C1.d1 XOR Y1, 8)
        Y9 = C1.c1 + Y13;   Y5 = ROR(C1.b1 XOR Y9, 7)
    C2, the call G(X2, X6, X10, X14; w7, w0):
        C2.a1 = X2 + X6 + w7;   C2.d1 = ROR(X14 XOR C2.a1, 16)
        C2.c1 = X10 + C2.d1;   C2.b1 = ROR(X6 XOR C2.c1, 12)
        Y2 = C2.a1 + C2.b1 + w0;   Y14 = ROR(C2.d1 XOR Y2, 8)
        Y10 = C2.c1 + Y14;   Y6 = ROR(C2.b1 XOR Y10, 7)
    E1 on A, with its c input Y11; third and fourth assignment in one line:
        E1.a1 = Y1 + Y6 + w12;   E1.d1 = ROR(Y12 XOR E1.a1, 16)
        E1.b1 = ROR(Y6 XOR (Y11 + E1.d1), 12);   E1.a2 = E1.a1 + E1.b1 + w5
    E3 on A, with its a input Y3 and w15 = 0; first and second in one line:
        E3.h1 = ROR(Y14 XOR (Y3 + Y4), 16);   E3.g1 = Y9 + E3.h1
        E3.f1 = ROR(Y4 XOR E3.g1, 12);   E3.e2 = (Y3 + Y4) + E3.f1 + w8

These 24 lines define nothing of the message. E3.h1, E3.g1, E3.f1, E3.e2 are the h1, g1, f1, e2 of 6.2, and the word z of Lemma A is C2.d1 XOR Y2.

**The order and the levels.** The 29 + 21 + 10 + 12 + 24 = 96 lines above are taken in the order in which they are printed: step O, step M, step Y, step T, then the lines of round 1. Give every line a *level*: the lines of step O are *outer* lines, those of step M *middle* lines, those of step Y *table* lines, and the 12 lines of step T and the 24 lines of round 1 are the 36 *trial* lines. Table C says, for every call, which line is each of its eight assignments: an entry is the name on the left of that line.

| Call | 1st | 2nd | 3rd | 4th | 5th | 6th | 7th | 8th |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K0 | w0 | K0.a1 | K0.d1 | K0.c1 | w1 | S0 | S12 | K0.b1 |
| K1 | w2 | K1.a1 | K1.d1 | K1.b1 | w3 | S1 | K1.c1 | S5 |
| K2 | K2.a1 | K2.d1 | K2.c1 | K2.b1 | S2 | S14 | S10 | S6 |
| K3 | w6 | K3.a1 | K3.c1 | K3.b1 | w7 | K3.d1 | S11 | S7 |
| D0 | w8 | D0.a1 | D0.c1 | D0.b1 | w9 | D0.d1 | X10 | X5 |
| D1 | w10 | D1.a1 | D1.d1 | D1.b1 | w11 | X1 | D1.c1 | X6 |
| D2 | w12 | S13 | S8 | D2.c1 | D2.a1 | D2.d1 | X13 | D2.b1 |
| D3 | S3 | D3.a1 | D3.c1 | S4 | D3.b1 | X14 | X9 | X4 |
| C0 | X0 | X12 | X8 | C0.b1 | C0.a1 | Y0 | Y12 | Y8 |
| C1 | C1.a1 | C1.d1 | C1.c1 | C1.b1 | Y1 | Y13 | Y9 | Y5 |
| C2 | C2.a1 | C2.d1 | C2.c1 | C2.b1 | Y2 | Y14 | Y10 | Y6 |

The inputs, the message words and the outputs of the eleven calls are those of Section 1: K0 has inputs (IV[0], IV[4], IV[0], 0) and outputs (S0, S4, S8, S12), K1 has (IV[1], IV[5], IV[1], 0) and (S1, S5, S9, S13), K2 has (IV[2], IV[6], IV[2], 55) and (S2, S6, S10, S14), K3 has (IV[3], IV[7], IV[3], 11) and (S3, S7, S11, S15); D0 maps (S0, S5, S10, S15) to (X0, X5, X10, X15), D1 maps (S1, S6, S11, S12) to (X1, X6, X11, X12), D2 maps (S2, S7, S8, S13) to (X2, X7, X8, X13), D3 maps (S3, S4, S9, S14) to (X3, X4, X9, X14); C0, C1, C2 map (X0, X4, X8, X12), (X1, X5, X9, X13), (X2, X6, X10, X14) to (Y0, Y4, Y8, Y12), (Y1, Y5, Y9, Y13), (Y2, Y6, Y10, Y14). The remaining eight lines are E1.a1, E1.d1, E1.b1, E1.a2, which are the first, the second, the third with the fourth, and the fifth assignment of E1 for message A, and E3.h1, E3.g1, E3.f1, E3.e2, which are the first with the second, the third, the fourth and the fifth assignment of E3 for message A.

**Lemma T2.** (a) *Triangular.* In the printed order every line assigns a name that no earlier line assigns and that is neither one of the eight words nor a constant, and it reads only constants, the eight words (the eighth under the name Y4 in the lines of round 1) and names of earlier lines. A line of step O reads no word other than the six of the outer step, a line of step M reads neither y nor a name of step Y, and a line of step Y reads neither X2 nor a name of step M. Every line is one assignment of one call, solved for the name on its left; the two exceptions are the lines for E1.b1 and for E3.h1, each of which is two assignments with the first substituted into the second (c1 = Y11 + E1.d1 and e1 = Y3 + Y4 + w15), and the line for E3.e2 uses the same e1. By Table C the 96 lines are, each exactly once: the eight assignments of each of the eleven calls K0, K1, K2, K3, D0, D1, D2, D3, C0, C1, C2, with the inputs and the message words of Section 1 for block length 55, with w4 = W4, w13 = W13, w14 = w15 = 0, and with the constants X3, X7, X11, X15 as the a output of D3, the b output of D2, the c output of D1 and the d output of D0; and the first five assignments of E1 and of E3 for message A.

(b) *The calls.* For every choice of the eight words, the names of steps O, M, Y and T are the executions of the eleven calls as listed after Table C, each with its two message words; C0 has first, second, third and fourth value C0.a1, C0.d1, C0.c1, C0.b1 and outputs (Y0, y, Y8, Y12); and E1.a1, E1.d1, E1.b1, E1.a2 and E3.h1, E3.g1, E3.f1, E3.e2 are the first, second, fourth and fifth value of E1 and the second, third, fourth and fifth value of E3 in the compression of message A.

(c) *The levels.* An outer line is a function of the six words alone. A middle line is a function of the six words and X2 and does not depend on y. A table line is a function of the six words and y and does not depend on X2. In particular the sixteen message words of two trials of one context differ at most in w8, w9, w10, w11.

(d) *Admissible blocks.* Call a block (w0, .., w15) *admissible* if w4 = W4, w13 = W13, w14 = w15 = 0 and round 0 on it with block length 55 ends with (X[3], X[7], X[11], X[15]) equal to the four constants. The map of this section from the eight words to the block of A is a bijection onto the admissible blocks.

Proof. (a) is read off the displays: every name on a right side is a constant, one of the eight words or the left side of an earlier line, and the three statements about steps O, M and Y are seen by looking at the names their lines read. That each formula is the stated assignment of the stated call, solved for the name on its left, is seen by comparing it with the eight assignments of Section 2 and with the inputs, outputs and message words of the call. Table C has exactly one name in each of its 88 cells, the 88 names are different, and with the eight lines of E1 and E3 they are the 96 lines.

(b) An assignment of Section 2 is an equation between words. Solving it for one of its terms gives an equivalent equation: a = b + c + x holds exactly when x = a - b - c, and d = ROR(D XOR a, r) exactly when D = ROL(d, r) XOR a, all modulo 2^32. A line defines the name on its left by such an equation, so the equation holds between the names once the line has run, and by (a) no later line changes any of them. By (a) and Table C, for each of the eleven calls all eight of its assignments hold between the names, with the inputs and message words of Section 1. By Fact 1 the names are then the execution of that call. Where an output of a call is a constant (X3 for D3, X7 for D2, X11 for D1, X15 for D0), the assignments that contain that output hold with the constant in its place (the lines for D3.b1 and X14; for D2.b1; for D1.c1 and X6; for D0.d1 and X10), so the call has the constant as that output. For C0 the eighth assignment is the line for Y8, which contains y as the b output. The lines of E1 and E3 are the assignments of 6.2 for message A with Y11 and Y3 of Fact P; they compute forwards from names that are, by what was just shown, the values Y1, Y6, Y12 and Y4, Y9, Y14 of the compression of A.

(c) By induction over the printed order, with (a): an outer line reads only constants, the six words and outer lines, which are functions of the six words by induction; a middle line reads, besides these, only X2 and middle lines; a table line reads, besides outer names, only y and table lines. The message words w0..w7 and w12 are constants, one of the six words, outer lines (w6, w7) or middle lines (w0, w1, w2, w3, w12), and w13, w14, w15 are constants; only w8, w9, w10, w11 are trial lines.

(d) Every block that the construction outputs is admissible: by (b), round 0 with block length 55 leaves the state X of the names, in which X[3], X[7], X[11], X[15] are the constants, and the four pinned words are constants of the construction. *Injective:* by (b) each of the eight words is the value of its name in the compression of A (two values of the call C0 and one of the call D3, two words of the state S, a message word, a word of the state X and a word of the state Y), so it is a function of the block. *Onto:* take an admissible block, run its compression forwards with block length 55 and give every value its name. These forward values satisfy all the equations of (a): they are executions of the calls, the four outputs that are constants in the construction are those constants because the block is admissible, and Y3 and Y11 are the values of Fact P because C3 has the inputs X3, X7, X11, X15, W4, W13. Now run the lines on the eight words taken from the forward values. By induction over the lines, every line returns the forward value of its name: the names it reads have their forward values, the forward values satisfy the equation of the line, and an assignment has exactly one solution for any one of its terms when the others are given. So the words w0..w15 that the lines return are the block. QED.

*The same pairs as entry c66f230d.* Section 4 of that entry builds the block of A from the eight words (vc, vd, S11, S4, X13, X14, w0, y) by 72 lines that are the assignments of the nine calls K0..K3, D0..D3, C0 in another triangular order (its Lemmas S, F and Y). The argument of (d) applies to it as well, so both constructions are bijections onto the same set of admissible blocks, and B is determined by A in both: the 2^256 pairs are the same pairs, enumerated in another order. What differs is which of them a run of the search visits and in which groups. This remark is not used in any proof below.

*What Lemma T2 does not say.* Eleven of the trial lines are the line for E3.h1 and the ten it depends on (X0, D0.d1, D0.c1, X10, C2.a1, C2.d1, C2.c1, C2.b1, Y2, Y14). That no order with fewer exists was the answer of a solver in the search that produced the order; it is not used here and not claimed.

## 5. The half-collision

**Theorem.** For every choice of the seven words of a context (C0.c1, C0.d1, D3.d1, S15, S9, w5, X2) and of the word y, steps O, M, Y, T, S2 and S3 output two distinct messages A and B, of 55 and 63 bytes, whose complete 2-round digests agree on digest words 0, 2, 5 and 7; and in both compressions the b output of C0 is Y4 = y.

Proof. The sixteen words of steps O, M, Y and T have w14 = w15 = 0 and w13 = W13, whose top byte is zero. So bytes 55 to 63 of their encoding are zero: A, the first 55 bytes, is an honest 55-byte message whose zero-filled block is the sixteen words, and B is an honest 63-byte message that ends in eight zero bytes and whose zero-filled block is the sixteen words with w4, w5 replaced (3.1). Run round 0 on the words of A with block length 55. By Lemma T2 (b) the column calls leave the state S of the names and the diagonal calls, which act on disjoint state words, leave the state X of the names. So the state after round 0 has (X[3], X[7], X[11], X[15]) equal to the four constants, and w4 = W4, w13 = W13. By Lemma L the compression of B has the same state X after round 0. The two compressions share every word except w4, w5, so Lemma H gives the four digest words. C0 reads X0, X4, X8, X12 and w2, w6, which are the same in both compressions, and has b output y by Lemma T2 (b). The messages are distinct because their lengths differ. QED.

Distinct choices of the eight words give distinct messages A: C0.c1 and C0.d1 are values inside C0, D3.d1 is a value inside D3, S15 and S9 are state words after the column step of round 0, w5 is a message word, X2 is a state word after round 0 and y is a state word after the column step of round 1, and all of them are functions of the message (Lemma T2 (d)). The construction yields 2^256 different half-colliding pairs.
