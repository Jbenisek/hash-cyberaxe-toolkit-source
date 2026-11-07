# SHA-256: tried and untried, by technique family and step depth

Generated 2026-10-10 12:50 -0600 by `research/endgame/sha256_grid.py --md` from the same records as `sha256_cells.csv` (this
folder), which `research/endgame/make_endgame.py` draws on the endgame page. Edit the script, not this file. Research
only: nothing staged or submitted, no yukon commands, and no solver, GPU or experiment run for this grid.

**Tracks.** sha256-r37-exploratory (unit 2644; board best 61.71473, d3ec5c41) and sha256-r38-exploratory (unit
2728; board best 72.64, 0ae69bcb; our derivative row 72.61489, unfiled). r31 and r32 are closed boards, kept as
history.

**Sources.** Our own summaries only, under `research/sha256grid/`: `map-lit/FAMILIES.md` (the 20 rows),
`map-lit/literature.tsv`, `map-lit/leader_cost_split.txt`, `map-r37/gaps_r37.tsv`, `map-r37/ledger_levers.out.txt`,
`map-r38/MAP_r38.md`, `map-r38/levers_r38.out.txt`, `holes/late_variants_r37.log`. No board JSON, BOARDS_TABLE.tsv or
other teams' notes were opened; other entries appear by id only.

**Labels.** Each number keeps its source's label. COMPUTED: exact arithmetic or a program's output. DERIVED: read or
reasoned from a cited source; board scores are DERIVED (participants' filed numbers). GUESS: an untested estimate.
The counts below are COMPUTED by sha256_grid.py.

**Columns.** r31, r32: closed boards. r33-36 and r39+: no board, so a cell there counts as tried only where a
published result or a measured run exists at that depth. r37, r38: the live boards.

**Cell marks.** `T x`: tried, best score x (or the result named). `C x`: closed, x is the closing number. `U`:
untried. `n/a`: not applicable (the rules exclude it, the method stops below 31 steps, or no source exists). `Cn`: n
closed levers inside a tried cell. `on`: n logged ideas not yet tried. On the closed boards T means used in a filing
not stated as failed, and C means used only in failed filings. † marks a record whose track (r31 or r32) is not in
our summaries; it is listed in both columns. On the page these show as A (tried), D (closed), o (ideas) and X (n/a).

## Grid

| family | r31 closed | r32 closed | r33-36 no board | r37 live | r38 live | r39+ no board |
|---|---|---|---|---|---|---|
| F01 generic birthday | T 125.94 | T 124.6 | U | T 123.93722, C1 | T 123.96717, C1 | U |
| F02 grouped / round-skip birthday | T 125.94 | T (no score) | U | T 123.93722 | T 123.96717 | U |
| F03 single-block local collision | n/a | n/a | n/a | n/a | n/a | n/a |
| F04 characteristic search | C refuted † | T 46.57, C1 | T 2^45.86 run | U, o1 | U, o1 | T lit 39-step SFS |
| F05 SFS / free-start as end product | n/a | n/a | n/a | n/a | n/a | n/a |
| F06 two-block SFS-to-collision | T 31.61 | T 39.964 | T lit 35: 2^48.3 | T 61.71473, o1 | T 72.64 | C 39 not reached |
| F07 truncated longer route | U | T 46.57 | U | U, o1 | n/a | n/a |
| F08 multi-target variants | T 31.61 | T (no score) | U | T 61.71473, C1, o2 | T 72.64, C1, o1 | U |
| F09 CV-indexed tables | T (no score) † | T (no score) † | U | T 61.71473, C2, o1 | T 72.64, C3 | U |
| F10 condition relaxation | T 31.61 | T 39.964 | U | T 61.71473, o2 | T 72.64, o1 | U |
| F11 early abort / staged filters | T (no score) † | T 39.964 | U | T 61.71473 | T 72.64, o2 | U |
| F12 bit-slicing / SWAR | T (no score) † | T (no score) † | U | T (no score), o3 | T 99.91651, o4 | U |
| F13 neutral bits / boomerangs | C failed build † | C failed build † | U | U, o1 | U, o1 | U |
| F14 multi-block near-collision | U | U | U | U, o1 | U, o1 | U |
| F15 GPU brute force | U | U | U | C 261.5 days, o2 | U, o1 | U |
| F16 advice / allowance accounting | T 37.22 | T 46.57 | U | T 61.71473, C2, o1 | T 72.64, C2, o2 | U |
| F17 stored-pair replay | T 31.61 | T (no score) | U | n/a | n/a | n/a |
| F18 ledger engineering | U | T (no score) | U | T 61.71473, o1 | T 72.61489 ours, C2, o3 | U |
| F19 other 37-step characteristics | n/a | n/a | n/a | U, o2 | n/a | n/a |
| F20 whole-problem SAT | U | U | U | U, o1 | U, o1 | U |

Counts (COMPUTED by sha256_grid.py, 120 cells):

| column | tried | closed | untried | n/a |
|---|---|---|---|---|
| r31 | 10 | 2 | 5 | 3 |
| r32 | 13 | 1 | 3 | 3 |
| r33-36 | 2 | 0 | 15 | 3 |
| r37 | 10 | 1 | 6 | 3 |
| r38 | 10 | 0 | 5 | 5 |
| r39+ | 1 | 1 | 13 | 5 |
| all | 46 | 5 | 47 | 22 |

## Live tracks: untried families and logged ideas

### r37 (board best 61.71473)

Untried families here (a filing would be a new line on this track): F04, F07, F13, F14, F19, F20.

- F04 characteristic search (U, o1): G5b-re-optimised-characteristic(GUESS-multi-bit)
- F06 two-block SFS-to-collision (T 61.71473, o1): memory-heavy-2026/1080-variant(G9)
- F07 truncated longer route (U, o1): 38-step-2026/1120-route-cut-to-37(low-value-GUESS)
- F08 multi-target variants (T 61.71473, C1, o2): A1/A2-variants(16.04x-family;gain-at-most-about-0.14-bit); fresh-Step-1-solutions(x2->61.11006)
- F09 CV-indexed tables (T 61.71473, C2, o1): G7-W6-cb-table(gain-about-0.03-bit-GUESS)
- F10 condition relaxation (T 61.71473, o2): Step-3-relaxation(74-conditions;q3-x2->61.0987); G5c-q3-as-collision-event(gain-at-most-0.2-bit-GUESS)
- F12 bit-slicing / SWAR (T (no score), o3): G2-bit-sliced-first-blocks(gain-about-0.13-bit); G1-7-lane-SWAR-for-u(gain-about-0.08-bit-GUESS); bit-slice-u-over-gathered-pairs(GUESS-worse)
- F13 neutral bits / boomerangs (U, o1): neutral-bits/boomerangs-rows-16..22(GUESS)
- F14 multi-block near-collision (U, o1): multi-block-near-collision(GUESS-dearer)
- F15 GPU brute force (C 261.5 days, o2): GPU-exhaustive-table-stats-H9(gain-0-to-0.04-bit); GPU-large-q3-studies(evidence-only)
- F16 advice / allowance accounting (T 61.71473, C2, o1): measured-37-step-re-run(A_C-removed->61.19051)
- F18 ledger engineering (T 61.71473, o1): Bernstein-cap(gain-about-0.013-bit)
- F19 other 37-step characteristics (U, o2): ZLGW26-2026/232-37-step; LLWS26-2026/1080-37-step(theoretical)
- F20 whole-problem SAT (U, o1): whole-collision-SAT(GUESS-unlikely)

### r38 (board best 72.64)

Untried families here (a filing would be a new line on this track): F04, F13, F14, F15, F20.

- F04 characteristic search (U, o1): new-characteristic-or-dense-part
- F08 multi-target variants (T 72.64, C1, o1): G6-fresh-Step-1(L*=4:gain-about-0.26-bit-GUESS)
- F10 condition relaxation (T 72.64, o1): Step-3-relaxation(about-101-conditions;q3-x2->72.064)
- F11 early abort / staged filters (T 72.64, o2): G4c-unrolled-entry-loop(gain-0.169-GUESS); decision-DAG-on-A0-blocks(7319bba9-port)
- F12 bit-slicing / SWAR (T 99.91651, o4): G4a-first-block-bit-sliced(gain-0.069-GUESS); G4b-A0-blocks-packed(gain-0.115-GUESS); G4d-row-17-path-bit-sliced(gain-0.079-GUESS); G8-solved-first-block-family+DP-tables(GUESS)
- F13 neutral bits / boomerangs (U, o1): neutral-bits/boomerangs-rows-16..22(GUESS)
- F14 multi-block near-collision (U, o1): multi-block-near-collision(GUESS-dearer)
- F15 GPU brute force (U, o1): GPU-large-q3-studies(evidence-only)
- F16 advice / allowance accounting (T 72.64, C2, o2): G2-A_S-2^50(->72.37992); G3-r37-allowances-or-measured-A_C(->72.06709)
- F18 ledger engineering (T 72.61489 ours, C2, o3): G1-revert-two-margins(->71.66909); G5-N1-cap-1.25x(->72.60991); G7-organizer-executed-H5-test
- F20 whole-problem SAT (U, o1): whole-collision-SAT(GUESS-unlikely)

## Largest logged sizes on the live tracks

Copied from the sources with their labels; nothing was re-run for this grid. Totals are log2 of the charged work.

**r37 (board best 61.71473).**
1. F10 Step-3 condition relaxation, never used on r37 (it worked on r31/r32): q3 x2 gives 61.0987 and x4 gives
   60.6520 (COMPUTED from GUESS gain factors).
2. F08 fresh Step-1 solutions: success per first block x2 gives 61.11006 (DERIVED); how far L* varies between
   solutions is a GUESS.
3. F16 a measured 37-step re-run of the characteristic search: with A_C removed, 61.19051 (DERIVED); out of reach on
   two CPU processes (GUESS: days to weeks).
4. F08 A1/A2 variants: a gain of at most about 0.14 bit (DERIVED), overlapping F12's G2.
5. F12 bit-sliced first blocks in the A0-variant line: about 0.13 bit (DERIVED).
6. Smaller: F12 7-lane SWAR for u, about 0.08 bit (GUESS); F15 exhaustive table statistics, 0 to 0.04 bit; F09 W6 cb
   table, about 0.03 bit (GUESS); F18 Bernstein cap, about 0.013 bit.
7. New lines of unknown size, each a distinct path: F19 the unused 37-step characteristics (2026/232, 2026/1080); F04
   our own or a re-optimised characteristic (GUESS multi-bit); F07 the 38-step route cut to 37 (low value, GUESS); F13
   neutral bits or boomerangs on rows 16..22; F14 multi-block chaining; F20 whole-collision SAT.

**r38 (board best 72.64; our derivative row 72.61489).**
1. F18 G1, the leader line's two voluntary margins reverted: 71.66909 (COMPUTED, premise risk); with F16 G2 and no
   pad, 71.11112 (COMPUTED).
2. F16 G3, r37's allowance convention or a measured A_C: 72.06709 (COMPUTED; the r38 judges refused 2^64 and 2^68).
3. F10 Step-3 relaxation: q3 x2 gives 72.064 and x4 gives 71.665 (COMPUTED from GUESS factors).
4. F12 and F11 engine work on the scalar DP program: conservative 72.11254 (GUESS op counts).
5. F16 G2, A_S at 2^50: 72.37992 (COMPUTED, low risk).
6. F08 G6 fresh Step-1 solutions: about 0.26 bit online at |L*| = 4 (GUESS).
7. Smaller: F18 G5, the N1 cap 4x -> 1.25x: 72.60991 (DERIVED).
8. New lines: F04 a new characteristic or dense part, F13 neutral bits, F14 multi-block, F20 whole SAT. F15 (GPU) can
   only add evidence.

## Cell notes

One line per cell with its best score or closing number and its sources. Cells not listed have no board at that depth and nothing recorded. Record ids for every cell are in sha256_cells.csv (and on the endgame page, on hover).

### F01 generic birthday

- r31, T 125.94: best 125.94 (d02732c7), DERIVED [FAMILIES]; closed board
- r32, T 124.6: best 124.6 (5c3f233e), DERIVED [FAMILIES]; closed board
- r33-36, U: no board at this depth; the generic cost does not depend on depth (about 2^128 nominal, DERIVED [FAMILIES]), so there is nothing to scout
- r37, T 123.93722, C1: best 123.93722 (5951ba00), DERIVED [FAMILIES], 62.22 bits above the leader 61.71473 (COMPUTED). Closed as a lever: rho / vOW alternatives are irrelevant at 124 vs 61.7 [gaps_r37 G9]
- r38, T 123.96717, C1: best 123.96717 (668d3f56), DERIVED [FAMILIES]; distribution-free entries f02ff88f, 8c92f07c, 1708c3d3, 6739adfa at 128.12-128.23 [MAP_r38]. Closed as a lever: the generic family is exhausted, floor about 123.9 (DERIVED [MAP_r38])
- r39+, U: no board at this depth; the generic cost does not depend on depth (about 2^128 nominal, DERIVED [FAMILIES]), so there is nothing to scout

### F02 grouped / round-skip birthday

- r31, T 125.94: best 125.94 (d02732c7), DERIVED, and 35ce0758 [FAMILIES]; closed board
- r32, T (no score): 68ca8e4f and 6b88bdb7 used it; their scores are not in our summaries (the generic-family best on r32 is 124.6, 5c3f233e, row F01) [FAMILIES]
- r33-36, U: no board at this depth; the generic cost does not depend on depth (about 2^128 nominal, DERIVED [FAMILIES]), so there is nothing to scout
- r37, T 123.93722: best 123.93722 (5951ba00), DERIVED; also 64bca7e2 and 6de1b685 [FAMILIES]
- r38, T 123.96717: best 123.96717 (668d3f56), DERIVED; also c65868c3. The ladder 124.968 -> 123.96717 is constant factors on one idea: one-block 55-byte messages, 2^24-message groups sharing W0..W12, a key on digest words fixed before the last rounds, bit-sliced 256-lane circuits [MAP_r38]
- r39+, U: no board at this depth; the generic cost does not depend on depth (about 2^128 nominal, DERIVED [FAMILIES]), so there is nothing to scout

### F03 single-block local collision

- r31, r32, r33-36, r37, r38, r39+, n/a: not applicable: single-block local-collision routes stop at 28 steps (MNS13 practical 28-step collision, DERIVED [literature.tsv]); every column is 31 steps or more

### F04 characteristic search

- r31, C refuted †: 6d554419: own in-chain SAT search, failed (refuted) [FAMILIES]. † Its track (r31 or r32) is not in our summaries, so it is listed in both columns; 8bad82c1 / 1ded36a8 (measured route search) are listed for r31/r32 without track or status. r31 entries used the published LLWDS24 31-step characteristic [literature.tsv]
- r32, T 46.57, C1: best 46.57 (6eeefb64, promoted): a measured re-run of the characteristic search for the 35-step route cut to 32, DERIVED [FAMILIES]. † 6d554419 refuted (track not stated); 8bad82c1 / 1ded36a8 measured route search (track and status not stated)
- r33-36, T 2^45.86 run: measured run: 6eeefb64 re-ran the 35-step characteristic search, 593,858 CPU-s [gaps_r37 G4], quoted as 2^45.86 [MAP_r38 H4], DERIVED; the published routes behind the boards come from the public SAT/SMT tool [LLW24a] (DERIVED [literature.tsv])
- r37, U, o1: untried on the board: the 37-step search is only charged as the allowance A_C = 2^60 (row F16). Logged: G5b, re-optimise the characteristic for the variant-amortised regime, GUESS multi-bit, needs the LLW24 tool and a new search (heavy) [gaps_r37]; our own characteristic with a measured search would also be a new line [FAMILIES hole 3]
- r38, U, o1: untried on the board: the 38-step search is only charged as the allowance A_C = 2^70 (row F16). Logged: a new characteristic or a new dense part [MAP_r38 s.5]
- r39+, T lit 39-step SFS: published: SAT/SMT tools find 39-step semi-free-start characteristics (LLW23, about 3 h on 120 threads; LLW24), DERIVED [literature.tsv]; no 39-step collision route exists (row F06)

### F05 SFS / free-start as end product

- r31, r32, r33-36, r37, r38, r39+, n/a: rules exclude free-start and semi-free-start results (cost model v5, DERIVED [FAMILIES]); they serve only as validation witnesses inside row-F06 entries (r37 1c368173 and d3ec5c41, r38 the c99df2dc line); published SFS reach is 38 steps (MNS13) and 39 steps, practical (LLW23, LLW24)

### F06 two-block SFS-to-collision

- r31, T 31.61: best 31.61 (1347c47e, accepted), DERIVED; 50592e75 37.22 (promoted) [FAMILIES]; the LLWDS24 31-step two-block pair is about 2^40.5 (board-quoted, DERIVED [literature.tsv])
- r32, T 39.964: best 39.964 (58c83d12, accepted), DERIVED; 6eeefb64 46.57 (promoted) [FAMILIES]
- r33-36, T lit 35: 2^48.3: published: LLWS26 35-step collision, practical, 2^48.3 (board-quoted); LZLLQZ26 36-step pair found (DERIVED [literature.tsv])
- r37, T 61.71473, o1: best 61.71473 (d3ec5c41, the leader: the two-block attack of 2026/1120 with 222 classes of A0-variants), DERIVED; 7319bba9 62.34263. This design's floor is about 2^61.41 at 17 ops per good pair (COMPUTED [leader_cost_split]), so the leader sits about 0.3 bit above it. Logged: a memory-heavy variant of the 2026/1080 framework, memory being free (size unknown) [gaps_r37 G9]
- r38, T 72.64: best 72.64 (0ae69bcb, the leader: the c99df2dc construction, 78.12, with re-priced allowances), DERIVED; our rebuild gives 72.633442 and the attack without allowances is 2^72.06675 (COMPUTED [MAP_r38, levers_r38]); A0 line 91.5962 (2d1c4fc2), S line 99.91651 (deb673ae) [MAP_r38]; our derivative row 72.61489 is in row F18
- r39+, C 39 not reached: closed in the literature: LZLLQZ26 does not reach 39 steps on SHA-256 (its 38-step attack costs 2^104.3), and LLWS26 failed at 38 (DERIVED [literature.tsv])

### F07 truncated longer route

- r31, U: untried; closed board; r31 entries used the published 31-step characteristic (LLWDS24) [literature.tsv]
- r32, T 46.57: best 46.57 (6eeefb64, promoted): the CRYPTO 2026 (LLWS26) 35-step route cut to 32; also 23960a0e and 1e318d08, DERIVED [FAMILIES]
- r33-36, U: no board; the 35-step (LLWS26) and 36-step (LZLLQZ26) routes exist to cut [literature.tsv]
- r37, U, o1: untried. Logged: truncation has low value at 37/38 steps (GUESS [FAMILIES]); the only longer source route is the 38-step route of 2026/1120 (DERIVED [literature.tsv])
- r38, r39+, n/a: no source route: no published collision route is longer than 38 steps (LZLLQZ26 does not reach 39; the 39-step results are semi-free-start only), DERIVED [literature.tsv]

### F08 multi-target variants

- r31, T 31.61: best 31.61 (1347c47e: 483 starting points, 5.7M table tuples), DERIVED; 3651663d (448 own starting points; placed on r31 by the row order in FAMILIES) [FAMILIES]; closed board
- r32, T (no score): the ed55a9d7 line: valid-tuple tables of about 1.4e9 records; score not in our summaries [FAMILIES]
- r37, T 61.71473, C1, o2: best 61.71473 (d3ec5c41: 222 of 22,976 classes, 782,800 of 12,103,680 A0-variants), DERIVED [gaps_r37 G3]; also 1c368173 (12.1M variants), b947b377, 1f12a09a, 7319bba9 [FAMILIES]. Closed: late dense-part variants (free E bits of rows 9..13): 2 variants keep the rows, sum of |L*| 32 against 32 for S alone, ratio 1.000 (COMPUTED [late_variants_r37.log]). Logged: A1/A2 variants, joint (A0, A1) family 2^27.53 = 16.04x the A0 family (COMPUTED [gaps_r37 G3]) but a gain of at most about 0.14 bit, since it only amortises the per-first-block share (DERIVED [gaps_r37 G3]; FAMILIES hole 1 had left the size open, GUESS); fresh Step-1 solutions, success per first block x2 -> 61.11006 (DERIVED [ledger_levers])
- r38, T 72.64, C1, o1: best 72.64 (0ae69bcb: (A0, A1, A2) dense-part variants, 2^37.48 per chaining value), DERIVED; A0-only line 91.5962 (2d1c4fc2) [MAP_r38]. Closed: more A0 values only amortise the 8.35% first-block share, about 0.06 bit, and double the table preprocessing (DERIVED [MAP_r38 s.5]). Logged: G6 fresh Step-1 solutions (|L*| = 1 today against the paper's 2^2): |L*| = 4 gains about 0.26 bit online (GUESS [MAP_r38])

### F09 CV-indexed tables

- r31, T (no score) †: † 8080939c (record word and one-cell lookup) [FAMILIES]: its track (r31 or r32) is not in our summaries, so it is listed in both columns
- r32, T (no score) †: † 8080939c (record word and one-cell lookup) [FAMILIES]: track not stated, listed in both columns
- r37, T 61.71473, C2, o1: best 61.71473 (d3ec5c41: x-indexed W6 fibre table), DERIVED; 1c368173 c7 classes [FAMILIES]. Closed: r38's (Y, Z0) row-16 table does not transfer, 16 usable A1 values against 2^19.82 on r38 and W6/W7 depend on A1 (COMPUTED counts, DERIVED conclusion [gaps_r37 G3]); a table for the row-16 stage: u needs 7 CV words (the leader's statement, DERIVED [gaps_r37 G1]). Logged: G7 W6 cb-amortisation table, about 0.03 bit (GUESS [gaps_r37])
- r38, T 72.64, C3: best 72.64 (0ae69bcb: per-A0 row-16 (Y, Z0) tables, 2^64 buckets each), DERIVED; 2d1c4fc2 91.5962 uses r37's c7 classes on the A0 line [MAP_r38]. Closed (DERIVED [MAP_r38 s.5]): a W7 pre-filter in the tables needs x = A_-1 in the index, 2^96 buckets per A0; r37's c7 classes do not collapse in the DP line (c7 depends on A1); a row-17+ index needs W2 (five CV words). FAMILIES hole 4 priced halving the per-(CV, A0) work at 72.121 (COMPUTED from a GUESS factor); MAP_r38 rates r37's x-precomputation low on r38

### F10 condition relaxation

- r31, T 31.61: best 31.61 (1347c47e), DERIVED; relaxed W20 also in fe63aaad and 50592e75 (37.22) [FAMILIES]
- r32, T 39.964: best 39.964 (58c83d12: x1.181 at stage 16), DERIVED; 3873e7f5 x1.2983; ed55a9d7 46 -> 44 conditions [FAMILIES]
- r37, T 61.71473, o2: partial use: the exact Step-2 sets F6/F7 (6c77089c lineage) are in the leader d3ec5c41, 61.71473, DERIVED [FAMILIES]; the 74 Step-3 conditions (rows 16..36) were never relaxed. Logged: Step-3 relaxation, q3 x1.3 -> 61.4625, x2 -> 61.0987, x4 -> 60.6520 (COMPUTED from GUESS gain factors [leader_cost_split]); G5c q3 as the collision event, at most about 0.2 bit (GUESS [gaps_r37])
- r38, T 72.64, o1: partial use: the exact F7 set (20a43626 / 3d819a4b) is reused by the 0ae69bcb line, 72.64, DERIVED [MAP_r38]; the about 101 Step-3 conditions were never relaxed. Logged: Step-3 relaxation, q3 x2 -> 72.064, x4 -> 71.665 (COMPUTED from GUESS factors [leader_cost_split])

### F11 early abort / staged filters

- r31, T (no score) †: † c712ea19 and f807117b [FAMILIES]: their tracks (r31 or r32) are not in our summaries, so they are listed in both columns
- r32, T 39.964: best 39.964 (58c83d12), DERIVED [FAMILIES]; † c712ea19 and f807117b (track not stated)
- r37, T 61.71473: best 61.71473 (d3ec5c41: staged filters; it replaced the decision DAG of 7319bba9, 62.34263, by tables), DERIVED [FAMILIES]
- r38, T 72.64, o2: best 72.64 (0ae69bcb: a staged filter cascade with caps, bucket entry, W7 bitmap, 10-bit row-17 mask, deep path; the classification is ours, DERIVED from MAP_r38 s.2). Logged: G4(c) unrolled entry loop with one branch per bucket, 56.69 -> 35 ops, 0.169 bit (GUESS op counts [levers_r38]); r37's decision DAG (7319bba9) on the A0-block stage, part of G4(b) [MAP_r38 s.5-6]

### F12 bit-slicing / SWAR

- r31, T (no score) †: † f310d44f (7 x 36-bit lanes, the origin), 028aa8d0, 035a5381, 6e5214dd [FAMILIES]: tracks (r31 or r32) not in our summaries, so they are listed in both columns
- r32, T (no score) †: † f310d44f, 028aa8d0, 035a5381, 6e5214dd [FAMILIES]: track not stated, listed in both columns
- r37, T (no score), o3: used, scores not in our summaries: ad9745bf (first blocks bit-sliced at 172.4 ops per trial), efd8aa9d, 1c368173 (bit-sliced W6 filter) [FAMILIES]; the leader charges one full unit per first block. Logged: G2 bit-sliced first blocks in the A0-variant line, 61.584..61.588, about 0.13 bit (DERIVED [ledger_levers]); G1 7-lane 36-bit SWAR for u, about 0.08 bit (GUESS); bit-slicing u over gathered pairs looks worse, about 20 ops per lane against 16.9 (GUESS [gaps_r37 G1])
- r38, T 99.91651, o4: best 99.91651 (deb673ae: solved first-block family, 171.5 ops per trial), DERIVED; a82eeb40 256-lane evaluator at 195.5 ops per trial, d5a10596 [MAP_r38]; the DP online program (72.64) has no SWAR or bit-slicing. Logged (GUESS op counts, exact arithmetic [levers_r38]): G4(a) first block 2728 -> 400 ops, 0.069 bit; G4(b) A0 blocks 30 -> 15 ops, 0.115; G4(d) row-17 path 25.41 -> 15, 0.079; with G4(c) the conservative total is 72.11254; G8 deb673ae's first-block family feeding the DP tables

### F13 neutral bits / boomerangs

- r31, C failed build †: † 43641180: a neutral-bit table in a failed starting-point build [FAMILIES]; its track (r31 or r32) is not in our summaries, so it is listed in both columns
- r32, C failed build †: † 43641180 (a failed starting-point build with a neutral-bit table): track not stated, listed in both columns
- r37, U, o1: untried on any SHA-256 board. Logged (GUESS-level [FAMILIES hole 7]): neutral bits or boomerang paths that satisfy part of rows 16..22 deterministically; the A0/A1/A2 variants are a cousin limited to rows up to 15
- r38, U, o1: untried: the DP line uses no neutral bits, its free words are the modification [MAP_r38]. Logged: as on r37 (GUESS-level [FAMILIES hole 7])

### F14 multi-block near-collision

- r31, U: untried (notes that mention 3 blocks mean padding) [FAMILIES]
- r32, U: untried (notes that mention 3 blocks mean padding) [FAMILIES]
- r37, U, o1: untried. Logged: multi-block near-collision chaining (a nonzero CV difference cancelled by a later block), likely dearer than row F06 at 37/38 steps (GUESS [FAMILIES])
- r38, U, o1: untried. Logged: as on r37 (GUESS [FAMILIES])

### F15 GPU brute force

- r31, U: untried: several r31 notes say there was no GPU run [FAMILIES]
- r32, U: untried: no GPU run is recorded in our summaries
- r37, C 261.5 days, o2: a GPU buys wall-clock only (work is summed over processors), so it cannot lower the v5 scalar by itself [FAMILIES]. Closed: running the attack for a real pair, 2^58.32 first blocks, is about 261.5 days on one 3090 (COMPUTED from a GUESS 2^33.1 SHA-256/s [leader_cost_split]). Logged: exhaustive table statistics that remove premise H9 (x1.02 margin; 0 to 0.04 bit [gaps_r37 G6]), about 2^51 simple ops, about 128 s at a GUESS 2^44 ops/s; large q3 studies (evidence only) [FAMILIES hole 8]
- r38, U, o1: untried as a run: GPUs appear only as an A_C accounting ceiling (2f30479f: 10^4 GPUs for 10 years = 2^73.3, A_C 2^76) [MAP_r38]. Logged: large q3 studies (evidence only) [FAMILIES hole 8]

### F16 advice / allowance accounting

- r31, T 37.22: best 37.22 (50592e75, promoted): the published characteristic accepted as public text, A_C = 0, DERIVED [FAMILIES]; † 621d0fb0 passed the same way (track not stated, listed in both columns)
- r32, T 46.57: best 46.57 (6eeefb64, promoted): a measured re-run accepted, DERIVED [FAMILIES]; † 621d0fb0 (public text, track not stated)
- r37, T 61.71473, C2, o1: best 61.71473 (d3ec5c41: A_C 2^60, A_S 2^50, DEV 2^40; A_C is 30.5% of the total, COMPUTED [leader_cost_split]), DERIVED. Closed: 76407c7c (not evaluable on A_C) and 871bfee5 (failed on H4) [gaps_r37 G4]. Logged: a measured 37-step re-run replacing A_C: A_C removed -> 61.19051, A_C 2^56 -> 61.22949 (DERIVED [ledger_levers]); out of reach on 2 CPU processes (GUESS: days to weeks; the 35-step re-run took 593,858 CPU-s) [gaps_r37 G4]
- r38, T 72.64, C2, o2: best 72.64 (0ae69bcb: A_C 2^70 from a CPU ceiling, A_S 2^70, DEV 2^64), DERIVED; 2f30479f 76.12 (A_C 2^76), 7914208c 78.03 [MAP_r38]. Closed: 8bc7d6c5 70.23909 (A_C 2^64 as a bare claim) and fd3ac033 72.45 (A_C 2^68 anchored on the 35-step re-run), both not evaluable [MAP_r38]. Logged: G2 A_S 2^50 at the r37 convention -> 72.37992 (COMPUTED, low risk); G3 r37's allowances (2^60 / 2^50 / 2^40) or a measured A_C -> 72.06709 (COMPUTED; r38 refused 2^64 and 2^68) [levers_r38, MAP_r38]

### F17 stored-pair replay

- r31, T 31.61: best 31.61 (1347c47e: a real pair built at 2^26.7 online trials), DERIVED; 50592e75 37.22 [FAMILIES]
- r32, T (no score): retained-pair entries 8f955606 and e5312a9b; scores not in our summaries [FAMILIES]
- r33-36, U: no board; published real pairs exist at 35 (LLWS26) and 36 steps (LZLLQZ26), DERIVED [literature.tsv]
- r37, r38, r39+, n/a: needs a real collision pair at this depth and none exists (37: no published pair; 38: 2^104.3 in LZLLQZ26; 39: not reached), DERIVED [literature.tsv]; a 37-step pair at today's design is 2^58.32 first blocks, about 261.5 days on one 3090 (COMPUTED from a GUESS rate [leader_cost_split])

### F18 ledger engineering

- r31, U: not recorded for r31 in our summaries (the jungjipdo and Meganpark980320 ledger lines are cited from r32 notes) [FAMILIES]
- r32, T (no score): the jungjipdo and Meganpark980320 lines: ledger steps worth about 0.01-0.1 bit each (DERIVED from r32 notes [FAMILIES]); scores not in our summaries
- r37, T 61.71473, o1: best 61.71473 (d3ec5c41), DERIVED; 087a18c4 exact-rational ledger with q3 at the printed 99% bound (H6) and the exact success floor (H7); 7319bba9 [FAMILIES, MAP_r38 s.6]. Logged: a Bernstein cap, about 0.013 bit [gaps_r37 G6]
- r38, T 72.61489 ours, C2, o3: ours: 72.61489 = the leader construction with the 2% N_G pad removed (D35, unfiled; COMPUTED [MAP_r38 G5]); 20dbd783 (S line) uses the exact success floor H7 [MAP_r38]. Closed: 426af47b 72.63, claim rounded below the exact ledger 72.633442, failed (cause GUESS); 3b532546 78.11, a participant-measured pair delta 0.0079 rejected [MAP_r38]. Logged: G1 revert the two voluntary margins (q3_model 2^-101.01, structural pair delta 0.002931) -> 71.66909 (COMPUTED, premise risk), with G2 and no pad 71.11112 (COMPUTED); G5 N1 cap 4x -> 1.25x -> 72.60991 (DERIVED); G7 an organizer-executed H5 test would back G1 (GUESS runtime fit) [levers_r38, MAP_r38]

### F19 other 37-step characteristics

- r37, U, o2: untried: no r37 entry cites ZLGW26 (2026/232); the LLWS26 (2026/1080) 37-step attack is theoretical [FAMILIES, literature.tsv]. Logged: each is a distinct filed line for the coop count; complexities unknown (paper bodies unreadable here) [FAMILIES hole 5]
- r31, r32, r33-36, n/a: not applicable: this row is the unused published 37-step characteristics; a use at fewer steps is truncation (row F07)
- r38, r39+, n/a: no source: 2026/232 has no 38-step row (per r38 note 8b2ebe50) and LLWS26 failed at 38 steps, DERIVED [FAMILIES, literature.tsv]

### F20 whole-problem SAT

- r31, U: untried as whole-problem SAT: SAT (z3, STP + CryptoMiniSat) only built starting points (1347c47e) [FAMILIES]
- r32, U: untried as whole-problem SAT: SAT only built starting points (the jungjipdo line, track not stated) [FAMILIES]
- r37, U, o1: untried: SAT runs only inside the allowances [FAMILIES]. Logged: whole-collision SAT, unlikely at 37/38 (GUESS [FAMILIES hole 7])
- r38, U, o1: untried. Logged: as on r37 (GUESS); the literature has a 38-step semi-free-start by SAT plus computer algebra (ANB24, GUESS; not a collision) [literature.tsv]

## What this grid could not settle

- Closed-board tracks: 6d554419, 8bad82c1, 1ded36a8, 8080939c, c712ea19, f807117b, f310d44f, 028aa8d0, 035a5381,
  6e5214dd, 43641180 and 621d0fb0 are listed for r31/r32 without a track (†), and many closed-board scores are
  missing. Settling them needs the board files, which this brief excluded.
- 8bad82c1 / 1ded36a8 (measured route search) have no status in our summaries, so they appear only in the F04 notes,
  not in any cell's records.
- r33-36: no run of ours at these depths appears in the files read; the column holds published results and the
  measured 35-step run quoted from 6eeefb64.
- The 37-step complexities inside 2026/1120 and 2026/232 are unknown here (FAMILIES: the ePrint PDF bodies returned
  HTTP 403).
- Classifications that are mine (DERIVED): F11 counts the staged filter cascades of d3ec5c41 and 0ae69bcb as tried;
  F10 counts the exact Step-2 sets on r37/r38 as a partial use; F18 on r31 is untried only because nothing is
  recorded; 3651663d is placed on r31 by the row order in FAMILIES.
- F08 A1/A2 on r37: gaps_r37 G3 bounds the gain at about 0.14 bit (DERIVED, on COMPUTED counts), while FAMILIES hole 1
  had left the size open (GUESS: 0 to several bits). The grid uses G3.
- F09 on r38: FAMILIES hole 4 priced a halving of the per-(CV, A0) work at 72.121 (COMPUTED from a GUESS factor);
  MAP_r38 s.5 rules out the W7 pre-filter form (2^96 buckets per A0) and rates the x-precomputation low. The grid
  follows MAP_r38 and marks that lever closed.
- Our own SHA-256 items outside this grid's sources: the Sol panel of make_endgame.py (seen about 12:48 on
  2026-10-10 while adding this grid; not checked, numbers as listed there) shows D71 (r37 freedom, J/V1 joint
  enumeration pending; bears on F08 r37), D72 (r38 72.60993, PROVED cap-only under H1/H2/H5; bears on the F18 r38 N1
  cap idea), D75 (r38 72.61489, conditional on an audited A_C; MAP_r38 G5 gives the same number for the 2% pad
  removal, D35, and the two descriptions are not reconciled here) and D76 (r37 61.67456*, H9, conditional; bears on
  the F15 r37 H9 idea). The grid's marks do not include them.
- Nothing was run for this grid; every size is its source's number with its source's label.
