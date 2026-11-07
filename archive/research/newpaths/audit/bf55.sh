#!/bin/bash
cd "$(dirname "$0")"
start=$(date +%s)
timeout 3000 ./bf3 rules_fixed_len55_plain.txt 7 0 1 > bf3_fixed55_plain_k7.out 2>&1
end=$(date +%s)
echo "fixed len55 plain kmax=7 nproc=1: $((end-start)) s; parts done: $(grep -c DONE bf3_fixed55_plain_k7.out)/1; covering sets found: $(grep -c FOUND bf3_fixed55_plain_k7.out)" >> bf_summary.log
