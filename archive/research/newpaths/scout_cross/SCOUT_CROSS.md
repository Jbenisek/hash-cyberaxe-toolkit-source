# SCOUT_CROSS.md: attacks on related designs, mapped onto 2-round BLAKE3

Folder: research\newpaths\scout_cross. Written 2026-10-08. Research only: no yukon, no submission, no posts.
Tags: COMPUTED = run here (command in section 5). DERIVED = read from a cited source, or follows by an
argument given here. GUESS = judgement, or not checked against a source.
Not repeated here: everything in ..\literature\LITERATURE.md. Also not repeated: fringe's tests
(..\fringe\RESULTS.txt): message-level neutral bits, rotational and RX pairs, E0/E2 symmetry, Wagner on the
XOR split, table-backed CV, and multi-block CV differences. Where a technique maps onto one of those, I
only cite the source and point to fringe.

Setting recap (DERIVED, verified in ..\..\NEW_PATHS.md and fringe): out_i = v_i ^ v_{i+8}.
A half: out0 = E0.a^E2.c, out2 = E2.a^E0.c, out5 = E0.b^E2.d, out7 = E2.b^E0.d.
B half: out1 = E1.a^E3.c, out3 = E3.a^E1.c, out4 = E3.b^E1.d, out6 = E1.b^E3.d.
E0..E3 are round 1's diagonal calls. Each half is the XOR of two G calls, with the words swapped
(a<->c, b<->d).

## 0. Bottom line

1. DERIVED. I found no technique from Salsa/ChaCha, Skein/Threefish, SipHash, Speck/Simon/Chaskey, SHA-1/SHA-2
   or Keccak that gives a 2-round BLAKE3 path cheaper than the board. Each one falls into one of three groups:
   (a) already in the 55/63 path under another name: connector / target-difference algorithm = the K2 length
   cancellation; start-from-the-middle = the inside-out member construction; partitioning = classes and S8;
   XOR-fold cancellation (Rumba) = Lemma D; S-function counting = the carry automata.
   (b) dead for a fixed-IV hash collision: PNB key recovery, differential-linear, rotational, internal
   differentials, boomerang distinguishers, chosen-prefix correction blocks, Wagner on independent lists.
   (c) worth less under this cost model because trials are already cheap: neutral bits, tunnels, amplified
   boomerangs. The filed path's trial costs 3.485 word operations = 2^-6.95 units. Amplification can save at
   most that residual, under 2 bits. The exponent is set by the event probability.
2. COMPUTED (TEST 1a), new freedom. BLAKE3's tree mode gives free instance constants. In the organizer's
   reference code (verifier/blake3.py, 2 rounds), a collision of the LAST CHUNK's compression is a full-hash
   collision. Take M = P||B and M' = P||B', with P = t full chunks and B, B' of 55 and 63 bytes. That
   compression then has counter v12/v13 = t (any t from 1 to about 2^51, set by the prefix length) and flags
   v15 = 3 (or 2, with a chained CV, when the last chunk has more than one block), instead of t = 0 and
   flags 11. Checked for t = 1, 2, 3, 5 and for 2- and 3-block last chunks. fringe's angle 10 says "root
   counter is always 0": that is true, but the collision does not have to be at the root.
3. COMPUTED (TESTS 1b, 1c). The free constants do not help. (1b) In toy 2-round BLAKE3, the
   length-sibling pair's A-half zero channel had the same rate within sampling noise across 8 instances:
   the filed one, counter 1, random counters with flags 3, and random CVs with flags 2. Checked at w = 6
   and 8. (1c) In the filed path's own trial model (Grok job20 FIX7), the counter enters as q2 = t_lo and
   k2 = t_hi. A small t is neutral (sum of top-8 co-pass 5.68-5.70 against 5.675/5.680 at t = 0). A random
   32-bit t_lo lowers the mean X2 co-pass from 0.2585 to 0.242-0.246. Any t_hi != 0 lowers x30/x31 by
   0.02-0.04. So the filed t = 0 is already in the best region. DERIVED: round 0 is a bijection for every
   choice of constants, so the constants only relabel messages and can matter only to a construction that
   uses a specific constant value. 1c shows exactly that case, and its sign is against us.
4. COMPUTED + DERIVED (TEST 2, Rumba-style XOR cancellation). Lemma 1: for the 55/63 sibling pair, E3 is
   ALWAYS active. dY3 = 0 would need R0 + R1 = 0 mod w; at w = 32, 16 + 12 = 28. Observed: 0 events in all
   runs. So the B half can close only through the XOR fold (the filed path's Lemma D). Lemma 2 gives a
   necessary condition at 32 bits: dE3.b1 = dE3.c2 xor rotr(dE3.c2, 1). Lemma 2 also shows that toys with
   R2 = R3 cannot close the B half at all: job28's primary rotations at w = 5 and 6, and its alternate
   rotations at w = 8. Agents using those toys should switch rotations. Without class conditions the fold
   is weak. A-half fold: 10 events against 8 expected at w = 6 (random level). B half at w = 6 with
   non-degenerate rotations (3,2,2,1): 22 events against 13.1 expected, about 0.75 bit over random. The filed
   path's 27.5 bits over random come from its class engineering, not from the fold itself.
5. DERIVED. Internal differentials (Keccak squeeze, Grostl) stay dead, even with the free counter. Choosing
   t = (flags << 32) | len makes row 3 (t_lo, t_hi, len, flags) symmetric under the column shift c -> c+2.
   Row 2 is always IV0..IV3 in every BLAKE3 compression, and IV0 != IV2, IV1 != IV3. No counter or CV choice
   can fix that.

## 1. Technique map

Columns: source | mechanism | precise analogue in 2-round BLAKE3 | does "memory free, preprocessing up to
~2^85 free" change its value | verdict.

### 1.1 Salsa20 / ChaCha (the same quarter-round family; BLAKE took ChaCha's G)
- Truncated differentials + probabilistic neutral bits (PNB), key recovery [AFKMR08]. 2025 refinements:
  PNB sets from several output-bit differences [2025/1830], bit puncturing [2025/437], probabilistic neutral
  expressions [2025/2334]. Differential-linear with ARX linear approximations [BLT20, 2020/775].
  Mechanism: a 1-round differential that holds with probability about 1 for chosen nonces, then a biased bit
  after r rounds. PNBs are key bits with little effect on the backward computation, so only the significant
  key bits are guessed (DERIVED from the abstracts and [AFKMR08] section 3).
  Analogue: none. There is no secret, and our attacker already controls 512 message bits in every round
  (ChaCha's attacker controls only the nonce/counter). A biased output bit is a distinguisher, not a zero
  output difference. Cost model: no change. Verdict: dead for collisions (DERIVED).
- Rumba (XOR of 4 Salsa20 calls) collisions [AFKMR08, section 4], read from the local copy
  papers\AFKMR08.txt. The same differential runs in two independent instances F0 and F2, so the output
  differences cancel in the XOR (dR0 = dR2). The first round is linearized with 18 fixed input bits, saving
  2^4. A 2-neutral set (a maximum clique) of 146-147 bits is used; flipping up to 20 of them keeps
  2-round conformance with probability 0.68 over a 2^80 space. Total about 2^79 for 3-round Rumba, against
  2^85 without these tricks and 2^256 generically. A birthday list-match between F0-pairs and F2-pairs is used
  only for near-collisions.
  Analogue: the fold. A half: need dE2_out = swap(dE0_out); B half: dE3_out = swap(dE1_out), with
  swap(a,b,c,d) = (c,d,a,b). This is exactly the leaders' Lemma D. Two differences from Rumba: the two
  instances are NOT independent (shared Y state and message), so Rumba's list matching does not apply
  (../sidepaths, ../separable: MITM splits 0 bits); and the swap means "same differential in both" does not
  cancel. Cost model: Rumba's amplification (neutral bits) is worth < 2 bits here (bottom line 1c).
  Verdict: in use (Lemma D); measured in TEST 2.
- Linearization by sufficient conditions [AFKMR08 4.2]. The paper says it "does not work well for more than
  one round because of an avalanche effect of fixed bits". The analogue (Keccak "linear structures",
  [GLS16]) would need 1.5 rounds affine on 192 or more dimensions to make the A half constant by linear
  algebra. Dead (DERIVED).

### 1.2 Skein / Threefish
- Rotational rebound [KNR10, 2010/538]: rotational pairs plus a rebound inbound phase give rotational
  "collisions" for 53/57 of 72 rounds of the Skein-256/512 compression function. These are distinguishers.
  Analogue: (M, M<<<r). The constants (IV, counter, length, flags) are not rotation-invariant, and a
  rotational pair is not a collision. fringe angle 5 measured 2^-9 per G at r = 1, so 2^-144 or worse over
  16 calls. Dead (fringe; DERIVED).
- Near-collisions on the reduced Skein/BLAKE compression [SWWD10]: in LITERATURE (chosen IV).

### 1.3 SipHash
- [DMS14, 2014/722]: automated nonlinear characteristic search, with exact ARX probabilities generalised
  from S-functions. Best SipHash-2-4 characteristic 2^-236.3; a practical distinguisher on the finalization.
  Analogue: the same tool for BLAKE3 equal-length message differences. DERIVED here: since round 0 is a
  bijection M -> X, an equal-length pair always has dX != 0, so round 1 must absorb a nonzero state
  difference with message differences that each enter a single G. job28's greedy trails (-130/-173/-213 at
  w = 8/12/16) and the spec's 2^-185 say this is far off. A message-modification-aware search, where only
  round-1 conditions are counted, has not been run anywhere. It is LITERATURE 4.7's "suggested" item.
  Verdict: needs more, low prior (GUESS).

### 1.4 Speck / Simon / Chaskey
- Matsui-style threshold search for ARX trails [BV14; BVL16, 2016/409]; key recovery on round-reduced
  Speck [Din14, 2014/320]. Only the trail-search tool transfers (same use as 1.3).
- Chaskey partitioning [Leu16, 2015/968] (refining Biham-Carmeli): split the data by a few bits around an
  addition, so that the addition is nearly linear inside each part; this raises the differential-linear
  bias. Analogue: the leaders' classes and S8 sub-class (values chosen so carries are fixed). Under our cost
  model a partition is free only if its bits are inside-out free words. Verdict: in use (GUESS on how far
  their classes already exploit it).
- Simon (AND-RX) was not searched: no addition, little transfer (GUESS).

### 1.5 SHA-1 / SHA-2
- Neutral bits [BC04, 2004/146], tunnels [Kli06, 2006/105], amplified boomerang auxiliary paths [JP07],
  all combined in SHAttered [SBKAM17, 2017/190]. They generate many conforming messages from one at near
  zero cost per message.
  Analogue: (i) for the filed path, the trials are already 2^-6.95 units each, so the gain is under 2 bits;
  (ii) for IDEA 1 (half-fixed family), neutral directions would replace checks. fringe found 0 neutral 1-2
  bit message differences. shape_torus finds one irreducible core of 68-94 words, so a flip in any free
  word reaches the core. Tunnels = exact multi-word compensations: these are fringe's sum absorption
  (Y0+m1) and length siblings (m4, m5 vs block length), already found. Verdict: dead or in use.
- Two-block / semi-free-start conversion [MNS13]; first practical 31-step SHA-256 collision [LLWDS24]
  (slides read: papers\LLWDS24_slides.txt). Precompute valid internal states, then hash arbitrary first
  blocks and match the resulting chaining value against the table; time 2^40.5, memory 2^19.8.
  Analogue: fringe's table-backed CV (2 CV words prescribed per lookup with 2^64 preprocessing). New here:
  the chunk counter and flags are further constants that come FREE (bottom line 2, TEST 1).
- Chosen-prefix collisions [LP20, 2020/014]: a birthday phase to reach a correctable chaining-value
  difference, then near-collision blocks. It needs free-start correction in a later block; the cheapest
  2-round free-start collision is 2^112 [LX09], and fringe angle 10 shows the CV difference returns in
  round 1. Dead.
- SAT-based local-collision and characteristic search for SHA-256, up to 37 steps [2026/232]; [LLW24] is
  in LITERATURE. A tool for 1.3, not a mechanism.

### 1.6 Keccak
- Internal differentials and squeeze attacks [Pey10, 2010/223; DDS13, 2012/672; ZHL23]. Map many inputs
  into a small symmetric subspace, then run a birthday search inside it; 3-round Keccak-384/512 collisions,
  5-round Keccak-256. Mechanism: the round function is symmetric, and the low-weight constants break the
  symmetry only a little.
  Analogue: the column shift c -> c+2 commutes with both BLAKE3 steps if message pairs match. Row 2 (always
  IV0..IV3) breaks it in every compression, even with the free counter (bottom line 5). fringe's partial
  versions (E0 = E2): 6-7 checks. Dead.
- Target difference algorithm [DDS12, 2011/624] and connectors [QSLG17, 2017/128]: solve 1-2 rounds
  algebraically so that pairs reach the start of a high-probability characteristic. Also: truncated output
  means the last 1.5 rounds only need the digest bits to agree. Analogue: the K2 length cancellation (a
  probability-1 connector of one G call), and Lemma D (only the folded output must agree). In use.

### 1.7 Generic results on "output = XOR of two halves"
- Wagner's k-tree [Wag02] and Bernstein's Rumba20 note (output size for a XOR of independent expansions;
  listed at https://cr.yp.to/rumba20.html, page not readable by my fetch tool). Both need XOR of functions
  of INDEPENDENT inputs. BLAKE3 folds two halves of one permutation output. A product family would need 768
  bits of conditions on a 512-bit message (fringe angle 9). The tree mode does give a free product family
  (parent message = L||R from independent subtrees), but the parent output is a compression of L||R, not a
  XOR, and L and R are hash outputs with no message modification. Dead (DERIVED).
- PRF bounds for XOR/truncation of permutations, e.g. summation-truncation hybrid [GM20]. Generically the
  fold is as good as truncation. Any gain is structural: the 2-call split of each half. No attack transfers.
- Rebound / super-S-box with tables [MRST09; GP10, 2009/531]: analogue "super-G" tables (2^64 entries for a G
  call with two constant ports). This is fringe's angle 11 and audit's 'pair' rules; no gain in greedy.

## 2. TEST 1: free instance constants from the tree mode

1a (COMPUTED, t1_tree.py -> t1_tree.txt). For the organizer's reference I patched _compress so that the
last-chunk compression of B2 (63 bytes) returns B1's CV (55 bytes). The two full hashes then agree, and the
unpatched hashes differ. The logged instance of that call is (counter t, block_len 55/63, flags 3,
cv = IV) for t = 1, 2, 3, 5. With 1 or 2 extra blocks in the last chunk it is (t, 55/63, flags 2,
cv = chained). So a collision of that compression is a full collision.
Practical limit (DERIVED): the verifier hashes the whole message, so t should stay small (16t compressions to
verify). A t near 2^33 (needed for the symmetric row 3) means a 13 TB message.

1b (COMPUTED, t2_sibling.py; xtoy.py validated against the reference: 0 mismatches in 200 random
(cv, counter, length, flags) at w = 32). Length-sibling pairs (block lengths 55 and 63, with m4 and m5
adjusted as in fringe's angle 3): round-0 state identical in every pair (Xbad = 0). Results per instance,
N = 2^24 pairs:

log2 P[ZA] (A-half zero channel: dY7 = dY15 = 0), COMPUTED (t2_w6_n24.txt, t2_w8_n24.txt):

| instance | w = 6 (rots 3,2,1,1) | w = 8 (rots 4,3,2,1) |
|---|---|---|
| filed: IV, t = 0, flags 11 | -14.42 | -18.79 |
| last chunk, t = 1, flags 3 | -14.40 | -18.71 |
| last chunk, t random (3 values), flags 3 | -14.43 / -14.50 / -14.47 | -18.87 / -18.87 / -19.14 |
| 2-block last chunk, random CV, t random, flags 2 | -14.38 / -14.35 / -14.38 | -19.00 / -18.64 / -18.83 |
| expected sampling sd | about 0.05 (about 770 events) | about 0.24 (about 36 events) |

The spread is within about 2 sd in both columns. The single-word rates P[dY7 = 0], P[dY11 = 0] and
P[dY15 = 0] agree to within 0.04 across instances. Verdict: no detectable instance dependence (COMPUTED).
The A-half zero channel scales as about 2^-2.4w (2^-14.4 at w = 6, 2^-18.8 at w = 8; GUESS: about 2^-75
at w = 32 unpinned). The filed path pins C3 instead.

1c (COMPUTED, t1c_counter.py -> t1c_counter.txt). The filed path's own trial model. In the filed
construction the counter words appear as q2 = v12 and k2 = v13 (job20 ANSWER.md: "K0.a1 = ROL(K0.d1,16)",
"K1.a1 = ROL(K1.d1,16)"). I reused Grok's FIX7 hand model (compare_models.py; job20 found it
indistinguishable from the exact model), swept q2 = t_lo and k2 = t_hi, and measured the H4 pass rate and
the H4 co-pass of the e1/X2 flips, which are the inputs to the cluster lever. 2^20 samples per case:
- t = 0 (filed), two seeds: sum of the top-8 co-pass 5.675 / 5.680; mean X2 co-pass 0.2585 / 0.2586.
- t_lo in {1, 2, 0x10, 0x8000}: 5.696-5.700; mean X2 0.2589-0.2594, the same as t = 0 within noise (0.004).
- t_lo = random 20-bit (6 values): 5.683-5.695; mean X2 0.2547-0.2564, slightly lower.
- t_lo = random 32-bit (4 values, i.e. a message of up to 4 TB): 5.650-5.682; mean X2 0.242-0.246, lower.
- t_hi != 0 (t >= 2^32): 5.595 and 5.539; x30 0.754/0.751, x31 0.668/0.666, against 0.77/0.70 at t = 0.
  Clearly worse.
- H4 pass rate p0*16 is 0.990-1.008 everywhere (balanced, as job20 found).
Verdict: the counter does move the filed model, but t = 0 is already the best region. A small t is
neutral and a large t costs. No gain for the filed path from the free counter (COMPUTED in the model;
the real pins are assumed reachable for t != 0, which the round-0 bijection makes plausible: DERIVED).

## 3. TEST 2: XOR-fold channel vs zero channel (Rumba's cancellation, in BLAKE3's fold)

Lemma (DERIVED). For the sibling pair, C3 = G(X3,X7,X11,X15; m4,m13) receives only the x-difference
a1' = a1 ^ 8, an additive difference of +-8. Then d1 differs in one bit p = 3 - R0. c1 differs by a carry run
starting at p. b1 differs by that run rotated right by R1, and Y3 = a2 = a1 + b1 + y. Equality a2 = a2' needs
b1' - b1 = -(a1' - a1) = -+8, i.e. an XOR run starting at bit 3. That forces p - R1 = 3 (mod w), i.e.
R0 + R1 = 0 (mod w). At w = 32, 16 + 12 = 28, so dY3 != 0 always and E3 is always active. The same holds at
the toy rotations (w = 6: 3+2; w = 8: 4+3). Confirmed: 0 events in all runs, including 2^18 pairs at
w = 32 with the real IV and rotations (t3_lemmas.txt). The argument uses no constant, so it holds for every
instance (counter, flags, CV).
Consequence: the B half can only close by the fold (dE3_out = swap(dE1_out)), never by zero differences.

Lemma 2 (DERIVED; a necessary condition of the B-half fold for the sibling pair). E1 = G(Y1,Y6,Y11,Y12;
m12,m5) has differences only in c (Y11) and y (m5), so dE1.d1 = 0 and dE1.d2 = rotr(dE1.a2, R2). E3 has a
difference only in a (Y3). The fold conditions out1 (dE1.a2 = dE3.c2) and out4 (dE3.b2 = dE1.d2) then give
   dE3.b1 = dE3.c2 xor rotr(dE3.c2, R2 - R3).
At w = 32 (R2 - R3 = 1): dE3.b1 = dE3.c2 xor rotr(dE3.c2, 1), a 32-bit relation that any Lemma-D pattern must
satisfy. If R2 = R3 it forces dE3.b1 = 0, hence dc1 = dd1 = da1 = 0 and dY3 = 0, which contradicts
Lemma 1. So the B half CANNOT collide at toy rotations with R2 = R3: job28's primary rotations at w = 5
and 6 (2,1,1,1), (3,2,1,1), and its alt rotations at w = 8 (4,3,2,2). Warning for other agents using
those toys: they are degenerate for this event. Confirmed: B = 0 events at w = 5 (2^22 x 8 pairs, about 32
expected at random) and at w = 6 primary (2^24 x 8, about 8 expected).

Measurements (COMPUTED; t2_w6_n24.txt, t2_w8_n24.txt, t2_w5_n22.txt, t2_w6alt_n24.txt, t2b_w6.txt):
- A half, w = 6 primary, 2^27 pairs: zero channel 2^-14.4; fold channel (A equal with dY7 or dY15 != 0)
  10 events = 2^-23.7, against 8 expected for a random 24-bit match. The fold adds nothing above random,
  and the zero channel is 2^9 larger.
- A half, w = 8, 2^27 pairs: fold channel 0 events (0.03 expected at random).
- A half, w = 5 (rots 2,1,1,1, where dY15 = 0 never occurs): A equal only through the fold, at 2^-19.2 to
  2^-22 per instance, around the random 2^-20.
- Per output word, w = 6 primary, 2^24 pairs (t2b): every word is equal at 2^-6.0 (random); the zero
  channel is 2^-11 to 2^-14.3 and the fold channel is 2^-6.0. At the word level nothing beats random.
- B half, w = 6 alternate rotations (3,2,2,1), not degenerate (t2_w6alt_n24.txt, t3_lemmas.txt):
  14 events in 2^27 pairs (per instance 2,5,2,3,0,0,1,1), plus 8 events in a further 2^26 pairs.
  Over all alt runs (2^27.7 pairs, including two t3 runs with 0 events) that is 22 against 13.1 expected for a random 24-bit match: about 1.7x random, i.e. 0.75 bit above it
  (Poisson tail about 1%). All B events went through the fold (the zero channel is impossible by Lemma 1).
  Lemma 2's relation held on all 8 events checked (0 failures). Its premises (dE1.d1 = 0 and
  dE1.d2 = rotr(dE1.a2, R2)) held on every pair, including 2^18 pairs at w = 32 with the real rotations and IV.
  The 5 IV instances gave 20 events against 10 expected; the 3 random-CV instances gave 2 against 3. That
  is too few events to claim any instance dependence.
- A half on the same alt toy: zero channel 2^-14.35 to 2^-14.49; fold 11 events in 2^27 (8 expected).
Verdict on Rumba-style XOR cancellation: in BLAKE3 it is forced for the B half (E3 is always active). Without
the filed path's class conditions it gives only about 1 bit over random at w = 6, and nothing in the A
half. The two instances are coupled and swapped, so Rumba's "same differential twice, independent lists"
structure is absent. Dead as a new path; it is already the mechanism of the filed path's second half,
where the class conditions (not the fold) supply the 27.5 bits.

## 4. What is left

1. Done in the model (TEST 1c): the counter words q2/k2 of the filed construction are best at 0. Not
   modelled: flags 3 instead of 11 changes K3's d input. In the FIX7 model w6 and w7 are free uniform words,
   so K3's constants do not appear there (DERIVED from compare_models.py). A path that pins K3's
   inputs could check flags 3 against 11 in one run. Expected gain: none (GUESS).
   Keep in mind for anyone: the last-chunk trick is a free re-instancing of ANY single-block path. It also
   costs nothing to verify for small t (16t + 1 extra compressions).
2. GUESS. The one transfer not yet run anywhere is a characteristic search that counts only round-1
   conditions, models round 0 by message modification, and needs only the folded output (SipHash/SHA-2
   tools + Keccak's "truncated output" view). Low prior: the 0-difference start of the filed path is only
   possible because of the v14 difference, and equal-length pairs always have dX != 0.
3. Everything else in section 1 is dead or already in use.

## 5. Commands (Windows python 3.14 + numpy; folder scout_cross)
- python -B xtoy.py                 (w=32 check against hash-smash/verifier/blake3.py; prints 0 mismatches)
- python -B t1_tree.py > t1_tree.txt
- python -B t1c_counter.py 20 1 > t1c_counter.txt   (imports exact_model from research\grok\work\job20_copass, read only)
- python -B t2_sibling.py 6 24 5 > t2_w6_n24.txt ; python -B t2_sibling.py 8 24 6 > t2_w8_n24.txt
- python -B t2_sibling.py 5 22 8 > t2_w5_n22.txt ; python -B t2_sibling.py 6 24 21 alt > t2_w6alt_n24.txt
- python -B t2b_words.py 6 24 4 > t2b_w6.txt
- python -B t3_lemmas.py 32 18 ; python -B t3_lemmas.py 6 26 alt   (-> t3_lemmas.txt)
Each t2_sibling run takes about 8 x 55 s; t1c about 3 min; t3 at 2^26 about 4 min.
Files: xtoy.py (toy model, w=32 checked against the reference), t1_tree.py, t1c_counter.py,
t2_sibling.py, t2b_words.py, t3_lemmas.py, pdftext.py, outputs *.txt, papers\ (AFKMR08, LLWDS24 slides with
text extractions), my_pids.txt (PIDs of my background runs; all finished).
- python -B pdftext.py in.pdf out.txt   (crude PDF text extraction used for papers\)

## 6. References (URLs; local copies in papers\ where noted)
- [AFKMR08] Aumasson, Fischer, Khazaei, Meier, Rechberger, New features of Latin dances, FSE 2008. https://www.aumasson.jp/data/papers/AFKMR08.pdf (papers\AFKMR08.pdf/.txt), https://eprint.iacr.org/2007/472
- [2025/1830] A new approach to improved PNB-based attacks on reduced-round ChaCha and Salsa. https://eprint.iacr.org/2025/1830.pdf (abstract via search)
- [2025/437] Improved cryptanalysis of ChaCha: beating PNBs with bit puncturing. https://eprint.iacr.org/2025/437 (abstract via search)
- [2025/2334] Moving a step of ChaCha in syncopated rhythm. https://eprint.iacr.org/2025/2334 (abstract via search)
- [2025/428] On improved cryptanalytic results against ChaCha for reduced rounds >= 7. https://eprint.iacr.org/2025/428.pdf (abstract via search)
- [BLT20] Beierle, Leander, Todo, Improved differential-linear attacks with applications to ARX ciphers, CRYPTO 2020. https://eprint.iacr.org/2020/775
- [KNR10] Khovratovich, Nikolic, Rechberger, Rotational rebound attacks on reduced Skein. https://eprint.iacr.org/2010/538
- [DMS14] Dobraunig, Mendel, Schlaeffer, Differential cryptanalysis of SipHash, SAC 2014. https://eprint.iacr.org/2014/722
- [BV14] Biryukov, Velichkov, Automatic search for differential trails in ARX ciphers, CT-RSA 2014 (via the search result for BVL16; not fetched). [BVL16] Biryukov, Velichkov, Le Corre, Automatic search for the best trails in ARX: application to block cipher Speck, FSE 2016. https://eprint.iacr.org/2016/409
- [Din14] Dinur, Improved differential cryptanalysis of round-reduced Speck, SAC 2014. https://eprint.iacr.org/2014/320
- [Leu16] Leurent, Improved differential-linear cryptanalysis of 7-round Chaskey with partitioning, EUROCRYPT 2016. https://eprint.iacr.org/2015/968
- [BC04] Biham, Chen, Near-collisions of SHA-0, CRYPTO 2004. https://eprint.iacr.org/2004/146
- [Kli06] Klima, Tunnels in hash functions: MD5 collisions within a minute. https://eprint.iacr.org/2006/105
- [JP07] Joux, Peyrin, Hash functions and the (amplified) boomerang attack, CRYPTO 2007. https://www.iacr.org/archive/crypto2007/46220242/46220242.pdf
- [SBKAM17] Stevens, Bursztein, Karpman, Albertini, Markov, The first collision for full SHA-1. https://eprint.iacr.org/2017/190
- [MNS13] Mendel, Nad, Schlaeffer, Improving local collisions: new attacks on reduced SHA-256, EUROCRYPT 2013, doi 10.1007/978-3-642-38348-9_16 (two-block, 31 steps, 2^65.5; per search summaries and LLWDS24 slides)
- [LLWDS24] Li, Liu, Wang, Dong, Sun, The first practical collision for 31-step SHA-256, ASIACRYPT 2024. Slides: https://iacr.org/submit/files/slides/2024/asiacrypt/asiacrypt2024/64/64_slides.pdf (papers\LLWDS24_slides.pdf/.txt)
- [2026/232] Zhang, Li, Gao, Wang, Collision attacks on SHA-256 up to 37 steps with improved trail search. https://eprint.iacr.org/2026/232 (abstract only)
- [LP20] Leurent, Peyrin, SHA-1 is a shambles. https://eprint.iacr.org/2020/014
- [Pey10] Peyrin, Improved differential attacks for ECHO and Grostl (internal differentials). https://eprint.iacr.org/2010/223
- [DDS13] Dinur, Dunkelman, Shamir, Collision attacks on up to 5 rounds of SHA-3 using generalized internal differentials. https://eprint.iacr.org/2012/672
- [ZHL23] Zhang, Hou, Liu, Collision attacks on round-reduced SHA-3 using conditional internal differentials, EUROCRYPT 2023. https://www.iacr.org/archive/eurocrypt2023/14004425/14004425.pdf
- [DDS12] Dinur, Dunkelman, Shamir, New attacks on Keccak-224 and Keccak-256 (target difference algorithm), FSE 2012. https://eprint.iacr.org/2011/624
- [QSLG17] Qiao, Song, Liu, Guo, New collision attacks on round-reduced Keccak. https://eprint.iacr.org/2017/128 (as in LITERATURE)
- [GLS16] Guo, Liu, Song, Linear structures. https://eprint.iacr.org/2016/878 (as in LITERATURE)
- [Wag02] Wagner, A generalized birthday problem, CRYPTO 2002. https://people.eecs.berkeley.edu/~daw/papers/genbday.html
- [GM20] Gunsing, Mennink, The summation-truncation hybrid, CRYPTO 2020. https://iacr.org/archive/crypto2020/12171202/12171202.pdf
- [MRST09] Mendel, Rechberger, Schlaeffer, Thomsen, The rebound attack, FSE 2009 (via https://en.wikipedia.org/wiki/Rebound_attack). [GP10] Gilbert, Peyrin, Super-Sbox cryptanalysis. https://eprint.iacr.org/2009/531
- [LX09] Li, Xu, Attacks on round-reduced BLAKE. https://eprint.iacr.org/2009/238 (as in LITERATURE)
- Organizer reference: ./hash-smash/verifier/blake3.py and target-profiles\blake3-r2-prefix-v1.json ("Prefix rounds 0 through 1 ... in every chunk, parent and root compression").

Search limits: no BLAKE3-specific reduced-round paper found (extended search, 2025-2026). The only "BLAKE3
2.5 rounds" claims I saw were blog pages (https://shattered.io/blake3-vs-sha256-2026/ and others), with no
paper behind them; LITERATURE traces them to LX09's free-start result. Bernstein's Rumba20 page did not
load. MNS13 was not read in full.
