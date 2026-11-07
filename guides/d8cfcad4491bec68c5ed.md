# attack

Source: `research/poseidon/orchard/tf_test/attack.h`

Public SHA-256: `9130524d6151a7383cb22af3bca8eed2f079744e02cf82c6e390ef2a37c97394`

## Purpose recorded in the source

ifndef ATTACK_H
define ATTACK_H
include "common.h"
endif

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/tf_test/proof_template.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
