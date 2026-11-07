# U8: order of the MDS matrix M inside F_{p^3}^*, using the (partial) factorisation of p^3-1.

Source: `research/poseidon/levels/U8/exp4.py`

Public SHA-256: `79449a970ee9176a78c258ecc0fddad242938664ae04f5137b1814eb629b8b77`

## Purpose recorded in the source

U8: order of the MDS matrix M inside F_{p^3}^*, using the (partial) factorisation of p^3-1.
N = p^3-1 = (p-1)(p^2+p+1); gcd(p-1, p^2+p+1) = gcd(p-1,3) = 3
valuation of each known prime in N

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "poseidon_ref",
  "re",
  "sympy",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "pr",
    "line": 7,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "mm",
    "line": 8,
    "arguments": [
      "A",
      "B"
    ],
    "doc": ""
  },
  {
    "name": "mpow",
    "line": 10,
    "arguments": [
      "A",
      "e"
    ],
    "doc": ""
  },
  {
    "name": "isscalar",
    "line": 16,
    "arguments": [
      "A"
    ],
    "doc": ""
  },
  {
    "name": "val",
    "line": 34,
    "arguments": [
      "n",
      "r"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
