# count dups

Source: `research/fifties/angles/a6/count_dups.py`

Public SHA-256: `cdec7726f9644f68acf79b1bc195156d584ca8cdf99c6479d730e9abc14cbb57`

## Purpose recorded in the source

A6: count duplicate frame keys and duplicate tables (word table, rule-A table, both) from the GPU records.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "collections",
  "struct",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "dups",
    "line": 5,
    "arguments": [
      "items"
    ],
    "doc": "Number of items minus the number of distinct items, and the largest group."
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
