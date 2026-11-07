# gen ref

Source: `research/blake3_r7/b8/gen_c/gen_ref.py`

Public SHA-256: `e6cdd4a411804b73afb98a67c421d378f1a52d249894e336b99ed03c34f70dae`

## Purpose recorded in the source

Reference listing of the Python generator (rolled_ref.listing) for the C port to match: ref_program.txt (one line per instruction: op dst a b, none = 65535), ref_summary.txt.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "hashlib",
  "os",
  "rolled_ref",
  "sys"
]
```

## Read alongside

- research/blake3_r7/b8/proof_t8.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
