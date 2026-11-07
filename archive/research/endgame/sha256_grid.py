# SHA-256 tried/untried grid: technique family (rows F01-F20) x step depth (columns), same cell format as
# sha3_cells.csv. Writes research/sha256grid/sha256_cells.csv; make_endgame.py draws it after the SHA3-256 grids.
# Run: python -B sha256_grid.py        writes the CSV
#      python -B sha256_grid.py --md   also rewrites research/sha256grid/GRID.md from the same records
# Sources (our own summaries under research/sha256grid/, read only): map-lit/FAMILIES.md (the 20 families),
#   map-lit/literature.tsv, map-lit/leader_cost_split.txt, map-r37/gaps_r37.tsv, map-r37/ledger_levers.out.txt,
#   map-r38/MAP_r38.md, map-r38/levers_r38.out.txt, holes/late_variants_r37.log.
import csv, os, sys
from datetime import datetime

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(os.path.dirname(HERE), 'sha256grid')
if '--outdir' in sys.argv:  # test runs only
    OUTDIR = sys.argv[sys.argv.index('--outdir') + 1]
GRID = 'SHA-256 familyxdepth'  # make_endgame.py splits at the first 'x': row axis 'SHA-256 family', column axis 'depth'

FAM = [('F01', 'generic birthday'), ('F02', 'grouped / round-skip birthday'), ('F03', 'single-block local collision'),
       ('F04', 'characteristic search'), ('F05', 'SFS / free-start as end product'), ('F06', 'two-block SFS-to-collision'),
       ('F07', 'truncated longer route'), ('F08', 'multi-target variants'), ('F09', 'CV-indexed tables'),
       ('F10', 'condition relaxation'), ('F11', 'early abort / staged filters'), ('F12', 'bit-slicing / SWAR'),
       ('F13', 'neutral bits / boomerangs'), ('F14', 'multi-block near-collision'), ('F15', 'GPU brute force'),
       ('F16', 'advice / allowance accounting'), ('F17', 'stored-pair replay'), ('F18', 'ledger engineering'),
       ('F19', 'other 37-step characteristics'), ('F20', 'whole-problem SAT')]
DEPTH = ['r31', 'r32', 'r33-36', 'r37', 'r38', 'r39+']
HEADS = {'r31': 'r31 closed', 'r32': 'r32 closed', 'r33-36': 'r33-36 no board', 'r37': 'r37 live', 'r38': 'r38 live',
         'r39+': 'r39+ no board'}

# id  family  depth  status (alive / dead / open). Ids: an 8-hex board entry (another team's unless marked ours:),
# lit: a published result, ours: our own work, idea: logged but not tried. 'track-r31-or-r32': the closed-board
# track is not in our summaries, so the record sits in both closed columns.
REC = """
d02732c7:125.94 F01 r31 alive
5c3f233e:124.6 F01 r32 alive
5951ba00:123.93722 F01 r37 alive
rho/vOW-variants:irrelevant-at-124-vs-61.7 F01 r37 dead
668d3f56:123.96717 F01 r38 alive
generic-family-exhausted:floor-about-123.9 F01 r38 dead
d02732c7:125.94 F02 r31 alive
35ce0758 F02 r31 alive
68ca8e4f F02 r32 alive
6b88bdb7 F02 r32 alive
5951ba00:123.93722 F02 r37 alive
64bca7e2 F02 r37 alive
6de1b685 F02 r37 alive
668d3f56:123.96717 F02 r38 alive
c65868c3 F02 r38 alive
6d554419:own-SAT-search-refuted(track-r31-or-r32) F04 r31 dead
6d554419:own-SAT-search-refuted(track-r31-or-r32) F04 r32 dead
6eeefb64:46.57(measured-search-re-run) F04 r32 alive
6eeefb64:35-step-search-re-run(593858-CPU-s) F04 r33-36 alive
idea:G5b-re-optimised-characteristic(GUESS-multi-bit) F04 r37 open
idea:new-characteristic-or-dense-part F04 r38 open
lit:39-step-SFS-characteristics(LLW23,LLW24) F04 r39+ alive
1347c47e:31.61(accepted) F06 r31 alive
50592e75:37.22(promoted) F06 r31 alive
58c83d12:39.964(accepted) F06 r32 alive
6eeefb64:46.57(promoted) F06 r32 alive
lit:LLWS26-35-step-2^48.3 F06 r33-36 alive
lit:LZLLQZ26-36-step-pair F06 r33-36 alive
d3ec5c41:61.71473(leader) F06 r37 alive
7319bba9:62.34263 F06 r37 alive
idea:memory-heavy-2026/1080-variant(G9) F06 r37 open
0ae69bcb:72.64(leader) F06 r38 alive
c99df2dc:78.12(base) F06 r38 alive
2d1c4fc2:91.5962(A0-line) F06 r38 alive
deb673ae:99.91651(S-line) F06 r38 alive
lit:LZLLQZ26-39-steps-not-reached F06 r39+ dead
6eeefb64:46.57(35-step-route-cut-to-32) F07 r32 alive
23960a0e F07 r32 alive
1e318d08 F07 r32 alive
idea:38-step-2026/1120-route-cut-to-37(low-value-GUESS) F07 r37 open
1347c47e:31.61(483-starting-points) F08 r31 alive
3651663d(448-starting-points) F08 r31 alive
ed55a9d7-line(1.4e9-record-tables) F08 r32 alive
d3ec5c41:61.71473(222-A0-classes) F08 r37 alive
1c368173(12.1M-A0-variants) F08 r37 alive
b947b377 F08 r37 alive
1f12a09a F08 r37 alive
7319bba9:62.34263 F08 r37 alive
ours:late-dense-part-variants(rows-9..13):ratio-1.000 F08 r37 dead
idea:A1/A2-variants(16.04x-family;gain-at-most-about-0.14-bit) F08 r37 open
idea:fresh-Step-1-solutions(x2->61.11006) F08 r37 open
0ae69bcb:72.64(A0/A1/A2-variants-2^37.48-per-CV) F08 r38 alive
2d1c4fc2:91.5962(A0-variants) F08 r38 alive
more-A0-values:gain-about-0.06-bit;2x-preprocessing F08 r38 dead
idea:G6-fresh-Step-1(L*=4:gain-about-0.26-bit-GUESS) F08 r38 open
8080939c(record-word-lookup;track-r31-or-r32) F09 r31 alive
8080939c(record-word-lookup;track-r31-or-r32) F09 r32 alive
1c368173(c7-classes) F09 r37 alive
d3ec5c41:61.71473(x-indexed-W6-fibre-table) F09 r37 alive
r38-(Y,Z0)-table:16-A1-values-vs-2^19.82 F09 r37 dead
row-16-u-table:u-needs-7-CV-words F09 r37 dead
idea:G7-W6-cb-table(gain-about-0.03-bit-GUESS) F09 r37 open
0ae69bcb:72.64(per-A0-(Y,Z0)-tables) F09 r38 alive
2d1c4fc2:91.5962(c7-classes) F09 r38 alive
x-indexed-W7-prefilter:2^96-buckets-per-A0 F09 r38 dead
c7-classes-in-DP-line:do-not-collapse F09 r38 dead
row-17+-table-index:needs-W2(5-CV-words) F09 r38 dead
1347c47e:31.61(relaxed-W20) F10 r31 alive
50592e75:37.22(relaxed-W20) F10 r31 alive
fe63aaad(relaxed-W20) F10 r31 alive
58c83d12:39.964(x1.181-stage-16) F10 r32 alive
3873e7f5(x1.2983) F10 r32 alive
ed55a9d7(46->44-conditions) F10 r32 alive
d3ec5c41:61.71473(exact-Step-2-sets-F6/F7) F10 r37 alive
idea:Step-3-relaxation(74-conditions;q3-x2->61.0987) F10 r37 open
idea:G5c-q3-as-collision-event(gain-at-most-0.2-bit-GUESS) F10 r37 open
0ae69bcb:72.64(exact-F7-set) F10 r38 alive
idea:Step-3-relaxation(about-101-conditions;q3-x2->72.064) F10 r38 open
c712ea19(track-r31-or-r32) F11 r31 alive
f807117b(track-r31-or-r32) F11 r31 alive
c712ea19(track-r31-or-r32) F11 r32 alive
f807117b(track-r31-or-r32) F11 r32 alive
58c83d12:39.964 F11 r32 alive
d3ec5c41:61.71473(staged-filters) F11 r37 alive
7319bba9:62.34263(decision-DAG) F11 r37 alive
0ae69bcb:72.64(staged-cascade-with-caps) F11 r38 alive
idea:G4c-unrolled-entry-loop(gain-0.169-GUESS) F11 r38 open
idea:decision-DAG-on-A0-blocks(7319bba9-port) F11 r38 open
f310d44f+028aa8d0+035a5381+6e5214dd(track-r31-or-r32) F12 r31 alive
f310d44f+028aa8d0+035a5381+6e5214dd(track-r31-or-r32) F12 r32 alive
ad9745bf(bit-sliced-first-blocks-172.4-ops) F12 r37 alive
efd8aa9d F12 r37 alive
1c368173(bit-sliced-W6-filter) F12 r37 alive
idea:G2-bit-sliced-first-blocks(gain-about-0.13-bit) F12 r37 open
idea:G1-7-lane-SWAR-for-u(gain-about-0.08-bit-GUESS) F12 r37 open
idea:bit-slice-u-over-gathered-pairs(GUESS-worse) F12 r37 open
deb673ae:99.91651(171.5-ops-per-trial) F12 r38 alive
a82eeb40(256-lane-195.5-ops) F12 r38 alive
d5a10596 F12 r38 alive
idea:G4a-first-block-bit-sliced(gain-0.069-GUESS) F12 r38 open
idea:G4b-A0-blocks-packed(gain-0.115-GUESS) F12 r38 open
idea:G4d-row-17-path-bit-sliced(gain-0.079-GUESS) F12 r38 open
idea:G8-solved-first-block-family+DP-tables(GUESS) F12 r38 open
43641180(neutral-bit-table;failed-build;track-r31-or-r32) F13 r31 dead
43641180(neutral-bit-table;failed-build;track-r31-or-r32) F13 r32 dead
idea:neutral-bits/boomerangs-rows-16..22(GUESS) F13 r37 open
idea:neutral-bits/boomerangs-rows-16..22(GUESS) F13 r38 open
idea:multi-block-near-collision(GUESS-dearer) F14 r37 open
idea:multi-block-near-collision(GUESS-dearer) F14 r38 open
GPU-real-37-step-pair:261.5-days-on-one-3090 F15 r37 dead
idea:GPU-exhaustive-table-stats-H9(gain-0-to-0.04-bit) F15 r37 open
idea:GPU-large-q3-studies(evidence-only) F15 r37 open
idea:GPU-large-q3-studies(evidence-only) F15 r38 open
50592e75:37.22(public-text-A_C=0) F16 r31 alive
621d0fb0(public-text;track-r31-or-r32) F16 r31 alive
621d0fb0(public-text;track-r31-or-r32) F16 r32 alive
6eeefb64:46.57(measured-re-run) F16 r32 alive
d3ec5c41:61.71473(A_C-2^60;A_S-2^50;DEV-2^40) F16 r37 alive
76407c7c(not-evaluable-on-A_C) F16 r37 dead
871bfee5(failed-on-H4) F16 r37 dead
idea:measured-37-step-re-run(A_C-removed->61.19051) F16 r37 open
0ae69bcb:72.64(A_C-2^70-CPU-ceiling) F16 r38 alive
2f30479f:76.12(A_C-2^76) F16 r38 alive
7914208c:78.03 F16 r38 alive
8bc7d6c5:70.23909(A_C-2^64-not-evaluable) F16 r38 dead
fd3ac033:72.45(A_C-2^68-not-evaluable) F16 r38 dead
idea:G2-A_S-2^50(->72.37992) F16 r38 open
idea:G3-r37-allowances-or-measured-A_C(->72.06709) F16 r38 open
1347c47e:31.61(real-pair-2^26.7-trials) F17 r31 alive
50592e75:37.22 F17 r31 alive
8f955606(retained-pair) F17 r32 alive
e5312a9b(retained-pair) F17 r32 alive
jungjipdo-line F18 r32 alive
Meganpark980320-line F18 r32 alive
d3ec5c41:61.71473 F18 r37 alive
087a18c4(exact-rational-ledger;H6;H7) F18 r37 alive
7319bba9:62.34263 F18 r37 alive
idea:Bernstein-cap(gain-about-0.013-bit) F18 r37 open
ours:D35-pad-removed:72.61489(unfiled) F18 r38 alive
20dbd783(exact-success-floor-H7) F18 r38 alive
426af47b:72.63(rounded-below-ledger;failed) F18 r38 dead
3b532546:78.11(measured-pair-delta-rejected) F18 r38 dead
idea:G1-revert-two-margins(->71.66909) F18 r38 open
idea:G5-N1-cap-1.25x(->72.60991) F18 r38 open
idea:G7-organizer-executed-H5-test F18 r38 open
idea:ZLGW26-2026/232-37-step F19 r37 open
idea:LLWS26-2026/1080-37-step(theoretical) F19 r37 open
idea:whole-collision-SAT(GUESS-unlikely) F20 r37 open
idea:whole-collision-SAT(GUESS-unlikely) F20 r38 open
"""

GENERIC = ("no board at this depth; the generic cost does not depend on depth (about 2^128 nominal, DERIVED "
           "[FAMILIES]), so there is nothing to scout")
# (family, depth) -> (best score or closing number for GRID.md, reason = the page's 'why'). Every board cell that is
# not n/a has a note; cells without one take NOBOARD.
NOTE = {
    ('F01', 'r31'): ("125.94", "best 125.94 (d02732c7), DERIVED [FAMILIES]; closed board"),
    ('F01', 'r32'): ("124.6", "best 124.6 (5c3f233e), DERIVED [FAMILIES]; closed board"),
    ('F01', 'r33-36'): ("", GENERIC),
    ('F01', 'r37'): ("123.93722", "best 123.93722 (5951ba00), DERIVED [FAMILIES], 62.22 bits above the leader 61.71473 "
                     "(COMPUTED). Closed as a lever: rho / vOW alternatives are irrelevant at 124 vs 61.7 [gaps_r37 G9]"),
    ('F01', 'r38'): ("123.96717", "best 123.96717 (668d3f56), DERIVED [FAMILIES]; distribution-free entries f02ff88f, "
                     "8c92f07c, 1708c3d3, 6739adfa at 128.12-128.23 [MAP_r38]. Closed as a lever: the generic family is "
                     "exhausted, floor about 123.9 (DERIVED [MAP_r38])"),
    ('F01', 'r39+'): ("", GENERIC),
    ('F02', 'r31'): ("125.94", "best 125.94 (d02732c7), DERIVED, and 35ce0758 [FAMILIES]; closed board"),
    ('F02', 'r32'): ("(no score)", "68ca8e4f and 6b88bdb7 used it; their scores are not in our summaries (the "
                     "generic-family best on r32 is 124.6, 5c3f233e, row F01) [FAMILIES]"),
    ('F02', 'r33-36'): ("", GENERIC),
    ('F02', 'r37'): ("123.93722", "best 123.93722 (5951ba00), DERIVED; also 64bca7e2 and 6de1b685 [FAMILIES]"),
    ('F02', 'r38'): ("123.96717", "best 123.96717 (668d3f56), DERIVED; also c65868c3. The ladder 124.968 -> 123.96717 is "
                     "constant factors on one idea: one-block 55-byte messages, 2^24-message groups sharing W0..W12, a key "
                     "on digest words fixed before the last rounds, bit-sliced 256-lane circuits [MAP_r38]"),
    ('F02', 'r39+'): ("", GENERIC),
    ('F04', 'r31'): ("refuted †", "6d554419: own in-chain SAT search, failed (refuted) [FAMILIES]. † Its track (r31 or "
                     "r32) is not in our summaries, so it is listed in both columns; 8bad82c1 / 1ded36a8 (measured route "
                     "search) are listed for r31/r32 without track or status. r31 entries used the published LLWDS24 "
                     "31-step characteristic [literature.tsv]"),
    ('F04', 'r32'): ("46.57", "best 46.57 (6eeefb64, promoted): a measured re-run of the characteristic search for the "
                     "35-step route cut to 32, DERIVED [FAMILIES]. † 6d554419 refuted (track not stated); 8bad82c1 / "
                     "1ded36a8 measured route search (track and status not stated)"),
    ('F04', 'r33-36'): ("2^45.86 run", "measured run: 6eeefb64 re-ran the 35-step characteristic search, 593,858 CPU-s "
                        "[gaps_r37 G4], quoted as 2^45.86 [MAP_r38 H4], DERIVED; the published routes behind the boards "
                        "come from the public SAT/SMT tool [LLW24a] (DERIVED [literature.tsv])"),
    ('F04', 'r37'): ("", "untried on the board: the 37-step search is only charged as the allowance A_C = 2^60 (row "
                     "F16). Logged: G5b, re-optimise the characteristic for the variant-amortised regime, GUESS multi-bit, "
                     "needs the LLW24 tool and a new search (heavy) [gaps_r37]; our own characteristic with a measured "
                     "search would also be a new line [FAMILIES hole 3]"),
    ('F04', 'r38'): ("", "untried on the board: the 38-step search is only charged as the allowance A_C = 2^70 (row "
                     "F16). Logged: a new characteristic or a new dense part [MAP_r38 s.5]"),
    ('F04', 'r39+'): ("lit 39-step SFS", "published: SAT/SMT tools find 39-step semi-free-start characteristics (LLW23, "
                      "about 3 h on 120 threads; LLW24), DERIVED [literature.tsv]; no 39-step collision route exists "
                      "(row F06)"),
    ('F06', 'r31'): ("31.61", "best 31.61 (1347c47e, accepted), DERIVED; 50592e75 37.22 (promoted) [FAMILIES]; the "
                     "LLWDS24 31-step two-block pair is about 2^40.5 (board-quoted, DERIVED [literature.tsv])"),
    ('F06', 'r32'): ("39.964", "best 39.964 (58c83d12, accepted), DERIVED; 6eeefb64 46.57 (promoted) [FAMILIES]"),
    ('F06', 'r33-36'): ("lit 35: 2^48.3", "published: LLWS26 35-step collision, practical, 2^48.3 (board-quoted); "
                        "LZLLQZ26 36-step pair found (DERIVED [literature.tsv])"),
    ('F06', 'r37'): ("61.71473", "best 61.71473 (d3ec5c41, the leader: the two-block attack of 2026/1120 with 222 classes "
                     "of A0-variants), DERIVED; 7319bba9 62.34263. This design's floor is about 2^61.41 at 17 ops per good "
                     "pair (COMPUTED [leader_cost_split]), so the leader sits about 0.3 bit above it. Logged: a "
                     "memory-heavy variant of the 2026/1080 framework, memory being free (size unknown) [gaps_r37 G9]"),
    ('F06', 'r38'): ("72.64", "best 72.64 (0ae69bcb, the leader: the c99df2dc construction, 78.12, with re-priced "
                     "allowances), DERIVED; our rebuild gives 72.633442 and the attack without allowances is 2^72.06675 "
                     "(COMPUTED [MAP_r38, levers_r38]); A0 line 91.5962 (2d1c4fc2), S line 99.91651 (deb673ae) "
                     "[MAP_r38]; our derivative row 72.61489 is in row F18"),
    ('F06', 'r39+'): ("39 not reached", "closed in the literature: LZLLQZ26 does not reach 39 steps on SHA-256 (its "
                      "38-step attack costs 2^104.3), and LLWS26 failed at 38 (DERIVED [literature.tsv])"),
    ('F07', 'r31'): ("", "untried; closed board; r31 entries used the published 31-step characteristic (LLWDS24) "
                     "[literature.tsv]"),
    ('F07', 'r32'): ("46.57", "best 46.57 (6eeefb64, promoted): the CRYPTO 2026 (LLWS26) 35-step route cut to 32; also "
                     "23960a0e and 1e318d08, DERIVED [FAMILIES]"),
    ('F07', 'r33-36'): ("", "no board; the 35-step (LLWS26) and 36-step (LZLLQZ26) routes exist to cut [literature.tsv]"),
    ('F07', 'r37'): ("", "untried. Logged: truncation has low value at 37/38 steps (GUESS [FAMILIES]); the only longer "
                     "source route is the 38-step route of 2026/1120 (DERIVED [literature.tsv])"),
    ('F08', 'r31'): ("31.61", "best 31.61 (1347c47e: 483 starting points, 5.7M table tuples), DERIVED; 3651663d (448 own "
                     "starting points; placed on r31 by the row order in FAMILIES) [FAMILIES]; closed board"),
    ('F08', 'r32'): ("(no score)", "the ed55a9d7 line: valid-tuple tables of about 1.4e9 records; score not in our "
                     "summaries [FAMILIES]"),
    ('F08', 'r37'): ("61.71473", "best 61.71473 (d3ec5c41: 222 of 22,976 classes, 782,800 of 12,103,680 A0-variants), "
                     "DERIVED [gaps_r37 G3]; also 1c368173 (12.1M variants), b947b377, 1f12a09a, 7319bba9 [FAMILIES]. "
                     "Closed: late dense-part variants (free E bits of rows 9..13): 2 variants keep the rows, sum of |L*| "
                     "32 against 32 for S alone, ratio 1.000 (COMPUTED [late_variants_r37.log]). Logged: A1/A2 variants, "
                     "joint (A0, A1) family 2^27.53 = 16.04x the A0 family (COMPUTED [gaps_r37 G3]) but a gain of at "
                     "most about 0.14 bit, since it only amortises the per-first-block share (DERIVED [gaps_r37 G3]; "
                     "FAMILIES hole 1 had left the size open, GUESS); fresh Step-1 solutions, success per first block x2 "
                     "-> 61.11006 (DERIVED [ledger_levers])"),
    ('F08', 'r38'): ("72.64", "best 72.64 (0ae69bcb: (A0, A1, A2) dense-part variants, 2^37.48 per chaining value), "
                     "DERIVED; A0-only line 91.5962 (2d1c4fc2) [MAP_r38]. Closed: more A0 values only amortise the 8.35% "
                     "first-block share, about 0.06 bit, and double the table preprocessing (DERIVED [MAP_r38 s.5]). "
                     "Logged: G6 fresh Step-1 solutions (|L*| = 1 today against the paper's 2^2): |L*| = 4 gains about "
                     "0.26 bit online (GUESS [MAP_r38])"),
    ('F09', 'r31'): ("(no score) †", "† 8080939c (record word and one-cell lookup) [FAMILIES]: its track (r31 or r32) is "
                     "not in our summaries, so it is listed in both columns"),
    ('F09', 'r32'): ("(no score) †", "† 8080939c (record word and one-cell lookup) [FAMILIES]: track not stated, listed "
                     "in both columns"),
    ('F09', 'r37'): ("61.71473", "best 61.71473 (d3ec5c41: x-indexed W6 fibre table), DERIVED; 1c368173 c7 classes "
                     "[FAMILIES]. Closed: r38's (Y, Z0) row-16 table does not transfer, 16 usable A1 values against "
                     "2^19.82 on r38 and W6/W7 depend on A1 (COMPUTED counts, DERIVED conclusion [gaps_r37 G3]); a table "
                     "for the row-16 stage: u needs 7 CV words (the leader's statement, DERIVED [gaps_r37 G1]). Logged: G7 "
                     "W6 cb-amortisation table, about 0.03 bit (GUESS [gaps_r37])"),
    ('F09', 'r38'): ("72.64", "best 72.64 (0ae69bcb: per-A0 row-16 (Y, Z0) tables, 2^64 buckets each), DERIVED; 2d1c4fc2 "
                     "91.5962 uses r37's c7 classes on the A0 line [MAP_r38]. Closed (DERIVED [MAP_r38 s.5]): a W7 "
                     "pre-filter in the tables needs x = A_-1 in the index, 2^96 buckets per A0; r37's c7 classes do not "
                     "collapse in the DP line (c7 depends on A1); a row-17+ index needs W2 (five CV words). FAMILIES hole 4 "
                     "priced halving the per-(CV, A0) work at 72.121 (COMPUTED from a GUESS factor); MAP_r38 rates r37's "
                     "x-precomputation low on r38"),
    ('F10', 'r31'): ("31.61", "best 31.61 (1347c47e), DERIVED; relaxed W20 also in fe63aaad and 50592e75 (37.22) "
                     "[FAMILIES]"),
    ('F10', 'r32'): ("39.964", "best 39.964 (58c83d12: x1.181 at stage 16), DERIVED; 3873e7f5 x1.2983; ed55a9d7 46 -> 44 "
                     "conditions [FAMILIES]"),
    ('F10', 'r37'): ("61.71473", "partial use: the exact Step-2 sets F6/F7 (6c77089c lineage) are in the leader d3ec5c41, "
                     "61.71473, DERIVED [FAMILIES]; the 74 Step-3 conditions (rows 16..36) were never relaxed. Logged: "
                     "Step-3 relaxation, q3 x1.3 -> 61.4625, x2 -> 61.0987, x4 -> 60.6520 (COMPUTED from GUESS gain "
                     "factors [leader_cost_split]); G5c q3 as the collision event, at most about 0.2 bit (GUESS "
                     "[gaps_r37])"),
    ('F10', 'r38'): ("72.64", "partial use: the exact F7 set (20a43626 / 3d819a4b) is reused by the 0ae69bcb line, 72.64, "
                     "DERIVED [MAP_r38]; the about 101 Step-3 conditions were never relaxed. Logged: Step-3 relaxation, q3 "
                     "x2 -> 72.064, x4 -> 71.665 (COMPUTED from GUESS factors [leader_cost_split])"),
    ('F11', 'r31'): ("(no score) †", "† c712ea19 and f807117b [FAMILIES]: their tracks (r31 or r32) are not in our "
                     "summaries, so they are listed in both columns"),
    ('F11', 'r32'): ("39.964", "best 39.964 (58c83d12), DERIVED [FAMILIES]; † c712ea19 and f807117b (track not stated)"),
    ('F11', 'r37'): ("61.71473", "best 61.71473 (d3ec5c41: staged filters; it replaced the decision DAG of 7319bba9, "
                     "62.34263, by tables), DERIVED [FAMILIES]"),
    ('F11', 'r38'): ("72.64", "best 72.64 (0ae69bcb: a staged filter cascade with caps, bucket entry, W7 bitmap, 10-bit "
                     "row-17 mask, deep path; the classification is ours, DERIVED from MAP_r38 s.2). Logged: G4(c) unrolled "
                     "entry loop with one branch per bucket, 56.69 -> 35 ops, 0.169 bit (GUESS op counts [levers_r38]); "
                     "r37's decision DAG (7319bba9) on the A0-block stage, part of G4(b) [MAP_r38 s.5-6]"),
    ('F12', 'r31'): ("(no score) †", "† f310d44f (7 x 36-bit lanes, the origin), 028aa8d0, 035a5381, 6e5214dd "
                     "[FAMILIES]: tracks (r31 or r32) not in our summaries, so they are listed in both columns"),
    ('F12', 'r32'): ("(no score) †", "† f310d44f, 028aa8d0, 035a5381, 6e5214dd [FAMILIES]: track not stated, listed in "
                     "both columns"),
    ('F12', 'r37'): ("(no score)", "used, scores not in our summaries: ad9745bf (first blocks bit-sliced at 172.4 ops per "
                     "trial), efd8aa9d, 1c368173 (bit-sliced W6 filter) [FAMILIES]; the leader charges one full unit per "
                     "first block. Logged: G2 bit-sliced first blocks in the A0-variant line, 61.584..61.588, about 0.13 "
                     "bit (DERIVED [ledger_levers]); G1 7-lane 36-bit SWAR for u, about 0.08 bit (GUESS); bit-slicing u "
                     "over gathered pairs looks worse, about 20 ops per lane against 16.9 (GUESS [gaps_r37 G1])"),
    ('F12', 'r38'): ("99.91651", "best 99.91651 (deb673ae: solved first-block family, 171.5 ops per trial), DERIVED; "
                     "a82eeb40 256-lane evaluator at 195.5 ops per trial, d5a10596 [MAP_r38]; the DP online program "
                     "(72.64) has no SWAR or bit-slicing. Logged (GUESS op counts, exact arithmetic [levers_r38]): G4(a) "
                     "first block 2728 -> 400 ops, 0.069 bit; G4(b) A0 blocks 30 -> 15 ops, 0.115; G4(d) row-17 path "
                     "25.41 -> 15, 0.079; with G4(c) the conservative total is 72.11254; G8 deb673ae's first-block "
                     "family feeding the DP tables"),
    ('F13', 'r31'): ("failed build †", "† 43641180: a neutral-bit table in a failed starting-point build [FAMILIES]; "
                     "its track (r31 or r32) is not in our summaries, so it is listed in both columns"),
    ('F13', 'r32'): ("failed build †", "† 43641180 (a failed starting-point build with a neutral-bit table): track not "
                     "stated, listed in both columns"),
    ('F13', 'r37'): ("", "untried on any SHA-256 board. Logged (GUESS-level [FAMILIES hole 7]): neutral bits or boomerang "
                     "paths that satisfy part of rows 16..22 deterministically; the A0/A1/A2 variants are a cousin "
                     "limited to rows up to 15"),
    ('F13', 'r38'): ("", "untried: the DP line uses no neutral bits, its free words are the modification [MAP_r38]. "
                     "Logged: as on r37 (GUESS-level [FAMILIES hole 7])"),
    ('F14', 'r31'): ("", "untried (notes that mention 3 blocks mean padding) [FAMILIES]"),
    ('F14', 'r32'): ("", "untried (notes that mention 3 blocks mean padding) [FAMILIES]"),
    ('F14', 'r37'): ("", "untried. Logged: multi-block near-collision chaining (a nonzero CV difference cancelled by a "
                     "later block), likely dearer than row F06 at 37/38 steps (GUESS [FAMILIES])"),
    ('F14', 'r38'): ("", "untried. Logged: as on r37 (GUESS [FAMILIES])"),
    ('F15', 'r31'): ("", "untried: several r31 notes say there was no GPU run [FAMILIES]"),
    ('F15', 'r32'): ("", "untried: no GPU run is recorded in our summaries"),
    ('F15', 'r37'): ("261.5 days", "a GPU buys wall-clock only (work is summed over processors), so it cannot lower the "
                     "v5 scalar by itself [FAMILIES]. Closed: running the attack for a real pair, 2^58.32 first blocks, "
                     "is about 261.5 days on one 3090 (COMPUTED from a GUESS 2^33.1 SHA-256/s [leader_cost_split]). "
                     "Logged: exhaustive table statistics that remove premise H9 (x1.02 margin; 0 to 0.04 bit "
                     "[gaps_r37 G6]), about 2^51 simple ops, about 128 s at a GUESS 2^44 ops/s; large q3 studies "
                     "(evidence only) [FAMILIES hole 8]"),
    ('F15', 'r38'): ("", "untried as a run: GPUs appear only as an A_C accounting ceiling (2f30479f: 10^4 GPUs for 10 "
                     "years = 2^73.3, A_C 2^76) [MAP_r38]. Logged: large q3 studies (evidence only) [FAMILIES hole 8]"),
    ('F16', 'r31'): ("37.22", "best 37.22 (50592e75, promoted): the published characteristic accepted as public text, "
                     "A_C = 0, DERIVED [FAMILIES]; † 621d0fb0 passed the same way (track not stated, listed in both "
                     "columns)"),
    ('F16', 'r32'): ("46.57", "best 46.57 (6eeefb64, promoted): a measured re-run accepted, DERIVED [FAMILIES]; † "
                     "621d0fb0 (public text, track not stated)"),
    ('F16', 'r37'): ("61.71473", "best 61.71473 (d3ec5c41: A_C 2^60, A_S 2^50, DEV 2^40; A_C is 30.5% of the total, "
                     "COMPUTED [leader_cost_split]), DERIVED. Closed: 76407c7c (not evaluable on A_C) and 871bfee5 "
                     "(failed on H4) [gaps_r37 G4]. Logged: a measured 37-step re-run replacing A_C: A_C removed -> "
                     "61.19051, A_C 2^56 -> 61.22949 (DERIVED [ledger_levers]); out of reach on 2 CPU processes (GUESS: "
                     "days to weeks; the 35-step re-run took 593,858 CPU-s) [gaps_r37 G4]"),
    ('F16', 'r38'): ("72.64", "best 72.64 (0ae69bcb: A_C 2^70 from a CPU ceiling, A_S 2^70, DEV 2^64), DERIVED; "
                     "2f30479f 76.12 (A_C 2^76), 7914208c 78.03 [MAP_r38]. Closed: 8bc7d6c5 70.23909 (A_C 2^64 as a bare "
                     "claim) and fd3ac033 72.45 (A_C 2^68 anchored on the 35-step re-run), both not evaluable [MAP_r38]. "
                     "Logged: G2 A_S 2^50 at the r37 convention -> 72.37992 (COMPUTED, low risk); G3 r37's allowances "
                     "(2^60 / 2^50 / 2^40) or a measured A_C -> 72.06709 (COMPUTED; r38 refused 2^64 and 2^68) "
                     "[levers_r38, MAP_r38]"),
    ('F17', 'r31'): ("31.61", "best 31.61 (1347c47e: a real pair built at 2^26.7 online trials), DERIVED; 50592e75 37.22 "
                     "[FAMILIES]"),
    ('F17', 'r32'): ("(no score)", "retained-pair entries 8f955606 and e5312a9b; scores not in our summaries "
                     "[FAMILIES]"),
    ('F17', 'r33-36'): ("", "no board; published real pairs exist at 35 (LLWS26) and 36 steps (LZLLQZ26), DERIVED "
                        "[literature.tsv]"),
    ('F18', 'r31'): ("", "not recorded for r31 in our summaries (the jungjipdo and Meganpark980320 ledger lines are "
                     "cited from r32 notes) [FAMILIES]"),
    ('F18', 'r32'): ("(no score)", "the jungjipdo and Meganpark980320 lines: ledger steps worth about 0.01-0.1 bit each "
                     "(DERIVED from r32 notes [FAMILIES]); scores not in our summaries"),
    ('F18', 'r37'): ("61.71473", "best 61.71473 (d3ec5c41), DERIVED; 087a18c4 exact-rational ledger with q3 at the "
                     "printed 99% bound (H6) and the exact success floor (H7); 7319bba9 [FAMILIES, MAP_r38 s.6]. Logged: "
                     "a Bernstein cap, about 0.013 bit [gaps_r37 G6]"),
    ('F18', 'r38'): ("72.61489 ours", "ours: 72.61489 = the leader construction with the 2% N_G pad removed (D35, "
                     "unfiled; COMPUTED [MAP_r38 G5]); 20dbd783 (S line) uses the exact success floor H7 [MAP_r38]. "
                     "Closed: 426af47b 72.63, claim rounded below the exact ledger 72.633442, failed (cause GUESS); "
                     "3b532546 78.11, a participant-measured pair delta 0.0079 rejected [MAP_r38]. Logged: G1 revert the "
                     "two voluntary margins (q3_model 2^-101.01, structural pair delta 0.002931) -> 71.66909 (COMPUTED, "
                     "premise risk), with G2 and no pad 71.11112 (COMPUTED); G5 N1 cap 4x -> 1.25x -> 72.60991 "
                     "(DERIVED); G7 an organizer-executed H5 test would back G1 (GUESS runtime fit) [levers_r38, "
                     "MAP_r38]"),
    ('F19', 'r37'): ("", "untried: no r37 entry cites ZLGW26 (2026/232); the LLWS26 (2026/1080) 37-step attack is "
                     "theoretical [FAMILIES, literature.tsv]. Logged: each is a distinct filed line for the coop count; "
                     "complexities unknown (paper bodies unreadable here) [FAMILIES hole 5]"),
    ('F20', 'r31'): ("", "untried as whole-problem SAT: SAT (z3, STP + CryptoMiniSat) only built starting points "
                     "(1347c47e) [FAMILIES]"),
    ('F20', 'r32'): ("", "untried as whole-problem SAT: SAT only built starting points (the jungjipdo line, track not "
                     "stated) [FAMILIES]"),
    ('F20', 'r37'): ("", "untried: SAT runs only inside the allowances [FAMILIES]. Logged: whole-collision SAT, unlikely "
                     "at 37/38 (GUESS [FAMILIES hole 7])"),
    ('F20', 'r38'): ("", "untried. Logged: as on r37 (GUESS); the literature has a 38-step semi-free-start by SAT plus "
                     "computer algebra (ANB24, GUESS; not a collision) [literature.tsv]"),
}
NOBOARD = {'r33-36': 'no board at 33-36 steps; no published result or measured run for this family in our summaries',
           'r39+': 'no board at 39+ steps; nothing recorded for this family in our summaries'}

# Not-applicable cells (mark 'impossible', drawn as X): family, depths, reason
IMP = [
    ('F03', DEPTH, "not applicable: single-block local-collision routes stop at 28 steps (MNS13 practical 28-step "
                   "collision, DERIVED [literature.tsv]); every column is 31 steps or more"),
    ('F05', DEPTH, "rules exclude free-start and semi-free-start results (cost model v5, DERIVED [FAMILIES]); they serve "
                   "only as validation witnesses inside row-F06 entries (r37 1c368173 and d3ec5c41, r38 the c99df2dc "
                   "line); published SFS reach is 38 steps (MNS13) and 39 steps, practical (LLW23, LLW24)"),
    ('F07', ['r38', 'r39+'], "no source route: no published collision route is longer than 38 steps (LZLLQZ26 does not "
                             "reach 39; the 39-step results are semi-free-start only), DERIVED [literature.tsv]"),
    ('F17', ['r37', 'r38', 'r39+'], "needs a real collision pair at this depth and none exists (37: no published pair; "
                                    "38: 2^104.3 in LZLLQZ26; 39: not reached), DERIVED [literature.tsv]; a 37-step pair "
                                    "at today's design is 2^58.32 first blocks, about 261.5 days on one 3090 (COMPUTED "
                                    "from a GUESS rate [leader_cost_split])"),
    ('F19', ['r31', 'r32', 'r33-36'], "not applicable: this row is the unused published 37-step characteristics; a use "
                                      "at fewer steps is truncation (row F07)"),
    ('F19', ['r38', 'r39+'], "no source: 2026/232 has no 38-step row (per r38 note 8b2ebe50) and LLWS26 failed at 38 "
                             "steps, DERIVED [FAMILIES, literature.tsv]"),
]

HEAD = """# SHA-256: tried and untried, by technique family and step depth

Generated {built} by `research/endgame/sha256_grid.py --md` from the same records as `sha256_cells.csv` (this
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
"""

TAIL1 = """## Largest logged sizes on the live tracks

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
"""

NOTES_INTRO = ("One line per cell with its best score or closing number and its sources. Cells not listed have no "
               "board at that depth and nothing recorded. Record ids for every cell are in sha256_cells.csv (and on the "
               "endgame page, on hover).")

TAIL2 = """## What this grid could not settle

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
"""

FIELDS = ['grid', 'row', 'col', 'mark', 'alive', 'dead', 'open_logged', 'reason']


def load():
    fams = [f for f, _ in FAM]
    recs = []
    for line in REC.strip().splitlines():
        p = line.split()
        assert len(p) == 4 and p[1] in fams and p[2] in DEPTH and p[3] in ('alive', 'dead', 'open'), line
        assert '|' not in p[0], line
        recs.append(p)
    imp = {}
    for f, ds, why in IMP:
        for d in ds:
            assert f in fams and d in DEPTH and (f, d) not in imp, (f, d)
            imp[(f, d)] = why
    for k, (best, why) in NOTE.items():
        assert k[0] in fams and k[1] in DEPTH and k not in imp and '|' not in best and why, k
    return recs, imp


def build():
    recs, imp = load()
    cells = []
    for f, label in FAM:
        for d in DEPTH:
            hit = [r for r in recs if r[1] == f and r[2] == d]
            al, de, op = ([r[0] for r in hit if r[3] == s] for s in ('alive', 'dead', 'open'))
            if (f, d) in imp:
                assert not hit, (f, d)
                mark, best, why = 'impossible', '', imp[(f, d)]
            else:
                if (f, d) not in NOTE:  # only the no-board columns may fall back to a default note
                    assert d in NOBOARD and not hit, (f, d)
                best, why = NOTE.get((f, d), ('', NOBOARD.get(d, '')))
                mark = 'tried-alive' if al else 'tried-dead' if de else 'untried'
                assert bool(best) == (mark != 'untried'), (f, d, mark, best)
            cells.append(dict(grid=GRID, row=f + ' ' + label, col=d, mark=mark, alive=' '.join(al), dead=' '.join(de),
                              open_logged=' '.join(op), reason=why, fam=f, best=best, nd=len(de), no=len(op)))
    return cells


def write_csv(cells):
    path = os.path.join(OUTDIR, 'sha256_cells.csv')
    with open(path, 'w', encoding='utf-8', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS, extrasaction='ignore')
        w.writeheader()
        w.writerows(cells)
    return path


def short(c):
    if c['mark'] == 'impossible':
        return 'n/a'
    s = {'tried-alive': 'T ', 'tried-dead': 'C ', 'untried': 'U'}[c['mark']] + c['best']
    if c['mark'] == 'tried-alive' and c['nd']:
        s += ', C%d' % c['nd']
    if c['no']:
        s += ', o%d' % c['no']
    return s


def write_md(cells):
    by = {(c['fam'], c['col']): c for c in cells}
    built = datetime.now().astimezone().strftime('%Y-%m-%d %H:%M %z')
    out = [HEAD.replace('{built}', built).rstrip(), '', '## Grid', '',
           '| family | ' + ' | '.join(HEADS[d] for d in DEPTH) + ' |', '|---' * (len(DEPTH) + 1) + '|']
    for f, label in FAM:
        out.append('| %s %s | %s |' % (f, label, ' | '.join(short(by[(f, d)]) for d in DEPTH)))
    names = [('tried-alive', 'tried'), ('tried-dead', 'closed'), ('untried', 'untried'), ('impossible', 'n/a')]
    out += ['', 'Counts (COMPUTED by sha256_grid.py, %d cells):' % len(cells), '',
            '| column | ' + ' | '.join(n for _, n in names) + ' |', '|---' * (len(names) + 1) + '|']
    for d in DEPTH + ['all']:
        cs = [c for c in cells if d == 'all' or c['col'] == d]
        out.append('| %s | %s |' % (d, ' | '.join(str(sum(c['mark'] == m for c in cs)) for m, _ in names)))
    out += ['', '## Live tracks: untried families and logged ideas', '']
    for d, best in (('r37', '61.71473'), ('r38', '72.64')):
        un = [f for f, _ in FAM if by[(f, d)]['mark'] == 'untried']
        out += ['### %s (board best %s)' % (d, best), '',
                'Untried families here (a filing would be a new line on this track): %s.' % ', '.join(un), '']
        for f, label in FAM:
            c = by[(f, d)]
            if c['open_logged']:
                ideas = '; '.join(x[5:] if x.startswith('idea:') else x for x in c['open_logged'].split())
                out.append('- %s %s (%s): %s' % (f, label, short(c), ideas))
        out.append('')
    out += [TAIL1.strip(), '', '## Cell notes', '', NOTES_INTRO, '']
    for f, label in FAM:
        out += ['### %s %s' % (f, label), '']
        imp = {}
        for d in DEPTH:
            c = by[(f, d)]
            if c['mark'] == 'impossible':
                imp.setdefault(c['reason'], []).append(d)
            elif (f, d) in NOTE:
                out.append('- %s, %s: %s' % (d, short(c), c['reason']))
        for why, ds in imp.items():
            out.append('- %s, n/a: %s' % (', '.join(ds), why))
        out.append('')
    out.append(TAIL2.strip())
    path = os.path.join(OUTDIR, 'GRID.md')
    with open(path, 'w', encoding='utf-8', newline='\n') as fh:
        fh.write('\n'.join(out) + '\n')
    return path


if __name__ == '__main__':
    cells = build()
    print('wrote', write_csv(cells))
    if '--md' in sys.argv:
        print('wrote', write_md(cells))
    n = {m: sum(c['mark'] == m for c in cells) for m in ('tried-alive', 'tried-dead', 'untried', 'impossible')}
    print('sha256_cells.csv: %d records, %d cells,' % (len(REC.strip().splitlines()), len(cells)), n)
