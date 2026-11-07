#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/kverify_0
s=$(date +%s); timeout 110 kissat -q r2_D4_U90.cnf > r2_D4_U90.out 2>&1; rc=$?
echo "r2_D4_U90 rc=$rc $(grep '^s ' r2_D4_U90.out) secs=$(( $(date +%s) - s ))" >> sat_c.log
