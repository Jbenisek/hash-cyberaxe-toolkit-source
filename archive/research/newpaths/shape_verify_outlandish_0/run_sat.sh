#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# kissat runs for the lemma cross-check; at most 4 at a time; results appended to sat.log
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_verify_outlandish_0
run() { f=$1; t=$2; s=$(date +%s); timeout $t kissat -q $f > $(basename $f .cnf).kout 2>&1; rc=$?; e=$(date +%s); echo "$(basename $f) rc=$rc secs=$((e-s)) $(grep -m1 '^s ' $(basename $f .cnf).kout)" >> sat.log; }
echo "start $(date)" >> sat.log
run toy_r1_out0_k15.cnf 120 &
run toy_r1_out0_k14.cnf 120 &
run toy_r1_out0_out2_out5_k13.cnf 120 &
run toy_r1_out0_out2_out5_k12.cnf 120 &
wait
run ../gd_fixed_len64_k5_T100.cnf 600 &
run real_out0_k16.cnf 300 &
run real_out0_k15.cnf 600 &
wait
echo "done $(date)" >> sat.log
