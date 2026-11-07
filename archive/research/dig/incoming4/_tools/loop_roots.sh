#!/bin/bash
cd "$(dirname "$0")"
for s in 41 42 43 44 45 46; do
  nice -n 10 timeout 170 python exp_root.py $s 0 > root_run_$s.txt 2>&1
  if grep -q "'collision'" root_run_$s.txt; then echo "success seed $s" > root_success.txt; break; fi
done
echo finished > root_loop_done.txt
