# eng

Source: `research/dig/incoming4/_tools/eng.py`

Public SHA-256: `b64a6247df4679e51af8bf7590a7c224d1b67682e96a848a2eed05eb3d1f3375`

## Purpose recorded in the source

dig-scan-poseidon engine: exact digest polynomial on the skip line, with per-layer variants (flint, Pallas).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "flint",
  "os",
  "poseidon_ref",
  "random",
  "sys",
  "time"
]
```

## Entry points

```json
[
  {
    "name": "p5",
    "line": 13,
    "arguments": [
      "f"
    ],
    "doc": ""
  },
  {
    "name": "lincomb",
    "line": 16,
    "arguments": [
      "coefs",
      "polys"
    ],
    "doc": ""
  },
  {
    "name": "mat_apply",
    "line": 22,
    "arguments": [
      "Mx",
      "st"
    ],
    "doc": ""
  },
  {
    "name": "default_var",
    "line": 25,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "round_opts",
    "line": 29,
    "arguments": [
      "idx",
      "var"
    ],
    "doc": ""
  },
  {
    "name": "setup",
    "line": 35,
    "arguments": [
      "Mat0",
      "o0",
      "j",
      "o1"
    ],
    "doc": "line for kept coordinate j under round-0 matrix Mat0; returns (a,b,U0,V0) with x = A(U,V)+base."
  },
  {
    "name": "run_line",
    "line": 52,
    "arguments": [
      "r",
      "j",
      "var",
      "verbose"
    ],
    "doc": "Exact digest polynomial in W on line j. Returns dict(deg, lc!=0, poly, state degrees)."
  },
  {
    "name": "validate",
    "line": 89,
    "arguments": [],
    "doc": "tool check: poseidon_ref vs pinned vectors and flint line digest vs reference hash"
  }
]
```

## Read alongside

- research/dig/SCHEMA.md
- research/dig/d243_w6full_result_record.json
- research/dig/d253_b3m_proof_release_audit.json
- research/dig/rec_d243_poseidon_d15625_result.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
