# Approaches tried on this path that did not improve it: sources for the pkg7 text

Compiled by the main session ("Remainder"), 2026-10-07 about 01:30, for the evidence pass. Each line: what was
tried, the result, the evidence file, who proposed it. Figures marked VERIFIED were read from the file by the main
session; the evidence-pass helper must still read each one from its file before writing it into the text.

1. Solving the residual "inside-out" from known values with redundancy (the owner's "solve it backwards, like a
   zipper" idea). Exhaustive known-set search: on side 1 the smallest redundancy that leaves a complete known set
   is r = 2 (222,513 sets, all of effective r = 2, none with a split equation: VERIFIED in
   `research\h8\redlift\main\out\st_side1_r2.txt`); side 3 has no complete known set at r = 2 (VERIFIED,
   `st_side3_r2.txt`) and its r = 3 case was not completed (stopped 2026-10-06 21:50); all seven words have none up
   to r = 4 (VERIFIED, `seven_r1..r3.txt`, `st_seven_r4.txt`). Each unit of redundancy costs a factor 2^32, so the
   lift cannot pay. Proposed by: the owner. Search: Borrow.
2. A SAT solver per trial to force further conditions. Levels 0 to 2 solve in 0.6 to 6.0 s, levels 3 and 4 give no
   answer in 900 s (VERIFIED, `research\h8\satlift\out\runs.txt`); against about 7 operations per trial for the
   ordinary search this never pays. Proposed by: the owner's request to try forcing; run by Borrow.
3. Forcing a second condition through a coupled block of 2 to 4 equations. 30 of 30 cases UNSAT; the smallest
   coupled block that forces anything is 35 equations (E1.d1), 20 (E3.h1), 49 (both); forcing c1 into its heaviest
   cube costs at least 18,900 operations per forced trial against a break-even of 11,673: a loss of at least 0.7
   bit (VERIFIED, `research\h8\block\VERIFY.md`, `BLOCK_REPORT.md`). Helpers.
4. Bit-level steering and neutral bits for the first-stage test. No neutral bits: a single-bit change keeps the
   condition in 0.048 percent of cases against 0.049 by chance (`research\h8\bitlevel\GRID_REPORT.md`,
   `VERIFY.md`; figure from the handoff, verify). Proposed by: the owner's "grid" view; helpers. (The same study
   found the neighbour effect that the cluster design later uses.)
5. Table lookups to prescribe a second word, and multi-level loops. No gain: the per-trial equation counts stay
   (11 / 25 / 26 and 6 / 18 / 19) (`research\h8\multilevel\ML_REPORT.md`, `ML_VERIFY.md`; `research\tablesolve`;
   figures from the handoff, verify). Helpers.
6. Other absolute values of the same pinned constants ("realizations"). The best of all 4,432 constructed
   realizations gains 177.69 of 162,266,764 (one part in a million) (`research\realize\REALIZE_REPORT.md`; verify).
   Proposed by: GPT Sol 6.1's observation that the count depends on absolute values; helpers.
7. The "four-active" fork (all four diagonal calls active). Best complete trail costs 253 against 100 for the
   path used; proved unsatisfiable only up to 70 to 77 (`research\paths\fouractive\FOUR_REPORT.md`; verify).
   Evidence, not a proof. Helpers; Sol and Grok predicted it would be weak.
8. A search for better pinned constants in the same family (server, 2026-10-06 night, about 2.5 hours, family 8):
   bounds 100 to 103 gave no answer, bound 104 gave two sets with exact class rates 107,785 and 30,487, against
   162,266,764 in use (VERIFIED, `astra-jobs\task6-results\out\totals.txt`). GPT-6 Luna ran it.
9. Other message-length families. Estimates 102 to 107 for the best families other than the two filed ones
   (`research\paths\ATLAS.md` Table 1; verify). Helpers. These remain paths of their own, not dead.
10. A plan to fix bits of the first-stage word with two "knob" words (proposed by a model reached through
    Venice): false on 2,000 real trials (handoff, 2026-10-06 bullet 20:38 and earlier; verify the trial count in
    the 2026-10-06 records before quoting it).

Wording for the text: these are negative results ON THIS PATH; each line should say what would be needed to
revisit it (for 1: a lift of redundancy 1 on side 3 would have to exist; for 7: a proof above 100 or a trail
below 100; for 9: their own packages).
