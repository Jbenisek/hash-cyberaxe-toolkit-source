#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# fast functional-graph runs; usage: bash run_fg8.sh tag "emb half zero seed starts rounds" ...
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nature || exit 1
[ -x fg8 ] || gcc -O3 -march=native -o fg8 fg8.c -lm
tag=$1; shift
echo "fg8-$tag pid $$ start $(date)" >> pids.txt
for args in "$@"; do timeout 1500 ./fg8 $args >> fg8_$tag.out 2>&1 || echo "fg8 $args exit $?" >> fg8_$tag.out; done
echo "fg8-$tag done $(date)" >> pids.txt
