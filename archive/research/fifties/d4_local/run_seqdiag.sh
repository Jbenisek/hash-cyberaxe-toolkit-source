#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/d4_local" || exit 1
gcc -O3 -march=native -Wall -Wno-misleading-indentation -o d4c_diag d4c.c 2>&1 | head -30
for arm in none len flags; do
  COUNT_C=1 ./d4c_diag seq $arm 240 9${#arm}1 - 1000 > seqdiag_$arm.txt 2>&1 &
done
wait
grep -h -E "^seq arm|^stage C|FOUND" seqdiag_*.txt
