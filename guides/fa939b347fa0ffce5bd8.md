# t1c counter

Source: `research/newpaths/scout_cross/t1c_counter.py`

Public SHA-256: `b255e381ed042779075ab8e734f309b2213df4034ba601d8b3d1c84a794277f5`

## Purpose recorded in the source

TEST 1c: does the filed path's trial model depend on the chunk counter?
In the filed construction q2 = 0 and k2 = 0 are the counter words v12, v13 (job20 ANSWER.md:
'K0.a1 = ROL(K0.d1,16)' and 'K1.a1 = ROL(K1.d1,16)').  With the last-chunk trick (TEST 1a) the
counter t is free, so q2 = t_lo and k2 = t_hi can be chosen.  This reuses the HASH$CyberAxe team's FIX7 hand model
(research/grok/work/job20_copass/compare_models.py, h1_hand + draw_hand, copied, read-only import of
exact_model), which job20 found indistinguishable from the exact model, and sweeps q2 (and k2).
Measured: H4 pass rate p0 and H4 co-pass for the e1/X2 flips (the cluster lever's inputs).
CAVEAT: the model treats the other words as independent uniform; the pins (Y3, X3, X7, X11, X15,
W13, W4) were found for t = 0 and are assumed to stay reachable (round 0 is a bijection).
Usage: python -B t1c_counter.py [log2 samples=20] [seed=1]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "exact_model",
  "numpy",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "u",
    "line": 21,
    "arguments": [
      "rng",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "u32",
    "line": 25,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "h1_hand",
    "line": 29,
    "arguments": [
      "C",
      "e1",
      "X2"
    ],
    "doc": ""
  },
  {
    "name": "draw",
    "line": 54,
    "arguments": [
      "rng",
      "n",
      "q2",
      "k2"
    ],
    "doc": ""
  },
  {
    "name": "flips",
    "line": 64,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "measure",
    "line": 70,
    "arguments": [
      "q2",
      "k2",
      "lg",
      "seed"
    ],
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
