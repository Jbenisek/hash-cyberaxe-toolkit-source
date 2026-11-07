# direct: no chunk tables; per group 32 l x 6 ops + 8 = 200 ops (our bound), same survivors

Source: `research/dig/incoming2/sha256-37-G02-U03/work/scen.py`

Public SHA-256: `52901444cdf21ca8be429481da090b7b18cd048c7663cfc8ae61523fac133c38`

## Purpose recorded in the source

direct: no chunk tables; per group 32 l x 6 ops + 8 = 200 ops (our bound), same survivors
no filter at all: every l exact-tested for every lane
ideal oracle: free membership, only rare path
HI table (9th condition bit 30): extra probe ops e per group; PNZ, MU halved approx (exact value unknown: 9 cond -> MU=32/512)
pair list materialised: store+load per group

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "copy",
  "fractions",
  "json",
  "lowm_copy",
  "math"
]
```

## Entry points

```json
[
  {
    "name": "run",
    "line": 5,
    "arguments": [
      "name",
      "mem"
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
