# Full K3 scans for several x-differences, one after another (one process at a time).

Source: `research/newpaths/untried/b3-mode/k3_multi.sh`

Public SHA-256: `b0b8b109bbf6a32216f656c47d08669b81ea2566ccaaa75da650dd3b4a785e98`

## Purpose recorded in the source

Full K3 scans for several x-differences, one after another (one process at a time).
Usage: k3_multi.sh <flags> <dx hex> [<dx hex> ...]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/newpaths/untried/b3-mode/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
