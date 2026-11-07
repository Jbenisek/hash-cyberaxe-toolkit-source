# ---------------- Part C: the c1 cube ----------------

Source: `research/fifties/angles/a7/anf_degree.py`

Public SHA-256: `55c15d1762d17eb878f7d0a1f1de24c2cf71553e8d187197d76aafd2e242be99`

## Purpose recorded in the source

A7 (ANGLES.md section 7): algebraic degree (ANF, Moebius transform) of the stage-A and residual bits.

Part C (the c1 cube of pkg16f, 21 free bits, per frame = the six words ctr_batch reads, from halfsearch.ctr_outer):
  h1 = ROR(Y14 ^ e1, 16) (all 32 bits; rule A reads its parities), the 8 rule-A parities, the rule-A pass flag,
  and the E1 word (zero = hit; the residual), as Boolean functions of the 21 free bits of c1 (ctr_c1 order).
Part Y (the member y of pkg21 outer.py / memberloop.py, 19 free bits, per context = seven outer words):
  omega = Y3 + y + w8 (input of test (2)) and Y9 (input of test (1)), as functions of the 19 member bits.
For every output bit: degree of its ANF and the number of variables its ANF involves. 16 random frames each.
Run: python -B anf_degree.py   (numpy; writes nothing but stdout)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "halfsearch",
  "hashlib",
  "json",
  "memberloop",
  "numpy",
  "os",
  "outer",
  "struct",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "rorv",
    "line": 28,
    "arguments": [
      "x",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "rolv",
    "line": 32,
    "arguments": [
      "x",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "words",
    "line": 36,
    "arguments": [
      "tag",
      "i",
      "k"
    ],
    "doc": ""
  },
  {
    "name": "moebius",
    "line": 40,
    "arguments": [
      "t",
      "n"
    ],
    "doc": "In-place ANF of 32 packed Boolean functions (uint32 truth table of length 2^n, index bit i = variable i)."
  },
  {
    "name": "profile",
    "line": 49,
    "arguments": [
      "anf",
      "n",
      "nbits"
    ],
    "doc": "Per output bit: (degree, number of variables in the ANF, number of monomials)."
  },
  {
    "name": "lanes_c",
    "line": 74,
    "arguments": [
      "key"
    ],
    "doc": ""
  },
  {
    "name": "key_of",
    "line": 99,
    "arguments": [
      "o"
    ],
    "doc": ""
  },
  {
    "name": "scalar_lane",
    "line": 103,
    "arguments": [
      "key",
      "c1"
    ],
    "doc": ""
  },
  {
    "name": "evv",
    "line": 129,
    "arguments": [
      "e",
      "v"
    ],
    "doc": ""
  },
  {
    "name": "lanes_y",
    "line": 150,
    "arguments": [
      "seven"
    ],
    "doc": ""
  },
  {
    "name": "main",
    "line": 160,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/fifties/angles/a7/anf_result.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
