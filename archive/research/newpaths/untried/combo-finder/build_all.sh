#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# compile the remaining tools (CPU, one process at a time)
cd "${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/combo-finder" || exit 1
gcc -O3 -march=native -o k2check k2check.c -lm && echo k2check ok
gcc -O3 -march=native -o mkjoint mkjoint.c -lm && echo mkjoint ok
gcc -O3 -march=native -o mkk1prob mkk1prob.c -lm && echo mkk1prob ok
gcc -O3 -march=native -o d3test d3test.c -lm && echo d3test ok
gcc -O3 -march=native -o b3final b3final.c -lm && echo b3final ok
nvcc -O3 -arch=sm_86 -o k1gpu k1gpu.cu 2>&1 | grep -iv warning | head -5; ls -la k1gpu && echo k1gpu ok
nvcc -O3 -arch=sm_86 -o k3gpu k3gpu.cu 2>&1 | grep -iv warning | head -5; ls -la k3gpu && echo k3gpu ok
