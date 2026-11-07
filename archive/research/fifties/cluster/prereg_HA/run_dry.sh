#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# prereg_HA step 2 (GPU half): generate + build the kernel, run it on the dry clusters.
# $1 = seed64 hex of the label "dry" (from Windows python: ref.py seed dry; WSL python3 has no numpy).
# The comparison runs afterwards on Windows python: ref.py dry gpu_dry.bin
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/cluster/prereg_HA"
python3 gen_cu.py
nvcc -O3 -arch=sm_86 -o gate gate.cu 2>&1 | grep -v "declared but never referenced" || true
test -x gate
echo "dry seed64 $1"
./gate dry "$1" 65536 gpu_dry.bin
