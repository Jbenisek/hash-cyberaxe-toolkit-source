# followup

Source: `research/newpaths/hotspot/followup.py`

Public SHA-256: `1d548d7921c85a1d9c0a34b31070f177fecb28e66f0ad9a6392713e1d1339920`

## Purpose recorded in the source

followup.py (hotspot; research only) - checks of the hot spots found by analyze_hot.py.
1. GF(2) affine relations that hold for EVERY logged event (c1 free bits for E1 events; Y9 / w8 / e1 bits for E3).
2. Fixed regions (named here, from the discovery half of out/h_sub.bin): gain = P(region | event) / P(region | null) on
   the held-out half (thread id odd) and on the whole-class file, for every event.
3. Exact (DP) per-Y9 probability that Delta f1 is in the eps* list, and the gain curve of keeping the best Y9 values;
   the same for the R = 0 targets Delta f1 = tau ^ ror(tau, 1).
  python -B followup.py out/h_sub.bin out/h_all.bin

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "analyze_hot",
  "numpy",
  "ref",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "bit",
    "line": 22,
    "arguments": [
      "R",
      "w",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "affine_relations",
    "line": 26,
    "arguments": [
      "V",
      "labels"
    ],
    "doc": "all (a, c) with a . x = c for every row x of V (rows of 0/1); returns list of (bits in a, c)"
  },
  {
    "name": "dp_y9",
    "line": 64,
    "arguments": [
      "y9",
      "targets"
    ],
    "doc": "exact number of h1 (out of 2^32) with Delta g1 in targets, for each y9 (vector)"
  },
  {
    "name": "regions",
    "line": 93,
    "arguments": [
      "R"
    ],
    "doc": ""
  }
]
```

## Read alongside

- research/newpaths/hotspot/dp_proof.py

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
