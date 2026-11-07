#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-1: rebuild the scout's sampler here and rerun it for S* and r4g8 (one process at a time)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
gcc -O3 -march=native -o a2r0_c a2r0.c -lm || exit 1
SSTAR=$(python3 -c "
import sys; sys.path.insert(0, '.')
from r38core import TX
print(' '.join('%08x' % TX[0][i] for i in range(16)))")
echo "== S* A0..A15: $SSTAR"
./a2r0_c $SSTAR 24 7 48
echo "== r4g8"
./a2r0_c 4493f513 f5ab3979 0c7897cd 837074f8 50748c96 9fe5f173 ffd9cecb 3e016e83 b6a6b5f9 3ec0b304 bcc85d8c 25d3cc99 4846f2d8 c2dc0441 c84cdcb9 91c40603 24 7 48
