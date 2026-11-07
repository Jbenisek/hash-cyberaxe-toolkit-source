#!/bin/bash
# usage: cmscheck.sh <timeout> <cnf>...   cryptominisat5 (XOR detection on by default), prints exit code and seconds
cd "$(dirname "$0")"
to=$1; shift
for f in "$@"; do
  ( t0=$(date +%s.%N)
    timeout "$to" cryptominisat5 --verb 0 "$f" > "$f.cms.sol"; rc=$?
    t1=$(date +%s.%N)
    echo "$f cms exit=$rc secs=$(echo "$t1 - $t0" | bc)" ) &
done
wait
