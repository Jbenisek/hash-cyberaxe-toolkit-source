#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Build and run the rotational scans on both data sets. One process, OpenMP threads.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/rotational" || exit 1
gcc -O3 -march=native -fopenmp -Wall -o /tmp/rotscan_rot rotscan.c 2>&1 | head -30
sha256sum rotscan.c
export OMP_NUM_THREADS=16
date
for s in rand ctx; do
  /usr/bin/time -f "$s: %e s, %M KB" /tmp/rotscan_rot ../data $s out_$s > log_$s.txt 2>&1
  echo "$s exit $?" >> log_$s.txt
  cat log_$s.txt
done
date
ls -l out_*
