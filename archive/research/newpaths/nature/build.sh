#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build nature.c and print self-test vectors for the python cross-check
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
gcc -O3 -march=native -o nature nature.c -lm 2> build.err || { cat build.err; exit 1; }
for w in 8 16 32; do ./nature selftest $w 7 5; done > selftest.txt
echo built; wc -l selftest.txt
