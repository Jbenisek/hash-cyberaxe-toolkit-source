# A free half-collision and a search inside one class for 2-round BLAKE3

The scalar below is `time_log2` under `collision-frontier-v5`. Memory is a
separately reported resource bound.

This exploratory package targets blake3-r2-prefix-v1. It has an exact part and
a heuristic part, and it keeps them apart.

**Exact part.** An explicit construction maps any nine 32-bit words to a
60-byte message A and a 62-byte message B whose complete 2-round BLAKE3-256
digests agree on digest words 0, 2, 5 and 7, that is on 128 of the 256 digest
bits. There is no search in this construction and no probability: it holds for
all 2^288 choices of the nine words (Sections 2 to 5). A second exact
construction enumerates such pairs while it holds one internal word of round
1, called Y4, inside a set of {{members}} values, the *class* (Section 6.1).

**Heuristic part.** A collision needs the other four digest words to agree as
well. The algorithm searches 2^{{T}} such pairs, all with Y4 in the class, for
one where they do. The search has no table that grows with the number of
trials and does no sorting or lookup. Seven trials are evaluated in one
256-bit word, in two stages. Every batch runs stage A, which tests
{{rule_conditions}} bit conditions on one internal word of every trial (rule A). Only
a batch in which a trial satisfies rule A runs stage 2, which tests a 32-bit
condition that every collision satisfies. A batch in which no trial
satisfies rule A is dropped; a trial that fails rule A is examined further
only if another trial of its batch satisfies it, and Section 7 does not
count such a trial. A trial is charged {{charge}} primitive operations, memory loads
included. Three heuristics are declared: H1, that a trial satisfies rule A
and completes the collision with probability at least 2^-{{T1}}; H2, that a
budget on the passes of the second test suffices; and H3, that at most
{{stage2_share_words}} of the batches run stage 2. Under the three the search
succeeds with probability at least 0.39. Total
charged time is below 2^{{total_bound}} target-compression units, so the claimed
scalar is {{time_log2}}. The search needs less than 2^{{online_log2}} bytes of memory; the
declared 2^{{memory_log2}} bytes also cover the computations by which the constants
and the class were selected (Sections 6 to 9).

The rate in H1 is an assumption: 2^{{F}} = {{factor}} times the rate of a uniform
128-bit value. It is not read off single digest words. Section 10 describes
what it is set against. The remaining half of the digest depends on seven
words, one of which is Y4. Under the model that the other six behave like
independent uniform words over the trials, the rate is the number of
solutions of a fixed system of equations, and that number is counted: an
enumeration without sampling gives {{exact_total}} times 2^-128 for Y4 in the
class, as a lower bound because part of the enumeration is left out. Rule A
is not implied by a collision: some solutions violate it and are lost. The
figure that the claim uses is therefore smaller. It leaves out every part
of the count for which a solver found a solution that violates rule A,
{{rule_lost}} in all, and is {{rule_count}}. H1
assumes {{factor}} times, {{exact_over_factor}} times less. {{intro_choice_sentence}} The counting
program is not part of the package, and it and all its checks are the
participant's. The model was compared
with real messages only on events of probability about 2^-32 and above. The
organizer-run experiments measure neither the model nor the factor. With
the uniform rate in place of {{factor}} times it, the same search needs 2^127
trials and gives time_log2 = {{uniform_time}}.

No full 2-round collision is exhibited, and the search is far beyond feasible
computation. What is exhibited, and checked by the organizer's own runner, is
the exact half-collision on trials of the search and a toy-scale run of the
class search, without the two tests and the packing that set the cost of a
trial. The program the organizer runs also contains the packed two-stage
batch, a machine that counts its operations and loads, and a self-test of
that count (Section 6.5). Those counts are the program's own; the organizer
does not check them.

## 1. Exact complete hash on the messages used

H is unkeyed BLAKE3-256 with only rounds 0 and 1 kept in every compression.
Every message produced has n = 60 or n = 62 bytes. A message of n <= 64 bytes
is one chunk consisting of one block, with no parent node, so H evaluates
exactly one compression. The block is the message followed by 64 - n zero
bytes, used only for loading words. The compression has flags
CHUNK_START | CHUNK_END | ROOT = 11, true block length n, and chunk counter
and root-output counter both zero. There is no key and no derivation flag.

Decode the zero-filled block into sixteen little-endian 32-bit words w[0..15].
The IV is

    6a09e667 bb67ae85 3c6ef372 a54ff53a
    510e527f 9b05688c 1f83d9ab 5be0cd19.

Initialize v[0..7] = IV, v[8..11] = IV[0..3] and v[12..15] = (0, 0, n, 11).
The block length n is the initial value of v[14] and enters nowhere else. All
additions and subtractions on state and message words are modulo 2^32. ROR and
ROL rotate a 32-bit word. G(a,b,c,d,x,y) is

    v[a] = v[a]+v[b]+x;  v[d] = ROR(v[d] XOR v[a],16)
    v[c] = v[c]+v[d];    v[b] = ROR(v[b] XOR v[c],12)
    v[a] = v[a]+v[b]+y;  v[d] = ROR(v[d] XOR v[a],8)
    v[c] = v[c]+v[d];    v[b] = ROR(v[b] XOR v[c],7).

A round is four column calls followed by four diagonal calls on the current
schedule s, and between rounds s is replaced by s[P[i]] with
P = (2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8). Written out for the two retained
rounds, with names used throughout:

    round 0   K0 = G(0,4,8,12, w0, w1)     K1 = G(1,5,9,13, w2, w3)
              K2 = G(2,6,10,14, w4, w5)    K3 = G(3,7,11,15, w6, w7)
              D0 = G(0,5,10,15, w8, w9)    D1 = G(1,6,11,12, w10, w11)
              D2 = G(2,7,8,13, w12, w13)   D3 = G(3,4,9,14, w14, w15)
    round 1   C0 = G(0,4,8,12, w2, w6)     C1 = G(1,5,9,13, w3, w10)
              C2 = G(2,6,10,14, w7, w0)    C3 = G(3,7,11,15, w4, w13)
              E0 = G(0,5,10,15, w1, w11)   E1 = G(1,6,11,12, w12, w5)
              E2 = G(2,7,8,13, w9, w14)    E3 = G(3,4,9,14, w15, w8)

S denotes the state after K0..K3, X the state after round 0, Y the state after
C0..C3 and Z the final state. The compression output is
o[i] = Z[i] XOR Z[i+8] and o[i+8] = Z[i+8] XOR IV[i] for i = 0..7. The digest
H(m) is the first 32 output bytes, LE4(o[0]) || ... || LE4(o[7]).

This is the complete hash of the target profile restricted to inputs of 60
and 62 bytes: standard IV, standard flags, true block length, both retained
rounds with the standard permutation, standard feed-forward and the full
256-bit digest. It is not a free-start, chosen-IV, compression-only or
truncated-output setting.

## 2. Inverting one G call

Consider one call G(a,b,c,d,x,y) with input values A, B, C, D and name its
eight assignments

    a1 = A + B + x           d1 = ROR(D XOR a1, 16)
    c1 = C + d1              b1 = ROR(B XOR c1, 12)
    a2 = a1 + b1 + y         d2 = ROR(d1 XOR a2, 8)
    c2 = c1 + d2             b2 = ROR(b1 XOR c2, 7).

Its outputs are (a2, b2, c2, d2).

**Fact 1.** Reading the assignments backwards,

    b1 = ROL(b2, 7) XOR c2       c1 = c2 - d2       d1 = ROL(d2, 8) XOR a2
    B  = ROL(b1, 12) XOR c1      C  = c1 - d1
    a1 = ROL(d1, 16) XOR D       y  = a2 - a1 - b1      x = a1 - A - B.

So the four outputs determine b1, c1, d1 and the inputs B and C; and whenever
values A, B, C, D, a2, b2, c2, d2 satisfy the two equations for B and C, the
words x and y given by the last line make the call map (A,B,C,D) to
(a2,b2,c2,d2). Each line is one assignment solved for another of its terms.

## 3. Three ingredients

**3.1 The length is cancelled inside K2.** K2 is the only call of round 0 that
reads the block length n, the initial value of v[14], and it overwrites that
word; it is also the only call of round 0 that reads w4 and w5. Its inputs are
(IV[2], IV[6], IV[2], n). Put K = IV[2] + IV[6] = 5bf2cd1d. For lengths 60 and
62, whose XOR is 2, define for any w4, w5

    w4' = ((K + w4) XOR 2) - K        w5' = w5 + w4 - w4'.

**Lemma L.** K2 with block length 60 and words (w4, w5) leaves the same four
state words as K2 with block length 62 and words (w4', w5').

Proof. Let a1 = K + w4. In the second execution the first assignment gives
K + w4' = a1 XOR 2, so the second gives ROR(62 XOR a1 XOR 2, 16) =
ROR(60 XOR a1, 16), the same d1. The third and fourth depend only on d1 and
constants. The fifth gives (a1 XOR 2) + b1 + w5' = a1 + b1 + w5 because
w5' - w5 = w4 - w4' = a1 - (a1 XOR 2). The last three depend only on values
already shown equal. QED.

Hence two messages of 60 and 62 bytes that share every word except w4, w5,
related as above, have the same state S after the column step and the same
state X after round 0, since no other call of round 0 reads v[14], w4 or w5
before K2 has made the states equal. For both to be honest byte strings of
their lengths, word 15 must be zero in both: bytes 60..63 are zero fill for
the 60-byte message, and the 62-byte message is chosen to end in two zero
bytes, with bytes 62, 63 zero fill. This is the only constraint on the words.

**3.2 A pinned call C3.** Fix the six constants

    X3 = {{X3}}   X7 = {{X7}}   X11 = {{X11}}   X15 = {{X15}}
    W4 = {{W4}}   W13 = {{W13}}

Then K + W4 = {{KW4}} and W4' = ((K + W4) XOR 2) - K = {{W4B}}, so
W4 - W4' = {{delta}}{{delta_note}}. Evaluate C3 = G(3,7,11,15, w4, W13)
on the inputs (X3, X7, X11, X15) with w4 = W4 and with w4 = W4':

{{factp_table}}

**Fact P.** The two executions give the same d output {{P_d2}} and the same b
output {{P_b2}}. They differ in the a output ({{Y3}}, {{Y3B}}) and in the c
output ({{Y11}}, {{Y11B}}). This is a finite computation on the displayed
constants.

**3.3 Half of the digest does not see the difference.**

**Lemma H.** Take two executions of the 2-round compression that have the same
state X after round 0 and the same message words except w4 and w5. Suppose
(X[3], X[7], X[11], X[15]) = (X3, X7, X11, X15), w13 = W13, and w4 is W4 in the
first execution and W4' in the second. Then the two digests agree on digest
words 0, 2, 5 and 7.

Proof. C0, C1, C2 read neither w4 nor w5 and act on identical states, so they
leave identical values in both executions. C3 reads state words 3, 7, 11, 15
and the words w4, w13; by Fact P it leaves the same v[7] and v[15] in both
executions and may differ only in v[3] and v[11]. So Y agrees except possibly
in Y[3] and Y[11]. E0 reads Y[0], Y[5], Y[10], Y[15] and w1, w11. E2 reads
Y[2], Y[7], Y[8], Y[13] and w9, w14. None of these is Y[3], Y[11], w4 or w5, so
E0 and E2 produce identical outputs Z[0], Z[5], Z[10], Z[15] and Z[2], Z[7],
Z[8], Z[13]. Finally o[0] = Z[0] XOR Z[8], o[2] = Z[2] XOR Z[10],
o[5] = Z[5] XOR Z[13] and o[7] = Z[7] XOR Z[15] use only those eight words.
QED.

The remaining digest words o[1] = Z[1] XOR Z[9], o[3] = Z[3] XOR Z[11],
o[4] = Z[4] XOR Z[12] and o[6] = Z[6] XOR Z[14] are computed from the outputs
of E1 and E3 only. The **residual** of a pair is the 128-bit string
R = (o[1] XOR o'[1], o[3] XOR o'[3], o[4] XOR o'[4], o[6] XOR o'[6]). The pair
is a collision exactly when R = 0.

## 4. Construction: the message from the state after round 0

Round 0 with the fixed initial state is invertible: the state X after it
determines the sixteen message words. The construction uses this to place the
six constants of 3.2 where Lemma H needs them. Its input is nine free words

    X1, X2, X5, X6, X9, X10, X12, X13, X14.

**Step S1.** Set X3, X7, X11, X15 to the constants, w4 = W4, w13 = W13,
w15 = 0, and compute in this order, all arithmetic modulo 2^32:

    constants of K2:  p = K + W4;  q = ROR(p XOR 60, 16);  r = q + IV[2];
                      u = ROR(r XOR IV[6], 12)
    from D1:   b = ROL(X6,7) XOR X11;   c = X11 - X12;   d = ROL(X12,8) XOR X1
               S6 = ROL(b,12) XOR c;    S11 = c - d;     keep b, d as bD1, dD1
    link:      S10 = u XOR ROL(S6,7)
    from D0:   b = ROL(X5,7) XOR X10;   c = X10 - X15;   S5 = ROL(b,12) XOR c
               d = c - S10;             X0 = d XOR ROL(X15,8)
               keep b, d as bD0, dD0
    K2:        S14 = S10 - r;   S2 = ROL(S14,8) XOR q;   w5 = S2 - p - u
    from D3:   d = ROL(X14,8) XOR X3;  a = ROL(d,16) XOR S14;  b = X3 - a - w15
               X4 = ROR(b XOR X9, 7);   c = X9 - X14
               S4 = ROL(b,12) XOR c;    S9 = c - d;      keep a as aD3
    K1:        (S1, S13, w2, w3) = COL(1, S5, S9, 0)
    from D2:   d = ROL(X13,8) XOR X2;  a = ROL(d,16) XOR S13;  b = X2 - a - w13
               X8 = b XOR ROL(X7,7);    c = X8 - X13
               S7 = ROL(b,12) XOR c;    S8 = c - d;      w12 = a - S2 - S7
    K0:        (S0, S12, w0, w1) = COL(0, S4, S8, 0)
    K3:        (S3, S15, w6, w7) = COL(3, S7, S11, 11)
    words:     a = ROL(dD0,16) XOR S15;  w8 = a - S0 - S5;   w9 = X0 - a - bD0
               a = ROL(dD1,16) XOR S12;  w10 = a - S1 - S6;  w11 = X1 - a - bD1
               w14 = aD3 - S3 - S4

where COL(j, sb, sc, d0) inverts column call Kj from its b and c outputs:

    b1 = ROL(sb,7) XOR sc;   c1 = ROL(b1,12) XOR IV[4+j];   sd = sc - c1
    d1 = c1 - IV[j];         a1 = ROL(d1,16) XOR d0
    x = a1 - IV[j] - IV[4+j];   sa = ROL(sd,8) XOR d1;   y = sa - a1 - b1
    result (sa, sd, x, y).

**Step S2.** w4' = W4' and w5' = w5 + W4 - W4', all modulo 2^32. For the
constants of 3.2 that is w5' = w5 + {{delta}}, the same as w5 {{delta_signed}}.

**Step S3.** A is the first 60 bytes of the little-endian encoding of
w0..w15. B is the first 62 bytes of the encoding of the same words with w4, w5
replaced by w4', w5'.

**Lemma S.** For every choice of the nine free words, running round 0 forward
on the words of step S1 with block length 60 gives the column-step state
S[0..15] and the state X[0..15] of step S1, in particular
(X[3], X[7], X[11], X[15]) equal to the four constants; and w4 = W4,
w13 = W13, w15 = 0.

Proof. The three word values hold by definition. The rest is Fact 1 applied
call by call; every quantity is defined before it is used.

- D1 has outputs (X1, X6, X11, X12). Fact 1 gives its b and c inputs as the
  S6 and S11 of step S1, and its words as w10, w11 once its a and d inputs
  S1, S12 are known.
- D0 has outputs (X0, X5, X10, X15). Its b input is S5 by Fact 1. Its c input
  is c - d with d = ROL(X15,8) XOR X0; step S1 chooses X0 so that this equals
  S10. Its words are w8, w9 by Fact 1.
- D3 has outputs (X3, X4, X9, X14) and d input S14. With d and a as in step
  S1, Fact 1 gives y = X3 - a - b1 where b1 = ROL(X4,7) XOR X9; step S1
  chooses X4 so that b1 equals X3 - a - w15, hence y = w15 = 0. Its b and c
  inputs are S4, S9 and its first word is w14.
- D2 has outputs (X2, X7, X8, X13) and d input S13. In the same way step S1
  chooses X8 so that its second word is w13 = W13; its b and c inputs are
  S7, S8 and its first word is w12.
- K2 has inputs (IV[2], IV[6], IV[2], 60) and first word W4, so its first
  four assignments give p, q, r, u. Its outputs must be (S2, S6, S10, S14):
  the last assignment requires u XOR S10 = ROL(S6,7), which is the link line;
  the seventh requires S10 = r + S14; the sixth requires
  q XOR S2 = ROL(S14,8); the fifth gives w5 = S2 - p - u.
- K1, K0 and K3 have inputs (IV[j], IV[4+j], IV[j], d0) with d0 = 0, 0, 11
  and prescribed b and c outputs. COL is Fact 1 for that situation: it returns
  the a and d outputs and the two words.

So the sixteen words map the initial state to S under the column step, and S
to X under the diagonal step. QED.

## 5. The half-collision

**Theorem.** For every choice of the nine free words, steps S1 to S3 output
two distinct messages A and B, of 60 and 62 bytes, whose complete 2-round
digests agree on digest words 0, 2, 5 and 7.

Proof. By Lemma S, word 15 is zero, so A is an honest 60-byte message and B
an honest 62-byte message ending in two zero bytes, and the compression of A
is the one analysed in Lemma S. By Lemma L the compression of B has the same
state X after round 0. The two compressions share every word except w4, w5,
and satisfy the hypotheses of Lemma H by Lemma S and step S2. Lemma H gives
the four digest words. The messages are distinct because their lengths
differ. QED.

Distinct choices of the nine words give distinct states X and so distinct
messages A: the construction yields 2^288 different half-colliding pairs.

## 6. The search for the other half

**6.1 Trials.** A *context* is the output of step S1 for some nine words: the
words w0..w15 and the states S and X. A trial replaces seven message words of
a context, w6..w11 and w14, so that one word of round 1 takes a prescribed
value. That word is Y4, the b output of C0.

*The class.* The first message word of E3 is w15 = 0, so the first assignment
of E3 is e1 = Y3 + Y4 for message A and e1' = Y3' + Y4 for message B, with
Y3 = {{Y3}} and Y3' = {{Y3B}} from Fact P. Put DY3 = Y3' - Y3 = {{DY3}}.
The second assignment is h1 = ROR(Y14 XOR e1, 16), so the XOR difference
between A and B of E3's first-half d value is

    eta = h1 XOR h1' = ROR((Y3 + Y4) XOR (Y3 + Y4 + DY3), 16),

a function of Y4 alone. Fix eta = {{eta}}. The *class* is the set of all
words Y4 that give this eta.

**Lemma Q.** The class is the set of all Y4 with

    ((Y3 + Y4) AND {{qmask}}) = {{qvalue}}.

It has {{members}} members: the {{free_bits}} bits of e1 = Y3 + Y4 at the positions
where {{qmask}} has a zero are free, bit 31 among them, and Y4 = e1 - Y3.

Proof. Put x = ROL(eta,16) = {{x}} and m = x AND 7fffffff = {{qmask}}.
{{x_bit31_sentence}} Y4 is in the class exactly when e1 XOR (e1 + DY3) = x,
that is when (e1 XOR x) - e1 = DY3 modulo 2^32. For words e and x,
(e XOR x) - e is, modulo 2^32, the sum over the bits i of x of 2^i where bit
i of e is 0 and of -2^i where it is 1, which is 2 ((NOT e) AND x) - x; for
i = 31 the two signs give the same word. So the condition is
2 ((NOT e1) AND x) = DY3 + x modulo 2^32. Here DY3 + x = {{qsum}} modulo
2^32, which is even. Doubling modulo 2^32 discards bit 31 of
(NOT e1) AND x, so the condition does not involve bit 31 of e1, and on the
other bits it is ((NOT e1) AND m) = {{qsum}} >> 1 = {{qhalf}}. All bits of
{{qhalf}} lie in m, so this fixes the {{fixed_bits}} bits of e1 on m to
(e1 AND m) = (NOT {{qhalf}}) AND m = {{qvalue}} and leaves the other {{free_bits}} bits
free. QED.

Member number k of the class, for 0 <= k < {{members_plain}}, is the Y4 whose e1 has
the bits of k at its {{free_bits}} free positions, in increasing order of position.

*The trial.* A **trial** is a context, a word alpha and a member y of the
class. Its message words are those of the context with w6..w11 and w14
replaced as follows. The lines are executed in order; S, X and w on the right
are the context's values until a line assigns the name, and the new value
from then on. bD1 and aD3 are the values kept in step S1.

    D0 family, parameter alpha:
        c = alpha - X15;   dD0 = c - S10;   X0 = ROL(X15,8) XOR dD0
        bD0 = ROR(S5 XOR c, 12);   X5 = ROR(bD0 XOR alpha, 7);   X10 = alpha
    C0 backwards from its b output y:
        pa = X0 + X4 + w2;   pd = ROR(X12 XOR pa, 16);   pc = X8 + pd
        pb = ROR(X4 XOR pc, 12);   Y8 = ROL(y,7) XOR pb;   Y12 = Y8 - pc
        Y0 = ROL(Y12,8) XOR pd;   w6 = Y0 - pa - pb
    K3 with its b output S7 kept:
        ka = IV[3] + IV[7] + w6;   kd = ROR(ka XOR 11, 16);   kc = IV[3] + kd
        kb = ROR(IV[7] XOR kc, 12);   S11 = ROL(S7,7) XOR kb;   S15 = S11 - kc
        S3 = ROL(S15,8) XOR kd;   w7 = S3 - ka - kb
    D1, D0 and D3 with the new S11, S15 and S3:
        d = (X11 - X12) - S11;   X1 = ROL(X12,8) XOR d
        a = ROL(d,16) XOR S12;   w10 = a - S1 - S6;   w11 = X1 - a - bD1
        a = ROL(dD0,16) XOR S15;   w8 = a - S0 - S5;   w9 = X0 - a - bD0
        w14 = aD3 - S3 - S4

The names assigned are X0, X5, X10, then S11, S15, S3, then X1, and the seven
words. Everything else, S7 in particular, keeps the context's value.

**Lemma F.** (a) For every alpha and every word S15, D0 with inputs
(S0, S5, S10, S15) and the words (w8, w9) above has outputs
(X0, X5, alpha, X15), and X0, X5 do not depend on S15. (b) For every word
S11, D1 with inputs (S1, S6, S11, S12) and the words (w10, w11) above has
outputs (X1, X6, X11, X12), where X6, X11, X12 are the context's. (c) For
every word S3, D3 with inputs (S3, S4, S9, S14) and the words (w14, w15) has
the context's outputs (X3, X4, X9, X14).

Proof. (a) The first assignment gives S0 + S5 + w8 = a; the second
ROR(S15 XOR a, 16) = dD0; the third S10 + dD0 = c; the fourth bD0; the fifth
a + bD0 + w9 = X0; the sixth ROR(dD0 XOR X0, 8) = X15 by the definition of X0;
the seventh c + X15 = alpha; the eighth X5. The lines that define X0 and X5
do not contain S15. (b) Put c = X11 - X12. In step S1, bD1 = ROL(X6,7) XOR X11
and S6 = ROL(bD1,12) XOR c, and none of X6, X11, X12, S6 is assigned by the
trial. The first assignment gives S1 + S6 + w10 = a; the second
ROR(S12 XOR a, 16) = d; the third S11 + d = c; the fourth
ROR(S6 XOR c, 12) = bD1; the fifth a + bD1 + w11 = X1; the sixth
ROR(d XOR X1, 8) = X12 by the definition of X1; the seventh c + X12 = X11;
the eighth ROR(bD1 XOR X11, 7) = X6. (c) D3 reads S3 only in its first
assignment, which gives S3 + S4 + w14 = aD3, the value it has in the context.
Its other inputs and w15 are the context's, so its outputs are. QED.

**Lemma Y.** For every word y, C0 with inputs (X0, X4, X8, X12) and words
(w2, w6) has b output y and d output Y12.

Proof. C0 reads w6 only in its fifth assignment. Its first four assignments
give pa, pd, pc, pb. The fifth gives pa + pb + w6 = Y0; the sixth
ROR(pd XOR Y0, 8) = Y12 by the definition of Y0; the seventh pc + Y12 = Y8;
the eighth ROR(pb XOR Y8, 7) = y by the definition of Y8. QED.

**Lemma K.** For every word w6, K3 with words (w6, w7) has outputs
(S3, S7, S11, S15): its b output is the S7 of the context, and its a, c and d
outputs are the new S3, S11 and S15.

Proof. K3 has inputs (IV[3], IV[7], IV[3], 11). Its first four assignments
give ka, kd, kc, kb. The fifth gives ka + kb + w7 = S3; the sixth
ROR(kd XOR S3, 8) = S15 by the definition of S3; the seventh kc + S15 = S11;
the eighth ROR(kb XOR S11, 7) = S7 by the definition of S11. QED.

**Lemma T.** For every trial, round 0 with block length 60 maps the trial's
words to the context's column-step state with S3, S11, S15 replaced, and to
the context's state X with X0, X1, X5, X10 replaced, as assigned above. So
(X[3], X[7], X[11], X[15]) are the four constants and w4 = W4, w13 = W13,
w15 = 0. In round 1, C0 has b output Y4 = y, a member of the class. The
messages A and B built from the trial's words by steps S2 and S3 have complete
2-round digests that agree on digest words 0, 2, 5 and 7.

Proof. The words w0..w5 are the context's, so K0, K1, K2 leave the context's
values by Lemma S, and K3 leaves (S3, S7, S11, S15) by Lemma K. D2 reads state
words 2, 7, 8, 13 and w12, w13, none of which changed, and leaves the
context's X2, X7, X8, X13. D0, D1 and D3 leave the stated outputs by Lemma F.
C0 reads X0, X4, X8, X12 and w2, w6, so Lemma Y gives Y4 = y. Finally, the
proof of the theorem of Section 5 uses the output of step S1 only through
three properties: w15 = 0, the state X after round 0 for block length 60 has
the four constants, and w4 = W4, w13 = W13. The trial's words have them, so
that proof applies to the trial unchanged. QED.

Every line of step S1 is an equation of one call of round 0, or one of the
three word values, solved for the name on its left. So it holds for any
sixteen words whose round 0 has these three word values and these four state
words, and the trial is the output of step S1 for the nine words
(X1, X2, X5, X6, X9, alpha, X12, X13, X14) of its own state. A trial is thus
one of the 2^288 pairs of Section 5, chosen so that its Y4 lies in the class.

**6.2 The residual of a trial.** With Y3, Y3', Y11, Y11' the a and c outputs of
C3 from Fact P ({{Y3}}, {{Y3B}}, {{Y11}}, {{Y11B}}),
delta = W4 - W4' = {{delta}} and the trial's words and state:

    (.., Y4, .., Y12) = C0 = G(X0, X4, X8, X12, w2, w6)
    (Y1, .., Y9, ..)  = C1 = G(X1, X5, X9, X13, w3, w10)
    (.., Y6, .., Y14) = C2 = G(X2, X6, X10, X14, w7, w0)
    E1 on A:  G(Y1, Y6, Y11,  Y12, w12, w5)
    E1 on B:  G(Y1, Y6, Y11', Y12, w12, w5 + delta)
    E3 on A:  G(Y3,  Y4, Y9, Y14, w15, w8)
    E3 on B:  G(Y3', Y4, Y9, Y14, w15, w8)

and R is formed from the eight output words of E1 and E3 as in 3.3. Y4 = y
and Y12 are known from 6.1 without evaluating C0. Write a1, d1, c1, b1, a2, ..
for the assignments of E1 and e1, h1, g1, f1, e2, h2, g2, f2 for those of E3
in the order a, d, c, b; a prime marks message B.

**6.3 Three tests of a trial.** The algorithm uses two tests: rule A, a
condition on one word of E3 (Lemma A), and the E1 test, a 32-bit condition
on E1 alone (Lemma N). A third test, the early test of Lemma E, was the test
of the submissions named in Section 10. The algorithm of this package does
not use it. It is kept because the measurements of Section 10 report its
passes.

**Lemma E.** If R = 0 then
(f1 XOR f1') = t XOR ROR(t, 1) with t = a2 XOR a2'.

Proof. In E1 the inputs Y1, Y6, Y12 and the first word are the same for A and
B, so a1 and d1 are the same, and d2 XOR d2' = ROR(a2 XOR a2', 8). In E3,
f2 XOR f2' = ROR((f1 XOR f1') XOR (g2 XOR g2'), 7). R = 0 says in its first
word that a2 XOR a2' = g2 XOR g2' (digest word 1 is Z[1] XOR Z[9], the a output
of E1 and the c output of E3) and in its third word that
d2 XOR d2' = f2 XOR f2' (digest word 4 is Z[4] XOR Z[12], the b output of E3
and the d output of E1). Substituting, ROR(t, 8) = ROR((f1 XOR f1') XOR t, 7),
and rotating both sides left by 7 gives the claim. QED.

A trial *passes the early test* when the word
(f1 XOR f1') XOR t XOR ROR(t, 1) is zero. The test needs the first five
assignments of E1 and the first four of E3 for both messages.

**Lemma N.** For a trial of 6.1 put beta = b1 XOR b1' and eps = c2 XOR c2',
both taken from E1, and

    n = eps XOR ROL(beta XOR eps, 1) XOR eta.

Let D3 and D6 be the XOR differences between A and B of digest words 3 and
6, which are the second and the fourth word of R. Then n = D3 XOR ROL(D6, 8)
for every trial. In particular R = 0 implies n = 0.

Proof. Digest word 3 is Z[3] XOR Z[11], the a output of E3 and the c output
of E1, so D3 = (e2 XOR e2') XOR eps. Digest word 6 is Z[6] XOR Z[14], the b
output of E1 and the d output of E3, so D6 = (b2 XOR b2') XOR (h2 XOR h2').
In E1, b2 = ROR(b1 XOR c2, 7), so b2 XOR b2' = ROR(beta XOR eps, 7). In E3,
h2 = ROR(h1 XOR e2, 8), and h1 XOR h1' = eta for every Y4 in the class (6.1),
so h2 XOR h2' = ROR(eta XOR e2 XOR e2', 8). Rotating D6 left by 8 gives
ROL(D6, 8) = ROL(beta XOR eps, 1) XOR eta XOR (e2 XOR e2'). The XOR with D3
cancels e2 XOR e2' and leaves n. QED.

A trial *passes the E1 test* when n = 0. The word n needs the first seven
assignments of E1 for both messages and nothing of E3: for a trial of 6.1
the eta of E3 is the constant of the class.

*Rule A.* Let h1 be the second value of E3 on message A, as in 6.2. A trial
*satisfies rule A* when all of the following hold:

{{rule_a_block}}

These are {{rule_conditions}} conditions, each on one bit or on the XOR of two bits, so a
uniform word satisfies rule A with probability 2^-{{rule_pass_exp}}.

**Lemma A.** (a) For a trial of 6.1 let z = a2 XOR d1 be the XOR of the
fifth and the second value of C2, and e1 = Y3 + Y4. Then
ROL(h1, 24) = z XOR ROL(e1, 8): bit i of h1 is bit (i + 24) mod 32 of z XOR
bit (i + 16) mod 32 of e1. (b) For every Y4 in the class, the trial
satisfies rule A exactly when

{{rule_z_block}}

(c) Put S = {{a_shift}}, ALL = {{a_all}} and V = {{a_value}}. The word

    ((z XOR ((z >> 1) AND S)) AND ALL) XOR V

is zero exactly when the trial satisfies rule A.

Proof. (a) The sixth assignment of C2 is Y14 = ROR(d1 XOR a2, 8) = ROR(z, 8),
and the second assignment of E3 is h1 = ROR(Y14 XOR e1, 16). So
h1 = ROR(z, 24) XOR ROR(e1, 16), and rotating left by 24 gives the claim.
(b) Rule A reads the bits {{rule_h_bits}} of h1. By (a) each of them is a
bit of z XOR a bit of e1, and the bits of e1 that enter are bits
{{rule_e_bits}}. All of these lie in the mask
{{qmask}} of Lemma Q, so they have the same value for every member of
the class: in {{qvalue}}, {{rule_e_values}}. Inserting these values into the
{{rule_conditions}} conditions gives the conditions on z. (c) Bit p of
z XOR ((z >> 1) AND S) is the XOR of bits p and p + 1 of z at the positions
p of S and bit p of z elsewhere. S holds the lower positions of the
{{rule_pairs}} conditions on two bits, ALL holds these and the position of the
condition on one bit, and V holds the required values. QED.

*What Lemma A does not say.* Lemma A says that the word of (c) tests rule A
exactly. It does not say that a collision satisfies rule A, and that is not
true: there are solutions of R = 0 with Y4 in the class whose h1 violates
rule A, and Section 10 prints one. Rule A is therefore a filter that loses
solutions. A batch in which no trial satisfies it is dropped, whether or
not one of its trials has a zero residual; a trial that fails rule A is
examined further only if another trial of its batch satisfies it (6.4).
How much is lost is a question about the count of Section 10 and is
answered there: the figure that H1 is set against leaves out, in full, every
outcome of the count for which a solver found a solution that violates
rule A. For the other outcomes {{rule_unsat_who}} that no such
solution exists; these answers are not certified.

**6.4 Algorithm.**

1. Draw one fresh uniform 256-bit word and take from it the four words
   X2, X5, X6, X9. Set X1 = X10 = 0: every trial replaces X1, and the D0
   family replaces X5 and X10 and keeps S5, which the drawn X5 determines.
2. For each of the 2^{{ctx}} values of (X12, X13, X14) with {{ctx_ranges}},
   in a fixed order: run step S1 to get a context. For each of the 2^32
   values of alpha: compute the D0 family, the first half of C0 and the
   per-alpha constants. Then run the batches of 6.5 for the {{members}}
   members of the class in the order of their numbers, seven members in one
   packed word. Every batch runs stage A, which tests rule A for its seven
   trials. If none of them satisfies rule A the batch ends and its trials
   are dropped. Otherwise the batch runs stage 2, which evaluates the E1
   test for its seven trials.
3. For every trial of a batch that ran stage 2 whose E1 test word is zero,
   compute its words by 6.1 and R in full. If R = 0, build A and B by steps
   S2 and S3 from the trial's words, evaluate H(A) and H(B), check that they
   agree, output (A, B) and halt.
4. Halt with failure if 2^{{pass_budget}} trials have been processed in step 3
   without R = 0; or if {{stage2_budget}} batches have run stage 2, which is
   {{stage2_share_words}} of the {{batches_total}} batches of a run; or when all
   trials are exhausted.

A trial with R = 0 that satisfies rule A is found: its batch runs stage 2,
its E1 test word is zero by Lemma N, and step 3 computes its residual,
unless one of the two budgets of step 4 has ended the run before. A trial
with R = 0 that violates rule A is found only if another trial of its batch
satisfies rule A; Section 7 does not count such trials.

The contexts are {{ctx_product}} = 2^{{ctx}}, and the trials are
2^{{ctx}} * 2^32 * 2^{{free_bits}} = 2^{{T}} half-colliding pairs by Lemma T,
and they are distinct. Two contexts differ in X12, X13 or X14, which no trial
changes, so their trials have different states X and different words. Trials
of one context with different alpha differ in X10 = alpha. Trials of one
context and one alpha with different members differ in Y4, which is a
function of the words.

**6.5 Seven trials in one word.** A packed word holds seven lanes of 36 bits
at bit offsets 0, 36, .., 216. A lane represents its value modulo 2^32; bits
32..35 are carry guards. A constant is placed in all seven lanes once per
context or per alpha. Additions are single 256-bit additions. A rotation of
every lane by r is the five operations

    PROR(z, r) = ((z >> r) AND A_r) OR ((z << (32-r)) AND B_r)

with A_r selecting the low 32-r bits of every lane and B_r the next r bits;
the masks discard guard bits and bits shifted in from the neighbouring lane,
so the result is reduced below 2^32. With M = 2^32 - 1 in every lane, a
difference x - y of two lanes is x + (y XOR M) + 1, the difference of a
constant x and a lane y is (y XOR M) + (x + 1), and adding the constant -y
for a constant y is one addition.

The lane layout, seven 36-bit lanes with reduction delayed to the rotations
and a five-operation masked rotation, follows the public ticket 2bf40fb on
this track, which uses it for a birthday search. What is evaluated in the
lanes here is different.

*What a batch computes.* The seven trials of a batch share a context and an
alpha and are seven consecutive members of the class. The members enter
through one list that does not depend on the context: for batch j, U[j]
holds ROL(y,7), one member y per lane. The list
has {{list_words}} packed words, because {{members_plain}} = {{full_batches}} * 7 + {{rest}};
{{last_word_spare}}. The list is computed once, before step 2. A
batch has two stages. Stage A computes in every lane, in the names of 6.1
to 6.3:

- C0 backwards: Y8 = U[j] XOR pb, Y12 = Y8 - pc, Y0 = ROL(Y12,8) XOR pd and
  ka = Y0 + (IV[3] + IV[7] - pa - pb), which is IV[3] + IV[7] + w6.
- K3: kd, kc, kb, S11, S15 = S11 - kc, S3, and the first value of C2,
  v = X2 + X6 + w7, as S3 - (ka + kb) + (X2 + X6).
- C2 to z: its second to fifth values and z, the XOR of the fifth and the
  second.
- Rule A: the word of Lemma A (c), and whether it is zero in some lane.

If that word is zero in no lane, the batch ends. Otherwise stage 2 computes:

- The entry count: the number of batches that have run stage 2 is advanced
  and compared with its budget (step 4).
- C2, rest: Y14 = ROR(z, 8) and Y6, its sixth and eighth values.
- D1: d = (X11 - X12) - S11, X1 = ROL(X12,8) XOR d and a = ROL(d,16) XOR S12.
- C1 to Y1: its first five assignments. The first is X1 + (X5 + w3) and the
  fifth, Y1, is the sum of the first, the fourth, a and the constant
  -S1 - S6, since w10 = a - S1 - S6.
- E1 on A and B: a1, d1, c1, c1', b1, b1', a2, a2', c2, c2'.
- The E1 test: eps = c2 XOR c2', beta XOR eps, the word n of Lemma N, and
  whether n is zero in some lane.

Nothing of E3 is evaluated in a batch. Rule A is a condition on h1, a value
of E3, but by Lemma A it is tested on z, a value of C2, with the bits of e1
that it needs folded into the constant V. The words w6, w7 and w10 are never
formed on their own, and w8, w9, w11 and w14 are not needed in a batch: step
3 computes them for the trials it processes.

*No lane overflows.* Rotation outputs, list entries and constants are below
B = 2^32, and an XOR is never longer in bits than its operands. Every sum
formed in the batch is below 10 B, which is below 2^36, so no carry leaves a
lane. In detail: Y12 and ka are below 2B. In K3, kc is below 2B, S15 below
3B, ka + kb below 3B, its complement (ka + kb) XOR M below 4B and v below 6B.
In C2 the third value is below 2B and the fifth, v plus two values below B,
is below 8B; z, the XOR of the fifth and the second, is below 8B. The only
sum of the rule A part is the one that forms the flags, below 2B. In stage
2 the sum for Y6 is below 3B. In D1, d and X1 are below 2B. In C1 the sums
are below 3B (first), 2B and 6B (Y1, a sum of a value below 3B and three
values below B). In E1 they are below 8B (a1 = Y1 + Y6 + w12), 2B (c1 and
c1'), 10B (the two a2) and 3B (c2 and c2'). The only sum of the E1 test
forms the flags, below 2B. Since every lane stays below 2^36, the low 32
bits of every lane equal the scalar value modulo 2^32, and XOR and PROR
read only those bits. In the word of Lemma A (c), S and ALL lie below bit
31, so (z >> 1) AND S reads bit p + 1 of the same lane for the positions p
of S, the AND with ALL discards the guard bits of z, and the word is below
B. The word n is reduced by an AND with M.

*Operation count of one batch.* The batch runs on a load/store machine with
16 registers. The second column counts additions, XOR, AND, OR, shifts, the
comparisons and the branches, with PROR = 5. The third column counts memory
traffic: every constant operand, that is a per-context or per-alpha constant,
a list entry, a rotation mask, the mask M, a constant of rule A or a budget,
is fetched from memory each time it is used and charged as one load. Shift distances are fixed in the
instruction.

| Part | What is computed | Operations | Loads |
| --- | --- | ---: | ---: |
| loop | next list position, end test, branch | 3 | 1 |
| C0 backwards | Y8 (1), Y12 (1), Y0 (6), ka (1) | 9 | 7 |
| K3 | kd (6), kc (1), kb (6), S11 (1), S15 (3), S3 (6), v (4) | 27 | 14 |
| C2 to z | d1 (6), c1 (1), b1 (6), fifth (2), z (1) | 16 | 8 |
| rule A | word (5), flags and branch (4) | 9 | 6 |
| | stage A, every batch | {{stage_a_ops}} | {{stage_a_loads}} |
| entry count | next count, budget test, branch | 3 | 1 |
| C2, rest | Y14 (5), c2 (1), Y6 (6) | 12 | 4 |
| D1 | d (2), X1 (1), a (6) | 9 | 6 |
| C1 to Y1 | first (1), d1 (6), c1 (1), b1 (6), Y1 (3) | 17 | 9 |
| E1, A and B | a1 d1 (8), c1 c1' b1 b1' (14), a2 a2' c2 c2' (18) | 40 | 15 |
| E1 test | eps, beta XOR eps (3), n (8), flags and branch (4) | 15 | 7 |
| | stage 2, only after a pass of stage A | {{stage_2_ops}} | {{stage_2_loads}} |

So stage A is {{stage_a_ops}} + {{stage_a_loads}} = {{stage_a_total}} primitive operations and stage 2 is
{{stage_2_ops}} + {{stage_2_loads}} = {{stage_2_total}}. No store is needed: the list position and the
entry count stay in two registers across batches, and the batch values
that are live at any point fit in the other 14; the self-test below reports
the number in use.

Each XOR followed by a rotation is 6 operations, a two-term sum 1, a
three-term sum 2 and a difference of two lanes 3; a rotation loads its two
masks. For example K3 is: ka XOR 11 and rotate (6), + IV[3] (1), XOR IV[7]
and rotate (6), XOR ROL(S7,7) (1), S11 - kc (3), rotate S15 and XOR kd (6),
and for v the sum ka + kb (1), XOR M (1), + S3 (1), + (X2 + X6 + 1) (1): 27
operations, with loads for 11, IV[3], IV[7], ROL(S7,7), M, 1, M, X2 + X6 + 1
and three mask pairs: 14. The loads of C0 backwards are U[j], pb, -pc, pd,
the constant IV[3] + IV[7] - pa - pb and one mask pair. The loop advances
the list position, compares it with the end of the list, which is loaded,
and branches. In the rule A part the word of Lemma A (c) is a shift, an AND
with S, an XOR with z, an AND with ALL and an XOR with V (5 operations, 3
loads); the flags are formed by adding 2^32 - 1 to every lane and selecting
bit 32 of every lane, which is set exactly in the lanes whose word is
nonzero (2 operations, 2 loads); the flags are compared with a loaded
constant and stage A ends with a branch (2 operations, 1 load). The entry
count is one addition, a comparison with the loaded budget and a branch. In
C2, Y14 is a rotation of z (5) and Y6 a sum, an XOR and a rotation (7). In
E1, each of c2 and c2' is an XOR, a rotation and a sum (7). In the E1 test,
eps is one XOR, beta XOR eps two, and n a rotation by one, two XORs and the
AND with M (8, with loads for one mask pair, eta and M); the flags, the
comparison and the branch are as in stage A.

The per-alpha constants are seven: pb, -pc, pd and IV[3] + IV[7] - pa - pb
for C0, X5 and X5 + w3 for C1, and alpha for C2. The per-context constants
are fourteen. The constants S, ALL and V of rule A depend on the class
only.

*The count in the submitted program.* The program of the two declared
experiments, experiments/halfsearch.py, contains this batch and the machine
that counts it. A packed word is one integer with seven 36-bit lanes. Every
addition, XOR, AND, OR and shift of packed words is a call that adds one
operation, every constant operand and list entry is fetched by a call that
adds one load, and every comparison and every branch adds one operation.
The batch is written with these calls only; forming the constants and the
list word is not part of it. The program always evaluates both stages, so
that stage 2 is counted and checked for every batch; the algorithm runs
stage 2 only after a pass of stage A. The command

    python3 experiments/halfsearch.py --selftest N [seed]

runs N batches. The nine context words, alpha and the list position of a
case come from SHAKE-256 of the seed text (default 1) and the case number.
Every fourth case is the last batch of the class, and in every fifth case
each context word and alpha is 0, 2^32 - 1 or as drawn. Every lane is
checked against the real messages of its trial. The program builds the
messages A and B of the trial by steps S2 and S3 and compresses each in
full, with a 2-round compression written out from Section 1 and with no
shortcut of the batch. From these two compressions it takes Y4 of A; h1,
the second value of E3 on A; the word n of Lemma N, from E1 evaluated for A
and for B on their own states and words; and the two digests. A lane is
right when Y4 is the member of the lane, the digests agree on digest words
0, 2, 5 and 7, the stage-A flag says whether h1 satisfies rule A as written
in 6.3, the reduced word of stage 2 equals n, n equals D3 XOR ROL(D6, 8) of
the two digests, and the stage-2 flag says whether n is nonzero; and no
lane of a batch counts as right unless both branches are taken exactly when
one of the seven words in front of them is zero. The program prints one
JSON line: the number of cases, the lanes checked and the lanes right, the
lanes that satisfy rule A and the batches in which one does, the operations
and loads of every part and of both stages, whether they are the same in
every case and equal to the table above, for every part the largest lane of
a sum next to the bound quoted above, the largest number of registers in
use at one time, the number of per-context and per-alpha constants, the
number of class members in the list, for how many patterns of zero and
nonzero lanes the flags are right, and for how many packed words built from
all patterns of the bits of z that rule A reads the stage-A flags are
right. Its exit status is 0 only if all of these agree with this section.

With N = {{st_cases}} and seed {{st_seed}} it reports {{st_lanes}} of {{st_lanes}} lanes right;
{{stage_a_ops}} operations and {{stage_a_loads}} loads in stage A and {{stage_2_ops}} and {{stage_2_loads}} in stage 2, per part
as in the table and the same in every case; largest sums of
{{st_sums}}
times 2^32 in C0 backwards, K3, C2 to z, rule A, C2 rest, D1, C1, E1 and
the E1 test, below the bounds 2, 6, 8, 2, 3, 2, 6, 10 and 2; {{st_ctx_constants}}
per-context and {{st_alpha_constants}} per-alpha constants; {{members}} members in the
{{list_words}} words of the list; and at most {{st_registers}} registers in use. The
register figure follows every value, loaded constants and the intermediate
values of a rotation included, from the step that makes it to its last
use, with the operations in the order of the program, and adds two
registers for the list position and the entry count. In that run {{st_pass_a}}
lanes satisfy rule A, in {{st_entered}} batches. None of the {{st_lanes}} words n of
that run is zero, so the flags are also formed for all 128 patterns of zero
and nonzero lanes: all 128 are right. Rule A reads {{rule_z_bits_count}} bits of z; the
program forms {{st_a_patterns}} packed words in which every pattern of these bits occurs
once in every lane, with different other bits, filled guard bits and
another member of the class in every lane, and compares the stage-A flags
with rule A as written on h1 = ROR(ROR(z, 8) XOR e1, 16): all {{st_a_patterns}} are
right, and a lane satisfies rule A in {{st_a_satisfied}} of them.

{{big_selftest_sentence}} {{research_batch_sentence}}

In the declared experiment `residual-search` the same program evaluates one
batch per organizer seed, for that seed's context and alpha and the list
position that holds the first member tried, and returns the operations and
loads of its two stages, its number of right lanes and whether a lane
satisfied rule A as observations. The organizer's runner records
observations as untrusted and does not recompute them. The self-test and
these observations therefore show what the program in the package counts,
and that its lanes agree with the program's own compression of the real
messages. They are a participant check, not an organizer verification of
the cost.

## 7. Success probability

The probability space is the one uniform 256-bit word of step 1, for the
fixed target. The algorithm is otherwise deterministic. The trials depend on
that word only through the four words X2, X5, X6, X9.

Call a trial *good* when R = 0 and the trial satisfies rule A. By 6.4 a
good trial is found unless a budget of step 4 ends the run before.

**Heuristic H1 (score-critical).** Over the coins, the 2^{{T}} trials behave
with respect to the event "good" like independent events of probability at
least 2^-{{T1}} each, to the extent that the probability that no trial is good
is at most exp(-1/2) + 0.002. The rate 2^-{{T1}} is 2^{{F}} = {{factor}} times the
rate of a uniform 128-bit value. The factor is assumed. Section 10 describes
what it is set against: for Y4 in the class and under the seven-word model,
a count without sampling of the solutions of R = 0, from which every outcome
for which a solver found a solution that violates rule A is left out, and
which gives the lower bound {{rule_count}} if the solvers' answers for the
other outcomes are right; a participant computation. The organizer-run
experiments do not measure the factor.

**Heuristic H2 (supporting).** With probability at least 0.9995 over the
coins, fewer than 2^{{pass_budget}} of the 2^{{T}} trials pass the E1 test of Lemma N
without having R = 0. (The budget corresponds to a pass rate of 2^-{{pass_shift}}. The
pass rate measured on {{pass_measured_on}} is 2^{{pass_rate}}, which
would give 2^{{pass_expected}} passes, below the budget by a factor of 2^{{pass_margin}}. Step 3
processes only the passes that lie in batches that ran stage 2, which are
fewer. That the number of passes of one run stays near this mean is part of
the assumption{{h2_support}}.)

**Heuristic H3 (supporting).** With probability at least 0.9995 over the
coins, fewer than {{stage2_budget}} of the 2^{{T}} trials satisfy rule A. (A
batch runs stage 2 only if one of its trials satisfies rule A, and every
trial lies in one batch, so the number of batches that run stage 2 is at
most the number of trials that satisfy rule A. The budget is a share
2^{{stage2_trial_share}} of the trials. A uniform h1
satisfies rule A with probability 2^-{{rule_pass_exp}}. {{h3_measured_sentence}} That
the share of one run stays this close to its mean is part of the
assumption.)

Under H1, H2 and H3 the algorithm outputs a collision with probability at
least 1 - exp(-1/2) - 0.002 - 0.0005 - 0.0005 > 0.3934 - 0.003 = 0.3904 >=
0.39. When it outputs a pair, the pair is a genuine collision: step 3
checks both complete digests, and the messages have different lengths.

*Sensitivity to the factor.* If the rate of good trials is f * 2^-128, the
2^{{T}} trials give 1 - exp(-f/2^{{F1}}) - 0.003 with the same allowances, which
reaches 0.39 only for f >= {{f_min}}: the assumed {{factor}} leaves no slack on
the probability side. The margin of the claim lies between the assumed
{{factor}} and the counted {{rule_count}}, a factor of {{exact_over_factor}}. For an f
between 1 and 2^{{F}} the same success probability needs 2^127 / f trials and,
at the same {{charge}} operations per trial, the total of Section 8 is below
2^({{uniform_total2}} - log2 f): below 2^{{total_bound}} at f = 2^{{F}}, and below
2^{{uniform_total2}} at f = 1, the uniform rate, where
{{charge}} * 2^127 / 430 = 2^{{uniform_exp}} and the package would submit {{uniform_time}}. With
the more cautious f = 2^{{alt_F}} = {{alt_factor}}, which is {{exact_over_alt}} times below the
count, the same package would search 2^{{alt_T}} trials, twice as many contexts,
and would submit {{alt_time}}.

*Remark on clustering.* H1 asks for more than a rate: it asks that the good
trials do not come in clusters. Under M the count of Section 10 gives
{{rule_count}} * 2^{{T}} / 2^128 = {{per_run}} expected good trials in a run, or more,
where H1 needs {{assumed_per_run}}. Suppose that these trials came in clusters of m on
average and that the clusters fell independently. Then a run would contain
one with probability about 1 - exp(-{{per_run}} / m), and the bound 0.39 would
hold for m up to {{cluster_max}}. So if the counted rate is right, the bound
survives a clustering of the successes by that factor. This is a remark and
not a proof: the counted rate rests on M, and nothing here bounds m.
Section 10 reports what was measured on the question.

None of the three heuristics is proved. Section 10 lists the evidence.

## 8. Charged time

One 2-round target compression costs one unit and every other primitive word
operation costs 1/C units with C = 430.

- **Main loop.** For one context and one alpha the {{members}} members take
  {{list_words}} batches: {{full_batches}} full ones and {{last_batch}} and is
  charged in full. A run has 2^{{alphas_exp}} pairs of a context and an alpha and
  so {{batches_total}} batches. Every batch runs stage A, {{stage_a_total}} primitive
  operations by 6.5, memory loads included. By step 4 at most
  {{stage2_share_words}} of the batches, {{stage2_budget}}, run stage 2, {{stage_2_total}}
  operations each. The work per alpha before the batches is the D0 family
  and the first half of C0 (below 40 operations), the seven per-alpha
  constants of 6.5, each placed in seven lanes (12 operations) and stored,
  and the loads of the context words read: below 256 operations. On every
  run the main loop therefore costs at most 2^{{alphas_exp}} times
  {{list_words}} * {{stage_a_total}} + {{list_words}} * {{stage_2_total}} / {{stage2_den}} + 256 = {{alpha_ops}}
  operations, which is less than {{per_trial}} per trial. It is charged
  2^{{alphas_exp}} times {{charge}} * {{members_plain}} = {{alpha_charged}}, that is {{charge}} per trial;
  the difference, {{alpha_margin_pct}}% of the bound, is margin. The main loop is charged
  2^{{T}} * {{charge}} operations. This is the budgeted cost, a bound for every
  run. The expected cost is lower: if a trial satisfies rule A with
  probability 2^-{{rule_pass_exp}}, at most 7 * 2^-{{rule_pass_exp}} = {{rule_share}} of the batches
  run stage 2 on average, and a trial costs at most {{per_trial_expected}} operations
  on average.
- **Per context.** Step S1 is below 2^10 operations. Placing the 14
  per-context constants of the batch in seven lanes and storing them is
  14 * 13 = 182 more. Together they are below 2^11 operations. There are
  2^{{ctx}} contexts: 2^{{ctx_ops}} operations.
- **List.** The list of 6.5 is computed once from eta and Y3: {{members}}
  members at fewer than 64 operations each, 2^{{lists_ops}} operations. The
  three constants of rule A are stored.
- **Passes of the E1 test.** At most 2^{{pass_budget}} are processed (step 4). The
  batch keeps no values of a passing trial, so the trial is recomputed in
  scalar form from its member number: its words by 6.1, the calls C1 and
  C2, E1 and E3 for both messages, and the comparison of R. That is below
  2^10 operations each, loads and the count of the processed trials
  included: 2^{{pass_ops}} operations, a share below 2^-{{pass_share}} of the main loop.
- **Final step.** Steps S2, S3 and two complete hash evaluations with their
  input handling: below 2^11 operations and 2 units, once.
- **Randomness.** One random word, charged as one operation.
- **Preprocessing.** The six constants of 3.2, the word eta of 6.1 and rule
  A are stored in the program. The constants were found by a solver search
  and chosen by the count of Section 10, and rule A was read off counts of
  the same kind. That search, the counts and the measurements of
  Section 10 used fewer than 2^{{sel_ops}} primitive operations in total; this
  figure is the participant's estimate from the running times, not a count.
  As a bound for recomputing a valid set of constants that does not depend
  on that solver, exhaustive search over (w4, w13) for the four fixed
  inputs finds constants with the property of Fact P with at most 2^64
  candidates at two G evaluations and a comparison each, below 128
  operations: 2^71 operations, below 2^63 units.

Total:

    T <= ({{charge}} * 2^{{T}} + 2^{{pass_ops}} + 2^{{ctx_ops}} + 2^{{sel_ops}} + 2^{{lists_ops}} + 2^11 + 1) / 430
         + 2 + 2^63
       <  {{charge}} * 2^{{T}} * (1 + 2^-7) / 430 + 2^64
       <  2^{{total_exp}} + 2^64
       <  2^{{total_bound}}.

Here {{charge}} * 2^{{T}} / 430 = 2^({{T}} + {{log_charge}} - {{log_unit}}) = 2^{{main_exp}}. The
terms after the first add up to less than 2^{{rest_exp}}, which is below
{{charge}} * 2^{{T}} * 2^-7 = 2^{{seventh}}, and log2(1 + 2^-7) < 0.01123. The submitted
bound is time_log2 = {{time_log2}}, a factor of about {{slack}} above this total. This
is a worst-case bound for the algorithm as stated, which halts within its
two budgets on every run.

No sorting or lookup is charged because the algorithm has none: a trial is
tested against zero, not against other trials. The only stored list is the
fixed list of class members of 6.5, which is read in order; its loads are
among the {{stage_a_loads}} of stage A.

## 9. Memory, preprocessing and advice

The program is the step S1 formulas, the trial of 6.1, the packed batch of
6.5 and a compression routine for the final check. Bound the code by 4096
instruction templates of at most four 256-bit words each: 2^14 words, which
is 2^19 bytes. Data is the context (48 words), the per-context and per-alpha
constants in packed form (below 32 words), the masks and the fixed constants
(below 32 words), the list of class members ({{list_words}} words), the batch
temporaries (below 64 words) and the two messages and digests of the final
check: fewer than {{data_words}} words, that is {{data_bytes}} bytes. The memory of
the search is therefore below 2^19 + {{data_bytes}} < 2^{{online_log2}} bytes. Nothing
grows with the number of trials.

*Memory of the preprocessing.* The computations by which the constants and
the class were selected needed far more memory than the search. The solver
search and the counting programs ran on a desktop machine and stayed below
16 GB of main memory, 2^34 bytes; the sampling programs and the programs
for real messages stayed below 10 GB of the memory of one graphics card.
These two limits are the participant's observation of the runs, not
instrumented peaks. memory_log2_bytes = {{memory_log2}} covers both at once,
2^34 + 10 * 2^30 < 2^35 bytes, and with them the search. The cost model
does not score memory.

preprocessing_log2 = {{preprocessing_log2}} is the bound of Section 8 for recomputing the six
constants; it also covers their selection and the selection of eta and of
rule A, and it is included in T. nonuniform_advice_log2_bytes = {{advice_log2}} covers
the 28 bytes of the six constants and eta and the 12 bytes of the three
constants S, ALL and V of rule A (Lemma A), {{advice_bytes}} bytes in all. The list
of 6.5 is not advice: the program computes it from eta and Y3 by Lemma Q.
There is no other stored data and no stored collision.

