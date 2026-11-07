#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Confirmation runs with fresh seeds: E1 census (2^14 contexts x 2^21 cube = 2^35) and group hull (256 groups).
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/joint" || exit 1
OMP_NUM_THREADS=8 /usr/bin/time -f "elapsed %e s" ./e1filter 16384 0x4531464c54523032 e1filter_hits2.txt > e1filter_out2.txt 2>&1
OMP_NUM_THREADS=8 /usr/bin/time -f "elapsed %e s" ./grouphull 256 0x47524f5550483032 > grouphull_out2.txt 2>&1