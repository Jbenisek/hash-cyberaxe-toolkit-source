#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/tools/traillab"
W="${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming/sha256-38-U01/work
( time timeout 300 ./traillab backward --chi chi/chi38.txt --rows 19 19 --noenum --threads 3 ) > $W/out/_b19_base.txt 2>&1
