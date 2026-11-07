#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# all pairs and triples of sibling lengths 55..64: is there one pinned C3 with equal (b,d) outputs?
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
mkdir -p sib
out=sweep_sib.txt
: > $out
for a in $(seq 55 64); do for b in $(seq $((a+1)) 64); do
  f=sib/p_${a}_${b}.smt2
  python3 triple_smt.py $a,$b $f 2>/dev/null || echo "python3 missing"
  r=$(timeout 60 z3 -T:55 $f 2>&1 | head -1)
  echo "pair $a $b $r" >> $out
done; done
for a in $(seq 55 64); do for b in $(seq $((a+1)) 64); do for c in $(seq $((b+1)) 64); do
  f=sib/t_${a}_${b}_${c}.smt2
  python3 triple_smt.py $a,$b,$c $f
  r=$(timeout 60 z3 -T:55 $f 2>&1 | head -1)
  echo "triple $a $b $c $r" >> $out
done; done; done
echo done > sweep_sib.done
