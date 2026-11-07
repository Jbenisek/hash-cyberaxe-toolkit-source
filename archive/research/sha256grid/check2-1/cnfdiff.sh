#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1"
echo "== my c_base vs scout step1_base"; python3 cnfdiff.py c_base.cnf $S/step1_base.cnf
echo "== my c_base vs scout step1_k1"; python3 cnfdiff.py c_base.cnf $S/step1_k1.cnf
echo "== scout step1_base vs scout selftest_fix (S* fixed, same generator version)"; python3 cnfdiff.py $S/step1_base.cnf $S/selftest_fix.cnf | head -4
