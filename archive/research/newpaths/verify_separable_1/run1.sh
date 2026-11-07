#!/bin/bash
# build vs.c, quick sanity runs (foreground, short)
cd "$(dirname "$0")"
gcc -O3 -march=native -o vs vs.c || { echo BUILD_FAIL; exit 1; }
echo "== stats K=4 (expect max 25 per separable R1)"
timeout 100 ./vs my_fixed.txt stats 4
echo "== full K=5 single part (quick self-test; expect none)"
time timeout 100 ./vs my_fixed.txt full 5 0 1 | tail -1
echo "== full K=8 on a tiny slice to see that 8-sets are found"
timeout 60 ./vs my_fixed.txt full 8 0 4000 | head -3
