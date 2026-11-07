# common

Source: `research/poseidon/orchard/exec_r4b/common.h`

Public SHA-256: `f8e05a0edc0774f0d9a0027eada8e39b6fc46503fcf5d3a97a35221177d23d91`

## Purpose recorded in the source

ifndef COMMON_H
define COMMON_H
include "pallas.h"
include <stdint.h>
include <stddef.h>
include <stdlib.h>
include <string.h>
include <stdio.h>
define LD(n)  do { X.ld  += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
define ST(n)  do { X.st  += (uint64_t)(n); X.ctl += (uint64_t)(n); } while (0)
define CTL(n) (X.ctl += (uint64_t)(n))

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/exec_r4b/proof_template_exec.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
