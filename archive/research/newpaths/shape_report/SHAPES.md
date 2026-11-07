# Shapes tried on 2-round BLAKE3

For the owner. Research only: nothing was submitted, yukon was never run, trace stayed off. Written 2026-10-08.

Every statement carries a label. COMPUTED means a program measured it. DERIVED means it follows from algebra or counting. GUESS means it is a judgement.

## The short answer

- We took your idea two ways. First literally: sphere, hexagon, ring, torus, cube, circle, Moebius strip, fractal. Then we let the mathematics pick its own best shape and compared.
- Three agents tried the 42 shapes listed below. Two skeptic agents re-checked the one shape that looked open.
- For real BLAKE3, no shape beats plain birthday search, 2^128 (COMPUTED). The board is at about 2^92. The best shaped route costs about 2^189 (COMPUTED).
- The one open door, the "sphere at level 3" at 2^80, was closed by both skeptics independently (COMPUTED + DERIVED).
- Your shapes did produce two real findings. A torus symmetry would break BLAKE3 at 2^64 if its starting constants were symmetric. A parity proof shows the real constants block it (DERIVED, checked on toys). Several small "rings" are cheap to solve, and they are now reusable tools.

## How to read the cost column

- Cost is log2 of the total work in contest units. One unit is one 2-round compression. Lower is better.
- 128 is the plain birthday attack. The board's best is about 92 to 94. Below 85 would be very strong.
- "no members" means the shape's family is empty for real BLAKE3, so there is no cost.
- "tool" means a cheap piece that helps inside other methods but is not an attack by itself.

## What a "shape" means here (game-dev picture)

The attack (idea 1) is a big puzzle: 100 to 128 unknown 32-bit words tied by 96 to 116 small equations. A shape is how you cut the puzzle into chunks and glue the partial answers back together. Think of chunking a game level. Each chunk border becomes a list of partial answers that must be built. Memory is free in this contest, but building the list is not: the cost is the size of the biggest list, 2^(32 x border words). A thin waist in the map means a cheap attack. (DERIVED)

A grid, ring, hexagon or sphere becomes the order in which chunks are visited. A closed loop (ring, torus, sphere surface) must be cut once before you can walk it. (DERIVED)

## One line per shape

| # | Shape | What it means here | What happened | Verdict | Cost |
|---|---|---|---|---|---|
| 1 | Path (straight line) | Guess a few words, then solve the rest one equation at a time | Needs 6 guessed words per member. Lists of 2^192 (COMPUTED) | dead | 189 |
| 2 | Star (hub and spokes) | One centre list joined to several side lists | Sibling agents measured 2^193 (COMPUTED) | dead | 193 |
| 3 | Sphere / onion | Peel the puzzle from both ends toward the middle | Border 15 words, no better than random (COMPUTED) | dead | about 477 |
| 4 | Hexagon (6 sectors) | Split the 4x4 state into 6 wedges, solve wedge by wedge | Border 14 words (COMPUTED) | dead | about 445 |
| 5 | Ring polygon of 8 calls | Walk the 8 round-0 G calls around their natural ring | Border 14 words (COMPUTED) | dead | about 445 |
| 6 | Torus sweep | Walk the 4x4 state along its diagonals | Border 13 words (COMPUTED) | dead | about 413 |
| 7 | Cylinder | Walk the state column by column | Border 14 words (COMPUTED) | dead | about 445 |
| 8 | Message cycles | Follow the two 8-cycles of the message shuffle | Border 14 words (COMPUTED) | dead | about 445 |
| 9 | Message hub | Put the message words in the centre | Border 14 words. Random orders give 15 to 17 (COMPUTED) | dead | about 445 |
| 10 | Spine with bushy branches | The best shape a search found for the "fixed" family | Border 8 words, or 6 with 2 extra words held constant (COMPUTED) | dead | 189 |
| 11 | Two lobes joined at one neck | Best shape for the wider family. Lobe 1: round-0 D calls and C calls. Lobe 2: E0, E2 and the outputs | Border 6 words. The same 6 came from three search methods and several starts (COMPUTED) | dead | 189 |
| 12 | Any arrangement of whole G calls | Grids, cubes, rings, hexagons and stars of calls, searched exactly | Exact best border 6 (COMPUTED) | dead | 189 |
| 13 | Every possible tree (lower bound) | Every tree has a middle chunk holding 1/3 to 2/3 of the puzzle. Its border is the floor | No chunk border below 5 found in 36+ searches. Not proved (GUESS) | dead on evidence, not proved | 157 or more if right |
| 14 | Closed loops (ring, torus, sphere surface) | A loop must be cut once, then it is a tree with extra words | Covered by row 13 (DERIVED) | dead | above row 13 |
| 15 | Bit slicing and partial keys | Hold some bits instead of whole words | Each bit held saves at most one bit of list. No gain over whole words (DERIVED, small caveat) | dead | no gain |
| 16 | Rings: the tangled core, fixed family | Split the puzzle into blocks that must be solved together | About 170,000 setups tried. Always one tangled core of 68 to 94 words that needs 4 cut words (COMPUTED) | dead | 192 |
| 17 | Rings: the tangled core, wider family | Same split for the wider family | One core of 63 to 114 words, 4 cut words (COMPUTED) | dead | 192 |
| 18 | Bit ring | Each word is a ring of 32 bits: cut one bit and run around | On the core the cut never went below 128 bits (COMPUTED, heuristic) | dead | 192 |
| 19 | Small rings inside one G call | Little loops outside the core | 38 to 61 kinds, solved with 1 to 32 seed bits. Checked by brute force at 16 bits, 0 mismatches (COMPUTED) | tool | tool |
| 20 | Torus ring between E0 and E2 | The two output-half calls are linked by the output pairs | One loop is linear: cut 1 bit and run around the ring (COMPUTED). Outside the core | tool | tool |
| 21 | Torus shift by 2, full family | State symmetric under a 2-column shift | Empty for real BLAKE3: a parity proof needs the starting words to have an even sum, and theirs is odd (5 of the 8 IV words are odd; re-checked here, COMPUTED). Toy checks: 0 members (DERIVED + COMPUTED) | dead | no members |
| 22 | Torus shift by 2, half family | Only E0 and E2 inputs symmetric | Only 2 free words, digest still 192 bits: too small (COMPUTED) | dead | no members |
| 23 | Torus shift by 2, after round-1 columns | Symmetry imposed mid-way | 7 checks per member (COMPUTED) | dead | 288 |
| 24 | Torus shift by 2, E0/E2 half | Symmetry on one half only | 3 checks, 192-bit digest. Combined with idea 1 it has no freedom left (COMPUTED) | dead | 192 |
| 25 | Torus shift by 1 or 3 | All 4 columns identical | 12 conditions on 4 words: empty (DERIVED) | dead | no members |
| 26 | Torus flips (columns become diagonals) | Mirror maps of the 4x4 torus | All 4 flips break the output pairing (COMPUTED) | dead | no members |
| 27 | Made-up symmetric IV | What the real IV blocks | With fake symmetric constants: a 2^64 attack, 2 real collisions found at 12-bit toy size. The real IV blocks it (COMPUTED) | dead for BLAKE3 | 64 if the IV were symmetric |
| 28 | XOR-shifted torus | Symmetric up to a fixed XOR | Same counts as row 21 (DERIVED) | dead | no members |
| 29 | Circle: rotated pairs | Rotate every message word, compare outputs | Uniform, same as random (COMPUTED). Even an exact symmetry gives at best 2^125.5 (DERIVED) | dead | 128 |
| 30 | Circle: word parity | The one thing every rotation keeps | Noise level at 8, 16 and 32 bits (COMPUTED) | dead | 128 |
| 31 | Folded circle | Words made of two equal halves act like a half-size BLAKE3 | Dies at the first addition (COMPUTED) | dead | 128 |
| 32 | Hexagon: lattice symmetry | The 4x4 state is a triangular-lattice torus | No symmetry survives the message shuffle and the starting state (COMPUTED) | dead | 128 |
| 33 | Hexagon: call graph | Link each message word's round-0 call to its round-1 call | One octagon and two squares, no hexagon. Square families uniform (COMPUTED) | dead | 128 |
| 34 | Hexagon: three-way sums | Treat a+b+x as a 3-list join | Same cost as a 2-list join (DERIVED) | dead | no gain |
| 35 | Sphere: hold part of the half-digest | Fix only k of the 4 output words | Each held word costs a full 32-bit check and saves 16 bits. Best is k=0 (COMPUTED) | dead | 128 + 16k |
| 36 | Sphere door at level 3 | Hold 3 words for free, giving 2^80 | Refuted by 2 skeptics: exactly 3 checks, not 0 (COMPUTED + DERIVED) | dead | 176 (any join tree 112 or more) |
| 37 | Sphere: Hamming balls, lumpy image | Messages near a centre; uneven output spread | No excess collisions at 8, 12, 16 bits. Re-run with a new seed agrees (COMPUTED) | dead | 128 |
| 38 | Moebius twists | 14 twists (shuffle powers, flips, rotations, complement, ...) | All uniform at 8 and 16 bits (COMPUTED) | dead | 128 |
| 39 | Moebius slide | A message whose round 0 returns the start state | Exactly one such message exists. One message, not a family (COMPUTED) | dead | no family |
| 40 | Fractal nesting | Fix output words one level at a time | Each level costs 2^32 and saves 2^16 (COMPUTED) | dead | 128 + 16k |
| 41 | Mirror fold | Output is unchanged by swapping state rows | Using it needs a 512-bit match (DERIVED) | dead | no family |
| 42 | Tied message families | Words tied along transpose, mirror, palindrome, x=y, shuffle orbits | Uniform at 8, 12, 16 bits (COMPUTED). See the follow-up below | dead | 128 |

Cost notes. Rows 3 to 9 convert a border of B words to a cost of about 32 x B - 3 (DERIVED, using shape_any's list-cost formula). Rows 3 to 9 use the wider family with 10 words held constant, which is the best case for those shapes.

## Why no shape helps (plain words)

- Every G call takes one word from every call of the layer before it. Every message word is used in both rounds. (DERIVED)
- In game terms: every room has a door to every room on the next floor. There is no chokepoint to split the map. Mathematicians call this an expander. (DERIVED)
- So any chunk big enough to matter has a wide border. Your literal shapes landed at borders of 13 to 32 words, no better than random orders. The shape the maths picked is irregular, two lobes on a spine, with a border of 6. A useful attack needs a border of 2 (below 2^85) or 3 (about 2^93). (COMPUTED for the borders, DERIVED for the targets)

## Alive

Nothing is alive. No shape reaches 2^128, let alone the board.

Open items, with the next concrete test:

1. Is there any tree with a border of 3 or 4? (row 13)
   - Status: no border below 5 found. The exact proof runs did not finish. (GUESS that 5 is the floor)
   - Why it matters: border 3 would cost about 2^93 (competitive). Border 4 would cost about 2^125 (barely below generic).
   - Next test: prove "no middle chunk has a border below 4" on the fixed family (slack 2, the smallest case). Use a stronger exact method than plain SAT: an ILP or MaxSAT model, or SAT with the chunk forced to contain one named G call to break symmetry. The solvers timed out even on a known-yes test, so the encoding must change first.
2. Can the tangled core be cut with 3 words instead of 4? (rows 16, 17)
   - Not proved impossible. Even if it works it costs about 2^160 (DERIVED: 2^96 per member, 2^64 members), so it stays dead. A split into 1-cut rings would give about 2^96. No such split showed up in about 170,000 setups (COMPUTED).
   - Next test, only if cheap: an exact minimum-cut (feedback set) solver on the 68-word core for the index set m0, m4, m6, m7.
3. The 8-bit "P-invariant" blip (row 42), flagged by a skeptic as a GUESS. Checked here, see below.

## Follow-up done for this report: the P-invariant blip

The P-invariant family ties message words along the two 8-cycles of the shuffle. It has 2 free words, so it is the same family for every random seed. At 8-bit toy size one 4-word output group, (0,1,3,7), had 5 colliding pairs where 0.5 were expected. A new seed cannot re-test a fixed family, so it was left as a GUESS.

What I ran (pinv.c and run.sh in this folder; outputs pinv_small.txt and pinv_w12.txt). I enumerated the whole family at 6, 8, 10 and 12 bits and counted colliding pairs on all 70 four-word output groups. Each group expects 0.5 pairs, so 35 in total.

- 8 bits: the 5 pairs on (0,1,3,7) reproduce, and the two halves match shape_odd exactly (0 and 2 pairs), so my toy code agrees with theirs. The total over all 70 groups is 37, against 35 expected. The 5 pairs show no pattern in their two free words. (COMPUTED)
- 6 bits: (0,1,3,7) has 1 pair, total 40. 10 bits: (0,1,3,7) has 0 pairs, total 38. (COMPUTED)
- 8 bits with a slightly changed IV (XOR 0x5a or 0x01 into the chaining value): (0,1,3,7) has 1 and 0 pairs, totals 35 and 25. (COMPUTED)
- 12 bits (2^24 members, the whole family): (0,1,3,7) has 0 pairs. The total over 70 groups is 39, against 35 expected. The worst group has 2. (COMPUTED)
- Verdict: a chance hit. The best of 70 groups reaching 5 happens about 1.2% of the time by luck (DERIVED). It does not repeat at other sizes, and it vanishes when the IV changes. Dead.

## Useful side results for the main session

- Exact check counts (skeptic 0, COMPUTED): holding k of the 4 half-digest words needs exactly k checks. The whole half needs 4 checks, so 16 guesses. The main session's undecided outhalf SAT runs at 12, 13 and 14 guesses are all impossible and can be stopped. The fixed family needs exactly 4 checks, as you found.
- A simple rule decides 0-check questions without SAT (DERIVED, checked by brute force on 27,406 small cases): an order with no checks exists exactly when repeated peeling leaves nothing (the "2-core" is empty). Guesses cannot open a non-empty core.
- Join trees for the whole half cost at least 2^96 (skeptic 0, DERIVED from ksplit's argument plus c(4) = 4). This closes ksplit's open "12-guess" case.
- The identity x + y = A_out - a_in - b_in - b1 holds for every G call (DERIVED). It links paired G calls linearly.
- bitgd.py (shape_torus) solves small bit rings exactly. Validated by brute force.

## Blocked or not verified

Blocked:
- shape_any and shape_verify_outlandish_0: one foreground sleep each was refused by the harness. They switched to Monitor or polling and did not retry.
- shape_odd: one foreground sleep was refused the same way. It polled result files instead.
- This report: a foreground "sleep 90" before reading the 12-bit result was refused by the harness. Not retried in any form. I waited for the background job's own finish notice instead.

Not verified:
- No exact lower bound on the border above the trivial one (row 13). The SAT and pseudo-Boolean runs timed out, even on a known-yes test.
- No exact lower bound for bit-level guess-and-determine. The greedy search found 128 bits, which equals 4 words.
- A 3-cut of the tangled core is not ruled out (it would still cost about 2^160).
- Methods outside "solve and join lists" were out of scope: differential paths, algebraic attacks, multi-block.
- Tables that span several G calls after heavy promotion are covered only through the join-tree bound.
- No toy end-to-end attack was run. Nothing came close to 2^85, so there was nothing to run.

Process notes:
- shape_any briefly ran 5 jobs, one over the cap of 4, then corrected it.
- Another session edited the shared gd_order.py at 12:45. shape_any checked that this did not change its exported systems.
- No agent wrote outside its own folder.

## Where the details are

All under ./research/newpaths:
- shape_any\NOTES.txt: join trees, literal shapes as orders, exact brick search, the neck bound.
- shape_torus\README.txt: rings, the tangled core, torus symmetry and the parity proof.
- shape_odd\NOTES.txt: circle, hexagon, sphere, Moebius, fractal, mirror.
- shape_verify_outlandish_0\NOTES.txt and shape_verify_outlandish_1\NOTES.txt: the two refutations of the sphere door.
- shape_report\ (this folder): this report and the P-invariant follow-up.
