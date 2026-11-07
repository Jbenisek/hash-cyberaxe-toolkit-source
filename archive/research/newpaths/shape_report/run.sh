#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_report
gcc -O2 -o pinv pinv.c || exit 1
for w in 6 8 10; do ./pinv $w; done > pinv_small.txt 2>&1
./pinv 8 0x5a >> pinv_small.txt 2>&1
./pinv 8 0x01 >> pinv_small.txt 2>&1
timeout 900 ./pinv 12 > pinv_w12.txt 2>&1
echo DONE >> pinv_w12.txt
