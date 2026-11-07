#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# kverify_0: controls and the two-region question, sequential, one process
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/kverify_0
for spec in r1_D4_S25:60 r1_D2_S14:60 r1_D2_S15:300 r2_D12_U93:300 r2_D4_U93:1200; do
  f=${spec%%:*}; t=${spec##*:}
  s=$(date +%s)
  timeout $t kissat -q $f.cnf > $f.out 2>&1
  rc=$?
  echo "$f rc=$rc $(grep '^s ' $f.out) secs=$(( $(date +%s) - s ))" >> sat_a.log
done
echo done >> sat_a.log
