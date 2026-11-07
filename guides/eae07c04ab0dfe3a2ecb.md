# ref

Source: `research/dig/incoming2/blake3-r2-G05-U06/work/ref.py`

Public SHA-256: `3c80f14fe5fe8b30c6aa43864c5f698fab3133080f6dcc3c10c28f809db1c477`

## Purpose recorded in the source

known answer 1: full 7-round BLAKE3 empty-string digest of the verifier equals official
known answer 2: my 2-round compression (init, round0 via verifier _g, round1 via round1()) == verifier r=2

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "os",
  "random",
  "struct",
  "sys",
  "verifier"
]
```

## Entry points

```json
[
  {
    "name": "ror",
    "line": 5,
    "arguments": [
      "x",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "G",
    "line": 6,
    "arguments": [
      "v",
      "a",
      "b",
      "c",
      "d",
      "x",
      "y"
    ],
    "doc": ""
  },
  {
    "name": "round1",
    "line": 8,
    "arguments": [
      "X",
      "mp"
    ],
    "doc": "one more round on state X with ROUND-1 ordered message mp[0..15]; returns Y (after columns), Z"
  },
  {
    "name": "fold",
    "line": 17,
    "arguments": [
      "Z"
    ],
    "doc": ""
  },
  {
    "name": "mp_from_w",
    "line": 18,
    "arguments": [
      "w"
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
