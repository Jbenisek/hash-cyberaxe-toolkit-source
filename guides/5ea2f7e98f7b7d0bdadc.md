# grouphull

Source: `research/fifties/perspectives/joint/grouphull.c`

Public SHA-256: `8d9e08da5217c0ccf182595c64cf59d04f6f8247f0f33bb88f19934b0aecce5e`

## Purpose recorded in the source

grouphull.c - conditional GF(2) structure of R inside one (context, member) group, over the WHOLE cube j < 2^21.
Reuses the pkgCG algebra of ../data/gen.c (step CO + step CT up to E1/E3; no compression needed because
R = K1 ^ K3 exactly, DATA.md). For each group: affine rank of {R(j)} after 2^10, 2^14 and 2^21 cube points, and
whether 0 lies in the affine hull (every relation a.R = const has const = 0).
  grouphull check <inputs.u32> <keys.u32>      recompute K1, K3 for every stored row and compare
  grouphull <groups> <seed>
define main gen_main_unused
include "../data/gen.c"
undef main
include <omp.h>
include <math.h>

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/fifties/perspectives/joint/RESULT.md

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
