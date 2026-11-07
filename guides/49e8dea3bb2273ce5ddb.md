# k3recs

Source: `research/newpaths/untried/combo-finder/k3recs.py`

Public SHA-256: `483bc0c64a3de47384b5e72fe8dae14a79e03816ceb521924c34916fe49d1815`

## Purpose recorded in the source

Summarise K3 solution records (A delta D nsol hit) from k3gpu: distinct deltas, 2-adic valuations,
per-delta multiplicity.  Usage: python k3recs.py FILE

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "collections",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "v2",
    "line": 9,
    "arguments": [
      "x"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/combo-finder/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
