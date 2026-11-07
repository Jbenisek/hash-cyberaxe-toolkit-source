# ledger

Source: `research/newpaths/untried/ctr_alg/ledger.py`

Public SHA-256: `5f6d7eea8ed0e1681d13a4d91194a2f117914b0058cc43bd48999c0cab0b9ff0`

## Purpose recorded in the source

ledger.py (untried/ctr_alg; research only) - every work measure per passing step on the record steps (rec7 = the
150 steps of e3solve_out.txt, rec11 = the 120 steps of e3solve2.py's run, pooled = 270), and its value on the X2
ledger: stack_calc.py V4, T = log2(S * c / 430) + 0.02, c = 400 + 35 + 2^-9.8132 * SOLVE, S = 2^69.987 (R_SUB).
Inputs: systems.json (e3sat.py), time_split.json + time_split_cms.json (e3sat_time.py), cms_inproc.json.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "math",
  "os"
]
```

## Entry points

```json
[
  {
    "name": "T",
    "line": 20,
    "arguments": [
      "solve"
    ],
    "doc": ""
  },
  {
    "name": "T4p",
    "line": 57,
    "arguments": [
      "solve"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/ctr_alg/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
