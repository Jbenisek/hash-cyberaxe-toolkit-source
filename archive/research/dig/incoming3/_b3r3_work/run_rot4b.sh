#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming3/_b3r3_work"
for r in 16 12 8 7; do
  E="0 4 $r $((r+4)) $((32-r)) $((36-r)) 32 36"
  K=$(seq -s ' ' 1 35)
  nice -n 10 ./rotsearch $r 4 full "$E" "$K"
done
