#!/bin/bash
cd "$(dirname "$0")"
for i in 0 1 2; do
  nice -n 10 ./lean_attack 2 3 $((2000+i)) $i 1 > logs/r2_run$i.txt 2>&1 &
done
wait
