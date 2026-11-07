# analyze3

Source: `research/newpaths/untried/s3-plane-degrees/analyze3.py`

Public SHA-256: `405f2aee081eaa0b2c7d245cbd656f03e367fc8e2697e88188c869c43d54ee02`

## Purpose recorded in the source

Round-3 'door' on special cosets: chi3 output bits that are AFFINE on a whole coset t + W40 (coset_k2: all 64 random
2-cube sums zero), explained by the chi3 input linear forms on the same coset (coset_k1: 64 random first derivatives):
chi3 out (x,y,z) = b(x) + (b(x+1)+1) b(x+2) is affine on the coset iff form(x+1) = 0, form(x+2) = 0 or form(x+1) = form(x+2).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "collections",
  "json",
  "numpy",
  "struct"
]
```

## Entry points

```json
[
  {
    "name": "P",
    "line": 11,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "readvec",
    "line": 13,
    "arguments": [
      "name"
    ],
    "doc": ""
  },
  {
    "name": "bits_of",
    "line": 21,
    "arguments": [
      "sums",
      "stage"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/s3-plane-degrees/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
