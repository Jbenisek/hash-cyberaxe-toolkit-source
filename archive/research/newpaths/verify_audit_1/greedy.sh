#!/bin/bash
cd "$(dirname "$0")"
timeout 110 ./split sys_fixed_plain.txt greedy 200 1 7 > greedy7_a.txt 2> greedy7_a.log &
timeout 110 ./split sys_fixed_plain.txt greedy 200 2 7 > greedy7_b.txt 2> greedy7_b.log &
wait
cat greedy7_a.log greedy7_b.log
sort -u greedy7_a.txt greedy7_b.txt | wc -l
