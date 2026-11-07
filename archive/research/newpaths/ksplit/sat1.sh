#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# usage: sat1.sh <cnf> <timeout_s>
cd "${HASHCYBERAXE_WORKSPACE}"/research/newpaths/ksplit
timeout $2 kissat -q $1 > ${1%.cnf}.out 2>&1; echo "exit=$?" >> ${1%.cnf}.out
