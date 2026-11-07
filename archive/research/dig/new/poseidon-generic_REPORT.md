# Poseidon generic rho rows r3..r56: dig report (2026-10-17, ~01:00-01:45 MDT)

Cells: `poseidon-generic.dug.jsonl` (756 cells; validate passes with the hash whitelist widened). Source file untouched. Local python only, nice 19, one process at a time, no GPU, no cloud, no WSL. All numbers recomputed on the factory code (`rows_1016/factory/posgen_route2d2/rows/rR/rho.py --plan`, `work/tune.py`); the ledger reproduces every row's filed `ledger_without_prep` with difference 0.

## Cells closed
- 284 OPEN cells closed to COMPUTED (all 12 OPEN question types over r3..r56). 755 COMPUTED, 1 LOCAL_ONLY (r56 Q8, the one rival: tanctl e62e3daf 126.827, ours 2d2 r56 is 126.21919). 0 OPEN, 0 KILLED.
- About 470 cells (Q1, Q2..Q7, Q9, Q11..Q14 on every row) were rewritten with row-specific numbers, because the prefill was stale in two places:
  1. The prefilled Q9/Q13 said the hidden-basis cut (-4 ops) was NOT applied in ROUTE2D2. It is applied: every 2d2 row has 136+12r step ops (r20: 376, package says "136 + 12 r"), not 140+12r.
  2. The prefilled Q5 said the filed n carries 1.393*n0 = 0.4846 bit of slack. That is route2/2c. The 2d2 rows have n = n0, slack_bits 0.0, success 0.39000000x.
- r43 Q10 (was OPEN): filed bb856819 at 01:00 MDT, status validating, no ruling yet.

## New findings
1. **Generic r3..r6 are buildable** (empty squares since the factory builds r>=7). The 2d2 template built in scratch at r3, r4, r5, r6 gives time_log2 126.32675 / 126.31755 / 126.30951 / 126.30243 (172/184/196/208 step ops, memory 1,048,548 to 1,048,560 B), selftest step == reference rounds 6/6, line affine. Organizer `verify_digest` NOT run (needs WSL organizer root). The algebraic line (38.6 / 42.9 / 47.1 / 52.8) beats them by 80+ bits, so they are extra paths with no rank gain.
2. **Unroll optimum drifts with r** (tune.py on patched copies, all 50 rows, 12 variants each). Best base unroll: U=16 at r7-r15, 12 at r16-r26, 8 (filed) at r27-r41, 6 from r42. The 2d2 rows all use U=8.
3. **Top-bit DP uniformity** (own test, real map): 300k outputs at r7 and 100k at r30, 24-bit prefix pair collisions top/low/mid = 2702/2609/2607 (expected 2682, sigma 52) and 295/293/317 (expected 298). Top bits are as random as low bits. The gap law with top-bit DPs is still not re-measured.
4. **Memory sits exactly at 2^20 (zero headroom) on r10, r18, r34, r42, r50**; other rows have 4-40 B. Code is 9 percent of the budget at r7 and 28 percent at r56.
5. Lemma loss eps_total (5.0e-4 to 6.3e-4) is worth at most 0.0012 to 0.0015 bit of n; dominated by n*d/N, already tuned (KD 19/2).

## Remaining levers (ledger-recomputed, bits of time_log2, per row)
Mean over r7..r56: A compare-only DP 0.00318; A + best unroll 0.00335 (max 0.00735 at r7); A + block add+branch + best unroll 0.00364; D fixed function 0.00319; E sum-tail recovery 0.00119. Sum over the 50 rows: A+U 0.168, A+B+U 0.182. Everything left is below 0.01 bit per row: the generic rows are tapped out apart from these.

## Top 5 levers (bits x rows) with a build brief
1. **Compare-only DP + per-row unroll** (A+U): 0.0034 mean x 50 rows = 0.168 bit-rows (r7 0.0074, r56 0.0020). Brief: set `W_LOOP=2`, DP = {x < T} (T about 2^141.2, table word stores x>>16 plus the 16-bit side field as now), UNROLL from the breakpoints above, update proof Section 6 listing and the gap-law sentence (re-measure gaps with top-bit DPs, minutes), rerun `gen_row.py R` + `stage_row.sh R`.
2. **Fixed function e_0 = 0 (D)**: 0.0032 x 50 = 0.159 bit-rows. Brief: drop the rho0 ADD (KAT passed in dig_posgen); needs the owner to accept a fixed-function H1 (premise change, judge risk). Not recommended before 1 is filed.
3. **Sum-tail recovery budget (E)**: 0.0012 x 50 = 0.060 bit-rows. Brief: replace 3*gmax by a bound on g1 + 2*g2 (two independent geometric gaps), prove one tail sentence, change `gmax`/`3*gmax` in ledger and Lemma 2; no code change.
4. **Block add+branch (B)**: extra 0.0004 x 50 = 0.020 bit-rows. Brief: `W_BLOCK=2` (counter test by the flag of the add); rule-dependent fused op, judges have not seen it for this loop.
5. **Lemma loss eps (tighten the failure terms)**: up to 0.0012-0.0015 x 50 = about 0.065 bit-rows ceiling. Brief: re-tune KD/H/TAB jointly with a sharper `n*d/N` term (first d cycle values with no DP); only worthwhile if lever 1 is already filed.
(Also: generic r3..r6 as extra paths, 4 rows, zero rank gain, needs `gen_row.py` to accept R<7.)

## Empty squares (recorded)
- r3..r6: no factory row, no filing; built in scratch (above); dominated by algebraic.
- Rivals: no valid rival entry on most generic rows (board snapshot 01:00 MDT); only r56 has one.
- Gap law with top-bit DPs: not measured (only uniformity). H1 evidence exists only at r7, r23, r56 (other rows inherit).
- Organizer `verify_digest` not run for any row built in scratch; no lever variant was KAT-ed beyond the step program (step is unchanged by A, B, E, U).
- Gap-law-free levers D and E carry premise/proof risk, not tested by a judge.

## Files
Scratch tools: session scratchpad `pgcalc.py`, `fill2.py`, `topbit.py`, `var/v.py`, `var/grid.py`, `pg36/` (r3..r6 builds). No factory file was changed.
