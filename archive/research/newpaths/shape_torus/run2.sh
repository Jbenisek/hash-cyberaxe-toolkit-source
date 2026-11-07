#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_torus
timeout 100 ./torus 2 8 -1 > torus_fam_w8.txt 2>&1
timeout 100 ./torus 3 8 > torus_symiv_w8.txt 2>&1
timeout 100 ./torus 3 12 > torus_symiv_w12.txt 2>&1
