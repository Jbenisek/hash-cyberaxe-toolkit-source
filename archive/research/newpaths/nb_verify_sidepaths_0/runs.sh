#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# 6 configurations, 2^33 trials each, at most 3 at a time, each capped at 900 s.
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/nb_verify_sidepaths_0 || exit 1
mkdir -p out
run(){ timeout 900 ./cvrate $1 $2 33 $3 > out/$1_$2.txt 2>&1; }
run iv 0 101 & run cv 1 102 & run cv 2 103 & wait
run cv 3 104 & run cv 4 105 & run m 0 106 & wait
echo done > out/ALLDONE
