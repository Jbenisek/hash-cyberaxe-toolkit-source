# Copies of the night's per-beta files for the longer list of betas (all betas with k at most 14), which the

Source: `research/pkg5/tools/fetch_totals.sh`

Public SHA-256: `09bc0fbfc90bc967ee8c1f8c038d1165e232abb99290f4c6a689459bcb73e0df`

## Purpose recorded in the source

Copies of the night's per-beta files for the longer list of betas (all betas with k at most 14), which the
night's scripts left in the WSL home only (~/hashsmash/night_main/scan/). Nothing is computed here.
tools/pkg5_data.py reads a per-beta file from evidence/ in place of research/night/main/ when the copy in
evidence/ holds more betas. The sum of each copy is printed next to the line of the night's own summary
file (research/night/main/extend_totals.txt), which must agree.

  wsl -d Ubuntu -- bash './research/pkg5/tools/fetch_totals.sh' [eta ...]

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
