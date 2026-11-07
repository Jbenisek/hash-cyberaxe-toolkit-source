#!/bin/bash
cd "$(dirname "$0")"
gcc -O2 -o probe_cost probe_cost.c common.c ntt.c poly.c pallas.c -lm && ./probe_cost
size exec_attack > ../logs/size.txt; cat ../logs/size.txt
ps -eo pid,etime,pcpu,cmd | grep exec_attack | grep -v grep
