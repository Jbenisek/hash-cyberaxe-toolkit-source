#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/scout2-1" || exit 1
for f in pc_k2_noR pc_k3_noR pc_k8_noPR pc_k9_noPR pc_s2_k4_noR pc_s2_k5_noR; do
  s=$(date +%s.%N)
  kissat -q --time=300 $f.cnf > $f.out 2>&1
  rc=$?
  e=$(date +%s.%N)
  echo "$f rc=$rc $(grep '^s ' $f.out) wall=$(echo "$e - $s" | bc)"
done