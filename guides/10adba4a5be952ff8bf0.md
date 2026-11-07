# test loop

Source: `research/poseidon/orchard/exec_r2e/src/_unused/test_loop.c`

Public SHA-256: `1893f0535684f778e2733e0d5d42063e127cafc012ad74ce8594900af64cc157`

## Purpose recorded in the source

include "common.h"
include <time.h>

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/exec_r2e/proof_template.md
- research/poseidon/orchard/exec_r2e/proof_template_exec.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
