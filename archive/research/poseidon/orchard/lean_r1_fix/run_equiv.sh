#!/bin/bash
# re-run two campaign seeds of the earlier build with the final build and compare centre outcomes and outputs
cd "$(dirname "$0")"
mkdir -p logs/equiv_checks
for s in 2000 3000; do
  nice -n 10 ./lean_final 1 1 $s $((s%3)) 1 > logs/equiv_checks/final_seed_$s.txt 2>&1
done
