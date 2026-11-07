# core

Source: `research/newpaths/shape_odd/core.py`

Public SHA-256: `3e3e4bd71da52484a6afe7a5178d05265967443d8c6122e2f5d19d1474900a81`

## Purpose recorded in the source

2-core of the guess-and-determine hypergraph (plain model, no tables).
Peeling: repeatedly remove a variable that occurs in exactly one remaining equation, together with that equation
(it can be solved LAST from that equation).  What remains is the unique 2-core: every remaining variable occurs in
>= 2 remaining equations.  Variables left with no equation ("stranded") must be guessed.
A 0-check order needs: guesses = freedom, and the guesses must break the whole core.
Usage: python core.py

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "gd_order",
  "itertools",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "core",
    "line": 16,
    "arguments": [
      "eqs",
      "const"
    ],
    "doc": ""
  },
  {
    "name": "report",
    "line": 40,
    "arguments": [
      "label",
      "eqs",
      "const"
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
