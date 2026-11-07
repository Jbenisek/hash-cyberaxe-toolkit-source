#!/bin/bash
# usage: run_stats.sh worker_id deadline_epoch binary outdir  -- one centre per process, seeds 1000*worker+i, line j = seed mod 3
cd "$(dirname "$0")"
w=$1; dl=$2; bin=${3:-./lean_final}; dir=${4:-logs/stats_b}; i=0
mkdir -p $dir
while [ "$(date +%s)" -lt "$dl" ]; do
  s=$((10000*w+i)); i=$((i+1))
  nice -n 10 $bin 1 1 $s $((s%3)) 1 > $dir/seed_$s.txt 2>&1
done
