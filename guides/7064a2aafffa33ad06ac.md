# absorb32

Source: `research/newpaths/counter_swing/around/absorb32.py`

Public SHA-256: `bcbc64262e117152482c01ba287a915d2d6f1818480b5b92776c0cbc13d7e2e3`

## Purpose recorded in the source

absorb32.py - real 32-bit check, on the organizer's own functions (org_blake3.py = verifier/blake3.py copy),
that a leaf (last chunk, one 64-byte block) and a parent node can be made to agree on the whole state after
round 0, for every leaf-vs-parent placement the tree allows (tree_align.py), by copying the parent's message
(the two child CVs) and changing only the absorbing words of the columns whose d input differs.

Node descriptors come from the organizer's _chunk_output (leaf at chunk index t) and _parent_output (parent over
child chunks t and t+1, their CVs computed with _chunk_output/_compress at their true indices). Round-0 equality is
tested as equality of all 16 words of _compress(..., rounds=1): with cv = IV on both sides those 16 words fix the
state after round 0.
Run: python -B absorb32.py [trials]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "org_blake3",
  "random",
  "struct",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "absorb_words",
    "line": 22,
    "arguments": [
      "par_words",
      "d_par",
      "d_leaf",
      "cols"
    ],
    "doc": "d_par / d_leaf: the 4 d inputs (v12..v15) of parent and leaf. Returns leaf words."
  },
  {
    "name": "one",
    "line": 34,
    "arguments": [
      "rnd",
      "t",
      "root_level"
    ],
    "doc": "Returns (round0_equal, n_equal_cv_words_after_2_rounds, leaf_bytes_ok)."
  },
  {
    "name": "main",
    "line": 74,
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
