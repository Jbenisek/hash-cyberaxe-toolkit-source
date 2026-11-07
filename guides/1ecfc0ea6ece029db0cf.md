# find W1,W2 distinct with ell(W1)=ell(W2): roots of (ell(W)-ell(W1))/(W-W1)

Source: `research/dig/incoming4/_tools/exp_lane0.py`

Public SHA-256: `208a40fafa0946d096eceee5c9036b94341aad6cfb1cc43bc37d11e91aa3562a`

## Purpose recorded in the source

find W1,W2 distinct with ell(W1)=ell(W2): roots of (ell(W)-ell(W1))/(W-W1)
check: P1 S-box input lane 0 equal, and difference after P1 is M(0,d1,d2)
full digest equal? (expect no)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "polylib",
  "random",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "state3",
    "line": 29,
    "arguments": [
      "W"
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
