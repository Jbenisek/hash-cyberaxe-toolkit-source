# also current files not in prev, within blake3-r2 and src

Source: `research/pkg7/work/fix3/check/cmp.py`

Public SHA-256: `dc1b4ed8bb26c22534cb7f7e0a7d34f3b3b142a69da6340c486c408e9e9552e7`

## Purpose recorded in the source

also current files not in prev, within blake3-r2 and src

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "difflib",
  "hashlib",
  "os",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "sha",
    "line": 6,
    "arguments": [
      "path"
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
