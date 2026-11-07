#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-4 campaign Y: filed first row-17 test kept + collision (M) and rows 17..37 relaxed (H), NP 4000, 8 seeds each;
# the first seed of each dumps its verified successes for the Python cross-check with vt38.py
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
date > campY.log
./chk38 M 83001 4000 2048 65536 131072 256 1024 16 262144 sfs_M.txt >> campY.log
for s in 2 3 4 5 6 7 8; do ./chk38 M $((83000 + s)) 4000 2048 65536 131072 256 1024 16 262144 >> campY.log; done
./chk38 H 84001 4000 65536 65536 131072 256 1024 16 262144 sfs_H.txt >> campY.log
for s in 2 3 4 5 6 7 8; do ./chk38 H $((84000 + s)) 4000 65536 65536 131072 256 1024 16 262144 >> campY.log; done
date >> campY.log
