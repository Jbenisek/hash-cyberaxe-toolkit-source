#!/bin/bash
# usage: hunt.sh first_seed step count   -> runs seeds first, first+step, ... (sequentially), logs/single_<seed>.txt
cd "$(dirname "$0")"
mkdir -p logs
[ -x ./single ] || ./build.sh single
s=$1
for i in $(seq 1 $3); do
  nice -n 10 ./single $s > logs/single_$s.txt 2>&1
  echo "EXIT $?" >> logs/single_$s.txt
  s=$((s + $2))
done
