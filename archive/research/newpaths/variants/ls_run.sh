#!/bin/bash
# usage: ls_run.sh <secs> <seed> <model>...  (runs two at a time)
cd "$(dirname "$0")"
gcc -O3 -march=native -o ls ls.c 2>/dev/null
s=$1; seed=$2; shift 2
for m in "$@"; do
  ( timeout $((s+30)) ./ls models/$m.mdl $s $seed > res/ls_${m}_s$seed.out ) &
  while [ $(jobs -r | wc -l) -ge 2 ]; do sleep 1; done
done
wait
for m in "$@"; do echo "$m: $(grep BEST res/ls_${m}_s$seed.out | tail -1 | cut -c1-12) $(tail -1 res/ls_${m}_s$seed.out)"; done
