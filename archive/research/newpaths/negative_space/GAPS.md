# GAPS: the negative space of 2-round BLAKE3, and what is left untried

Folder `research\newpaths\negative_space`. Written 2026-10-08. Research only: existing records were re-read and
re-coded, and no experiment was run. Nothing was filed, posted or cancelled, trace is untouched, pkg11 is untouched,
and nothing was written outside this folder. Every "cheap first test" below is a proposal. None was run here.
Tags: COMPUTED / DERIVED / GUESS as in the catalogue. The coding of each record onto the axes is GUESS (judgement).

Files: `AXES.md` (codes), `records.csv` (191 rows), `GRIDS.md` (three grids), `cells.csv` (ids per cell), `build.py`.

## 0. The map in numbers

- Records: 191 = 170 catalogue + 13 new (X: today's counter_next and counter_swing outputs) + 8 CENSUS-only (K).
- Status: alive 38, dead 107, open (logged, never run) 15, n/a 31 (concerns and tools).
- Grid marks:
  - free x tech, 72 cells: alive 8, dead 20, impossible 32, untried 12.
  - base x tech, 45 cells: alive 8, dead 21, impossible 7, untried 9.
  - layer x tech, 54 cells: alive 7, dead 26, impossible 5, untried 16. Most of these are coding artifacts; see GRIDS.md.
- Not available: `newpaths\collision_pattern` is empty, and `newpaths\hotspot` does not exist. counter_next and
  counter_swing have no summary document, so the X rows come from their printed outputs only.

## 1. Shape of the negative space (DERIVED from records.csv)

1. **One base carries everything alive.** All 35 alive 2-round records rest on the block-length cancellation (C1):
   26 on the root free half (fh), 8 on the counter lever (ctr), and 1 re-instanced (A11). No alive record exists
   without it.
2. **The alive band is narrow.** It runs canc at r0 (the free half), then class or gd at r1c/r1d (the residual),
   then cost levers. The 8 alive cells of free x tech are len x canc, cv x canc, msg x gd, ctr x gd, msg x class,
   const x class, none x class and none x cost.
3. **Three regions are closed in every technique tried.**
   - Idea-1 family: 28 dead across 7 techniques. The floor is 4 checks (192), and the best is 144 (I4).
   - Generic whole-function methods: 23 dead. Trails cost at least 2^185, symmetry is blocked by the IV, and there
     is no gradient.
   - Mode-level differences: 13 dead. Anything that puts the two messages at different node types or positions
     dies (M1, X7, X8, K2, K10).
4. **The walls (X cells) have five reasons.**
   - IV0..IV3 sit in row 2 of every compression, so there is no symmetric state.
   - Length and flags have few legal values, so they work only as pair differences.
   - Round 0 is solved by its inverse (C4), so there is nothing to search there.
   - Tables cut cost per trial, never the trial count (R21).
   - Cost levers save at most log2(430) = 8.7 bits, against a best dead-region form of 144.
5. **The untried cells cluster on the counter base.** It is new: 4 of its 9 techniques were never tried. They also
   cluster on chosen constants (const x join, alg, heur).

## 2. Untried cells, ranked by plausibility (GUESS ranking)

| # | cell (grid: row x col) | plausibility | one-line reason | cheap first test (not run) |
|---|---|---|---|---|
| 1 | free: const x alg, on base ctr | medium-high | Pins were searched only for the root rate (R17: none better at bounds 100-103). The counter's rate factor is instead R_beta x 2^k for the one prescribed beta, and that reorders pins: L6c is 101.37 at the root but 87.14 on the counter (CENSUS). | Rank every pin with a per-beta file by max over beta of R_beta x 2^k. Count per-beta files for the 10 scored pins that lack one (L8c, L8d, L4b, ... L120a; L8b is screened only). Then rerun the pin solver with that objective for deltas 8 and 6. Any new pin is its own entry. |
| 2 | free: mem x alg, on base ctr | medium (only if X2 holds) | X2 spends 2^18.5-2^19.3 ops per passing outer step. E3's inputs are outer-step values (e3real 40/40), memory is free, and 2^85 preprocessing is negligible (C15). | From e3solve, count the distinct keys the DFS reads per passing step (tau and the Y9/w8 bits it touches). A key space of 2^60 or less makes a table feasible. Gain is GUESS, about 2 bits, the gap between V4p 70.21 and V4s 68.14. |
| 3 | free/base: ctr x alg | medium | A solver per trial lost about 18 bits on the root (N6), because trials cost 6.5 ops. On the counter path a passing step comes once per 2^9.81 outer steps (X1), so a solve per pass is affordable. | Hand the recorded E3 systems of about 20 passing steps to CaDiCaL or CryptoMiniSat (XOR on), and compare their work with the DFS's 2^15.9 nodes. stack_calc's V4s (68.13) already GUESSES 2^15. |
| 4 | free/base: ctr x join | low-medium | The split was 0 bits at counter fixed (N17). With t free, E3 is fixed per outer step, so the B event is a one-sided target. A join needs an E1-side list that does not depend on the outer step. | Run the two-sided split search (`grok\work\job30_split\coupling.py`) on `counter_next\knobs\model.py` with t free (seconds). |
| 5 | free: const x join | low | N17 names this exact need: a construction that decouples E1 and E3. C7 (no small separator) argues against it. | Same split search, with each candidate extra pinned word added as a constant. |
| 6 | free/base: ctr x trail | low | The exact counter (V1) already sums every E1/E3 characteristic, so a trail tool (T11) adds conditions, not rate. | None before 1-3. Check what T11's tool needs. |
| 7 | ctr x heur, const x heur, cv x heur | low | No gradient: one flip changes 63.5 of 128 bits (N15, C7). For constants, exact counting beats search (R17). | None. |
| 8 | base mode x trail/alg/heur/cost; free cv x trail, flag x trail; base gen x class | very low | Rate does not depend on the instance (A11, 8 instances; R18). A CV or flags difference reaches both halves. CV words in row b cannot be absorbed by one call (CONCERNS 4). A flags difference is absorbed by w6 and w7, but w6 lands in C0.y, which changes all four of C0's outputs (CONCERNS 3). Trails cost at least 2^185 (C8). Distinguishers do not transfer to a 256-bit match (L4). | None. |

## 3. Logged ideas never run (open), worth one line each

- **X9: the counter prescribes E3.h1 instead of E1.d1.** A basis exists with t free (constraint_check part 2) but
  was never valued. Test: from a15_outcomes.tsv and the e3cond tables, compute P(h1 condition | success)/q and
  compare it with 2^9.55 for E1.d1. Plausibility: medium-low. X2 already harvests most of E3's structure per pass.
- **A10: clusters on the counter loop.** GUESS 2-3 bits. It brings back the H4-H6 premises that made 64c075ac
  not_evaluable (C11). Value: medium. Evaluability: poor.
- **X6 and census V10: high counter word t_hi solved per outer step.**
  - GUESS: no gain if the aim is to force passing outer steps. Realising w8 costs a 2^-13 filter, while the natural
    pass share is 2^-9.81 (X1). DERIVED from those two figures only.
  - A w8-conditional count would settle it.
- **G9: richest c1 values.** This is part of A9 and needs Sol's enrichment count.
- **Small root refinements:** R2 (0.28 bit), R4 (0.12), R16 (about 1/3 bit).
- **Long shots, each needing a tool build:** T6 (period-8 differences), T7, T11, T12, L1 (bit-level carry MITM),
  L2 (programmatic SAT), I20, I21.

## 4. Edges: a dead cell next to an alive one

| edge | dead side | alive side | worth probing? |
|---|---|---|---|
| E1 prescribed words | N1: a second word at counter fixed | A9: t free buys exactly one word; N23: three words dead | settled; the open question is which word (X9) |
| E2 outer-step selection | R4: certified +-8.4% on the root, about 0.12 bit | X1: exact filter on the counter, +9.8 bits, because E3's inputs are outer-step values | **yes, first.** Word-model check (seconds): does the root two-level loop also fix (Y4, Y9, w8) per outer step? If it does, the gain lands on the root path, the only one whose half the harness can see. GUESS: unlikely, since the +-8.4% certificate says outer words barely move the root rate. |
| E3 solver work | N6: SAT per trial | X2: a solve per passing outer step | yes: gaps 2 and 3 |
| E4 pins | R17: no better root pin | K4: the counter reorders pins | yes: gap 1 |
| E5 split / MITM | N17: 0-bit split at counter fixed | ctr x join untried | gap 4 |
| E6 resolution | bit-level gd and steering (I16, N8, N9, L5) | bit-level class selection (A3-A5, R7, X1, X3) | bit-level join (L1) is logged, never run: low |
| E7 tree position | the two messages at different nodes or types (M1, X7, X8, K2, K10) | the same position, non-root (A9, A11, K3, K4) | no: the boundary is exact |
| E8 multi-block last chunk | t per trial (K1: the CV depends on t, 0/1000) | t constant (A11 / census V06) | no: every block of chunk t carries t |
| E9 clusters | (none dead) | A8 on the root (not_evaluable) | A10 on the counter: only if H4-H6 can be evidenced |

## 5. Limits

- Each record has one value per axis, its key idea. A record that mixes ideas (for example A5 = length + pin + class)
  appears only under its key idea. The base grid adds context, but a different coding would move some cells.
- X1 to X4 and X13 are DERIVED and unadjudicated. X2 found 0 E3 solutions in 270 real passing steps. At this depth
  that is no evidence either way (GUESS).
- Plausibility ranks are judgement.
- Blocked: nothing was refused or stopped.
