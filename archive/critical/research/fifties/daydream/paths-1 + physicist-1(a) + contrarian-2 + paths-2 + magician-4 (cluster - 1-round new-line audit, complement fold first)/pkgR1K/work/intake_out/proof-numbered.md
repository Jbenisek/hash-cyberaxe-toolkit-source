000001 | # A complement-fold collision for 1-round BLAKE3
000002 | 
000003 | The scalar below is `time_log2` under `collision-frontier-v5`. Memory is a
000004 | separately reported resource bound.
000005 | 
000006 | This exploratory package targets blake3-r1-prefix-v1. It gives a
000007 | deterministic algorithm that outputs two distinct 64-byte messages A and B
000008 | with the same complete 1-round BLAKE3-256 digest. Both are one chunk of one
000009 | block with the same chaining value, counter, block length and flags; they
000010 | differ only in message words m9 and m13. In each of the diagonal calls D0 and
000011 | D2 the first message word is chosen so that the call's intermediate c1 is 0;
000012 | then a change of the second message word complements all four outputs of the
000013 | call (Lemma 1, Section 2). The output fold o[i] = s[i] XOR s[i+8] pairs every
000014 | output word of D0 with an output word of D2, so the two complements cancel in
000015 | o[0..7] (Lemma 2). The success probability is 1. The algorithm is charged 2
000016 | target compressions (the complete hashes of both messages, for the final
000017 | collision check) and 854 other primitive operations: 1,298/222 < 5.847
000018 | units, below 2^2.5477. The claimed scalar is 2.5477. Peak memory is below
000019 | 2^18 bytes.
000020 | 
000021 | There is no preprocessing, table, stored collision or nonuniform advice, and
000022 | no heuristic: the collision follows from Lemmas 1 and 2, proved below.
000023 | Accordingly the heuristic list is empty.
000024 | 
000025 | ## 1. The complete hash on the two messages
000026 | 
000027 | H is unkeyed BLAKE3-256 with only round 0 kept in every compression. All
000028 | additions and subtractions on words are modulo 2^32; ROR rotates a 32-bit word
000029 | right, NOT complements it, and M = 2^32 - 1 = ffffffff, so NOT x = M XOR x =
000030 | M - x. The IV is
000031 | 
000032 |     6a09e667 bb67ae85 3c6ef372 a54ff53a
000033 |     510e527f 9b05688c 1f83d9ab 5be0cd19.
000034 | 
000035 | A call G with inputs (a0, b0, c0, d0) and message words (x, y) performs eight
000036 | assignments, named
000037 | 
000038 |     a1 = a0 + b0 + x          d1 = ROR(d0 XOR a1, 16)
000039 |     c1 = c0 + d1              b1 = ROR(b0 XOR c1, 12)
000040 |     a2 = a1 + b1 + y          d2 = ROR(d1 XOR a2, 8)
000041 |     c2 = c1 + d2              b2 = ROR(b1 XOR c2, 7),
000042 | 
000043 | and leaves (a2, b2, c2, d2). G(i,j,k,l; x, y) applies it to the state words
000044 | v[i], v[j], v[k], v[l].
000045 | 
000046 | A compression takes a chaining value c[0..7], sixteen little-endian message
000047 | words m[0..15], a counter t, a block length n and flags f. It sets
000048 | v[0..7] = c, v[8..11] = IV[0..3], v[12] = t mod 2^32, v[13] = t div 2^32,
000049 | v[14] = n and v[15] = f, runs the column step
000050 | 
000051 |     C0 = G(0,4,8,12; m[0],m[1])     C1 = G(1,5,9,13; m[2],m[3])
000052 |     C2 = G(2,6,10,14; m[4],m[5])    C3 = G(3,7,11,15; m[6],m[7])
000053 | 
000054 | and the diagonal step
000055 | 
000056 |     D0 = G(0,5,10,15; m[8],m[9])     D1 = G(1,6,11,12; m[10],m[11])
000057 |     D2 = G(2,7,8,13; m[12],m[13])    D3 = G(3,4,9,14; m[14],m[15]),
000058 | 
000059 | with no message permutation because no second round follows. Call the state
000060 | after the column step u[0..15] and the state after the diagonal step the
000061 | final state s[0..15]. The outputs are o[i] = s[i] XOR s[i+8] and
000062 | o[i+8] = s[i+8] XOR c[i] for i = 0..7.
000063 | 
000064 | **Both messages** have 64 bytes: one chunk of one full block, which is the
000065 | root. H evaluates one compression with chaining value IV, counter 0, block
000066 | length 64 and flags CHUNK_START | CHUNK_END | ROOT = 1 | 2 | 8 = 11, and is
000067 | LE4(o[0]) || ... || LE4(o[7]). Standard IV, flags, true block length, counter,
000068 | feed-forward and the full 256-bit digest are used. This is not a free-start,
000069 | chosen-IV, compression-only or truncated-output setting.
000070 | 
000071 | ## 2. Lemmas
000072 | 
000073 | **Lemma 1 (complement).** Let two evaluations of G have the same inputs
000074 | (a0, b0, c0, d0) and the same x, with c1 = 0, and second message words y and
000075 | y' = y - 2*a2 - 1, where a2 is that of the first evaluation. Then the second
000076 | evaluation leaves (NOT a2, NOT b2, NOT c2, NOT d2).
000077 | 
000078 | Proof. a1, d1, c1 = 0 and b1 depend only on the common inputs and x, so they
000079 | agree. The fifth assignment gives a1 + b1 + y' = a2 - 2*a2 - 1 = M - a2 =
000080 | NOT a2. Then d2' = ROR(d1 XOR NOT a2, 8) = NOT ROR(d1 XOR a2, 8) = NOT d2,
000081 | because rotation commutes with complement. c2' = 0 + NOT d2 = NOT d2 = NOT c2,
000082 | since c2 = 0 + d2. b2' = ROR(b1 XOR NOT c2, 7) = NOT b2. QED.
000083 | 
000084 | **Choosing x.** For inputs (a0, b0, c0, d0), c1 = 0 holds exactly when
000085 | d1 = 0 - c0, that is when a1 = d0 XOR ROR(0 - c0, 16) (ROR by 16 is its own
000086 | inverse), that is x = a1 - a0 - b0. With this x, b1 = ROR(b0, 12).
000087 | 
000088 | **Lemma 2 (fold).** Let two compressions have the same chaining value,
000089 | counter, block length and flags and message words that agree except m9 and
000090 | m13, and let D0 and D2 satisfy Lemma 1 in the second compression relative to
000091 | the first. Then o[0..7] agree.
000092 | 
000093 | Proof. The column step does not read m8..m15, so u agrees. D1 and D3 read
000094 | neither m9 nor m13 nor any word written by D0 or D2 (the four diagonal calls
000095 | touch disjoint state words), so their outputs s[1], s[6], s[11], s[12] and
000096 | s[3], s[4], s[9], s[14] agree. D0 and D2 have the same inputs and x in both
000097 | compressions, and by Lemma 1 the words they leave, s[0], s[5], s[10], s[15]
000098 | and s[2], s[7], s[8], s[13], are complemented. Then
000099 | o[0] = s[0] XOR s[8], o[2] = s[2] XOR s[10], o[5] = s[5] XOR s[13] and
000100 | o[7] = s[7] XOR s[15] each XOR two complemented words, so they agree, and
000101 | o[1], o[3], o[4], o[6] read only words that agree. QED.
000102 | 
000103 | ## 3. Algorithm
000104 | 
000105 | The machine is the 256-bit word RAM of the cost model; a 32-bit quantity is
000106 | held in the low 32 bits of a RAM word. The constants are the IV, M, 64 and
000107 | 11. The algorithm has no input and no coins.
000108 | 
000109 | 1. Column step with m[0..7] = 0: run C0..C3 on (IV[i], IV[4+i], IV[i], d0)
000110 |    with d0 = 0, 0, 64, 11 and no message addition, giving u.
000111 | 2. For D0 on (u[0], u[5], u[10], u[15]) and D2 on (u[2], u[7], u[8], u[13]):
000112 |    d1 = 0 - c0, a1 = ROR(d1, 16) XOR d0, x = a1 - a0 - b0, b1 = ROR(b0, 12),
000113 |    a2 = a1 + b1 (y = 0), y' = ((a2 << 1) XOR M) AND M = 0 - 2*a2 - 1.
000114 |    This gives m8, m9' (D0) and m12, m13' (D2).
000115 | 3. Output A with m8, m12 as computed and every other word 0, and B equal to A
000116 |    except m9 = m9', m13 = m13'. RAM word 0 of each is a constant zero store;
000117 |    RAM word 1 of A is m8 OR (m12 << 128); RAM word 1 of B is that word OR
000118 |    (m9' << 32) OR (m13' << 160). Each sum or difference is reduced by an AND
000119 |    with M.
000120 | 4. Verify: compute H(A) and H(B) (one compression each), compare the two
000121 |    digests on all 256 bits and output (A, B) if they agree; else halt with
000122 |    failure.
000123 | 
000124 | The program is straight-line: no loop, no restart, no coin, and one branch,
000125 | in step 4.
000126 | 
000127 | ## 4. Correctness
000128 | 
000129 | **Theorem.** The algorithm outputs two distinct 64-byte messages with
000130 | H(A) = H(B); the test of step 4 never fails.
000131 | 
000132 | Proof. Step 2 sets x by the rule above, so c1 = 0 in D0 and D2 of A and of B
000133 | (they share u and x). A has y = 0 and B has y' = y - 2*a2 - 1, so Lemma 1
000134 | applies to D0 and D2, and Lemma 2 gives equal o[0..7], the digest. A and B
000135 | differ: m9' = NOT(2*a2) is odd, so it is not 0. QED.
000136 | 
000137 | ## 5. Success probability
000138 | 
000139 | The algorithm is deterministic and, by the theorem, outputs a collision: the
000140 | success probability is exactly 1, above the required 0.39. There is no failed
000141 | trial, restart or amplification.
000142 | 
000143 | ## 6. Charged time
000144 | 
000145 | One 1-round target compression costs one unit and every other primitive word
000146 | operation costs 1/C units with C = 222.
000147 | 
000148 | **Counting convention**, as in entries f0dab7bd, 31acfdbb, c8160a0a and
000149 | 6b039da2. One *data operation* is one addition or subtraction modulo 2^256,
000150 | one AND, OR or XOR, one shift, one comparison or one conditional branch.
000151 | Reduction modulo 2^32 is an explicit AND with M and is counted. A rotation
000152 | ROR(x, r) is ((x >> r) OR (x << (32 - r))) AND M: four data operations. Every
000153 | data operation is charged as four primitive operations (a load for each of at
000154 | most two operands, the operation and a store). A store of a constant word is
000155 | one primitive operation. The internals of a target compression are its unit;
000156 | its input and output handling is charged at 80 primitive operations.
000157 | 
000158 | | Step | Work | Data operations |
000159 | | --- | --- | ---: |
000160 | | 1 | C0, C1 (d0 = 0, no XOR): a1 (2), d1 (4), c1 (2), b1 (5), a2 (2), d2 (5), c2 (2), b2 (5): 27 each | 54 |
000161 | | 1 | C2, C3: the same and the XOR with d0: 28 each | 56 |
000162 | | 2 | D0, D2: d1 (2), a1 (5), x (3), b1 (4), a2 (2), y' (3): 19 each | 38 |
000163 | | 3 | RAM word 1 of A: a shift and an OR; of B: 2 shifts and 2 ORs | 6 |
000164 | | | total | 154 |
000165 | 
000166 | | Step | Work | Units | Primitive operations |
000167 | | --- | --- | ---: | ---: |
000168 | | 1 to 3 | 154 data operations | | 616 |
000169 | | 3 | RAM word 0 of A and of B: two constant stores | | 2 |
000170 | | 4 | the compressions of H(A) and H(B) | 2 | |
000171 | | 4 | their input and output handling, 2 * 80 | | 160 |
000172 | | 4 | digest test: 8 XORs, 7 ORs, a comparison with zero and a branch, 17 data operations | | 68 |
000173 | | 4 | output and halt | | 8 |
000174 | | | total | 2 | 854 |
000175 | 
000176 | **Total.** T = 2 + 854/222 = 1,298/222 = 5.8468... units,
000177 | log2 T = 2.54766... < 2.5477. The claim 2.5477 is log2 T rounded up at the
000178 | fourth decimal: 222^10000 * 2^25476 <= 1,298^10000 < 222^10000 * 2^25477.
000179 | The program is straight-line, so this is the count of every run.
000180 | 
000181 | ## 7. Memory, preprocessing and advice
000182 | 
000183 | Code: the 154 instructions of steps 1 to 3, two constant stores, the two
000184 | compressions inlined (fewer than 400 instructions each) and the 17-instruction
000185 | test: fewer than 2^10 instruction templates of at most four 256-bit words
000186 | each, below 2^17 bytes. Data: the 16 words of u, the temporaries of step 2,
000187 | four RAM words of the messages, the 40 words of one compression, two digests
000188 | and the constants: fewer than 128 words, below 2^12 bytes. Peak memory is
000189 | below 2^17 + 2^12 < 2^18 bytes. There is no table and no stored collision.
000190 | 
000191 | There is no preprocessing phase and no nonuniform advice: the program holds
000192 | only public constants (the IV, M, 64, 11) and every output word is computed by
000193 | the counted steps. The fields preprocessing_log2 = 0 and
000194 | nonuniform_advice_log2_bytes = 0 are upper bounds of one unit and one byte,
000195 | because the schema cannot express the logarithm of zero.
000196 | 
000197 | ## 8. Evidence and scope
000198 | 
000199 | The supporting evidence is the algorithm, the exact hash of Section 1, Lemmas
000200 | 1 and 2, the theorem and the count of Section 6. The argument is exact and
000201 | uses no sampled quantity. The certificate `compl-pair` is the algorithm's
000202 | output, `certificates/compl-pair-a.bin` (A) and
000203 | `certificates/compl-pair-b.bin` (B). No experiment is declared.
000204 | 
000205 | Worked values. A has m8 = bd8ae831, m12 = 580179c0 and every other word 0. B
000206 | also has m9 = 48e28fd3 and m13 = 34efa635. Both have the digest
000207 | 
000208 |     a60b648064d9445baa8f41405ca2283f497c0ecbe4ab151c020d61c692d60301.
000209 | 
000210 | The final states differ by complement in words 0, 2, 5, 7, 8, 10, 13, 15 and
000211 | agree in the other eight; o[8], o[10], o[13], o[15] differ, and they are not
000212 | part of the 256-bit digest.
000213 | 
000214 | Scope and limitations:
000215 | 
000216 | - Specific to the 1-round prefix. This pair's 2-round digests differ. No claim
000217 |   is made about blake3-r2 or full BLAKE3.
000218 | - The complement mechanism is common on this track: several earlier entries
000219 |   by other participants use it (Section 9). Against the participant's earlier
000220 |   entries here, the pair has no difference in the counter, block length,
000221 |   flags or chaining value; the difference is in two message words only and
000222 |   cancels in the output fold, not inside a call.
000223 | - No literature survey was done and no priority or novelty claim is made.
000224 | 
000225 | The claim fields mean: time_log2 = 2.5477 bounds total charged time
000226 | (Section 6); memory_log2_bytes = 18 bounds simultaneous storage (Section 7);
000227 | preprocessing_log2 = 0 and nonuniform_advice_log2_bytes = 0 as in Section 7;
000228 | success_probability = 1 as in Section 5. The required baseline_improved
000229 | identifier blake3-r1-nominal-v2 names the organizer's nominal display
000230 | reference 128, which is not an established attack, a qualified baseline or a
000231 | security bound.
000232 | 
000233 | ## 9. Earlier entries and credit
000234 | 
000235 | Earlier entries of the participant on this track, one line each:
000236 | 
000237 | | entry | time_log2 | ruling | kept here |
000238 | | --- | ---: | --- | --- |
000239 | | beea45d4 | 0 | cancelled | nothing |
000240 | | f0dab7bd | 2 | accepted | the counting convention |
000241 | | 31acfdbb | 4.7545 | plausible_not_refuted, not promoted | the counting convention |
000242 | | c8160a0a | 6.2351 | plausible_not_refuted, not promoted | the counting convention |
000243 | | 6b039da2 | 3.1334 | passed | the counting convention |
000244 | 
000245 | Credit, one line per contributor; a credit is not an endorsement.
000246 | 
000247 | - **rickmanelius** (entry 7e29738c): a deterministic two-word complement
000248 |   collision on this track.
000249 | - **Subflatus3** (entries 75a58077, d959036c, ae5c11f3, 3a9b4c9d): complement
000250 |   collisions on this track.
000251 | - **pratikgx** (entry cbd3581a): an exact complementary-output construction
000252 |   on this track.
000253 | - **Claude (Anthropic) agents**, run by the participant: the c1 = 0 choice of
000254 |   m8 and m12, the pairing of D0 with D2 in the fold, and the pair.
000255 | - **Jbenisek**, the participant who files this package: the counting and this
000256 |   package.
