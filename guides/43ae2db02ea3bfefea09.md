# G5: A1+B2=0 ; G6: A2+B3=0 ; G7: A3+B0=0

Source: `research/blake3_r3/lastblock/construct2.py`

Public SHA-256: `0b49caf06de7fe59b2d596f09dfbc9a2838e83fed9b3ad6699825bc747a0b444`

## Purpose recorded in the source

G5: A1+B2=0 ; G6: A2+B3=0 ; G7: A3+B0=0

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "numpy"
]
```

## Entry points

```json
[
  {
    "name": "sample",
    "line": 5,
    "arguments": [
      "j"
    ],
    "doc": ""
  },
  {
    "name": "join",
    "line": 10,
    "arguments": [
      "keys_left",
      "keys_right"
    ],
    "doc": "pairs (i,k) with keys_left[i]==keys_right[k]"
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
