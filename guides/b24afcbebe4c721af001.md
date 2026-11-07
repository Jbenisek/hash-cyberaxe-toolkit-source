# e3solve

Source: `research/newpaths/counter_next/stack/e3solve.py`

Public SHA-256: `c4d27e3a63f5c4a34649c1b490081e1423b944c566a1886c640b7fe893e6df97`

## Purpose recorded in the source

e3solve.py [SEED] [PLANTS] [STEPS]   (counter_next/stack; research only)

Prototype of an E3-first solve for one outer step of the counter arrangement: given (y, Q = Y9, W = w8), find EVERY
h1 in Z_2^32 for which E3 matches an outcome (G, eps, tau):  (1) dg1 = G, (2) de2 = eps, (3) dg2 = tau.
Method: enumerate the solutions f1 of (2) by a carry DFS pruned with a backward feasibility table (output-sensitive),
map f1 -> g1 = ROL(f1,12) ^ y -> h1 = g1 - Q, test (1), then run E3 on both messages and test (3).
Checks: (a) PLANTS random real E3 pairs, each pair's own differences as the target: its h1 must be among the solutions
(completeness); every returned h1 must satisfy all three conditions on a forward re-run (soundness).
(b) STEPS outer steps that pass the exact outer filter (outer_filter.py) for the beta* outcomes: number of f1
solutions enumerated, DFS nodes, survivors of (1), solutions of (1)-(3); an op count of the solve.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "math",
  "random",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 16,
    "arguments": [
      "x",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "rol",
    "line": 17,
    "arguments": [
      "x",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "G",
    "line": 23,
    "arguments": [
      "tau"
    ],
    "doc": ""
  },
  {
    "name": "e3",
    "line": 26,
    "arguments": [
      "a",
      "y",
      "q",
      "h1",
      "w8"
    ],
    "doc": ""
  },
  {
    "name": "trans",
    "line": 37,
    "arguments": [
      "a",
      "b",
      "d",
      "o",
      "c",
      "cb",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "solutions_add_xor",
    "line": 44,
    "arguments": [
      "x0",
      "x1",
      "dz",
      "out",
      "stats"
    ],
    "doc": "all v with (x0 + v) ^ (x1 + (v ^ dz)) == out; backward-pruned DFS.  stats[0] += nodes."
  },
  {
    "name": "solve_step",
    "line": 76,
    "arguments": [
      "y",
      "q",
      "w8",
      "targets",
      "stats"
    ],
    "doc": "targets: list of (G, eps, tau).  returns sorted list of (h1, index)."
  },
  {
    "name": "member",
    "line": 96,
    "arguments": [
      "rng"
    ],
    "doc": ""
  },
  {
    "name": "solvable1",
    "line": 100,
    "arguments": [
      "q",
      "g"
    ],
    "doc": ""
  },
  {
    "name": "solvable2",
    "line": 109,
    "arguments": [
      "E",
      "df1",
      "eps"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 119,
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
