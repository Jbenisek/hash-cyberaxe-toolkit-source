#!/bin/bash
cd "$(dirname "$0")"; mkdir -p ../logs
bash build_exec.sh 2>&1 | grep -E "error" ; ( ulimit -s 64; nice -n 19 timeout 58 ./exec_attack 0 3 1 0 1 0 0 1 > ../logs/small_r0.txt ); grep -E "CENTRE|SUMMARY|FAULT|HALF" ../logs/small_r0.txt; R=0 python3 verify_collision.py ../logs/small_r0.txt
