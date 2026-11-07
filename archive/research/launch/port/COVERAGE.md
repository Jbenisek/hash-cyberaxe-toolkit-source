# Template coverage (10-18 21:05 MDT) — every filed row templates and reconstructs EXACT

mktmpl aligns rows of any size (diffing sections become block slots), so EVERY row can be put in a template and
rebuilt byte for byte. What varies is how much it GENERALIZES: a family that shares most lines fills a new round
from a values file; rows that share little still reconstruct exactly but store most of each row as blocks (useful
for a number-only refile, not for a new round).

## Families — share most lines, a new round = values file + newrow.py (<1s) + intake
| family | rows | reconstruct | held-out row | build+intake |
|---|---|---|---|---|
| poseidon_onecentre | r11,r12-r22 (12) | EXACT 4 files | r13 identical | 0.45s |
| poseidon_generic | r7-r56 (50) | EXACT 4 files | r40 identical | 0.44s |
| sha3_r9_r22 | r9-r22 (14) | EXACT 4 files | r15 identical | 0.38s |
| sha256_r40_r64 | r40-r64 (25) | EXACT 4 files | r50 identical | 0.50s |
| blake3_r5_r7 | r5,r6,r7 (3) | EXACT 4 files | ALL FIT | — |

## Pair / low-generalization templates — reconstruct EXACT, mostly blocks (good for refiles)
| template | rows | note |
|---|---|---|
| sha3_r7_r8 | r7,r8 | 204-line diff, 2 rows |
| sha3_r23_r24 | r23,r24 | 185-line diff, 2 rows |
| blake3_pareto | r1,r3,r4,r5,r6,r7 | reconstructs all 6; r1/r3/r4 share only ~8 lines (stored as blocks) |

## Single filed rows — single-row template (reconstructs exact; = the package until a sibling is filed)
- SHA-256 r39 (templates/sha256_r39_single): reconstruct EXACT; end-to-end intake PASS (mechanically_valid, 73 s).
- BLAKE3 r1/r2/r3/r4 (templates/blake3_r*_single): reconstruct EXACT each.

EVERY filed row now has a template that reconstructs it byte for byte (28 template files, 0 failures).

## End-to-end mock intake (mock_times.txt) — build from a base package, fill, organizer intake, stage-only
| row | from | build | intake | result |
|---|---|---|---|---|
| poseidon one-centre r13 | r12 base | 0.45 s | 98 s | mechanically_valid |
| poseidon generic r40 | r39 base | 0.44 s | 20 s | mechanically_valid |
| sha3 r15 | r14 base | 0.38 s | 2.3 s | pareto_candidate rc=0 |
| sha256 r50 | r49 base | 0.50 s | 26 s | mechanically_valid |
| sha256 r39 (single) | itself | 0.41 s | 73 s | mechanically_valid |
| blake3 r6 | r5 base | 0.37 s | 3 s | mechanically_valid (ack_flags answered) |

No row is left without a path. Build time is always under 0.5 s; intake time is the organizer's.
