#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/sha256-37-G04-U04/work
./h1 rand 28 20261012 > h1_rand28.out 2>&1
./h1 ctr 27 1 > h1_ctr27.out 2>&1
./h1 w15 27 2 > h1_w15_27.out 2>&1
echo done > h1_done.flag
