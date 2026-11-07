# apply h16

Source: `research/blake3_r7/bsel/apply_h16.py`

Public SHA-256: `0e5a55bc948d5337a31ac371c5229249a659eb80463b068ca4ecfa9c3f0c5834`

## Purpose recorded in the source

apply_h16.py : B3R7 H16 = u5b + 64-bit table slots (47-bit key, 17-bit trail number; the slot layout of TheTradoor 09fe5fcd, the 47-bit key of
b1e6de75) + age cap 16 L. Constants in bsrho.py and appA.py, every sentence that names the entry layout in proof_t.md, note_t.md, build_all.py.
Each replacement must match exactly once.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os"
]
```

## Entry points

```json
[
  {
    "name": "edit",
    "line": 8,
    "arguments": [
      "rel",
      "pairs"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/blake3_r7/bsel/RESULT.md
- research/blake3_r7/bsel/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
