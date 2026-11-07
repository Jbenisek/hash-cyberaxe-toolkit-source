#!/bin/bash
cd "$(dirname "$0")"
for s in fixed_plain fixed_tables; do
  ( timeout 3000 ./split sys_$s.txt stats 4 > stats_${s}_k4.out
    timeout 3000 ./split sys_$s.txt stats 5 > stats_${s}_k5.out ) &
done
wait
