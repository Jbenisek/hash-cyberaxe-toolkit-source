# ledger arithmetic for class-table alternatives. Inputs are the shipped ledger/memory numbers of a0lean38 (ledger.out of our G02 scan): per-first-block terms.

Source: `research/dig/incoming2/sha256-38-G04-U04/work/scan4.py`

Public SHA-256: `5628f0a6a8a836a656ec9418bb8d4c1315825ff7cdb4494fb2161b001af9f3de`

## Purpose recorded in the source

ledger arithmetic for class-table alternatives. Inputs are the shipped ledger/memory numbers of a0lean38 (ledger.out of our G02 scan): per-first-block terms.
memory per class
no grouping: every one of the 345600 variants tests its own W7 (16.64 ops each, 1497.66/90 per class test), good variants then need >=0 further ops
gate by classes but bit-slice: each class tested once = shipped
cost split

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "a0lean38",
  "json",
  "math"
]
```

## Entry points

```json
[
  {
    "name": "dT",
    "line": 12,
    "arguments": [
      "K",
      "fixed_",
      "perK_"
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
