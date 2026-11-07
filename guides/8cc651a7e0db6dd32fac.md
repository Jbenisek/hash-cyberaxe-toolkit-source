# exp root

Source: `research/dig/incoming4/_tools/exp_root.py`

Public SHA-256: `0daa05622b2c1563a4484b7e0f547e44847677ca9c4cec178df8b2888ef39de8`

## Purpose recorded in the source

p = 1 mod 4: use flint poly sqrt? use Tonelli-Shanks

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "polylib",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "sqrt_mod",
    "line": 7,
    "arguments": [
      "x"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/dig/SCHEMA.md
- research/dig/d243_w6full_result_record.json
- research/dig/d253_b3m_proof_release_audit.json
- research/dig/rec_d243_poseidon_d15625_result.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
