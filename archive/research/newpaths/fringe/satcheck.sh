#!/bin/bash
# usage: satcheck.sh <timeout> <cnf>...   quick foreground kissat runs, prints file, exit code and seconds
cd "$(dirname "$0")"
to=$1; shift
for f in "$@"; do
  t0=$(date +%s.%N)
  timeout "$to" kissat -q "$f" > "$f.kissat.sol"; rc=$?
  t1=$(date +%s.%N)
  echo "$f exit=$rc secs=$(echo "$t1 - $t0" | bc)"
done
