# ================================================================ 2 the target hash (Orchard Poseidon, ConstantLength<2>, 8 full + 56 partial rounds)

Source: `research/poseidon/generic/core_rho.py`

Public SHA-256: `9eeee475af9493ee2156d64e3407bee741075233a81f10fb3ebf8a4a2164d7d9`

## Purpose recorded in the source

================================================================ 2 the target hash (Orchard Poseidon, ConstantLength<2>, 8 full + 56 partial rounds)
================================================================ 3 the search: one trail, distinguished points, one table, recovery

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Entry points

```json
[
  {
    "name": "digest",
    "line": 6,
    "arguments": [
      "m0",
      "m1"
    ],
    "doc": "Digest of the Orchard hash of the two canonical field elements (m0, m1): initial state [m0, m1, 2^65], 64 rounds, output state[0]."
  },
  {
    "name": "enc",
    "line": 27,
    "arguments": [
      "x"
    ],
    "doc": "Canonical 32-byte little-endian encoding (x < P)."
  },
  {
    "name": "search",
    "line": 34,
    "arguments": [
      "F",
      "is_dp",
      "x0",
      "steps",
      "mcap",
      "gmax"
    ],
    "doc": "Single-trail collision search on the map F: x_0 = x0, x_i = F(x_{i-1}).  Every value x_i, i >= 1, with is_dp(x_i) is stored with its index.\nHalts (failure) after `steps` evaluations, when more than `mcap` distinguished points would be stored, or when the recovery needs a gap\nlonger than gmax.  When a distinguished value repeats (x_b = x_a, a < b) the trail is periodic from a with period L = b - a;"
  },
  {
    "name": "plan",
    "line": 97,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "F_n",
    "line": 121,
    "arguments": [
      "v"
    ],
    "doc": ""
  },
  {
    "name": "is_dp_n",
    "line": 128,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "run_rho",
    "line": 132,
    "arguments": [
      "seed"
    ],
    "doc": ""
  },
  {
    "name": "run_proj",
    "line": 142,
    "arguments": [
      "seed"
    ],
    "doc": "Full-width walk g(x) = digest(x, 0) on field elements: 64 points of the real map from a seed start; a pair when the low 10 bits of two digests agree."
  },
  {
    "name": "main",
    "line": 156,
    "arguments": [],
    "doc": ""
  }
]
```

## Read alongside

- research/poseidon/generic/make_manifests.py
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
