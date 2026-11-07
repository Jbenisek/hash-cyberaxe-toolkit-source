#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# K1-K3 coupling test: walsh on keys.u32; data R = K1^K3 against K1 ^ (K3 of another row of the same half).
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/joint" || exit 1
gcc -O3 -march=native -fopenmp -Wall -o walsh walsh.c -lm 2>&1 | head
for m in kraw kspiral kspiral7; do
  OMP_NUM_THREADS=16 /usr/bin/time -f "elapsed %e s" ./walsh ../data/rand/keys.u32 $m 1048576 0x4a4f494e54303032 4 > walsh_${m}_out.txt 2>&1
done
