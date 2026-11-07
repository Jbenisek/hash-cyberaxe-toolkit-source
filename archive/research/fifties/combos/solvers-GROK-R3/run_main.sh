#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# one z3 process at a time: scaling curve (low NN bits of each guess word free, 4*NN free bits, -T:120, stop at first
# non-sat), then the full instance inst_true (128 free bits) with -T:900.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/combos/solvers-GROK-R3" || exit 1
echo "runner pid $$ start $(date -Is)" > run_main.log
for b in 04 06 08 10 12 14 16; do
  s=$(date +%s.%N)
  z3 -T:120 -st part_b$b.smt2 > part_b$b.out 2>&1 &
  echo "part_b$b z3 pid $!" >> run_main.log; wait $!
  e=$(date +%s.%N)
  r=$(head -1 part_b$b.out)
  echo "part_b$b free_bits $((10#$b * 4)) result $r wall $(echo "$e - $s" | bc) s" >> run_main.log
  [ "$r" = "sat" ] || break
done
s=$(date +%s.%N)
z3 -T:900 -st inst_true.smt2 > inst_true.out 2>&1 &
echo "inst_true z3 pid $! start $(date -Is)" >> run_main.log; wait $!
e=$(date +%s.%N)
echo "inst_true free_bits 128 result $(head -1 inst_true.out) wall $(echo "$e - $s" | bc) s" >> run_main.log
echo "done $(date -Is)" >> run_main.log
