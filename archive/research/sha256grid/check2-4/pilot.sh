#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
gcc -O3 -march=native -Wall -Wno-unused-function -o chk38 chk38.c -lm 2>&1 | head -30
date
# small pilots of each mode (NP 500)
/usr/bin/time -f "%e s %M KB" ./chk38 C 7001 500 2048 64 64 8 8 4 262144
/usr/bin/time -f "%e s %M KB" ./chk38 T 7002 500 2048 64 64 8 8 4 131072
/usr/bin/time -f "%e s %M KB" ./chk38 M 7003 500 2048 65536 131072 256 1024 16 262144
/usr/bin/time -f "%e s %M KB" ./chk38 H 7004 500 65536 65536 131072 256 1024 16 262144
date
