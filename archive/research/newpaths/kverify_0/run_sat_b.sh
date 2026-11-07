#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# kverify_0: single-region question (R8 analogue), one process
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/kverify_0
for spec in r1_D4_S47:1500; do
  f=${spec%%:*}; t=${spec##*:}
  s=$(date +%s)
  timeout $t kissat -q $f.cnf > $f.out 2>&1
  rc=$?
  echo "$f rc=$rc $(grep '^s ' $f.out) secs=$(( $(date +%s) - s ))" >> sat_b.log
done
echo done >> sat_b.log
