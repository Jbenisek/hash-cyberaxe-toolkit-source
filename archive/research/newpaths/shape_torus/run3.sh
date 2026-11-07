#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_torus
gcc -O2 -o torus torus.c 2>&1 | head
for off in 0 3 5 8 11 13 16 19 21 24 1 2 4 6 7 9 10 12; do timeout 60 ./torus 2 8 -1 $off; done > torus_fam_w8.txt 2>&1
