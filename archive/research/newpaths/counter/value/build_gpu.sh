#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build the GPU counter-rate program and run a short smoke test (counter/value)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/value
cd "$D" || exit 1
export PATH=$PATH:/usr/local/cuda/bin
python3 -B gen_ctr.py cone4_E1b1_B10.txt ctr_gen.cuh || exit 1
nvcc -O3 -arch=sm_86 -o ctr_gpu ctr_gpu.cu 2> build_gpu.err || { cat build_gpu.err; exit 1; }
echo built
time ./ctr_gpu real 1 16 4 12 4 1 > smoke_gpu.txt
head -40 smoke_gpu.txt
