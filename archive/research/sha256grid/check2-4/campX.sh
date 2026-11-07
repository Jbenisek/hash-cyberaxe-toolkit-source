#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-4 campaign X: cell event (C, the filed q3) and tail-only relaxation (T), NP 4000, 8 seeds each
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
date > campX.log
for s in 1 2 3 4 5 6 7 8; do ./chk38 C $((81000 + s)) 4000 2048 64 64 8 8 4 262144 >> campX.log; done
for s in 1 2 3 4 5 6 7 8; do ./chk38 T $((82000 + s)) 4000 2048 64 64 8 8 4 131072 >> campX.log; done
date >> campX.log
