#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run the 14 tail experiments of the staged r39tail.py on the public seeds, all at once, nice 0; outputs + wall times in work/tail/
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best
cd $P/work/tail
for i in $(seq -w 1 14); do ( s=$(date +%s%N); python3 -B $P/sha256/experiments/r39tail.py < r39-tail-$i.json > out_$i.json 2> err_$i.txt; echo "$i rc=$? ms=$(( ($(date +%s%N)-s)/1000000 ))" >> times.txt ) & done; wait
echo ALL DONE >> times.txt
