# cvdiff

Source: `research/newpaths/counter_swing/around/cvdiff.py`

Public SHA-256: `dc79dd8dd64d860d489610a040221b880b0be1a01448783e142469e744f3df92`

## Purpose recorded in the source

cvdiff.py - chaining-value differences as the difference source (the multi-block / two-block "swing").
A non-first block of a chunk starts from a chained CV h. Two messages whose chunks differ in an earlier block
reach the last block with h != h'. Lemma G1 (b and c inputs of a G call are functions of its output) forces
h4..h7 = h'4..h'7; a difference in h0..h3 (the a inputs) is absorbed by the column's x word alone.
Also the CHUNK_START case: a multi-block last block (flags 2, cv = chained h) vs a one-block last chunk
(flags 3, cv = IV) at the same position; it needs h4..h7 = IV4..IV7 (planted here, costs 2^128 for real).
Prints round-0 equality, the round-1 message differences and the dY pattern at w = 32, and pattern rates at w = 8.
Run: python -B cvdiff.py

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "tb3"
]
```

## Entry points

```json
[
  {
    "name": "absorb_a_d",
    "line": 18,
    "arguments": [
      "toy",
      "vb",
      "vo",
      "m",
      "cols"
    ],
    "doc": "columns may differ in a (v[c]) and/or d (v[c+12]); b, c must be equal."
  },
  {
    "name": "run",
    "line": 31,
    "arguments": [
      "w",
      "n",
      "batches",
      "cfg",
      "rng"
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
