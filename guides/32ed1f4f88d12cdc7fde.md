# spot check of the definition against vt38.inF7 on a few values

Source: `research/sha256grid/check2-3/f7count.py`

Public SHA-256: `bf7160869393941495c874476b425b745e23c7ce243ebf23ed2b79c3a3b7c19a`

## Purpose recorded in the source

check2-3: exact |F7| = #{w in 2^32 : s0(w + D7) - s0(w) = T7} by exhaustive numpy count (D7, T7 from vt38.py);
the q3 tail weight 2^(32-f)/|F7| and p2 = |F7|/2^32 of the ledger depend on it.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "importlib.util",
  "math",
  "numpy",
  "random",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 10,
    "arguments": [
      "x",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "s0",
    "line": 11,
    "arguments": [
      "x"
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
