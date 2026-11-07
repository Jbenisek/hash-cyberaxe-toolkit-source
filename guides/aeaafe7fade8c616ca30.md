# test lm

Source: `research/newpaths/untried/b3-trail/test_lm.py`

Public SHA-256: `cfbfc813eb78d0714f4a4599271dc3e676d4f76c44847f5d89adb2f3126e733d`

## Purpose recorded in the source

test_lm.py - brute-force checks of the LM formula and of the CNF encoding of b3trail.py.

1. For n = 5 bits, every (a, b, c): exact xdp+ by enumerating all x, y equals 2^-lm(a,b,c)
   (and 0 exactly when lm says impossible).
2. The add2 clause set of b3trail.Builder(n=5), evaluated at every (a, b, c) with minimal weight
   bits, accepts exactly the LM-valid triples and its weight equals lm().

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "b3trail",
  "decode",
  "itertools",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "exact_xdp",
    "line": 17,
    "arguments": [
      "a",
      "b",
      "c",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 27,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/untried/b3-trail/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
