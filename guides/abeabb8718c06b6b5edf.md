# gd2

Source: `research/newpaths/untried/b3-r1c/gd2.py`

Public SHA-256: `c34fdd8fbeef6448b9805427c142e8549ee68b1c10bc6255cacabc358909b5c2`

## Purpose recorded in the source

b3-r1c scout: complete word-level GD peak search (all unknown words are guess candidates).

Same relation system as gd.py.  Incremental closure; iterative deepening on the peak;
memo on the closed known-set.  Usage: python gd2.py <case> <peak> [budget_s]
cases: lift (9 E words held, dof 0), e3 (E3 held, dof 5), e1 (E1 held, dof 4).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "gd",
  "sys",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "close",
    "line": 14,
    "arguments": [
      "known",
      "used",
      "new"
    ],
    "doc": ""
  },
  {
    "name": "solve",
    "line": 33,
    "arguments": [
      "known0",
      "peak",
      "budget"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/b3-r1c/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
