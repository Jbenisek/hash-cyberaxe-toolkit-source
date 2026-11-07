#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# CPU lane B (no GPU): q3gpu2 cpubatch, master 4343, all run indices, V = 8192 fresh variants per run, per-A0 accounting
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-3" || exit 1
echo $$ > cpulaneB.pid
exec ./q3gpu2 cpubatch 4343 0 1 "$1" 4000 2048 64 64 8 8 4 8192 8192 cpuB_m4343
