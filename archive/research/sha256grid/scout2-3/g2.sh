#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# G2 MAIN (PREREG_q3gpu.txt): master 20261010, runs 0..N-1 (N = $1, fixed from the G1 pilot speed), V = 4096 per run
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
./q3gpu2 gpusmc 20261010 0 "$1" 4000 2048 64 64 8 8 4 8192 4096 g2_main 1
tail -1 g2_main.log
