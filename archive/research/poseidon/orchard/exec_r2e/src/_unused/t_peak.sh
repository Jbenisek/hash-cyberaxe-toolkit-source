#!/bin/bash
cd "$(dirname "$0")"
gcc -O1 -g -rdynamic -fno-inline -DPEAKTRACE -o test_hgcd_t test_hgcd.c common.c ntt.c poly.c hgcd.c pallas.c -lm 2>&1 | grep -i " error"
( ulimit -s 64; nice -n 19 ./test_hgcd_t 195312 1 0 50 96 0 17 2>&1 | tail -40 )
