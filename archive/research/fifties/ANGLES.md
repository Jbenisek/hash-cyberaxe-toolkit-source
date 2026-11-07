# ANGLES: eight untried angles for a 2-round BLAKE3 collision (2026-10-09)

Read: scouts/EDGES_FIBRE.md (all 14 items), NEW_PATHS.md (all), END_OF_LINE.md (headings; sections 2, 3.1, 3.5, 3.7, 3.8, 4.1, 5).
None of the eight is closed there. Labels: PROVED / MEASURED / DERIVED (exact arithmetic or algebra) / GUESS.
Scratch checks ran from the session scratchpad (angles\mover.py, c3len.py, pins.py), not from the workspace.
Bottom line: only angle 1, backed by 2 and 3, aims at the sub-60 condition in EDGES_FIBRE item 3. That depends on
the track allowing multi-chunk messages, which nobody has checked yet. Every other angle is worth 2 bits or less (GUESS).

## Measured while writing
- M1 MEASURED: the chunk-index mover (angle 1) leaves the whole post-round-0 state unchanged. Checked on 2,000 random
  55-byte blocks with counters below 2^20: 0 mismatches. The 63-byte twin at the moved counter shares that state too
  (2,000 of 2,000). DERIVED: it is the same identity as the 55/63 K2 length cancellation.
- M2 MEASURED: with the documented pins (X3,X7,X11,X15,W4,W13 from END_OF_LINE section 2), a reconstructed round-1 C3
  reproduces the 55/63 free half: Y7 and Y15 are equal, dY3 = fff8ffff, dY11 = fff77ffb. No other block length in
  1..64 keeps it (0 of 62).
- M3 MEASURED: with random pins, the free half holds for a given partner length in 0 of 2^26 draws, for each of 13
  lengths. So P < 2^-24.4 at 95 per cent.
- MEASURED (1 case) + DERIVED: changing flags from 11 to 3 and re-solving m6 and m7 in K3 keeps the post-round-0 state.

## 1. Chunk-index movers: 2^32 new trials per base that leave round 0 untouched (rank 1; chance GUESS medium, size up to 6+ bits)
Mechanism: put the twins in the final chunk of an (i+1)-chunk message: lengths 1024i+55 and 1024i+63, with the same
first i chunks (any content). That final chunk is one block, with counter i in v12, v13 = 0 when i < 2^32, and
flags CHUNK_START|CHUNK_END = 3. K0 is G(IV0,IV4,IV0,i; m0,m1). Move i to i' with a1' = a1 xor (i xor i'),
m0' = a1' - IV0 - IV4 and m1' = m1 + a1 - a1': K0's output stays the same, and so does the whole post-round-0 state (M1).
In round 1, m0 is C2's second word and m1 is E0's first word. A mover therefore changes only Y2, Y6, Y10, Y14 and E0.
E0 is on half A, which both twins share, so the free half holds (DERIVED from the schedule). In a single block,
fixing the post-round-0 state and m4..m15 fixes m0..m3, because G's input and output determine its message words
(DERIVED). The counter adds 2^32 trials per base. v13 adds 2^22 more, but those change C0 and C1 (and with them Y4's
class) and need messages of at least 4 TiB.
Why >= 2 bits: EDGES item 3 says sub-60 needs m >= 2^27.06 trials sharing K's constants, against 2^21 now. If K's 18
constants do not read Y6, Y14 or m1, each mover is a new trial on the same table. Then i < 2^7 (128 KiB messages)
covers the missing 6.06 bits (DERIVED from their figures; their curve is cited, not rechecked). A mover costs 7 word
ops before the E-side work (C2's second half, DERIVED).
Might fail: (a) the track limits messages to one block or chunk, or caps the length. (b) K reads Y6 (E1.b) or
Y14 (E3.d). Then every mover is a new frame and the only gain is a cheaper rebuild. (c) Pins and classes must be
rebuilt for flags 3: v15 feeds K3, and the m6/m7 re-solve moves C0.y and C2.x. (d) Mover trials are correlated
within a base.
Test (< 1 h): read the track's message and mode limits (minutes). In the frame builder, set flags 3 and apply 2^10
movers to each of 64 bases; count changed K constants. On the 3090, compare stage pass rates over 2^32 mover trials
and 2^32 ordinary trials. If they agree within 3 sd, the angle is alive. If any K constant changes, only angle 2's gain remains.

## 2. Mover-invariant staging (rank 2; chance GUESS medium if 1 is allowed, size GUESS 0.5-1 bit)
Mechanism: a stage condition whose inputs avoid Y2, Y6, Y10, Y14 and m1 is the same for all movers of a base
(DERIVED). E3's first step a1 = Y3 + Y4 + m15 (the carry pattern of the a-slot difference) is invariant. E1's
a1 = Y1 + Y6 + m12 is not. Pay the invariant conditions once per base, then run only the rest per mover.
Why: the cost per surviving trial falls by the invariant share of stage A.
Might fail: the per-trial charge is a small part of the total (frames dominate), or few conditions are invariant.
Test (minutes, CPU): tag each stage-A and E1-acceptance condition with its input words from the program; add up the
ops and the pass probability of the invariant ones.

## 3. Solve E3's carries through Y14 instead of filtering (rank 3; chance GUESS low-medium, size GUESS 0.5-2 bits)
Mechanism: Y14 = rotr(d1 xor (a1 + b1 + m0), 8) inside C2 is a bijection of m0, and so of the counter (DERIVED).
In E3, d1 = rotr(Y14 xor a1, 16) is a bijection of Y14, and c1 = Y9 + d1 carries the a-slot difference. List the
d1 values that give the wanted carry pattern bit by bit (carries run upward) and map them back to counters. Those
movers pass E3's c1 conditions with certainty. Y6 (E1.b) follows and stays random. Next rung: b1 = rotr(Y4 xor c1, 12).
Why: a filter becomes an enumeration. Supply per base stays the same; the cost per surviving trial falls by about
1/p_c1 on that stage.
Might fail: hitting an arbitrary m0 needs the full 2^32 counter range (messages up to 4 TiB). With i < 2^k only
2^(k-32) of the solutions can be reached. The current class may already fix these carries.
Test (< 1 h, CPU): over 1,024 bases, list the good-d1 set, map it to counters, check that all pass, and check that
E1 acceptance on those movers matches the ordinary rate.

## 4. Multi-length k-tuplets on one base (rank 4; chance GUESS low, size <= 1.58 bits for k=3, <= 2.58 for k=4, DERIVED caps)
Mechanism: the K2 cancellation is exact for any pair of block lengths and any m4 (a1' = a1 xor (L xor L'), DERIVED;
the check passed for all 63 partners). One base can carry k lengths that share every word except m4 and m5, if
round-1 C3 keeps Y7 and Y15 for each partner: k-1 conditions of 64 bits each on the six pins. k messages give
k(k-1)/2 pairs with equal half A. Each extra member costs about two E-side G calls; C3 is pinned, so it is a constant.
Single-bit partners of 63 are 62, 61, 59, 55 and 47 (47 keeps 376 free bits).
Might fail: M2 and M3 show the current pins serve no other length and random pins almost never do, so pins must be
constructed. The other families were 3 to 4 bits poorer (END_OF_LINE 3.8). A pair 2^-3.3 as rich adds only
log2(1 + 2^-3.3) = 0.14 bit (DERIVED).
Test (< 1 h): run kissat on the six pin words with the C3 conditions for {55, 63, L3}, L3 in {47, 59, 61, 62} (a tiny
CNF). If one is satisfiable, measure the stage-1 rate of (L3, 63) against (55, 63) over 2^32 trials on the 3090.
Kill the angle if no pins exist or the rate ratio is below 1/4.

## 5. Narrow-lane early abort (rank 5; chance GUESS low-medium, size GUESS <= 2 bits on stage A)
Mechanism: a condition on the low t bits of an addition whose inputs arrive without a rotation (E3 a1 = Y3+Y4+m15;
E1 a1 = Y1+Y6+m12) needs only the inputs' low t bits. Such conditions fit in (t+1)-bit lanes: 256/(t+1) trials per
word op instead of 7 (36-bit lanes, END_OF_LINE section 2). For t = 8 that is 28 lanes, 4 times as many (DERIVED).
Might fail: the cost model or the judge refuses sub-word lanes (count as written); the leaders already do this; few
conditions depend only on low bits.
Test (minutes): read how collision-frontier-v5 defines ops and lanes; list the stage-A conditions with their bit
ranges and rotation depth; price them.

## 6. Tabulate per-frame tables by their true key (rank 6; chance GUESS low, size large: removes the m condition)
Mechanism: memory is free. K's image over g covers 0.6321 of 2^32 (EDGES item 7). If a frame's table depends on
fewer bits than all 18 constants, build every table once (2^31.3 builds) and replace each per-frame build with a lookup.
Might fail: EDGES items 5 and 14 say the constants fix the frame, so the table may read all 576 constant bits.
Test (< 1 h, GPU): hash the contents of 2^20 sampled tables and count duplicates. If the key is a k with 2^31.3
values, expect 2^40 / 2^32.34, about 200 (DERIVED). Zero duplicates means the key space is above about 2^39: closed.

## 7. Low algebraic degree in member and mover bits (rank 7; chance GUESS low, size d bits per solvable condition)
Mechanism: compute the ANF of each stage-A condition bit and each residual bit as a function of the 21 cube bits c1
(Moebius transform over 2^21 points) and of the low 20 counter bits. A condition of degree <= 2 in 10 or more
variables can be solved per frame, by enumerating its solutions, instead of filtered.
Might fail: END_OF_LINE 4.1 found no neutral bit, and rule A survives a flip in at most 2 x 2^-8 of trials. Two
ARX rounds are probably at full degree.
Test (minutes, CPU): run the Moebius transform on 16 frames and histogram the degrees. Kill the angle if no bit has degree <= 3.

## 8. Two-block final chunk: the chaining value as 256 tunable bits (rank 8; chance GUESS low, size unknown)
Mechanism: lengths 64+55 and 64+63 with a shared first block P. Block 2 starts from h = CV(P) instead of the IV,
with flags 2 (or 10 at the root), and can be combined with angle 1. Each draw of h costs one compression. 2^50 draws
cost about 0.001 bit at 2^60 (DERIVED) and buy about 50 bit-conditions on h. The a-slot words h0..h3 are absorbed by
m0, m2, m4 and m6 (DERIVED), so the effect comes through h4..h7. The IV is the only fixed input that the class and
pin searches never moved. A richer class, or a pin set that serves k lengths (angle 4), may need it.
Might fail: the rate barely moves with constants: outer words moved it by +-8.4% (END_OF_LINE 3.5), and the best of
4,432 pin values was better by one part in a million.
Test (< 1 h): run 64 random h values through the class or stage-1 counter. A rate spread below 10% closes it.

## Closed by inspection while writing (DERIVED; do not redo)
- A 55-byte block has exactly one 63-byte K2 partner: G's input state and output fix (m4', m5'). No multi-partner trick.
- Twins with difference 8 are exactly the pairs (L, L xor 8) with bit 3 of L clear. L = 55 has the most free bits (440).
- Differences in the 63-byte twin's padding words (m13's top byte, m14, m15) meet an equal state in D2/D3, so their
  outputs differ (by the uniqueness above) and the difference spreads to both halves.
- Counters give no E1/E3 product structure (NEW_PATHS idea 2). Each mover feeds one round-1 column, and every column
  feeds both E1 and E3 (C2: Y6 and Y14; v13 through C0 and C1: Y4, Y12, Y1, Y9).
- No cheaper mover from the chaining value: changing h changes all eight words, and only the a-slot words can be absorbed.
