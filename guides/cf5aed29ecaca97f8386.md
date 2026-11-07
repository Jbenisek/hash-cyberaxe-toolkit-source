# Context check on the organizer verifier (read-only import, no file writes).

Source: `research/newpaths/flag_audit/ctx_check.py`

Public SHA-256: `4bfe0dc20a077621b50fc84f2bcf215fcb219f6db1bf8ea1697abe03dc030332`

## Purpose recorded in the source

Context check on the organizer verifier (read-only import, no file writes).
Logs every compression call: role, cv origin, counter (v12,v13), block_len (v14), flags (v15).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "importlib.util",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "tag",
    "line": 15,
    "arguments": [
      "cv"
    ],
    "doc": ""
  },
  {
    "name": "wrapped",
    "line": 21,
    "arguments": [
      "cv",
      "words",
      "counter",
      "block_len",
      "flags",
      "rounds"
    ],
    "doc": ""
  },
  {
    "name": "run",
    "line": 33,
    "arguments": [
      "data",
      "label"
    ],
    "doc": ""
  },
  {
    "name": "compact",
    "line": 42,
    "arguments": [
      "data",
      "label"
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
