# outbuf

Source: `research/poseidon/pkg_r7_paper/v3/src/outbuf.h`

Public SHA-256: `313e6f16f8cbc642b36b80f1163403110bdcaada8ce686c867ad3199431862ff`

## Purpose recorded in the source

ifndef OUTBUF_H
define OUTBUF_H
include <stddef.h>
define OUTCAP 8192              /* capacity of the output buffer: the whole report is appended to it and written by one write */
endif

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/poseidon/pkg_r7_paper/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
