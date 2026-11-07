#!/bin/bash
# background: exhaustive K=7 (6 parts, decreasing order) + random minimal bases with key scan (2 procs)
cd "$(dirname "$0")"
for p in 0 1 2 3 4 5; do
  timeout 1800 ./vs my_fixed.txt full 7 $p 6 > full7_p$p.out 2>&1 &
done
timeout 1800 ./vs my_fixed.txt rand 20000 1 400 > rand_s1.out 2>&1 &
timeout 1800 ./vs my_outhalf.txt rand 3000 2 0 > rand_oh_s2.out 2>&1 &
wait
echo "run2 done $(date)" >> run2.log
