#!/usr/bin/env bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/blake3_r3/stack1020/ext"
REPO=$(ls -d /root/hashsmash/yukon/hashsmash 2>/dev/null || ls -d /root/hashsmash/hash-smash 2>/dev/null | head -1)
ls "$REPO/verifier/blake3.py" || exit 1
nice -n 10 python3 -B ref_check.py "$REPO" ../pkg/blake3/experiments > ref_check.out 2>&1; cat ref_check.out
rm -rf ../pkg/blake3/experiments/__pycache__
