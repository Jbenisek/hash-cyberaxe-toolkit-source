#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Build walsh.c and run the weight 1..4 scans in three coordinate systems (raw, spiral = rotate by 8, spiral7 = rotate by 7).
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/joint" || exit 1
gcc -O3 -march=native -fopenmp -Wall -o walsh walsh.c -lm 2>&1 | head
for m in raw spiral spiral7; do
  OMP_NUM_THREADS=16 /usr/bin/time -f "elapsed %e s" ./walsh ../data/rand/res.u32 $m 1048576 0x4a4f494e54303031 4 > walsh_${m}_out.txt 2>&1
done
