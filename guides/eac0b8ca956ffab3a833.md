# j2 real

Source: `research/poseidon/levels/J2/j2_real.py`

Public SHA-256: `95f64b67261bb3d4e2f6ce9e2579b74c78529c8af87597ca219df2f747d6cac7`

## Purpose recorded in the source

J2 real: level polynomial of lane 0 after R3 along the line rho=rho0 (degree 625 in nk); factor pattern of (L3(x)-L3(P))/(x-nk0).
Validate against poseidon_ref (value check) first. Control: random degree-624 polys; single process.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "flint",
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
    "name": "mds_poly",
    "line": 8,
    "arguments": [
      "s"
    ],
    "doc": ""
  },
  {
    "name": "l3_poly",
    "line": 10,
    "arguments": [
      "rho0"
    ],
    "doc": ""
  },
  {
    "name": "l3_val",
    "line": 17,
    "arguments": [
      "nk",
      "rho"
    ],
    "doc": ""
  },
  {
    "name": "pattern",
    "line": 29,
    "arguments": [
      "g"
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
