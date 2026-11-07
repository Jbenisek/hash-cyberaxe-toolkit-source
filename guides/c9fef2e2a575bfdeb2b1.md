# zero cells with big E

Source: `research/poseidon/levels/J3/cmp.py`

Public SHA-256: `659b7ae37b0715218d97ae04c7bc371bab0ceadc7eb8b0e698227363a468c2bc`

## Purpose recorded in the source

zero cells with big E

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "math",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "z",
    "line": 3,
    "arguments": [
      "c",
      "e"
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
