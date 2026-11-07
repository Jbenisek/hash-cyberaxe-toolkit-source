# corex

Source: `research/newpaths/variants/corex.c`

Public SHA-256: `09b5ee6441132017e52530afe8e5a24f2e9542e473362b2e74c07f7565235873`

## Purpose recorded in the source

Guess sets built on a small "self-checked" core: every r-set of class representatives whose closure has r-1 checks
(dimension 1) is extended by exactly E more representatives (canonical order) until the closure is everything.
Prints "SOL core... extras..." for split.c.   usage: corex model r E
include <stdio.h>
include <stdlib.h>
define MAXR 4096

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/newpaths/variants/README.txt
- research/newpaths/variants/RESULTS.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
