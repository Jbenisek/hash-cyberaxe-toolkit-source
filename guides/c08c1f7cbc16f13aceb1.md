# mkcert

Source: `research/poseidon/orchard/twofam_r2/mkcert.py`

Public SHA-256: `f8f7e0a8905870e10cd1df0e7d5ab634534cc8e628034469a735981cd0f2f997`

## Purpose recorded in the source

Build certrun.c (certificate-run driver) from twofam.c.  Not part of the charged program.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Entry points

```json
[
  {
    "name": "rep",
    "line": 6,
    "arguments": [
      "a",
      "b"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/orchard/twofam_r2/proof_template.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
