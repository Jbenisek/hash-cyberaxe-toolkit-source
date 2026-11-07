#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build and run the c1 cheap-test recheck; 15 minute cap
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nb_verify_nature_0 || exit 1
gcc -O3 -march=native -o c1test c1test.c -lm 2> build.err || { echo BUILD FAILED; cat build.err; exit 1; }
echo "start $(date)" > c1test.out
timeout 900 ./c1test 4294967296 777 >> c1test.out 2>&1
echo "exit $? end $(date)" >> c1test.out
