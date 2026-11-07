#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming2/sha256-37-G04-U06/work" || exit 1
p=$1; shift
[ -x ./blk ] && [ blk -nt blk.c ] || gcc -O3 -march=native -fopenmp -o blk blk.c -lm 2>&1 | grep -E "error|warning: impl"
./blk "$@"
