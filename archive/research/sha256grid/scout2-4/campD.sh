#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# campaign D: variant dispersion of the relaxed estimate (cut 16 and cut 22 with a fixed variant from the sample)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4" || exit 1
date > campD.log
for v in 0 101 202 303 404 505; do ./smc38r 16 $((39000 + v)) 4000 2048 64 64 8 8 4 8192 65536 4096 4096 512 512 128 131072 $v | sed "s/^/fixvar $v /" >> campD.log; done
for v in 0 101 202 303 404 505; do ./smc38r C $((39500 + v)) 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 0 $v | sed "s/^/fixvar $v /" >> campD.log; done
date >> campD.log