# ledger38d.py - the exact ledger of the r38 variant-table attack, derivative R38d (Appendix C).  ledger38.py of the base

Source: `research/dig/incoming2/sha256-38-G02-U01/work/g02_ledger38.py`

Public SHA-256: `3708a73dc3856b0ad9d62fef0724983a195dceed3fe09928af7d171204f7ac9b`

## Purpose recorded in the source

ledger38d.py - the exact ledger of the r38 variant-table attack, derivative R38d (Appendix C).  ledger38.py of the base
package with three inputs added: the tables list the NGW = 22 live words of G (L0), the deep path has its own counter N2
(L4), and the W7 path and the fill pass are those of the levered program (L2).  Every operation count is an executed-operation
count of the counted programs (runs/costs.json, runs/pre1.json, runs/pre2.json); probabilities are exact rationals except
q3_model and delta.  With --base it is ledger38.py exactly (NGW = 32, no N2) and reproduces 2^71.695220.
  python3 ledger38d.py [--base] [--q3 -101.5] [--delta 1] [--eps-log2 -4] [--ac 70] [--as 60] [--dev 60] [--succ 0.39]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Declared inputs

```json
[
  {
    "declared_arguments": [
      "--base"
    ],
    "action": "store_true"
  },
  {
    "declared_arguments": [
      "--q3"
    ]
  },
  {
    "declared_arguments": [
      "--delta"
    ],
    "default": 1.0
  },
  {
    "declared_arguments": [
      "--eps-log2"
    ]
  },
  {
    "declared_arguments": [
      "--ac"
    ],
    "default": 70
  },
  {
    "declared_arguments": [
      "--as"
    ],
    "dest": "as_",
    "default": 60
  },
  {
    "declared_arguments": [
      "--dev"
    ],
    "default": 60
  },
  {
    "declared_arguments": [
      "--succ"
    ],
    "default": "0.39"
  }
]
```

## Imports

```json
[
  "argparse",
  "decimal",
  "fractions",
  "json",
  "math",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "log2d",
    "line": 20,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "up5",
    "line": 21,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "pre_ops",
    "line": 23,
    "arguments": [
      "cs",
      "p1",
      "p2",
      "ngw",
      "lev",
      "B",
      "xprefix"
    ],
    "doc": "Preprocessing in word operations: every term is (items) x (executed operations per item) + loop control."
  },
  {
    "name": "ledger",
    "line": 42,
    "arguments": [
      "q3_log2",
      "delta",
      "eps",
      "ac",
      "as_",
      "dev",
      "succ",
      "tol",
      "show",
      "costs",
      "p1",
      "p2",
      "base",
      "ngw",
      "n2",
      "eps2",
      "B",
      "scan_ops",
      "xiter",
      "drop",
      "xprefix",
      "p5stream",
      "nbB",
      "rej_ops",
      "esz",
      "nosent",
      "xne",
      "xcw",
      "code_B"
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
