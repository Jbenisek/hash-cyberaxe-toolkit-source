# check2-1: run when chain B is done (one Python process at a time, alongside chain A's kissat)

Source: `research/sha256grid/check2-1/mid.sh`

Public SHA-256: `aa9143e22e24eda8fe1d4f60191761e89e06bcc3ba9640aa4cc3248d5bd8feb3`

## Purpose recorded in the source

check2-1: run when chain B is done (one Python process at a time, alongside chain A's kissat)

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
