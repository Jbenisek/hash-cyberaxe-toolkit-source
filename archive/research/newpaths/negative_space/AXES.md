# AXES: how each record is placed

Folder `research\newpaths\negative_space`. Written 2026-10-08. Research only: existing records were read and
re-coded. No experiment was run, nothing was filed, posted or cancelled, and nothing outside this folder was written.

Each record gets one value on six axes. The value is where its **key idea** sits, not everything it touches. One
context tag (BASE) says which construction the record builds on. Coding is judgement (GUESS) unless the source
says it outright.

| axis | codes | meaning |
|---|---|---|
| FREE (source of freedom the key idea spends or adds) | `msg` | message words only (fixed IV, the pair's own free words) |
| | `len` | block-length field, used as the pair difference |
| | `ctr` | chunk counter: solved per trial, constant, or a difference |
| | `flag` | flags or node type (leaf, parent, root) |
| | `cv` | chaining value, prefix, block or tree position |
| | `const` | constants or targets chosen offline: pins, classes, cubes, outer-step selection |
| | `mem` | tables and precomputation |
| | `none` | no freedom added: measurement, convention, cost |
| PART (output part the idea acts on) | `A` / `B` / `AB` / `k` | digest half A (words 0,2,5,7; E0/E2), half B (words 1,3,4,6; E1/E3), all 256 bits, a few words |
| LAYER (where the idea acts) | `r0` `r1c` `r1d` `fold` `mode` `all` | round 0; round-1 columns (C calls, Y words); round-1 diagonals (E calls, e1/h1/d1); output fold; tree/chunk level; no single layer |
| TECH (technique family) | `trail` `gd` `join` `sym` `class` `canc` `alg` `heur` `cost` | differential trail; solving order, guess-and-determine, basis, message modification; birthday, list join, MITM; symmetry, invariants, rotational; statistical class selection, counting, filtering, staging; structural cancellation or absorption; algebraic, SAT, solver; heuristic or nature-inspired search; cost engineering or convention |
| RES (resolution) | `word` / `bit` | word-level or bit-level conditions |
| GOAL | `half` `resid` `samp` `coll` `cost` `tool` | free half-collision; raise the residual rate; family sampler for a birthday; full collision directly; cut cost per trial; evidence, bound or tool |
| BASE (context tag) | `fh` `ctr` `mode` `fam` `gen` `r1` | root free half (55/63 lineage); counter lever; mode-level placements; idea-1 family; generic whole-function; the 1-round track |

## Status (column `status` in records.csv)

- `alive`: an own score below 128 that is in use, filed, counted or derived, and not superseded. New records from
  today's `counter_next` and `counter_swing` outputs are alive only as DERIVED and unadjudicated.
- `dead`: closed, refuted, no gain, superseded, or proved impossible.
- `open`: logged but never run (GUESS score, "not run", "untested", "parked"). In the grids an open-only cell counts
  as untried.
- `n/a`: a concern (C1-C16) or a tool (V1-V10, I14, S14, L3, L8, X10). These are left out of the grids.

## Records

- The 170 catalogue records keep their ids, names and scores (`methods.csv`).
- X1-X13: today's `counter_next` and `counter_swing` output files. Those folders have no summary document yet, so
  only their printed results were used.
- K1-K10: CENSUS rows that the catalogue does not list (K7, K8 were folded into A11, F6, F7).
- Columns: `cost` is the own score or exact cost (blank when the record has no single number). `label` is the
  source's COMPUTED / DERIVED / GUESS tag.

## Rebuild

`python -B build.py` reads `catalogue\catalogue\methods.csv` (read-only). It writes `records.csv`, `cells.csv`
and `GRIDS.md` in this folder in under a second. The classification table sits at the top of build.py.
