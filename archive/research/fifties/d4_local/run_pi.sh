#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/d4_local" || exit 1
gcc -O3 -march=native -Wall -Wno-misleading-indentation -o d4c d4c.c 2>&1 | head -30
for arm in none len flags; do
  ./d4c pi $arm 20000 501 > pi_$arm.txt 2>&1 &
done
EARLY=1 RETRY_CAP=1000000 ./d4c stats none 2000000 601 - 0 > early_none.txt 2>&1 &
wait
echo done
