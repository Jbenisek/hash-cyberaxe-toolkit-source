# debug: RR=1 (RRX), MAXTR=K (default 8), random tapes from /dev/urandom, quick check of the coin-tape program: RRX=1 K=8 bash small_r1.sh

Source: `research/poseidon/pkg_r7_paper/v3/tests/small_r1.sh`

Public SHA-256: `0091608072dc16223e806400175a0255a538c8c539ef08e328670c2123b6e584`

## Purpose recorded in the source

debug: RR=1 (RRX), MAXTR=K (default 8), random tapes from /dev/urandom, quick check of the coin-tape program: RRX=1 K=8 bash small_r1.sh

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/pkg_r7_paper/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
