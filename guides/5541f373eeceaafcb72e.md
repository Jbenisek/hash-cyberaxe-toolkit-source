# e4 capacity

Source: `research/poseidon/levels/U10/e4_capacity.py`

Public SHA-256: `990d62ddc5958a6e87c23a60c7ea8d003312d895090d1fb28df376990691ddf9`

## Purpose recorded in the source

U10 Q4: scan all capacity values at q=257 (r=1,2) and q=769 (r=1).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "time",
  "toylib"
]
```

## Entry points

```json
[
  {
    "name": "run",
    "line": 5,
    "arguments": [
      "q",
      "r",
      "seed",
      "caps"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
