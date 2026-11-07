#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# one process at a time, nice 10, 300 s cap each
cd "$(dirname "$0")"
for w in 8 16 32; do
  python3 gen.py $w w$w.cnf
  start=$(date +%s)
  nice -n 10 kissat --time=300 -q w$w.cnf > w$w.out 2>&1; rc=$?
  echo "W=$w rc=$rc secs=$(( $(date +%s)-start )) $(grep '^s ' w$w.out)" | tee -a summary.txt
  if [ $rc -eq 10 ]; then python3 verify.py w$w.cnf w$w.out "${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/spider_diff" | tee -a summary.txt; fi
done
echo DONE >> summary.txt
