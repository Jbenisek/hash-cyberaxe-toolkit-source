# SHA3-256 Pareto rows r6..r24 - dig report (2026-10-17, ~90 min, research only)

Cells: `research/dig/new/sha3.dug.jsonl` (266 cells; CELLS.jsonl and the other families untouched).
Before: 202 OPEN / 52 COMPUTED / 12 LOCAL_ONLY. After: **245 COMPUTED / 17 LOCAL_ONLY / 4 OPEN**.
Method: numbers read from the v4 certificates (`rows_1016/factory/ls1v4/out/r8..r22`: cert_out, ledger, counts, rulecheck), RESULT.md files, the 10-17 board snapshots (data only), plus four own minutes-scale tests (below). Nothing built, packaged, staged or submitted. Local: one WSL process at a time, nice 19, no GPU.

## Own tests (labelled own_test=true in the cells)
1. **Polarity planner (gen4 mode 4) on r9..r21**, same trial as the row's v4 build, base = gen3 mode 3 (which reproduces the v4 ledgers exactly). 12 new rows measured, all 12 programs checked against a Python Keccak (verify.py): **0 bad bits of 16384**. Gain per row -0.0038..-0.0057 bit (r8..r22, 15 rows, sum about -0.074).
2. **Rival r6 constants (sraiw 7d11f600, "annihilating family") in our gen3**: re-expressed in our lane roles, r8 +405 ops (+0.0144 bit WORSE), r22 +406, linear forms 2112 vs 1709. Does not transfer (one family member only; their stated 14 constant lanes not reproduced, I get 11).
3. **LS1 v4 model extrapolated to r23/r24** (dig_ls1rows model.py, A+C, 4 records/word, gen3 ops 146,799 at r24): r23 ~124.530, r24 ~124.544 vs filed generic 124.849 / 124.855. Calibration on r22 +0.0027, r8 +0.0009.
4. Preprocessing-memory margin trend from the 15 v4 certificates: 509 KB (r8) falling 33.5 KB per round to **37,180 B at r22**; so r23 fits (~+4 KB), r24 is ~29 KB over 2^20.

## Findings that change the grid
- **r6 is not a Pareto row** (acceptedRoundCounts 7..24). It sits on the exploratory board, where sraiw 7d11f600 leads with 124.13884 (27,391 ops) over our LS1C3 2acfdbee 124.16399 (27,889 ops). The prefilled r6 Q8 and Q10 said "no rival / no filing": corrected.
- **Filed LS1R7 (124.28591) is on the old generator**: 35,517 ops vs 33,950 from the present gen3; it is worse than our own r8 (124.23221). No LS1 v3/v4 r7 row was ever built.
- v4 realised its levers: delta vs v3 -0.0195..-0.0544 on r8..r22 (r8 -0.0334 vs the -0.0327 dig_ls1rows prediction; r18 -0.0544 vs -0.0533; r22 -0.0381 vs -0.0352): the dig_ls1rows model holds. All 15 rows are staged, not filed; board (00:59 snapshot) shows LS1V4R8..R19 only.
- The "NOT vs 320 per round floor" in the Q13 cells reads below the floor (e.g. 180/round at r12) because the chi10 trick and constant folding remove NOTs; the floor is the pure model, not a bound.

## Empty squares
- Rivals: none on r8..r23 (Pareto board); r7 kaankolcu 84a44ee0 124.419; r24 sraiw ac6d8975 124.563 (arithmetic does not hold up, gap_sha3r24); r6 sraiw 7d11f600 (exploratory).
- OPEN (4): r6 Q3 memory peak, Q4 packing, Q6 premise, Q7 preprocessing (need the LS1C3 package text; not read).
- LOCAL_ONLY (17): r7 Q2-Q7 (no v3/v4 r7 row, filed proof not re-read), r6 Q2/Q5, r23 Q1/Q2/Q7 (not itemized in files read), r23/r24 Q12/Q13/Q14 (model extrapolation, nothing built), r24 Q2.
- Not tested: judge view of the v4 rows (no ruling yet), H_rand beyond what the rows already carry, verify.py on the polarity programs of r15/r22 beyond the existing matrix.

## Pattern across rows
One lever applies to the whole LS1 range r7..r22: gen4 polarity (-0.004..-0.006 per row, flat). The v4 A/B/C gain shape is smooth with one break at r18 (v3 H was table-forced). Memory regime: search margin ~4.5 KB on every row, preprocessing margin shrinks linearly and ends at r24.

## Top 5 levers (bits x rows)
| # | lever | est. bits x rows | label | one-line build brief |
|---|---|---|---|---|
| 1 | LS1 v4 line on r23 and r24 instead of generic v4b | about -0.31 x 2 = -0.62 | MODEL, not built | run `row4.sh 23` / `24` (gen3 NR=23/24, KAT, cert4, other4); r23 fits memory as is; r24 needs the gen3 image (~303 KB) trimmed by >=30 KB or the program streamed; then package with the v4 template |
| 2 | Rebuild r7 on the current pipeline (gen3 + v4 A/B/C + polarity) | -0.083 (v3 cert) to about -0.12 x 1 | COMPUTED gen level (33,950 vs 35,517 ops; cert 124.20272), cert4 not run | `row4.sh 7` (needs S for r7 from the memory formula), package as LS1V4R7 with the filed LS1R7 as dependency |
| 3 | Port v4 A+B+C (+polarity) to the r6 LS1C3 line | about -0.035..-0.04 x 1; closes the 0.025 gap to sraiw 7d11f600 | ESTIMATE from r8 | apply other4/cert4 to the r6 generator (walk_a/s14 chi10 build, 27,889 ops); keep ISA as in LS1C3 |
| 4 | gen4 polarity planner (mode 4) on r7..r22 | -0.004..-0.006 x 16 rows = about -0.08 total | COMPUTED ops, 16 programs 0 bad bits; cert re-run only on r7/r8/r15/r22 | build gen4 (SC=16, WLOOK=3) into the row factory; rerun cert4 per row; fold into the next refile of each row, not alone |
| 5 | Packing/drop-length for the generic lines (r23/r24 if lever 1 is blocked) | -0.06..-0.11 x 2 | CLAIMED (BIT_PACKING_AUDIT, not re-read) | 3 records/word drop-length table in sha3genv4b; only if the LS1 line cannot meet 2^20 at r24 |

Considered and dropped: rival annihilating constants in gen3 (worse, +0.014), +table words (needs register-indirect ISA), margin 4096->0 (<=0.0006), drop "+Lc" in HMAX (-0.0003..-0.0005 x 15, fold in with any refile).
