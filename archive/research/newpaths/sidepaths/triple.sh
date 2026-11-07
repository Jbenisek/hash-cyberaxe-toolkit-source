#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# z3 on sibling-pin queries, each with a time limit; results in triple_<name>.out
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/sidepaths
for q in pair_55_63 tri_55_63_59 tri_55_63_64 tri_55_63_56 quad_55_63_59_64; do
  start=$(date +%s)
  timeout 300 z3 -T:290 $q.smt2 > triple_$q.out 2>&1
  echo "exit=$? secs=$(( $(date +%s) - start ))" >> triple_$q.out
done
echo done > triple.done
