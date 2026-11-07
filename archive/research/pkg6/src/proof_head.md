# A free half-collision and a search inside one class for 2-round BLAKE3

The scalar below is `time_log2` under `collision-frontier-v5`. Memory is a
separately reported resource bound.

This exploratory package targets blake3-r2-prefix-v1. It has an exact part and
a heuristic part, and it keeps them apart.

**Exact part.** An explicit construction maps any eight 32-bit words to a
55-byte message A and a 63-byte message B whose complete 2-round BLAKE3-256
digests agree on digest words 0, 2, 5 and 7, that is on 128 of the 256 digest
bits. There is no search in this construction and no probability: it holds for
all 2^256 choices of the eight words (Sections 2 to 5). One of the eight words
is the value of one internal word of round 1, called Y4. The search holds Y4
inside a set of {{members}} values, the *class* (Section 6.1).

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
solutions of a fixed system of equations, and that number is counted: it
is {{exact_total}} times 2^-128 for Y4 in the class, all but a part below 1
from an enumeration without sampling. Rule A is not implied by a collision:
some solutions violate it and are lost. The figure that the claim uses is
therefore smaller. It leaves out every part of the count for which a
solver found a solution that violates rule A, and the part that rests on
estimates, {{rule_lost}} in all, and is {{rule_count}}. H1
assumes {{factor}} times, {{exact_over_factor}} times less. The counting
program is not part of the package, and it and all its checks are the
participant's. The model was compared with real messages only on events of
probability about 2^-{{deep_exp}} and above, the deepest of them events of one
of the two calls alone, and one comparison shows that the model does not
hold inside a single context: the share of the
trials of one context that satisfy rule A differs from context to context,
and only its average over contexts is the model's value (Section 10). The
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
Every message produced has n = 55 or n = 63 bytes. A message of n <= 64 bytes
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

This is the complete hash of the target profile restricted to inputs of 55
and 63 bytes: standard IV, standard flags, true block length, both retained
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

Its outputs are (a2, b2, c2, d2). The values a1, d1, c1, b1 are called the
first, second, third and fourth value of the call, a2 the fifth, and so on.

**Fact 1.** Reading the assignments backwards,

    b1 = ROL(b2, 7) XOR c2       c1 = c2 - d2       d1 = ROL(d2, 8) XOR a2
    B  = ROL(b1, 12) XOR c1      C  = c1 - d1
    a1 = ROL(d1, 16) XOR D       y  = a2 - a1 - b1      x = a1 - A - B.

Each line is one assignment solved for another of its terms. A set of words
A, B, C, D, x, y, a1, d1, c1, b1, a2, d2, c2, b2 is the execution of one
call exactly when the eight assignments hold, in whatever order and for
whichever of their terms they were solved. The constructions below use
nothing else: every line of theirs is one assignment of one call, solved
for the name on its left.

## 3. Three ingredients

**3.1 The length is cancelled inside K2.** K2 is the only call of round 0 that
reads the block length n, the initial value of v[14], and it overwrites that
word; it is also the only call of round 0 that reads w4 and w5. Its inputs are
(IV[2], IV[6], IV[2], n). Put K = IV[2] + IV[6] = 5bf2cd1d. For lengths 55 and
63, whose XOR is 8, define for any w4, w5

    w4' = ((K + w4) XOR 8) - K        w5' = w5 + w4 - w4'.

**Lemma L.** K2 with block length 55 and words (w4, w5) leaves the same four
state words as K2 with block length 63 and words (w4', w5').

Proof. Let a1 = K + w4. In the second execution the first assignment gives
K + w4' = a1 XOR 8, so the second gives ROR(63 XOR a1 XOR 8, 16) =
ROR(55 XOR a1, 16) because 63 XOR 8 = 55: the same d1. The third and fourth
depend only on d1 and constants. The fifth gives
(a1 XOR 8) + b1 + w5' = a1 + b1 + w5 because
w5' - w5 = w4 - w4' = a1 - (a1 XOR 8). The last three depend only on values
already shown equal. QED.

Hence two messages of 55 and 63 bytes that share every word except w4, w5,
related as above, have the same state S after the column step and the same
state X after round 0, since no other call of round 0 reads v[14], w4 or w5
before K2 has made the states equal.

*Which words must be zero.* For both messages to be honest byte strings of
their lengths with the same words w6..w15, the bytes 55 to 63 of the block
must be zero in both. In the 55-byte message they are zero fill. In the
63-byte message bytes 55 to 62 are its last eight bytes, which are chosen
to be zero, and byte 63 is zero fill. Byte 55 is the top byte of w13, bytes
56 to 59 are w14 and bytes 60 to 63 are w15. So the family needs

    w14 = 0,   w15 = 0,   top byte of w13 = 0,

and nothing else: bytes 0 to 54 are free in both messages.

**3.2 A pinned call C3.** Fix the six constants

    X3 = {{X3}}   X7 = {{X7}}   X11 = {{X11}}   X15 = {{X15}}
    W4 = {{W4}}   W13 = {{W13}}

The top byte of W13 is zero. K + W4 = {{KW4}} and W4' = ((K + W4) XOR 8) - K = {{W4B}}, so
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

## 4. Construction: the message from eight words

The construction places the six constants of 3.2 where Lemma H needs them,
keeps w14 = w15 = 0, and gives the word Y4, the b output of C0, a
prescribed value. Its input is eight free words: the seven words of a
*context*,

    vc, vd, S11, S4, X13, X14, w0,

where vc and vd are the third and the second value of the round-1 call C0,
S11 and S4 are words of the state after the column step of round 0, X13
and X14 are words of the state after round 0 and w0 is a message word; and
one more word y, the value that Y4 is to have. The state words X3, X7, X11,
X15 are the constants, w4 = W4, w13 = W13 and w14 = w15 = 0. Step S1 uses
the seven words of the context only. Step T uses y. In both steps a name
on the right is a context word, a constant or a name assigned on an
earlier line, and all arithmetic is modulo 2^32.

**Step S1 (the context).**

    K0, forwards from w0 and backwards from S4:
        ka = IV[0] + IV[4] + w0;   kd = ROR(ka, 16);   kc = IV[0] + kd
        kb = ROR(IV[4] XOR kc, 12)
        S8 = ROL(S4,7) XOR kb;   S12 = S8 - kc;   S0 = ROL(S12,8) XOR kd
        w1 = S0 - ka - kb
    D2, backwards from its outputs X7, X8, X13:
        X8 = vc - vd;   tc = X8 - X13;   td = tc - S8;   tb = ROL(X7,7) XOR X8
        S7 = ROL(tb,12) XOR tc;   X2 = ROL(X13,8) XOR td
        ta = X2 - tb - W13;   S13 = ROL(td,16) XOR ta
    K3, backwards from its outputs S7, S11:
        mb = ROL(S7,7) XOR S11;   mc = ROL(mb,12) XOR IV[7];   md = mc - IV[3]
        S15 = S11 - mc;   S3 = ROL(S15,8) XOR md;   ma = ROL(md,16) XOR 11
        w6 = ma - IV[3] - IV[7];   w7 = S3 - ma - mb
    K2, its first four values:
        p = K + W4;   q = ROR(p XOR 55, 16);   r = IV[2] + q
        u = ROR(IV[6] XOR r, 12)
    D3 with w14 = w15 = 0, the lines that do not read X14:
        ea = S3 + S4;   eb = X3 - ea;   ec = ROL(eb,12) XOR S4
    D3, the lines that read X14:
        ed = ROL(X14,8) XOR X3;   S9 = ec - ed;   S14 = ROL(ed,16) XOR ea
        X9 = ec + X14;   X4 = ROR(eb XOR X9, 7)
    K2, rest:
        S10 = r + S14;   S6 = ROR(u XOR S10, 7);   S2 = ROL(S14,8) XOR q
        w5 = S2 - p - u
    D2, its first word:
        w12 = ta - S2 - S7
    K1, backwards from its outputs S9, S13:
        nc = S9 - S13;   nd = nc - IV[1];   na = ROL(nd,16)
        nb = ROR(IV[5] XOR nc, 12);   S1 = ROL(S13,8) XOR nd
        S5 = ROR(nb XOR S9, 7);   w2 = na - IV[1] - IV[5];   w3 = S1 - na - nb
    C0, its fourth value:
        vb = ROR(X4 XOR vc, 12)

Step S1 assigns the twelve message words w0..w7, w12 and, as constants,
w4 = W4, w13 = W13, w14 = w15 = 0; the sixteen words S0..S15; and X2, X4,
X8, X9. The lines before "D3, the lines that read X14" do not contain X14,
and all later lines do, directly or through S9, S14, X9 or X4.

**Step T (the four words w8..w11, from y).**

    C0, backwards from its b output y:
        Y8 = ROL(y,7) XOR vb;   Y12 = Y8 - vc;   Y0 = ROL(Y12,8) XOR vd
        va = Y0 - vb - w6;   X0 = va - X4 - w2;   X12 = ROL(vd,16) XOR va
    D0, backwards from its outputs X0, X15:
        fd = ROL(X15,8) XOR X0;   fc = S10 + fd;   X10 = fc + X15
        fb = ROR(S5 XOR fc, 12);   X5 = ROR(fb XOR X10, 7)
        fa = ROL(fd,16) XOR S15;   w8 = fa - S0 - S5;   w9 = X0 - fa - fb
    D1, backwards from its outputs X11, X12:
        gc = X11 - X12;   gb = ROR(S6 XOR gc, 12);   X6 = ROR(gb XOR X11, 7)
        gd = gc - S11;   X1 = ROL(X12,8) XOR gd
        ga = ROL(gd,16) XOR S12;   w10 = ga - S1 - S6;   w11 = X1 - ga - gb

Step T assigns X0, X12, X10, X5, X6, X1 and the four words w8..w11. It
changes no name of step S1.

**Step S2.** w4' = W4' and w5' = w5 + W4 - W4', all modulo 2^32. For the
constants of 3.2 that is w5' = w5 + {{delta}}, the same as w5 {{delta_signed}}.

**Step S3.** A is the first 55 bytes of the little-endian encoding of
w0..w15. B is the first 63 bytes of the encoding of the same words with w4, w5
replaced by w4', w5'.

**Lemma S.** For every choice of the seven words of the context, the six
calls K0, K1, K2, K3, D2 and D3 of round 0 with block length 55, with the
words of step S1, are as follows.

- K0 maps (IV[0], IV[4], IV[0], 0) to (S0, S4, S8, S12).
- K1 maps (IV[1], IV[5], IV[1], 0) to (S1, S5, S9, S13).
- K2 maps (IV[2], IV[6], IV[2], 55) to (S2, S6, S10, S14).
- K3 maps (IV[3], IV[7], IV[3], 11) to (S3, S7, S11, S15).
- D2 maps (S2, S7, S8, S13) to (X2, X7, X8, X13).
- D3 maps (S3, S4, S9, S14) to (X3, X4, X9, X14).

Proof. For each call the eight assignments of Section 2 are checked against
the lines of step S1; "holds by the line for N" means that the line of step
S1 that assigns N is that assignment, solved for N.

- K0, words (w0, w1). The first four assignments are the lines for ka, kd
  (its d input is 0), kc and kb. The fifth, ka + kb + w1 = S0, holds by the
  line for w1; the sixth, ROR(kd XOR S0, 8) = S12, by the line for S0; the
  seventh, kc + S12 = S8, by the line for S12; the eighth,
  ROR(kb XOR S8, 7) = S4, by the line for S8. S4 is the context word.
- K3, words (w6, w7). The eighth assignment, ROR(mb XOR S11, 7) = S7, holds
  by the line for mb; the fourth, ROR(IV[7] XOR mc, 12) = mb, by the line
  for mc; the third, IV[3] + md = mc, by the line for md; the seventh,
  mc + S15 = S11, by the line for S15; the sixth, ROR(md XOR S3, 8) = S15,
  by the line for S3; the second, ROR(11 XOR ma, 16) = md, by the line for
  ma; the first, IV[3] + IV[7] + w6 = ma, by the line for w6; the fifth,
  ma + mb + w7 = S3, by the line for w7. S7 comes from the lines of D2,
  S11 is the context word.
- K2, words (W4, w5). The first four assignments are the lines for p, q, r
  and u. The seventh, r + S14 = S10, holds by the line for S10; the eighth,
  ROR(u XOR S10, 7) = S6, by the line for S6; the sixth,
  ROR(q XOR S2, 8) = S14, by the line for S2; the fifth, p + u + w5 = S2,
  by the line for w5. S14 comes from the lines of D3.
- K1, words (w2, w3). The seventh assignment, nc + S13 = S9, holds by the
  line for nc; the third, IV[1] + nd = nc, by the line for nd; the second,
  ROR(0 XOR na, 16) = nd, by the line for na; the first,
  IV[1] + IV[5] + w2 = na, by the line for w2; the fourth is the line for
  nb; the sixth, ROR(nd XOR S1, 8) = S13, holds by the line for S1; the
  eighth is the line for S5; the fifth, na + nb + w3 = S1, holds by the
  line for w3. S9 comes from the lines of D3 and S13 from those of D2.
- D2, words (w12, W13). The seventh assignment, tc + X13 = X8, holds by the
  line for tc; the third, S8 + td = tc, by the line for td; the eighth,
  ROR(tb XOR X8, 7) = X7, by the line for tb; the fourth,
  ROR(S7 XOR tc, 12) = tb, by the line for S7; the sixth,
  ROR(td XOR X2, 8) = X13, by the line for X2; the fifth,
  ta + tb + W13 = X2, by the line for ta; the second,
  ROR(S13 XOR ta, 16) = td, by the line for S13; the first,
  S2 + S7 + w12 = ta, by the line for w12. X7 is the constant, X13 the
  context word, and X8 = vc - vd is a definition.
- D3, words (w14, w15) = (0, 0). The first assignment, S3 + S4 + 0 = ea, is
  the line for ea; the fifth, ea + eb + 0 = X3, holds by the line for eb;
  the fourth, ROR(S4 XOR ec, 12) = eb, by the line for ec; the sixth,
  ROR(ed XOR X3, 8) = X14, by the line for ed; the third, S9 + ed = ec, by
  the line for S9; the second, ROR(S14 XOR ea, 16) = ed, by the line for
  S14; the seventh, ec + X14 = X9, is the line for X9; the eighth is the
  line for X4. X3 is the constant, X14 the context word.

Every name is assigned once, and every line uses only names assigned on
earlier lines: the lines of K0 give S8, which the lines of D2 use; these
give S7 and S13; the lines of K3 use S7 and give S3; the lines of D3 use S3
and give S9, S14 and X4; the rest of K2 uses S14 and gives S2, which the
line for w12 uses; the lines of K1 use S9 and S13. QED.

**Lemma F.** For every context and every word y, with the words of steps S1
and T: D0 maps (S0, S5, S10, S15) to (X0, X5, X10, X15), and D1 maps
(S1, S6, S11, S12) to (X1, X6, X11, X12).

Proof. D0, words (w8, w9): the sixth assignment, ROR(fd XOR X0, 8) = X15,
holds by the line for fd; the third is the line for fc; the seventh is the
line for X10; the fourth is the line for fb; the eighth is the line for X5;
the second, ROR(S15 XOR fa, 16) = fd, holds by the line for fa; the first,
S0 + S5 + w8 = fa, by the line for w8; the fifth, fa + fb + w9 = X0, by the
line for w9. D1, words (w10, w11): the seventh assignment,
gc + X12 = X11, holds by the line for gc; the fourth is the line for gb;
the eighth is the line for X6; the third, S11 + gd = gc, holds by the line
for gd; the sixth, ROR(gd XOR X1, 8) = X12, by the line for X1; the second,
ROR(S12 XOR ga, 16) = gd, by the line for ga; the first,
S1 + S6 + w10 = ga, by the line for w10; the fifth, ga + gb + w11 = X1, by
the line for w11. The inputs S0, S1, S5, S6, S10, S11, S12, S15 are those
of step S1, X15 and X11 are the constants, and X0 and X12 come from the
first lines of step T. QED.

**Lemma Y.** For every context and every word y, C0 with inputs
(X0, X4, X8, X12) and words (w2, w6) has first, second, third and fourth
value va, vd, vc and vb, and outputs (Y0, y, Y8, Y12).

Proof. The first assignment, X0 + X4 + w2 = va, holds by the line for X0;
the second, ROR(X12 XOR va, 16) = vd, by the line for X12; the third,
X8 + vd = vc, by the line X8 = vc - vd of step S1; the fourth is the line
for vb of step S1; the fifth, va + vb + w6 = Y0, holds by the line for va;
the sixth, ROR(vd XOR Y0, 8) = Y12, by the line for Y0; the seventh,
vc + Y12 = Y8, by the line for Y12; the eighth, ROR(vb XOR Y8, 7) = y, by
the line for Y8. QED.

## 5. The half-collision

**Theorem.** For every choice of the seven words of a context and of the
word y, steps S1, T, S2 and S3 output two distinct messages A and B, of 55
and 63 bytes, whose complete 2-round digests agree on digest words 0, 2, 5
and 7; and in both compressions the b output of C0 is Y4 = y.

Proof. The sixteen words of steps S1 and T have w14 = w15 = 0 and
w13 = W13, whose top byte is zero. So bytes 55 to 63 of their encoding are
zero: A, the first 55 bytes, is an honest 55-byte message whose zero-filled
block is the sixteen words, and B is an honest 63-byte message that ends in
eight zero bytes and whose zero-filled block is the sixteen words with w4,
w5 replaced (3.1). Run round 0 on the words of A with block length 55. The
column calls read the initial state, so by Lemma S they leave the state S
of step S1. The diagonal calls then read S: D0 and D1 leave
(X0, X5, X10, X15) and (X1, X6, X11, X12) by Lemma F, D2 and D3 leave
(X2, X7, X8, X13) and (X3, X4, X9, X14) by Lemma S; the four calls act on
disjoint state words. So the state after round 0 has
(X[3], X[7], X[11], X[15]) equal to the four constants, and w4 = W4,
w13 = W13. By Lemma L the compression of B has the same state X after
round 0. The two compressions share every word except w4, w5, so Lemma H
gives the four digest words. C0 reads X0, X4, X8, X12 and w2, w6, which are
the same in both compressions, and has b output y by Lemma Y. The messages
are distinct because their lengths differ. QED.

Distinct choices of the eight words give distinct messages A: vc and vd are
values inside C0, S11 and S4 are state words after the column step, X13
and X14 are state words after round 0, w0 is a message word and y is a
state word after the column step of round 1, and all of them are functions
of the message. The construction yields 2^256 different half-colliding
pairs.

## 6. The search for the other half

**6.1 Trials.** A *context* is seven words (vc, vd, S11, S4, X13, X14, w0)
together with everything that step S1 computes from them. The class
defined next is a set of values of Y4. A **trial** is a context and a
member y of the class; its messages A and B are the output of steps S1, T,
S2 and S3 for the context's seven words and y. Only step T depends on y: the
trials of one context differ in the four message words w8..w11 and in
nothing else of the message.

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

**Lemma T.** For every context and every member y of the class, the
messages A and B of the trial are distinct messages of 55 and 63 bytes
whose complete 2-round digests agree on digest words 0, 2, 5 and 7; in
both compressions Y4 = y; and the XOR difference between A and B of E3's
first-half d value is eta = {{eta}}.

Proof. The first two statements are the theorem of Section 5. In both
compressions w15 = 0 and Y14 is the same, the a input of E3 is Y3 for A and
Y3' for B by Fact P, and Y4 = y is a member of the class, so the difference
is eta by the definition of the class. QED.

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
and Y12 are known from step T without evaluating C0 forwards. Write a1, d1,
c1, b1, a2, .. for the assignments of E1 and e1, h1, g1, f1, e2, h2, g2, f2
for those of E3 in the order a, d, c, b; a prime marks message B.

**6.3 Three tests of a trial.** The algorithm uses two tests: rule A, a
condition on one word of E3 (Lemma A), and the E1 test, a 32-bit condition
on E1 alone (Lemma N). A third test, the early test of Lemma E, was the test
of the first submissions named in Section 10. The algorithm of this package
does not use it. It is kept because the measurements of Section 10 report
its passes.

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
h2 = ROR(h1 XOR e2, 8), and h1 XOR h1' = eta for every Y4 in the class
(Lemma T), so h2 XOR h2' = ROR(eta XOR e2 XOR e2', 8). Rotating D6 left by 8
gives ROL(D6, 8) = ROL(beta XOR eps, 1) XOR eta XOR (e2 XOR e2'). The XOR
with D3 cancels e2 XOR e2' and leaves n. QED.

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

(c) {{rule_c_put}} The word

{{rule_c_formula}}

is zero exactly when the trial satisfies rule A.

Proof. (a) The sixth assignment of C2 is Y14 = ROR(d1 XOR a2, 8) = ROR(z, 8),
and the second assignment of E3 is h1 = ROR(Y14 XOR e1, 16). So
h1 = ROR(z, 24) XOR ROR(e1, 16), and rotating left by 24 gives the claim.
(b) Rule A reads the bits {{rule_h_bits}} of h1. By (a) each of them is a
bit of z XOR a bit of e1, and the bits of e1 that enter are bits
{{rule_e_bits}}. All of these lie in the mask
{{qmask}} of Lemma Q, so they have the same value for every member of
the class: in {{qvalue}}, {{rule_e_values}}. Inserting these values into the
{{rule_conditions}} conditions gives the conditions on z. (c) {{rule_c_proof}} QED.

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
rule A. For the other outcomes three SAT solvers answered that no such
solution exists, and an exact count of the E3 side finds none; Section 10
says how these answers were checked and by whom.

**6.4 Algorithm.**

1. Draw one fresh uniform 256-bit word and take from it the four words
   S11, S4, X13 and w0.
2. For each of the 2^{{ctx}} values of (vc, vd) with vd < 2^{{d_bits}}, in a fixed
   order: run the lines of step S1 that do not read X14, and store what
   the later steps need. For each of the 2^32 values of X14, in increasing
   order: run the lines of step S1 that read X14 and form the constants of
   6.5 that depend on X14. Then run the batches of 6.5 for the {{members}}
   members of the class in the order of their numbers, seven members in
   one packed word. Every batch runs stage A, which tests rule A for its
   seven trials. If none of them satisfies rule A the batch ends and its
   trials are dropped. Otherwise the batch runs stage 2, which evaluates
   the E1 test for its seven trials.
3. For every trial of a batch that ran stage 2 whose E1 test word is zero,
   compute its words by step T and R in full. If R = 0, build A and B by
   steps S2 and S3 from the trial's words, evaluate H(A) and H(B), check
   that they agree, output (A, B) and halt.
4. Halt with failure if 2^{{pass_budget}} trials have been processed in step 3
   without R = 0; or if {{stage2_budget}} batches have run stage 2, which is
   {{stage2_share_words}} of the {{batches_total}} batches of a run; or when all
   trials are exhausted.

A trial with R = 0 that satisfies rule A is found: its batch runs stage 2,
its E1 test word is zero by Lemma N, and step 3 computes its residual,
unless one of the two budgets of step 4 has ended the run before. A trial
with R = 0 that violates rule A is found only if another trial of its batch
satisfies rule A; Section 7 does not count such trials.

The pairs (vc, vd) are 2^32 * 2^{{d_bits}} = 2^{{ctx}}, and the trials are
2^{{ctx}} * 2^32 * 2^{{free_bits}} = 2^{{T}} half-colliding pairs by Lemma T. They
are distinct by the remark after the theorem of Section 5: two trials
differ in vc, in vd, in X14 or in Y4, and each of these is a function of the
message A.

**6.5 Seven trials in one word.** A packed word holds seven lanes of 36 bits
at bit offsets 0, 36, .., 216. A lane represents its value modulo 2^32; bits
32..35 are carry guards. A constant is placed in all seven lanes before the
batches that use it. Additions are single 256-bit additions. A rotation of
every lane by r is the five operations

    PROR(z, r) = ((z >> r) AND A_r) OR ((z << (32-r)) AND B_r)

with A_r selecting the low 32-r bits of every lane and B_r the next r bits;
the masks discard guard bits and bits shifted in from the neighbouring lane,
so the result is reduced below 2^32. With M = 2^32 - 1 in every lane, the
complement of the low 32 bits of a lane is an XOR with M, a difference
x - y of a constant x and a lane y is (y XOR M) + (x + 1), and subtracting a
constant y is one addition of the constant -y.

The lane layout, seven 36-bit lanes with reduction delayed to the rotations
and a five-operation masked rotation, follows the public ticket 2bf40fb on
this track, which uses it for a birthday search. What is evaluated in the
lanes here is different.

*What a batch computes.* The seven trials of a batch share a context and
are seven consecutive members of the class. The members enter through one
list that does not depend on the context: for batch j, U[j] holds ROL(y,7),
one member y per lane. The list
has {{list_words}} packed words, because {{members_plain}} = {{full_batches}} * 7 + {{rest}};
{{last_word_spare}}. The list is computed once, before step 2. A
batch has two stages. Stage A computes in every lane, in the names of step
T and of 6.2 to 6.3:

- C0 backwards: Y8 = U[j] XOR vb, Y12 = Y8 - vc, Y0 = ROL(Y12,8) XOR vd,
  va = Y0 + (-vb - w6), and the complement of X12 as
  va XOR NOT ROL(vd,16).
- D0 and D1, as far as C2 needs them: fd = (va + (-X4 - w2)) XOR ROL(X15,8),
  which is ROL(X15,8) XOR X0; X10 = fd + (S10 + X15); gc = X11 - X12, formed
  as (NOT X12) + (X11 + 1); gb and X6.
- C2 to z: its first value X6 + (X2 + w7), its second, third and fourth
  value, the fifth as the first plus the fourth plus w0, and z, the XOR of
  the fifth and the second.
- Rule A: the word of Lemma A (c), and whether it is zero in some lane.

If that word is zero in no lane, the batch ends. Otherwise stage 2 computes:

- The entry count: the number of batches that have run stage 2 is advanced
  and compared with its budget (step 4).
- C2, rest: Y14 = ROR(z, 8) and Y6, its sixth and eighth values.
- D0 and D1, rest: fb from X10 + (-X15) and S5, and X5; gd = gc + (-S11);
  X1 = ROL(X12,8) XOR gd, formed from the complement of X12 and one more
  XOR with M; and ga = ROL(gd,16) XOR S12.
- C1 to Y1: its first value X1 + X5 + w3, its second, third and fourth
  value, and its fifth, Y1, as the sum of the first, the fourth, ga and
  the constant -S1 - S6, since w10 = ga - S1 - S6.
- E1 on A and B: a1, d1, c1, c1', b1, b1', a2, a2', c2, c2'.
- The E1 test: eps = c2 XOR c2', beta XOR eps, the word n of Lemma N, and
  whether n is zero in some lane.

Nothing of E3 is evaluated in a batch. Rule A is a condition on h1, a value
of E3, but by Lemma A it is tested on z, a value of C2, with the bits of e1
that it needs folded into the constant V. The words w8..w11 are never
formed in a batch: w10 enters Y1 through ga, and step 3 computes all four
for the trials it processes.

*No lane overflows.* Put B = 2^32. Rotation outputs, list entries and
constants are below B. An XOR with a value below B changes only the low 32
bits of a lane, so it keeps a bound that is a multiple of B. In C0
backwards the sums are Y12 and va, below 2B. In the part D0 and D1 they
are va + (-X4 - w2), below 3B; X10, a value below 3B plus a constant, below
4B; and gc, below 3B. In C2 the first value is below 2B, the third,
X10 plus a rotation output, below 5B, and the fifth below 4B. In the rest
of C2 the sum for Y6 is the third value plus Y14, below 6B. In the rest of
D0 and D1 the sums are X10 + (-X15), below 5B, and gd, below 4B; X1 is
below 4B. In C1 the first value is below 6B, the third below 2B, and Y1, a
value below 6B plus three values below B, below 9B. In E1 a1 is below 11B,
c1 and c1' are below 2B, the two a2 are below 13B and c2 and c2' are below
3B. The sums that form the flags of the two tests are below 2B. Every sum
is therefore below 13B, which is below 2^36 = 16B, so no carry leaves a
lane, the low 32 bits of every lane equal the scalar value modulo 2^32,
and XOR and PROR read only those bits. In the word of Lemma A (c) every
shifted bit that is kept comes from the low 32 bits of the same lane,
because a condition joins two bits p < q <= 31 of z and is kept at
position p; the AND with ALL discards the guard bits of z, and the word is
below B. The word n is reduced by an AND with M.

*Operation count of one batch.* The batch runs on a load/store machine with
16 registers. The second column counts additions, XOR, AND, OR, shifts, the
comparisons and the branches, with PROR = 5. The third column counts memory
traffic: every constant operand, that is a constant of the context, a list
entry, a rotation mask, the mask M, a constant of rule A or a budget, is
fetched from memory each time it is used and charged as one load. Shift
distances are fixed in the instruction.

| Part | What is computed | Operations | Loads |
| --- | --- | ---: | ---: |
| loop | next list position, end test, branch | 3 | 1 |
| C0 backwards | Y8 (1), Y12 (1), Y0 (6), va (1), NOT X12 (1) | 10 | 8 |
| D0 and D1 | fd (2), X10 (1), gc (1), gb (6), X6 (6) | 16 | 10 |
| C2 to z | first (1), d1 (6), c1 (1), b1 (6), z (3) | 17 | 7 |
| rule A | {{rule_part_cells}} |
| | stage A, every batch | {{stage_a_ops}} | {{stage_a_loads}} |
| entry count | next count, budget test, branch | 3 | 1 |
| C2, rest | Y14 (5), Y6 (7) | 12 | 4 |
| D0 and D1, rest | fb (7), X5 (6), gd (1), X1 (7), ga (6) | 27 | 13 |
| C1 to Y1 | first (2), d1 (6), c1 (1), b1 (6), Y1 (3) | 18 | 8 |
| E1, A and B | a1 d1 (8), c1 c1' b1 b1' (14), a2 a2' c2 c2' (18) | 40 | 15 |
| E1 test | eps, beta XOR eps (3), n (8), flags and branch (4) | 15 | 7 |
| | stage 2, only after a pass of stage A | {{stage_2_ops}} | {{stage_2_loads}} |

So stage A is {{stage_a_ops}} + {{stage_a_loads}} = {{stage_a_total}} primitive operations and stage 2 is
{{stage_2_ops}} + {{stage_2_loads}} = {{stage_2_total}}. No store is needed: the list position and the
entry count stay in two registers across batches, and the batch values
that are live at any point fit in the other 14; the self-test below reports
the number in use.

Each XOR followed by a rotation is 6 operations, a two-term sum 1 and a
three-term sum 2; a rotation loads its two masks. The loads of C0 backwards
are U[j], vb, -vc, vd, -vb - w6, NOT ROL(vd,16) and one mask pair. The loads of
the part D0 and D1 are -X4 - w2, ROL(X15,8), S10 + X15, X11 + 1, S6, X11
and two mask pairs. In C2 the loads are X2 + w7, X14, w0 and two mask
pairs; its third value adds two registers. The loop advances the list
position, compares it with the end of the list, which is loaded, and
branches. {{rule_part_sentence}} The flags are formed by adding 2^32 - 1 to
every lane and selecting bit 32 of every lane, which is set exactly in the
lanes whose word is nonzero (2 operations, 2 loads); the flags are compared
with a loaded constant and stage A ends with a branch (2 operations, 1
load). The entry count is one addition, a comparison with the loaded
budget and a branch. In the rest of C2, Y14 is a rotation of z (5) and Y6
a sum, an XOR and a rotation (7). In the rest of D0 and D1, fb is a sum,
an XOR and a rotation (7, with loads for -X15, S5 and one mask pair), X5 an
XOR and a rotation (6), gd one addition of -S11, X1 a rotation and two
XORs (7, with loads for one mask pair and M) and ga a rotation and an XOR
with S12 (6). In C1 the loads are w3, X13, X9, -S1 - S6 and two mask pairs.
In E1, each of c2 and c2' is an XOR, a rotation and a sum (7); its loads
are w12, Y11, Y11', w5, w5 + delta and five mask pairs. In the E1 test,
eps is one XOR, beta XOR eps two, and n a rotation by one, two XORs and the
AND with M (8, with loads for one mask pair, eta and M); the flags, the
comparison and the branch are as in stage A.

The constants of a batch that change with X14 are thirteen: vb, -vb - w6,
-X4 - w2, S10 + X15, S6, X14, S5, w3, X9, -S1 - S6, w12, w5 and
w5 + delta. Those that change only with the other six words of the context
are eight: -vc, vd, NOT ROL(vd,16), X2 + w7, w0, -S11, S12 and X13. The
constants of rule A depend on the class only, and ROL(X15,8), X11 + 1,
X11, -X15, Y11, Y11', eta, M and the masks are fixed.

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

runs N batches. The seven context words and the list position of a case
come from SHAKE-256 of the seed text (default 1) and the case number.
Every fourth case is the last batch of the class, and in every fifth case
each context word is 0, 2^32 - 1 or as drawn. Every lane is
checked against the real messages of its trial. The program builds the
messages A and B of the trial by steps S1, T, S2 and S3 and compresses each
in full, with a 2-round compression written out from Section 1 and with no
shortcut of the batch. From these two compressions it takes Y4 of A; h1,
the second value of E3 on A; the word n of Lemma N, from E1 evaluated for A
and for B on their own states and words; and the two digests. A lane is
right when the sixteen words of the 55 bytes of A are the words of the
trial, Y4 is the member of the lane, the digests agree on digest words
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
use at one time, the number of constants per context and per value of X14,
the number of class members in the list, for how many patterns of zero and
nonzero lanes the flags are right, and for how many packed words built from
all patterns of the bits of z that rule A reads the stage-A flags are
right. Its exit status is 0 only if all of these agree with this section.

With N = {{st_cases}} and seed {{st_seed}} it reports {{st_lanes}} of {{st_lanes}} lanes right;
{{stage_a_ops}} operations and {{stage_a_loads}} loads in stage A and {{stage_2_ops}} and {{stage_2_loads}} in stage 2, per part
as in the table and the same in every case; largest sums of
{{st_sums}}
times 2^32 in C0 backwards, D0 and D1, C2 to z, rule A, the rest of C2, the
rest of D0 and D1, C1, E1 and the E1 test, below the bounds 2, 4, 5, 2, 6,
5, 9, 13 and 2; {{st_ctx_constants}}
constants per context and {{st_x14_constants}} per value of X14; {{members}} members in the
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

{{big_selftest_sentence}} {{bound_tool_sentence}}

In the declared experiment `residual-search` the same program evaluates one
batch per organizer seed, for that seed's context and the list position
that holds the first member tried, and returns the operations and loads of
its two stages, its number of right lanes and whether a lane satisfied
rule A as observations. The organizer's runner records observations as
untrusted and does not recompute them. The self-test and these
observations therefore show what the program in the package counts, and
that its lanes agree with the program's own compression of the real
messages. They are a participant check, not an organizer verification of
the cost.

## 7. Success probability

The probability space is the one uniform 256-bit word of step 1, for the
fixed target. The algorithm is otherwise deterministic. The trials depend on
that word only through the four words S11, S4, X13 and w0.

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
pass rate measured on real trials with these constants is 2^{{pass_rate}}, which
would give 2^{{pass_expected}} passes, below the budget by a factor of 2^{{pass_margin}}. Step 3
processes only the passes that lie in batches that ran stage 2, which are
fewer. That the number of passes of one run stays near this mean is part of
the assumption.)

**Heuristic H3 (supporting).** With probability at least 0.9995 over the
coins, fewer than {{stage2_budget}} of the 2^{{T}} trials satisfy rule A. (A
batch runs stage 2 only if one of its trials satisfies rule A, and every
trial lies in one batch, so the number of batches that run stage 2 is at
most the number of trials that satisfy rule A. The budget is a share
2^{{stage2_trial_share}} of the trials, {{budget_over_rule}} times 2^-{{rule_pass_exp}}. A uniform h1
satisfies rule A with probability 2^-{{rule_pass_exp}}. What step 4 budgets is
batches, and the statement on trials is a sufficient condition for it. It
leaves less room than the batches themselves do: a factor of {{budget_over_rule}}
on the average share of the trials, where the measured share of the
batches that hold a trial satisfying rule A is {{batch_share_random}} for random
contexts and {{batch_share_layout}} for contexts laid out in the ranges of the
algorithm, and at most {{batch_share_max}} for any single context among the
{{batch_contexts}} of the samples of Section 10, against the budget of {{budget_share}}.
H3 is a statement about
the average over the 2^{{alphas_exp}} contexts of a run. In its form on trials it is
not true context by context: the largest share of the trials of one
context seen in the samples of Section 10 is {{ctx_share_max}} times 2^-{{rule_pass_exp}}, and such
a context exceeds the budget on its own trials, though not on its own batches. What was measured is that the average over contexts is
2^-{{rule_pass_exp}} to within the errors stated there. That the average over
the contexts of one run stays that close to this mean is the assumption.)

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
count, the same package would search 2^{{alt_T}} trials, twice as many pairs
(vc, vd), and would submit {{alt_time}}.

*Remark on clustering.* H1 asks for more than a rate: it asks that the good
trials do not come in clusters. Under M the count of Section 10 gives
{{rule_count}} * 2^{{T}} / 2^128 = {{per_run}} expected good trials in a run, or more,
where H1 needs {{assumed_per_run}}. Suppose that these trials came in clusters of m on
average and that the clusters fell independently. Then a run would contain
one with probability about 1 - exp(-{{per_run}} / m), and the bound 0.39 would
hold for m up to {{cluster_max}}. So if the counted rate is right, the bound
survives a clustering of the successes by that factor. This is a remark and
not a proof: the counted rate rests on M, and nothing here bounds m. The
dependence of rule A on the context, stated under H3, is a clustering of
one of the two conditions of "good" by context, of the size measured in
Section 10.

None of the three heuristics is proved. Section 10 lists the evidence.

## 8. Charged time

One 2-round target compression costs one unit and every other primitive word
operation costs 1/C units with C = 430.

- **Main loop.** For one context the {{members}} members take
  {{list_words}} batches: {{full_batches}} full ones and {{last_batch}} and is
  charged in full. A run has 2^{{alphas_exp}} contexts, that is pairs of a pair
  (vc, vd) and a value of X14, and so {{batches_total}} batches. Every batch
  runs stage A, {{stage_a_total}} primitive operations by 6.5, memory loads
  included. By step 4 at most {{stage2_share_words}} of the batches,
  {{stage2_budget}}, run stage 2, {{stage_2_total}} operations each. The work per
  value of X14 before its batches is the next value of X14 and its end
  test, the lines of step S1 that read X14 and the thirteen constants of
  6.5 that change with X14, each placed in seven lanes and stored. Written
  out on the machine of the submitted program by a participant tool, it is
  {{prep_ops}} operations, {{prep_loads}} loads and {{prep_stores}} stores, {{prep_total}} in all; it is
  charged as {{prep_bound}}. On every run the main loop therefore costs at
  most 2^{{alphas_exp}} times
  {{list_words}} * {{stage_a_total}} + {{list_words}} * {{stage_2_total}} / {{stage2_den}} + {{prep_bound}} = {{alpha_ops}}
  operations, which is less than {{per_trial}} per trial. It is charged
  2^{{alphas_exp}} times {{charge}} * {{members_plain}} = {{alpha_charged}}, that is {{charge}} per trial;
  the difference, {{alpha_margin_pct}}% of the bound, is margin. The main loop is charged
  2^{{T}} * {{charge}} operations. This is the budgeted cost, a bound for every
  run. The expected cost is lower: if the average share of the trials that
  satisfy rule A is 2^-{{rule_pass_exp}}, at most 7 * 2^-{{rule_pass_exp}} = {{rule_share}} of the batches
  run stage 2 on average, and a trial costs at most {{per_trial_expected}} operations
  on average.
- **Per pair (vc, vd).** The lines of step S1 that do not read X14 are 31
  assignments, each below 16 operations, its loads and its store included. Storing the
  nine words that the lines of X14 read, placing the eight constants
  of 6.5 that do not change with X14 in seven lanes and storing them, and
  the step to the next pair with its end test and branch are below 200
  operations more. Together they are below 2^11 operations;
  this is a bound and was not written out on the machine. There are
  2^{{ctx}} pairs: 2^{{ctx_ops}} operations.
- **List.** The list of 6.5 is computed once from eta and Y3: {{members}}
  members at fewer than 64 operations each, 2^{{lists_ops}} operations. The
  constants of rule A are stored.
- **Passes of the E1 test.** At most 2^{{pass_budget}} are processed (step 4). The
  batch keeps no values of a passing trial, so the trial is recomputed in
  scalar form from its member number: its words by step T, the calls C1
  and C2, E1 and E3 for both messages, and the comparison of R. That is
  below 2^10 operations each, loads and the count of the processed trials
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
  inputs finds constants with the property of Fact P and a zero top byte
  of w13 with at most 2^64 candidates at two G evaluations and a
  comparison each, below 128 operations: 2^71 operations, below 2^63
  units.

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

The program is the lines of steps S1 and T, the packed batch of 6.5 and a
compression routine for the final check. Bound the code by 4096
instruction templates of at most four 256-bit words each: 2^14 words, which
is 2^19 bytes. Data is the context (below 64 words), the constants of a
batch in packed form (below 64 words), the masks and the fixed constants
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
the 28 bytes of the six constants and eta and the {{advice_rule_bytes}} bytes of the
{{advice_rule_words}} constants of rule A (Lemma A), {{advice_bytes}} bytes in all. The list
of 6.5 is not advice: the program computes it from eta and Y3 by Lemma Q.
There is no other stored data and no stored collision.
