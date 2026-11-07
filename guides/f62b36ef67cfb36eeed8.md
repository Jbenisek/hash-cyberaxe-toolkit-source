# g02_mem.py - G02 memory axis for the filed r37 table line (pkgR37c xtab.py ledger).  Own code; reads xtab.py/lowm.py as modules of OUR packages.

Source: `research/dig/incoming2/sha256-37-G02-U01/work/g02_mem.py`

Public SHA-256: `e1a9d3f6cb51e5a8b48288259e288c38bbc3c86250f913acd054bd3ad293b95a`

## Purpose recorded in the source

g02_mem.py - G02 memory axis for the filed r37 table line (pkgR37c xtab.py ledger).  Own code; reads xtab.py/lowm.py as modules of OUR packages.
Step 1 reproduce time_log2 / T_num/T_den / byte total.  Step 2 D126 shard model (known answer k=5).  Step 3 reject-early shard model, R16T and ANC variants.
---------- bytes (exact, proof.md Section 14 of the filed line) ----------
---------- the ledger with parameters (copy of xtab.ledger arithmetic) ----------

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "decimal",
  "fractions",
  "importlib.util",
  "json",
  "math",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "load",
    "line": 8,
    "arguments": [
      "n",
      "p"
    ],
    "doc": ""
  },
  {
    "name": "mem_bound",
    "line": 22,
    "arguments": [
      "B",
      "r16",
      "anc"
    ],
    "doc": ""
  },
  {
    "name": "Sscore",
    "line": 24,
    "arguments": [
      "t",
      "m"
    ],
    "doc": ""
  },
  {
    "name": "ledger_param",
    "line": 28,
    "arguments": [
      "B",
      "mode",
      "scan_lane",
      "probe_delta_group",
      "pre_div",
      "q3_log2",
      "test_ops"
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
