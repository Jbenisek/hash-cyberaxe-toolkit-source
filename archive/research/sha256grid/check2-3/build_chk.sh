#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-3: build the scout's q3gpu.cu (copied here, sha256 d3a796f13d810828...) into this folder; nvcc only, no GPU use
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-3" || exit 1
sha256sum q3gpu.cu consts.h twobit.h | cut -c1-16,65-
nvcc -O3 -std=c++17 -arch=sm_86 -o q3gpu_chk q3gpu.cu > build_chk.log 2>&1
echo "rc=$?"; grep -E "error" build_chk.log | head
sha256sum q3gpu_chk "../scout2-3/q3gpu2" | cut -c1-16,65-
./q3gpu_chk selftest | head -12
