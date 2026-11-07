#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/dig/incoming2/sha256-37-G04-U03/work" || exit 1
gcc -O3 -march=native -Wall -Wno-unused-function -Wno-unused-variable -pthread -o scan scan.c ../../../../tools/traillab/src/traillab.c -lm 2>&1 | grep -E "error|warning" | head -20
ls -la scan
