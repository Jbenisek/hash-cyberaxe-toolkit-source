# t1 q1 chi2

Source: `research/dig/incoming/sha3-r6-U02/work/t1_q1_chi2.py`

Public SHA-256: `879f0e8264b3b9d537ad20fedf834f9cae7ecdcc262c977f3789711f6f65dd78`

## Purpose recorded in the source

affinity in z: second difference for random z pairs
words: (lane, bit) positions where any slice differs
slice-uniform: for a bit position, all slices differ (all ones) or none
chi2 input diff rows

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "kk6",
  "numpy",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "A2of",
    "line": 5,
    "arguments": [
      "L"
    ],
    "doc": ""
  },
  {
    "name": "O2Pof",
    "line": 6,
    "arguments": [
      "A2"
    ],
    "doc": ""
  },
  {
    "name": "run",
    "line": 8,
    "arguments": [
      "drop",
      "N",
      "seed",
      "verbose"
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
