#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build hotspot.cu and run a seconds-long smoke test (hotspot folder; research only)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/hotspot
cd "$D" || exit 1
mkdir -p out
nvcc -O3 -arch=sm_86 -o hotspot hotspot.cu 2> build.err || { cat build.err; exit 1; }
echo built
# 2^30 trials, full HW histogram, generous sampling, HW threshold 0
time timeout 120 ./hotspot 1 16 0 12 4 7 4 4 6 0 0 128 out/smoke.bin > out/smoke.txt 2> out/smoke.err
echo "exit $?"
cat out/smoke.txt
ls -l out/smoke.bin
