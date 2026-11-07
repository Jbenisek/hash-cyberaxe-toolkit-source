# split

Source: `research/poseidon/pkg_r7_paper/v2/src/split.c`

Public SHA-256: `34564b9c67755602d63a587e5a30866d58a07456c1ab12ae39239947e5b7e46e`

## Purpose recorded in the source

include "attack.h"
include "pallas_consts.h"
include "hgcd.h"
define CL_MAX 152          /* classical Euclid up to this degree, the fast gcd above */

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/pkg_r7_paper/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
