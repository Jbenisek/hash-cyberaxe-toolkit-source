# stats_chk.py - check2-4: summary of my chk38 runs (campX.log, campY.log): per mode the mean of the estimates Z,

Source: `research/sha256grid/check2-4/stats_chk.py`

Public SHA-256: `631ef0abea6ce99ccad96d8d9bcb1e97c19f8cd9cc9e0385e159e13b8c76d45a`

## Purpose recorded in the source

stats_chk.py - check2-4: summary of my chk38 runs (campX.log, campY.log): per mode the mean of the estimates Z,
relative sd, one-sided 99% Student bounds (as in the filed rules), stage means, verification failures, and the gain
factors g = mean(mode) / mean(C) with the conservative ratio (99% lower of the mode / 99% upper of C).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "math",
  "re",
  "statistics",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
