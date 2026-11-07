#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# campaign B: rows 17..37 relaxed with row 16 cells (cut 16) and row 16 relaxed too (cut 15, G'), NP 4000
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
date > campB.log
for s in 34011 34012 34013 34014 34015 34016 34017 34018; do ./smc38r 16 $s 4000 2048 64 64 8 8 4 8192 65536 4096 4096 512 512 128 131072 >> campB.log; done
for s in 35011 35012 35013 35014; do ./smc38r 15 $s 4000 2048 64 64 8 8 4 8192 65536 4096 4096 512 512 128 131072 >> campB.log; done
for s in 36011 36012 36013 36014; do ./smc38r 25 $s 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 0 >> campB.log; done
date >> campB.log