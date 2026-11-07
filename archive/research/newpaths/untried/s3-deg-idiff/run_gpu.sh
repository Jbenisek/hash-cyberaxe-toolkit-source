#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build (if needed) and run the cube-sum kernel on one parameter file; stop only this process
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/s3-deg-idiff"
if [ ! -x ./cube6_bin ] || [ cube6.cu -nt cube6_bin ]; then /usr/bin/nvcc -O3 -o cube6_bin cube6.cu; fi
./cube6_bin "$1"
