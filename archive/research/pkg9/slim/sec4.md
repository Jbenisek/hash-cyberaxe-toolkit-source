    w4 = W4    a1=7ffffff8 d1=7af83f3a c1=befb9f3a b1=01200183
               a2=8127c181 d2=bbfbdffe c2=7af77f38 b2=76f7aefd
    w4 = W4'   a1=80000000 d1=8500c0c5 c1=c90420c5 b1=fed77e78
               a2=7edf3e7e d2=bbfbdffe c2=850000c3 b2=76f7aefd

**Fact P.** The two executions give the same d output bbfbdffe and the same b
output 76f7aefd. They differ in the a output (8127c181, 7edf3e7e) and in the c
output (7af77f38, 850000c3); a finite computation on the displayed constants.

**3.3 Half of the digest does not see the difference.**

**Lemma H.** Take two executions of the 2-round compression that have the same
state X after round 0 and the same message words except w4 and w5. Suppose
(X[3], X[7], X[11], X[15]) = (X3, X7, X11, X15), w13 = W13, and w4 is W4 in the
first execution and W4' in the second. Then the two digests agree on digest
words 0, 2, 5 and 7.

Proof. C0, C1, C2 read neither w4 nor w5 and act on identical states, so they
leave identical values. C3 reads state words 3, 7, 11, 15 and the words w4,
w13; by Fact P it leaves the same v[7] and v[15] and may differ only in v[3]
and v[11], so Y agrees except possibly in Y[3] and Y[11]. E0 reads Y[0], Y[5],
Y[10], Y[15] and w1, w11, E2 reads Y[2], Y[7], Y[8], Y[13] and w9, w14, none
of them Y[3], Y[11], w4 or w5, so Z[0], Z[2], Z[5], Z[7], Z[8], Z[10], Z[13],
Z[15] are identical; by Section 1 digest words 0, 2, 5, 7 use only those. QED.

The remaining digest words o[1] = Z[1] XOR Z[9], o[3] = Z[3] XOR Z[11],
o[4] = Z[4] XOR Z[12] and o[6] = Z[6] XOR Z[14] come from E1 and E3 only. The
**residual** of a pair is the 128-bit string R = (o[1] XOR o'[1], o[3] XOR
o'[3], o[4] XOR o'[4], o[6] XOR o'[6]); it is a collision exactly when R = 0.

## 4. Construction: the message from eight words, in three levels

The construction places the six constants of 3.2 where Lemma H needs them,
keeps w14 = w15 = 0, and gives the word Y4, the b output of C0, a prescribed
value. Its input is eight free words. Six of them belong to an *outer step*:

    C0.c1, C0.d1, D3.d1, S15, S9, w5,

the seventh is X2, a word of the state after round 0; the six words and X2
together are a *context*. The eighth is y, the value that Y4 is to have. The
state words X3, X7, X11, X15 are the constants, w4 = W4, w13 = W13 and
w14 = w15 = 0.

*Names.* For a call TAG of Section 1, TAG.a1, TAG.d1, TAG.c1 and TAG.b1 are its
first, second, third and fourth value (Section 2); its other four values carry
the names of the state they are written to (S, X and Y of Section 1). In the
names of entry c66f230d, C0.c1 = vc, C0.d1 = vd, C0.b1 = vb and C0.a1 = va.

The construction has four steps. Step O reads the six words of the outer step,
step M reads X2 in addition, step Y reads the six words and y and not X2, and
step T reads everything; all arithmetic is modulo 2^32. In the program steps O
and M are `outer` and `middle` ("Step S1"), step Y `member`, step T `trial`.

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

**Step S2.** w4' = W4' and w5' = w5 + W4 - W4', all modulo 2^32. For the
constants of 3.2 that is w5' = w5 + fffffff8, the same as w5 - 8.

**Step S3.** A is the first 55 bytes of the little-endian encoding of w0..w15,
B the first 63 bytes of the same encoding with w4, w5 replaced by w4', w5'.

*Round 1, forwards (24 lines).* The tests of 6.3 read values of round 1,
computed from the names above by C1 and C2 forwards and the first five E1 and
E3 assignments for A; Y3, Y11 are the Fact P constants for w4 = W4, and Y4 = y.

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

These 24 lines define nothing of the message. E3.h1, E3.g1, E3.f1, E3.e2 are
the h1, g1, f1, e2 of 6.2, and the word z of Lemma A is C2.d1 XOR Y2.

**The order and the levels.** The 29 + 21 + 10 + 12 + 24 = 96 lines above are
taken in the printed order: step O, M, Y, T, then round 1. The *level* of a
line is *outer* for step O, *middle* for step M, *table* for step Y, and
*trial* for step T and round 1 (12 + 24 = 36 lines). Table C says, for every
call, which line is each of its eight assignments: the name on its left.

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

**Lemma T2.** (a) *Triangular.* In the printed order every line assigns a name
that no earlier line assigns and that is neither one of the eight words nor a
constant, and reads only constants, the eight words (the eighth as Y4 in the
round-1 lines) and names of earlier lines. A step O line reads no word but the
six of the outer step, a step M line reads neither y nor a step Y name, and a
step Y line reads neither X2 nor a step M name. Every line is one assignment of
one call solved for the name on its left, except the lines for E1.b1 and for
E3.h1, each two assignments with the first substituted into the second
(c1 = Y11 + E1.d1 and e1 = Y3 + Y4 + w15), the same e1 being used by the line
for E3.e2. By Table C the 96 lines are, each exactly once: the eight
assignments of each of the eleven calls K0..K3, D0..D3, C0, C1, C2, with the
inputs and the message words of Section 1 for block length 55, with w4 = W4,
w13 = W13, w14 = w15 = 0, and with X3, X7, X11, X15 as the a output of D3, the
b of D2, the c of D1 and the d of D0; and the first five assignments of E1 and
of E3 for message A.

(b) *The calls.* For every choice of the eight words, the names of steps O, M,
Y and T are the executions of the eleven calls of Section 1, each with its two
message words; C0 has first, second, third and fourth value C0.a1, C0.d1,
C0.c1, C0.b1 and outputs (Y0, y, Y8, Y12); and E1.a1, E1.d1, E1.b1, E1.a2 and
E3.h1, E3.g1, E3.f1, E3.e2 are the first, second, fourth and fifth value of E1
and the second, third, fourth and fifth value of E3 in the compression of A.

(c) *The levels.* An outer line is a function of the six words alone. A middle
line is a function of the six words and X2 and does not depend on y. A table
line is a function of the six words and y and does not depend on X2. In
particular the sixteen message words of two trials of one context differ at
most in w8, w9, w10, w11.

(d) *Admissible blocks.* Call a block (w0, .., w15) *admissible* if w4 = W4,
w13 = W13, w14 = w15 = 0 and round 0 on it with block length 55 ends with
(X[3], X[7], X[11], X[15]) equal to the four constants. The map of this section
from the eight words to the block of A is a bijection onto the admissible
blocks.

Proof. (a) is read off the displays, by comparing each formula with the eight
assignments of Section 2 and the inputs, outputs and message words of its call,
and from Table C: one name in each of its 88 cells, all different, which with
the eight lines of E1 and E3 are the 96 lines.

(b) By Fact 1 an assignment solved for one of its terms is an equivalent
equation, so a line's equation holds between the names once it has run, and by
(a) no later line changes them. By (a) and Table C all eight assignments of
each of the eleven calls hold between the names with the inputs and message
words of Section 1, so by Fact 1 the names are the execution of that call.
Where an output is a constant (X3 for D3, X7 for D2, X11 for D1, X15 for D0)
the assignments containing it hold with the constant in its place, so the call
has it as that output, and for C0 the eighth assignment is the line for Y8,
which contains y as the b output. The lines of E1 and E3 are the assignments
of 6.2 for message A with Y11 and Y3 of Fact P, computed forwards from the
values Y1, Y6, Y12 and Y4, Y9, Y14 of the compression of A.

(c) By induction over the printed order, with (a): an outer line reads only
constants, the six words and outer lines; a middle line reads, besides these,
only X2 and middle lines; a table line reads, besides outer names, only y and
table lines. Of the message words, w0..w7 and w12 are constants, one of the six
words, outer lines (w6, w7) or middle lines (w0..w3, w12), and w13, w14, w15
are constants; only
