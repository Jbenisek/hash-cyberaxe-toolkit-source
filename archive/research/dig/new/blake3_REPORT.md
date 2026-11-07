# BLAKE3 Pareto rows r3..r7: dig report (10-17, ~01:40 MDT)

Cells: `research/dig/new/blake3.dug.jsonl` (73 records: the 70 survey cells plus 3 new X-cells; all pass `add_cell.validate` with the hash whitelist widened; ids unique). CELLS.jsonl and other families untouched.
Labels: COMPUTED = read from our ledgers/filed text, or run here as a ledger-only (plan/ledger) test; no generator, KAT, selftest or organizer intake was run for anything new. Nothing built, staged or filed.

## Cells closed
- 40 OPEN -> 0 OPEN. Final status count: 70 COMPUTED, 2 LOCAL_ONLY (rival rows, unchanged), 1 BEDROCK (r3 Q13, unchanged).
- Closed by file-read plus arithmetic: Q2 (control), Q3 (memory), Q4 (packing), Q5 (slack), Q6 (premise/evidence), Q7 (preprocessing), Q12 (special at that round) on all five rows, Q13 on r4..r7. Arithmetic cross-checks that reproduce filed ledgers exactly: rolled steps r5c 37,218 and r6c 46,214 and r7c 55,210 ops; memory sums r3/r4d/r5b/r6b/r7c/r7e; per-round increment 7,184 gates (r3 17,238, r4 24,422, r5 31,606, r6 38,790, r7 45,974).
- Closed by a run here (7 cells + 3 X-cells, `own_test` true; scripts in the session scratchpad, 1 process, nice-low, no GPU, no cloud): r3 Q3, Q5, Q11, Q12, Q14, r4 Q3, Q4, X1..X3.
  - Compact bsrho ledger reproduced: r3 124.76595 (the DERIVED 124.766 of blake3_r7/compact/RESULT.md), r4 124.86022 (filed-build 124.86023).
  - First-collision lemma on the r3 v2 program: FAILS at its kappa 11 (P 0.38535; cut_halt 0.0226 because r3 keeps cmax 2). At kappa 13/14 it holds (P 0.40146/0.40063): time 124.83985 -> 124.80083 (-0.0390 incl. kappa).
  - r3 kappa scan: 11 -> 14 = -0.0143 alone; with 10 B entries -0.0554. Registers 1,024 -> 800: -0.0013.
  - Memory sensitivity on the 5-byte compact line: +-8 KiB moves r3/r4 by < 0.00003 bit.
- Side effect: I copied `lemma_r3.py` into `research/levers_1016/dig_b3r4r7/` while testing (a new file, nothing edited); the other scripts are in the scratchpad.

## Empty squares (checked, nothing there)
- r3: no adder below 5 gates (bedrock); loop unroll < 0.0003; probability margin < 0.001; memory limit above 2^20 worse (planner); no rolling (fits).
- Compact (5-byte) line, all rows r3..r7: recovery is 0.32-0.35 % of N, control 0.15-0.21 %, events < 2e-8: the main loop is 99.65-99.68 %. Memory, registers, counters, entry packing, instruction bytes are worth < 0.00003 bit per 8 KiB. The success bound is at 0.390000001 (zero slack). So nothing is left below the gate count except unfiled rows.
- r4 rolled (+0.055 worse), prefix 1 (+0.02..0.054 worse), prefix 3 (no fit), unroll u=2 (+0.031), 6 B entries (+0.28), kappa 13 -> 14 on rows already at 13 (-0.003).
- Neighbour r2 (B3Z8) memory levers do not transfer to this family.
- Not testable: full-width H1 evidence; judge acceptance of the 5 B gate word and of the loop pricing (H3 was graded plausible in all lanes of a0398a27 per HANDOFF 10-17 01:00).

## Patterns across rows
1. Every added round costs exactly +7,184 gates (40 adders x 154 + 1,024 XOR); per-trail ops / C(r) rises 0.106 -> 0.113 -> 0.117 -> 0.120 -> 0.122 (r3..r7), so the compact-line score climbs +0.094, +0.054, +0.035, +0.025 per round (124.766, 124.860, 124.914, 124.950, 124.975).
2. The 5-byte gate word is the one lever that spans the family: it removes the straight/rolled regime change (r4 954 KB is the last 36 B straight line that fits). Gain vs the best 36 B line: r4 -0.0745, r5 -0.2836, r6 -0.2812, r7 -0.3166, r3 -0.0464 (vs the 124.8123 front). Everything else (rolling, register/counter/entry trims, recovery rolling) is a 36 B-line fallback and dies on the compact line.
3. The first-collision lemma plus kappa 13/14 spans r3..r7 (-0.039, -0.0535, -0.0296, -0.0284, -0.0216); already inside the compact builds and r6d/r7d, not in r3 v2, r4d/r4f, r5c.
4. r3 is the odd row: kappa 11, cmax 2, 25 B entries (r4d..r7 are kappa 13, cmax 1, 10 B). That is where the unclaimed gap sits.

## Top 5 levers (bits x rows touched, with a one-line build brief)
1. **r3 compact line**: -0.0739 vs v2 (-0.0464 vs front 124.8123) x 1 row, the only row with no compact/first-collision filing. Brief: run the r7 compact bsrho at ROUNDS=3 UNIT=638 (ledger 124.76595, Tp 1,328, 87,359 entries), use the u5b 17-bit trail field (87,359 > 65,536), rebuild generator/KAT/selftest at r3, set Section 4 to the first-collision proof with cmax and kappa 14 constants; cmax 2 makes the lemma conservative.
2. **Get r4 and r5 compact (u5b) judged and verify r7e's field**: -0.0745 (r4) and -0.2836 (r5) = -0.358 x 2 rows. They sit in the u5b queue (HANDOFF 10-17 01:10); r6 is filed (f07a5442). Brief: confirm the filer posts r4/r5; r7e 76ab339a (72,522 entries) was named by the 00:45 HANDOFF as having the 16-bit overflow, so check/refile it in the 17-bit form.
3. **36 B fallback for r3 (kappa 14 + first-collision, keep 1,024 regs)**: -0.039 x 1 row, if the 5 B convention is refused. Brief: change KAPPA_256 to 13/14, cmax 1 if the program allows, replace Lemma 2 with the first-collision text, re-plan B.
4. **First-collision on the remaining 36 B lines**: r4 -0.0535 (r4d/r4f), r5 -0.0296 (r5c): about -0.083 x 2 rows, also fallback-only. Brief: rewrite Lemma 2 Steps 2-6 (cutlemma RESULT s1-4) and have an independent read first.
5. **Small trims on a 36 B r3**: 10 B entries + kappa 14 -0.0554 (needs recovery re-priced, about 2x recovery work), registers 800 -0.0013: about -0.06 x 1 row, again only if the compact line is refused. Brief: re-price recovery with recomputed lengths and rerun `plan` with ENTRY=10, KAPPA_256=14.
Honest ceiling: with levers 1-2 filed the family sits at the compact floor (main loop 99.65 %, zero P slack); the remaining headroom is under 0.01 bit per row unless an adder-level idea beats 5 gates/bit.
