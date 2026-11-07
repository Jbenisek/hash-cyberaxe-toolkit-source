# gen

Source: `research/blake3_r5/b5/gen_c/gen.c`

Public SHA-256: `97ce272cef1f4b0dc13ebcbb8fa7c4f9d750c6506fc42104b33e3e1ae69003ca`

## Purpose recorded in the source

ifndef NMAX
define NMAX 31863                 /* nodes: constant 0, 256 inputs, one per gate */
endif
ifndef CODE_BYTES
define CODE_BYTES 1221192
endif
define ROUNDS 5
define N 256
define REC 36
define CTR_BYTES 16384
define NODE(s) (((s) >> 1) & 0xFFFFu)
define REG(s) ((s) >> 17)
define ZERO 0u
define ONE 1u

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/blake3_r5/b5/proof_t.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
