#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# after campaigns X and Y: run statistics, vt38 cross-check of my H dump, then re-run the scout's plain-MC binary with
# its own seeds (stdout only; it writes no file) to check the reported tail ratios 2.50 (row 23) and 2.53 (row 22)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-4" || exit 1
export PYTHONDONTWRITEBYTECODE=1
date
python3 -B stats_chk.py campX.log campY.log > stats_chk.out 2>&1; cat stats_chk.out
python3 -B chkverify.py sfs_H.txt 300 > verify_H.out 2>&1; cat verify_H.out
S="${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-4"
date
"$S/smc38r_p" P23 51001 4000 2048 64 64 8 8 4 8192 0 0 0 0 0 0 0 > plain_rerun.out 2>&1
"$S/smc38r_p" P22 51002 4000 2048 64 64 8 8 4 16384 0 0 0 0 0 0 0 >> plain_rerun.out 2>&1
cat plain_rerun.out
date
