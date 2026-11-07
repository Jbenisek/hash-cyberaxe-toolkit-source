# map-lit: SHA-256 literature and technique-family map (2026-10-10, 11:45 -06:00)

| File | What it is |
|---|---|
| FAMILIES.md | The deliverable: 20 technique families, best-known SHA-256 results, fit to the fixed-IV target, which r31/r32/r37/r38 entries used each one, leader cost anatomy, ranked holes, convention gap, limits |
| literature.tsv | Literature anchors with ePrint ids; each row labelled DERIVED (abstract fetched today or board-quoted) or GUESS (memory) |
| entry_family_tags.tsv | COMPUTED keyword tags for all 309 entries on the four SHA-256 boards (noisy; for lookup, not proof) |
| leader_cost_split.txt | COMPUTED arithmetic: r37 and r38 leader ledgers split into online, allowances and floors, with sensitivities for the holes |
| tools/list_board.py | Extracts id, user, status, scores and note heads from a board JSON |
| tools/scan_families.py | Keyword family tagger and snippet viewer over the board notes |
| tools/tsv_and_math.py | TSV recency check and the ledger arithmetic behind leader_cost_split.txt |

Nothing here is a filing. Participants' text is not copied; entries are cited by submission id.
