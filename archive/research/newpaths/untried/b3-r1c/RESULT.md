# b3-r1c: round-1 column calls (C calls, Y words). Scout result, 2026-10-10

Cells: layer r1c x {gd, join, sym, cost}. This is our own research. Nothing was filed or submitted. One CPU
process ran at a time. The longest run took 380 s. kissat always ran with `--time`.
Labels: COMPUTED (I ran it), DERIVED (arithmetic on computed or cited numbers), PROVED (short algebra, written
out below), GUESS.

## Verdict: open. One cost lead; the other three cells are dead or impossible

| cell | verdict | number |
|---|---|---|
| join: build the E1-side and E3-side C outputs separately, then lift | dead | the lift's best word-level guess-and-determine order peaks at **4 words = 2^128 candidates**; an exhaustive search found no order with peak <= 3 (COMPUTED). kissat cannot close even the last one-word loop in 60 s (COMPUTED) |
| gd: prescribe more E inputs by construction (t_hi = 0) | dead | only **two late words** exist at r1c: the member y (C0 second half) and the trial word w0 (C2 second half). Each reaches one E-chain word, and the front line uses both. Holding all of E3 needs at least one 32-bit scan (exhaustive at peak 5). C1's outputs Y1 and Y9 are never free (COMPUTED) |
| sym | impossible | only the identity column rotation keeps the difference support {C3} fixed. The residual's word map (a c)(b d) is not a symmetry of G (PROVED) |
| cost | **open lead** | **t_hi inner walk**: 2^19 legal steps per outer step with C0 and D1 unchanged; omega mod 2^16 is constant on 9 contiguous blocks; omega >> 16 is free per step (COMPUTED). If the omega and gate rows vanished, the gain is at most **1.21 bits** on pkgCK's rows (DERIVED; the assumption behind it is a GUESS) |

## 0. Setup (COMPUTED)

`model.py` rebuilds the front-line parameterisation from map Section 2. The words are C0.d1, D2.a1, D2.b1, S11,
S4, X9, w6, the member y = Y4, and the trial word w0, with t solved in K0. Every step is a single inversion.
On 2000 random tuples:
- 2000/2000 collide on digest words 0, 2, 5, 7 under the reference `_compress` with rounds = 2.
- 2000/2000 have the residual equal to the E1 key XOR the E3 key.
- C3's outputs match map 2.2 exactly: Y3 8127c181 / 7edf3e7e, Y7 76f7aefd, Y11 7af77f38 / 850000c3, Y15 bbfbdffe.

How r1c splits the work (DERIVED from that construction):

| level | what it computes |
|---|---|
| context | C0 first half (C0.b1, C0.c1, C0.d1) |
| member y | C0 second half (Y4 = y, Y12), D0 (w8), D1, C1 (Y1, Y9), C2 first half |
| trial w0 | only C2's second half: Y14 (E3.d) and Y6 (E1.b), linked by Y6 = ror(C2.b1 ^ (C2.c1 + Y14), 7) |
| none | C3 is constant |

The per-trial r1c work is therefore at most 4 word ops. There is nothing to remove there.

## 1. C3 is already at the optimum (PROVED)

1. The pair differs only in C3's x input (w4). So a1 differs, d1 = ror(d ^ a1, 16) differs, and c1 = c + d1
   differs, always.
2. If d2 is equal, then c2 = c1 + d2 differs, and a2 ^ a2' = d1 ^ d1' is nonzero.
3. If d2 differs, then either c2 differs, or c2 is equal and b2 = ror(b1 ^ c2, 7) differs (b1 differs).

Every pattern other than {a, c} therefore touches b or d. Those feed E2 or E0 and break the four pinned words. The
pins already force the unique pattern {a, c}, so no condition can be removed at C3.

## 2. Join on the C-call outputs: dead

Each of C0, C1 and C2 sends one word to E1 and one to E3 (C1: Y1 / Y9, C2: Y6 / Y14, C0: Y12 / Y4). A join means
making E1 inputs (Y1, Y6, Y12, w12, w5) and E3 inputs (Y4, Y9, Y14, w8) independently, matching the keys, then
lifting the 9-word E tuple to a message. The counts match (9 free words, 9 E words), so the system is square.

**The lift is the obstruction.**
- Word-level system: 11 G calls, 88 relations, 88 unknown words. Each relation is solvable for any single
  unknown.
- `gd2.py` searched all orders exhaustively with an exact memo:
  - peak <= 1: none (81 nodes)
  - peak <= 2: none (3,915 nodes)
  - peak <= 3: none (87,482 nodes, 15,798 states)
  - (COMPUTED)
- `gd.py` found an order with peak 4: K3.a1 -> S3 -> S4 -> C0.c1 (1 check) -> D2.c1 (4 checks).
- `gd_eval.py lift` confirms it on the real compression (COMPUTED):
  - 200/200 planted pairs recovered.
  - 1 check after the 4th guess, 4 after the 5th.
  - a one-bit-wrong D2.c1 is rejected 200/200.

So one lift costs about 2^128 candidates. The front line's whole budget is 2^(62.9459 + 8.75) = 2^71.7 ops
(DERIVED), at least 56 bits below that.

**Bit level (kissat, `lift_sat.py`, planted instance, COMPUTED):**

| words given | result |
|---|---|
| all unknowns | SAT in 0.1 s, verified (the encoding is correct) |
| all 5 GD words | SAT in 0.1 s |
| 4 GD words (one 32-bit loop left) | UNKNOWN in 60 s |
| 3 GD words | UNKNOWN in 60 s |

SAT is weaker than a plain 2^32 word scan here, so it gives no shortcut through the lift.

## 3. GD: which E words can be prescribed for free (zero scan)

A set H is free if some 9-word basis containing H assigns every word exactly once with no checks.
`hold.py`, `hold3.py`, `hold_e.py` and `hold_c1.py` use exchange search from the front-line basis, to depth 1-2.
A miss is not a proof, except where the search was exhaustive.

- **Free alone:** Y4, Y14, w8, Y6, Y12, w12, w5.
- **Never free:** Y1 and Y9, alone or with anything (depth 2).
- **Largest free sets:** {Y4, Y14, Y12, w12, w5} and {Y4, Y6, Y12, w12, w5}. `gd_eval basis` built 500/500
  legal pairs with the chosen words (COMPUTED). This buys nothing for the residual: E1 sees w12 only through
  Y1 + w12, Y12 only through d1, and w5 only after adding a1 + b1. All three are randomised by Y1, which cannot
  be held (DERIVED from G's equations).
- **E-call internals with Y4:** E1.c1, E3.c1, E3.d1 and E3.b1 are each free; E1.b1 is not.
  - No pair of E1.c1 with E3.c1, E3.d1, w8, Y9, Y1 or E1.b1 is free (depth 2, COMPUTED).
  - So the trial word can aim at E1's chain (the front line's Q* cube) or at E3's chain (GAPS X9's question), not
    both.
- **Holding all of E3:**
  - no order without a scan exists (exhaustive at peak 5: 37.0M nodes, 109 s, COMPUTED);
  - my search for a one-scan order (peak 6) timed out at 380 s;
  - split_e3 reports a one-scan solve (2^37.43 ops, cited, not re-derived).
- **Why C1 is the bottleneck:** both of C1's message words are spent in round 0 (w3 is K1's y input, w10 is D1's
  x input), and all four D calls feed it. With t_hi = 0 nothing late reaches C1.
- **With t_hi free** (t < 2^51, so t_hi < 2^19 by the reference's length bound len < 2^61):
  - Y9 or Y1 becomes free alone, but not together with Y4 (depth 2).
  - {Y4, E1.c1, w8} becomes free; `thi_check.py` verified it 300/300 on the reference.
  - A solved t_hi is uniform (chi2 16.6 on 15 df) and legal 4/20,000 times (2.44 expected), so a prescribed w8
    costs a 2^-13 filter. That matches GAPS X6 (COMPUTED / DERIVED).

## 4. Symmetry: impossible (PROVED)

- The round's wiring has exactly four automorphisms, the column rotations. Shifting by 2 maps E1 to E3. Our
  difference sits only in C3, so only the identity preserves it.
- The residual pairs E1.a with E3.c, E1.b with E3.d, E1.c with E3.a and E1.d with E3.b. That is the swap
  (a c)(b d) after the shift. G is not equivariant under that swap: message words enter only through a, and the
  rotation amounts (16, 12 vs 8, 7) differ.
- Map item 9 already closed rotational relations.

## 5. Cost: the t_hi inner walk (best candidate, open)

Hold an outer step (context and member y) fixed and walk K1.a1 through its legal block of 2^19 values. Then
t_hi = K1.a1 ^ rol(K1.d1, 16) < 2^19, w2 walks an interval, and X0 = C0.a1 - X4 - w2 moves the opposite way.
C0's a1 is unchanged, so **C0 is unchanged**. **D1 is unchanged** too. Only D0 (w8, w9, X5, X10), w3, C1 (Y1, Y9)
and C2's first half move.

Measured over 4 outer steps x 2^19 steps (`thi_walk.py`, COMPUTED):
- 512 reference checks, 0 failures: half-collision holds, Y0/Y4/Y8/Y12 and X1/X6/X11/X12 unchanged.

Measured with w2 in interval order (`thi_blocks.py w2`, 3 outer steps, COMPUTED):
- omega = Y3 + y + w8 takes **9 values mod 2^16, in 9 contiguous blocks** of up to 65,536 steps.
- Bit 16 and above change on every step: omega >> 16 runs through X0's low 16 bits, so it is free inside a block.
- For comparison, a front-line cluster of 32 members shares omega mod 2^9 (1 value in 3/3 samples; the map says
  one of two).

Per step it costs about 5 ops to reach omega and about 27 ops to reach every E input. The front line needs 8 lines
for omega (52 units per 7-member batch) and 17 lines for Y9 (fill 54, plus 7 per lane) (DERIVED from my rebuild).

**Value.** In pkgCK's rows (map 2.7), opened clusters (0.530) and representative batches (0.039) are omega
computation and gating. If the omega test and gate read only omega and words that stay constant per member, the
walk decides them per block and solves the high bits directly. Then those rows vanish: the remaining share is
0.432, a **gain of at most 1.21 bits** (search 2^61.97, about 61.98 on pkgCK's rows) (DERIVED; the assumption is a
GUESS). pkgCL's rows are not in my reading list.

**Risks:**
1. The Y9 rows could grow or shrink.
2. Outer steps now share y, Y12, C0 and D1 in blocks of 2^19, which strains the dependence clause H1'(ii).
3. Messages reach about 2^60 bytes, with a 64-bit counter (t_hi > 0). The front line only uses t < 2^32.

This is not GAPS X6 (solve t_hi to force w8, a 2^-13 filter): the walk enumerates the legal range directly and pays
no filter.

## 6. Not tested; the next test

- I did not read frontline.py, Lemma F, or the omega test definition; the brief did not list them. Pricing the
  lead needs them:
  1. what the omega test, the 2^21-word gate and Lemma F's two words read;
  2. a t_hi-walk member loop, metered on the scaled rig;
  3. a rerun of the preregistered rate experiment on the walk's distribution;
  4. whether the organizer accepts t >= 2^32.
- A meet-in-the-middle inside the lift was not searched. It would have to beat the 2^128 GD peak by about 56 bits.
- The one-scan E3 order was not re-derived (it timed out).
- Exchange-search misses are not proofs.

## 7. Files (all in this folder)

`model.py` (pair model, verified), `gd.py` / `gd2.py` (symbolic GD, exhaustive search), `gd_eval.py` (numeric
closure), `hold*.py` (free-holdable sets), `lift_sat.py` (kissat lift), `thi_check.py`, `thi_walk.py`,
`thi_blocks.py`; outputs `*_out.txt`, `sat_runs.txt`, `gd2_*.txt`. `debug1.py` is a scratch check from building
the model. The CNF files were deleted after each run.

## 8. Refusals or stops

None. No tool call was refused or stopped. The 380 s peak-6 search ended at its own budget, not by any external
stop.
