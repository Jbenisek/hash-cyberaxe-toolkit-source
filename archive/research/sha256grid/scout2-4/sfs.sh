#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
./smc38r 16 34011 4000 2048 64 64 8 8 4 8192 65536 4096 4096 512 512 128 131072 -1 sfs_cut16.txt
./smc38r 22 32011 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 131072 -1 sfs_cut22.txt
wc -l sfs_cut16.txt sfs_cut22.txt