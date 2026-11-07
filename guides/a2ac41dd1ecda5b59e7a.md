# attack

Source: `research/poseidon/orchard/exec_r5b/attack.h`

Public SHA-256: `6e0886d3c55eb7b87c1e3e5fe35c2918325d60098791d0fc4313b0fc4c51428b`

## Purpose recorded in the source

ifndef ATTACK_H
define ATTACK_H
include "common.h"

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/exec_r5b/proof_template_exec.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
