#!/bin/bash
# usage: full_run.sh K sysname...   runs fullsets with 8 parts for each system, sequentially
cd "$(dirname "$0")"
K=$1; shift
for s in "$@"; do
  for p in 0 1 2 3 4 5 6 7; do
    timeout 7200 ./fullsets sys_$s.txt $K $p 8 > full_${s}_k${K}_p$p.out &
  done
  wait
  echo "$s K=$K done $(date)" >> full_run.log
done
