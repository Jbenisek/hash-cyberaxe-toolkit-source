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
timeout 300 ./traillab backward --chi chi/chi38.txt --rows 17 25 --noenum --threads 3 > $W/bw/base.txt 2>&1
for f in $W/chi/A17_*.txt $W/chi/E18_*.txt $W/chi/E21_*.txt; do n=$(basename $f .txt); timeout 300 ./traillab backward --chi $f --rows 17 25 --noenum --threads 3 > $W/bw/$n.txt 2>&1; done
