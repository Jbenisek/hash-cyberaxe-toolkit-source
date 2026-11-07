# AROUND: the tree as a difference or a knob (folder counter_swing\around)

Written 2026-10-08. Research only: no yukon, nothing filed, posted or cancelled, trace untouched, no credential
file opened, nothing written outside this folder, pkg11 not touched. The organizer verifier was copied here as
org_blake3.py (SHA-256 bf67aca2...0237, identical to hash-smash\verifier\blake3.py) and is the referee for every tree
or flag claim. Tags: COMPUTED = run here (file named). DERIVED = follows from a stated argument or a named source.
GUESS = judgement.

The question was the "swing" of the counter method: the counter as a DIFFERENCE instead of a shared free word,
a parent node instead of a chunk, a chunk root against a parent root, and anything else the tree, the flags or
the counters allow. Each idea is judged on its own (section 9 has the table).

## 0. Short answer

1. **Where one colliding compression can sit (COMPUTED, tree_align.txt).** For two messages with different chunk
   counts n1 < n2 <= 128 (all 16,256 ordered pairs), a single compression collision can sit only at
   - a parent-parent pair (same parameters, the difference is in the message alone), or
   - the LAST chunk of the shorter message against a parent node of the longer one. This needs n2 = t + q with
     t = n1 - 1 and 2 <= q <= lowbit(t), or t = 0 (the root level).

   A pure counter difference (two leaves with different chunk indices) is never one of them: 0 cases. Planted
   leaf-vs-parent collisions on the organizer's verifier agree with that rule in 52/52 cases.
2. **The earlier "counter difference is dead" verdict stands, with a corrected reason (COMPUTED + DERIVED).**
   - A counter difference only ever comes together with the flags difference, in a leaf-vs-parent pair.
   - In that pair, round 0 cancels EXACTLY. 500/500 per case at 32 bits on the organizer's own _compress and
     _chunk_output/_parent_output, for t = 0, 2, 2^31, 2^32, 5*2^32, 2^50, 2^32+2 and (2^19-1)*2^32.
   - At 1 round this gives real full collisions of messages with different chunk counts: 200/200 on the
     organizer's blake3(rounds=1) (r1_demo.txt). At 2 rounds it dies in round 1.
3. **Where each state difference goes in round 1 (COMPUTED at w = 32 and in toys; DERIVED from the permutation).**
   - v12 (counter low word) goes to m0 and m1, then to C2.y and E0.x.
   - v13 (counter high word) goes to m2 and m3, then to C0.x and C1.x.
   - v14 (length) goes to m4 and m5, then to C3.x and E1.y. This is the 55/63 path.
   - v15 (flags) goes to m6 and m7, then to C0.y and C2.x.

   A y-only difference in a G call changes all four outputs, with certainty (Lemma G3; COMPUTED 100% at every
   width). So the flags difference alone kills both digest halves. That covers the root level (flags 11 vs 12)
   and every non-root t below 2^32.
4. **The one non-fatal flags route: t a multiple of 2^32 (COMPUTED).**
   - There v13 sends m2 to C0.x, so C0 has x and y differences instead of y alone.
   - Round 1 then has C0 (x, y), C1 (x) and C2 (x) active, and no E-step message difference.
   - A free half needs three two-word patterns. Measured at random states: C0 2^-16.4, C1 2^-16.9, C2 2^-21.0 at
     w = 8. At w = 10 they fall to 2^-19.6, 2^-21.7 and below 2^-24; at w = 12 to about 2^-23 to 2^-24 or
     none; at w = 16 there is none in 2^24.
   - They cannot be pinned: the state entering round 1 is the parent's, and its block is two child CVs that the
     attacker cannot steer.
   - Its own cost: about 2^256 per pair trial, worse than birthday. It also needs messages of at least 4 TiB.
     Does not work.
5. **A collision at a parent node (item 3) cannot beat birthday (DERIVED, Lemma G2; COMPUTED parent_up.txt).**
   - A G call with the same input state is injective in its message words. So any difference in the parent block
     survives round 0: 0 of 2^18 at w = 32, and 16 of 16 words differ on average when the right child
     half-collides.
   - The block is two uncontrollable child CVs. The best is generic: 2^128 parent outputs, plus one child
     compression each (about 2^129).
6. **Other knobs (item 4).**
   - **CV difference (two-block "swing" of the length trick; COMPUTED routing, DERIVED cost).** A difference in a
     chained CV word h0..h3 is absorbed by one x word.
     - h2 alone gives the cleanest round-1 footprint of any source: C3.x only, with no E-step difference (the
       55/63 path also has E1.y).
     - h0 and h3 alone are fatal (y-only calls).
     - The price: the earlier block must give a 224-bit partial collision, 2^112 by birthday. Not competitive.
   - The CHUNK_START bit (flags 2 vs 3) and the ROOT bit are never differences on their own.
   - The parent has no free state word. The only per-trial free state words in the whole tree are the leaf
     counter (t_lo; t_hi is counter_next's).
7. **New concern for the organizers (COMPUTED).** Tree mode lets a non-root chunk compression be compared with
   a parent compression, which turns the counter and flags into a state difference.
   - At 1 round that is an exact full collision of messages of different chunk counts (64 bytes against 1,025
     bytes or more).
   - At 2 rounds what stops it is the message permutation (m6 lands in C0's y slot) and the fact that the parent
     block is made of CVs. It is not stopped by round 0.

## 1. Where can ONE colliding compression sit? (tree_align.py -> tree_align.txt)

What was checked:
- Part 1, own recursive tree: largest power-of-two left subtree, built from the organizer's own _chunk_output,
  _parent_output and _compress. It equals the organizer's blake3(rounds = 2) in 280/280 cases (n = 1..40 chunks;
  last chunk 1, 55, 63, 64, 65, 700 or 1024 bytes). COMPUTED.
- Part 2, every node pair (u1, u2) of the trees of n1 and n2 chunks (n1 != n2, both up to 128) where one
  compression collision, with all other aligned subtrees identical, gives equal digests. COMPUTED counts:

| placement | tree-1 node | tree-2 node | count |
|---|---|---|---|
| leaf-parent, non-root | last chunk | parent | 321 (and 321 mirrored) |
| leaf-parent, root level | last chunk = whole message (n1 = 1) | root parent | 127 (and 127 mirrored) |
| parent-parent | parent | parent | 23,040 (7,038 non-root + 16,002 root) |
| leaf-leaf, different chunk index (pure counter difference) | - | - | **0** |
| leaf-parent where the leaf is a FULL chunk (chained cv) | - | - | **0** |

- Every leaf-parent case has n2 = t + q, with t = n1 - 1, and 2 <= q <= lowbit(t), or t = 0. DERIVED reason: the
  stack after t chunks holds subtrees sized by the binary digits of t. The longer message keeps the same stack
  only if its extra q chunks fit under the smallest one.
- Part 3, planted on the organizer's verifier: M1 = P||X (t chunks plus a 64-byte X) and M2 = P||Q (q more
  chunks). The organizer's _compress was patched so that ONLY M1's last-chunk call returns M2's parent-node output.
  The digests are equal exactly when q <= lowbit(t): 52/52 as predicted (t = 1..64, q = 2..8). COMPUTED.
- Consequences (DERIVED):
  - The last chunks of two messages with different chunk counts are never compared with each other, so "two
    last-chunk compressions with different counters" does not occur in a one-collision attack.
  - A leaf-vs-parent pair always has the leaf as the last chunk of the shorter message. A one-block leaf has
    cv = IV and flags 3 (11 at the root). The parent has cv = IV, counter 0, length 64, flags 4 (12 at the root).

## 2. State differences and where round 1 sends them

Three exact facts about one G call (DERIVED by inverting G; the organizer's _g is the definition):
- **G1.** From the outputs alone, c1 = c2 - d2, d1 = ROL(d2, 8) ^ a2 and b1 = ROL(b2, 7) ^ c2. So the inputs
  c = c1 - d1 and b = ROL(b1, 12) ^ c1 are fixed by the output. Two calls with equal outputs have equal b and c.
  Only a and d differences can be absorbed, by x and y.
- **G2.** For one input state, G is injective in (x, y): equal outputs give equal a1, so y and then x are equal.
  A message difference with no state difference therefore always reaches the output.
- **G3.** If only y differs, then a2, then d2, then c2, then b2 all differ. That is certain.

Absorption: a d difference in column c is cancelled by x' = (a1 ^ d ^ d') - a - b and y' = y + a1 - a1'. An a
difference (a CV word 0..3) is cancelled by x alone.

Round-1 routing, with all 16 state words equal after round 0 (r0eq = 1 in every case), from route_out.txt and
cvdiff.txt (COMPUTED; 2^20 trials at w = 32, 2^24 at w = 8..16):

| source | absorbing words | round-1 calls hit | can it occur in the tree? | verdict |
|---|---|---|---|---|
| v12, counter low word | m0, m1 | C2.y, E0.x | only leaf-vs-parent, t mod 2^32 != 0 | fatal alone (C2.y) |
| v13, counter high word | m2, m3 | C0.x, C1.x | only leaf-vs-parent, t >= 2^32 | never alone (0 tree cases); the cleanest d source |
| v14, length | m4, m5 | C3.x, E1.y | same position, last block (55/63) | the board's path |
| v15, flags 3/11 vs 4/12 | m6, m7 | C0.y, C2.x | only leaf-vs-parent or root level | fatal unless v13 also differs |
| h0, CV word 0 | m0 | C2.y | multi-block chunk, earlier-block difference | fatal |
| h1 | m2 | C0.x | same | one pattern |
| h2 | m4 | C3.x | same | the cleanest of all: one x-only call, no E difference |
| h3 | m6 | C0.y | same | fatal unless h1 too |
| h4..h7 | - | - | - | cannot be absorbed (G1): costs 2^-128 |

- Fatal means a y-only C call. All four of its outputs differ in 100% of trials at w = 32 and in the toys (Lemma
  G3), so both digest halves receive differences.
- Patterns in the toys (route_out.txt, w = 8; rates per trial at random state values):

| configuration | C0 half-A / half-B pattern | C1 | C2 | C3 | half A equal |
|---|---|---|---|---|---|
| F_root (flags 11 vs 12) | 0 / 0 (y only) | - | 2^-22.4 / 0 | - | 0 |
| N_lo (t < 2^32) | 0 / 0 (y only) | - | 2^-19.1 / 0 | - | 0 |
| N_hi (t = k 2^32) | 2^-16.4 / 2^-16.4 | 2^-16.9 / 2^-17.2 | 2^-21.0 / 0 | - | 0 (needs all three) |
| N_hi, k = 1 | 2^-24.0 / 2^-19.5 | 0 / 0 | 2^-22.4 / 0 | - | 0 |
| LEN 55/63, unpinned (reference) | - | - | - | 2^-19.2 / 0 | 2^-19.2 = the C3 pattern |
| HYP v13 only | 2^-17.0 / 2^-17.4 | 2^-17.2 / 2^-17.2 | - | - | 0 (needs both) |
| CV h2 only (cvdiff.txt) | - | - | - | 57 and 65 in 2^23 (about 2^-17.1) | equals the pattern count |

  Every rate falls as w grows (route_out.txt). For N_hi C0: 2^-16.4 at w = 8, 2^-19.6 at w = 10, about 2^-24
  (1 hit) at w = 12, none at w = 16. That is about 2 bits per bit of width, so GUESS about 2^-64 or less per
  pattern at 32 bits.
  Low-weight differences make patterns rarer: the flags give |dx| <= 7, k = 1 gives a one-bit d. Without a pin
  they are worse than random.
- The 55/63 row shows what a pin does. Its free half appears exactly when the C3 pattern holds (28 = 28). The
  board makes that pattern certain by choosing C3's input values (pins), which needs a free message on the side
  that sets the round-0 state.

## 3. Item (1): a chunk root against a parent root (root level, t = 0)

- Which words differ (COMPUTED, absorb32.txt):
  - v15: 11 vs 12 (XOR 7).
  - v14: only if the chunk block is shorter than 64. Then the chunk side must carry zero bytes in words copied from
    the parent's block (child CVs), at 2^-8 per byte, so L = 64 is the only free choice (DERIVED).
  - The message: the chunk's 16 words copy the parent's block CV(Y) || CV(Z) except m6 and m7.
  - Counter: 0 on both sides.
- Round 0 cancels exactly: 500/500 at 32 bits on the organizer's functions. At 1 round the digests are equal:
  40/40 real pairs (64 bytes against 1,025 to 2,048 bytes). COMPUTED.
- Round 1: m6 is C0's y word. By G3, all four C0 outputs differ in every trial. C0 feeds E0.a, E2.c (half A) and
  E1.d, E3.b (half B), so neither half can be free. C2.x adds more. (COMPUTED 2^20/2^20; this re-derives the blake2
  agent's path F.)
- Flags 10 (the root block of a multi-block chunk, cv = chained h) against a parent: needs h4..h7 = IV4..IV7
  (G1), a fixed 128-bit target. Dead. (DERIVED)
- The parent side's cost when its words come from child chunks (DERIVED; GUESS on the price per word):
  - A fresh half of the block (8 words) costs one compression: a one-block right child, or the last block of
    the full left child with its first 15 blocks cached.
  - A chosen value in a child-CV word costs about 2^32 per word; no shortcut is known.
  - The fixed left child can be pre-selected under the 2^86-preprocessing convention, for about 2 pinned words.
  - None of that helps. Every round-1 input depends on the round-0 diagonal step, which reads m8..m15, the
    per-trial child.
- Verdict: does not work. Its own cost is about 2^256 per pair trial (both halves at 2^-128), so it falls back to
  generic birthday at 2^128. (DERIVED)

## 4. Item (2): two messages with different chunk counts, re-checked

- The old verdict (blake2 B6, sidepaths S5, nb_report section 4) said a counter difference needs two tree
  positions, hence a leaf-vs-parent or parent collision, and called it generic. Section 1 confirms the alignment
  part exactly (COMPUTED): 0 pure counter-difference placements.
- One correction (COMPUTED): "generic" does not apply in round 0. Leaf-vs-parent cancels exactly in round 0 for
  every allowed t, including t >= 2^32 (absorb32.txt). Round 1 and the uncontrollable parent block are what make
  it fail (sections 3 and 5).
- Verdict: dead, with these reasons.

## 5. The non-root leaf-vs-parent pair (items 1 and 2 combined)

- Placement: M1 = P||X, with t chunks and a one-block X (flags 3, counter t). M2 = P||Y||Z, whose parent over
  chunks t and t+1 (flags 4, counter 0, block CV(Y)||CV(Z)) sits where X sits. This needs t even (q = 2 <=
  lowbit(t)). COMPUTED on the verifier for small t (section 1).
- t < 2^32 (N_lo): v12 and v15 differ, with m0, m1, m6 and m7 absorbing. C0.y is y-only, so it is fatal as at the
  root. Dead. (COMPUTED)
- t = k * 2^32, with 1 <= k < 2^19 (N_hi): v12 is equal and v13 = k. Absorbing words m2, m3, m6, m7.
  - Round 1: C0 has x and y, C1 has x, C2 has x, C3 is clean, and the E step has no message difference.
  - It is the only flags configuration in the tree with no y-only call. (COMPUTED dY pattern xxx.xxx.xxx.xxx.)
  - A free half A needs three two-word patterns (C0: a, c equal; C1: b, d equal; C2: a, c equal). They hold
    together with probability about 2^-190 or less at 32 bits (GUESS from the toy slopes). Paying half A as a
    random 128-bit event is cheaper.
  - So per pair trial about 2^-256. Each trial costs about 3 compressions: a new right child, the leaf and the
    parent.
  - k is free per pair (19 bits), but it is not a cheap knob. Changing k changes t, and so the chunk indices of
    both children. That re-draws the whole parent block: about 17 compressions, since all 16 blocks of the full
    child Y use counter t. It is no cheaper than a fresh trial, and C2's difference comes from the flags anyway.
    (DERIVED)
  - Messages have at least 2^32 chunks (4 TiB or more). (DERIVED)
- t = k * 2^32 + j (N_lohi): adds C2.y and E0.x on top of N_hi. Worse. (COMPUTED)
- Verdict: does not work. Round 0 is exact, but every round-1 condition falls on a state the attacker cannot
  choose.

## 6. Item (3): a collision at a parent node (parent_up.py -> parent_up.txt)

- Both parents share cv, counter, length and flags, so the difference is in the message only. By G2, round 0
  never cancels. COMPUTED: 0 of 2^18 at w = 32 and 0 of 2^23 at w = 8 in all three cases:
  - right child half-collides, so m9, m11, m12, m14 differ: 16.00 of 16 words differ after round 0;
  - one word m8 differs: 4.00 words differ;
  - m2 and m3 differ: 16.00 words differ.
- There is no free half (sidepaths S10 agrees). The block is two child CVs, so the attacker cannot steer it.
- What a sub-birthday parent collision would need:
  - a block difference that survives 2 rounds with probability above 2^-128 (the best XOR trail found was 2^-821,
    blake2 B1);
  - AND a cheap way to produce children whose CVs carry exactly that difference. That is a near-collision of
    children: 2^112 for one differing word.
- Moving the 55/63 residual up one level (the last chunk half-collides, the parent finishes) is the first case
  above: dead.
- Own cost: generic, about 2^129 (2^128 parent outputs plus one child compression each). (DERIVED)

## 7. Item (4): anything else the tree, the flags or the counters allow

1. **CV difference (two blocks; cvdiff.py -> cvdiff.txt).** In the last block of a multi-block chunk, a
   difference in h0..h3 is absorbed by one x word.
   - COMPUTED: round 0 equal 262,144/262,144 per case at w = 32.
   - h2 alone gives C3.x and nothing else. That is cleaner than the length path, which also has E1.y. At w = 8 the
     free half appears exactly when the C3 pattern holds (57 / 2^23).
   - The last-block message is free, so a C3 pin could be chosen as on the board. But the x difference is now
     the constant -(h2' - h2), a random value set by the earlier block, and nobody has checked whether a pin
     exists for such a value. (GUESS: for some fraction of values.)
   - The price is the earlier block: 7 of 8 CV words equal, a 224-bit partial collision, 2^112. All blocks before
     the last have length 64 and the same counter, so the difference must come from the message alone (DERIVED).
   - With h1 and h2 together: 192 bits (2^96) and two patterns.
   - Own cost about 2^112 (DERIVED; GUESS that the second-block residual does not dominate).
   - Not competitive. It is a distinct path with its own concern: "a CV difference in word 2 is the cleanest
     round-1 footprint".
2. **CHUNK_START bit (flags 2 vs 3 at the same position).** It comes only with a CV difference: a multi-block
   last chunk against a one-block one. It needs h4..h7 = IV4..IV7 (G1), 2^128. Even when planted, it activates
   C0 (x, y), C2 (x, y) and C3 (x). Dead. (DERIVED + COMPUTED planted, cvdiff.txt)
3. **The ROOT bit** is fixed by message length. It differs only in the root-level pair of section 3. (COMPUTED,
   section 1)
4. **Free words.** Parents have none: counter 0, length 64 and flags fixed. Their block is CVs. The prefix P sets
   only t (R3 of nb_report). The leaf counter is the only per-trial free state word in the tree. Its high word is
   the counter_next agents' item and is not repeated here. (DERIVED)
5. **1 round (side result, COMPUTED r1_demo.txt).**
   - The leaf-vs-parent pair is an exact full collision of the organizer's blake3(rounds=1): 200/200 pairs, t = 0,
     2, 4, 6, 8. Example: a 64-byte message against a 1,172-byte one, both printed in hex.
   - It is structurally distinct from the known r1 entry (length path, accepted f0dab7bd at 2): different chunk
     counts, a flags difference and no zero-fill constraint.
   - Own cost: 17 one-round compressions (the full left child plus the right child), log2 about 4.1. Not better
     than 2.
   - It is listed for the "many paths" goal only. The owner decides whether it matters; nothing was filed.

## 8. Concerns for the organizers (new here)

- **C-tree-1.** Tree mode compares a non-root chunk compression with a parent compression whenever two messages
  have chunk counts t + 1 and t + q, with 2 <= q <= lowbit(t), or t = 0. The counter, the flags and (for short
  chunks) the length then become a state difference.
  - Round 0 cancels it exactly at every t, which gives real full collisions at 1 round.
  - At 2 rounds, what protects it is the message permutation (m6 goes to C0's y slot) and the fact that a
    parent's block is two CVs. The rounds do not.
  - The single exception (t a multiple of 2^32) needs 4-TiB messages and still has three unpinnable patterns.
    (COMPUTED + DERIVED)
- **C-tree-2.** Of all the state words that can differ, the counter's high word v13 would be the cleanest d
  source: two x-only round-1 calls and no E-step message difference. The tree never aligns two leaves with
  different counters, so it only ever appears next to the flags difference. (COMPUTED)
- **C-tree-3.** A CV difference in word 2 has the smallest round-1 footprint of any difference source: one x-only
  call. It is kept out of reach only by the 224-bit near-collision that the earlier block must deliver.
  (COMPUTED routing; DERIVED cost)

## 9. Methods, each on its own

| # | idea | own cost (log2) | what it needs | concern it shows | status |
|---|---|---|---|---|---|
| A1 | chunk root (flags 11) vs parent root (flags 12) | 256 per pair trial; falls back to 128 | nothing; it fails in round 1 | m6 sits in C0's y slot: the flags difference reaches both halves | COMPUTED (routing) + DERIVED (cost) |
| A2 | non-root leaf vs parent, t < 2^32 | 256 | the same | the same, plus C2.y and E0.x | COMPUTED + DERIVED |
| A3 | non-root leaf vs parent, t = k 2^32 | about 257.6 (2^-256 per trial, 3 compressions each) | three two-word patterns that cannot be pinned; 4 TiB or more | the only flags route with no y-only call | COMPUTED (routing, toy rates) + GUESS (32-bit pattern rates) |
| A4 | pure counter difference (two last chunks, different counts) | -1 (not realisable) | an alignment the tree never gives | the tree alignment lemma; 0 of 16,256 count pairs | COMPUTED |
| A5 | v13-only difference (hypothetical) | -1 (not realisable) | two leaves with different high counter words at one position | the cleanest d source | COMPUTED (routing) |
| A6 | collision at a parent node | about 129 (generic) | a child-CV difference that survives 2 rounds | G2: no message-only difference cancels in round 0 | COMPUTED + DERIVED |
| A7 | 55/63 residual moved up to the parent | 256 | - | the same as A6 | COMPUTED |
| A8 | CV difference in h2 (two blocks) | about 112 | a 224-bit first-block partial collision | the smallest round-1 footprint of any source | COMPUTED (routing) + DERIVED (cost) |
| A9 | CV difference in h1 + h2 (+ h3) | about 96 (first block) plus the residual | a 192-bit partial collision and 2 to 3 patterns | - | DERIVED + GUESS |
| A10 | CHUNK_START difference (flags 2 vs 3) | 128 or more | h4..h7 = IV4..IV7 | G1: b inputs never absorb | DERIVED + COMPUTED (planted) |
| A11 | short chunk root (L < 64) vs parent root | 256 plus 8(64 - L) | zero bytes in copied CV words | - | DERIVED |
| A12 | leaf vs parent at 1 round (r1 target) | about 4.1 | nothing | a distinct r1 path: different chunk counts, flags difference | COMPUTED 200/200 on the organizer's verifier |

## 10. Files and commands (Windows Python 3.14, numpy 2.4; -B everywhere)

| file | what | command |
|---|---|---|
| org_blake3.py | copy of hash-smash\verifier\blake3.py (referee) | - |
| tb3.py | vectorized 2-round compression at width w, with intermediates; selftest against org_blake3 | `python -B tb3.py` (0 mismatches in 400) |
| tree_align.py / .txt | tree check, placement enumeration, planted verifier checks | `python -B tree_align.py 128` |
| absorb32.py / .txt | 32-bit leaf-vs-parent round-0 cancellation on the organizer's functions | `python -B absorb32.py 500` |
| route.py / route_out.txt | routing and pattern rates, w = 32, 8, 10, 12, 16 | `python -B route.py` (about 10 min) |
| cvdiff.py / .txt | CV-difference routing (two-block) and the CHUNK_START plant | `python -B cvdiff.py` |
| parent_up.py / .txt | parent-node collisions: round 0 never cancels | `python -B parent_up.py` |
| r1_demo.py / .txt | 1-round full collisions from leaf vs parent on the organizer's blake3 | `python -B r1_demo.py` |
| my_pids.txt | the PID of the one background run (route.py, finished) | - |

Processes: route.py ran in the background (PID 6284) and finished by itself. Every other run was in the
foreground. At most 2 CPU processes ran at once. No GPU was used, since nothing here needed it.
