#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build perframe (WSL, CUDA 12.4, RTX 3090 = sm_86); KAT of the generators
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/perframe"
python3 -B gen_consts.py > gen_consts.json
nvcc -O3 -arch=sm_86 -o perframe perframe.cu 2> build.err || { cat build.err; exit 1; }
./perframe kat > kat_gpu.json
python3 -B ref_pf.py kat kat_gpu.json > kat_check.json
cat gen_consts.json kat_check.json
