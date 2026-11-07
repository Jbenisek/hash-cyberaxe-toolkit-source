# local38

Source: `research/sha256grid/scout2-4/local38.c`

Public SHA-256: `b56fd1a67c0366d6e18011f651b250742833836388ddf03f2e6555aa42060a15`

## Purpose recorded in the source

local38.c - scout2-4: exact local counts behind the relaxed-SMC gains (r38 characteristic, filed pkgR38a data).
 (1) W23: words w with the cells of W23 (x-values, XOR pattern of w vs w - dW23, the 4 two-bit conditions) versus
     words with only the modular condition that matters downstream, s1(w) - s1(w - dW23) = published ds1(W23)
     (it fixes dW25; dW30 = dW23 + ds0(W15) holds for every w).
 (2) W25: cells ('n' at bit 29 and the 3 two-bit conditions) versus s1(w) - s1(w - dW25) = published ds1(W25)
     (it fixes dW27).
 (3) Row 17 for the first K words of G: over all 2^32 values of E17^x, the number with every cell of row 17 AND the
     published modular differences of row 18, versus the number with the row-18 modular differences only.
usage: local38 K
include <stdio.h>
include <stdlib.h>
include <string.h>
include <stdint.h>
include "consts38.h"
define ROR(x,n) (((x)>>(n))|((x)<<(32-(n))))

## Source inspection and available execution evidence

static-source-review; not-replayed-for-publication.

A run budget is not specified in this guide. Check loop bounds, worker counts and memory requirements before choosing an experiment size.

## Read alongside

Companion documents are not listed here. Use the linked source for interfaces and prerequisites.

## Failure modes

- Missing historical dependencies or input files.
- Domain or target parameters may differ from the intended experiment.
- Publication redactions can change executable strings; compare source and public digests.
