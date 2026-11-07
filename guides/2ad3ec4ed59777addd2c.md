# ls all

Source: `research/newpaths/variants/ls_all.c`

Public SHA-256: `c3f7edabc395f726245a7fcd9900ca378e1928e997dcd83e234cacaebf396017`

## Purpose recorded in the source

Randomized local search for small guess sets (upper bounds) on models of any size (n <= 1024).
Construction: greedy (candidate words in rules with exactly one other unknown, random tie-break), then
improvement: drop two guesses and try every single replacement (k -> k-1); plateau moves: swap one guess.
usage: ls model seconds seed      prints improving solutions "BEST k: v1 v2 ..."
include <stdio.h>
include <stdlib.h>
include <string.h>
include <time.h>
define MAXN 1024
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
