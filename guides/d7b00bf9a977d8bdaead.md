# e3brute

Source: `research/newpaths/counter_next/knobs/e3brute.c`

Public SHA-256: `e784d73eb6b1d901414f170803296edd78fdf9fdee87207da52aeb4fd1ad6c14`

## Purpose recorded in the source

include <stdio.h>
include <stdlib.h>
include <stdint.h>
define Y3 0x8127c181u
define Y3B 0x7edf3e7eu
define ETA 0x830303cfu
define NT 512

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
