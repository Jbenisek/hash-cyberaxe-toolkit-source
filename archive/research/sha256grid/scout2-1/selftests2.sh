#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
for f in selftest_k1fix selftest_k1flip selftest_k2fix selftest_k2fixs2; do
  s=$(date +%s.%N)
  kissat -q --time=120 $f.cnf > $f.out 2>&1
  rc=$?
  e=$(date +%s.%N)
  echo "$f rc=$rc $(grep '^s ' $f.out) wall=$(echo "$e - $s" | bc)"
done