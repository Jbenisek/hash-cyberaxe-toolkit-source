# ntt

Source: `research/poseidon/orchard/exec_r6fast/ntt.c`

Public SHA-256: `0532c61876de54252dc3e96be17d19e278193f35252aeaf495b51db9634b0a7c`

## Purpose recorded in the source

include "common.h"
include "par.h"
include "pallas_consts.h"
ifndef NO_R2
endif

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
