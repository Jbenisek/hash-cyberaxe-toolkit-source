#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# per-coset first derivatives (k = 1): which chi3-input bits (B3) are CONSTANT on a given coset; 300 cosets x 64 cubes
# (same seed 302 as coset_k2 gives the SAME 300 cosets, since t depends only on seed and coset index)
set -e
D="${HASHCYBERAXE_WORKSPACE}/research/newpaths/untried/s3-plane-degrees"
cd "$D"
./cubes run w40.txt 302 19200 1 span 64 1 19200 runs/coset_k1
