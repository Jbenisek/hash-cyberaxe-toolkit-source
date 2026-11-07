# Ingest log (2026-10-12, one-time seed of CELLS.jsonl by ingest_2026-10-12.py)

Sources read (read only): research/tools/traillab/ATLAS37.md (22 evidence entries, the 10 ranked "?" targets, and all 136 "?" cells of the full matrix), research/retest/{rows22_24/RESULT.md, expansion_audit/AUDIT.md, r16_per_l/RESULT.md, interaction_grid/GRID.md + wave2_r37/r38/blake3/sha3.md, birthday/SUMMARY.md + r38_phiinv/RESULT.md + r38_validset/RESULT.md}, research/CLOSED_DOORS.md (rows 167-170 dated 10-12 plus the sha256/blake3 rows quoted by the sources), research/LEVERS.md (rows 203-264), HANDOFF.md lines 186-253 (2026-10-11 23:40 to 2026-10-12 02:04), and row_interactions/ (row_interaction_atlas.md, row_tests_summary.md and the four zips, unpacked to the scratchpad and read as data; no code from them was run).

Tagging rules used: own_test=true only where the number came from our own code, workflow or ledger; Luna cloud, Grok (left, right, cloud) and GPT 5.5 results are own_test=false and enter as CLAIMED-UNTESTED, including their "closed" verdicts, unless one of our records reproduces the number (then `confirmed_by`). Where we refuted an outside claim, the claim has its own KILLED record (own_test=true) so the disagreement shows up in CONTRADICTIONS.md.

Not ingested (gaps to fill with add_cell.py):
- Structural D/X formula cells of the ATLAS matrix without a "?" (several hundred; formula-derived, no information beyond the generator).
- Keccak[800] rows (hash is not in the five-value enum).
- Results that landed after the listed sources: research/tools/traillab/atlas_runs/*/RESULT.md (anchor rows 14/16, inverse expansion, hot-H1 row 15), research/tools/traillab/digs/zoneD* and zoneD_r1213, research/tools/traillab/row_cards/, research/sol_answer_D154/D167/D169*.md, research/retest/dense_boring/, research/dossiers/.
- Older CLOSED_DOORS rows (pre-10-12) and LEVERS rows 1-202 except where the late rows quote them; the blake3 w7_* smoke rows are only partly captured (rows are truncated in LEVERS.md).
- Estimates on OPEN cells (`potential_bits` x `prior`) are the ingestor's judgement, not measurements; only the ranked ATLAS targets and the lever rows carry them. The 126 generic "?" cells have none.
- A cell that ATLAS37 lists under several coordinates is recorded at one principal (i, j); the grid in MATRIX.md therefore under-fills the hot block.

## 2026-10-12 dig-scan-b3r3 (incoming3)
- Source: research/dig/incoming3/blake3-r3-U01..U99 (721 JSON records). Added 721; rejected 0 after fix.
- Fix: 72 records (U28-U36) carried an unknown field "cell"; dropped it (cell id already in notes), numbers/verdicts untouched. One accidental duplicate add (C1623 = C0974) removed.
- Not records, skipped: incoming3/_b3r3_work/*.json (10 scratch files), work/, work_b3r3/.
- Coverage after: blake3-r3 universe 786, scanned 533, unscanned 253. Poseidon (r1+r2) scanned 470, unscanned 666. Validation errors: 0. LEVER records: 13 (lever=true).
