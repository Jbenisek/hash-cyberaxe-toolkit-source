#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Build e1filter.c, check it against every stored rand row, then run the E1 census (2^14 contexts x full 2^21 cube = 2^35).
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/joint" || exit 1
gcc -O3 -march=native -fopenmp -Wall -Wno-unused-function -o e1filter e1filter.c -lm 2>&1 | head
./e1filter check ../data/rand/inputs.u32 ../data/rand/keys.u32 > e1filter_check_out.txt 2>&1
cat e1filter_check_out.txt
OMP_NUM_THREADS=8 /usr/bin/time -f "elapsed %e s" ./e1filter 16384 0x4531464c54523031 e1filter_hits.txt > e1filter_out.txt 2>&1
