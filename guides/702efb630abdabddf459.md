# dependence: fix 9 words, vary t_hi only

Source: `research/dig/incoming2/blake3-r2-G05-U03/work/t2.py`

Public SHA-256: `cd6cdb01ec31febc516a57bee4b07699047050bf0e49a23010eb357ababa00f7`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "b3ctr",
  "collections",
  "math",
  "random",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "rf",
    "line": 5,
    "arguments": [
      "hi"
    ],
    "doc": ""
  },
  {
    "name": "traces",
    "line": 11,
    "arguments": [
      "w",
      "t",
      "n"
    ],
    "doc": ""
  },
  {
    "name": "e1b",
    "line": 18,
    "arguments": [
      "tr",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "e3d",
    "line": 21,
    "arguments": [
      "tr",
      "w"
    ],
    "doc": ""
  },
  {
    "name": "hw",
    "line": 24,
    "arguments": [
      "x"
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
