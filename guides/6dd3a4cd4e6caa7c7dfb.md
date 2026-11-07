# validate

Source: `research/dig/incoming4/_pr2scan/validate.py`

Public SHA-256: `8f90777419ed395873ba996f9c0579398bbbb11adeab9508e90cde680f59ced1`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "copy",
  "pos_scan_lib",
  "sys",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "variant",
    "line": 4,
    "arguments": [
      "specs",
      "kind",
      "idx",
      "lane"
    ],
    "doc": ""
  },
  {
    "name": "ntt_degree",
    "line": 14,
    "arguments": [
      "alpha",
      "beta",
      "specs",
      "deg_bound_pow"
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
