# ---- H4 R2: exact recount of the A_C comparison ----

Source: `research/dig/incoming2/sha256-37-G07-U02/work/analyse.py`

Public SHA-256: `8735ef39ef70316394ef8ce80da681a1453cd9d7c519a055c70805840d273594`

## Purpose recorded in the source

---- H4 R2: exact recount of the A_C comparison ----
ratio 2^60 / 593858 CPU-s -> in CPU-s: 2^38.573 / 593858
share of T
per 1 bit of A_C: dT/d(ac)
A_S, DEV sensitivity (hand: T = AC+AS+DEV+..)
---- H5 R4: bits per primitive ----

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "copy",
  "decimal",
  "fractions",
  "json",
  "lowm",
  "math"
]
```

## Entry points

```json
[
  {
    "name": "with_",
    "line": 29,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "exact_dT",
    "line": 35,
    "arguments": [
      "o"
    ],
    "doc": ""
  },
  {
    "name": "lg",
    "line": 36,
    "arguments": [
      "o"
    ],
    "doc": ""
  },
  {
    "name": "d",
    "line": 37,
    "arguments": [
      "o"
    ],
    "doc": ""
  },
  {
    "name": "mu_req",
    "line": 61,
    "arguments": [
      "pcap"
    ],
    "doc": ""
  },
  {
    "name": "succ",
    "line": 64,
    "arguments": [
      "mu",
      "pcap"
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
