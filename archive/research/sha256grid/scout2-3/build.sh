#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build q3gpu (no GPU use): nvcc only
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
nvcc -O3 -std=c++17 -arch=sm_86 -Xptxas -v -o q3gpu q3gpu.cu > build.log 2>&1
rc=$?
grep -E "error|warning|k_tail|k_stage|k_vsample|registers|lmem|spill" build.log | head -60
echo "rc=$rc"
