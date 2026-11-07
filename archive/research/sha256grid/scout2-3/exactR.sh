#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# exact |R_j| recount on the GPU (run only while this session's G2 job holds GPU.lock)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
L="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/GPU.lock"
head -1 "$L" | grep -q "^scout2-3 " || { echo "lock not held by scout2-3; not running"; exit 9; }
./q3gpu2 >/dev/null 2>&1
./exactR "$@" | tee -a exactR.txt
