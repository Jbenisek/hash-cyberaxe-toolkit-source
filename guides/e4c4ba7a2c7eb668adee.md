# make claim

Source: `research/blake3_r3/bitslice2/make_claim.py`

Public SHA-256: `7ca0ba1021d81febd36c26e5174ca297925a9f6e77c1b4930495d63577feea8d`

## Purpose recorded in the source

Builds claim.json, experiments/manifest.json, submission-note.md and dependencies.json (run after make_pkg.py).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "bsrho",
  "json",
  "math",
  "os",
  "re",
  "sys"
]
```

## Entry points

```json
[
  {
    "name": "span",
    "line": 17,
    "arguments": [
      "head",
      "nxt"
    ],
    "doc": "1-based inclusive line range from the heading starting with `head` to the line before the heading starting with `nxt`."
  }
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
