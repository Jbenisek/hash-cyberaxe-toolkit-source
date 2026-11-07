#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Build grouphull.c, check K1/K3 against every stored rand row, then 64 groups over the whole 2^21 cube.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/joint" || exit 1
gcc -O3 -march=native -fopenmp -Wall -Wno-unused-function -o grouphull grouphull.c -lm 2>&1 | head
./grouphull check ../data/rand/inputs.u32 ../data/rand/keys.u32 > grouphull_check_out.txt 2>&1
cat grouphull_check_out.txt
OMP_NUM_THREADS=8 /usr/bin/time -f "elapsed %e s" ./grouphull 64 0x47524f5550483031 > grouphull_out.txt 2>&1
