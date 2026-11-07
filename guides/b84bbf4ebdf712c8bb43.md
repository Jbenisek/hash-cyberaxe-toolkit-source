# Stage pkg10 (the cluster package with the judge's findings fixed) into the Yukon checkout and run the organizer's

Source: `research/pkg10/pkg/tools/stage_pkg10.sh`

Public SHA-256: `82c92b3f09f6314746e186e1b36c38dd1a351fe3102092da5713c109d04d9de1`

## Purpose recorded in the source

Stage pkg10 (the cluster package with the judge's findings fixed) into the Yukon checkout and run the organizer's
own intake on it: the mechanical check, the declared experiments and the judge evidence. On the owner's explicit
go of 2026-10-07. Runs no yukon command and submits nothing. The candidate folder is backed up first.

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/pkg10/pkg/tools/proof_lines_check.py
- research/pkg10/pkg/tools/proof_lines_pkg7.py

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
