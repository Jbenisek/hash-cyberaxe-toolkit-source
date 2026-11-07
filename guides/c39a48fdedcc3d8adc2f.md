# single

Source: `research/poseidon/orchard/exec_r2_line/single.c`

Public SHA-256: `06e76949c756d400fbce6c244c140453226fc29ae87474f0345063dfb6bf878c`

## Purpose recorded in the source

include "attack.h"
include "hgcd.h"
include "pallas_consts.h"
include <time.h>
include <math.h>
ifndef RR
define RR 2
endif
ifndef LINE
define LINE 0
endif
define AMAX (RR == 1 ? 16 : 18)          /* 3 * 2^AMAX >= 2m - 1, m = 5^(6+RR) - 1: the largest transform length */
define MAXTR 64

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/orchard/exec_r2_line/proof_template_exec.md
- research/poseidon/d189_gpu_results.jsonl
- research/poseidon/d192_r2_results.jsonl

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
