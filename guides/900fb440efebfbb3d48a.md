# gen

Source: `research/blake3_r5/b8r5/gen_c/gen.c`

Public SHA-256: `7758bdfdcf4e1019b8d9292b2dcae139848f095e447d8cbd992c7862a98eb3f9`

## Purpose recorded in the source

ifndef NMAX
define NMAX 10056                 /* nodes of the larger segment: constant 0, inputs, one per gate */
endif
ifndef CODE_BYTES
define CODE_BYTES 795996
endif
define KPRE 2
define N 256
define SB 256
define WB 768
define TB 1312
define REC 36
define CTR_BYTES 16384
define NODE(s) (((s) >> 1) & 0xFFFFu)
define REG(s) ((s) >> 17)
define ZERO 0u
define ONE 1u
define NONE 0xFFFFu

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/blake3_r5/b8r5/proof_t8.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
