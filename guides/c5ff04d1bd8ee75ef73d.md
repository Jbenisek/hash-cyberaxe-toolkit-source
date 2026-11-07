# sqrt(-1): g^((p-1)/4)

Source: `research/poseidon/levels/U6/exp3.py`

Public SHA-256: `efa4228884b46b08d74a64907a8a5d59ffac883697f82f1a8ee86cb1d8fbf557`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "collections",
  "common",
  "itertools",
  "mpmath"
]
```

## Entry points

```json
[
  {
    "name": "chi2p",
    "line": 7,
    "arguments": [
      "obs",
      "exp"
    ],
    "doc": ""
  },
  {
    "name": "rep",
    "line": 58,
    "arguments": [
      "name",
      "vals"
    ],
    "doc": ""
  },
  {
    "name": "smooth_order",
    "line": 88,
    "arguments": [
      "a"
    ],
    "doc": ""
  },
  {
    "name": "fact",
    "line": 94,
    "arguments": [
      "n"
    ],
    "doc": ""
  },
  {
    "name": "cross",
    "line": 111,
    "arguments": [
      "a",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "det3",
    "line": 112,
    "arguments": [
      "a",
      "b",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "adj",
    "line": 113,
    "arguments": [
      "A"
    ],
    "doc": ""
  },
  {
    "name": "mpow",
    "line": 120,
    "arguments": [
      "k"
    ],
    "doc": ""
  },
  {
    "name": "gauss",
    "line": 149,
    "arguments": [
      "a",
      "mod"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
