#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# the one double-pair query that timed out at 190 s, with a longer limit, plus mixed-parity variants
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
: > double2_results.txt
for g in 55-63,56-58 55-63,56-60 55-63,58-60 55-63,60-62 57-63,56-58; do
  f=dbl/d_${g//,/_}.smt2
  python3 double_smt.py $g $f
  r=$(timeout 900 z3 -T:890 $f 2>&1 | tr '\n' ' ')
  echo "$g $r" >> double2_results.txt
done
echo done > double2.done
