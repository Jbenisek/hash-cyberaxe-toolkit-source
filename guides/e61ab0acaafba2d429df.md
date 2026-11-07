# make md

Source: `research/fifties/rates/make_md.py`

Public SHA-256: `86c98c7c91050ac583977f4602f51f4d186e736eeb22e1995f933eb54e740c23`

## Purpose recorded in the source

Write RATES.md from rates_analysis.json (analyze.py output).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "os"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
