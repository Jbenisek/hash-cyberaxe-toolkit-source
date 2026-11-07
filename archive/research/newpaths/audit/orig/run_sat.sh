#!/bin/bash
# usage: run_sat.sh <variant> <length> <T> <k...>
cd "$(dirname "$0")"
v=$1; l=$2; T=$3; shift 3
for k in "$@"; do
  timeout 600 kissat -q "gd_${v}_${l}_k${k}_T${T}.cnf" > "sat_${v}_${l}_k${k}.out"
  echo "k=$k exit=$? (10 SAT, 20 UNSAT, 124 timeout)"
done
