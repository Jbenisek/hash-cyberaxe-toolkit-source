#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o split split.c || exit 1
NOISE=2 timeout 100 ./split sys_fixed_plain.txt greedy 400 11 7 > g7n2.txt 2> g7n2.log &
NOISE=4 timeout 100 ./split sys_fixed_plain.txt greedy 400 12 7 > g7n4.txt 2> g7n4.log &
wait
cat g7n2.log g7n4.log
cat greedy7_a.txt greedy7_b.txt g7n2.txt g7n4.txt | while read -r l; do echo $l | tr ' ' '\n' | sort | tr '\n' ' '; echo; done | sort -u > covers7all.txt
wc -l covers7all.txt
