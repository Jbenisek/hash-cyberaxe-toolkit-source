# Exact ledger of the counted program (proof.md Sections 9-11). Integers and Fractions only.

Source: `research/dig/incoming2/sha256-37-G02-U05/work/ledger_appendix.py`

Public SHA-256: `7efeb7544c825e4bdae7ad599dfce5b37966e0f822f142bbe33961cada5b1c53`

## Purpose recorded in the source

Exact ledger of the counted program (proof.md Sections 9-11). Integers and Fractions only.
stage prices (primitives of the straight-line text, proof.md Section 9; the plane-program counts are measured by lowm.py and asserted at every execution)
the 222 classes: (variants, cube bits k, classes): lists 0, 1 / 2, 3, 4 / 5, 6 / 7, 8, 9 (proof.md Section 5.3)
allowances (unchanged) and the success-floor constants
operations of a passing class with relevant cube bits Q0 that do not depend on which reps are good (2^|Q0| runs)
scan, extraction and members of one run if all reps are good (times p6 for the expectation)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "fractions"
]
```

## Entry points

```json
[
  {
    "name": "subsets",
    "line": 22,
    "arguments": [
      "mask"
    ],
    "doc": ""
  },
  {
    "name": "lane_costs",
    "line": 23,
    "arguments": [
      "nls"
    ],
    "doc": ""
  },
  {
    "name": "memcost",
    "line": 24,
    "arguments": [
      "j"
    ],
    "doc": ""
  },
  {
    "name": "class_det",
    "line": 25,
    "arguments": [
      "n",
      "k",
      "Q0"
    ],
    "doc": ""
  },
  {
    "name": "class_run_cost",
    "line": 34,
    "arguments": [
      "n",
      "k",
      "Q0"
    ],
    "doc": ""
  },
  {
    "name": "class_expected",
    "line": 38,
    "arguments": [
      "n",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "class_max",
    "line": 41,
    "arguments": [
      "n",
      "k"
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
