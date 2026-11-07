# export38.py - scout2-4 (hole 4, Step-3 relaxation).  Reads ONLY the filed r38 package module

Source: `research/sha256grid/scout2-4/export38.py`

Public SHA-256: `65528ace133b86ad163bd7b0edf15d85d6a894218c726bab44967886f28d71df`

## Purpose recorded in the source

export38.py - scout2-4 (hole 4, Step-3 relaxation).  Reads ONLY the filed r38 package module
  research/tools/build_pkg/scratch/pkgR38a/base/experiments/vt38.py  (imported read-only, no side effects)
and writes consts38.h for smc38r.c: characteristic cells (A, E, W), '+' masks, two-bit conditions keyed at the
later row, the published semi-free-start pair (rows -4..37 of both members, W0..W37), G (32 words), and the 512
embedded variants with W8, W9, W10 of both members.  Also prints the published modular differences of rows 16..37.
usage: python -B export38.py
self-check: the published pair collides and follows every cell of rows 16..37
two-bit conditions (member x), keyed at max row
published pair, rows -4..37 (index i+4), W0..W37

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "importlib.util",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "arr",
    "line": 18,
    "arguments": [
      "name",
      "vals",
      "t"
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
