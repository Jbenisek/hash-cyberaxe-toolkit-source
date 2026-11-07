#!/bin/bash
# positive control for vfull: count full-closure 8-sets in the branch (0,1) (first index 0, first pair only)
cd "$(dirname "$0")"
timeout 1500 ./vfull vsys_fixed.txt 8 0 1000 0 > vfull_k8_branch01.out
echo "k8 branch done $(date)" >> vfull_run.log
