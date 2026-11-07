# check dbg

Source: `research/newpaths/nb_verify_sidepaths_0/check_dbg.py`

Public SHA-256: `30962048622aff215371a00aa8987ce98448b1d9e8ab84e9f5dcfca1dcd899ca`

## Purpose recorded in the source

Check cvrate's DBG lines: for each printed trial, rebuild the pair with s8_check.build_cv, hash the full
messages with the organizer reference at 2 rounds, and compare the residual (digest XOR, words 1,3,4,6).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "s8_check",
  "struct",
  "sys"
]
```

## Read alongside

- research/newpaths/nb_verify_sidepaths_0/README.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
