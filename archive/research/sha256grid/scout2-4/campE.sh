#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# campaign E: the event of a program that keeps the filed first row-17 test (E17^x 10-bit mask) and replaces the deep
# path's cell tests by the collision test: cut 16 with no outside proposals at row 17 (U17 = 0)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
date > campE.log
for s in 1 2 3 4 5 6 7 8; do ./smc38r 16 $((40100 + s)) 4000 2048 64 64 8 8 4 8192 0 4096 4096 512 512 128 131072 | sed "s/^/mask17 /" >> campE.log; done
date >> campE.log