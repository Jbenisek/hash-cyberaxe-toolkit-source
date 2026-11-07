# A complement-fold collision for 1-round BLAKE3

The scalar below is `time_log2` under `collision-frontier-v5`. Memory is a
separately reported resource bound.

This exploratory package targets blake3-r1-prefix-v1. It gives a
deterministic algorithm that outputs two distinct 64-byte messages A and B
with the same complete 1-round BLAKE3-256 digest. Both are one chunk of one
block with the same chaining value, counter, block length and flags; they
differ only in message words m9 and m13. In each of the diagonal calls D0 and
D2 the first message word is chosen so that the call's intermediate c1 is 0;
then a change of the second message word complements all four outputs of the
call (Lemma 1, Section 2). The output fold o[i] = s[i] XOR s[i+8] pairs every
output word of D0 with an output word of D2, so the two complements cancel in
o[0..7] (Lemma 2). The success probability is 1. The algorithm is charged 2
target compressions (the complete hashes of both messages, for the final
collision check) and 854 other primitive operations: 1,298/222 < 5.847
units, below 2^2.5477. The claimed scalar is 2.5477. Peak memory is below
2^18 bytes.

There is no preprocessing, table, stored collision or nonuniform advice, and
no heuristic: the collision follows from Lemmas 1 and 2, proved below.
Accordingly the heuristic list is empty.

## 1. The complete hash on the two messages

H is unkeyed BLAKE3-256 with only round 0 kept in every compression. All
additions and subtractions on words are modulo 2^32; ROR rotates a 32-bit word
right, NOT complements it, and M = 2^32 - 1 = ffffffff, so NOT x = M XOR x =
M - x. The IV is

    6a09e667 bb67ae85 3c6ef372 a54ff53a
    510e527f 9b05688c 1f83d9ab 5be0cd19.

A call G with inputs (a0, b0, c0, d0) and message words (x, y) performs eight
assignments, named

    a1 = a0 + b0 + x          d1 = ROR(d0 XOR a1, 16)
    c1 = c0 + d1              b1 = ROR(b0 XOR c1, 12)
    a2 = a1 + b1 + y          d2 = ROR(d1 XOR a2, 8)
    c2 = c1 + d2              b2 = ROR(b1 XOR c2, 7),

and leaves (a2, b2, c2, d2). G(i,j,k,l; x, y) applies it to the state words
v[i], v[j], v[k], v[l].

A compression takes a chaining value c[0..7], sixteen little-endian message
words m[0..15], a counter t, a block length n and flags f. It sets
v[0..7] = c, v[8..11] = IV[0..3], v[12] = t mod 2^32, v[13] = t div 2^32,
v[14] = n and v[15] = f, runs the column step

    C0 = G(0,4,8,12; m[0],m[1])     C1 = G(1,5,9,13; m[2],m[3])
    C2 = G(2,6,10,14; m[4],m[5])    C3 = G(3,7,11,15; m[6],m[7])

and the diagonal step

    D0 = G(0,5,10,15; m[8],m[9])     D1 = G(1,6,11,12; m[10],m[11])
    D2 = G(2,7,8,13; m[12],m[13])    D3 = G(3,4,9,14; m[14],m[15]),

with no message permutation because no second round follows. Call the state
after the column step u[0..15] and the state after the diagonal step the
final state s[0..15]. The outputs are o[i] = s[i] XOR s[i+8] and
o[i+8] = s[i+8] XOR c[i] for i = 0..7.

**Both messages** have 64 bytes: one chunk of one full block, which is the
root. H evaluates one compression with chaining value IV, counter 0, block
length 64 and flags CHUNK_START | CHUNK_END | ROOT = 1 | 2 | 8 = 11, and is
LE4(o[0]) || ... || LE4(o[7]). Standard IV, flags, true block length, counter,
feed-forward and the full 256-bit digest are used. This is not a free-start,
chosen-IV, compression-only or truncated-output setting.

## 2. Lemmas

**Lemma 1 (complement).** Let two evaluations of G have the same inputs
(a0, b0, c0, d0) and the same x, with c1 = 0, and second message words y and
y' = y - 2*a2 - 1, where a2 is that of the first evaluation. Then the second
evaluation leaves (NOT a2, NOT b2, NOT c2, NOT d2).

Proof. a1, d1, c1 = 0 and b1 depend only on the common inputs and x, so they
agree. The fifth assignment gives a1 + b1 + y' = a2 - 2*a2 - 1 = M - a2 =
NOT a2. Then d2' = ROR(d1 XOR NOT a2, 8) = NOT ROR(d1 XOR a2, 8) = NOT d2,
because rotation commutes with complement. c2' = 0 + NOT d2 = NOT d2 = NOT c2,
since c2 = 0 + d2. b2' = ROR(b1 XOR NOT c2, 7) = NOT b2. QED.

**Choosing x.** For inputs (a0, b0, c0, d0), c1 = 0 holds exactly when
d1 = 0 - c0, that is when a1 = d0 XOR ROR(0 - c0, 16) (ROR by 16 is its own
inverse), that is x = a1 - a0 - b0. With this x, b1 = ROR(b0, 12).

**Lemma 2 (fold).** Let two compressions have the same chaining value,
counter, block length and flags and message words that agree except m9 and
m13, and let D0 and D2 satisfy Lemma 1 in the second compression relative to
the first. Then o[0..7] agree.

Proof. The column step does not read m8..m15, so u agrees. D1 and D3 read
neither m9 nor m13 nor any word written by D0 or D2 (the four diagonal calls
touch disjoint state words), so their outputs s[1], s[6], s[11], s[12] and
s[3], s[4], s[9], s[14] agree. D0 and D2 have the same inputs and x in both
compressions, and by Lemma 1 the words they leave, s[0], s[5], s[10], s[15]
and s[2], s[7], s[8], s[13], are complemented. Then
o[0] = s[0] XOR s[8], o[2] = s[2] XOR s[10], o[5] = s[5] XOR s[13] and
o[7] = s[7] XOR s[15] each XOR two complemented words, so they agree, and
o[1], o[3], o[4], o[6] read only words that agree. QED.

## 3. Algorithm

The machine is the 256-bit word RAM of the cost model; a 32-bit quantity is
held in the low 32 bits of a RAM word. The constants are the IV, M, 64 and
11. The algorithm has no input and no coins.

1. Column step with m[0..7] = 0: run C0..C3 on (IV[i], IV[4+i], IV[i], d0)
   with d0 = 0, 0, 64, 11 and no message addition, giving u.
2. For D0 on (u[0], u[5], u[10], u[15]) and D2 on (u[2], u[7], u[8], u[13]):
   d1 = 0 - c0, a1 = ROR(d1, 16) XOR d0, x = a1 - a0 - b0, b1 = ROR(b0, 12),
   a2 = a1 + b1 (y = 0), y' = ((a2 << 1) XOR M) AND M = 0 - 2*a2 - 1.
   This gives m8, m9' (D0) and m12, m13' (D2).
3. Output A with m8, m12 as computed and every other word 0, and B equal to A
   except m9 = m9', m13 = m13'. RAM word 0 of each is a constant zero store;
   RAM word 1 of A is m8 OR (m12 << 128); RAM word 1 of B is that word OR
   (m9' << 32) OR (m13' << 160). Each sum or difference is reduced by an AND
   with M.
4. Verify: compute H(A) and H(B) (one compression each), compare the two
   digests on all 256 bits and output (A, B) if they agree; else halt with
   failure.

The program is straight-line: no loop, no restart, no coin, and one branch,
in step 4.

## 4. Correctness

**Theorem.** The algorithm outputs two distinct 64-byte messages with
H(A) = H(B); the test of step 4 never fails.

Proof. Step 2 sets x by the rule above, so c1 = 0 in D0 and D2 of A and of B
(they share u and x). A has y = 0 and B has y' = y - 2*a2 - 1, so Lemma 1
applies to D0 and D2, and Lemma 2 gives equal o[0..7], the digest. A and B
differ: m9' = NOT(2*a2) is odd, so it is not 0. QED.

## 5. Success probability

The algorithm is deterministic and, by the theorem, outputs a collision: the
success probability is exactly 1, above the required 0.39. There is no failed
trial, restart or amplification.

## 6. Charged time

One 1-round target compression costs one unit and every other primitive word
operation costs 1/C units with C = 222.

**Counting convention**, as in entries f0dab7bd, 31acfdbb, c8160a0a and
6b039da2. One *data operation* is one addition or subtraction modulo 2^256,
one AND, OR or XOR, one shift, one comparison or one conditional branch.
Reduction modulo 2^32 is an explicit AND with M and is counted. A rotation
ROR(x, r) is ((x >> r) OR (x << (32 - r))) AND M: four data operations. Every
data operation is charged as four primitive operations (a load for each of at
most two operands, the operation and a store). A store of a constant word is
one primitive operation. The internals of a target compression are its unit;
its input and output handling is charged at 80 primitive operations.

| Step | Work | Data operations |
| --- | --- | ---: |
| 1 | C0, C1 (d0 = 0, no XOR): a1 (2), d1 (4), c1 (2), b1 (5), a2 (2), d2 (5), c2 (2), b2 (5): 27 each | 54 |
| 1 | C2, C3: the same and the XOR with d0: 28 each | 56 |
| 2 | D0, D2: d1 (2), a1 (5), x (3), b1 (4), a2 (2), y' (3): 19 each | 38 |
| 3 | RAM word 1 of A: a shift and an OR; of B: 2 shifts and 2 ORs | 6 |
| | total | 154 |

| Step | Work | Units | Primitive operations |
| --- | --- | ---: | ---: |
| 1 to 3 | 154 data operations | | 616 |
| 3 | RAM word 0 of A and of B: two constant stores | | 2 |
| 4 | the compressions of H(A) and H(B) | 2 | |
| 4 | their input and output handling, 2 * 80 | | 160 |
| 4 | digest test: 8 XORs, 7 ORs, a comparison with zero and a branch, 17 data operations | | 68 |
| 4 | output and halt | | 8 |
| | total | 2 | 854 |

**Total.** T = 2 + 854/222 = 1,298/222 = 5.8468... units,
log2 T = 2.54766... < 2.5477. The claim 2.5477 is log2 T rounded up at the
fourth decimal: 222^10000 * 2^25476 <= 1,298^10000 < 222^10000 * 2^25477.
The program is straight-line, so this is the count of every run.

## 7. Memory, preprocessing and advice

Code: the 154 instructions of steps 1 to 3, two constant stores, the two
compressions inlined (fewer than 400 instructions each) and the 17-instruction
test: fewer than 2^10 instruction templates of at most four 256-bit words
each, below 2^17 bytes. Data: the 16 words of u, the temporaries of step 2,
four RAM words of the messages, the 40 words of one compression, two digests
and the constants: fewer than 128 words, below 2^12 bytes. Peak memory is
below 2^17 + 2^12 < 2^18 bytes. There is no table and no stored collision.

There is no preprocessing phase and no nonuniform advice: the program holds
only public constants (the IV, M, 64, 11) and every output word is computed by
the counted steps. The fields preprocessing_log2 = 0 and
nonuniform_advice_log2_bytes = 0 are upper bounds of one unit and one byte,
because the schema cannot express the logarithm of zero.

## 8. Evidence and scope

The supporting evidence is the algorithm, the exact hash of Section 1, Lemmas
1 and 2, the theorem and the count of Section 6. The argument is exact and
uses no sampled quantity. The certificate `compl-pair` is the algorithm's
output, `certificates/compl-pair-a.bin` (A) and
`certificates/compl-pair-b.bin` (B). No experiment is declared.

Worked values. A has m8 = bd8ae831, m12 = 580179c0 and every other word 0. B
also has m9 = 48e28fd3 and m13 = 34efa635. Both have the digest

    a60b648064d9445baa8f41405ca2283f497c0ecbe4ab151c020d61c692d60301.

The final states differ by complement in words 0, 2, 5, 7, 8, 10, 13, 15 and
agree in the other eight; o[8], o[10], o[13], o[15] differ, and they are not
part of the 256-bit digest.

Scope and limitations:

- Specific to the 1-round prefix. This pair's 2-round digests differ. No claim
  is made about blake3-r2 or full BLAKE3.
- The complement mechanism is common on this track: several earlier entries
  by other participants use it (Section 9). Against the participant's earlier
  entries here, the pair has no difference in the counter, block length,
  flags or chaining value; the difference is in two message words only and
  cancels in the output fold, not inside a call.
- No literature survey was done and no priority or novelty claim is made.

The claim fields mean: time_log2 = 2.5477 bounds total charged time
(Section 6); memory_log2_bytes = 18 bounds simultaneous storage (Section 7);
preprocessing_log2 = 0 and nonuniform_advice_log2_bytes = 0 as in Section 7;
success_probability = 1 as in Section 5. The required baseline_improved
identifier blake3-r1-nominal-v2 names the organizer's nominal display
reference 128, which is not an established attack, a qualified baseline or a
security bound.

## 9. Earlier entries and credit

Earlier entries of the participant on this track, one line each:

| entry | time_log2 | ruling | kept here |
| --- | ---: | --- | --- |
| beea45d4 | 0 | cancelled | nothing |
| f0dab7bd | 2 | accepted | the counting convention |
| 31acfdbb | 4.7545 | plausible_not_refuted, not promoted | the counting convention |
| c8160a0a | 6.2351 | plausible_not_refuted, not promoted | the counting convention |
| 6b039da2 | 3.1334 | passed | the counting convention |

Credit, one line per contributor; a credit is not an endorsement.

- **rickmanelius** (entry 7e29738c): a deterministic two-word complement
  collision on this track.
- **Subflatus3** (entries 75a58077, d959036c, ae5c11f3, 3a9b4c9d): complement
  collisions on this track.
- **pratikgx** (entry cbd3581a): an exact complementary-output construction
  on this track.
- **Claude (Anthropic) agents**, run by the participant: the c1 = 0 choice of
  m8 and m12, the pairing of D0 with D2 in the fold, and the pair.
- **Jbenisek**, the participant who files this package: the counting and this
  package.
