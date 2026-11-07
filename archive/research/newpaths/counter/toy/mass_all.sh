#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# rebuild, then exact counts for all 48 W=8 sets -> mass_set<ID>.txt, massmat_set<ID>.txt, mass_summary.txt
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
B=$HOME/ctr_toy_bin
cd "$D" || exit 1
g++ -O3 -march=native -x c++ -DWBITS=8 -w -o "$B/ctr_toy8" ctr_toy.c -lm || { echo BUILD FAILED; exit 1; }
: > mass_summary.txt
for i in $(seq 0 47); do
  "$B/ctr_toy8" mass sets_w8.txt $i "massmat_set$i.txt" > "mass_set$i.txt" 2>&1
  echo "set $i $(grep ^MASS mass_set$i.txt | awk '{print "n",$8,"sumper",$10,$13}') $(grep ^HEAVIEST mass_set$i.txt) | $(grep ^BESTGAIN mass_set$i.txt)" >> mass_summary.txt
done
cat mass_summary.txt
