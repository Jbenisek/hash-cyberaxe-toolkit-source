# batch isd

Source: `research/newpaths/blake2/batch_isd.py`

Public SHA-256: `39ec3ff8190847182b06fd12151b87feb7fa64b9e58526e0fc193ba8c9bcf339`

## Purpose recorded in the source

Run a list of ISD configs sequentially, append one JSON line per config to the output file.
Usage: python -B batch_isd.py outfile "w,setting,objective,iters,seed" ...

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "isd",
  "json",
  "sys"
]
```

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
