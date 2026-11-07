# ev

Source: `research/fifties/split_e3/ev.py`

Public SHA-256: `bbe8f0d8e7cae348231cb4f3365b1fb04ede8b7180d986519ba24d8bdddb55a2`

## Purpose recorded in the source

Exact evaluator of the outer system with counter 2 (T1 = v13 free) from pkg13/mitm/bits/rels.py relations, for a
design (forced F, free B, solved g): propagation order, the single check, pre/loop split, numeric solve,
CUDA code for the loop, and a full verification of a solution on the real 2-round compression (compress2).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "random",
  "rels",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 9,
    "arguments": [
      "x",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "wset",
    "line": 15,
    "arguments": [
      "r"
    ],
    "doc": ""
  },
  {
    "name": "order",
    "line": 17,
    "arguments": [
      "known"
    ],
    "doc": ""
  },
  {
    "name": "solve1",
    "line": 30,
    "arguments": [
      "r",
      "u",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "holds",
    "line": 41,
    "arguments": [
      "r",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "real_point",
    "line": 102,
    "arguments": [
      "rnd"
    ],
    "doc": ""
  },
  {
    "name": "c1_from_y14",
    "line": 106,
    "arguments": [
      "v",
      "y14"
    ],
    "doc": ""
  },
  {
    "name": "verify",
    "line": 110,
    "arguments": [
      "v",
      "F",
      "y14"
    ],
    "doc": "full check on the real 2-round compression of the two last-chunk blocks, counter T0 + 2^32*T1, flags 3."
  },
  {
    "name": "y14_of",
    "line": 125,
    "arguments": [
      "v"
    ],
    "doc": "Y14 of a real ctr_outer point for some trial: use cube member 0 of the old table to pick one."
  }
]
```

## Read alongside

- research/fifties/split_e3/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
