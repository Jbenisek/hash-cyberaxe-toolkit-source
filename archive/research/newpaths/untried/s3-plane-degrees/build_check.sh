#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build cubes.cu and dump all stages of 64 random native points for the Python self-check
set -e
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/s3-plane-degrees"
cd "$D"
/usr/bin/nvcc -O3 -arch=sm_86 -o cubes cubes.cu 2>&1 | grep -v "Wno-deprecated" || true
ls -la cubes
./cubes check w40.txt 7 64 check_points.txt
# small cube runs for the cross-check against cube_degree.cube (k = 3 and k = 9, span and basis)
./cubes run w40.txt 11 40 3 span 1 1 40 xc_k3
./cubes run w40.txt 12 40 9 span 1 1 40 xc_k9
./cubes run w40.txt 13 40 6 basis 1 1 40 xc_k6b
