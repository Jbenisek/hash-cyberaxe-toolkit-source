# common

Source: `research/blake3_r3/dig_scan/common.py`

Public SHA-256: `c759fcb54406503eac727888f7e11ff30278ebc712445ac2984160414ebeaf53`

## Purpose recorded in the source

Shared helpers for the blake3-r3 dig scan (own code). Imports the filed rho.py only as a library (own code).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "fractions",
  "hashlib",
  "math",
  "os",
  "re",
  "rho",
  "sys",
  "verifier"
]
```

## Entry points

```json
[
  {
    "name": "validate",
    "line": 12,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "led",
    "line": 30,
    "arguments": [
      "ph",
      "stage1",
      "U",
      "loop",
      "d",
      "lam",
      "inflight",
      "cutloss",
      "kappa",
      "extra",
      "st2",
      "tmax",
      "s1",
      "group",
      "lanes",
      "events_ops",
      "recov_fixed",
      "ndp_scale"
    ],
    "doc": "Copy of rho.ledger(256) with every knob exposed. Returns dict with total ops, time_log2, memory bytes, score."
  },
  {
    "name": "base",
    "line": 61,
    "arguments": [],
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
