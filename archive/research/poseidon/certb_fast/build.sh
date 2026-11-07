#!/bin/bash
cd "$(dirname "$0")"
gcc -O2 -c pallas.c -o pallas.o || exit 1
nvcc -O3 -arch=sm_86 -std=c++17 -Xptxas -v -o certb_fast certb_fast.cu pallas.o 2> build.log
rc=$?
grep -E "error|warning|spill|Used" build.log | head -60
exit $rc
