# regsat

Source: `research/newpaths/ksplit/regsat.py`

Public SHA-256: `0dcfd98ef87be906ee1e9aa8ab7c2c34a6caae7543545ee428486e987b085115`

## Purpose recorded in the source

Balanced-region lower bound for join trees (ksplit).

Question: is there a set V of words with lo <= |V| <= hi and delta(V) = |V| - Ein(V) <= D ?
(Ein(V) = equations whose unknown words all lie in V.)  Writes DIMACS; e_e -> v_w for w in e (sound: an
equation may only be counted when all its words are in V).
Usage: python regsat.py <sysfile> <lo> <hi> <D> <out.cnf>
       python regsat.py --decode <sysfile> <out.cnf> <solver output>

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "load",
    "line": 12,
    "arguments": [
      "fn"
    ],
    "doc": ""
  },
  {
    "name": "encode",
    "line": 62,
    "arguments": [
      "fn",
      "lo",
      "hi",
      "D"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 77,
    "arguments": [],
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
