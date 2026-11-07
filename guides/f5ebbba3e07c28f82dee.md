# tb3

Source: `research/newpaths/counter_swing/around/tb3.py`

Public SHA-256: `cfdbfc2ac97fad92fea98b03e29daf7ccdd7f6e7e96bb271f41878baa3e82147`

## Purpose recorded in the source

tb3.py - vectorized 2-round BLAKE3 compression at word width w (w = 32 is the real one), with intermediates.

Own code (folder counter_swing\around). Toy widths scale the rotations as floor(r*w/32) and take the top w bits of
each IV word, as the team's earlier toys did. selftest() checks w = 32 against the organizer's _compress
(copied here as org_blake3.py). Run: python -B tb3.py

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "org_blake3",
  "random"
]
```

## Entry points

```json
[
  {
    "name": "absorb",
    "line": 72,
    "arguments": [
      "toy",
      "v_base",
      "v_other",
      "m_base",
      "cols"
    ],
    "doc": "Message for the OTHER state so that round-0 column calls in `cols` give equal outputs.\nColumn c has a = v[c], b = v[c+4], d = v[c+12], x = m[2c], y = m[2c+1]. Requires a, b, c equal."
  },
  {
    "name": "selftest",
    "line": 86,
    "arguments": [
      "n",
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
