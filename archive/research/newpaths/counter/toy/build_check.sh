#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# build ctr_toy (W = 8) and run the construction checks and a tree-hash test (research only)
D="${HASHCYBERAXE_WORKSPACE}"/research/newpaths/counter/toy
B=$HOME/ctr_toy_bin
mkdir -p "$B"
cd "$D" || exit 1
g++ -O3 -march=native -x c++ -DWBITS=8 -w -o "$B/ctr_toy8" ctr_toy.c -lm || { echo BUILD FAILED; exit 1; }
echo "built $B/ctr_toy8"
"$B/ctr_toy8" treetest 77 40 > "$D/treetest_w8.txt"
echo "treetest lines: $(grep -c ^TT "$D/treetest_w8.txt")"
