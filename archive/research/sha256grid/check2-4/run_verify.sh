#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# runs one process at a time: the ledger, then the vt38 cross-checks of my dumps and of the scout's dumps
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
export PYTHONDONTWRITEBYTECODE=1
date
python3 -B ledger_chk.py 1.18 2 4 2.562 2.436 10.692 9.931 10.363 21.606 19.409 > ledger_chk.out 2>&1; cat ledger_chk.out
python3 -B chkverify.py sfs_M.txt 300 > verify_M.out 2>&1; cat verify_M.out
python3 -B chkverify.py sfs_H.txt 300 > verify_H.out 2>&1; cat verify_H.out
date
