# work/tools/equiv.py in WSL: N batches in all, split over the given number of processes (at most three), each

Source: `research/pkg9/pkg/work/equiv_run.sh`

Public SHA-256: `7faae6c610cc4bfbf4d09e73c5023e01c1569e476328d4b53189ea75d58d85ac`

## Purpose recorded in the source

work/tools/equiv.py in WSL: N batches in all, split over the given number of processes (at most three), each
started with nice -n 5. Research helper, not submitted.

  wsl -d Ubuntu -- bash "./research/pkg7/work/equiv_run.sh" 200000 e1 2

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
