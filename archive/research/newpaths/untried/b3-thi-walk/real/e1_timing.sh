#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# e1_timing.sh: a short E1 run to time the kernel (2^36 trials)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/b3-thi-walk/real
cd "$D" || exit 1
./bin/walk32 e1 2026101003 128 256 walk > out/e1_timing.txt
cat out/e1_timing.txt
date
