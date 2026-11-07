# appA

Source: `research/blake3_r3/bitslice/appA.py`

Public SHA-256: `1a1f7520f81f29c4db93e259977e91ab774924a7464a7ca743cbc03947acfe63`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "fractions",
  "math"
]
```

## Entry points

```json
[
  {
    "name": "inflight_m",
    "line": 15,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "plan",
    "line": 29,
    "arguments": [
      "Tp"
    ],
    "doc": ""
  },
  {
    "name": "tail_log2",
    "line": 39,
    "arguments": [
      "mean",
      "k"
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
