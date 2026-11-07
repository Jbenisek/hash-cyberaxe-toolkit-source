# research/dig/ - the single store for the row dig

One file of record: `CELLS.jsonl` (one JSON object per line, append only). Everything else here is generated.
Write only through `add_cell.py` (validated). Regenerate the views with `python build_views.py`.
Created 2026-10-12. What was ingested at creation is listed in `INGEST_LOG.md`.

## Fields (all required unless marked optional)

| field | type | meaning |
|---|---|---|
| id | str (optional on input; auto `Cnnnn` if absent) | stable id; may be set by the caller (e.g. `S37-E2`). Unique. |
| hash | `sha256-37` `sha256-38` `sha3-r5` `sha3-r6` `blake3-r2` `blake3-r3` `poseidon-r1` `poseidon-r2` | which target (Poseidon: Orchard P128Pow5T3, r = number of partial rounds; universe group PO in coverage.py: round x lane x layer x Q1..Q4 plus families LINE POLY ROOT LEDGER MEM PREM JUDGE MACHINE ALT DOOR; name answered cells as `universe cell <hash>|<loc>|<object>|<Q>` in notes) |
| row_i, row_j | int or null | source row and reader row (state rows -4..36 for sha256; null for non-grid objects) |
| object | str | short name, e.g. `row16 rel A16[8]^A16[17]`, `W22 exact set`, `rows 18/19 parities` |
| question | str | what the cell asks |
| labels | list | subset of `N D X C S I B P K E Z 0` (ATLAS37 legend: N neutral, D direct state read, X direct schedule tap, C carry-coupled, S selector, I invertible, B branching, P parity collapse, K killed fake freedom, E exact event looser than cells, Z tested no gain, 0 proved constant) |
| status | see below | |
| number | str | exact count, or gain bits with interval, as written by the producer |
| source | str | who produced the number (see Sources) |
| own_test | bool | true only if WE ran a test on our own code/data that produced this number or verdict |
| evidence | str | file path(s), relative to the workspace |
| date | `YYYY-MM-DD` | |
| lever | bool | true if the cell is (or was claimed to be) a gain lever |
| gain_bits | number or null | gain in bits, POSITIVE = saving (LEVERS.md writes savings as negative). Basis in `gain_basis`. |
| notes | str | caveats, conflicts, how it was ingested |

Optional fields: `held_fixed` (str: what the test held fixed - inputs, rows, words, parameters), `reopen_if` (str: the result that would justify reopening the cell), `topic` (comparison key; records with the same topic and different `number` are listed in CONTRADICTIONS.md), `gain_basis` (`q3` bits of probability, `T` log2 time, `S` memory-rule score, `count`), `potential_bits` and `prior` (0..1; the ingestor's estimates for OPEN cells, `EV = potential_bits * prior`; estimates, not measurements), `confirmed_by` (list of ids of own_test=true records that reproduce an outside number), `supersedes` (list of existing record ids that this record closes; see Supersession), `kind` (only `supersession`, see below).

## Supersession (closing old OPEN rows without editing the store)

The store is append-only, so an OPEN or CLAIMED-UNTESTED row is never edited or deleted. A later record that answers it names the old ids in `supersedes` (non-empty list; each id must already exist; no self-reference). `build_views.py` then treats every superseded id as closed: it is removed from the OPEN.md ranking and listed in OPEN.md section "Superseded" with the superseding id, moved to a "Superseded levers" section in LEVER_CELLS.md, tagged in CONTRADICTIONS.md, left out of the sha256-37 grid in MATRIX.md, and counted in MATRIX.md's "superseded" column (the status counts themselves are unchanged). Use it only for a full close; if the new record answers only part of the old question, leave the old row OPEN and say what remains in notes.

For records already written without the field (the closure was only in the `notes` text), append a bookkeeping record: `kind: "supersession"`, `id` = `<superseding id>-SUP`, `supersedes` = the old ids, all other required fields filled as inert placeholders (status COMPUTED, own_test false, lever false, number `n/a`). Views exclude `kind=supersession` records from every count and list; other readers of CELLS.jsonl see an ordinary record with own_test=false. `migrate_supersede_2026-10-13.py` is the first such backfill (11 records, 20 old ids). Normal path from now on: put `supersedes` on the new record itself.

## Status rule

| status | meaning |
|---|---|
| BEDROCK | proved or exhaustively counted; nothing to redo |
| COMPUTED | exact computation (automaton, DP, ledger arithmetic) |
| SAMPLED | measured by sampling, with an interval |
| LOCAL_ONLY | true for a window or prefix only, not checked on the full path |
| CLAIMED-UNTESTED | an outside model (Grok L/R/cloud, GPT 5.5, Luna cloud, Astra, Sol) says so; we have not tested it |
| KILLED | closed by a number. **Only with own_test=true.** |
| OPEN | not tested |

Enforced by `add_cell.py`:
1. `KILLED` requires `own_test=true`. An outside claim of "closed" enters as `CLAIMED-UNTESTED` (write "claimed closed" in notes) until our own test confirms it; then add a new own_test record with status KILLED and point the old one at it via `confirmed_by`.
2. A record from an outside source with `own_test=false` must be `CLAIMED-UNTESTED` or `OPEN`, unless `confirmed_by` names existing own_test=true records that reproduce the number.
3. `lever=true` records should carry `gain_bits` and `gain_basis` where a number exists.

## Sources (use these strings; free text after a colon is allowed)

Ours: `our trail lab`, `our workflow: <name>`, `Luna local`, `main session`.
Outside: `Luna cloud`, `Grok left`, `Grok right`, `Grok cloud`, `GPT 5.5`, `Astra`, `Sol cloud`.

## Adding a record

    python add_cell.py --json "{...}"
    python add_cell.py --file one_record.json

## Views (generated, do not edit)

- `OPEN.md`: OPEN and CLAIMED-UNTESTED cells ranked by EV, then row.
- `LEVER_CELLS.md`: all lever cells with gain, alive first, killed after.
- `MATRIX.md`: per-hash status counts, plus the sha256-37 grid of best status per (i, j).
- `CONTRADICTIONS.md`: same topic, different numbers.
- ATLAS37.md is still produced by `research/tools/traillab/atlas37_gen.py`, whose evidence table is hard-coded. `build_views.py` runs it only if the generator reads CELLS.jsonl (it does not yet; a note goes into MATRIX.md).

## Memory (added 10-13: "we need to know how much memory each lever, dig, row action takes")
Optional field `peak_mem` (str): peak memory the action implies INCLUDING preprocessing/precompute/advice, as `<log2 bytes> MEASURED|ESTIMATED <basis>` or `0 FREE` (checked on the fly, no stored table) or `UNKNOWN`. Back-fill for existing cells lives in `MEMORY.jsonl` (one `{id, peak_mem_log2, tag, kind, basis}` per cell; tag FREE / FITS-2^20 / BIG / UNKNOWN). Every new cell should carry `peak_mem`.
