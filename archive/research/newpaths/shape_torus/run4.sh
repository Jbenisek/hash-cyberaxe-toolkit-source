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
( for off in $(seq 0 24); do timeout 30 ./torus 4 8 0 $off; done
  for r in $(seq 1 40); do timeout 30 ./torus 4 8 0 -$r; done ) > torus_fam8_w8.txt 2>&1
