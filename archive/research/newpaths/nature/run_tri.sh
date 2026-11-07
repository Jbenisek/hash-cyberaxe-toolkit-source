#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# 3-word compensatory slices at w=8: all 560 word triples x 2^24 values, one base each (about 20 min per base)
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
echo "tri pid $$ start $(date)" >> pids.txt
{
timeout 2400 ./nature triples 41 0
timeout 2400 ./nature triples 41 1
} > tri.out 2>&1
echo "tri done $(date)" >> pids.txt
