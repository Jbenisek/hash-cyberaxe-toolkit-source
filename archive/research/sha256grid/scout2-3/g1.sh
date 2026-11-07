#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# G1: GPU = CPU equivalence (master 777 run 0, NP 200, as cputest.sh) + pilot of 256 full-size runs (master 9001)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
./q3gpu2 gpusmc 777 0 1 200 2048 64 64 8 8 4 8192 4096 g1_equiv 64
grep '^run' g1_equiv.log; grep '^run' cpusmc.txt
./q3gpu2 gpusmc 9001 0 256 4000 2048 64 64 8 8 4 8192 4096 g1_pilot 4
tail -1 g1_pilot.log
