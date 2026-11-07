#!/bin/bash
# usage: run_many2.sh <seconds> <cnf>...  parallel kissat with its own --time limit (no 'timeout' wrapper to be pkilled)
cd "$(dirname "$0")"
s=$1; shift
for f in "$@"; do
  ( kissat -q --time="$s" "$f" > "${f%.cnf}.out"; echo "$f exit=$? (10 SAT, 20 UNSAT, 0 unknown/time)" >> run_many2.log ) &
done
wait
