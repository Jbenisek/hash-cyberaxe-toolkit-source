# known vector: BLAKE3("") at 7 rounds

Source: `research/dig/incoming2/blake3-r2-G05-U11/work/validate_own.py`

Public SHA-256: `f6a2f325767a674631fd823aaf816885cda2b8a2cca20a6bb13ffbc8b4fa9150`

## Purpose recorded in the source

known vector: BLAKE3("") at 7 rounds
own: empty message root block: cv=IV,m=0,t=0,b=0,flags=1|2|8=11

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "b3own",
  "importlib.util",
  "numpy",
  "random",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
