#!/bin/bash
cd "$(dirname "$0")"
gcc -O3 -march=native -Wno-unused-result -o split split.c || exit 1
export PLAIN=1
timeout 60 ./split sys_fixed_plain.txt greedy 300 3 8 > greedy8p.txt 2> greedy8p.log
cat greedy8p.log
cat greedy8p.txt | while read -r l; do echo $l | tr ' ' '\n' | sort | tr '\n' ' '; echo; done | sort -u > covers8p.txt
wc -l covers8p.txt
head -40 covers8p.txt > c8p_head.txt
timeout 50 ./split sys_fixed_plain.txt split < c8p_head.txt > split8p.out
tail -1 split8p.out; head -3 split8p.out
