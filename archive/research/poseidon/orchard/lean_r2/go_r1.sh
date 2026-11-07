#!/bin/bash
cd "$(dirname "$0")"
DL=$(( $(date +%s) + 3600 ))
( ulimit -s 64; nice -n 10 ./lean_attack 1 2 7 1 1 > logs/ledger_r1.txt 2>&1 ) &
./run_samples.sh 1 1 $DL &
./run_samples.sh 1 2 $DL &
wait
