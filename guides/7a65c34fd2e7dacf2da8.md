# q8 cost table

Source: `research/poseidon/levels/U2/q8_cost_table.py`

Public SHA-256: `f114d0f5399eca3cd094bf6fb2bb9ec3b141f022634ef0bcc7a27f36d1320d6b`

## Purpose recorded in the source

Q8: degree vs S-box count vs multiplications per evaluation (r=1, r=2). Executed-operation counts from a counting field class.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "poseidon_ref",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "sbox",
    "line": 14,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "run",
    "line": 17,
    "arguments": [
      "r"
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
