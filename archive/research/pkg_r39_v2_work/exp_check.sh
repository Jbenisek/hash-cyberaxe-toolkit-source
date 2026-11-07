#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exp_check.sh TAG : the two program experiments of the staged r39joint.py on the public seeds (requests of the 2b4af365 build); outputs in pkg_r39_v2_work/exp_TAG/
W="${HASHCYBERAXE_WORKSPACE}"/research; P=$W/pkg_r39_$1; O=$W/pkg_r39_v2_work/exp_$1; mkdir -p $O; cd $O
for x in r39-transplant-claw r39-window-small; do
  ( s=$(date +%s%N); python3 -B $P/sha256/experiments/r39joint.py < $W/pkg_r39_best_work/exp/$x.json > out_$x.json 2> err_$x.txt
  echo "$x rc=$? ms=$(( ($(date +%s%N)-s)/1000000 )) $(tail -c 300 err_$x.txt)" >> times.txt ) &
done; wait; cat times.txt
