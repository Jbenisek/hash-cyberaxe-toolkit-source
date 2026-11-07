# summary

Source: `research/fifties/perspectives/data/summary.py`

Public SHA-256: `4583efbb569aef458195cc74643c89f8bdc360f61de369a4bf1947932568b165`

## Purpose recorded in the source

Sanity summary of rand/ and ctx/ (no analysis claims): per word of R, K1, K3 - distinct values, mean Hamming
weight, largest single-bit bias |P(bit=1) - 1/2| and the bit where it occurs, constant bits.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "numpy",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "hw",
    "line": 12,
    "arguments": [
      "a"
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
