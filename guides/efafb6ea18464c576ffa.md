# gen frames

Source: `research/fifties/angles/a6/gen_frames.py`

Public SHA-256: `1a377c95deb66e440c33e71ef25b5eb4387e610f7947c55c850e75714f1b7fca`

## Purpose recorded in the source

A6: sample per-frame (outer step) constants of the pkg16f counter batch; write consts.h, frames file, a reference check.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "halfsearch",
  "hashlib",
  "os",
  "struct",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "key_of",
    "line": 10,
    "arguments": [
      "o"
    ],
    "doc": "The six frame words the counter batch (ctr_batch) reads, plus e1 for rule A: Y12, Q=-Y1-w12, w5, C2.b1, C2.c1, e1."
  },
  {
    "name": "lane",
    "line": 14,
    "arguments": [
      "key",
      "c1"
    ],
    "doc": "One member of the per-frame table, as ctr_batch computes it: (word, rule A pass)."
  },
  {
    "name": "eight_of",
    "line": 30,
    "arguments": [
      "seed",
      "i"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 34,
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
