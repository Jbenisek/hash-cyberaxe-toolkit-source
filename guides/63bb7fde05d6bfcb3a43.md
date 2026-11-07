# nums

Source: `research/blake3_r4/bsel/roll/nums.py`

Public SHA-256: `dffb0e08dfc7a762ac0bca75cc00abf5cc4355463c9650034143f86aacd1803d`

## Purpose recorded in the source

Print the select-gate program numbers of one row.  usage: python -B nums.py <row dir>

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "bsrho",
  "json",
  "math",
  "os",
  "sys",
  "time"
]
```

## Read alongside

- research/blake3_r4/bsel/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
