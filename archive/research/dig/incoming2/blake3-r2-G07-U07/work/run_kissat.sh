#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
cd "${HASHCYBERAXE_WORKSPACE}"/research/dig/incoming2/blake3-r2-G07-U07/work
sha256sum /usr/bin/kissat > kissat_bin.sha
date +%s > kissat_start.txt
kissat --sat --seed=506 --time=2500 run20.cnf > kissat_run.out 2>&1
echo "exit $?" >> kissat_run.out
date +%s > kissat_end.txt
