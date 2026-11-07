# pgates

Source: `research/blake3_r3/stack1020/work/pgates.py`

Public SHA-256: `8042a9872e91a98a0aee05557625f9ea311a50edc3835eeacd1467e5debff5fa`

## Purpose recorded in the source

Live gate count of the r4 MDFA step for a chosen constant prefix m0..m7 (inputs at m8..m15).
override: dict word-index -> value forced after the round-1 column step (upper-bound probe only).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "bsrho_mdfa",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "gates",
    "line": 8,
    "arguments": [
      "key",
      "override"
    ],
    "doc": ""
  },
  {
    "name": "colstate",
    "line": 35,
    "arguments": [
      "key"
    ],
    "doc": "Scalar state after the round-1 column step for prefix key."
  }
]
```

## Read alongside

- research/blake3_r3/stack1020/work/proof_1.md
- research/blake3_r3/stack1020/work/proof_2.md
- research/blake3_r3/stack1020/work/proof_3.md
- research/blake3_r3/stack1020/work/proof_4.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
