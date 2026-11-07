#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
mkdir -p dbl
: > double_results.txt
for g in 55-63,57-61 55-63,56-58 55-63,59-61 55-63,56-64 55-57,59-61 56-64,58-62 55-59,57-61 56-58,60-62 55-63,57-59 56-60,58-62; do
  f=dbl/d_${g//,/_}.smt2
  python3 double_smt.py $g $f
  r=$(timeout 200 z3 -T:190 $f 2>&1 | tr '\n' ' ')
  echo "$g $r" >> double_results.txt
done
echo done > double.done
