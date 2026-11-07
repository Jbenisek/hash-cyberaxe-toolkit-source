#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# quick foreground checks (each well under a minute)
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
{
time ./nature neutral 8 11 2000
./nature neutral 16 12 1000
./nature neutral 32 13 1000
} > quick1.out 2>&1
cat quick1.out
