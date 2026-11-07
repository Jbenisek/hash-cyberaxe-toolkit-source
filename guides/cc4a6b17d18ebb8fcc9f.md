# t7 theta kernel

Source: `research/dig/incoming/sha3-r6-U02/work/t7_theta_kernel.py`

Public SHA-256: `242405addc784e4856987127413694b4dd2217b6d5acd0df7038b6ef0f997476`

## Purpose recorded in the source

Q4 theta cell: theta2 column-parity kernel membership of the z-space chi1-output differences, for the leader pair and all 21 aligned pairs.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "itertools",
  "json",
  "kk6",
  "numpy",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "varying",
    "line": 7,
    "arguments": [
      "l",
      "j"
    ],
    "doc": ""
  },
  {
    "name": "nullspace",
    "line": 9,
    "arguments": [
      "vecs"
    ],
    "doc": "vecs[j] = int; return basis of {u: XOR_j u_j vecs[j]=0} as list of ints over j"
  },
  {
    "name": "O2P",
    "line": 19,
    "arguments": [
      "S"
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
