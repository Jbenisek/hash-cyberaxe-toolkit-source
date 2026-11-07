#!/bin/bash
# usage: run_samples.sh R worker deadline_epoch  -- first-centre-only executions, seeds 100000*R+1000*worker+i, line = seed mod 3 (R=1) or fixed line 0 (R=2 uses LINE_FIXED=1)
cd "$(dirname "$0")"
R=$1; w=$2; dl=$3; i=0
while [ "$(date +%s)" -lt "$dl" ]; do
  s=$((100000*R+1000*w+i)); i=$((i+1))
  if [ "${LINE_FIXED:-0}" = 1 ]; then j=0; else j=$((s%3)); fi
  nice -n 10 ./lean_attack $R 1 $s $j 1 0 0 ${LINE_FIXED:-0} > logs/r${R}_s$s.txt 2>&1
done
