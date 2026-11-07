# mk

Source: `research/dig/incoming2/sha256-38-G07-U03/work/mk.py`

Public SHA-256: `e5621cdf59c58d0365ca630b425cf6c03147cabc12ee39c6a94a43e37df54782`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "add_cell",
  "json",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "rec",
    "line": 7,
    "arguments": [
      "cid",
      "obj",
      "q",
      "labels",
      "status",
      "number",
      "notes"
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
