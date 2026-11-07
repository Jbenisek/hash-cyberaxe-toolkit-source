# Full 2^32 scans (numpy, one process) for MOVERS.md.

Source: `research/fifties/movers/scan.py`

Public SHA-256: `b18282d2cf1a72e60d5191db2214d155088614ef9f67790c46eaf4d8647c35d3`

## Purpose recorded in the source

Full 2^32 scans (numpy, one process) for MOVERS.md.
Part 1: outer tuples sharing one constant tuple. With the 18 constants fixed, S7 and S3 are fixed; for each w6,
  S11 = ROL7(S7) ^ K3.b1(w6) and S3 = f(w6). Count all w6 with f(w6) = S3, rebuild each tuple, test Y4 in class.
Part 2: forward m = |image of K| for one constant tuple: preimage counts n of K(g0) for sampled g0; |Im|/2^32 = E[1/n].
Run: python -B scan.py [seed]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "halfsearch",
  "movers",
  "numpy",
  "random",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "nrol",
    "line": 15,
    "arguments": [
      "x",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "nror",
    "line": 16,
    "arguments": [
      "x",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "part1",
    "line": 19,
    "arguments": [
      "rnd",
      "steps"
    ],
    "doc": ""
  },
  {
    "name": "Kvec",
    "line": 44,
    "arguments": [
      "g",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "part2",
    "line": 61,
    "arguments": [
      "rnd",
      "tuples",
      "ntar"
    ],
    "doc": ""
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
