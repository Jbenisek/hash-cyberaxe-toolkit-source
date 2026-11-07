# Organizer reference op count of blake3 _compress at 1,2,3,7 rounds by operation type (their Word-counter method, run on THEIR verifier only).

Source: `research/dig/incoming3/blake3-r3-U75/work/orgcount.py`

Public SHA-256: `7d69765268f46f53de7fe9ff3b665b6cbc4cf0a847c0538c7784b4016d5cbee3`

## Purpose recorded in the source

Organizer reference op count of blake3 _compress at 1,2,3,7 rounds by operation type (their Word-counter method, run on THEIR verifier only).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "collections",
  "operator",
  "sys",
  "verifier"
]
```

## Entry points

```json
[
  {
    "name": "mk",
    "line": 7,
    "arguments": [
      "name",
      "op"
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
