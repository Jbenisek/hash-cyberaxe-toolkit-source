#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# third point of the scaling curve (28 free bits), started only after run_main.sh finished (one z3 process at a time)
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/combos/solvers-GROK-R3" || exit 1
grep -q "^done" run_main.log || { echo "run_main not done"; exit 1; }
s=$(date +%s.%N)
z3 -T:600 -st part_b07.smt2 > part_b07.out 2>&1 &
echo "part_b07 z3 pid $! start $(date -Is)" >> run_main.log; wait $!
e=$(date +%s.%N)
echo "part_b07 free_bits 28 result $(head -1 part_b07.out) wall $(echo "$e - $s" | bc) s" >> run_main.log
echo "extra done $(date -Is)" >> run_main.log
