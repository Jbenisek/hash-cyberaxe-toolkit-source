#!/bin/bash
# builds and runs the rows==2 unit test with a normal libc (not shipped). usage: bash test/build_t.sh
cd "$(dirname "$0")/.." || exit 1
L="common.c ntt.c poly.c lean.c line.c split.c hgcd.c pallas.c"
gcc -O2 -march=native -DARENA=200000000 -o test/t_r2_new test/t_r2.c $L 2>&1 | grep -v "warning\|note:" | head -20
nice -n 10 test/t_r2_new
