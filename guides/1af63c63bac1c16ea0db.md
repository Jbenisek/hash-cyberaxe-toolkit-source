# ref check

Source: `research/blake3_r6/b6v2/ext/ref_check.py`

Public SHA-256: `dda475690948d63778aa436aa9daa4c6056989453320d9c843f20a9815b8827b`

## Purpose recorded in the source

External check (not shipped): the program's scalar digest vs the organizer reference verifier/blake3.py at 3 rounds first, then 4 (target) and 7, and at 7 rounds
both vs the blake3 library (pip blake3 1.0.11).   usage: ref_check.py <organizer-repo-dir> <experiments-dir>

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "blake3",
  "bsrho",
  "importlib.util",
  "random",
  "struct",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "mine",
    "line": 9,
    "arguments": [
      "msg",
      "rounds"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r6/b6v2/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
