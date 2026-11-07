#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
set -e
cd "${HASHCYBERAXE_WORKSPACE}/research/fifties/context"
gcc -O3 -march=native -fopenmp -o ctx ctx.c
/usr/bin/time -v ./ctx > ctx_out.json 2> ctx_time.txt
tail -c 300 ctx_out.json
grep -E "Elapsed|Maximum resident" ctx_time.txt
