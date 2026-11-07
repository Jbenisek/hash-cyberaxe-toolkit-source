#!/bin/bash
# usage: build_k.sh K  -> test_keep_K with hgcd_base_k = K
cd "$(dirname "$0")"
gcc -O3 -march=native -DBASEK=$1 -Wno-unused-function -o test_keep_$1 test_keep.c common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c -lm
