# SHA-256 reduced-step collision: technique families vs. the boards

Built 2026-10-10 11:45 -06:00 (map-lit agent). Research only: nothing staged or filed, no yukon commands, no
experiments run, no GPU lock taken. Participants' text is not copied here; entries are cited by submission id.

**Labels.** COMPUTED = produced in this session by `tools/*.py` (board extraction, keyword scan, ledger
arithmetic; output in `leader_cost_split.txt`). DERIVED = read from a cited source (ePrint abstract fetched
today, the organizer rules in `research/sha3r6/rules/live/`, or a public board note cited by id). GUESS = my
estimate or recollection, not checked today.

**Target fit (DERIVED, FRONTIER_LANES.md / cost model v5).** Ordinary collision of complete padded messages,
standard IV, first r steps in every compression, full 256-bit digest. Free-start, compression-only, truncated
and quantum results do not count. Score = log2(total charged work) in target compressions; other word
operations cost 1/C (C = 2644 for r37, 2728 for r38); preprocessing, failed trials and advice are charged;
memory is reported but free; success >= 0.39; work is summed over all processors (a GPU buys wall-clock only).

**Sources read.** ePrint abstracts for 2015/350, 2014/302, 2016/374, 2023/285, 2024/349, 2026/232, 2026/1080,
2026/1120, 2021/886 (PDF bodies return HTTP 403 to the fetch tool, so paper-internal numbers come from board
notes). Board data: r31/r32 closed boards (135 + 97 entries) and the 11:25 live r37/r38 boards (34 + 43
entries), all COMPUTED-extracted; top 8 notes of r31 and r32 read in full; r37 d3ec5c41 and 1c368173, r38
0ae69bcb read in full; c99df2dc and other r37/r38 notes read by keyword snippets only.

## 1. Family table

Status key: **core** = carries the board leaders; **used** = filed by someone; **partial** = used on some
tracks or only in a weak form; **GAP** = no entry on the named track uses it.

| # | Family | Best known SHA-256 result | Fits fixed-IV target? | r31 / r32 (closed) | r37 / r38 (live) | Status |
|---|---|---|---|---|---|---|
| F01 | Generic birthday (sort / hash table / distinguished points, van Oorschot-Wiener) | any step count at about 2^128 (DERIVED: organizer nominal 128) | yes | best 125.94 d02732c7; 124.6 5c3f233e | best 123.93722 5951ba00; 123.96717 668d3f56 | used, saturated, 60+ bits behind |
| F02 | Grouped partial evaluation / round-skip key, bit-sliced birthday (accounting below 128) | same | yes | d02732c7, 35ce0758; 68ca8e4f, 6b88bdb7 | 5951ba00, 64bca7e2, 6de1b685; 668d3f56, c65868c3 | used, saturated |
| F03 | Single-block local collision + message modification (NB08, IMPR08, SS08, MNS11, MNS13) | 28-step collision, practical (DERIVED, MNS13) | yes, but stops at 28 steps | none (tracks start at 31) | none | not applicable |
| F04 | Automated characteristic search: guess-and-determine (MNS11/13, EMS14, DEM15) and SAT/SMT/MILP (LLW23/24, ZLGW26, LLWS26, LZLLQZ26) | characteristics for a 38-step collision at 2^104.3 and practical 39-step SFS (DERIVED) | tool only; its output feeds F06 | 6d554419 own in-chain SAT search (failed: refuted); 8bad82c1 / 1ded36a8 measured route search; 6eeefb64 measured re-run, promoted 46.57 | none run; the search is charged only as an allowance A_C | **GAP on r37/r38** |
| F05 | Semi-free-start / free-start collision as the end product | 39-step SFS practical (DERIVED, LLW23/LLW24); 38-step SFS (MNS13) | **no** (rules exclude) | not scored | used only as validation witnesses (a0-sfs-r37 in 1c368173 and d3ec5c41; SFS witnesses in c99df2dc) | building block only |
| F06 | Two-block SFS-to-collision conversion (same first block; Step 1 dense part, Step 2 chaining-value filter, Step 3 uncontrolled part; memory-efficient MITM of LLWS26) | 36-step pair found; 37 steps theoretical (ZLGW26, LLWS26, LZLLQZ26); 38 steps 2^104.3 (DERIVED) | **yes** | every competitive entry: 1347c47e 31.61 (accepted), 50592e75 37.22 (promoted); 58c83d12 39.964 (accepted), 6eeefb64 46.57 (promoted) | d3ec5c41 61.71473; 0ae69bcb 72.64 | core |
| F07 | Truncating a longer published route to the track's step count | inherits the source route | yes | r32: the CRYPTO 2026 35-step route cut to 32 (6eeefb64, 23960a0e, 1e318d08) | none | used on r32 only; low value at 37/38 (GUESS) |
| F08 | Multi-target second blocks: many Step-1 / dense-part solutions per chaining value, first block matched against all of them | board-level only | yes | 3651663d (448 own starting points), 1347c47e (483 starting points, 5.7M table tuples), r32 valid-tuple tables of about 1.4e9 records (ed55a9d7 line) | r37: A0-variants only (1c368173: 12.1M variants; b947b377; 222 classes in 1f12a09a, 7319bba9, d3ec5c41). r38: (A0, A1, A2) variants, about 2^37.48 per chaining value (c99df2dc, 0ae69bcb) | core; **GAP: no r37 entry varies A1/A2** (COMPUTED keyword scan) |
| F09 | Chaining-value-indexed precomputed tables (amortize over the 2^32 values of one CV word; table matching between first-block outputs and variant requirements) | board-level only | yes | 8080939c record word and one-cell lookup | r37: c7 classes (1c368173), x-indexed W6 fibre table (d3ec5c41). r38: per-A0 row-16 tables (c99df2dc) | used; **GAP: the two tracks' table tricks are not cross-ported** |
| F10 | Condition relaxation: test the necessary condition instead of the characteristic's sufficient one; exact filter sets; measured differential effect | board gains on r32: x1.2983 (3873e7f5), x1.181 stage 16 (58c83d12), 46 to 44 conditions (ed55a9d7) (DERIVED) | yes | r31 relaxed W20 (fe63aaad, 50592e75, 1347c47e); r32 as listed | exact Step-2 sets F6/F7 from the 6c77089c lineage; **no relaxation of the Step-3 conditions** (rows 16..36; 74 conditions on r37, about 101 on r38) | **GAP on r37/r38 Step 3** |
| F11 | Early-abort ordering, staged filters, decision DAGs | implementation | yes | c712ea19, f807117b, 58c83d12 | 7319bba9 (decision DAG), superseded by tables in d3ec5c41 | used |
| F12 | Bit-sliced / SWAR batch evaluation (several trials per 256-bit word) | implementation | yes | f310d44f (7 x 36-bit lanes, origin), 028aa8d0, 035a5381, 6e5214dd | r37 first blocks bit-sliced at 172.4 ops/trial (ad9745bf), W6 filter bit-sliced (1c368173); r38 256-lane evaluator (a82eeb40, d5a10596) | used; **small GAP: the r37 A0-variant line charges 1 full unit per first block** |
| F13 | Neutral bits / probabilistic neutral bits / tunnels / boomerangs (auxiliary differentials) | full SHA-1 and MD5 collisions (GUESS); none in the SHA-256 abstracts read | yes (inside the second block) | only a neutral-bit table in a failed starting-point build (43641180) | none; the A0/A1/A2 variants are a cousin limited to rows up to 15 | **GAP everywhere** |
| F14 | Multi-block near-collision chaining (nonzero chaining-value difference cancelled by a later block, Wang style) | no SHA-256 result known (GUESS) | yes in principle | none ("3-block" mentions are padding) | none | **GAP**; likely dearer than F06 at 37/38 steps (GUESS) |
| F15 | GPU / hardware brute force on the free part (first-block trials, birthday) | 128-bit 3-XOR on full SHA-256, about 8.7e22 operations (DERIVED, BBDN21) | resource, not a technique | no GPU run (several r31 notes say so) | none; a GPU throughput ceiling appears only as an accounting bound for A_C (0ae69bcb) | **GAP**, but it cannot lower the v5 scalar |
| F16 | Advice / allowance accounting for characteristic and Step-1 searches (A_C, A_S, DEV; published characteristic as public text; measured re-run) | rules-level | rules-level | public text accepted: 50592e75 (promoted), 621d0fb0; measured re-run accepted: 6eeefb64 | r37 A_C 2^60, A_S 2^50, DEV 2^40 (1c368173 onward; 76407c7c was not evaluable on A_C). r38 A_C, A_S 2^70, DEV 2^64 (0ae69bcb); 8bc7d6c5 (A_C 2^64) and fd3ac033 (measurement-anchored 2^68) not evaluable | used; **GAP: no measured re-run of the 37/38-step searches** |
| F17 | Replay of a stored, self-built collision with the whole construction chain charged | r31: real pair built at 2^26.7 online trials (DERIVED, 1347c47e) | yes | 1347c47e 31.61, 50592e75 37.22; r32 retained-pair entries (8f955606, e5312a9b) | impossible until a real 37/38-step pair exists | closed-board family |
| F18 | Ledger engineering: 64-register machine, packed pricing, exact rationals, success-floor bounds (Bernstein, Chebyshev, Bonferroni), cap/T optimization | each step worth about 0.01-0.1 bit (DERIVED from r32 notes) | yes | jungjipdo and Meganpark980320 lines | 087a18c4 exact-rational ledger, 7319bba9, d3ec5c41 | used |
| F19 | Other published 37-step characteristics: ZLGW26 (2026/232) and LLWS26 (2026/1080, theoretical 37) | 37 steps (DERIVED) | yes | n/a | **no r37 entry cites 2026/232** (it appears only in r38 8b2ebe50, which notes it has no 38-step row) | **GAP: new attack lines** |
| F20 | Whole-problem SAT / algebraic solving (SAT + computer algebra) | 38-step SFS (GUESS, ANB24) | yes in principle | SAT only for starting points (z3 and STP+CryptoMiniSat in the jungjipdo line and 1347c47e) | SAT only inside the allowances | unlikely at 37/38 (GUESS) |

## 2. Anatomy of the live leaders (inputs DERIVED from notes; arithmetic COMPUTED, see `leader_cost_split.txt`)

**r37, d3ec5c41 at 61.71473.** The two-block attack of 2026/1120 with 222 classes of A0-variants. N_FB =
2^58.316 first blocks at about 7.33 units each (online about 2^61.19), plus A_C 2^60, A_S 2^50, DEV 2^40.
- A_C is **30.5%** of the total (COMPUTED).
- Step 3 needs about 2^73.0 candidates (q3 = 2^-74.03, success floor mu = 0.4947), so about 2^68.0 good pairs at
  32 candidates each and about 2^14.7 candidates per first block (COMPUTED).
- The packed row-16 stage costs about 17 operations per good pair, roughly 14,000 of the 16,431 data-dependent
  operations per first block (DERIVED). This design's floor is therefore about 2^60.73 online, or **2^61.41** with
  A_C at 2^60 (COMPUTED): the leader sits about 0.3 bit above its own floor.

**r38, 0ae69bcb at 72.64.** The construction is qkniep's c99df2dc. Dense-part variants over (A0, A1, A2) give
about 2^37.48 per chaining value, with per-A0 row-16 tables. N_G = 2^68.43 first blocks at 1 + 256 x 117 / 2728 =
11.98 units each, so online is 2^72.016 (COMPUTED; matches the note). Allowances are 2^71.01, table construction
2^67.21, and q3_model = 2^-102 against a measured bound near 2^-101.

## 3. Holes, ranked (each with the check that would settle it)

1. **(A1, A2) dense-part freedom on r37, with r38-style per-A0 row-16 tables.**
   - No r37 entry varies A1 or A2 (COMPUTED scan). 1c368173 itself names this as an open step.
   - On r38 the same idea cut the first-block count by about 2^35.5 against a single Step-1 solution (DERIVED, c99df2dc).
   - It attacks the very term that holds r37 at its 2^61.41 floor: per-good-pair work.
   - Size: unknown (GUESS: from nothing up to several bits). Two things could stop it: the 37-step characteristic may
     pin A1 and A2 more tightly than the 38-step one, and r38's table build costs 2^67.2 units, a warning on cost.
   - Check: an exact count of valid (A1, A2) per A0 for the r37 characteristic (rows -4..15 hold; W8..W13
     differences kept), then a cost model that includes table preprocessing. A sibling folder
     `sha256grid/map-r37/freedom` already exists; I did not read it.
2. **Step-3 necessary-condition relaxation on r37 and r38** (unused there; it worked on r31 and r32).
   - r37: q3 x1.3 gives 61.46, x2 gives 61.10, x4 gives 60.65 (COMPUTED from GUESS gain factors).
   - r38: x2 gives 72.06, x4 gives 71.67 (COMPUTED).
   - Check: for each Step-3 stage, compare a Monte-Carlo pass rate under the weakest condition that still gives
     equal states after the last difference-carrying step with the characteristic's rate. The r32 method is in
     3873e7f5 and 58c83d12.
3. **A measured re-run of the characteristic and Step-1 searches, replacing A_C and A_S.**
   - r37: A_C at 2^46 alone gives 61.19 (-0.52 bit). r38: A_C and A_S at 2^50 give 72.07 (-0.56 bit). Both COMPUTED.
   - The r38 judges rejected a measurement anchored on a different search (fd3ac033). The 6eeefb64 precedent was
     an actual re-run of the same tool on the same route.
   - The tool is CPU SAT (kissat / CryptoMiniSat), so a GPU does not help.
   - Our own characteristic with a measured search would be a new path as well (F04 + F19).
4. **Cross-port the table tricks between the tracks.**
   - Moving r37's x-indexed amortization onto r38's per-(CV, A0) loop: halving that work gives 72.12 with today's
     allowances, or 71.23 with the allowances at 2^50; quartering it gives 70.51 with low allowances (COMPUTED from
     GUESS factors).
5. **Unused published 37-step paths** (2026/232; LLWS26 37-step).
   - Each is a distinct filed line for the coop count. Complexity is unknown (paper body unreadable here).
   - Check: fetch the PDF through an allowed route, or ask the owner.
6. **Bit-sliced first-block pricing on the r37 A0-variant line.**
   - 0.08 to 0.15 units per first block instead of 1 gives -0.12 to -0.13 bit (COMPUTED).
   - Earlier r37 entries that priced first blocks this way passed review (ad9745bf, efd8aa9d). One r31 advisory
     warned against pricing a full target compression below one unit.
7. **Fringe, never tried on any SHA-256 board:**
   - neutral bits or boomerang (auxiliary) paths that satisfy part of rows 16..22 deterministically;
   - multi-block near-collision chaining;
   - whole-collision SAT.
   - All are GUESS-level; the first has the clearest mechanism.
8. **GPU work that strengthens evidence without moving the scalar:**
   - exhaustive table statistics (removes d3ec5c41's sampling premise H9; about 2^51 simple operations, roughly
     128 s at a GUESSED 2^44 ops/s);
   - large q3 studies.
   - A real 37-step pair is out of reach at today's design: 2^58.3 first blocks would take about 261 days on one
     3090 (COMPUTED from a GUESSED 2^33.1 full SHA-256/s).

## 4. Convention gap to record (not a technique)

The closed boards accepted "the published characteristic is public algorithm text" with A_C = 0 (50592e75
promoted, 621d0fb0 passed). The live r37/r38 judges instead demanded evidence for A_C (76407c7c and 8bc7d6c5 were
not evaluable). This is a candidate for the organizer-notes batch; it is the owner's call.

## 5. What I could not check

- ePrint PDF bodies return HTTP 403 to the fetch tool. I did not try to work around this. As a result, the
  37-step complexities inside 2026/1120 and 2026/232 are unknown here.
- ASIACRYPT 2024 (LLWDS24) and MNS11 are not on ePrint; their numbers are board-quoted or from memory.
- Keyword tags in `entry_family_tags.tsv` are noisy: a tag means the words appear in a note, not that the
  technique is central.
- I read r37/r38 notes only for the leaders. No experiment, solver or GPU job was run.
