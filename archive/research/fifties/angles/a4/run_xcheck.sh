#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run_xcheck.sh - the four brief CNFs (with format constraints) re-solved by two independent solvers.
D="${HASHCYBERAXE_WORKSPACE}"/research/fifties/angles/a4
cd "$D" || exit 1
for L in 47 59 61 62; do
  c=$(cadical -q -t 600 sat/c3_$L.cnf | grep '^s ')
  m=$(cryptominisat5 --verb 0 --maxtime 600 sat/c3_$L.cnf | grep '^s ')
  echo "L3=$L cadical: $c | cryptominisat5: $m"
done
