#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/rot5"
for r in 12 16 8 7; do for c in 0 1; do
 E="0 $r $((32-r)) 32 36"; K="$r $((32-r)) $((36-r)) 32 36"
 echo "clean=$c"; date; nice -n 19 timeout 590 ./rotfuse $r 5 full "$E" "$K" 0 1 $c
done; done
