#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build_probe.sh: build walk32 and print host probes (cross-checked in Python by check_probe.py); then the shares run
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/b3-thi-walk/real
cd "$D" || exit 1
mkdir -p bin out
nvcc -O3 -arch=sm_86 -w -o bin/walk32 walk32.cu -lm 2>&1 | grep -v '^$' | head -30
sha256sum bin/walk32
./bin/walk32 probe 2026101001 > out/probe.txt
wc -l out/probe.txt
# shares: 2^16 groups x 7 full blocks x 2^16 steps = 3.0e10 real outer steps, every line evaluated
./bin/walk32 shares 2026101002 65536 > out/shares.txt
cat out/shares.txt
date
