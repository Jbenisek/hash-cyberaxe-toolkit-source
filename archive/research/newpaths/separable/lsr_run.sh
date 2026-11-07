#!/bin/bash
cd "$(dirname "$0")"
timeout 1500 ./lsearch_r sys_fixed_t2.txt 11 30 100000 7 > lsr_fixed_t2.out &
timeout 1500 ./lsearch_r sys_outhalf_t2.txt 12 20 100000 15 > lsr_outhalf_t2.out &
wait
echo "lsr done $(date)" >> ls_run.log
