# SIDEPATHS - side agent for new ideas and paths (2-round BLAKE3 collision)

Folder `research\newpaths\sidepaths`. Written 2026-10-08. Research only: no yukon, nothing submitted, no trace,
no credential file opened, only my own processes stopped. Every statement is tagged COMPUTED (a program here
produced it), DERIVED (follows by argument from stated facts) or GUESS.

Read first and not redone: `..\..\NEW_PATHS.md`, `..\..\END_OF_LINE.md`, and the folders `literature`, `fringe`,
`separable`, `shape_odd`, `variants`, `kmath`, `ksplit`, `shape_torus`, `shape_any`, `audit`. Those settled the
"E0/E2-fixed family" (idea 1: 4 checks, no split), MITM on the residual (no split), trails, symmetry and shapes.
This folder looks at what is left: the filed 55/63 family itself, the target's edge cases, and the owner's two
questions (BLAKE2, biology).

## 0. Bottom line

1. No new path below the board was found. Twelve ideas were tested or argued; ten are dead, two are small
   engineering levers (S9 bitslicing, at most a few tenths of a bit).
2. The strongest new result is a closing one (S10, DERIVED + COMPUTED): in a single block, the ONLY way to get
   digest words for free from two messages is the filed structure: the length difference absorbed completely in
   K2 (Lemma L), then a pinned C3 with equal b and d outputs, then a residual of E1 (c and y differences) against
   E3 (a difference). Every leak pattern of K2, and every equal-length round-0 local collision, is either
   impossible or puts a difference into a round-1 column call or into half A. So inside one block, "new paths" can
   only be new pins, classes and trial costs - which is what `research\paths` (the atlas) already searches.
3. Inside that structure, two natural extensions are now closed by exhaustive solver runs:
   - S1: no residual-side word other than the E1/E3 inputs (g1, h1, e2, g2, E1.a1, E1.d1, E1.a2) can be a free
     coordinate of the family, with or without Y4, even with 2^64-entry tables: a second "class" cannot be held
     for free (exhaustive guess-basis search, 0 bases in every case; positive controls find bases).
   - S2: one pinned C3 can never serve three block lengths (160 of 160 triples UNSAT in z3), nor two disjoint
     length pairs (14 of 14 UNSAT). One trial yields exactly one pair.
4. The residual has no local structure: every single-bit move of the eight free words changes about half of the
   128 residual bits (S3, 14,460 moves, mean 63.5). Hill climbing, "evolution" and neutral-network walks are
   random search here.
5. Owner's questions: nothing from BLAKE2 cryptanalysis transfers beyond the Li-Xu cancellation the path already
   uses (section 8.1). Biology: section 8.2 maps thirteen natural mechanisms; the ones that were new were tested
   and died; the rest are already inside the filed path.

## 1. Scoreboard

| # | idea (nature analogy) | verdict | projected effect | tag |
|---|---|---|---|---|
| S1 | "Retrosynthesis": a second residual-side word as a free coordinate (a second class beside Y4) | dead | no gain: every such word costs a 32-bit check per member | COMPUTED |
| S2 | "Alternative splicing": one pinned C3 for 3+ block lengths (3 pairs per trial) | dead | - | COMPUTED (z3, 160/160 triples UNSAT) |
| S2b | Two disjoint length pairs on one base (2 pairs per trial) | dead (14 of 14 UNSAT) | - | COMPUTED (z3) |
| S3 | "Affinity maturation": hill climb on the residual | dead | - | COMPUTED |
| S4 | Keyed / derive-key / XOF output | dead (out of scope) | - | DERIVED |
| S5 | Chunk counters, tree shapes, parent root, flags 10/11/12 | dead | generic | DERIVED |
| S6 | Pin with a weight-1 C3 difference (sparse E1/E3 inputs) | dead (impossible) | - | DERIVED |
| S7 | Equal-length pair whose difference reaches only E1/E3 | dead (impossible) | - | DERIVED |
| S8 | Two blocks, chaining value chosen by 2^85 preprocessing | dead | <= 0.12 bit | DERIVED |
| S9 | "Pooled testing": bitslice 256 trials per 256-bit word | small | ~0.07 bit realistic; <= 0.7 bit with a redesign | DERIVED + GUESS |
| S10 | Is the filed structure the only free half-collision in one block? | yes | closes the search space | DERIVED + COMPUTED (z3) |
| S11 | "Recombination": cross w8..w11 between members of one context | dead | - | DERIVED |
| S12 | "Stigmergy": spend more trials in rich-looking contexts | dead (record: +-8.4 %) | <= 0.12 bit | DERIVED |

## 2. S1 "retrosynthesis": prescribe the residual side, then solve for the message

**Idea.** Cells and chemists plan backwards from the product (reverse transcription, retrosynthesis). Here: the
collision condition R = 0 depends only on the inputs of E1 and E3. The filed path makes ONE of them, Y4, a free
coordinate and holds it in a class of 2^19 values that fixes the XOR difference of E3's first d value (eta); that
one choice is worth about 2^27 over uniform. If a second residual-side word (E3.g1, E3.h1, E3.e2, E1.d1, ...)
could also be a free coordinate, its own class would make the next difference deterministic as well: a further
factor of roughly 2^8 to 2^12 per word (GUESS, from the weights of the differences), enough for the 80s. In the
limit, all eight effective E1/E3 inputs free would let one sample a solution of the residual system (the exact
counter's automaton can sample as well as count) and solve for the message at O(1) per collision.

**Test (COMPUTED).** `pin_model.py`: word-level model of the pinned family, message A (pins X3, X7, X11, X15, W4,
W13; w14 = w15 = 0; C3 constant; E1, E3 in full); 108 unknown words, 100 equations, freedom 8. The published basis
(C0.c1, C0.d1, D3.d1, S15, S9, w5, X2, Y4) closes everything. `gdx` (exhaustive minimum-guess search, copied from
`variants`) asks whether a 0-check basis contains the listed words.

| prescribed | further guesses k | 0-check basis? | search nodes |
|---|---|---|---|
| positive control Y4 + w5 | 6 | **yes, 11,234 bases** (47,110 with tables) | 211 M |
| positive control Y4 | 7 | **yes** (bases listed in `res_y4_k7.txt`) | - |
| Y4 + E3.c1 (g1) | 6 | no | 196 M |
| Y4 + E3.d1 (h1, rule A's word) | 6 | no | 196 M |
| Y4 + E3.a2 (e2) | 6 | no | 231 M |
| Y4 + E3.c2 (g2) | 6 | no | 231 M |
| Y4 + E1.a1 | 6 | no | 250 M |
| Y4 + E1.d1 (fixes E1's c1 difference) | 6 | no | 196 M |
| Y4 + E1.a2 | 6 | no | 249 M |
| Y4 + g1 + E1.d1; Y4 + h1 + g1; Y4 + h1 + E1.d1; Y4 + w5 + E1.d1; Y4 + w5 + g1 | 5 | no (each) | 11-13 M |
| g1 alone; h1 alone; E1.d1 alone | 7 | no (each) | 2.8-3.0 G |
| with 2^64-entry tables for K0, K1, K3 (`--t2`): Y4 + each of g1, h1, e2, g2, E1.a1, E1.d1, E1.a2 | 6 | no (each) | 194-249 M |

So, in the word model with and without 2^64-entry tables for the constant-input column calls, no residual-side
internal word can be a free coordinate of the family, with or without Y4. Holding one costs a 32-bit check per
member, which is what the filed search already pays by filtering. Words that can share a basis with Y4 and w5
(`all_y4_w5_k6.txt`, `union.py`) include w12 and Y12 = C0.d2, but E1's first difference depends on
Y12 XOR (Y1 + Y6 + w12) jointly, and that is not free. **Verdict: dead.** Limits: the model solves one unknown
per equation (plus the K-call tables); bit-level steering is outside it, and the record already found it fails
("no neutral bit", "knob words false", "coupled equations 30 of 30 unsatisfiable", END_OF_LINE 4.1).

Files: `pin_model.py`, `mk_models.py`, `gdx.c`, `build.sh`, `run_gdx.sh`, `batch1.sh`, `batch2.sh`, `m_*.model`
(+ `.vars`), `res_*.txt`, `union.sh`, `union.py`, `all_y4_w5_k6.txt`.

## 3. S2 "alternative splicing": one base message read at several lengths

**Idea.** A virus reads one stretch of DNA in several frames. Here one base message can be read at every length
L >= 55: with a1_L = a1_55 XOR 55 XOR L in K2, every "sibling" has the same round-0 state (fringe angle 3;
re-verified for L = 55..63, COMPUTED, `siblings.py`). Siblings differ only in w4 (C3's x) and w5 (E1's y), so
digest words 0, 2, 5, 7 agree between two siblings exactly when C3 gives them equal b and d outputs (DERIVED from
Lemma H). New question: a pin whose C3 gives equal (b, d) for three lengths, so each trial yields three
half-colliding pairs instead of one (at most log2 3 = 1.58 bits).

**Test 1 (COMPUTED, `siblings.py`).** Filed pin H8 at lengths 55..63: only 55 and 63 share C3's (b, d).

**Test 2 (COMPUTED, `triple_smt.py`, `sweep_sib.sh`, `sweep_sib2.sh`, z3 4.13.3).** Unknowns T = X3 + X7 - K,
Q = K + W4, X7, X11, X15, W13 (top byte 0); C3's first value for length L is T + (Q XOR 55 XOR L) (Q free, so any
set of lengths is covered); assert equal b and d outputs. Encoding checked: H8's constants satisfy the 55/63
query (sat) and fail it with XOR 4 instead of 8 (unsat) (`h8check.smt2`, `h8check_neg.smt2`).
- All 45 pairs of lengths 55..64: a pin exists **exactly when the lengths have the same parity** (XOR even); every
  odd-XOR pair is UNSAT (`sweep_sib.txt`). The atlas's pairs all have even XOR, consistent.
- All 120 triples of lengths 55..64: **UNSAT, every one** (about 1 s each).
- 40 random same-parity triples of lengths 1..64: **UNSAT, every one** (`sweep_sib2.txt`).
**Verdict: dead.** One base can never carry more than one half-colliding pair.

**Test 3, two disjoint pairs on one base (COMPUTED, `double_smt.py`, `double.sh`, `double2.sh`).** E.g. 55-63 and
57-61 on one base, each pair with equal (b, d) (two 64-bit conditions on about 184 bits, so not excluded by
counting). **All 14 cases UNSAT** (`double_results.txt`, `double2_results.txt`):

| two pairs on one base | z3 |
|---|---|
| 55-63 + 57-61, 55-63 + 59-61, 55-63 + 56-64, 55-57 + 59-61, 56-64 + 58-62, 55-59 + 57-61, 56-58 + 60-62, 55-63 + 57-59, 56-60 + 58-62 | UNSAT (190 s limit) |
| 55-63 + 56-58 (timed out at 190 s, UNSAT at 890 s), 55-63 + 56-60, 55-63 + 58-60, 55-63 + 60-62, 57-63 + 56-58 | UNSAT |

So one set of C3 inputs supports one length pair and no more, whether the pairs share a length or not. GUESS:
the (b, d) condition needs a long carry run in C3's first value between the two executions (H8: 7ffffff8 vs
80000000, XOR fffffff8; z3's own 55/63 pin: 7f8c0007 vs 7f8bffff, XOR 0007fff8), and one base can place such a
run for only one pair. **S2b dead.**

## 4. S3 "affinity maturation": is there a gradient on the residual?

**Idea.** Antibodies improve by small mutations plus selection. Here: flip one bit of one free word, keep the move
if the 128-bit residual R gets closer to 0. Needs small moves to change R a little.

**Test (COMPUTED, `fam55.py`, `locality.py`).** `fam55.py` writes out the filed construction (proof.md section 4,
steps O, M, Y, T; `research\grok\work\job16_entry\h8_ref.py` could not be used: its `arrangement.txt` holds 82
bytes and the module fails its own self-test). Self-test: 200 of 200 pairs half-collide on words 0, 2, 5, 7, and
`hash2` equals the organizer's `verifier/blake3.py` at 2 rounds. Then 60 random trials, every single-bit flip of
every free word (y: its 17 free sub-class bits), 14,460 flips. Distance between old and new R: mean 63.52,
minimum 37, 1st percentile 50, median 64; no flip at or below 32; no (word, bit) with mean below 61.5. A random
function: mean 64, sd 5.66, minimum over 14,460 about 41. **Verdict: dead.**

## 5. S10 the structure is forced (and S6, S7)

Question: with two single-block messages, could K2 let part of a length difference out ("leak") and have it
absorbed elsewhere in round 0, or could an equal-length pair do the same, giving a different free half-collision?

- A G call can absorb an input difference with its message words only in the a input (by x: a and x enter only
  through a1 = a + b + x) or in the d input (by x and y, Lemma L's pattern). b or c differences cannot be absorbed:
  inverting from equal outputs (proof.md Fact 1) gives B = ROL(b1, 12) XOR c1 and C = c1 - d1, which involve
  neither x nor y. DERIVED; z3 (`leak_smt.py`, `leak.sh`, `leak_results.txt`): `in_a` sat, `in_b` unsat,
  `in_d` sat, `in_c` timed out (impossible by the line above).
- K2's outputs go to S2 (a of D2), S6 (b of D1), S10 (c of D0), S14 (d of D3). So only a leak inside {S2, S14} could
  be absorbed in round 0. z3, K2 with lengths 55 vs 63 and free message words, outputs differing exactly on a set:
  {b}, {c}, {d}, {a,b}, {a,d} UNSAT; {a} and {b,c} timed out but are impossible in two lines (DERIVED: {a}: equal d2
  and different a2 force different d1, so c1 = IV2 + d1 and c2 = c1 + d2 differ; {b,c}: equal a2, d2 force equal
  d1, c1, b1, so c2 is equal); {a,c}, {b,d}, {c,d} and all larger sets SAT, but each contains b or c.
  Besides, absorbing S14 would need w14, which round 1 reads in E2 (half A).
- Equal lengths (DERIVED): round-0 differences must start in a column call (constant state inputs), and a call
  with equal inputs and different message words changes at least two outputs (single-word leaks are impossible by
  the same Fact 1 lines). The only absorbable column outputs whose absorbing message words do not reach C0..C2 or
  half A in round 1 are S2 (absorbed by w12, read in round 1 only by E1) and S13 (absorbed by w12, w13: E1 and the
  pinned C3); they lie in different calls and each would have to leak alone. The others (S0, S12, S1, S3, S15,
  S14) need w8..w11 or w14, which reach C1, E0 or E2. What remains is a difference that enters E0/E2 and is
  cancelled there: the record's "four-active fork" (best complete trail 2^-253).
- Inside the structure, C3 must give equal (b, d): an {a, c}-equal C3 leaves E1 with only a y difference and E3
  with none, and a G call with only a y difference always changes its output (DERIVED).
- S6 (DERIVED): for a pinned C3 with delta = d1 XOR d1', Y3 XOR Y3' = delta, Y11' - Y11 = d1' - d1, and equal b
  outputs force ROR12(c1 XOR c1') = c2 XOR c2' with c1, c2 carrying the same additive difference. For a weight-1
  delta that difference is +-2^k, whose XOR pattern is a carry run starting at bit k on both sides; rotated by 12
  it cannot equal itself. So weight-1 pins are impossible; H8's delta is fff8ffff (COMPUTED from Fact P). (Only
  weight 1 was excluded; the atlas covers the possible pins.)

**Verdict.** In one block, two messages get digest words for free only through Lemma L plus a pinned C3, and the
residual is always E1 (c, y) against E3 (a). New single-block paths are therefore new pins, classes and trial
costs. DERIVED + COMPUTED.

## 6. Target-definition edge cases (S4, S5, S8)

From `hash-smash\target-profiles\blake3-r2-prefix-v1.json` and `verifier\blake3.py`:
- **Keyed, derive-key, XOF (S4): dead.** "Standard BLAKE3 IV; unkeyed mode. No keyed hashing or key derivation";
  out of scope: "Changing rounds, IV, padding, mode or output length"; the digest is the first 32 root bytes.
- **Chunk counters and tree shapes (S5): dead.** A leaf's counter equals its position, so two messages compare
  leaves at equal positions with equal counters. A counter difference (it would sit in K0's d input) arises only
  between trees of different shapes, and then one side of the root block is a parent output (its message is two
  chaining values we do not control) or a leaf is matched against a parent: every case needs a collision of a
  compression whose message we cannot choose. DERIVED.
- **Flags 11 / 10 / 12 (S5): dead.** A flags difference sits in K3's d input and could be cancelled by w6, w7, but
  round 1 reads w6 in C0 and w7 in C2, which feed both halves; and the other message's CV (chained, not the IV) or
  root block (two chaining values) would have to match on 128 to 256 bits. DERIVED.
- **Two blocks with a chosen chaining value (S8): dead.** The 55/63 trick works in a last block (flags 10,
  K = cv2 + cv6); the pins are internal values. Under model M the rate depends only on C3's outputs and the w5
  difference, not on the CV; the realizable deviation (the certified outer-word effect) is about +-8 %. DERIVED.
- Byte lengths only ("finite byte strings"), single-block lengths 0..64: the other length pairs are the atlas's.

## 7. Cost and search levers (S9, S11, S12)

- **S9 bitslicing.** The cost model is a "256-bit word RAM", so 256 trials can share each bitwise operation if
  each trial is one bit position; rotations become free. Hand count for stage A (DERIVED from proof.md 6.3 and
  Lemma A): 4 additions of a variable and a per-context constant (3-4 ops per bit, the constant changes with X2),
  2 additions of two variables (5 per bit), 3 variable XORs (32 each), 2 table values as 32 slices each, rule A
  about 20: about 900 ops per 256 trials = 3.5 per trial, against 47/7 = 6.7 for the filed 7-lane stage A. But the
  filed cost table (proof.md section 8, 67.585 per representative) is dominated by the neighbour path (31.72 stage A
  + 22.10 stage 2); neighbours of different X2 values do not share constants and come from scattered table rows,
  and stage 2 needs the rare passing lanes extracted. Bitslicing only the representatives saves about 3.4 of
  67.6 = 0.07 bit; all stage-A work at 1.9x would give 0.46 bit, at 3x 0.69 bit (GUESS, needs a redesign).
  **Small; low priority.**
- **S11 recombination.** Two members of one context share all message words except w8..w11 and the column state.
  Taking w8, w9 from one and w10, w11 from the other gives an admissible block (D0 and D1 outputs each from one
  parent, X15 and X11 pinned), so it half-collides too. But C0 then reads X0 from one parent and X12 from the
  other: Y4 is a fresh word, in the class with probability 2^-13. Trials outside the class: no gain. DERIVED.
- **S12 stigmergy (adaptive allocation).** Gains only what a context changes in the rate; certified extremes of
  the outer-word effect +8.389 % / -8.386 % (END_OF_LINE 3.5): at most 0.12 bit. DERIVED.

## 8. The owner's two questions

### 8.1 Anything from the BLAKE2 research worth trying?

`..\literature\LITERATURE.md` read the BLAKE/BLAKE2 papers. Two more web searches here found nothing newer on
reduced-round BLAKE2s/BLAKE3 collisions (hits: https://ehash.iaik.tugraz.at/wiki/BLAKE.html,
https://eprint.iacr.org/2009/238). What transfers (DERIVED from LITERATURE.md and the sources it cites):
- Li-Xu's cancellation of a state-word difference by a message word of the same G call
  (https://eprint.iacr.org/2009/238) is the only BLAKE-era fixed-IV technique that applies, and the 55/63 path is
  exactly it with the block-length word. Section 5 shows it is the only such cancellation in one block.
- BLAKE2's counter and finalisation flags sit where BLAKE3 has counter, length and flags; in BLAKE3 the root
  counter is 0 and the flags are fixed per message shape, so only the length varies (S5).
- BLAKE2 fixed points, rotational and squeeze results need a chosen or symmetric IV (https://eprint.iacr.org/2013/467);
  the 2.5-round "BLAKE2s collision" of surveys is free-start; boomerang and higher-order MITM work targets the
  permutation or preimages (https://eprint.iacr.org/2014/1012, https://espitau.github.io/bin/HOD.pdf).
So nothing from BLAKE2 beyond what the filed path already uses.

### 8.2 Biology: nature's shortcuts, mapped and tested

| nature | the trick | as an attack step | result |
|---|---|---|---|
| reverse transcription, retrosynthesis | build backwards from the product | prescribe residual-side words, solve for the message | S1 dead, COMPUTED |
| alternative splicing, overlapping genes | one sequence read several ways | one base message read at 3+ lengths | S2 dead, COMPUTED |
| antibody affinity maturation | small mutations plus selection | hill climb on the residual | S3 dead, COMPUTED |
| flu reassortment, crossing over | swap segments between parents | swap w8..w11 between members | S11 dead, DERIVED |
| ant trails (stigmergy) | memory in the environment steers search | favour rich-looking contexts | S12 dead (record) |
| pooled testing, many ribosomes per mRNA | one test or machine for many copies | 7 lanes (filed) or 256-bit bitslicing | S9 small |
| kinetic proofreading (Hopfield 1974) | two cheap checks beat one expensive one | rule A, then the E1 test, with budgets | already in the filed path |
| enzymes | stored structure lowers the barrier | precomputed tables (memory is free) | filed per-outer-step table; bigger tables need a split that does not exist (`separable`) |
| allostery | a distant site switches the active site | the block length steering K2 | the filed path's Lemma L |
| base pairing | complementary halves bind | E1's difference mirrors E3's through the XOR fold | the filed residual condition |
| neutral networks | many genotypes, one phenotype | the 2^256 half-colliding pairs | the filed family |
| capsid / crystal symmetry | identical subunits | rotational, torus, mirror symmetry | dead (`fringe`, `shape_odd`, `shape_torus`) |
| gene duplication, endosymbiosis | a second copy or genome | two-block, two-chunk messages | S5, S8 dead |

Nature's shortcuts work where a problem has slack that small steps can exploit (folding funnels, selection on
partial fitness). At the residual this hash has none: one bit flip changes half of the 128 residual bits (S3), and
no residual-side word can be steered for free (S1). The slack it does have - the length cancellation, the free
half, the class - is what the filed path uses, and section 5 shows that slack is unique in one block.

## 9. What is left (for the main session)

- Nothing here gives a new entry. The honest new-path statement: in one block the filed structure is the only free
  half-collision (S10), so breadth must come from other pins/length pairs (atlas, ~101 each) or from leaving the
  free-half paradigm, where every tested route (idea 1, trails, symmetry, MITM) is far above the board.
- Small cost lever: bitsliced stage A (S9), worth looking at only if the cluster path is redesigned around it.
- The parity rule for pins (a pin exists for a length pair iff the XOR is even; no pin for any triple) is a clean
  fact the atlas can cite. COMPUTED (z3).

## 10. Files

`SIDEPATHS.md` (this), `fam55.py` (filed construction, self-tested), `locality.py` + `locality.txt` (S3),
`pin_model.py`, `mk_models.py`, `gdx.c`, `build.sh`, `run_gdx.sh`, `batch1.sh`, `batch2.sh`, `union.sh`, `union.py`,
`m_*.model`, `res_*.txt`, `all_y4_w5_k6.txt` (S1), `siblings.py`, `triple_smt.py`, `triple.sh`, `sweep_sib.sh`,
`sweep_sib2.sh`, `sweep_sib.txt`, `sweep_sib2.txt`, `triple_*.out`, `h8check*.smt2`, `double_smt.py`, `double.sh`,
`double2.sh`, `double_results.txt`, `double2_results.txt`, `sib\`, `sib2\`, `dbl\` (S2), `leak_smt.py`, `leak.sh`,
`leak_results.txt`, `leak\` (S10).
