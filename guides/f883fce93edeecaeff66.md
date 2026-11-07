# quicktests

Source: `research/newpaths/fringe/quicktests.py`

Public SHA-256: `cbb8899a29107c6497494faf6d5881b93e3f80cdb2ba65b475fe0b5ebb2c3045`

## Purpose recorded in the source

Quick toy tests for the fringe angles (numpy, vectorised over many messages).
  absorb  : E0 output depends on Y0+m1 only (a and x enter G only via a1 = a+b+x)            [w=32]
  sym     : E0 eff. inputs = E2 eff. inputs  ->  out0=out2 and out5=out7                       [w=32]
  neutral : single-bit and two-bit message differences that keep the E0/E2 inputs unchanged   [w=8, w=32]
  rx      : rotational probability of one G call and of the K layer with BLAKE3 constants     [w=32]
Usage: python quicktests.py <test> [N]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "itertools",
  "numpy",
  "random",
  "sys",
  "toyb3"
]
```

## Entry points

```json
[
  {
    "name": "vrotr",
    "line": 16,
    "arguments": [
      "z",
      "r",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "vG",
    "line": 24,
    "arguments": [
      "a",
      "b",
      "c",
      "d",
      "x",
      "y",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "vtrace",
    "line": 38,
    "arguments": [
      "M",
      "w",
      "upto"
    ],
    "doc": "M: (N,16) uint64.  Returns state after round-1 columns (Y) and final state Z (lists of arrays)."
  },
  {
    "name": "inA",
    "line": 60,
    "arguments": [
      "Y",
      "M"
    ],
    "doc": ""
  },
  {
    "name": "effA",
    "line": 64,
    "arguments": [
      "Y",
      "M",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "t_absorb",
    "line": 70,
    "arguments": [
      "N"
    ],
    "doc": ""
  },
  {
    "name": "t_sym",
    "line": 84,
    "arguments": [
      "N"
    ],
    "doc": ""
  },
  {
    "name": "t_neutral",
    "line": 101,
    "arguments": [
      "N"
    ],
    "doc": ""
  },
  {
    "name": "t_rx",
    "line": 128,
    "arguments": [
      "N"
    ],
    "doc": ""
  },
  {
    "name": "t_sibling",
    "line": 145,
    "arguments": [
      "N"
    ],
    "doc": "Length siblings: for one base message, every block length L gets (m4_L, m5_L) with identical round-0 output.\nK2 = G(IV2, IV6, IV2, L; m4, m5): d enters only via d1 = rotr(L ^ a1, 16) and a1 only via d1 and a2, so\na1_L = a1* ^ L, m4_L = a1_L - IV2 - IV6, m5_L = m5* + a1* - a1_L keeps K2's output (exact, any L)."
  }
]
```

## Read alongside

- research/newpaths/fringe/RESULTS.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
