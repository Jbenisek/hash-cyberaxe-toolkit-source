#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
export PYTHONDONTWRITEBYTECODE=1
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4"
date
python3 -B verify_scout.py "$S/sfs_cut16.txt" > verify_scout.out 2>&1
python3 -B verify_scout.py "$S/sfs_cut22.txt" >> verify_scout.out 2>&1
cat verify_scout.out
date
