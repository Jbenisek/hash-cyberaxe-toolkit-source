#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/av11/recount" || exit 1
# fresh seed 20261009771 (different from verify seed); 2800 launches x 2^31 = 6.01e12 samples per q
./rc meas 20261009771 00000000 2800 > meas_q00000000.txt 2>&1
./rc meas 20261009771 80000000 2800 > meas_q80000000.txt 2>&1
echo done > meas_done.txt
