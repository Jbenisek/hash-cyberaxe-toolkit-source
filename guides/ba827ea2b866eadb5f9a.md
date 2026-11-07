# usage: bash restage.sh <full uuid of our filed B3R6 entry>   (WSL; run after the owner has filed r6). Rebuilds the r5 package with the real id, restages pos_b3r5, runs intake + rul

Source: `research/blake3_r5/b5/restage.sh`

Public SHA-256: `4f02c3800da39d5c6cdb4bbba316b845b2326240c592ca96067411c5f07f3e8a`

## Purpose recorded in the source

usage: bash restage.sh <full uuid of our filed B3R6 entry>   (WSL; run after the owner has filed r6). Rebuilds the r5 package with the real id, restages pos_b3r5, runs intake + rulecheck, writes launch/submit_pareto_b3r5.sh

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/blake3_r5/b5/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
