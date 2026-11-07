#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/av11/recount" || exit 1
nvcc -O3 -arch=sm_86 -o rc rc.cu 2>&1 | grep -v warning | head -20
./rc verify 918273645 > verify_out.txt 2>&1; echo "verify exit $?" >> verify_out.txt
./rc meas 918273645 00000000 16 > speed_test.txt 2>&1
