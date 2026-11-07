#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# eshare.sh: exact E count of whole walk contexts from their block low halves (research only)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/untried/b3-thi-walk/real
cd "$D" || exit 1
nvcc -O3 -arch=sm_86 -w -o bin/walk32 walk32.cu -lm 2>&1 | grep -v '^$' | head -30
./bin/walk32 probe 2026101001 > out/probe3.txt
cmp out/probe.txt out/probe3.txt && echo "probe unchanged"
# small run against the walked share run (same seed, same 65,536 contexts): must reproduce its E total exactly
./bin/walk32 eshare 2026101002 65536 > out/eshare_check.txt
cat out/eshare_check.txt
./bin/walk32 eshare 2026101021 4294967296 > out/eshare_2p32.txt
./bin/walk32 eshare 2026101022 17179869184 > out/eshare_2p34.txt
cat out/eshare_2p34.txt
cat out/eshare_2p32.txt
date
