# pins toy

Source: `research/newpaths/blake2/pins_toy.py`

Public SHA-256: `2817b54aa71d0874fac14861d8bb048e9a0a5bae441e9fa3e00bd0875e7b87de`

## Purpose recorded in the source

Pinnable output patterns of one G call (COMPUTED, toy widths).  The board pins all six inputs of C3 so that a
message difference in x (m4) leaves only outputs a, c different - a value-dependent transition that no XOR-linear
characteristic has (board_lin.txt).  Here: for a modular difference delta in x only, in y only, or in both, the
frequency over random inputs of every zero-pattern of the output difference (which of a2, b2, c2, d2 are equal).
A pattern with frequency > 0 can be pinned (choose constants from a hit); frequency 0 over many samples and an
exact argument = impossible.  Usage: python -B pins_toy.py N

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "rots",
    "line": 13,
    "arguments": [
      "w"
    ],
    "doc": ""
  },
  {
    "name": "vrotr",
    "line": 17,
    "arguments": [
      "z",
      "r",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "vG",
    "line": 22,
    "arguments": [
      "a",
      "b",
      "c",
      "d",
      "x",
      "y",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 30,
    "arguments": [
      "N"
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
