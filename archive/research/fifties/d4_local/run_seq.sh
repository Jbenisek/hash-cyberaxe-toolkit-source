#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/d4_local" || exit 1
gcc -O3 -march=native -Wall -Wno-misleading-indentation -o d4c_seq d4c.c 2>&1 | head -30
date
SECS=${1:-1500}
for arm in none len flags; do
  for s in 811 812; do
    ./d4c_seq seq $arm $SECS $s seq_${arm}_$s.bin 2000000 > seq_${arm}_$s.txt 2>&1 &
  done
done
wait
date
echo done
