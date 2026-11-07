#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_torus
( for off in 0 1 2 3 4 5 6 7 8 9; do timeout 60 ./torus 4 12 0 $off; done
  for r in $(seq 1 30); do timeout 60 ./torus 4 12 0 -$r; done ) > torus_fam8_w12.txt 2>&1
( timeout 400 ./torus 4 16 0 0; timeout 400 ./torus 4 16 0 2 ) > torus_fam8_w16.txt 2>&1
