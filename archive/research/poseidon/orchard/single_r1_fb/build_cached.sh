#!/bin/bash
# variant with cached spectra of mu and g in the powering: binary single_c
set -e
cd "$(dirname "$0")"
CF="-O3 -march=native -Wall -Wextra -Wno-unused-function -Wno-unused-variable -Wno-unused-parameter"
gcc $CF -DCACHED_POW -o single_c single.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm
