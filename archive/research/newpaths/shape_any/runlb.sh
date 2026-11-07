#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# run kissat on the given cnf names (in cnf/), at most 4 at a time, timeout per file in seconds = $1
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/shape_any/cnf
TO=$1; shift
for f in "$@"; do
  ( timeout $TO kissat -q $f.cnf > $f.out 2>&1; echo "$f exit=$?" >> ../lb_runs.log ) &
done
wait
