# build-only check of the shipped sources at r = 7 with the ledger arena (wsl -d Ubuntu -- bash build_r7.sh); prints size and a sha256 prefix of the binary

Source: `research/poseidon/pkg_r7_paper/v2/tests/build_r7.sh`

Public SHA-256: `a5365dcd342f2c602c39869e0f877348a52cc3d3426eee28d6e5de9b36fa1ab3`

## Purpose recorded in the source

build-only check of the shipped sources at r = 7 with the ledger arena (wsl -d Ubuntu -- bash build_r7.sh); prints size and a sha256 prefix of the binary

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/pkg_r7_paper/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
