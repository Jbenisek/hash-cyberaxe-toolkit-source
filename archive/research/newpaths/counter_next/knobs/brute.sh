#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# brute.sh: build e3brute and run it on every case of brute_cases.txt (partial system, targets of brute_targets.txt).
# Output: brute_out_<i>.txt per case.  One process at a time.
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter_next/knobs || exit 1
gcc -O3 -march=native -o e3brute e3brute.c || exit 1
tr ' ' '\n' < brute_targets.txt > brute_targets_nl.txt
i=0
grep -v '^#' brute_cases.txt | while read y Y9 w8 rest; do
  start=$(date +%s)
  ./e3brute $y $Y9 $w8 brute_targets_nl.txt > brute_out_$i.txt
  echo "case $i y=$y Y9=$Y9 w8=$w8: $(tail -1 brute_out_$i.txt) in $(( $(date +%s) - start )) s" >> brute_log.txt
  i=$((i+1))
done
echo done >> brute_log.txt
