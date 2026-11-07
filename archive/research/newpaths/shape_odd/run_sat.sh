#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_odd
run() { f=$1; t=$2; s=$(date +%s); timeout $t kissat -q $f.cnf > $f.kissat.out 2>&1; rc=$?; e=$(date +%s); echo "$f rc=$rc secs=$((e-s)) $(grep -m1 '^s ' $f.kissat.out)" >> sat_sphere.log; }
run sph_out0_k16 300
run sph_out0_k15 600 &
run sph_out2_k15 600 &
wait
run sph_out5_k15 600 &
run sph_out7_k15 600 &
wait
echo ALLDONE >> sat_sphere.log