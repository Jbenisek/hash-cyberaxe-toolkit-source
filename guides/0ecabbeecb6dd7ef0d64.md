# Memory-free alternatives (Floyd, Brent) on a random mapping: evaluations to FIND A COLLISION PAIR (x != y, f(x)=f(y)),

Source: `research/dig/incoming3/blake3-r3-U79/work/cyc.py`

Public SHA-256: `1d9803b36ce8b193d4e7881e190e40fca68a283c2385adfbe6f20a31638787f1`

## Purpose recorded in the source

Memory-free alternatives (Floyd, Brent) on a random mapping: evaluations to FIND A COLLISION PAIR (x != y, f(x)=f(y)),
in units of sqrt(N); success within a budget E is P(total <= E). Compared with the filed program: Q = 0.99885 sqrt(N) evaluations for success 0.39.
Floyd
phase 2: find mu and the colliding pair
Brent
find mu: hare is lam ahead of tortoise from x0

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
    "name": "run",
    "line": 5,
    "arguments": [
      "logN",
      "T"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/dig/incoming3/D414-SHA3-R6-141-PROOF-ERRATA-20261014.json
- research/dig/incoming3/D415-SHA3-R6-141-PROOF-REFRESH-DRAFT-20261014.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
