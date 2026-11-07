# q12

Source: `research/dig/incoming/sha3-r6-U01/work/q12.py`

Public SHA-256: `da6bb145667c508bb847ba1fc91e344e69172bd1a89490e513edb58207131a83`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "random",
  "sha3lab",
  "statistics",
  "sys",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "setup",
    "line": 6,
    "arguments": [
      "fmt"
    ],
    "doc": ""
  },
  {
    "name": "eq_of",
    "line": 26,
    "arguments": [
      "F",
      "c"
    ],
    "doc": ""
  },
  {
    "name": "measure",
    "line": 31,
    "arguments": [
      "F",
      "dirs",
      "m",
      "nrandz",
      "rng",
      "deep"
    ],
    "doc": ""
  },
  {
    "name": "build_sys",
    "line": 87,
    "arguments": [
      "F",
      "conds",
      "skip"
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
