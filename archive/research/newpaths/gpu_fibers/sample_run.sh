#!/bin/bash
# build, then a sweep: W=6 (rot 3,2,2,1), W=7 (4,3,2,1), W=8 (4,3,2,1); N = 2^30; several seeds (different fixed words)
cd "$(dirname "$0")"
nvcc -O3 -arch=sm_86 -o fibers_sample fibers_sample.cu 2>&1 | grep -i error | head -3
for s in 1 2 3 4 5 6; do ./fibers_sample 6 3 2 2 1 30 $s; done
for s in 1 2 3 4; do ./fibers_sample 7 4 3 2 1 30 $s; done
for s in 1 2 3 4; do ./fibers_sample 8 4 3 2 1 30 $s; done
echo SWEEPDONE
