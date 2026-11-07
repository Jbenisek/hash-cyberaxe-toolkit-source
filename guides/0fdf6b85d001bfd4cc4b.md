# zperm

Source: `research/fifties/av11/zperm.c`

Public SHA-256: `00307729475ae569d6026743133d589fe0071758ff11312346496a8d81c7cdb6`

## Purpose recorded in the source

Test: for fixed (b,f,h), is z -> y(b,h,z,f) a permutation of 2^32? (explains p_land = 2^-rho exactly)
Also tests fixed (b,h,z): f -> y, and fixed (b,z,f): h -> y (known non-permutation).
include <stdio.h>
include <stdlib.h>
include <stdint.h>
include <string.h>
define IV3 0xa54ff53au
define IV7 0x5be0cd19u

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

- research/fifties/av11/results_alt.json
- research/fifties/av11/results_alt_table.txt
- research/fifties/av11/results_main.json
- research/fifties/av11/results_main_table.txt

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
