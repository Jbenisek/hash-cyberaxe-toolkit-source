# exact dependency table: where does each round-0 message word get read in round 1 (PERM), per cancel channel

Source: `research/dig/incoming2/blake3-r2-G05-U08/work/e7_reads.py`

Public SHA-256: `4e3ceac6ded6fc355d7a8623f6927c9f204cc1ab3e40fc3aa3bb486150eecced`

## Purpose recorded in the source

exact dependency table: where does each round-0 message word get read in round 1 (PERM), per cancel channel

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Entry points

```json
[
  {
    "name": "where",
    "line": 4,
    "arguments": [
      "m"
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
