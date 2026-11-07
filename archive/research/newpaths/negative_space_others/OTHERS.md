# OTHERS: the other teams' research on our negative-space chart

Folder `research\newpaths\negative_space_others`. Written 2026-10-08. Research only: notes were read and public
pages fetched read-only. Nothing was filed, posted, commented or cancelled, yukon was not run, and trace is untouched.
Credit: every row names the team and the entry id as their notes give them. Their work is theirs.

**Files.** `records_others.csv` has 93 rows (OT01-OT93). It uses the columns of `negative_space\records.csv` plus
`team/entry`, with the same axis codes (`negative_space\AXES.md`).
- `cost` is their own score.
- `label` is their review state: review plausible_not_refuted, PROMOTED, FAILED (with the source of the reason),
  or "their note (not judged)".
- `status` follows AXES.md. A generic entry at 128 or above is `dead`, because it gains nothing over the nominal
  128, even when its own line counts it alive.
- The coding onto the axes is judgement (GUESS), as for our records.

**Sources** (fetched 2026-10-08, about 23:10-23:30 UTC):
- local notes: `research\rivals\` (11 notes), and `research\others\notes_r2\` and `notes_r1\` (95 notes), with
  their digest `research\others\TECHNIQUES.md`;
- 622 pull requests of github.com/Layr-Labs/hash-smash (public API). Each submitter note is the PR body. About 100
  are BLAKE3, and 14 r2 notes are newer than the local copies;
- PR comments for the outcome of 9 entries;
- four review dossiers through nightly.link (runs 37584006810, 37682823958, 37658843575, 37815183846);
- discussions 399 and 520. The repository has no plain issues.

Blocked: nothing was refused. Proofs inside the packages were not read, only the notes and dossier findings.

## (a) Their wins that our records lack or set aside

Our record is checked in `catalogue\catalogue\METHODS.md`. The cell is where the row lands in our grids.

| lever (team, entry, row) | worth to them | our record | cell (our mark) |
|---|---|---|---|
| **Loop order S2K.** Lanes over seven X2 values, a per-outer-step X2 table (about 2^40 bytes), and Lemma A3 folds rule A into one constant per 256 positions. Stage A 28 -> 19. (winglock c19feef4, OT19) | 94.1982 -> 93.7358 | lack | mem x cost (dead: R21) |
| **Lane stride 2^14.** Lanes 2^14 apart share rule-A outcomes less often; stage-B share 0.5765 -> 0.377 p_B. (Subflatus3 ef81f589, OT23) | -> 93.5891 | lack | msg x cost, r1d x cost (untried) |
| **Paired and quad stage-A tests** with a hit tree of at most 10 ops per entry. (Subflatus3 5ca02dfb OT25; winglock ef052659 OT26) | -> 93.5576 -> 93.5322 | set aside (R5 pooled testing, "low priority") | r1d x cost (untried) |
| **Early exit on W4** (Lemma E: shared Y4 gives f1^f1' = ROR(g1^g1',12), so W4 needs E1 to a2 and E3 to g1 only). Stage C 119 -> 61. (winglock ef052659, OT26) | part of 0.025 bit | lack | fold x cost (untried) |
| **Lemma D' and the block accumulator.** One zero test per X14 value, 224 -> 219 ops. (winglock 2bb5d604, OT07) | 96.86 -> 96.75 | lack | fold x cost (untried) |
| **Premises from preregistered uniform samples.** Single-batch units (Lemma U), Lemma C' plus the empirical Bernstein bound at 2^-64 as the decision rule, budgets 1/6000 above the premise. (Subflatus3 52bb50ee OT12 and 1d5e54ce OT18; leech1996 5266c5ce OT13) | 94.45 -> 94.167; 52bb50ee is the only promoted r2 entry | set aside (R2 "not started") | none x cost |
| **One score-critical heuristic.** All premises are parts (i) and (ii) of H1. On d598fe29 all four lanes rated it plausible, with material findings only. (winglock line, OT31) | it passes review | lack (our 64c075ac failed on separate H4-H6) | none x cost |
| **X14 = 0** by D3.d1 = X3 (winglock 21252124, OT15) | 94.24 -> 94.1982 | set aside (R6 "not adopted") | msg x gd |
| **64 registers** with resident constants (all of winglock's line) | about 0.5 bit (TECHNIQUES 2.1) | set aside (R12, owner) | none x cost |
| **Generic line below 128.** Seven 36-bit lanes (tekkac 2bf40fb6, OT50); grouped partial evaluation (jaazinn, ercumentyildirim); interleaved keys at **124.937** (winglock afb6e58f, OT58); bitsliced hash at 137.65 ops/message, under one compression (jungjipdo bda6f216, OT74); 2^128 samples meet the 0.39 bar (leech1996 86108a41, OT83) | 140 -> 124.937 | lack (our records hold the generic as "128" only) | gen x cost (**X** in ours) |
| **Fixed-a3:** two message words fix a state word, so one round-1 call is constant over the inner loop. (5kyguy 200fd0ea OT59, 5ebba6b3 OT60) | 227 -> 212 ops; 125.16 | lack | r1c x gd (untried); gen x gd (dead) |

Order to test, by size against effort: the evidence route (samples + one H1), then S2K and the 2^14 stride if
they carry over to our two-level loop (about 0.6 bit for them), then the early exit and the quad test.

## (b) Their dead ends (and wins) in cells our chart marks untried or impossible

`python -B overlay.py` (this folder) lays their rows (status alive/dead/open, base not r1) over `cells.csv`, the
same filter as `build.py`. Cells flagged `<<<` differ from our mark.

- **Untried in ours, dead ends in theirs:**
  - r1d x cost: four dead ends.
    - leech1996 5266c5ce: no stage-A cut from rotation hoisting or duplicate lanes (OT14).
    - Subflatus3 ef81f589: every other stride 2^k (k = 0..29) and every odd multiple is worse than 2^14 (OT24).
    - winglock ef052659: no hit tree below 10 ops per entry (OT27).
    - Th0rgal df8bd46d: a 2^32-entry table costs 122 ops/batch against 42 packed (OT36).
    Three wins sit in the same cell.
  - msg x cost (ours "o 1"): the stride scan above (OT24), next to 10 alive rows.
  - cv x trail: winglock 208336d1: Li-Xu's 2- and 2.5-round results are free-start only, so out of scope (OT44).
- **Untried in ours, alive in theirs:** fold x cost (OT07, OT26) and r1c x gd (OT59, OT60; OT61 open).
- **Marked dead or impossible in ours, alive in theirs:**
  - gen x cost (**X**, "best generic form is 144"): 11 alive generic entries at 124.937-127.481. The wall's
    number is wrong for plain birthday plus cost work. It is still about 32 bits above the structural line.
  - gen x gd (dead): fixed-a3 and state-word enumeration at 125.10-127.25 (OT57, OT59, OT60).
  - mem x cost (dead, R21): the S2K table (OT19). It cuts cost per trial, as the X reason says tables can, and it
    was worth 0.46 bit.
- **Our walls, confirmed by their dead ends:**
  - r0 x trail: the complement pair breaks in round 2 (OT42, OT87).
  - r0 x join: per-column collisions do not assemble (OT76).
  - r0 x alg: closed-form partner per G (OT77), and the "algebraic look" (OT49).
  - all x alg: ten Bitwuzla runs ended "unknown" (OT43, next to our N22).
- **Not touched by anyone:** the whole ctr row, the mode and flag rows, const x join/alg/heur, and gen x class.
  None of their 93 rows uses the chunk counter (see d).

## (c) Our gaps (GAPS.md) that someone else already covered

- **Section 3, R2, budgets just above the premise (0.28 bit): covered, and their failure shows the trap.**
  - The method is Subflatus3's 52bb50ee, 1d5e54ce and ef81f589, plus leech1996's 5266c5ce: preregistered
    single-batch samples of 2^34-2^35 units, Lemma C' with the empirical Bernstein bound at 2^-64 on a 1/1000 grid,
    budgets x6001/6000. The samplers (sbmeas.c, sbbatch.c, sbs2k.c) are in their proof appendices.
  - The trap: leech1996's 9b9f45d0 picked 0.585 after reading the sample, with no fresh sample. It was ruled
    not_evaluable (F-H1-POST-SAMPLE, OT17).
- **Section 3, A10 (clusters bring back H4-H6), and edge E9:** the route that has passed review is one H1 with
  parts (OT31). Separate premises H2/H3 were ruled unsupported on bc68993e (OT05). Same pattern as our 64c075ac.
- **Edge E2 (outer-step selection on the root):** partial. GordoAR 6a600434 and winglock d598fe29 cut the vd range to
  70 percent, and the stage rates barely moved:
  - d598fe29: 0.3 and 0.1 combined s.e. for the stage-B share and for rule A with the filter;
  - 6a600434: stage-B share 0.5456 against 0.5464, about 1.7 s.e.
  That is the stage events only, not the full event, but it agrees with "outer words barely move the root rate".
- **Gap 3, a solver per passing step:** no one did it per pass.
  - winglock's whole-instance SMT runs ended "unknown" (OT43).
  - The judge refused SAT wall-clock converted to operations as an "undisclosed implicit heuristic" (kampred99
    46281d57 and three successors, OT92). Gap 3's solver work must be bounded in counted operations (node count
    x ops per node), not in seconds.
- **Gaps 4 and 5, joins:** not covered on our bases. The same obstacle is confirmed independently.
  - winglock 18a7fc52 on Jbenisek's 60/62 line: "a second freely settable word and a residual birthday ... Each
    round-1 column call feeds both E1 and E3" (OT03).
  - The only working half-split MITM is at 1 round (kampred99 1d598029, 80, OT88).
- **Gap 8 (cv x trail):** confirmed very low. Li-Xu's 2-round results are free-start only (OT44).
- **Not covered by anyone:** gaps 1, 2, 6 and 7; X9; R4 and R16; L1; and every counter cell.
- **Correction to section 1, point 4, and the gen x cost X reason:** the generic line is at 124.937, not 144
  (see b).

## (d) What their notes say about our chunk-counter method

**No prior use found.** Searched for chunk, counter, tree, parent, non-root, multi-chunk, leaf, v12 and 1024: the
95 local notes, the rivals folder, and about 100 BLAKE3 PR bodies. Every r2 entry hashes one root block with
counter 0 and flags 11, in 55/63, 64 or 33 bytes. Nobody uses a second chunk, a non-root compression, or the
counter as an unknown. Only notes and PR bodies were searched, not the proofs.

What bears on it:
1. **The profile allows it, and one team said so.** zeeshan8281 868829c0: "The target profile permits other
   message lengths and preserves the complete standard 1024-byte chunk tree, parent nodes, counters and root
   output". The same note keeps the root flags "rather than searching for a collision of a free-start or non-root
   compression function". A reviewer may file "non-root collision" under out of scope, so Lemma T must lead the
   proof.
2. **"A second freely settable word" failed before.** winglock 18a7fc52 tried one with the counter fixed: "none of
   these led anywhere". The counter cancels in round 0 but meets the same round-1 calls (col2.y, diag0.x). Our
   claim is narrow: one prescribed word, c1 in the beta* cube. The proof should say in one line why winglock's
   obstacle does not apply.
3. **Round-1 injectivity assumes counter 0.** winglock 208336d1 proves that the round-1 state fixes all 16 message
   words. With t free, round 0 is 2^32-to-1. The two do not conflict, but a reviewer may cite theirs, so we should
   state the difference.
4. **E is their beta filter.** Every staged machine since 098e66f4 tests it as stage B. With t solved it becomes
   certain, so the S2K14, quad and early-exit levers, tuned to a stage-B share of 0.377 p_B, would need to be
   re-derived rather than stacked onto 84.96. GUESS.
5. **The harness cannot run it at full size.** The sandbox is 20 s, 128 MB, one CPU, with no file reads
   (Subflatus3 daaa89de failed intake at about 24 s; GordoAR 2553709b crashed reading a file). Verification
   compressions must be charged (GordoAR 8fc264b9). A 2-4 TiB pair can be neither built nor checked there, so use
   internal events or toy widths (METHOD_NOTE section 4 already says this).
6. **New premises need a frozen sample.** The unpriced t = 0 exclusion and the t distribution should be bounded in
   the proof or covered by a preregistered sample. A post-hoc number failed (9b9f45d0, OT17).
7. **A declared preprocessing bound can fail on its own.** On 9b9f45d0 the evaluability lane rated the declared
   2^86 bound unsupported ("implicit-preprocessing-upper-bound"), and that alone made it not_evaluable. The same
   2^86 passed on every other entry in that line.
8. **Bundle the premises.** The counter needs fewer premises (no H4-H6). Written as parts of one H1, with the sample
   code in proof.md, it follows the route that passed on d598fe29.

**Reasons it would not work:** none stated. The only "tree-parent" mention is Subflatus3 fdc25b28 (r1, 1.83): a
"dead avenue" with no detail (OT89). On r1 one more compression costs a whole unit against scores near 2, and that
reason does not carry over to r2.
