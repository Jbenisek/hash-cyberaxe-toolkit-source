# check

Source: `research/blake3_r5/b8r5/gen_c/native/check.py`

Public SHA-256: `83c2c8ef7207591a07a96d9b87a7acbaa1ac03f40c608039e835f72f7be59523`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "hashlib",
  "os",
  "struct",
  "sys"
]
```

## Read alongside

- research/blake3_r5/b8r5/proof_t8.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
