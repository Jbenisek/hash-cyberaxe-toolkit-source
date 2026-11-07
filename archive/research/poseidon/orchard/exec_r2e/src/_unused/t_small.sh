#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -DHGPROF -o test_hgcd_p test_hgcd.c common.c ntt.c poly.c hgcd.c pallas.c -lm 2>&1 | grep -iE "error|warning: unused" 
for a in "3000 3 1" "2001 0 1" "777 40 1" "5000 7 1" "1200 1 1"; do ( ulimit -s 64; nice -n 19 ./test_hgcd_p $a | grep -E "HGCD|hgcd:" ); done
