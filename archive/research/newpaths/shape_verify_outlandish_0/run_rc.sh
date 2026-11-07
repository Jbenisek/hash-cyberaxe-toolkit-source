#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# sequential kissat chain over the CNF names given as arguments (600 s each); results appended to rc.log
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_verify_outlandish_0
for f in "$@"; do
  s=$(date +%s)
  timeout 600 kissat -q $f > $(basename $f .cnf).kout 2>&1
  rc=$?
  e=$(date +%s)
  echo "$f rc=$rc secs=$((e-s)) $(grep -m1 '^s ' $(basename $f .cnf).kout)" >> rc.log
done
