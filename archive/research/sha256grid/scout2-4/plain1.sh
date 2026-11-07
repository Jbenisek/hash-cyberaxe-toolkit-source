#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
gcc -O3 -march=native -Wall -Wno-unused-function -o smc38r_p smc38r.c -lm 2>&1 | head
date
/usr/bin/time -f "%e s" ./smc38r_p P23 51001 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 0
/usr/bin/time -f "%e s" ./smc38r_p P22 51002 4000 2048 64 64 8 8 4 16384 0 0 0 0 0 0 0
date