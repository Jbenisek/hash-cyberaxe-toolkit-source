# run gen

Source: `research/blake3_r7/b8/gen_c/run_gen.py`

Public SHA-256: `b0f9dc77d403f10891ecc6ed600e8521b5c81a53342f538278990994cfea7e29`

## Purpose recorded in the source

Run gen.wasm in the 1 MiB VM and compare with the Python reference (ref_program.txt, ref_summary.txt).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "hashlib",
  "json",
  "os",
  "struct",
  "sys",
  "vm_r7"
]
```

## Read alongside

- research/blake3_r7/b8/proof_t8.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
