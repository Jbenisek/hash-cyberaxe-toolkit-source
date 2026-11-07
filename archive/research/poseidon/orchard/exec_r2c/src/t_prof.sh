#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -o test_hgcd_p test_hgcd.c common.c ntt.c poly.c hgcd.c pallas.c -lm 2>&1 | grep -i " error"
( ulimit -s 64; nice -n 19 ./test_hgcd_p ${1:-195312} 1 0 50 96 0 17 )
