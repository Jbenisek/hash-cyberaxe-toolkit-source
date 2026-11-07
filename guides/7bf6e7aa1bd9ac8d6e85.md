# freeze combinations among chain words (ops only)

Source: `research/dig/incoming3/blake3-r3-U46/work/exp_words.py`

Public SHA-256: `316412f4bc9f6d0a4adbcf148d01454f64599c80e5a391970567c5b331e82c62`

## Purpose recorded in the source

exp_words.py - message words m0..m11 of the blake3-r3 circuit: uses, op deltas under changes, diffusion. -> words_out.json

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "b3scan",
  "json",
  "numpy",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "tl",
    "line": 12,
    "arguments": [
      "o"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/dig/incoming3/D414-SHA3-R6-141-PROOF-ERRATA-20261014.json
- research/dig/incoming3/D415-SHA3-R6-141-PROOF-REFRESH-DRAFT-20261014.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
