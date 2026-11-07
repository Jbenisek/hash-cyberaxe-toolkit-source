# diag

Source: `research/newpaths/untried/ctr_alg/diag.py`

Public SHA-256: `55ff3209f3f1eda41d71838ab0e224650dad46e773b0f6bc591b0c36eb05d2ea`

## Purpose recorded in the source

diag.py (untried/ctr_alg; research only) - two checks behind e3sat.py.
(1) Plant feasibility for the beta* outcomes: Lipmaa-Moriai xdp+ weights of condition (1) [(q + h1) vs (q + h1^eta)]
    and of condition (3) given (1),(2) [(g1 + h2) vs (g1^G + h2^dh2), dh2 = ror(eta ^ eps, 8)], plus a sampled rate.
(2) Every kissat counter on one real system (sys00.cnf written by e3sat.py), to see where its work is counted.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "e3solve",
  "os",
  "random",
  "subprocess",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "lm",
    "line": 16,
    "arguments": [
      "a",
      "b",
      "g"
    ],
    "doc": "xdp+(a, b -> g): None if impossible, else weight w (probability 2^-w)."
  }
]
```

## Read alongside

- research/newpaths/untried/ctr_alg/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
