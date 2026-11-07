# b3

Source: `research/dig/incoming2/blake3-r2-G05-U07/work/b3.py`

Public SHA-256: `ef1dc882c3a9f1e4797a670dd3e7f1d28f632fcf28401e8b1d0d2b55777e138d`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

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
    "name": "G",
    "line": 5,
    "arguments": [
      "v",
      "a",
      "b",
      "c",
      "d",
      "mx",
      "my"
    ],
    "doc": ""
  },
  {
    "name": "rnd",
    "line": 10,
    "arguments": [
      "v",
      "m"
    ],
    "doc": ""
  },
  {
    "name": "init",
    "line": 13,
    "arguments": [
      "h",
      "m",
      "tlo",
      "thi",
      "b",
      "d"
    ],
    "doc": ""
  },
  {
    "name": "states",
    "line": 14,
    "arguments": [
      "h",
      "m",
      "tlo",
      "thi",
      "b",
      "d",
      "rounds"
    ],
    "doc": "returns list of states after each round (index 0 = init)"
  },
  {
    "name": "compress",
    "line": 20,
    "arguments": [
      "h",
      "m",
      "tlo",
      "thi",
      "b",
      "d",
      "rounds",
      "full"
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
