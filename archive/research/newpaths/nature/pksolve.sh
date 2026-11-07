#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# solve pre-generated period-K instances one after another (each capped), results in pksolve.out
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
echo "pksolve pid $$ start $(date)" >> pids.txt
for f in "$@"; do
  timeout ${CAP:-240} cryptominisat5 --verb 0 $f > ${f%.cnf}.sol 2>&1
  st=$(grep -m1 '^s ' ${f%.cnf}.sol)
  echo "$f -> ${st:-TIMEOUT(${CAP:-240}s)} $(date +%T)" >> pksolve.out
done
echo "pksolve done $(date)" >> pids.txt
