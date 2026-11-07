# pooled zero-cell advantages for D (both streams), the 'lean toward 0' summary

Source: `research/fifties/perspectives/onescomp/replicate.py`

Public SHA-256: `f833283d067cbe2fc41cdaab9c2bb65f8c35f41fdd91acdd1935e0624c15b421`

## Purpose recorded in the source

Replication on STREAM 2 (fresh seeds) of (a) the pre-registered hypotheses in prereg.json and (b) every test that was
Bonferroni-significant on STREAM 1. Each stream is compared with its own control stream. Writes replicate_out.txt.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "numpy",
  "oclib",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "say",
    "line": 14,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/fifties/perspectives/onescomp/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
