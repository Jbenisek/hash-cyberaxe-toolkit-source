# u1 real

Source: `research/poseidon/levels/U1/u1_real.py`

Public SHA-256: `308a37f9109d0b198c5baab9cad27559710ba114955fab3f0d89981e38ad97d6`

## Purpose recorded in the source

U1 real-field experiments (Pallas). Single process, exact big-int. Run: python u1_real.py > u1_real_output.txt

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "itertools",
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
    "name": "matinv",
    "line": 10,
    "arguments": [
      "M"
    ],
    "doc": ""
  },
  {
    "name": "H_from_state",
    "line": 29,
    "arguments": [
      "s",
      "r"
    ],
    "doc": ""
  },
  {
    "name": "root5",
    "line": 34,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "to_AB",
    "line": 35,
    "arguments": [
      "nk",
      "rho"
    ],
    "doc": ""
  },
  {
    "name": "planestate",
    "line": 36,
    "arguments": [
      "A",
      "B",
      "K"
    ],
    "doc": ""
  },
  {
    "name": "degree_of",
    "line": 89,
    "arguments": [
      "f",
      "nmax"
    ],
    "doc": ""
  },
  {
    "name": "lane_deg_profile",
    "line": 96,
    "arguments": [
      "u",
      "v",
      "a",
      "b",
      "rounds_to"
    ],
    "doc": ""
  },
  {
    "name": "exp_binary",
    "line": 133,
    "arguments": [
      "x",
      "e",
      "ctr"
    ],
    "doc": ""
  },
  {
    "name": "exp_window",
    "line": 139,
    "arguments": [
      "x",
      "e",
      "k",
      "ctr"
    ],
    "doc": ""
  },
  {
    "name": "exp_struct",
    "line": 169,
    "arguments": [
      "x",
      "k",
      "ctr"
    ],
    "doc": ""
  },
  {
    "name": "jac_rank",
    "line": 201,
    "arguments": [
      "Jm"
    ],
    "doc": ""
  },
  {
    "name": "tangent_run",
    "line": 207,
    "arguments": [
      "nk",
      "rho",
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
