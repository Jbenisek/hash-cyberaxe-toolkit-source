# exp tail

Source: `research/dig/incoming3/blake3-r3-U46/work/exp_tail.py`

Public SHA-256: `47c3b7fef1f0a0c547280f9687fbf67965e756874a34c57a00719797f77ab6e0`

## Purpose recorded in the source

exp_tail.py - sample the unreduced lane sums of the add chains in the 'no internal masks' circuit (policy none).
Counts, per big add site, how often the unreduced value reaches T units (T*2^32); lane limit is 16 units (2^36).

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Imports

```json
[
  "b3scan",
  "json",
  "numpy",
  "os",
  "sys",
  "time"
]
```

## Read alongside

- research/dig/incoming3/D414-SHA3-R6-141-PROOF-ERRATA-20261014.json
- research/dig/incoming3/D415-SHA3-R6-141-PROOF-REFRESH-DRAFT-20261014.json

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
