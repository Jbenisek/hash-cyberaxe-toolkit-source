#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# campaign C: where the gain sits (cuts 18..21) and a 2x-particle, 2-4x-proposal check of cut 16 (heavy tails)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
date > campC.log
for cut in 18 19 20 21; do for s in 1 2 3 4; do ./smc38r $cut $((37000 + cut * 10 + s)) 4000 2048 64 64 8 8 4 8192 65536 4096 4096 512 512 128 131072 >> campC.log; done; done
for s in 1 2 3 4; do ./smc38r 16 $((38000 + s)) 8000 2048 64 64 8 8 4 8192 131072 16384 16384 2048 2048 512 262144 >> campC.log; done
date >> campC.log