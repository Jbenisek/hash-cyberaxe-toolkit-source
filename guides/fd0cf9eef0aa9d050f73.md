# density of pins: random (X3,X7,X11,X15,w4,w13), shift s=+8: P(C3 outputs b and d both equal); also d only / b only

Source: `research/dig/incoming2/blake3-r2-G05-U08/work/e6_density.py`

Public SHA-256: `c086d77238b0771aef2d9418d509ae599207b1abc89db22650ae305d0a3644ab`

## Purpose recorded in the source

density of pins: random (X3,X7,X11,X15,w4,w13), shift s=+8: P(C3 outputs b and d both equal); also d only / b only

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 4,
    "arguments": [
      "x",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "c3",
    "line": 5,
    "arguments": [
      "a",
      "b",
      "c",
      "d",
      "x",
      "y"
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
