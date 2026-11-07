# oclib

Source: `research/fifties/perspectives/onescomp/oclib.py`

Public SHA-256: `a6762a96f91cb363e2432ba69a6ce0bf3b78acfccdfb65f351fbb99a2f5103bc`

## Purpose recorded in the source

Ones'-complement lens (Z/(2^32-1)) on the front-line residual: shared counting and evaluation.

Counts are built either in numpy (from the stored data) or by oc_stream.c (streaming, fresh samples); both
produce the SAME flat layout (layout() below), so one evaluator serves both.

Quantities, per residual word w in (1,3,4,6) (index 0..3):
  D  = oc(dA) - oc(dB) mod M          the residual read in ones'-complement coordinates (primary)
  R  = oc(dA ^ dB)                     the XOR residual R read as an element of Z/M
  E  = D - oc_diff(x) - oc_diff(y)     epsilon: what is left when D is split as E1 part + E3 part
                                       (digest word = x ^ y, x from one diagonal G, y from the other)
  S  = oc(dA) - oc(dA ^ R_other) mod M surrogate: D rebuilt with a residual from ANOTHER row (keeps R's
                                       distribution, breaks the dA <-> R coupling); a control, never tested
where oc(x) = x mod (2^32-1) (0xFFFFFFFF -> 0) and M = 2^32-1 = 3*5*17*257*65537.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "math",
  "numpy",
  "scipy"
]
```

## Entry points

```json
[
  {
    "name": "ordm",
    "line": 29,
    "arguments": [
      "g",
      "p"
    ],
    "doc": ""
  },
  {
    "name": "coset_index",
    "line": 37,
    "arguments": [
      "p",
      "g"
    ],
    "doc": ""
  },
  {
    "name": "layout",
    "line": 51,
    "arguments": [],
    "doc": "Ordered list of (key, length): the flat layout shared with oc_stream.c."
  },
  {
    "name": "split_flat",
    "line": 69,
    "arguments": [
      "flat"
    ],
    "doc": ""
  },
  {
    "name": "oc",
    "line": 78,
    "arguments": [
      "x"
    ],
    "doc": ""
  },
  {
    "name": "ocsub",
    "line": 84,
    "arguments": [
      "a",
      "b"
    ],
    "doc": ""
  },
  {
    "name": "quantities",
    "line": 90,
    "arguments": [
      "dA",
      "dB",
      "xA",
      "xB",
      "yA",
      "yB",
      "rng"
    ],
    "doc": "dA,dB,xA,... : (N,4) uint32. Returns dict Q -> (N,4) int64 in [0,M)."
  },
  {
    "name": "counts_from",
    "line": 100,
    "arguments": [
      "Qv"
    ],
    "doc": ""
  },
  {
    "name": "to_flat",
    "line": 130,
    "arguments": [
      "C"
    ],
    "doc": ""
  },
  {
    "name": "_div_expect",
    "line": 134,
    "arguments": [],
    "doc": ""
  },
  {
    "name": "chi2_uniform",
    "line": 147,
    "arguments": [
      "h"
    ],
    "doc": ""
  },
  {
    "name": "zero_test",
    "line": 154,
    "arguments": [
      "c0",
      "n",
      "prob"
    ],
    "doc": ""
  },
  {
    "name": "evaluate",
    "line": 168,
    "arguments": [
      "C",
      "qs"
    ],
    "doc": "All tests on one count set. Returns dict id -> dict(stat, p, eff, kind)."
  },
  {
    "name": "chi2_two",
    "line": 205,
    "arguments": [
      "a",
      "b"
    ],
    "doc": "Two-sample chi-square homogeneity test of histograms a (tested) and b (reference/control)."
  },
  {
    "name": "zero_two",
    "line": 221,
    "arguments": [
      "a0",
      "Na",
      "b0",
      "Nb"
    ],
    "doc": "Cell-0 frequency of the tested set vs the reference. Returns (z, p, adv bits, se of adv)."
  },
  {
    "name": "evaluate2",
    "line": 241,
    "arguments": [
      "C",
      "Cref",
      "qs"
    ],
    "doc": "All tests of one count set against a reference count set (the control stream). id -> dict."
  },
  {
    "name": "h2",
    "line": 278,
    "arguments": [
      "v"
    ],
    "doc": "Renyi-2 entropy estimate from collisions; returns (H2 or None, distinct, top value, top freq)."
  }
]
```

## Read alongside

- research/fifties/perspectives/onescomp/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
