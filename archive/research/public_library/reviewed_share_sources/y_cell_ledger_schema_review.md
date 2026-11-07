# Historical board/lever ledger: schema and publication scope

Original filename: `CELL_LEDGER.tsv`.
Original SHA-256: `bd4201886602f38b9ec34b61b111cf287514ef0ce8bfe0f9e6cf598e68ffb280`.
Original size: 24,359 bytes; 111 lines including the header; 110 parsed data rows. Schema, first five rows, group counts and historical timestamp fields inspected on 2026-10-29. This was not a scientific revalidation of every ledger claim.

This file is **not** the 125,700-row solver-run ledger. It is a historical board and lever inventory. Its 15 columns are track, row, our_best_filed_id, our_best_filed_score, our_best_status, leader_id, leader_score, gap_to_leader, our_inflight, staged_or_counted_score, staged_basis, staged_date, open_levers, blockers and board_read. The open-levers column encodes lever, delta, basis and date within a cell.

| Track | Rows |
|---|---:|
| Pareto BLAKE3 | 5 |
| Pareto Poseidon | 56 |
| Pareto SHA-256 | 26 |
| Pareto SHA3-256 | 18 |
| BLAKE3 r2 exploratory | 1 |
| SHA-256 r37 exploratory | 1 |
| SHA-256 r38 exploratory | 1 |
| SHA3-256 r5 exploratory | 1 |
| SHA3-256 r6 exploratory | 1 |

All 110 rows have historical status `review`; the common board-read timestamp is 2026-10-20 03:00 MDT. The first rows compare filed BLAKE3 r3-r7 scores with then-leading entries and retain counted-but-unfiled alternatives. They are not fresh rankings, final acceptances or verified current best costs.

Publication disposition: retain this schema/count/provenance note as a historical data guide. Do not republish the mixed raw TSV as a current board or treat its blockers and planned levers as proved scientific conclusions. A clean historical table would need per-field review and dates, preserving filed versus counted status; underlying scientific methods belong in their original package articles. Operational command strings, private coordination pointers and internal scheduling commentary were not imported.
