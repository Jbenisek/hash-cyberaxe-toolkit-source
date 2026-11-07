# freedom2

Source: `research/sha256grid/map-r37/freedom/freedom2.c`

Public SHA-256: `647b6b9e492f3431aa8394c06d272a5494d8725703bc396d000f7c13703f043d`

## Purpose recorded in the source

include <stdio.h>
include <stdlib.h>
include <math.h>
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
