# build records

Source: `research/dig/incoming2/blake3-r2-G05-U08/work/build_records.py`

Public SHA-256: `15f467705f1dbfdf8d0cf58f43ccba429d11bee3ce1310258ead06aa2c199582`

## Purpose recorded in the source

Read the source and linked research notes for this program's role.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "json",
  "os"
]
```

## Entry points

```json
[
  {
    "name": "rd",
    "line": 6,
    "arguments": [
      "f"
    ],
    "doc": ""
  },
  {
    "name": "add",
    "line": 24,
    "arguments": [
      "cell",
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
