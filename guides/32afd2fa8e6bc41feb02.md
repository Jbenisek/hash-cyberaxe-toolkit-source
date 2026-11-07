# Self-contained exact ledger: integers and Fractions only; it imports no

Source: `research/dig/incoming2/sha3-r5-G02-U01/work/ledger_extracted.py`

Public SHA-256: `ff97201ff9b5aa3f615db0e8d8ecb17cdbec1419701bbd08d2a46379b025734b`

## Purpose recorded in the source

Self-contained exact ledger: integers and Fractions only; it imports no
experiment source and reads no file.  The base total is 4efa18a8's governing
total, which already charges every inherited row (A, B1, B2, C, D,
development item 26, E1, E2).  Rows (a)-(c) are 39ff21c4's and 6938d3fb's,
unchanged; (d) is 6938d3fb's row at the shipped key-word layout; (e) and (f)
are new.  All row values are primitives (1355 per target unit).
(a) online connector coin words (time only)
(b) replay test: 751 executed attempts repriced, 185 unexecuted slots removed
(c) coin words of G2's 2,176 and self-tests C, D's 96 + 91 attempts
(d) per-level key words at the layout keywords() builds (KOFF, 9 keys per
    word below level 64, 10 per word at level 64)

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
    "name": "level_words",
    "line": 30,
    "arguments": [
      "NBL"
    ],
    "doc": ""
  },
  {
    "name": "cert",
    "line": 77,
    "arguments": [
      "n"
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
