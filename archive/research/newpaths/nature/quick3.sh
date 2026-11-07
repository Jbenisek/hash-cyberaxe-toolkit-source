#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# short experiments (each under ~1 minute), run one after another in one process slot
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
gcc -O3 -march=native -o nature2 nature.c -lm 2> build2.err || { cat build2.err; exit 1; }
echo "quick3 pid $$ start $(date)" >> pids.txt
{
echo "== N1 more bases at w=8 (2^20 bases x 128 flips = 2^27 flips)"; timeout 300 ./nature2 neutral 8 101 1048576
echo "== N2 pairs, 8 bases"; timeout 300 ./nature2 pairs 102 8
echo "== N4 robustness"; timeout 300 ./nature2 robust 8 103 8 3000; timeout 300 ./nature2 robust 32 104 48 3000
echo "== C1 pivots"; timeout 300 ./nature2 pivot_ac 16 105 0; timeout 300 ./nature2 pivot_ac 32 106 20000; timeout 300 ./nature2 pivot_bd 16 107 4096
echo "== C1b sibling survival"; timeout 300 ./nature2 variants 8 108 20000; timeout 600 ./nature2 variants 16 109 2000
echo "== P1 landscape"; for f in 1 2 4 16; do timeout 120 ./nature2 autocorr 8 110 1048576 $f; done; timeout 120 ./nature2 autocorr 32 111 1048576 1; timeout 120 ./nature2 autocorr 32 112 1048576 2
timeout 300 ./nature2 anneal 113 100 4194304
echo "== I1 immune"; timeout 300 ./nature2 birthday 114 100; timeout 900 ./nature2 clonalg 115 8 67108864 0; timeout 600 ./nature2 clonalg 116 20 67108864 1
echo "== D1 palindromes w=12"; timeout 300 ./nature2 palin 12 117 268435456
} > quick3.out 2>&1
echo "quick3 done $(date)" >> pids.txt
