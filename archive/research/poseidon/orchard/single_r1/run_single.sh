#!/bin/bash
# usage: run_single.sh seed   -> logs/single_<seed>.txt (exit status on the last line)
cd "$(dirname "$0")"
mkdir -p logs
[ -x ./single ] || ./build.sh single
nice -n 10 ./single $1 > logs/single_$1.txt 2>&1
echo "EXIT $?" >> logs/single_$1.txt
