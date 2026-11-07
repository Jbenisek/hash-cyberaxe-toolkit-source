# e3depth

Source: `research/newpaths/hotspot/e3depth.py`

Public SHA-256: `14ba1299efc7509bded5550c16e304ab2f507d7a32ec23249ce8cabb35ae2d51`

## Purpose recorded in the source

e3depth.py (hotspot; research only) - how far the logged partial E3 events of eps(beta*) get toward the E3 side of
R = 0. For a listed E1 outcome (tau, eps*) of beta*, R = 0 needs on the E3 side (DERIVED from the trial code):
  eps3 = eps*,  Delta f1 = tau ^ ror(tau, 1),  Delta g2 = tau,  Delta h2 = ror(beta* ^ eps*, 7).
The E3 side is a function of h1 and the outer words only. Prints, per record, the best listed tau and the Hamming
distance of Delta g2 and Delta h2 from their targets.
  python -B e3depth.py out/h_sub.bin [out/h_all.bin]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "ref",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "e3side",
    "line": 20,
    "arguments": [
      "h1",
      "y9",
      "y4",
      "w8",
      "e1"
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
