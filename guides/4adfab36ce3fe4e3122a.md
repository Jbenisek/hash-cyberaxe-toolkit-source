# fix E

Source: `research/pkg10/fix_E.py`

Public SHA-256: `6a136dd4de8eac3456236613a8d048952521ed3a38b5bd5d1e2f54b9487556c3`

## Purpose recorded in the source

Make every statement of the stage-2 budget E match the program: E = STAGE_2_BUDGET = RUN_PAIRS * 2,341 >> 8,
one in 32 of the representative words of J pairs; neighbour words have their own budget S. Exact-once replacements.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
