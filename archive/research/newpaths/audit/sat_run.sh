#!/bin/bash
# usage: sat_run.sh <solver: kissat|cadical|cms> <timeout_s> <cnf>   -> <cnf>.<solver>.out, line in sat_summary.log
cd "$(dirname "$0")"
s=$1; to=$2; f=$3
start=$(date +%s)
case $s in
  kissat) timeout "$to" kissat -q "$f" > "$f.$s.out"; rc=$? ;;
  cadical) timeout "$to" cadical -q "$f" > "$f.$s.out"; rc=$? ;;
  cms) timeout "$to" cryptominisat5 --verb 0 "$f" > "$f.$s.out"; rc=$? ;;
esac
end=$(date +%s)
echo "$s $f exit=$rc (10 SAT, 20 UNSAT, 124 timeout) $((end-start)) s" >> sat_summary.log
