#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# K3 rate at non-root instances (the CV re-roll lever): random h7 with flags 0 (middle block) and 2 (CHUNK_END),
# 90 s each on the GPU, uniform delta.  Own processes only, one GPU job at a time.
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/combo-finder" || exit 1
date
./k3gpu 0x8f1bbcdc 0 90 41 0 k3gpu_inst_8f1bbcdc_f0.txt
./k3gpu 0x2a5b9c13 2 90 42 0 k3gpu_inst_2a5b9c13_f2.txt
./k3gpu 0x5BE0CD19 0 90 43 0 k3gpu_inst_iv7_f0.txt
date
