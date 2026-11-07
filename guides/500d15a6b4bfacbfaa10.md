# MACHINE.REGS Q2/Q3/Q4: register pressure of the filed 595-op batch (+4 filter ops), exact liveness; spill cost with Belady eviction

Source: `research/dig/incoming3/blake3-r3-U81/work/regs.py`

Public SHA-256: `e6ef18929efbdc6b12cdde77790e45f4e6b93688cae186fd78abbe41a9f3c3c0`

## Purpose recorded in the source

MACHINE.REGS Q2/Q3/Q4: register pressure of the filed 595-op batch (+4 filter ops), exact liveness; spill cost with Belady eviction
at R registers (loads and stores each charged 1 operation); greedy re-ordering as alternative.
filter on output word 0: f1=z0+K ; f2=f1&B ; compare-branch uses f2 (2 ops: charged as the "4" with the cmp+br counted as 2)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "common",
  "math",
  "re"
]
```

## Entry points

```json
[
  {
    "name": "liveness",
    "line": 16,
    "arguments": [
      "order"
    ],
    "doc": ""
  },
  {
    "name": "belady",
    "line": 31,
    "arguments": [
      "order",
      "Rn"
    ],
    "doc": ""
  },
  {
    "name": "greedy",
    "line": 66,
    "arguments": [
      "order"
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
