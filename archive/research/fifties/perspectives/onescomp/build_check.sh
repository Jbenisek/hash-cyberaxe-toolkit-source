#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# Build oc_stream and run the reproduction check (65,536 pairs, gen.c seed, 1 thread) + a timing probe.
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives/onescomp" || exit 1
gcc -O2 -Wall -fopenmp -o oc_stream oc_stream.c 2>&1 | head -30
./oc_stream real check_real_65536.bin 65536 0x5045525350310001 1
./oc_stream real probe.bin 1048576 0x1234 4
./oc_stream ctrl probe_ctrl.bin 1048576 0x1234 4
rm -f probe.bin probe_ctrl.bin
