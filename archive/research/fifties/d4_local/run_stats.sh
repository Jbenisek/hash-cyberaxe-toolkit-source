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
N=${1:-4000000}
for arm in none len flags; do
  for s in 201 202; do
    RETRY_CAP=1000000 COUNT_ALL=1 ./d4c stats $arm $N $s dump_${arm}_$s.bin 1000000 > stats_${arm}_$s.txt 2>&1 &
  done
done
wait
./d4c gbrute flags 6 31 > gbrute_flags.txt 2>&1
./d4c gbrute none 4 32 > gbrute_none.txt 2>&1
echo done
