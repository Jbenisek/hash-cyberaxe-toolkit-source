# verify collision

Source: `research/poseidon/orchard/exec_r2c/src/verify_collision.py`

Public SHA-256: `79a03418268b60b9d19a39899fbcc10486d04893fd8411d08ec02ad80821d566`

## Purpose recorded in the source

Independent check of collision lines printed by lean_attack (reads log files given on the command line).
Uses (1) poseidon_ref.hash_reduced (big-int reference, 11/11 public vectors) and (2) the organizer's verifier.poseidon.digest
from the read-only clone (messages: nk, rho as 32-byte little-endian each).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "poseidon_ref",
  "re",
  "sys",
  "verifier.hash_functions"
]
```

## Entry points

```json
[
  {
    "name": "parse",
    "line": 14,
    "arguments": [
      "path"
    ],
    "doc": ""
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
