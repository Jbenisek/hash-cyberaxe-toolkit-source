# sha256 Pareto dig, r39..r64 (site report, 2026-10-17 ~01:30 MDT)

Cells: `research/dig/new/sha256.dug.jsonl` (364 cells, 14 questions x 26 rows). Source of numbers: each row's `result.json`, `logs/ledger.out` and `pkg/sha256/claim.json` under `research/rows_1016/factory/{s256roll3 (r39-41), s256roll4 (r42-64)}`, plus `s256u5/r64`, `levers_1016/dig_s256step`, `gap_s256r64`, and the board snapshot (data only). No builds, no submissions, nothing deleted; one process (python), minutes.

## Cells closed
- 339 COMPUTED (61 prefilled before, 278 closed now), 25 OPEN, 0 KILLED, 0 LOCAL_ONLY (the one LOCAL_ONLY, r39 Q8, is now COMPUTED).
- The 25 OPEN cells are Q14 on r39..r63 (u5 5-byte unrolled kernel). Each carries a derived estimate in `number`/`gain_bits`; the closing run is a u5 row build with `rows_1016/factory/s256u5` (hours), gated by the H3 machine-convention ruling on 4e278a64.
- Q1-Q7, Q9, Q11-Q13 closed on all 26 rows from the exact ledgers. Check done on every row: log2(N/C) reproduces the recorded time_log2. Q8/Q10 were prefilled (rival present only on r39 and r64; the other 24 rows are empty squares for rivals as of 01:00 MDT).

## New finding (a defect, not a lever): executable preprocessing under-declared
Test (minutes, exact): executable preprocessing = fixed part 813,600 + the row's measured generator fuel (`gen_fuel`, wasm operators), divided by C, in log2. On r43 it gives 2^11.55379, identical to the judge's refutation of 59557cd0 (F-preprocessing-executable-undercount, declared 11.5). Applied to all 26 packages (`claim.json`):
- OVER the declaration (would be refuted the same way): r43 (11.55379 vs 11.5), r47 (11.40987 vs 11.4), r48 (11.51373 vs 11.5), r59 (11.05041 vs 11.0), r62 (10.83786 vs 10.8), r63 (10.94872 vs 10.9).
- Sibling packages r43b, r47b, r48b already declare the executable value (zero margin, rounded, which is allowed). r59b, r62b, r63b have no package yet. Margins on the other rows are 0.014..0.5 bit (smallest r52 0.0139, r49 0.0151, r51 0.0206).
- Cost of the fix: 0 bit (setup is about 1e-33 of N). Recommend adding this check to prefile for every family with a generator charged per call.

## Patterns across rows
- Time is nearly flat in R: r42 124.555 to r64 124.638 (0.083 bit over 22 rounds); body ops grow about 2,100 per round while C grows 84.
- Pareto dominance inside our own roll4 set: r58 (124.6272) is dominated by r59 (124.62655); r62 (124.63994) by r63 (124.63699) and r64 (124.6384). Whether the board scores dominated rows is NOT verified; check before spending filings on them.
- Sawtooth in (nit, ss): rows with ss=10 (r42, 46, 50, 54, 58) sit above their neighbours, ss=6/7 below. The stored sweeps (4 points per row) show the chosen point is the optimum; nit+1 costs +0.008..0.09.
- The 4984-gate, 4-step body is identical on all 26 rows, so every kernel lever transfers by construction. Ch/h shared XOR measured -0.0259/-0.0265/-0.0270 on r39/r40/r41 (flat).
- Memory is full within 0-20 bytes on every row (the only memory lever is the code/arrays/table trade). Success slack is 3e-9 to 4e-9 everywhere (worth <2e-8 bit): empty square on all rows.
- Control/dispatch is 0.2-0.4% of ops (about 0.003-0.006 bit): empty square.
- Rival rows: only r39 (we lead 0.48 bit; dariolina 744875ec) and r64 (rival 6b678689 124.41766 leads roll4 by 0.2207; u5 r64 124.39014 would lead by 0.027).

## Top 5 levers (estimated bits x rows touched)
1. **u5 5-byte unrolled kernel on r42..r63**: 0.224 (r42) to 0.244 (r63) bit per row, 22 rows, about 5.4 bit-rows (r64 measured 0.248; r39-41 only about 0.028 each). DERIVED estimate (overhead scaled by (R-16)/48 from the measured r64 overhead 18,603 ops), +-0.03. Brief: loop the existing s256u5 factory (row.py/stage_row.sh, built for r64 only) over R=42..63 with the declared-preprocessing fix of Q7; fire after the ruling on 4e278a64 (the only H3 machine-convention item refused once on d76f9105).
2. **Preprocessing-declaration fix + prefile check** (correctness, saves 6 refutations): rows r43, r47, r48, r59, r62, r63. Brief: declare ceil(log2((fixed + gen_fuel)/C), 0.1) in claim.json, proof Section 3.3 and note for those packages (r43b/47b/48b exist; build r59b/62b/63b) and add the fuel test to prefile.
3. **22 -> 19 byte table entry**: 0.004 to 0.014 bit per row (r39 0.0103, r64 0.0058), 26 rows, about 0.16 bit-rows. Brief: bit-level repack of key remainder, trail length and trail number (in the shared generator), proof change in the loss term; applies to all rows once.
4. **Halve the recovery program** (0.70% of N at r64 to 1.39% at r39): about 0.005 to 0.010 bit per row, 26 rows, about 0.14 bit-rows. Brief: wider packing does not help (only 2 trails); needs a cheaper recovery walk, low priority.
5. **Rival gate savings on unrolled rows** (shared a^b XOR reused as b^c in Maj, carry-save fold of K and constants): 618 gates = 0.0089 bit at r64, about 0.005-0.009 on r42..r63 after lever 1, about 0.16 bit-rows. Brief: port the two savings into bssha.py's unrolled mode (credit 6b678689) before building u5 rows.

## Empty squares (all COMPUTED, in cells)
Prefix choice and chain-word order (243 patterns, r39); polarity-by-majority (worse); rolling the schedule for table space (net 0); FA 5 gates/bit, 6 FA rows/step, K 2 gates/bit, Sigma 2 xor/bit (derived floors); success-bound slack (all rows); control/dispatch share (all rows); memory slack (all rows); schedule loop with unfolded constants vs unrolling those words (code cost about equals table gain, net about 0, DERIVED). Untested: global Paar CSE over the 4-step body (open since dig_s256step), the u5 build on r42..r63, bit-exact recheck of the Ch/h program on the cloud.

## Caveats
Estimates (Q4, Q9, Q14 gains) are derived, labelled in the cells. Rival notes were read as data only (first ~900 characters). Ledger/result values were read from files, not re-run, except the preprocessing recomputation and the log2(N/C) check. Local PC instability note applies to nothing here (no bit-exact runs).
