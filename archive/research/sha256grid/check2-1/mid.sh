#!/bin/bash

# Publication root: stable even when this driver changes working directories.
if [ -z "${HASHCYBERAXE_WORKSPACE:-}" ]; then
  _hca_here=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
  while [ ! -d "$_hca_here/research" ] && [ "$_hca_here" != / ]; do _hca_here=$(dirname -- "$_hca_here"); done
  HASHCYBERAXE_WORKSPACE=$_hca_here
fi
export HASHCYBERAXE_WORKSPACE
# check2-1: run when chain B is done (one Python process at a time, alongside chain A's kissat)
cd "${HASHCYBERAXE_WORKSPACE}/research/sha256grid/check2-1" || exit 1
[ -f B.chaindone ] && echo "chain B done: $(cat B.chaindone)" || { echo "chain B still running"; exit 0; }
grep -E '^s |process-time' cbase_s3.out
echo "== old (scout step1_base) vs regenerated base CNF, up to renaming of auxiliary variables"
python3 cnf_iso.py s_base.cnf c_base.cnf
date
