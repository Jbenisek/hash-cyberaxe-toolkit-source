# freedom3

Source: `research/sha256grid/map-r37/freedom/freedom3.c`

Public SHA-256: `1ac0bcd19b390f7789eea71689f4f9ef746e3d15e7a8e44a0eb45bae00748d57`

## Purpose recorded in the source

include <stdio.h>
include <stdlib.h>
include "consts.h"
define ROR(x,n) (((x) >> (n)) | ((x) << (32 - (n))))

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
