# mkrec

Source: `research/dig/incoming/blake3-r2-U07/work/mkrec.py`

Public SHA-256: `409a1f22d33b1124273af2732039d601caedad223800cfef02bb90f48d7a49eb`

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
    "line": 8,
    "arguments": [
      "w",
      "q",
      "obj",
      "question",
      "labels",
      "status",
      "number",
      "notes",
      "own"
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
