#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/blake3_r3
g++ -O2 -o rho_tag rho_tag.c -lm || exit 1
for w in 0 3 5 7; do ./rho_tag 32 400 3 $w; done
./rho_tag 40 40 3 0
./rho_tag 40 40 3 6
./rho_tag 32 400 2 0
