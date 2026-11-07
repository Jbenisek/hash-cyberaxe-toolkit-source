#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# G3 pool-size check: master 20261011, runs 0..N-1 (N = $1), V = 65536 fresh variants per run
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
./q3gpu2 gpusmc 20261011 0 "$1" 4000 2048 64 64 8 8 4 8192 65536 g3_pool 1
tail -1 g3_pool.log
