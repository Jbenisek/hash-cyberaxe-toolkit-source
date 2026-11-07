#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build tower.cu and check it reproduces the stored rand/ and ctx/ residuals and digests exactly
set -e
D="${HASHCYBERAXE_WORKSPACE}/research/fifties/perspectives"
cd "$D/modular"
nvcc -O3 -arch=sm_86 -o tower tower.cu 2>&1 | grep -v "^$" || true
for s in rand ctx; do
  ./tower check "$D/data/$s/inputs.u32" "$D/data/$s/res.u32" "$D/data/$s/dig.u32" | sed "s/^/[$s] /"
done
