#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build q3gpu2 (same source plus the cpubatch mode); the running CPU lane keeps using ./q3gpu
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
nvcc -O3 -std=c++17 -arch=sm_86 -o q3gpu2 q3gpu.cu > build2.log 2>&1
echo "rc=$?"; grep -E "error|warning" build2.log | head
./q3gpu2 cpusmc 777 0 200 2048 64 64 8 8 4 8192 4096 | head -1
grep '^run' cpusmc.txt
sha256sum q3gpu.cu q3gpu2 | cut -c1-16,65-
