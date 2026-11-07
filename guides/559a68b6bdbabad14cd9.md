# mk5

Source: `research/blake3_r5/compact/mk5.py`

Public SHA-256: `a393c1adcf5c40d3668b89cdbfbd0cc88b004d785424ac52db67ae6b89b52317`

## Purpose recorded in the source

Retarget the copied r7 compact build files to 5 rounds (text substitutions; run once).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "re",
  "sys"
]
```

## Read alongside

- research/blake3_r5/compact/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
