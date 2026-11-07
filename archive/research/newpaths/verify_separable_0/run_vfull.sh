#!/bin/bash
# verify_separable_0: build vfull, run the K=7 exhaustive check in 8 parts (background, timeout 1800 s each)
cd "$(dirname "$0")"
gcc -O3 -march=native -o vfull vfull.c || { echo BUILD FAIL > vfull_run.log; exit 1; }
for p in 0 1 2 3 4 5 6 7; do
  timeout 1800 ./vfull vsys_fixed.txt 7 $p 8 -1 > vfull_k7_p$p.out &
done
wait
echo "K=7 done $(date)" >> vfull_run.log
