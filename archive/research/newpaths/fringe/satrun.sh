#!/bin/bash
# usage: satrun.sh <timeout_s> <parallel> <solver> <cnf>...   (solver: kissat|cadical|cms)
# writes <cnf>.<solver>.sol and appends "<cnf> <solver> exit=<code> secs=<wall>" to satrun.log
cd "$(dirname "$0")"
to=$1; par=$2; solver=$3; shift 3
run_one() {
  f=$1
  t0=$(date +%s.%N)
  case $solver in
    kissat) timeout "$to" kissat -q "$f" > "$f.kissat.sol"; rc=$? ;;
    cadical) timeout "$to" cadical -q "$f" > "$f.cadical.sol"; rc=$? ;;
    cms) timeout "$to" cryptominisat5 --verb 0 "$f" > "$f.cms.sol"; rc=$? ;;
  esac
  t1=$(date +%s.%N)
  echo "$f $solver exit=$rc secs=$(echo "$t1 - $t0" | bc)" >> satrun.log
}
n=0
for f in "$@"; do
  run_one "$f" &
  n=$((n+1))
  if [ "$n" -ge "$par" ]; then wait -n; n=$((n-1)); fi
done
wait
