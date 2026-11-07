#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
gcc -O3 -march=native -Wall -Wno-unused-function -o smc38r smc38r.c -lm 2>&1 | head -30
date
# filed-size cell replica (NP 4000, children 2048 64 64 8 8 4, MT 8192), 3 seeds
for s in 31001 31002 31003; do /usr/bin/time -f "%e s" ./smc38r C $s 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 0; done
# pilots: relaxed with G (cut 16), with G' (cut 15), cells through 17 (cut 17), NP 1000
./smc38r 16 41001 1000 2048 64 64 8 8 4 8192 4096 256 256 32 32 8 8192
./smc38r 15 41002 1000 2048 64 64 8 8 4 8192 4096 256 256 32 32 8 8192
./smc38r 17 41003 1000 2048 64 64 8 8 4 8192 4096 256 256 32 32 8 8192
./smc38r 22 41004 1000 2048 64 64 8 8 4 8192 4096 256 256 32 32 8 8192
date