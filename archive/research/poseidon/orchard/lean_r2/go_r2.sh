#!/bin/bash
cd "$(dirname "$0")"
DL=$(( $(date +%s) + 7200 ))
export LINE_FIXED=1
( ulimit -s 64; nice -n 10 ./lean_attack 2 2 7 0 1 0 0 1 > logs/ledger_r2.txt 2>&1 ) &
./run_samples.sh 2 1 $DL &
./run_samples.sh 2 2 $DL &
wait
