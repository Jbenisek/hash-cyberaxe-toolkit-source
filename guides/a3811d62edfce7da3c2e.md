# exp steps

Source: `research/dig/incoming3/blake3-r3-U46/work/exp_steps.py`

Public SHA-256: `402f092695a39eeded4ff7b69b88b9214e49ff5c88c996fa183b40b805b69f14`

## Purpose recorded in the source

exp_steps.py - deterministic part of the blake3-r3 step/word scan. Writes steps_out.json and words_out.json.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "b3scan",
  "fractions",
  "json",
  "math",
  "numpy",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "ih_tail",
    "line": 14,
    "arguments": [
      "n",
      "x"
    ],
    "doc": "P(sum of n iid U[0,1) >= x), exact Fraction; x Fraction."
  },
  {
    "name": "per_step",
    "line": 29,
    "arguments": [
      "tr",
      "tag"
    ],
    "doc": ""
  },
  {
    "name": "variant_row",
    "line": 34,
    "arguments": [
      "label"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 43,
    "arguments": [],
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
