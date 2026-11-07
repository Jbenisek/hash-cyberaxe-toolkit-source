#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/blake3-r2-G07-U05/work
nvcc -O3 -arch=sm_86 -diag-suppress 1650 -o u05 u05.cu 2>&1 | tail -5
[ -f typed_t0.bin ] || ./u05 genlists
ls -la typed_t*.bin
# validation on known answers: control first (minutes), then the fresh scan
./u05 ctrl 0 0 3 200 > ctrl_t0_0_3.out 2>&1
cat ctrl_t0_0_3.out
