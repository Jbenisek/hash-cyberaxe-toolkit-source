# appA

Source: `research/blake3_r7/compact/appA.py`

Public SHA-256: `a26d0f68ea03f557da6d5a0b50ff78b4a4be9367f937640ca93dbfa1d007e649`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "decimal",
  "fractions",
  "math"
]
```

## Entry points

```json
[
  {
    "name": "tail_log2",
    "line": 21,
    "arguments": [
      "mean",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "plower",
    "line": 25,
    "arguments": [
      "Tp",
      "q"
    ],
    "doc": ""
  },
  {
    "name": "plan_tp",
    "line": 52,
    "arguments": [
      "Tp"
    ],
    "doc": ""
  },
  {
    "name": "certify",
    "line": 64,
    "arguments": [
      "Tp",
      "B"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r7/compact/RESULT.md
- research/blake3_r7/compact/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
