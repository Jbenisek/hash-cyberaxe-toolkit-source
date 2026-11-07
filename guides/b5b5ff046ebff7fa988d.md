# check

Source: `research/newpaths/collision_pattern/check.py`

Public SHA-256: `729f36bb6112872036385c0423764a62baad903876b02e4c1cf8b9fd3ec3713b`

## Purpose recorded in the source

check.py: the recovered parameters reproduce every found pair (words from the runs' own code = the saved
message A), every hit is a collision with no construction failure, null trials are valid and almost never collide.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "load",
  "numpy"
]
```

## Read alongside

- research/newpaths/collision_pattern/results.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
