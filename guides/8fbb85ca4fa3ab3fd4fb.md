# usage: run_many.sh <timeout_s> <cnf>...   runs kissat on each in parallel; prints one line per file

Source: `research/newpaths/audit/orig/run_many.sh`

Public SHA-256: `277bd814457c3b3e499a3a3572d49c29f12aa0e6e330f522c6055239a90a46f3`

## Purpose recorded in the source

usage: run_many.sh <timeout_s> <cnf>...   runs kissat on each in parallel; prints one line per file

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
