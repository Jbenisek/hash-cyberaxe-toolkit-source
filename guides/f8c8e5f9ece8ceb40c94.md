# REGS: one batch per sweep (needs ~28 planes < 32 regs): nsw = nb

Source: `research/dig/incoming2/sha256-37-G02-U04/work/variants.py`

Public SHA-256: `bf373661dcc7138ca6137fd968ba48cbd27068a01f35500daca0d4b70162f957`

## Purpose recorded in the source

REGS: one batch per sweep (needs ~28 planes < 32 regs): nsw = nb
PLANES recompute from the packed entries per use (naive bit insertion 3 ops, 64 word loads)
ENTRIES recompute per scan lane from the planes: extract s (3 ops/plane) + S0 (11) + pack (2) - the load (1)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "contextlib",
  "io",
  "math",
  "re",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "load",
    "line": 4,
    "arguments": [
      "patches"
    ],
    "doc": ""
  },
  {
    "name": "run",
    "line": 13,
    "arguments": [
      "ns"
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
