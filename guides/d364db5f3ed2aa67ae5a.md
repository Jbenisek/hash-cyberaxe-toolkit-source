# ntt

Source: `research/poseidon/orchard/exec_r4/ntt.c`

Public SHA-256: `2641f8b3c71ce1760f4c56b6209e9ddb52618fc57872430f552af3dfd7637a3d`

## Purpose recorded in the source

include "common.h"
include "pallas_consts.h"

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/exec_r4/proof_template_exec.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
