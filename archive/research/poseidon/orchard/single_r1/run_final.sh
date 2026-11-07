#!/bin/bash
# usage: run_final.sh seed [verbose]  -> logs/single_<seed>.txt
cd "$(dirname "$0")"
mkdir -p logs
nice -n 10 ./single $1 ${2:-0} > logs/single_$1.txt 2>&1
echo "EXIT $?" >> logs/single_$1.txt
