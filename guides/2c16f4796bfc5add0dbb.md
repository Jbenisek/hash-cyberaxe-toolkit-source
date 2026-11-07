# common

Source: `research/poseidon/orchard/solve/common.h`

Public SHA-256: `362b4f433933b8b868659a8cd32d8c226d891a1a63bdbfef76808760c67eeec9`

## Purpose recorded in the source

ifndef COMMON_H
define COMMON_H
include "../impl/pallas.h"
include <stdint.h>
include <stddef.h>
include <stdlib.h>
include <string.h>
include <stdio.h>
define LD(n)  (X.ld  += (uint64_t)(n))
define ST(n)  (X.st  += (uint64_t)(n))
define CTL(n) (X.ctl += (uint64_t)(n))
define NEW_FP(n) ((fp *)xalloc((size_t)(n) * sizeof(fp)))

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
