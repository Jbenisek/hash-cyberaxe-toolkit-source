#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run the two program experiments of the staged r39joint.py on the public seeds; outputs, stderr, wall time in work/exp/
P="${HASHCYBERAXE_WORKSPACE}"/research/pkg_r39_best
cd $P/work/exp
for x in r39-transplant-claw r39-window-small; do
  s=$(date +%s%N); python3 -B $P/sha256/experiments/r39joint.py < $x.json > out_$x.json 2> err_$x.txt
  echo "$x rc=$? ms=$(( ($(date +%s%N)-s)/1000000 ))" | tee -a times.txt; tail -3 err_$x.txt
done
